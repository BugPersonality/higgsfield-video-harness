#!/usr/bin/env python3
"""Memory hygiene linter (Doc Gardening): validates studio/, brands/*/taste.md, and campaign memory."""

from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import argparse
import datetime
import importlib.util
import json
import re
from pathlib import Path
from typing import Any

DIRECTOR_MAX_LINES = 60
ENGINE_MEMORY_MAX_LINES = 120
BRAND_TASTE_MAX_LINES = 80
DEFAULT_STALE_DAYS = 60

VALID_ENGINE_STATUSES = frozenset({"active", "stale", "graduated_to_code", "archived"})
VALID_REVIEW_VERDICTS = frozenset({"PASS", "CONCERNS", "FAIL", "REVIEW_HANDOFF_INVALID"})
VALID_DEFECT_CLASSES = frozenset(
    {
        "NONE",
        "MEDIA_TECH_DEFECT",
        "VISUAL_DRIFT_DEFECT",
        "TASTE_REGRESSION",
        "CONTINUITY_DEFECT",
        "POLICY_BLOCK",
        "BUDGET_CAP",
        "CONCERN",
        "FOLLOW_UP",
    }
)

ENG_BULLET_RE = re.compile(
    r"^\s*[-*]\s+\[(ENG-\d+)\]\s+(.+?)\s*$",
    re.IGNORECASE,
)
EV_HEADING_RE = re.compile(
    r"^###\s+(EV-\d+)\s*\((\d{4}-\d{2}-\d{2})\)(?:\s*[—–:-]\s*(.+))?\s*$",
    re.IGNORECASE,
)
RELATIVE_TIME_RE = re.compile(
    r"(?<!\w)(yesterday|last\s+week|last\s+month|two\s+days\s+ago|a\s+few\s+days\s+ago)(?!\w)",
    re.IGNORECASE,
)
REQUIRED_EV_FIELDS = ("Trigger trace", "Change", "Expected effect", "Retire / Revisit when")


