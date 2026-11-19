#!/usr/bin/env python3
"""Offline Markdown relative link and GitHub-style heading anchor checker."""

from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import argparse
import json
import re
import unicodedata
import urllib.parse
from pathlib import Path
from typing import Any

SKIP_SCHEMES = ("http://", "https://", "mailto:", "tel:", "data:", "javascript:")
FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")
HEADING_RE = re.compile(r"^\s{0,3}(#{1,6})\s+(.+?)\s*$")
HTML_ANCHOR_RE = re.compile(r"<a\s+[^>]*(?:id|name)\s*=\s*[\"']([^\"']+)[\"'][^>]*>", re.IGNORECASE)
LINK_RE = re.compile(r"(?<!!)\[(?:[^\[\]\\]|\\.)*\]\(([^)\n]+)\)")


def _replace_inline_code(line: str) -> str:
    """Replace Markdown inline code spans (`...`, ``...``) with inert text."""
    out: list[str] = []
    i = 0
    n = len(line)
    while i < n:
        if line[i] == "`":
            j = i
            while j < n and line[j] == "`":
                j += 1
            ticks = line[i:j]
            close_idx = line.find(ticks, j)
            if close_idx != -1:
                out.append("CODE")
                i = close_idx + len(ticks)
                continue
        out.append(line[i])
        i += 1
    return "".join(out)


