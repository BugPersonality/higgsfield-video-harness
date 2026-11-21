#!/usr/bin/env python3
"""Deterministic taste-log.md parser and taste-active.md compiler (0 LLM tokens)."""

from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import argparse
import hashlib
import importlib.util
import json
import re
from pathlib import Path
from typing import Any

FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")

STEERING_BULLET_RE = re.compile(
    r"^(\s*)[-*]\s+(?:\*\*|__)?"
    r"(Approved\s*/\s*LOCKED|More\s+of|Change\s*/\s*Steer|Never)"
    r"(?:\*\*|__)?\s*:\s*(?:\*\*|__)?\s*(.*)$",
    re.IGNORECASE,
)

SUPERSEDES_BULLET_RE = re.compile(
    r"^(\s*)[-*]\s+(?:\*\*|__)?Supersedes(?:\*\*|__)?\s*:\s*(?:\*\*|__)?\s*(.*)$",
    re.IGNORECASE,
)

SUPERSEDE_TOKEN_RE = re.compile(
    r"^(TL-\d+)(?:\[([^\]]+)\])?(?:\s*\(([^)]+)\))?$",
    re.IGNORECASE,
)

ACTIVE_META_RE = re.compile(
    r"<!--\s*compiled-from:\s*([^\s|]+)\s*\|\s*source_hash:\s*([0-9a-f]{12})\s*"
    r"\|\s*entries:\s*(\d+)\s*\|\s*active:\s*(\d+)\s*\|\s*superseded:\s*(\d+)\s*-->"
)

CANONICAL_CATEGORIES = (
    "Approved / LOCKED",
    "More of",
    "Change / Steer",
    "Never",
)

CATEGORY_ALIASES = {
    "approved / locked": "Approved / LOCKED",
    "approved/locked": "Approved / LOCKED",
    "approved": "Approved / LOCKED",
    "locked": "Approved / LOCKED",
    "more of": "More of",
    "change / steer": "Change / Steer",
    "change/steer": "Change / Steer",
    "change": "Change / Steer",
    "steer": "Change / Steer",
    "never": "Never",
}

SECTION_TITLES = {
    "Approved / LOCKED": "Active LOCKED",
    "More of": "More Of",
    "Change / Steer": "Active Steer",
    "Never": "Never",
}

DEFAULT_ACTIVE_MAX_LINES = 80