def _load_memory_compile():
    mod_path = Path(__file__).resolve().with_name("memory_compile.py")
    spec = importlib.util.spec_from_file_location("memory_compile", mod_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load sibling module: {mod_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_MEMORY_COMPILE = _load_memory_compile()


def _parse_iso_date(raw: str) -> datetime.date | None:
    try:
        return datetime.date.fromisoformat(raw.strip())
    except ValueError:
        return None


def parse_engine_memory(path: Path) -> dict[str, Any]:
    """Parse ACE-format studio/engine-memory.md entries."""
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    errors: list[str] = []
    entries: list[dict[str, Any]] = []
    seen_ids: set[str] = set()

    if len(lines) > ENGINE_MEMORY_MAX_LINES:
        errors.append(
            f"studio/engine-memory.md has {len(lines)} lines (must be <= {ENGINE_MEMORY_MAX_LINES} lines)"
        )

    for lineno, line in enumerate(lines, start=1):
        m = ENG_BULLET_RE.match(line)
        if not m:
            continue
        eng_id = m.group(1).upper()
        meta_str = m.group(2)
        if eng_id in seen_ids:
            errors.append(f"studio/engine-memory.md:{lineno}: duplicate entry ID '{eng_id}'")
        seen_ids.add(eng_id)

        kv: dict[str, str] = {}
        for part in meta_str.split("|"):
            part = part.strip()
            if "=" not in part:
                errors.append(
                    f"studio/engine-memory.md:{lineno} ({eng_id}): malformed metadata segment '{part}' (expected key=value)"
                )
                continue
            k, _, v = part.partition("=")
            kv[k.strip().lower()] = v.strip()

        model = kv.get("model", "")
        if not model:
            errors.append(f"studio/engine-memory.md:{lineno} ({eng_id}): missing 'model=<slug>'")

        helpful: int | None = None
        harmful: int | None = None
        for counter_name in ("helpful", "harmful"):
            raw_c = kv.get(counter_name)
            if raw_c is None or not re.match(r"^\d+$", raw_c):
                errors.append(
                    f"studio/engine-memory.md:{lineno} ({eng_id}): '{counter_name}' must be a non-negative integer"
                )
            else:
                val_i = int(raw_c)
                if counter_name == "helpful":
                    helpful = val_i
                else:
                    harmful = val_i

        verified_raw = kv.get("verified", "")
        verified_date = _parse_iso_date(verified_raw) if verified_raw else None
        if verified_date is None:
            errors.append(
                f"studio/engine-memory.md:{lineno} ({eng_id}): 'verified' must be ISO YYYY-MM-DD, got {verified_raw!r}"
            )

        status = kv.get("status", "").lower()
        if status not in VALID_ENGINE_STATUSES:
            errors.append(
                f"studio/engine-memory.md:{lineno} ({eng_id}): invalid status {status!r} "
                f"(expected one of {sorted(VALID_ENGINE_STATUSES)})"
            )

        entries.append(
            {
                "id": eng_id,
                "line": lineno,
                "model": model,
                "helpful": helpful,
                "harmful": harmful,
                "verified": verified_raw,
                "verified_date": verified_date,
                "status": status,
            }
        )

    return {
        "line_count": len(lines),
        "entries": entries,
        "errors": errors,
    }


def _validate_director(path: Path, errors: list[str], warnings: list[str]) -> dict[str, Any]:
    if not path.is_file():
        errors.append("missing required studio memory file: studio/director.md")
        return {"present": False, "line_count": 0}
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not text.strip():
        errors.append("studio/director.md is empty")
    if len(lines) > DIRECTOR_MAX_LINES:
        errors.append(
            f"studio/director.md has {len(lines)} lines (must be <= {DIRECTOR_MAX_LINES} lines)"
        )
    if not any(ln.startswith("# ") and not ln.startswith("## ") for ln in lines):
        errors.append("studio/director.md: missing H1 heading")
    if RELATIVE_TIME_RE.search(text):
        warnings.append(
            "studio/director.md: contains relative time phrasing; use absolute ISO dates (YYYY-MM-DD)"
        )
    return {"present": True, "line_count": len(lines)}


def _validate_evolution_log(path: Path, errors: list[str]) -> dict[str, Any]:
    if not path.is_file():
        errors.append("missing required SIM file: studio/evolution-log.md")
        return {"present": False, "entries": 0}
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    entries: list[tuple[str, str, list[str]]] = []
    cur_id: str | None = None
    cur_date: str = ""
    cur_body: list[str] = []

    for lineno, line in enumerate(lines, start=1):
        if line.startswith("### "):
            if cur_id is not None:
                entries.append((cur_id, cur_date, cur_body))
            m = EV_HEADING_RE.match(line)
            if not m:
                errors.append(
                    f"studio/evolution-log.md:{lineno}: invalid entry heading '{line.strip()}' "
                    "(expected '### EV-<NN> (YYYY-MM-DD) — <title>')"
                )
                cur_id = None
                cur_body = []
                continue
            cur_id = m.group(1).upper()
            cur_date = m.group(2)
            cur_body = []
            if _parse_iso_date(cur_date) is None:
                errors.append(
                    f"studio/evolution-log.md:{lineno} ({cur_id}): invalid ISO date '{cur_date}'"
                )
        elif cur_id is not None:
            cur_body.append(line)

    if cur_id is not None:
        entries.append((cur_id, cur_date, cur_body))

    seen_ids: set[str] = set()
    for ev_id, _, body in entries:
        if ev_id in seen_ids:
            errors.append(f"studio/evolution-log.md: duplicate entry ID '{ev_id}'")
        seen_ids.add(ev_id)
        joined = "\n".join(body)
        for field in REQUIRED_EV_FIELDS:
            pat = re.compile(rf"^[-*]\s+(?:\*\*|__)?{re.escape(field)}(?:\*\*|__)?\s*:", re.IGNORECASE | re.MULTILINE)
            if not pat.search(joined):
                errors.append(
                    f"studio/evolution-log.md ({ev_id}): missing required field '{field}'"
                )

    return {"present": True, "entries": len(entries)}


def _validate_brand_taste(
    taste_path: Path, repo_root: Path, errors: list[str], warnings: list[str]
) -> None:
    rel = str(taste_path.relative_to(repo_root))
    text = taste_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if len(lines) > BRAND_TASTE_MAX_LINES:
        errors.append(
            f"{rel} has {len(lines)} lines (must be <= {BRAND_TASTE_MAX_LINES} lines; "
            "keep campaign plots in taste-log.md and engine notes in studio/engine-memory.md)"
        )
    has_h1 = any(re.match(r"^#\s+Brand\s+Taste\s+Memory:\s*.+", ln) for ln in lines)
    if not has_h1:
        errors.append(f"{rel}: missing H1 matching '^# Brand Taste Memory: <brand>'")
    has_bullet = any(_MEMORY_COMPILE.STEERING_BULLET_RE.match(ln) for ln in lines)
    if not has_bullet:
        errors.append(
            f"{rel}: must include at least one canonical steering bullet "
            "('Approved / LOCKED', 'More of', 'Change / Steer', or 'Never')"
        )
    if RELATIVE_TIME_RE.search(text):
        warnings.append(
            f"{rel}: contains relative time phrasing; replace with absolute ISO dates (YYYY-MM-DD)"
        )


def _validate_review_log(
    log_path: Path, repo_root: Path, errors: list[str]
) -> int:
    rel = str(log_path.relative_to(repo_root))
    count = 0
    for lineno, raw in enumerate(log_path.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw.strip():
            continue
        try:
            obj = json.loads(raw)
        except json.JSONDecodeError as exc:
            errors.append(f"{rel}:{lineno}: malformed JSONL ({exc})")
            continue
        if not isinstance(obj, dict):
            errors.append(f"{rel}:{lineno}: expected JSON object")
            continue
        count += 1
        for req_key in ("ts", "round", "asset_id", "verdict", "defect_class"):
            val = obj.get(req_key)
            if not isinstance(val, str) or not val.strip():
                errors.append(f"{rel}:{lineno}: missing or empty required field '{req_key}'")
        verdict = obj.get("verdict")
        if isinstance(verdict, str) and verdict not in VALID_REVIEW_VERDICTS:
            errors.append(f"{rel}:{lineno}: invalid verdict {verdict!r}")
        defect = obj.get("defect_class")
        if isinstance(defect, str) and defect not in VALID_DEFECT_CLASSES:
            errors.append(f"{rel}:{lineno}: invalid defect_class {defect!r}")
    return count


def validate_memory(
    repo_root: Path,
    *,
    stale_days: int = DEFAULT_STALE_DAYS,
    as_of: datetime.date | None = None,
) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    today = as_of or datetime.date.today()

    studio_dir = repo_root / "studio"
    director_info = _validate_director(studio_dir / "director.md", errors, warnings)

    eng_path = studio_dir / "engine-memory.md"
    eng_entries_count = 0
    stale_engine_ids: list[str] = []
    if not eng_path.is_file():
        errors.append("missing required studio memory file: studio/engine-memory.md")
    else:
        eng = parse_engine_memory(eng_path)
        errors.extend(eng["errors"])
        eng_entries_count = len(eng["entries"])
        for entry in eng["entries"]:
            vdate = entry.get("verified_date")
            if entry["status"] == "active" and isinstance(vdate, datetime.date):
                age = (today - vdate).days
                if age > stale_days:
                    stale_engine_ids.append(entry["id"])
                    warnings.append(
                        f"studio/engine-memory.md ({entry['id']} / {entry['model']}): "
                        f"verified {entry['verified']} ({age}d ago > {stale_days}d); "
                        "re-verify on current Higgsfield models or mark status=stale"
                    )

    ev_info = _validate_evolution_log(studio_dir / "evolution-log.md", errors)

    # Brands
    brands_checked = 0
    brands_dir = repo_root / "brands"
    if brands_dir.is_dir():
        for taste_md in sorted(brands_dir.glob("*/taste.md")):
            brands_checked += 1
            _validate_brand_taste(taste_md, repo_root, errors, warnings)

    # Campaigns
    campaigns_checked = 0
    review_logs_checked = 0
    campaigns_dir = repo_root / "campaigns"
    if campaigns_dir.is_dir():
        for camp_dir in sorted(p for p in campaigns_dir.iterdir() if p.is_dir()):
            taste_log = camp_dir / "taste-log.md"
            if taste_log.is_file():
                campaigns_checked += 1
                rel_camp = str(camp_dir.relative_to(repo_root))
                parsed = _MEMORY_COMPILE.parse_taste_log(taste_log)
                for err in parsed["errors"]:
                    errors.append(f"{rel_camp}/{err}")
                active_path = camp_dir / "taste-active.md"
                if active_path.is_file():
                    meta = _MEMORY_COMPILE.extract_active_metadata(active_path)
                    if meta is None:
                        errors.append(
                            f"{rel_camp}/taste-active.md: missing compiled header; "
                            f"run `make memory-compile CAMPAIGN={camp_dir.name}`"
                        )
                    elif meta["source_hash"] != parsed["source_hash"]:
                        errors.append(
                            f"{rel_camp}/taste-active.md: stale snapshot "
                            f"({meta['source_hash']} != {parsed['source_hash']}); "
                            f"run `make memory-compile CAMPAIGN={camp_dir.name}`"
                        )
                    elif meta["line_count"] > _MEMORY_COMPILE.DEFAULT_ACTIVE_MAX_LINES:
                        warnings.append(
                            f"{rel_camp}/taste-active.md has {meta['line_count']} lines "
                            f"(soft cap <= {_MEMORY_COMPILE.DEFAULT_ACTIVE_MAX_LINES})"
                        )
                elif parsed["entry_count"] >= 4:
                    warnings.append(
                        f"{rel_camp}/taste-log.md has {parsed['entry_count']} entries without "
                        f"taste-active.md; run `make memory-compile CAMPAIGN={camp_dir.name}`"
                    )

            review_log = camp_dir / "qc" / "review-log.jsonl"
            if review_log.is_file():
                review_logs_checked += _validate_review_log(review_log, repo_root, errors)

    return {
        "ok": len(errors) == 0,
        "repo_root": str(repo_root),
        "as_of": today.isoformat(),
        "stale_days": stale_days,
        "checked": {
            "director_lines": director_info["line_count"],
            "engine_entries": eng_entries_count,
            "stale_engine_ids": stale_engine_ids,
            "evolution_entries": ev_info["entries"],
            "brand_taste_files": brands_checked,
            "campaigns": campaigns_checked,
            "review_log_records": review_logs_checked,
        },
        "warnings": warnings,
        "errors": errors,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate studio/, brands/*/taste.md, campaign taste snapshots, and qc/review-log.jsonl."
    )
    parser.add_argument(
        "repo_root",
        nargs="?",
        default=".",
        help="Path to repository root (default: current directory).",
    )
    parser.add_argument(
        "--stale-days",
        type=int,
        default=DEFAULT_STALE_DAYS,
        help=f"Flag active engine-memory rules older than N days (default: {DEFAULT_STALE_DAYS}).",
    )
    parser.add_argument(
        "--as-of",
        default=None,
        help="Reference ISO date YYYY-MM-DD for staleness checks (default: today).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="Emit validation report as JSON.",
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

    as_of_date: datetime.date | None = None
    if args.as_of:
        as_of_date = _parse_iso_date(args.as_of)
        if as_of_date is None:
            msg = f"invalid --as-of date '{args.as_of}' (expected YYYY-MM-DD)"
            if args.as_json:
                print(json.dumps({"ok": False, "error": msg}, indent=2))
            else:
                print(f"ERROR: {msg}", file=sys.stderr)
            return 2

    report = validate_memory(root, stale_days=args.stale_days, as_of=as_of_date)
    if args.as_json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        state = "OK" if report["ok"] else "FAIL"
        chk = report["checked"]
        print(
            f"[{state}] memory check ({root}): "
            f"director={chk['director_lines']}L, engine={chk['engine_entries']}, "
            f"evolution={chk['evolution_entries']}, brands={chk['brand_taste_files']}, "
            f"campaigns={chk['campaigns']}, reviews={chk['review_log_records']}"
        )
        for w in report["warnings"]:
            print(f"  WARN: {w}")
        for e in report["errors"]:
            print(f"  ERROR: {e}")

    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
