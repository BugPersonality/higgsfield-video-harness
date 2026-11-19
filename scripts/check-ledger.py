#!/usr/bin/env python3
"""Static structural validator & topological wave planner for Production Ledger V1."""

from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import argparse
import fnmatch
import importlib.util
import json
import re
from collections import defaultdict, deque
from pathlib import Path
from typing import Any

VALID_STATUSES = frozenset({"draft", "ready", "blocked", "done"})
VALID_SHAPES = frozenset(
    {"reference", "still", "audio", "pilot", "video", "assembly", "qa"}
)
REQUIRED_PACKET_SECTIONS = (
    "Outcome",
    "Depends on",
    "Sources",
    "Provides",
    "Boundary",
    "Mutable owners",
    "Exclusive locks",
    "Final validation",
    "Reopen if",
)
ALLOW_NONE_SECTIONS = frozenset({"Depends on", "Exclusive locks", "Mutable owners"})

TASK_ID_RE = re.compile(r"^T\d+[A-Za-z0-9_-]*$")
DEP_TOKEN_RE = re.compile(
    r"^([A-Za-z][A-Za-z0-9_.-]*)(?:\s*\[(acceptance|effect:[^\]]+)\])?$"
)
FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")


def _load_check_intent():
    mod_path = Path(__file__).resolve().with_name("check-intent.py")
    spec = importlib.util.spec_from_file_location("check_intent", mod_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load sibling module: {mod_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_CHECK_INTENT = _load_check_intent()


def _strip_md(text: str) -> str:
    val = text.strip()
    # Handle markdown link [label](target)
    lm = re.match(r"^\[[^\]]*\]\(([^)]+)\)$", val)
    if lm:
        val = lm.group(1).strip()
    while len(val) >= 2 and (
        (val.startswith("**") and val.endswith("**"))
        or (val.startswith("__") and val.endswith("__"))
        or (val.startswith("`") and val.endswith("`"))
    ):
        val = val[2:-2].strip() if val.startswith(("**", "__")) else val[1:-1].strip()
    return val


def _norm_heading(name: str) -> str:
    return re.sub(r"\s+", " ", name.strip()).lower()


def _parse_markdown_sections(text: str) -> tuple[str | None, dict[str, tuple[str, str]]]:
    """Return (first H1 line, map of normalized H2 heading -> (raw heading, body))."""
    h1: str | None = None
    sections: dict[str, tuple[str, str]] = {}
    cur_key: str | None = None
    cur_raw = ""
    cur_lines: list[str] = []

    in_fence = False
    fence_char = ""
    fence_len = 0

    for line in text.splitlines():
        fm = FENCE_RE.match(line)
        if not in_fence and fm:
            in_fence = True
            fence_char = fm.group(1)[0]
            fence_len = len(fm.group(1))
            if cur_key is not None:
                cur_lines.append(line)
            continue
        if in_fence:
            stripped = line.lstrip()
            if (
                stripped.startswith(fence_char * fence_len)
                and stripped.strip(fence_char).strip() == ""
            ):
                in_fence = False
            if cur_key is not None:
                cur_lines.append(line)
            continue

        if h1 is None and line.startswith("# ") and not line.startswith("## "):
            h1 = line[2:].strip()
            continue

        h2 = re.match(r"^##\s+(.+?)\s*$", line)
        if h2:
            if cur_key is not None:
                sections[cur_key] = (cur_raw, "\n".join(cur_lines))
            cur_raw = h2.group(1).strip()
            cur_key = _norm_heading(cur_raw)
            cur_lines = []
            continue

        if cur_key is not None:
            cur_lines.append(line)

    if cur_key is not None:
        sections[cur_key] = (cur_raw, "\n".join(cur_lines))

    return h1, sections


def _parse_dep_tokens(
    raw_text: str, context: str, errors: list[str]
) -> list[tuple[str, str | None]]:
    """Parse Depends on tokens into normalized (target, qualifier) tuples."""
    tokens: list[tuple[str, str | None]] = []
    # Split by newlines first, then commas (ignoring descriptive text after em-dash)
    raw_items: list[str] = []
    for line in raw_text.splitlines():
        cleaned = re.sub(r"^\s*[-*]\s+", "", line).strip()
        if not cleaned:
            continue
        # Strip inline commentary after ' — ' or ' -- '
        cleaned = re.split(r"\s+(?:—|--)\s+", cleaned, maxsplit=1)[0].strip()
        for part in cleaned.split(","):
            p = _strip_md(part).strip().rstrip(".;")
            if p:
                raw_items.append(p)

    if not raw_items:
        return []
    if len(raw_items) == 1 and raw_items[0].lower() in {"none", "-", "n/a", "no dependencies"}:
        if raw_items[0].lower() == "n/a":
            errors.append(f"{context}: use 'none' instead of placeholder 'N/A' in Depends on")
        return []

    seen: set[tuple[str, str | None]] = set()
    for item in raw_items:
        if item.lower() == "none":
            continue
        # Normalize internal spaces before [
        norm_item = re.sub(r"\s+", " ", item).strip()
        m = DEP_TOKEN_RE.match(norm_item)
        if not m:
            errors.append(
                f"{context}: invalid dependency token '{item}' "
                "(expected 'T<ID>', 'T<ID> [acceptance]', 'T<ID> [effect:<action>]', "
                "or '<external-gate> [effect:<action>]')"
            )
            continue
        target = m.group(1)
        qual = m.group(2).strip() if m.group(2) else None
        if not TASK_ID_RE.match(target) and (qual is None or not qual.startswith("effect:")):
            errors.append(
                f"{context}: non-task dependency '{item}' must declare '[effect:<action>]'"
            )
            continue
        pair = (target, qual)
        if pair not in seen:
            seen.add(pair)
            tokens.append(pair)
    return tokens


def _format_dep_token(pair: tuple[str, str | None]) -> str:
    return f"{pair[0]} [{pair[1]}]" if pair[1] else pair[0]


def _extract_list_entries(section_body: str) -> list[str]:
    """Extract normalized paths or lock identifiers from a packet section."""
    entries: list[str] = []
    for line in section_body.splitlines():
        stripped = re.sub(r"^\s*[-*]\s+", "", line).strip()
        if not stripped:
            continue
        # Strip commentary after ' — ', ' -- ', or trailing '(...)'
        core = re.split(r"\s+(?:—|--)\s+", stripped, maxsplit=1)[0].strip()
        core_no_paren = re.sub(r"\s*\([^)]*\)\s*$", "", core).strip()
        if core_no_paren.rstrip(".").lower() in {"none", "-", "read-only", "none (read-only)"}:
            continue

        # If backticked tokens exist on this line, extract them; otherwise split by comma
        backticks = re.findall(r"`([^`\n]+)`", core)
        if backticks:
            for bt in backticks:
                val = bt.strip()
                if val and val.lower() != "none":
                    entries.append(val)
        else:
            for part in core_no_paren.split(","):
                val = _strip_md(part).strip().rstrip(".;")
                if val and val.lower() != "none":
                    entries.append(val)
    return entries


def _norm_owner_path(path_str: str) -> str:
    p = path_str.strip().replace("\\", "/")
    while p.startswith("./"):
        p = p[2:]
    p = re.sub(r"/+", "/", p)
    return p.rstrip("/")


def _paths_overlap(a: str, b: str) -> bool:
    na = _norm_owner_path(a)
    nb = _norm_owner_path(b)
    if not na or not nb:
        return False
    if na == nb:
        return True
    if nb.startswith(na + "/") or na.startswith(nb + "/"):
        return True
    if any(ch in na for ch in ("*", "?", "[")) and fnmatch.fnmatch(nb, na):
        return True
    if any(ch in nb for ch in ("*", "?", "[")) and fnmatch.fnmatch(na, nb):
        return True
    # Check glob directory prefix overlap: e.g. dir/* vs dir/sub/file
    if na.endswith("/*") and nb.startswith(na[:-1]):
        return True
    return bool(nb.endswith("/*") and na.startswith(nb[:-1]))


def _parse_tasks_md(
    tasks_path: Path, errors: list[str]
) -> dict[str, Any]:
    text = tasks_path.read_text(encoding="utf-8")
    lines = text.splitlines()

    title: str | None = None
    headers: dict[str, str] = {}
    tasks: list[dict[str, Any]] = []

    task_line_re = re.compile(
        r"^\s*-\s+\[([ xX])\]\s+(T\d+[A-Za-z0-9_-]*)\s*:\s*(.+?)\s*$"
    )
    header_re = re.compile(
        r"^\s*(?:[-*]\s+)?(?:\*\*|__)?(status|Intent|Shotlist|Completion)(?:\*\*|__)?\s*:\s*(.+?)\s*$",
        re.IGNORECASE,
    )
    sub_dep_re = re.compile(
        r"^\s+(?:[-*]\s+)?(?:\*\*|__)?Depends\s+on(?:\*\*|__)?\s*:\s*(.+?)\s*$",
        re.IGNORECASE,
    )
    sub_pkt_re = re.compile(
        r"^\s+(?:[-*]\s+)?(?:\*\*|__)?Packet(?:\*\*|__)?\s*:\s*(.+?)\s*$",
        re.IGNORECASE,
    )

    current_task: dict[str, Any] | None = None
    seen_task_section = False

    for lineno, line in enumerate(lines, start=1):
        if title is None:
            tm = re.match(r"^#\s+Tasks:\s*(.+?)\s*$", line)
            if tm:
                title = tm.group(1).strip()
                continue

        tm = task_line_re.match(line)
        if tm:
            seen_task_section = True
            checked = tm.group(1).lower() == "x"
            tid = tm.group(2)
            raw_rest = tm.group(3).strip()

            shape: str | None = None
            shape_m = re.match(r"^(.*?)\s*\[([^\]]+)\]\s*$", raw_rest)
            if shape_m:
                task_title = shape_m.group(1).strip()
                raw_shape = shape_m.group(2).strip().lower()
                if raw_shape not in VALID_SHAPES:
                    errors.append(
                        f"tasks.md:{lineno} ({tid}): invalid shape '[{raw_shape}]' "
                        f"(expected one of {sorted(VALID_SHAPES)})"
                    )
                else:
                    shape = raw_shape
            else:
                task_title = raw_rest

            if _CHECK_INTENT.is_placeholder(task_title):
                errors.append(f"tasks.md:{lineno} ({tid}): task title is empty or placeholder")

            current_task = {
                "id": tid,
                "title": task_title,
                "shape": shape,
                "done": checked,
                "line": lineno,
                "depends_raw": None,
                "depends": [],
                "packet_raw": None,
            }
            tasks.append(current_task)
            continue

        if current_task is not None:
            dm = sub_dep_re.match(line)
            if dm:
                current_task["depends_raw"] = dm.group(1).strip()
                continue
            pm = sub_pkt_re.match(line)
            if pm:
                current_task["packet_raw"] = _strip_md(pm.group(1))
                continue
            if line.startswith("#"):
                current_task = None

        if not seen_task_section:
            hm = header_re.match(line)
            if hm:
                key = hm.group(1).lower()
                headers[key] = _strip_md(hm.group(2))

    return {
        "title": title,
        "headers": headers,
        "tasks": tasks,
    }


def _validate_shotlist(
    shotlist_path: Path,
    campaign_dir: Path,
    repo_root: Path,
    budget_envelope: dict[str, Any] | None,
    errors: list[str],
    warnings: list[str],
) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "path": str(shotlist_path),
        "present": True,
        "shot_count": 0,
        "draft_estimated": 0,
        "final_estimated": 0,
        "draft_cap": budget_envelope.get("draft_cap") if budget_envelope else None,
        "final_cap": budget_envelope.get("final_cap") if budget_envelope else None,
    }

    try:
        data = json.loads(shotlist_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"shotlist.json: failed to parse JSON: {exc}")
        return summary

    if not isinstance(data, dict):
        errors.append("shotlist.json: root must be a JSON object")
        return summary

    if data.get("schema_version") != 1:
        errors.append(
            f"shotlist.json: schema_version must be 1, got {data.get('schema_version')!r}"
        )

    # Optional top-level continuity_lock validation
    if "continuity_lock" in data and data["continuity_lock"] is not None:
        cl = data["continuity_lock"]
        if not isinstance(cl, dict):
            errors.append("shotlist.json: 'continuity_lock' must be a JSON object")
        else:
            for field in ("product", "lighting_and_palette", "space_cast_axis"):
                val = cl.get(field)
                if (
                    not isinstance(val, str)
                    or not val.strip()
                    or _CHECK_INTENT.is_placeholder(val)
                ):
                    errors.append(
                        f"shotlist.json (continuity_lock): missing, empty, or placeholder string '{field}'"
                    )

    shots = data.get("shots")
    if not isinstance(shots, list) or len(shots) == 0:
        errors.append("shotlist.json: 'shots' must be a non-empty list")
        return summary

    summary["shot_count"] = len(shots)
    shots_by_id: dict[str, dict[str, Any]] = {}

    def _check_prompt_file(val: Any, ctx: str) -> None:
        if not isinstance(val, str) or not val.strip():
            return
        p = Path(val)
        if p.is_absolute():
            if not p.is_file():
                errors.append(f"shotlist.json ({ctx}): prompt_file not found: {val}")
        else:
            if not (campaign_dir / p).is_file() and not (repo_root / p).is_file():
                errors.append(f"shotlist.json ({ctx}): prompt_file not found: {val}")

    def _num(val: Any, ctx: str) -> float:
        if val is None:
            return 0.0
        if isinstance(val, bool) or not isinstance(val, (int, float)):
            errors.append(f"shotlist.json ({ctx}): expected numeric credit value, got {val!r}")
            return 0.0
        if val < 0:
            errors.append(f"shotlist.json ({ctx}): credit value cannot be negative ({val})")
            return 0.0
        return float(val)

    still_sum = 0.0
    video_draft_sum = 0.0
    video_final_sum = 0.0
    audio_sum = 0.0

    # Collect declared top-level reference IDs
    declared_ref_ids: set[str] = set()
    raw_refs = data.get("references")
    if isinstance(raw_refs, list):
        for ridx, ref_obj in enumerate(raw_refs):
            if not isinstance(ref_obj, dict):
                errors.append(f"shotlist.json: references[{ridx}] must be an object")
                continue
            rid = ref_obj.get("id")
            if not isinstance(rid, str) or not rid.strip():
                errors.append(f"shotlist.json: references[{ridx}] missing non-empty string 'id'")
                continue
            if rid in declared_ref_ids:
                errors.append(f"shotlist.json: duplicate reference id '{rid}'")
            declared_ref_ids.add(rid.strip())

    # Check autonomy_mode parity with intent.md when present
    sl_mode = data.get("autonomy_mode")
    if (
        sl_mode is not None
        and budget_envelope
        and budget_envelope.get("autonomy_mode")
        and str(sl_mode).strip() != str(budget_envelope["autonomy_mode"]).strip()
    ):
        errors.append(
            f"shotlist.json: autonomy_mode '{sl_mode}' does not match intent.md "
            f"autonomy_mode '{budget_envelope['autonomy_mode']}'"
        )

    def _check_ref_id_list(ref_list: Any, ctx: str) -> None:
        if ref_list is None:
            return
        if not isinstance(ref_list, list):
            errors.append(f"shotlist.json ({ctx}): expected list of reference IDs")
            return
        for item in ref_list:
            if not isinstance(item, str) or not item.strip():
                errors.append(f"shotlist.json ({ctx}): invalid reference id {item!r}")
            elif item.strip() not in declared_ref_ids:
                errors.append(
                    f"shotlist.json ({ctx}): references undeclared reference id '{item.strip()}'"
                )

    total_duration_s = 0.0
    all_have_duration = True

    for idx, shot in enumerate(shots):
        if not isinstance(shot, dict):
            errors.append(f"shotlist.json: shots[{idx}] must be an object")
            continue
        sid = shot.get("id")
        if not isinstance(sid, str) or not sid.strip():
            errors.append(f"shotlist.json: shots[{idx}] missing non-empty string 'id'")
            continue
        if sid in shots_by_id:
            errors.append(f"shotlist.json: duplicate shot id '{sid}'")
        shots_by_id[sid] = shot

        if "duration_s" in shot and shot["duration_s"] is not None:
            dur_val = shot["duration_s"]
            if isinstance(dur_val, bool) or not isinstance(dur_val, (int, float)) or dur_val <= 0:
                errors.append(
                    f"shotlist.json (shot {sid}.duration_s): must be a positive number, got {dur_val!r}"
                )
                all_have_duration = False
            else:
                total_duration_s += float(dur_val)
        else:
            all_have_duration = False

        _check_prompt_file(shot.get("prompt_file"), f"shot {sid}")
        _check_ref_id_list(shot.get("references"), f"shot {sid}.references")

        # Optional per-shot test_take_check validation
        ttc_locations: list[tuple[str, Any]] = []
        if "test_take_check" in shot and shot["test_take_check"] is not None:
            ttc_locations.append((f"shot {sid}.test_take_check", shot["test_take_check"]))
        if (
            isinstance(shot.get("video"), dict)
            and "test_take_check" in shot["video"]
            and shot["video"]["test_take_check"] is not None
        ):
            ttc_locations.append(
                (f"shot {sid}.video.test_take_check", shot["video"]["test_take_check"])
            )
        for ttc_ctx, ttc in ttc_locations:
            if not isinstance(ttc, dict):
                errors.append(f"shotlist.json ({ttc_ctx}): must be a JSON object")
            else:
                for field in ("risk", "pass_check"):
                    val = ttc.get(field)
                    if (
                        not isinstance(val, str)
                        or not val.strip()
                        or _CHECK_INTENT.is_placeholder(val)
                    ):
                        errors.append(
                            f"shotlist.json ({ttc_ctx}): missing, empty, or placeholder string '{field}'"
                        )

        still = shot.get("still")
        if isinstance(still, dict):
            still_sum += _num(still.get("estimated_credits"), f"shot {sid}.still.estimated_credits")
            _check_prompt_file(still.get("prompt_file"), f"shot {sid}.still")
            _check_ref_id_list(still.get("references"), f"shot {sid}.still.references")

        video = shot.get("video")
        if isinstance(video, dict):
            video_draft_sum += _num(
                video.get("estimated_draft_credits"), f"shot {sid}.video.estimated_draft_credits"
            )
            video_final_sum += _num(
                video.get("estimated_final_credits"), f"shot {sid}.video.estimated_final_credits"
            )
            _check_prompt_file(video.get("prompt_file"), f"shot {sid}.video")
            _check_ref_id_list(video.get("references"), f"shot {sid}.video.references")
            _check_ref_id_list(
                video.get("image_references"), f"shot {sid}.video.image_references"
            )

        shot_audio = shot.get("audio")
        if isinstance(shot_audio, dict):
            if shot_audio.get("enabled", True) is True:
                audio_sum += _num(
                    shot_audio.get("estimated_credits"), f"shot {sid}.audio.estimated_credits"
                )
            _check_prompt_file(shot_audio.get("prompt_file"), f"shot {sid}.audio")

    # Verify sum(shots[].duration_s) == target_duration_s within 0.5s when declared
    target_dur = data.get("target_duration_s")
    if target_dur is not None:
        if isinstance(target_dur, bool) or not isinstance(target_dur, (int, float)) or target_dur <= 0:
            errors.append(
                f"shotlist.json: target_duration_s must be a positive number, got {target_dur!r}"
            )
        elif all_have_duration and abs(total_duration_s - float(target_dur)) > 0.5:
            errors.append(
                f"shotlist.json: sum(shots[].duration_s)={total_duration_s:.2f}s differs from "
                f"target_duration_s={float(target_dur):.2f}s by more than 0.5s"
            )

    # Validate start_image_from / end_image_from cross-references
    # Allowed forms: "<shot_id>.still", "<shot_id>.last_frame", or a declared ref_* ID
    for sid, shot in shots_by_id.items():
        refs_to_check: list[tuple[str, Any]] = []
        if "start_image_from" in shot:
            refs_to_check.append(("start_image_from", shot["start_image_from"]))
        if "end_image_from" in shot:
            refs_to_check.append(("end_image_from", shot["end_image_from"]))
        video = shot.get("video")
        if isinstance(video, dict):
            if "start_image_from" in video:
                refs_to_check.append(("video.start_image_from", video["start_image_from"]))
            if "end_image_from" in video:
                refs_to_check.append(("video.end_image_from", video["end_image_from"]))

        for field_label, ref_val in refs_to_check:
            if ref_val is None:
                continue
            if not isinstance(ref_val, str) or not ref_val.strip():
                errors.append(
                    f"shotlist.json (shot {sid}.{field_label}): invalid reference {ref_val!r}"
                )
                continue
            ref_str = ref_val.strip()
            if ref_str in declared_ref_ids:
                continue
            m_still = re.match(r"^([^.]+)\.still$", ref_str)
            m_last = re.match(r"^([^.]+)\.last_frame$", ref_str)
            if m_still:
                target_id = m_still.group(1)
                target_shot = shots_by_id.get(target_id)
                if target_shot is None:
                    errors.append(
                        f"shotlist.json (shot {sid}.{field_label}): references unknown shot '{target_id}'"
                    )
                elif not isinstance(target_shot.get("still"), dict) or not target_shot["still"]:
                    errors.append(
                        f"shotlist.json (shot {sid}.{field_label}): target shot '{target_id}' has no 'still' defined"
                    )
            elif m_last:
                target_id = m_last.group(1)
                target_shot = shots_by_id.get(target_id)
                if target_shot is None:
                    errors.append(
                        f"shotlist.json (shot {sid}.{field_label}): references unknown shot '{target_id}'"
                    )
                elif not isinstance(target_shot.get("video"), dict) or not target_shot["video"]:
                    errors.append(
                        f"shotlist.json (shot {sid}.{field_label}): target shot '{target_id}' has no 'video' defined"
                    )
            else:
                errors.append(
                    f"shotlist.json (shot {sid}.{field_label}): expected '<shot_id>.still', "
                    f"'<shot_id>.last_frame', or declared reference ID, got '{ref_val}'"
                )

    # Top-level audio credits & prompt files (sum track credits ONLY when enabled is true)
    top_audio = data.get("audio")
    if isinstance(top_audio, dict):
        if "estimated_credits" in top_audio and top_audio.get("enabled", True) is True:
            audio_sum += _num(top_audio.get("estimated_credits"), "audio.estimated_credits")
        _check_prompt_file(top_audio.get("prompt_file"), "audio")
        for track_name, track_obj in top_audio.items():
            if isinstance(track_obj, dict):
                if track_obj.get("enabled", True) is True:
                    audio_sum += _num(
                        track_obj.get("estimated_credits"),
                        f"audio.{track_name}.estimated_credits",
                    )
                _check_prompt_file(track_obj.get("prompt_file"), f"audio.{track_name}")
    elif isinstance(top_audio, list):
        for idx, track_obj in enumerate(top_audio):
            if isinstance(track_obj, dict):
                if track_obj.get("enabled", True) is True:
                    audio_sum += _num(
                        track_obj.get("estimated_credits"), f"audio[{idx}].estimated_credits"
                    )
                _check_prompt_file(track_obj.get("prompt_file"), f"audio[{idx}]")

    draft_est = still_sum + video_draft_sum + audio_sum
    final_est = video_final_sum
    # Preserve clean int representation when whole numbers
    summary["draft_estimated"] = int(draft_est) if draft_est.is_integer() else round(draft_est, 2)
    summary["final_estimated"] = int(final_est) if final_est.is_integer() else round(final_est, 2)
    summary["breakdown"] = {
        "still_credits": int(still_sum) if still_sum.is_integer() else round(still_sum, 2),
        "video_draft_credits": int(video_draft_sum) if video_draft_sum.is_integer() else round(video_draft_sum, 2),
        "audio_credits": int(audio_sum) if audio_sum.is_integer() else round(audio_sum, 2),
        "video_final_credits": int(video_final_sum) if video_final_sum.is_integer() else round(video_final_sum, 2),
    }

    if budget_envelope:
        dcap = budget_envelope.get("draft_cap")
        fcap = budget_envelope.get("final_cap")
        if dcap is not None and draft_est > dcap:
            errors.append(
                f"shotlist.json: draft estimated credits ({summary['draft_estimated']}) "
                f"exceed intent Draft cap ({dcap})"
            )
        if fcap is not None and final_est > fcap:
            errors.append(
                f"shotlist.json: final estimated credits ({summary['final_estimated']}) "
                f"exceed intent Final cap ({fcap})"
            )
    else:
        warnings.append("intent.md budget envelope unavailable; skipped shotlist cap comparison")

    return summary


def resolve_tasks_path(target: str | Path) -> Path:
    p = Path(target)
    if p.is_dir():
        return p / "tasks.md"
    return p


def validate_ledger(target: str | Path) -> dict[str, Any]:
    tasks_path = resolve_tasks_path(target)
    errors: list[str] = []
    warnings: list[str] = []

    if not tasks_path.is_file():
        return {
            "ok": False,
            "file_found": False,
            "path": str(tasks_path),
            "status": None,
            "waves": [],
            "budget": None,
            "warnings": [],
            "errors": [f"tasks file not found: {tasks_path}"],
        }

    campaign_dir = tasks_path.resolve().parent
    repo_root = _CHECK_INTENT.find_repo_root(tasks_path)

    parsed = _parse_tasks_md(tasks_path, errors)
    title = parsed["title"]
    headers = parsed["headers"]
    tasks = parsed["tasks"]

    if title is None or _CHECK_INTENT.is_placeholder(title):
        errors.append("tasks.md: missing or placeholder H1 title matching '^# Tasks: <title>'")

    status = headers.get("status", "").lower() if "status" in headers else None
    if status is None:
        errors.append("tasks.md: missing 'status:' header")
    elif status not in VALID_STATUSES:
        errors.append(
            f"tasks.md: invalid status '{status}' (expected one of {sorted(VALID_STATUSES)})"
        )

    for req_hdr in ("intent", "shotlist", "completion"):
        val = headers.get(req_hdr)
        if not val or _CHECK_INTENT.is_placeholder(val):
            errors.append(f"tasks.md: missing or placeholder '{req_hdr.capitalize()}:' header")

    # Resolve upstream intent.md
    intent_rel = headers.get("intent", "intent.md")
    intent_path = campaign_dir / intent_rel
    if not intent_path.is_file():
        alt_intent = repo_root / intent_rel
        if alt_intent.is_file():
            intent_path = alt_intent

    budget_envelope: dict[str, Any] | None = None
    if intent_path.is_file():
        budget_envelope = _CHECK_INTENT.parse_budget_envelope(intent_path)
        if status in {"ready", "done"} and budget_envelope.get("status") != "ready":
            errors.append(
                f"tasks.md status is '{status}' but upstream intent '{intent_path.name}' "
                f"has status '{budget_envelope.get('status')}' (must be 'ready')"
            )
    elif status in {"ready", "done"}:
        errors.append(
            f"tasks.md status is '{status}' but upstream intent file not found: {intent_rel}"
        )

    if not tasks:
        errors.append("tasks.md: no task lines ('- [ ] T<ID>: <title> [<shape>]') found")

    tasks_by_id: dict[str, dict[str, Any]] = {}
    packet_info: dict[str, dict[str, Any]] = {}

    for task in tasks:
        tid = task["id"]
        if tid in tasks_by_id:
            errors.append(f"tasks.md: duplicate task ID '{tid}'")
        tasks_by_id[tid] = task

        if task["depends_raw"] is None:
            errors.append(f"tasks.md ({tid}): missing 'Depends on:' line")
            task["depends"] = []
        else:
            task["depends"] = _parse_dep_tokens(
                task["depends_raw"], f"tasks.md ({tid})", errors
            )

        if not task["packet_raw"]:
            errors.append(f"tasks.md ({tid}): missing 'Packet:' line")
            continue

        pkt_rel = task["packet_raw"]
        pkt_path = campaign_dir / pkt_rel
        pkt_norm = pkt_rel.replace("\\", "/")
        if not re.match(rf"^(?:\./)?tasks/{re.escape(tid)}-[^/]+\.md$", pkt_norm):
            errors.append(
                f"tasks.md ({tid}): Packet path '{pkt_rel}' must match 'tasks/{tid}-*.md'"
            )
        if not pkt_path.is_file():
            errors.append(f"tasks.md ({tid}): packet file does not exist: {pkt_rel}")
            continue

        # Validate packet file
        pkt_text = pkt_path.read_text(encoding="utf-8")
        pkt_h1, pkt_sections = _parse_markdown_sections(pkt_text)

        if pkt_h1 is None:
            errors.append(f"{pkt_rel}: missing H1 heading '# {tid} — <title>'")
        else:
            h1_m = re.match(r"^(T\d+[A-Za-z0-9_-]*)\s*(?:—|--|–|-|:)\s*(.+?)\s*$", pkt_h1)
            if not h1_m:
                errors.append(
                    f"{pkt_rel}: H1 '# {pkt_h1}' does not match '# {tid} — <title>'"
                )
            elif h1_m.group(1) != tid:
                errors.append(
                    f"{pkt_rel}: H1 task ID '{h1_m.group(1)}' does not match tasks.md ID '{tid}'"
                )

        for sec in REQUIRED_PACKET_SECTIONS:
            sec_key = _norm_heading(sec)
            if sec_key not in pkt_sections:
                errors.append(f"{pkt_rel}: missing required section '## {sec}'")
                continue
            sec_body = pkt_sections[sec_key][1].strip()
            if not sec_body:
                errors.append(f"{pkt_rel}: section '## {sec}' is empty")
            elif (
                sec not in ALLOW_NONE_SECTIONS and _CHECK_INTENT.is_placeholder(sec_body)
            ) or (
                sec in ALLOW_NONE_SECTIONS
                and re.search(r"\b(?:TBD|TODO|TBA)\b", sec_body, re.IGNORECASE)
            ):
                errors.append(
                    f"{pkt_rel}: section '## {sec}' contains unresolved placeholder text"
                )

        # Compare Depends on tokens between tasks.md and packet
        dep_sec = pkt_sections.get(_norm_heading("Depends on"))
        if dep_sec is not None:
            pkt_deps = _parse_dep_tokens(dep_sec[1], f"{pkt_rel} (Depends on)", errors)
            if set(pkt_deps) != set(task["depends"]):
                t_str = ", ".join(_format_dep_token(d) for d in sorted(task["depends"])) or "none"
                p_str = ", ".join(_format_dep_token(d) for d in sorted(pkt_deps)) or "none"
                errors.append(
                    f"{pkt_rel}: 'Depends on' mismatch with tasks.md "
                    f"(tasks.md=[{t_str}] vs packet=[{p_str}])"
                )

        owners_sec = pkt_sections.get(_norm_heading("Mutable owners"))
        locks_sec = pkt_sections.get(_norm_heading("Exclusive locks"))
        packet_info[tid] = {
            "packet": pkt_rel,
            "mutable_owners": _extract_list_entries(owners_sec[1]) if owners_sec else [],
            "exclusive_locks": _extract_list_entries(locks_sec[1]) if locks_sec else [],
        }

    # Build task dependency DAG
    task_deps: dict[str, set[str]] = {tid: set() for tid in tasks_by_id}
    dependents: dict[str, set[str]] = defaultdict(set)

    for tid, task in tasks_by_id.items():
        for dep_target, _qual in task["depends"]:
            if TASK_ID_RE.match(dep_target):
                if dep_target == tid:
                    errors.append(f"DAG error: task '{tid}' cannot depend on itself")
                elif dep_target not in tasks_by_id:
                    errors.append(
                        f"DAG error: task '{tid}' depends on unknown task '{dep_target}'"
                    )
                else:
                    task_deps[tid].add(dep_target)
                    dependents[dep_target].add(tid)

    # Topological wave computation (Kahn's algorithm level-by-level)
    in_degree = {tid: len(deps) for tid, deps in task_deps.items()}
    ready_queue = sorted(tid for tid, deg in in_degree.items() if deg == 0)
    waves: list[list[str]] = []
    visited_count = 0

    while ready_queue:
        wave = list(ready_queue)
        waves.append(wave)
        visited_count += len(wave)
        next_ready: list[str] = []
        for tid in wave:
            for dep_of in dependents.get(tid, ()):
                in_degree[dep_of] -= 1
                if in_degree[dep_of] == 0:
                    next_ready.append(dep_of)
        ready_queue = sorted(next_ready)

    if visited_count < len(tasks_by_id):
        cycle_nodes = sorted(tid for tid, deg in in_degree.items() if deg > 0)
        errors.append(
            f"DAG error: dependency cycle detected involving tasks: {', '.join(cycle_nodes)}"
        )

    # Transitive ancestor check for domain invariant:
    # Every [video] or [pilot] task must depend (directly or transitively) on at least one [still] or [reference] task.
    def _ancestors(start_id: str) -> set[str]:
        seen: set[str] = set()
        q: deque[str] = deque(task_deps.get(start_id, ()))
        while q:
            cur = q.popleft()
            if cur in seen:
                continue
            seen.add(cur)
            q.extend(task_deps.get(cur, ()))
        return seen

    for tid, task in tasks_by_id.items():
        if task["shape"] in {"video", "pilot"}:
            anc = _ancestors(tid)
            has_anchor = any(
                tasks_by_id[a]["shape"] in {"still", "reference"} for a in anc
            )
            if not has_anchor:
                errors.append(
                    f"domain invariant violation ({tid} [{task['shape']}]): "
                    "must depend (directly or transitively) on at least one [still] or [reference] task"
                )

    # Disjoint Mutable owners / Exclusive locks check within each wave
    for wave_idx, wave in enumerate(waves, start=1):
        for i in range(len(wave)):
            for j in range(i + 1, len(wave)):
                ta, tb = wave[i], wave[j]
                info_a = packet_info.get(ta, {})
                info_b = packet_info.get(tb, {})
                owners_a = info_a.get("mutable_owners", [])
                owners_b = info_b.get("mutable_owners", [])
                locks_a = set(info_a.get("exclusive_locks", []))
                locks_b = set(info_b.get("exclusive_locks", []))
                shared_locks = sorted(locks_a & locks_b)

                overlapping_pairs: list[tuple[str, str]] = []
                for oa in owners_a:
                    for ob in owners_b:
                        if _paths_overlap(oa, ob):
                            overlapping_pairs.append((oa, ob))

                if overlapping_pairs:
                    pair_desc = ", ".join(
                        f"'{oa}' <-> '{ob}'" for oa, ob in overlapping_pairs
                    )
                    errors.append(
                        f"Wave {wave_idx} mutable owner conflict: {ta} and {tb} overlap on "
                        f"{pair_desc} (same-wave Mutable owners must be strictly disjoint)"
                    )
                if shared_locks:
                    warnings.append(
                        f"Wave {wave_idx} serialization note: {ta} and {tb} share exclusive lock "
                        f"({', '.join(shared_locks)})"
                    )

    # Validate shotlist.json if present
    shotlist_rel = headers.get("shotlist", "shotlist.json")
    shotlist_path = campaign_dir / shotlist_rel
    if not shotlist_path.is_file():
        fallback = campaign_dir / "shotlist.json"
        if fallback.is_file():
            shotlist_path = fallback

    budget_summary: dict[str, Any] | None = None
    if shotlist_path.is_file():
        budget_summary = _validate_shotlist(
            shotlist_path, campaign_dir, repo_root, budget_envelope, errors, warnings
        )

    return {
        "ok": len(errors) == 0,
        "file_found": True,
        "path": str(tasks_path),
        "title": title,
        "status": status,
        "waves": [{"wave": idx, "tasks": w} for idx, w in enumerate(waves, start=1)],
        "task_count": len(tasks_by_id),
        "budget": budget_summary,
        "warnings": warnings,
        "errors": errors,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate Production Ledger V1 (tasks.md, tasks/*.md, shotlist.json) and plan waves."
    )
    parser.add_argument(
        "target",
        help="Path to campaign directory or tasks.md file.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="Emit validation report and wave plan as JSON.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    report = validate_ledger(args.target)

    if args.as_json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        if not report["file_found"]:
            print(f"ERROR: {report['errors'][0]}", file=sys.stderr)
            return 2

        state = "OK" if report["ok"] else "FAIL"
        print(
            f"[{state}] {report['path']} "
            f"(status={report['status']}, tasks={report['task_count']}, waves={len(report['waves'])})"
        )
        for w in report["waves"]:
            print(f"  Wave {w['wave']}: {', '.join(w['tasks'])}")
        b = report.get("budget")
        if b:
            print(
                f"  Budget: draft={b['draft_estimated']}/{b['draft_cap']} credits, "
                f"final={b['final_estimated']}/{b['final_cap']} credits "
                f"({b['shot_count']} shots)"
            )
        for warn in report["warnings"]:
            print(f"  WARN: {warn}")
        for err in report["errors"]:
            print(f"  ERROR: {err}")

    if not report["file_found"]:
        return 2
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
