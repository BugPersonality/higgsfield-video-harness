#!/usr/bin/env python3
"""Local stdlib SQLite FTS5 BM25 search across studio/, brands/, and campaigns/ memory files."""

from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import argparse
import json
import re
import sqlite3
from pathlib import Path
from typing import Any

SCOPE_CHOICES = ("all", "studio", "brands", "campaigns")
CAMPAIGN_DOC_NAMES = (
    "brief.md",
    "taste-active.md",
    "taste-log.md",
    "style-bible.md",
    "script.md",
    "storyboard.md",
)


def _chunk_markdown(text: str, rel_path: str) -> list[tuple[str, str]]:
    """Split a Markdown file into logical heading/entry chunks for precise FTS5 hits."""
    chunks: list[tuple[str, str]] = []
    cur_section = "header"
    cur_lines: list[str] = []

    for line in text.splitlines():
        m_head = re.match(r"^(#{1,3})\s+(.+?)\s*$", line)
        m_eng = re.match(r"^\s*[-*]\s+\[(ENG-\d+)\]", line, re.IGNORECASE)
        if m_head:
            if cur_lines and "".join(cur_lines).strip():
                chunks.append((cur_section, "\n".join(cur_lines).strip()))
            cur_section = m_head.group(2).strip()
            cur_lines = [line]
        elif m_eng:
            if cur_lines and "".join(cur_lines).strip():
                chunks.append((cur_section, "\n".join(cur_lines).strip()))
            cur_section = m_eng.group(1).upper()
            cur_lines = [line]
        else:
            cur_lines.append(line)

    if cur_lines and "".join(cur_lines).strip():
        chunks.append((cur_section, "\n".join(cur_lines).strip()))

    return chunks or [(rel_path, text.strip())]


