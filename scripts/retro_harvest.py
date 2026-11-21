#!/usr/bin/env python3
"""Deterministic Meta-Harness trace harvester for R6 / studio-retro consolidation (0 LLM tokens)."""

from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import argparse
import importlib.util
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


def _load_sibling(filename: str, mod_name: str):
    mod_path = Path(__file__).resolve().with_name(filename)
    spec = importlib.util.spec_from_file_location(mod_name, mod_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load sibling module: {mod_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_CHECK_BRIEF = _load_sibling("check-brief.py", "check_brief")
_MEMORY_COMPILE = _load_sibling("memory_compile.py", "memory_compile")
_CHECK_MEMORY = _load_sibling("check-memory.py", "check_memory")


def _clean_num(val: float) -> int | float:
    return int(val) if float(val).is_integer() else round(val, 2)


def _read_jsonl(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    records: list[dict[str, Any]] = []
    errors: list[str] = []
    if not path.is_file():
        return records, errors
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"{path.name}:{lineno}: malformed JSON ({exc})")
            continue
        if isinstance(obj, dict):
            records.append(obj)
        else:
            errors.append(f"{path.name}:{lineno}: expected JSON object")
    return records, errors


def _collapse_receipts(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_res: dict[str, dict[str, Any]] = {}
    order: list[str] = []
    for idx, rec in enumerate(records):
        rid = str(rec.get("reservation_id") or "").strip() or f"anon-{idx}"
        if rid not in by_res:
            order.append(rid)
        by_res[rid] = rec
    return [by_res[rid] for rid in order]


def _effective_credits(rec: dict[str, Any]) -> float:
    for key in ("actual_credits", "credits", "estimated_credits"):
        val = rec.get(key)
        if isinstance(val, (int, float)) and not isinstance(val, bool) and val >= 0:
            return float(val)
    return 0.0


def _collect_prompt_versions(campaign_dir: Path) -> dict[str, list[str]]:
    prompts_dir = campaign_dir / "prompts"
    if not prompts_dir.is_dir():
        return {}
    grouped: dict[str, list[str]] = {}
    for p in sorted(prompts_dir.glob("*.txt")):
        stem = p.stem
        m = re.match(r"^(.+?)_v(\d+)(?:_[A-Za-z0-9]+)?$", stem)
        base = m.group(1) if m else stem
        grouped.setdefault(base, []).append(str(p.relative_to(campaign_dir)))
    return grouped


def harvest_campaign(campaign_dir: Path) -> dict[str, Any]:
    camp = campaign_dir.resolve()
    if not camp.is_dir():
        return {
            "ok": False,
            "campaign_dir": str(camp),
            "errors": [f"campaign directory not found: {camp}"],
        }

    repo_root = _CHECK_BRIEF.find_repo_root(camp / "brief.md")
    errors: list[str] = []

    # 1. Brief metadata
    brief_path = camp / "brief.md"
    brief_info: dict[str, Any] = {"present": brief_path.is_file()}
    if brief_path.is_file():
        env = _CHECK_BRIEF.parse_budget_envelope(brief_path)
        brief_info.update(
            {
                "status": env.get("status"),
                "campaign_cap": env.get("campaign_cap"),
                "max_retries": env.get("max_retries"),
            }
        )

    # 2. Receipts (CLI + Web Unlimited + Uploads)
    raw_receipts, rec_errs = _read_jsonl(camp / "receipts.jsonl")
    errors.extend(rec_errs)
    collapsed = _collapse_receipts(raw_receipts)

    paid_spent = 0.0
    spent_by_round: Counter[str] = Counter()
    spent_by_model: Counter[str] = Counter()
    paid_runs = 0
    paid_failures: list[dict[str, Any]] = []
    web_runs = 0
    web_by_model: Counter[str] = Counter()
    web_failures: list[dict[str, Any]] = []
    uploads = 0
    models_seen: set[str] = set()
    attempts_per_asset: Counter[str] = Counter()

    for rec in collapsed:
        kind = str(rec.get("kind") or "")
        channel = str(rec.get("channel") or "").lower()
        status = str(rec.get("status") or "").lower()
        model = str(rec.get("model") or "").strip()
        round_name = str(rec.get("round") or "unknown")
        shot = str(rec.get("shot") or "unknown")

        if kind == "upload":
            uploads += 1
            continue

        if model and model != "upload":
            models_seen.add(model)

        if channel == "web_unlimited":
            web_runs += 1
            if model:
                web_by_model[model] += 1
            attempts_per_asset[f"{shot}.{kind} (web)"] += 1
            if status in ("failed", "rejected", "ip_detected"):
                web_failures.append(
                    {
                        "round": round_name,
                        "shot": shot,
                        "kind": kind,
                        "model": model,
                        "status": status,
                        "note": rec.get("note"),
                    }
                )
        else:
            eff = _effective_credits(rec)
            paid_runs += 1
            paid_spent += eff
            spent_by_round[round_name] += eff
            if model:
                spent_by_model[model] += eff
            attempts_per_asset[f"{shot}.{kind} (cli)"] += 1
            if status in ("failed", "rejected", "ip_detected", "error", "download_failed"):
                paid_failures.append(
                    {
                        "round": round_name,
                        "shot": shot,
                        "kind": kind,
                        "model": model,
                        "status": status,
                        "credits": _clean_num(eff),
                    }
                )

    # 3. Visual Critic review log
    reviews, rev_errs = _read_jsonl(camp / "qc" / "review-log.jsonl")
    errors.extend(rev_errs)
    verdict_counts: Counter[str] = Counter()
    defect_counts: Counter[str] = Counter()
    non_pass_reviews: list[dict[str, Any]] = []
    for rev in reviews:
        v = str(rev.get("verdict") or "UNKNOWN")
        d = str(rev.get("defect_class") or "UNKNOWN")
        verdict_counts[v] += 1
        if d != "NONE":
            defect_counts[d] += 1
        if v != "PASS":
            non_pass_reviews.append(
                {
                    "round": rev.get("round"),
                    "asset_id": rev.get("asset_id"),
                    "version": rev.get("version"),
                    "verdict": v,
                    "defect_class": d,
                    "summary": rev.get("summary") or "",
                }
            )

    # 4. Shotlist & prompt churn (v1 -> vN)
    prompt_groups = _collect_prompt_versions(camp)
    high_churn_prompts = [
        {"asset": base, "versions": files}
        for base, files in sorted(prompt_groups.items())
        if len(files) >= 2
    ]

    shotlist_churn: list[dict[str, Any]] = []
    shotlist_path = camp / "shotlist.json"
    if shotlist_path.is_file():
        try:
            sl_data = json.loads(shotlist_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"shotlist.json: failed to parse ({exc})")
            sl_data = {}
        if isinstance(sl_data, dict):
            for lb in sl_data.get("lookbook") or []:
                if isinstance(lb, dict) and int(lb.get("version") or 1) >= 2:
                    shotlist_churn.append(
                        {"asset": f"lookbook.{lb.get('id')}", "version": lb.get("version"), "status": lb.get("status")}
                    )
            for shot in sl_data.get("shots") or []:
                if not isinstance(shot, dict):
                    continue
                sid = shot.get("id")
                for sub_kind in ("still", "video"):
                    obj = shot.get(sub_kind)
                    if isinstance(obj, dict) and int(obj.get("version") or 1) >= 2:
                        shotlist_churn.append(
                            {
                                "asset": f"{sid}.{sub_kind}",
                                "version": obj.get("version"),
                                "status": obj.get("status"),
                                "model": obj.get("model"),
                            }
                        )

    # 5. Taste log & Supersedes flips
    taste_path = camp / "taste-log.md"
    taste_summary: dict[str, Any] = {
        "present": taste_path.is_file(),
        "brand_seed": "none",
        "entries": 0,
        "active_entries": 0,
        "superseded_entries": 0,
        "flips": [],
    }
    if taste_path.is_file():
        parsed = _MEMORY_COMPILE.parse_taste_log(taste_path)
        errors.extend(parsed["errors"])
        compiled = _MEMORY_COMPILE.compile_active_taste(parsed) if not parsed["errors"] else None
        flips: list[dict[str, Any]] = []
        for entry in parsed["entries"]:
            if entry["supersedes"]:
                flips.append(
                    {
                        "by": entry["id"],
                        "heading": entry["heading"],
                        "supersedes": [s["raw"] for s in entry["supersedes"]],
                    }
                )
        taste_summary.update(
            {
                "brand_seed": parsed["brand_seed"],
                "entries": parsed["entry_count"],
                "active_entries": compiled["active_entry_count"] if compiled else parsed["entry_count"],
                "superseded_entries": compiled["superseded_entry_count"] if compiled else 0,
                "flips": flips,
            }
        )

    # 6. Cross-check against studio/engine-memory.md
    known_engine_models: set[str] = set()
    engine_path = repo_root / "studio" / "engine-memory.md"
    if engine_path.is_file():
        eng_parsed = _CHECK_MEMORY.parse_engine_memory(engine_path)
        known_engine_models = {e["model"] for e in eng_parsed["entries"] if e.get("model")}
    untracked_models = sorted(m for m in models_seen if m not in known_engine_models)

    top_retried = [
        {"asset": k, "attempts": v}
        for k, v in attempts_per_asset.most_common(10)
        if v >= 2
    ]

    return {
        "ok": len(errors) == 0,
        "campaign": camp.name,
        "campaign_dir": str(camp),
        "brief": brief_info,
        "telemetry": {
            "paid_cli_runs": paid_runs,
            "paid_credits_spent": _clean_num(paid_spent),
            "spent_by_round": {k: _clean_num(v) for k, v in sorted(spent_by_round.items())},
            "spent_by_model": {k: _clean_num(v) for k, v in spent_by_model.most_common()},
            "paid_failures": paid_failures,
            "web_unlimited_runs": web_runs,
            "web_by_model": dict(web_by_model.most_common()),
            "web_failures": web_failures,
            "uploads": uploads,
            "top_retried_assets": top_retried,
        },
        "reviews": {
            "total": len(reviews),
            "by_verdict": dict(verdict_counts),
            "by_defect_class": dict(defect_counts.most_common()),
            "non_pass": non_pass_reviews,
        },
        "churn": {
            "shotlist_bumped_versions": shotlist_churn,
            "multi_version_prompts": high_churn_prompts,
        },
        "taste": taste_summary,
        "graduation_signals": {
            "models_not_in_engine_memory": untracked_models,
            "telemetry_blind_spot": (
                web_runs == 0 and paid_runs == 0 and uploads > 0
            ),
            "missing_review_log": len(reviews) == 0,
        },
        "errors": errors,
    }


def render_markdown(report: dict[str, Any]) -> str:
    tel = report["telemetry"]
    rev = report["reviews"]
    taste = report["taste"]
    churn = report["churn"]
    sig = report["graduation_signals"]

    lines: list[str] = [
        f"# Retro Harvest Packet: {report['campaign']}",
        "",
        "## 1. Execution Telemetry (`receipts.jsonl`)",
        f"- **Brief status / cap:** `{report['brief'].get('status')}` / `{report['brief'].get('campaign_cap')}` cr.",
        f"- **Paid CLI:** `{tel['paid_cli_runs']}` runs, `{tel['paid_credits_spent']}` cr. spent (`by_round`: {tel['spent_by_round'] or '{}'})",
        f"- **Web Unlimited (`0 cr.`):** `{tel['web_unlimited_runs']}` runs (`by_model`: {tel['web_by_model'] or '{}'})",
        f"- **Uploads:** `{tel['uploads']}`",
    ]
    if tel["spent_by_model"]:
        lines.append(f"- **Paid spend by model:** {tel['spent_by_model']}")
    if tel["paid_failures"]:
        lines.append(f"- **Paid failures / blocks ({len(tel['paid_failures'])}):**")
        for f in tel["paid_failures"][:10]:
            lines.append(
                f"  - `{f['round']}` `{f['shot']}.{f['kind']}` (`{f['model']}`): `{f['status']}` ({f['credits']} cr.)"
            )
    if tel["web_failures"]:
        lines.append(f"- **Web Unlimited failures / blocks ({len(tel['web_failures'])}):**")
        for f in tel["web_failures"][:10]:
            note_s = f" — {f['note']}" if f.get("note") else ""
            lines.append(
                f"  - `{f['round']}` `{f['shot']}.{f['kind']}` (`{f['model']}`): `{f['status']}`{note_s}"
            )
    if tel["top_retried_assets"]:
        lines.append("- **High-retry assets (`>= 2` runs):**")
        for item in tel["top_retried_assets"]:
            lines.append(f"  - `{item['asset']}`: {item['attempts']} attempts")

    lines.extend(["", "## 2. Visual Critic Trace (`qc/review-log.jsonl`)"])
    if rev["total"] == 0:
        lines.append("- _No `qc/review-log.jsonl` records found (log future reviews via `qa_media.py log-review`)._")
    else:
        lines.append(f"- **Total reviews:** `{rev['total']}` | **Verdicts:** {rev['by_verdict']}")
        if rev["by_defect_class"]:
            lines.append(f"- **Defect classes:** {rev['by_defect_class']}")
        for item in rev["non_pass"][:12]:
            lines.append(
                f"  - `{item['round']}` `{item['asset_id']}` v{item['version']}: "
                f"`{item['verdict']}` / `{item['defect_class']}` — {item['summary']}"
            )

    lines.extend(["", "## 3. Prompt & Version Churn (Inspect Diffs in Reflector)"])
    if not churn["multi_version_prompts"] and not churn["shotlist_bumped_versions"]:
        lines.append("- _No multi-version prompt churn detected._")
    else:
        for item in churn["multi_version_prompts"][:15]:
            lines.append(f"- `{item['asset']}`: {', '.join(f'`{p}`' for p in item['versions'])}")

    lines.extend(
        [
            "",
            "## 4. Taste Evolution & Reversals (`taste-log.md`)",
            f"- **Brand seed:** {taste['brand_seed']}",
            f"- **Entries:** `{taste['entries']}` total (`{taste['active_entries']}` active, `{taste['superseded_entries']}` fully superseded)",
        ]
    )
    if taste["flips"]:
        lines.append("- **Direction flips (`Supersedes`):**")
        for fl in taste["flips"]:
            lines.append(f"  - `{fl['by']}` supersedes {', '.join(f'`{s}`' for s in fl['supersedes'])} — {fl['heading']}")

    lines.extend(["", "## 5. Graduation & Hygiene Signals"])
    if sig["models_not_in_engine_memory"]:
        lines.append(
            f"- **Models not yet in `studio/engine-memory.md`:** {', '.join(f'`{m}`' for m in sig['models_not_in_engine_memory'])}"
        )
    if sig["telemetry_blind_spot"]:
        lines.append(
            "- **Telemetry gap:** uploads exist with 0 logged CLI or Web Unlimited runs — log Web runs with `hf_guard.py log-web`."
        )
    if sig["missing_review_log"]:
        lines.append(
            "- **QC trace gap:** `qc/review-log.jsonl` missing — log pre-Dailies reviews with `qa_media.py log-review`."
        )
    if (
        not sig["models_not_in_engine_memory"]
        and not sig["telemetry_blind_spot"]
        and not sig["missing_review_log"]
    ):
        lines.append("- _All trace channels clean and synced._")

    return "\n".join(lines) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Harvest structured execution, QC, churn, and taste traces from a campaign for studio-retro."
    )
    parser.add_argument("campaign", help="Path to campaign directory.")
    parser.add_argument("--out", default=None, help="Optional Markdown file path to write the harvest packet.")
    parser.add_argument("--json", action="store_true", dest="as_json", help="Emit JSON report.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    report = harvest_campaign(Path(args.campaign))

    if args.out and report.get("ok"):
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(render_markdown(report), encoding="utf-8")

    if args.as_json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    elif not report.get("ok"):
        for err in report.get("errors") or []:
            print(f"ERROR: {err}", file=sys.stderr)
    else:
        sys.stdout.write(render_markdown(report))

    return 0 if report.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