def _load_check_brief():
    mod_path = Path(__file__).resolve().with_name("check-brief.py")
    spec = importlib.util.spec_from_file_location("check_brief", mod_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load sibling module: {mod_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_CHECK_BRIEF = _load_check_brief()


def _normalize_category(raw: str) -> str | None:
    cleaned = re.sub(r"\s+", " ", raw.strip()).lower()
    return CATEGORY_ALIASES.get(cleaned)


def _tl_num(tl_id: str) -> int:
    m = re.match(r"^TL-(\d+)$", tl_id.upper())
    return int(m.group(1)) if m else -1


def compute_source_hash(text: str) -> str:
    """Stable 12-hex SHA-256 digest of taste-log.md content (newline-normalized)."""
    normalized = text.replace("\r\n", "\n").encode("utf-8")
    return hashlib.sha256(normalized).hexdigest()[:12]


def _split_supersede_clauses(raw: str) -> list[str]:
    """Split comma/semicolon-separated Supersedes clauses while ignoring commas inside (...) or [...]."""
    clauses: list[str] = []
    buf: list[str] = []
    paren_depth = 0
    bracket_depth = 0
    for ch in raw:
        if ch == "(":
            paren_depth += 1
            buf.append(ch)
        elif ch == ")" and paren_depth > 0:
            paren_depth -= 1
            buf.append(ch)
        elif ch == "[":
            bracket_depth += 1
            buf.append(ch)
        elif ch == "]" and bracket_depth > 0:
            bracket_depth -= 1
            buf.append(ch)
        elif ch in (",", ";") and paren_depth == 0 and bracket_depth == 0:
            part = "".join(buf).strip()
            if part:
                clauses.append(part)
            buf = []
        else:
            buf.append(ch)
    tail = "".join(buf).strip()
    if tail:
        clauses.append(tail)
    return clauses


def _format_bullet_parts(parts: list[str]) -> str:
    """Flatten multi-line bullet continuations into a clean, compact single-line summary."""
    cleaned_parts: list[str] = []
    for raw in parts:
        item = raw.strip()
        if not item:
            continue
        item = re.sub(r"^[-*]\s+", "", item).strip()
        if item:
            cleaned_parts.append(item)
    if not cleaned_parts:
        return ""
    if len(cleaned_parts) == 1:
        return cleaned_parts[0]
    if cleaned_parts[0].endswith(":"):
        return f"{cleaned_parts[0]} {'; '.join(cleaned_parts[1:])}"
    return "; ".join(cleaned_parts)


def parse_taste_log(taste_path: Path) -> dict[str, Any]:
    """Parse and validate taste-log.md H1, TL-<NN> entries, bullets, and Supersedes graph."""
    text = taste_path.read_text(encoding="utf-8")
    source_hash = compute_source_hash(text)
    lines = text.splitlines()

    errors: list[str] = []
    warnings: list[str] = []

    h1_title: str | None = None
    brand_seed: str | None = None
    raw_entries: list[tuple[str, list[str]]] = []
    current_heading: str | None = None
    current_lines: list[str] = []

    in_fence = False
    fence_char = ""
    fence_len = 0

    for line in lines:
        fm = FENCE_RE.match(line)
        if not in_fence and fm:
            in_fence = True
            fence_char = fm.group(1)[0]
            fence_len = len(fm.group(1))
            if current_heading is not None:
                current_lines.append(line)
            continue
        if in_fence:
            stripped = line.lstrip()
            if (
                stripped.startswith(fence_char * fence_len)
                and stripped.strip(fence_char).strip() == ""
            ):
                in_fence = False
            if current_heading is not None:
                current_lines.append(line)
            continue

        if h1_title is None and line.startswith("# ") and not line.startswith("## "):
            m_h1 = re.match(r"^#\s+Taste\s+Log:\s*(.+?)\s*$", line)
            if m_h1:
                h1_title = m_h1.group(1).strip()
            else:
                errors.append(
                    f"taste-log.md: H1 must match '^# Taste Log: <title>', got '{line.strip()}'"
                )
                h1_title = ""
            continue

        if brand_seed is None and current_heading is None:
            m_seed = re.match(r"^Brand\s+taste\s+seed:\s*(.+?)\s*$", line, re.IGNORECASE)
            if m_seed:
                brand_seed = m_seed.group(1).strip()
                continue

        if re.match(r"^##\s+", line):
            if current_heading is not None:
                raw_entries.append((current_heading, current_lines))
                current_heading = None
                current_lines = []
            continue

        if re.match(r"^###\s+", line):
            if current_heading is not None:
                raw_entries.append((current_heading, current_lines))
            heading_body = line[3:].strip()
            if heading_body.upper().startswith("TL-"):
                current_heading = heading_body
                current_lines = []
            else:
                current_heading = None
                current_lines = []
            continue

        if current_heading is not None:
            current_lines.append(line)

    if current_heading is not None:
        raw_entries.append((current_heading, current_lines))

    if h1_title is None or (h1_title != "" and _CHECK_BRIEF.is_placeholder(h1_title)):
        errors.append(
            "taste-log.md: missing or placeholder H1 heading matching '^# Taste Log: <title>'"
        )

    seen_ids: set[str] = set()
    entries: list[dict[str, Any]] = []

    for raw_heading, body_lines in raw_entries:
        m_id = re.match(r"^(TL-\d+)(?:\b|[\s(—–:-]|$)", raw_heading, re.IGNORECASE)
        if not m_id:
            errors.append(
                f"taste-log.md: invalid entry heading '### {raw_heading}' (expected '### TL-<NN> ...')"
            )
            continue

        tl_id = m_id.group(1).upper()
        if tl_id in seen_ids:
            errors.append(f"taste-log.md: duplicate taste log entry ID '{tl_id}'")
        seen_ids.add(tl_id)

        bullets: list[dict[str, str]] = []
        supersedes: list[dict[str, Any]] = []
        has_steering = False

        idx = 0
        total_lines = len(body_lines)
        while idx < total_lines:
            line = body_lines[idx]

            sup_m = SUPERSEDES_BULLET_RE.match(line)
            if sup_m:
                base_indent = len(sup_m.group(1))
                sup_parts: list[str] = []
                inline_sup = sup_m.group(2).strip()
                if inline_sup:
                    sup_parts.append(inline_sup)
                idx += 1
                while idx < total_lines:
                    nxt = body_lines[idx]
                    if not nxt.strip():
                        idx += 1
                        continue
                    nxt_indent = len(nxt) - len(nxt.lstrip(" "))
                    if (
                        nxt_indent > base_indent
                        and not STEERING_BULLET_RE.match(nxt)
                        and not SUPERSEDES_BULLET_RE.match(nxt)
                    ):
                        sup_parts.append(nxt.strip())
                        idx += 1
                    else:
                        break
                raw_sup = " ".join(sup_parts).strip()
                cleaned_sup = raw_sup.strip("`").strip().rstrip(".")
                if cleaned_sup and cleaned_sup.lower() not in {"none", "-", "n/a"}:
                    for clause in _split_supersede_clauses(raw_sup):
                        clause_clean = clause.strip().strip("`").rstrip(".").strip()
                        if not clause_clean:
                            continue
                        tm = SUPERSEDE_TOKEN_RE.match(clause_clean)
                        if not tm:
                            errors.append(
                                f"taste-log.md ({tl_id}): invalid Supersedes clause '{clause_clean}' "
                                "(expected 'TL-NN', 'TL-NN[Category]', or 'TL-NN (scope)')"
                            )
                            continue
                        target_id = tm.group(1).upper()
                        raw_cat = tm.group(2)
                        scope_note = tm.group(3).strip() if tm.group(3) else None
                        cat_norm: str | None = None
                        if raw_cat is not None:
                            cat_norm = _normalize_category(raw_cat)
                            if cat_norm is None:
                                errors.append(
                                    f"taste-log.md ({tl_id}): unknown category '{raw_cat}' in Supersedes "
                                    f"clause '{clause_clean}' (expected one of {list(CANONICAL_CATEGORIES)})"
                                )
                                continue
                        supersedes.append(
                            {
                                "target": target_id,
                                "category": cat_norm,
                                "scope": scope_note,
                                "raw": clause_clean,
                            }
                        )
                continue

            sm = STEERING_BULLET_RE.match(line)
            if not sm:
                idx += 1
                continue

            base_indent = len(sm.group(1))
            category = _normalize_category(sm.group(2)) or sm.group(2).strip()
            val_parts: list[str] = []
            inline_val = sm.group(3).strip()
            if inline_val:
                val_parts.append(inline_val)
            idx += 1
            while idx < total_lines:
                nxt = body_lines[idx]
                if not nxt.strip():
                    idx += 1
                    continue
                nxt_indent = len(nxt) - len(nxt.lstrip(" "))
                if (
                    nxt_indent > base_indent
                    and not STEERING_BULLET_RE.match(nxt)
                    and not SUPERSEDES_BULLET_RE.match(nxt)
                ):
                    val_parts.append(nxt.strip())
                    idx += 1
                else:
                    break

            combined = _format_bullet_parts(val_parts)
            cleaned_none = re.sub(r"^[-*]\s+", "", combined).strip().rstrip(".").lower()
            if (
                combined
                and cleaned_none not in {"none", "-", "n/a"}
                and not _CHECK_BRIEF.is_placeholder(combined)
            ):
                has_steering = True
                bullets.append({"category": category, "text": combined})

        if not has_steering:
            errors.append(
                f"taste-log.md ({tl_id}): must include at least one non-placeholder steering bullet "
                "('Approved / LOCKED', 'More of', 'Change / Steer', or 'Never')"
            )

        entries.append(
            {
                "id": tl_id,
                "num": _tl_num(tl_id),
                "heading": raw_heading,
                "supersedes": supersedes,
                "bullets": bullets,
            }
        )

    # Validate Supersedes graph: target exists, no self-reference, no forward reference
    id_order = {e["id"]: pos for pos, e in enumerate(entries)}
    for pos, entry in enumerate(entries):
        src_id = entry["id"]
        for sup in entry["supersedes"]:
            tgt_id = sup["target"]
            if tgt_id == src_id:
                errors.append(f"taste-log.md ({src_id}): entry cannot supersede itself")
            elif tgt_id not in id_order:
                errors.append(
                    f"taste-log.md ({src_id}): Supersedes references unknown entry '{tgt_id}'"
                )
            elif id_order[tgt_id] > pos:
                errors.append(
                    f"taste-log.md ({src_id}): Supersedes references later entry '{tgt_id}' "
                    "(only earlier TL-NN entries can be superseded)"
                )

    return {
        "ok": len(errors) == 0,
        "path": str(taste_path),
        "title": h1_title or "",
        "brand_seed": brand_seed or "none",
        "source_hash": source_hash,
        "line_count": len(lines),
        "entry_count": len(entries),
        "entries": entries,
        "warnings": warnings,
        "errors": errors,
    }


def compile_active_taste(
    parsed: dict[str, Any], *, max_lines: int = DEFAULT_ACTIVE_MAX_LINES
) -> dict[str, Any]:
    """Compile parsed taste-log.md into a conflict-free taste-active.md snapshot."""
    entries: list[dict[str, Any]] = parsed["entries"]

    full_superseded: dict[str, list[str]] = {}
    cat_superseded: dict[tuple[str, str], list[str]] = {}
    scoped_notes: dict[str, list[tuple[str, str]]] = {}
    history_lines: list[str] = []

    for entry in entries:
        src_id = entry["id"]
        for sup in entry["supersedes"]:
            tgt = sup["target"]
            cat = sup["category"]
            scope = sup["scope"]
            if cat is not None:
                cat_superseded.setdefault((tgt, cat), []).append(src_id)
                label = f"`{tgt}[{cat}]`"
                if scope:
                    label += f" ({scope})"
                history_lines.append(f"- {label} -> superseded by `{src_id}`")
            elif scope is not None:
                scoped_notes.setdefault(tgt, []).append((src_id, scope))
                history_lines.append(f"- `{tgt}` ({scope}) -> partially superseded by `{src_id}`")
            else:
                full_superseded.setdefault(tgt, []).append(src_id)
                history_lines.append(f"- `{tgt}` -> superseded by `{src_id}`")

    grouped: dict[str, list[str]] = {cat: [] for cat in CANONICAL_CATEGORIES}
    active_entry_ids: list[str] = []

    for entry in entries:
        eid = entry["id"]
        if eid in full_superseded:
            continue
        notes_for_entry = scoped_notes.get(eid) or []
        note_suffix = ""
        if notes_for_entry:
            parts = [f"{by}: {sc}" for by, sc in notes_for_entry]
            note_suffix = f" *(partially superseded by {', '.join(parts)})*"

        kept_any = False
        for b in entry["bullets"]:
            cat = b["category"]
            if (eid, cat) in cat_superseded:
                continue
            if cat not in grouped:
                continue
            grouped[cat].append(f"- **[{eid}]** {b['text']}{note_suffix}")
            kept_any = True
        if kept_any:
            active_entry_ids.append(eid)

    superseded_count = len(full_superseded)
    active_count = len(active_entry_ids)
    total_entries = len(entries)

    out_lines: list[str] = [
        f"# Active Taste Snapshot: {parsed['title'] or 'Untitled Campaign'}",
        "",
        (
            f"<!-- compiled-from: taste-log.md | source_hash: {parsed['source_hash']} "
            f"| entries: {total_entries} | active: {active_count} | superseded: {superseded_count} -->"
        ),
        "",
        f"Brand taste seed: {parsed['brand_seed']}",
        "",
        "Compiled active rules from `taste-log.md` (read this first; open `taste-log.md` for full history).",
    ]

    if total_entries == 0:
        out_lines.extend(["", "_No `TL-NN` entries recorded yet._"])
    else:
        for cat in CANONICAL_CATEGORIES:
            items = grouped[cat]
            if not items:
                continue
            out_lines.append("")
            out_lines.append(f"## {SECTION_TITLES[cat]}")
            out_lines.append("")
            out_lines.extend(items)

    if history_lines:
        out_lines.append("")
        out_lines.append("## Superseded History")
        out_lines.append("")
        out_lines.extend(history_lines)

    markdown = "\n".join(out_lines) + "\n"
    compiled_line_count = len(out_lines)
    warnings: list[str] = []
    if compiled_line_count > max_lines:
        warnings.append(
            f"taste-active.md has {compiled_line_count} lines (soft cap <= {max_lines}); "
            "mark obsolete TL-NN entries with 'Supersedes:' or consolidate via studio-retro"
        )

    return {
        "markdown": markdown,
        "line_count": compiled_line_count,
        "source_hash": parsed["source_hash"],
        "entry_count": total_entries,
        "active_entry_count": active_count,
        "superseded_entry_count": superseded_count,
        "superseded_ids": sorted(full_superseded.keys()),
        "warnings": warnings,
    }


def extract_active_metadata(active_path: Path) -> dict[str, Any] | None:
    """Read compiled metadata header from an existing taste-active.md."""
    if not active_path.is_file():
        return None
    text = active_path.read_text(encoding="utf-8")
    m = ACTIVE_META_RE.search(text)
    if not m:
        return None
    return {
        "compiled_from": m.group(1),
        "source_hash": m.group(2),
        "entries": int(m.group(3)),
        "active": int(m.group(4)),
        "superseded": int(m.group(5)),
        "line_count": len(text.splitlines()),
    }


def resolve_campaign_dir(target: str | Path) -> Path:
    p = Path(target)
    if p.is_file():
        return p.resolve().parent
    return p.resolve()


def compile_campaign_memory(
    target: str | Path,
    *,
    check_only: bool = False,
    max_lines: int = DEFAULT_ACTIVE_MAX_LINES,
    write_file: bool = True,
) -> dict[str, Any]:
    campaign_dir = resolve_campaign_dir(target)
    taste_path = campaign_dir / "taste-log.md"
    active_path = campaign_dir / "taste-active.md"

    if not taste_path.is_file():
        return {
            "ok": False,
            "campaign_dir": str(campaign_dir),
            "taste_log_path": str(taste_path),
            "taste_active_path": str(active_path),
            "warnings": [],
            "errors": [f"taste-log.md not found: {taste_path}"],
        }

    parsed = parse_taste_log(taste_path)
    errors = list(parsed["errors"])
    warnings = list(parsed["warnings"])
    if errors:
        return {
            "ok": False,
            "campaign_dir": str(campaign_dir),
            "taste_log_path": str(taste_path),
            "taste_active_path": str(active_path),
            "source_hash": parsed["source_hash"],
            "entry_count": parsed["entry_count"],
            "warnings": warnings,
            "errors": errors,
        }

    compiled = compile_active_taste(parsed, max_lines=max_lines)
    warnings.extend(compiled["warnings"])

    if check_only:
        meta = extract_active_metadata(active_path)
        if meta is None:
            errors.append(
                f"taste-active.md is missing or lacks compiled header: {active_path} "
                "(run `make memory-compile CAMPAIGN=<slug>`)"
            )
        elif meta["source_hash"] != parsed["source_hash"]:
            errors.append(
                f"taste-active.md is stale (recorded hash {meta['source_hash']} != "
                f"taste-log.md hash {parsed['source_hash']}); run `make memory-compile CAMPAIGN=<slug>`"
            )
        return {
            "ok": len(errors) == 0,
            "checked": True,
            "campaign_dir": str(campaign_dir),
            "taste_log_path": str(taste_path),
            "taste_active_path": str(active_path),
            "source_hash": parsed["source_hash"],
            "entry_count": compiled["entry_count"],
            "active_entry_count": compiled["active_entry_count"],
            "superseded_entry_count": compiled["superseded_entry_count"],
            "line_count": compiled["line_count"],
            "warnings": warnings,
            "errors": errors,
        }

    if write_file:
        tmp_path = active_path.with_suffix(".md.tmp")
        tmp_path.write_text(compiled["markdown"], encoding="utf-8")
        tmp_path.replace(active_path)

    return {
        "ok": True,
        "written": write_file,
        "campaign_dir": str(campaign_dir),
        "taste_log_path": str(taste_path),
        "taste_active_path": str(active_path),
        "source_hash": parsed["source_hash"],
        "entry_count": compiled["entry_count"],
        "active_entry_count": compiled["active_entry_count"],
        "superseded_entry_count": compiled["superseded_entry_count"],
        "line_count": compiled["line_count"],
        "markdown": compiled["markdown"],
        "warnings": warnings,
        "errors": [],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compile campaigns/<slug>/taste-log.md into a conflict-free taste-active.md snapshot."
    )
    parser.add_argument(
        "target",
        help="Path to campaign directory or taste-log.md file.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify taste-active.md exists and matches current taste-log.md without writing.",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Print compiled taste-active.md to stdout without modifying files.",
    )
    parser.add_argument(
        "--max-lines",
        type=int,
        default=DEFAULT_ACTIVE_MAX_LINES,
        help=f"Soft line cap warning threshold for taste-active.md (default: {DEFAULT_ACTIVE_MAX_LINES}).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="Emit compile/check summary as JSON.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.check and args.stdout:
        print("ERROR: --check and --stdout cannot be combined", file=sys.stderr)
        return 2

    report = compile_campaign_memory(
        args.target,
        check_only=args.check,
        max_lines=args.max_lines,
        write_file=not args.stdout,
    )

    if args.stdout:
        if not report["ok"]:
            for err in report["errors"]:
                print(f"ERROR: {err}", file=sys.stderr)
            return 1
        sys.stdout.write(report["markdown"])
        return 0

    if args.as_json:
        out = {k: v for k, v in report.items() if k != "markdown"}
        print(json.dumps(out, indent=2, ensure_ascii=False))
    else:
        state = "OK" if report["ok"] else "FAIL"
        action = "checked" if args.check else "compiled"
        if report["ok"]:
            print(
                f"[{state}] {action} {report['taste_active_path']} "
                f"(entries={report['entry_count']}, active={report['active_entry_count']}, "
                f"superseded={report['superseded_entry_count']}, lines={report['line_count']}, "
                f"hash={report['source_hash']})"
            )
        else:
            print(f"[{state}] {report['taste_log_path']}")
        for w in report.get("warnings") or []:
            print(f"  WARN: {w}")
        for e in report.get("errors") or []:
            print(f"  ERROR: {e}")

    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