def _collect_documents(repo_root: Path, scope: str) -> list[tuple[str, str, str, str]]:
    """Return list of (scope_tag, rel_path, section, body)."""
    docs: list[tuple[str, str, str, str]] = []

    if scope in ("all", "studio"):
        studio_dir = repo_root / "studio"
        if studio_dir.is_dir():
            for md in sorted(studio_dir.glob("*.md")):
                rel = str(md.relative_to(repo_root))
                for sec, body in _chunk_markdown(md.read_text(encoding="utf-8", errors="replace"), rel):
                    docs.append(("studio", rel, sec, body))

    if scope in ("all", "brands"):
        brands_dir = repo_root / "brands"
        if brands_dir.is_dir():
            for md in sorted(brands_dir.glob("*/*.md")):
                rel = str(md.relative_to(repo_root))
                for sec, body in _chunk_markdown(md.read_text(encoding="utf-8", errors="replace"), rel):
                    docs.append(("brands", rel, sec, body))

    if scope in ("all", "campaigns"):
        camp_root = repo_root / "campaigns"
        if camp_root.is_dir():
            for camp_dir in sorted(p for p in camp_root.iterdir() if p.is_dir()):
                for fname in CAMPAIGN_DOC_NAMES:
                    fpath = camp_dir / fname
                    if not fpath.is_file():
                        continue
                    rel = str(fpath.relative_to(repo_root))
                    for sec, body in _chunk_markdown(fpath.read_text(encoding="utf-8", errors="replace"), rel):
                        docs.append(("campaigns", rel, sec, body))
                rev_log = camp_dir / "qc" / "review-log.jsonl"
                if rev_log.is_file():
                    rel = str(rev_log.relative_to(repo_root))
                    for idx, raw in enumerate(rev_log.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
                        if not raw.strip():
                            continue
                        try:
                            rec = json.loads(raw)
                        except json.JSONDecodeError:
                            continue
                        if isinstance(rec, dict):
                            sec = f"line {idx}: {rec.get('round', '')} {rec.get('asset_id', '')}".strip()
                            body = (
                                f"{rec.get('verdict', '')} {rec.get('defect_class', '')} "
                                f"{rec.get('reopen_owner', '')} {rec.get('summary', '')}"
                            ).strip()
                            docs.append(("campaigns", rel, sec, body))

    return docs


def _build_fts_query(raw_query: str) -> str:
    """Sanitize a free-form query into safe FTS5 token terms (supports Unicode / Cyrillic / hyphens)."""
    tokens = re.findall(r"[^\s\"'()*:^~+-]+", raw_query.strip())
    cleaned = [t.replace('"', "") for t in tokens if t.strip()]
    if not cleaned:
        return ""
    return " ".join(f'"{t}"' for t in cleaned)


def search_memory(
    repo_root: Path,
    query: str,
    *,
    scope: str = "all",
    limit: int = 10,
    db_path: Path | None = None,
) -> dict[str, Any]:
    fts_query = _build_fts_query(query)
    if not fts_query:
        return {
            "ok": False,
            "query": query,
            "scope": scope,
            "error": "query must contain at least one searchable term",
            "hits": [],
        }

    docs = _collect_documents(repo_root, scope)
    conn = sqlite3.connect(str(db_path) if db_path else ":memory:")
    try:
        conn.execute("DROP TABLE IF EXISTS memory_fts")
        conn.execute(
            "CREATE VIRTUAL TABLE memory_fts USING fts5("
            "scope, path, section, body, tokenize='unicode61')"
        )
        conn.executemany(
            "INSERT INTO memory_fts (scope, path, section, body) VALUES (?, ?, ?, ?)",
            docs,
        )
        rows = conn.execute(
            "SELECT scope, path, section, "
            "snippet(memory_fts, 3, '<<', '>>', ' ... ', 24) AS snippet, "
            "bm25(memory_fts) AS score "
            "FROM memory_fts WHERE memory_fts MATCH ? "
            "ORDER BY score LIMIT ?",
            (fts_query, max(1, limit)),
        ).fetchall()
    finally:
        conn.close()

    hits = [
        {
            "scope": r[0],
            "path": r[1],
            "section": r[2],
            "snippet": re.sub(r"\s+", " ", r[3]).strip(),
            "score": round(float(r[4]), 4),
        }
        for r in rows
    ]

    return {
        "ok": True,
        "repo_root": str(repo_root),
        "query": query,
        "fts_query": fts_query,
        "scope": scope,
        "indexed_chunks": len(docs),
        "hit_count": len(hits),
        "hits": hits,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="BM25 full-text search across studio/, brands/, and campaigns/ memory files (SQLite FTS5)."
    )
    parser.add_argument("query", help="Search query (any Unicode terms).")
    parser.add_argument(
        "--root",
        default=".",
        help="Path to repository root (default: current directory).",
    )
    parser.add_argument(
        "--scope",
        choices=SCOPE_CHOICES,
        default="all",
        help="Memory slice to search (default: all).",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Maximum hits to return (default: 10).",
    )
    parser.add_argument(
        "--db",
        default=None,
        help="Optional path to persist the rebuilt SQLite FTS5 index (default: in-memory).",
    )
    parser.add_argument("--json", action="store_true", dest="as_json", help="Emit JSON output.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    if not root.is_dir():
        msg = f"repository root directory not found: {root}"
        if args.as_json:
            print(json.dumps({"ok": False, "error": msg}, indent=2))
        else:
            print(f"ERROR: {msg}", file=sys.stderr)
        return 2

    report = search_memory(
        root,
        args.query,
        scope=args.scope,
        limit=args.limit,
        db_path=Path(args.db) if args.db else None,
    )

    if args.as_json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    elif not report["ok"]:
        print(f"ERROR: {report['error']}", file=sys.stderr)
    else:
        print(
            f"[OK] memory search '{report['query']}' "
            f"(scope={report['scope']}, indexed={report['indexed_chunks']} chunks, hits={report['hit_count']})"
        )
        for idx, hit in enumerate(report["hits"], start=1):
            print(f"  {idx}. [{hit['scope']}] {hit['path']} :: {hit['section']}")
            print(f"     {hit['snippet']}")

    return 0 if report["ok"] else 2


if __name__ == "__main__":
    sys.exit(main())