def _strip_heading_markdown(raw: str) -> str:
    # Remove optional closing ATX hashes (`## Title ##`)
    text = re.sub(r"\s+#+\s*$", "", raw).strip()
    # Replace images and links with their visible label
    text = re.sub(r"!\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    # Remove HTML tags
    text = re.sub(r"<[^>]+>", "", text)
    # Remove inline code backticks while preserving inner text
    text = re.sub(r"`+([^`]*)`+", r"\1", text)
    # Remove emphasis markers while preserving underscores inside words
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"~~([^~]+)~~", r"\1", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    text = re.sub(r"(?<!\w)__([^_]+)__(?!\w)", r"\1", text)
    text = re.sub(r"(?<!\w)_([^_]+)_(?!\w)", r"\1", text)
    return text.strip()


def github_slug(heading_text: str) -> str:
    """Generate a GitHub-style heading anchor slug."""
    cleaned = _strip_heading_markdown(heading_text).lower()
    kept: list[str] = []
    for ch in cleaned:
        if ch in (" ", "-", "_"):
            kept.append(ch)
        else:
            cat = unicodedata.category(ch)
            if cat and cat[0] in ("L", "N"):
                kept.append(ch)
    slug = "".join(kept).strip()
    return slug.replace(" ", "-")


def extract_anchors(md_path: Path) -> set[str]:
    """Extract all GitHub heading slugs and explicit HTML anchors from a Markdown file."""
    text = md_path.read_text(encoding="utf-8", errors="replace")
    anchors: set[str] = set()
    counts: dict[str, int] = {}

    in_fence = False
    fence_char = ""
    fence_len = 0

    for line in text.splitlines():
        fm = FENCE_RE.match(line)
        if not in_fence and fm:
            in_fence = True
            fence_char = fm.group(1)[0]
            fence_len = len(fm.group(1))
            continue
        if in_fence:
            stripped = line.lstrip()
            if (
                stripped.startswith(fence_char * fence_len)
                and stripped.strip(fence_char).strip() == ""
            ):
                in_fence = False
            continue

        for am in HTML_ANCHOR_RE.finditer(line):
            anchors.add(am.group(1).strip().lower())

        hm = HEADING_RE.match(line)
        if hm:
            base = github_slug(hm.group(2))
            if not base:
                continue
            count = counts.get(base, 0)
            slug = base if count == 0 else f"{base}-{count}"
            counts[base] = count + 1
            anchors.add(slug)

    return anchors


def _parse_link_target(raw_inside_parens: str) -> str:
    val = raw_inside_parens.strip()
    if not val:
        return ""
    if val.startswith("<"):
        end_angle = val.find(">")
        if end_angle != -1:
            return val[1:end_angle].strip()
    # Strip optional title: target "title" or target 'title'
    m = re.match(r'^(\S+)(?:\s+(?:"[^"]*"|\'[^\']*\'))?\s*$', val)
    if m:
        return m.group(1)
    return val.split()[0]


def collect_markdown_files(repo_root: Path) -> list[Path]:
    """Collect tracked/repo Markdown files under root, docs, .agents, brands, and campaigns."""
    files: set[Path] = set()
    for top_md in repo_root.glob("*.md"):
        if top_md.is_file():
            files.add(top_md.resolve())

    for subdir_name in ("docs", ".agents", "brands", "campaigns"):
        sub = repo_root / subdir_name
        if not sub.is_dir():
            continue
        for md in sub.rglob("*.md"):
            if not md.is_file():
                continue
            # Skip gitignored binary media directories if any
            if "media" in md.relative_to(repo_root).parts:
                continue
            files.add(md.resolve())

    return sorted(files)


def check_docs(repo_root: Path) -> dict[str, Any]:
    md_files = collect_markdown_files(repo_root)
    anchor_cache: dict[Path, set[str]] = {}
    errors: list[dict[str, Any]] = []
    links_checked = 0

    def _get_anchors(path: Path) -> set[str]:
        resolved = path.resolve()
        if resolved not in anchor_cache:
            anchor_cache[resolved] = extract_anchors(resolved)
        return anchor_cache[resolved]

    for md_path in md_files:
        rel_src = str(md_path.relative_to(repo_root))
        text = md_path.read_text(encoding="utf-8", errors="replace")

        in_fence = False
        fence_char = ""
        fence_len = 0

        for lineno, line in enumerate(text.splitlines(), start=1):
            fm = FENCE_RE.match(line)
            if not in_fence and fm:
                in_fence = True
                fence_char = fm.group(1)[0]
                fence_len = len(fm.group(1))
                continue
            if in_fence:
                stripped = line.lstrip()
                if (
                    stripped.startswith(fence_char * fence_len)
                    and stripped.strip(fence_char).strip() == ""
                ):
                    in_fence = False
                continue

            scrubbed = _replace_inline_code(line)
            for match in LINK_RE.finditer(scrubbed):
                target = _parse_link_target(match.group(1))
                if not target:
                    continue
                low_target = target.lower()
                if any(low_target.startswith(scheme) for scheme in SKIP_SCHEMES):
                    continue

                links_checked += 1

                if "#" in target:
                    path_part, fragment = target.split("#", 1)
                else:
                    path_part, fragment = target, ""

                # Drop optional query string if present on local link
                path_part = path_part.split("?", 1)[0]
                path_part_unquoted = urllib.parse.unquote(path_part)

                if not path_part_unquoted:
                    dest = md_path
                elif path_part_unquoted.startswith("/"):
                    dest = (repo_root / path_part_unquoted.lstrip("/")).resolve()
                else:
                    dest = (md_path.parent / path_part_unquoted).resolve()

                if not dest.exists():
                    errors.append(
                        {
                            "file": rel_src,
                            "line": lineno,
                            "target": target,
                            "reason": "target path does not exist",
                        }
                    )
                    continue

                if fragment:
                    frag_norm = urllib.parse.unquote(fragment).strip().lower()
                    if dest.is_file() and dest.suffix.lower() == ".md":
                        valid_anchors = _get_anchors(dest)
                        if frag_norm not in valid_anchors:
                            errors.append(
                                {
                                    "file": rel_src,
                                    "line": lineno,
                                    "target": target,
                                    "reason": f"heading anchor '#{fragment}' not found in {dest.name}",
                                }
                            )

    return {
        "ok": len(errors) == 0,
        "repo_root": str(repo_root),
        "files_scanned": len(md_files),
        "links_checked": links_checked,
        "errors": errors,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Verify relative Markdown links and GitHub heading anchors offline."
    )
    parser.add_argument(
        "repo_root",
        nargs="?",
        default=".",
        help="Path to repository root (default: current directory).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="Emit check report as JSON.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    root = Path(args.repo_root).resolve()
    if not root.is_dir():
        msg = f"repository root directory not found: {root}"
        if args.as_json:
            print(json.dumps({"ok": False, "error": msg}, indent=2))
        else:
            print(f"ERROR: {msg}", file=sys.stderr)
        return 2

    report = check_docs(root)
    if args.as_json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        state = "OK" if report["ok"] else "FAIL"
        print(
            f"[{state}] docs check ({root}): "
            f"files={report['files_scanned']}, links={report['links_checked']}, "
            f"errors={len(report['errors'])}"
        )
        for err in report["errors"]:
            print(
                f"  {err['file']}:{err['line']} -> {err['target']} ({err['reason']})"
            )

    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
