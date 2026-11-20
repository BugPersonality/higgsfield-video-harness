#!/usr/bin/env python3
"""Static structural validator for Feedback-Loop Studio campaigns (brief.md + taste-log.md + shotlist.json)."""

from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import argparse
import importlib.util
import json
import math
import re
from pathlib import Path
from typing import Any

VALID_ASSET_STATUSES = ("DRAFT", "IN_REVIEW", "ITERATING", "LOCKED")
VALID_ASSET_STATUS_SET = frozenset(VALID_ASSET_STATUSES)
VALID_LOOKBOOK_KINDS = frozenset({"character", "object", "location"})
VALID_CS4_MODES = frozenset({"t2v", "omni_reference", "video_edit", "video_extension"})
STILL_HARD_REF_CAPS = {
    "flux_kontext": 4,
    "seedream_5_5": 10,
    "kling_image_4_0": 10,
    "kling_omni_image": 10,
    "3d_jutsu_angles": 10,
    "nano_banana_pro": 14,
    "nano_banana_2_1": 14,
}
VIDEO_HARD_IMG_CAPS = {
    "kling4_0": 10,
    "kling_4_0_flash": 10,
    "flux_3_video": 10,
    "seedance_2_5": 30,
    "cinematic_studio_video_4_0": 30,
}
FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")

STEERING_BULLET_RE = re.compile(
    r"^(\s*)[-*]\s+(?:\*\*|__)?"
    r"(Approved\s*/\s*LOCKED|More\s+of|Change\s*/\s*Steer|Never)"
    r"(?:\*\*|__)?\s*:\s*(?:\*\*|__)?\s*(.*)$",
    re.IGNORECASE,
)


def _load_check_brief():
    mod_path = Path(__file__).resolve().with_name("check-brief.py")
    spec = importlib.util.spec_from_file_location("check_brief", mod_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load sibling module: {mod_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_CHECK_BRIEF = _load_check_brief()


def _clean_num(val: float) -> int | float:
    return int(val) if float(val).is_integer() else round(val, 2)


def _is_valid_version(val: Any) -> bool:
    return isinstance(val, int) and not isinstance(val, bool) and val >= 1


def _validate_taste_log(taste_path: Path, errors: list[str]) -> int:
    """Validate taste-log.md H1 and all ### TL-<NN> entries. Returns entry count."""
    text = taste_path.read_text(encoding="utf-8")
    lines = text.splitlines()

    h1_title: str | None = None
    entries: list[tuple[str, list[str]]] = []
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

        if re.match(r"^##\s+", line):
            if current_heading is not None:
                entries.append((current_heading, current_lines))
                current_heading = None
                current_lines = []
            continue

        if re.match(r"^###\s+", line):
            if current_heading is not None:
                entries.append((current_heading, current_lines))
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
        entries.append((current_heading, current_lines))

    if h1_title is None or (h1_title != "" and _CHECK_BRIEF.is_placeholder(h1_title)):
        errors.append(
            "taste-log.md: missing or placeholder H1 heading matching '^# Taste Log: <title>'"
        )

    seen_ids: set[str] = set()
    valid_entries = 0

    for raw_heading, body_lines in entries:
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
        valid_entries += 1

        has_steering = False
        idx = 0
        total_lines = len(body_lines)
        while idx < total_lines:
            line = body_lines[idx]
            sm = STEERING_BULLET_RE.match(line)
            if not sm:
                idx += 1
                continue
            base_indent = len(sm.group(1))
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
                if nxt_indent > base_indent and not STEERING_BULLET_RE.match(nxt):
                    val_parts.append(nxt.strip())
                    idx += 1
                else:
                    break
            combined = " ".join(val_parts).strip()
            cleaned_none = re.sub(r"^[-*]\s+", "", combined).strip().rstrip(".").lower()
            if (
                combined
                and cleaned_none not in {"none", "-", "n/a"}
                and not _CHECK_BRIEF.is_placeholder(combined)
            ):
                has_steering = True

        if not has_steering:
            errors.append(
                f"taste-log.md ({tl_id}): must include at least one non-placeholder steering bullet "
                "('Approved / LOCKED', 'More of', 'Change / Steer', or 'Never')"
            )

    return valid_entries


def _validate_shotlist(
    shotlist_path: Path,
    campaign_dir: Path,
    repo_root: Path,
    campaign_cap: int | None,
    errors: list[str],
    warnings: list[str],
) -> dict[str, Any]:
    status_counts = {st: 0 for st in VALID_ASSET_STATUSES}
    result: dict[str, Any] = {
        "shot_count": 0,
        "lookbook_count": 0,
        "status_counts": status_counts,
        "budget": {
            "r2_lookbook": 0,
            "r3_stills_audio": 0,
            "r4_draft_video": 0,
            "r5_final_video": 0,
            "planned_total": 0,
            "campaign_cap": campaign_cap,
            "remaining_planned": campaign_cap,
        },
    }

    try:
        data = json.loads(shotlist_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"shotlist.json: failed to parse JSON: {exc}")
        return result

    if not isinstance(data, dict):
        errors.append("shotlist.json: root must be a JSON object")
        return result

    if data.get("schema_version") != 1:
        errors.append(
            f"shotlist.json: schema_version must be 1, got {data.get('schema_version')!r}"
        )

    def _check_prompt_file(val: Any, ctx: str) -> None:
        if val is None:
            return
        if not isinstance(val, str):
            errors.append(f"shotlist.json ({ctx}): prompt_file must be a string, got {val!r}")
            return
        if not val.strip():
            return
        p = Path(val.strip())
        if p.is_absolute():
            if not p.is_file():
                errors.append(f"shotlist.json ({ctx}): prompt_file not found: {val}")
        elif not (campaign_dir / p).is_file() and not (repo_root / p).is_file():
            errors.append(f"shotlist.json ({ctx}): prompt_file not found: {val}")

    def _num(val: Any, ctx: str) -> float:
        if val is None:
            return 0.0
        if isinstance(val, bool) or not isinstance(val, (int, float)):
            errors.append(f"shotlist.json ({ctx}): expected numeric credit value, got {val!r}")
            return 0.0
        f = float(val)
        if not math.isfinite(f) or f < 0:
            errors.append(f"shotlist.json ({ctx}): credit value must be finite and >= 0, got {val!r}")
            return 0.0
        return f

    def _req_num(obj: dict[str, Any], key: str, ctx: str) -> float:
        if key not in obj or obj[key] is None:
            errors.append(
                f"shotlist.json ({ctx}): missing or null required numeric credit field '{key}'"
            )
            return 0.0
        return _num(obj[key], f"{ctx}.{key}")

    def _check_status_and_version(
        obj: dict[str, Any],
        ctx: str,
        *,
        require_status: bool,
        count_status: bool = True,
    ) -> str | None:
        raw_status = obj.get("status")
        valid_st: str | None = None
        if raw_status is None:
            if require_status:
                errors.append(
                    f"shotlist.json ({ctx}): missing required 'status' "
                    f"(expected one of {list(VALID_ASSET_STATUSES)})"
                )
        elif not isinstance(raw_status, str) or raw_status not in VALID_ASSET_STATUS_SET:
            errors.append(
                f"shotlist.json ({ctx}): invalid status {raw_status!r} "
                f"(expected one of {list(VALID_ASSET_STATUSES)})"
            )
        else:
            valid_st = raw_status
            if count_status:
                status_counts[valid_st] += 1

        if "version" in obj and obj["version"] is not None and not _is_valid_version(obj["version"]):
            errors.append(
                f"shotlist.json ({ctx}): 'version' must be a positive integer (>= 1), "
                f"got {obj['version']!r}"
            )
        return valid_st

    # Optional continuity_lock
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
                    or _CHECK_BRIEF.is_placeholder(val)
                ):
                    errors.append(
                        f"shotlist.json (continuity_lock): missing, empty, or placeholder string '{field}'"
                    )

    # Declared references
    declared_ref_ids: set[str] = set()
    raw_refs = data.get("references")
    if raw_refs is not None:
        if not isinstance(raw_refs, list):
            errors.append("shotlist.json: 'references' must be a list")
        else:
            for ridx, ref_obj in enumerate(raw_refs):
                if not isinstance(ref_obj, dict):
                    errors.append(f"shotlist.json: references[{ridx}] must be an object")
                    continue
                rid = ref_obj.get("id")
                if not isinstance(rid, str) or not rid.strip():
                    errors.append(f"shotlist.json: references[{ridx}] missing non-empty string 'id'")
                    continue
                rid_clean = rid.strip()
                if rid_clean in declared_ref_ids:
                    errors.append(f"shotlist.json: duplicate reference id '{rid_clean}'")
                declared_ref_ids.add(rid_clean)

    # Optional lookbook[]
    lookbook_ids: set[str] = set()
    r2_lookbook = 0.0
    raw_lookbook = data.get("lookbook")
    if raw_lookbook is not None:
        if not isinstance(raw_lookbook, list):
            errors.append("shotlist.json: 'lookbook' must be a list")
        else:
            result["lookbook_count"] = len(raw_lookbook)
            for lidx, lb in enumerate(raw_lookbook):
                ctx = f"lookbook[{lidx}]"
                if not isinstance(lb, dict):
                    errors.append(f"shotlist.json: {ctx} must be an object")
                    continue
                lid = lb.get("id")
                if not isinstance(lid, str) or not lid.strip():
                    errors.append(f"shotlist.json ({ctx}): missing non-empty string 'id'")
                    lid_clean = f"index_{lidx}"
                else:
                    lid_clean = lid.strip()
                    ctx = f"lookbook.{lid_clean}"
                    if lid_clean in lookbook_ids:
                        errors.append(f"shotlist.json: duplicate lookbook id '{lid_clean}'")
                    if lid_clean in declared_ref_ids:
                        errors.append(
                            f"shotlist.json: lookbook id '{lid_clean}' collides with references[].id"
                        )
                    lookbook_ids.add(lid_clean)

                lkind = lb.get("kind")
                if not isinstance(lkind, str) or lkind not in VALID_LOOKBOOK_KINDS:
                    errors.append(
                        f"shotlist.json ({ctx}): invalid kind {lkind!r} "
                        f"(expected one of {sorted(VALID_LOOKBOOK_KINDS)})"
                    )

                lb_status = _check_status_and_version(lb, ctx, require_status=True)

                variants = lb.get("variants_requested")
                if not isinstance(variants, int) or isinstance(variants, bool) or variants < 1:
                    errors.append(
                        f"shotlist.json ({ctx}): 'variants_requested' must be an integer >= 1, "
                        f"got {variants!r}"
                    )

                r2_lookbook += _req_num(lb, "estimated_credits", ctx)

                _check_prompt_file(lb.get("prompt_file"), ctx)

                if lb_status == "LOCKED":
                    approved_var = lb.get("approved_variant")
                    if (
                        not isinstance(approved_var, str)
                        or not approved_var.strip()
                        or _CHECK_BRIEF.is_placeholder(approved_var)
                    ):
                        errors.append(
                            f"shotlist.json ({ctx}): status is LOCKED but 'approved_variant' "
                            "is missing, empty, or placeholder"
                        )

    all_ref_ids = declared_ref_ids | lookbook_ids

    def _check_ref_id_list(ref_list: Any, ctx: str) -> None:
        if ref_list is None:
            return
        if not isinstance(ref_list, list):
            errors.append(f"shotlist.json ({ctx}): expected list of reference/lookbook IDs")
            return
        for item in ref_list:
            if not isinstance(item, str) or not item.strip():
                errors.append(f"shotlist.json ({ctx}): invalid reference id {item!r}")
            elif item.strip() not in all_ref_ids:
                errors.append(
                    f"shotlist.json ({ctx}): references undeclared reference/lookbook id '{item.strip()}'"
                )

    shots = data.get("shots")
    if not isinstance(shots, list) or len(shots) == 0:
        errors.append("shotlist.json: 'shots' must be a non-empty list")
        return result

    result["shot_count"] = len(shots)
    shots_by_id: dict[str, dict[str, Any]] = {}
    still_sum = 0.0
    video_draft_sum = 0.0
    video_final_sum = 0.0
    audio_sum = 0.0
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
        sid = sid.strip()
        if sid in shots_by_id:
            errors.append(f"shotlist.json: duplicate shot id '{sid}'")
        shots_by_id[sid] = shot

        dur_val = shot.get("duration_s")
        if dur_val is None:
            errors.append(f"shotlist.json (shot {sid}): missing required positive 'duration_s'")
            all_have_duration = False
        elif isinstance(dur_val, bool) or not isinstance(dur_val, (int, float)) or not math.isfinite(float(dur_val)) or dur_val <= 0:
            errors.append(
                f"shotlist.json (shot {sid}.duration_s): must be a positive number, got {dur_val!r}"
            )
            all_have_duration = False
        else:
            total_duration_s += float(dur_val)

        _check_prompt_file(shot.get("prompt_file"), f"shot {sid}")
        _check_ref_id_list(shot.get("references"), f"shot {sid}.references")

        # Optional per-shot test_take_check
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
                        or _CHECK_BRIEF.is_placeholder(val)
                    ):
                        errors.append(
                            f"shotlist.json ({ttc_ctx}): missing, empty, or placeholder string '{field}'"
                        )

        still = shot.get("still")
        if still is not None:
            if not isinstance(still, dict):
                errors.append(f"shotlist.json (shot {sid}.still): must be an object or null")
            else:
                _check_status_and_version(still, f"shot {sid}.still", require_status=True)
                still_sum += _req_num(still, "estimated_credits", f"shot {sid}.still")
                _check_prompt_file(still.get("prompt_file"), f"shot {sid}.still")
                _check_ref_id_list(still.get("references"), f"shot {sid}.still.references")
                _check_ref_id_list(
                    still.get("image_references"), f"shot {sid}.still.image_references"
                )
                still_ref_count = (
                    (len(still["references"]) if isinstance(still.get("references"), list) else 0)
                    + (
                        len(still["image_references"])
                        if isinstance(still.get("image_references"), list)
                        else 0
                    )
                )
                s_model = str(still.get("model") or "").strip()
                if s_model in STILL_HARD_REF_CAPS and still_ref_count > STILL_HARD_REF_CAPS[s_model]:
                    errors.append(
                        f"shotlist.json (shot {sid}.still): {still_ref_count} image references "
                        f"exceeds live CEL limit ({STILL_HARD_REF_CAPS[s_model]}) for '{s_model}'"
                    )
                elif still_ref_count > 6:
                    warnings.append(
                        f"shotlist.json (shot {sid}.still): {still_ref_count} image references "
                        "exceeds optimal R3 still budget (3-5, max 6); prune off-screen refs to prevent attention dilution"
                    )

        video = shot.get("video")
        if not isinstance(video, dict):
            errors.append(f"shotlist.json (shot {sid}.video): missing or non-object 'video'")
        else:
            _check_status_and_version(video, f"shot {sid}.video", require_status=True)
            video_draft_sum += _req_num(
                video, "estimated_draft_credits", f"shot {sid}.video"
            )
            video_final_sum += _req_num(
                video, "estimated_final_credits", f"shot {sid}.video"
            )
            if video.get("model") == "cinematic_studio_video_4_0":
                if video.get("is_workflow") is not True:
                    errors.append(
                        f"shotlist.json (shot {sid}.video): model 'cinematic_studio_video_4_0' "
                        "requires 'is_workflow': true"
                    )
                vmode = video.get("mode")
                if not isinstance(vmode, str) or vmode not in VALID_CS4_MODES:
                    errors.append(
                        f"shotlist.json (shot {sid}.video): model 'cinematic_studio_video_4_0' "
                        f"requires 'mode' in {sorted(VALID_CS4_MODES)}, got {vmode!r}"
                    )
                has_frame_anchor = (
                    shot.get("start_image_from") is not None
                    or shot.get("end_image_from") is not None
                    or video.get("start_image_from") is not None
                    or video.get("end_image_from") is not None
                )
                if has_frame_anchor and vmode != "omni_reference":
                    errors.append(
                        f"shotlist.json (shot {sid}.video): model 'cinematic_studio_video_4_0' "
                        "with non-null start_image_from/end_image_from requires "
                        f"'mode': 'omni_reference', got {vmode!r}"
                    )
            _check_prompt_file(video.get("prompt_file"), f"shot {sid}.video")
            _check_ref_id_list(video.get("references"), f"shot {sid}.video.references")
            _check_ref_id_list(
                video.get("image_references"), f"shot {sid}.video.image_references"
            )
            v_model = video.get("model")
            draft_params = video.get("draft_params") if isinstance(video.get("draft_params"), dict) else {}
            final_params = video.get("final_params") if isinstance(video.get("final_params"), dict) else {}
            if v_model in ("cinematic_studio_video_4_0", "seedance_2_5"):
                final_res = str(final_params.get("resolution") or "").lower()
                if final_res in ("1080p", "4k") and final_params.get("bitrate_mode") != "high":
                    warnings.append(
                        f"shotlist.json (shot {sid}.video.final_params): '{v_model}' at {final_res} "
                        "should set 'bitrate_mode': 'high' (0 cr. surcharge vs. standard)"
                    )
            if v_model in ("bytedance_video_upscale", "topaz_video", "video_upscale") and (
                str(draft_params.get("resolution") or "").lower() == "480p"
            ):
                warnings.append(
                    f"shotlist.json (shot {sid}.video): pixel-upscaling a 480p draft with '{v_model}' "
                    "causes halos/artifacts; prefer native 1080p or a clean >=720p source"
                )
            video_ref_count = (
                (len(video["image_references"]) if isinstance(video.get("image_references"), list) else 0)
                + (len(video["references"]) if isinstance(video.get("references"), list) else 0)
            )
            start_src = video.get("start_image_from")
            if start_src is None:
                start_src = shot.get("start_image_from")
            end_src = video.get("end_image_from")
            if end_src is None:
                end_src = shot.get("end_image_from")
            has_start = start_src is not None
            has_end = end_src is not None
            total_video_imgs = video_ref_count + (1 if has_start else 0) + (1 if has_end else 0)
            if v_model in VIDEO_HARD_IMG_CAPS and total_video_imgs > VIDEO_HARD_IMG_CAPS[v_model]:
                errors.append(
                    f"shotlist.json (shot {sid}.video): {total_video_imgs} total images "
                    f"(start/end + image_references) exceeds live CEL limit ({VIDEO_HARD_IMG_CAPS[v_model]}) for '{v_model}'"
                )
            elif total_video_imgs > 5:
                warnings.append(
                    f"shotlist.json (shot {sid}.video): {total_video_imgs} total images "
                    "exceeds optimal R4/R5 video budget (2-5); prune off-screen refs to prevent texture bleed and rigid motion"
                )
            if v_model in ("wan3_0", "wan3_0_prime") and (has_start or has_end) and video_ref_count > 0:
                warnings.append(
                    f"shotlist.json (shot {sid}.video): '{v_model}' live CEL forbids combining "
                    "start_image/end_image with image_references; omit --image_references at runtime or use seedance_2_5/kling4_0"
                )
            if (
                isinstance(start_src, str)
                and start_src.strip().endswith(".last_frame")
                and video_ref_count == 0
                and v_model in ("seedance_2_5", "cinematic_studio_video_4_0", "kling4_0", "kling_4_0_flash")
            ):
                warnings.append(
                    f"shotlist.json (shot {sid}.video): bridging from '{start_src.strip()}' without "
                    "canonical R2 image_references risks photocopy cascade drift; include original locked prop/location IDs"
                )

        shot_audio = shot.get("audio")
        if isinstance(shot_audio, dict):
            if shot_audio.get("enabled", True) is True:
                audio_sum += _num(
                    shot_audio.get("estimated_credits"), f"shot {sid}.audio.estimated_credits"
                )
            _check_prompt_file(shot_audio.get("prompt_file"), f"shot {sid}.audio")

    # Duration check against target_duration_s (±0.5s)
    target_dur = data.get("target_duration_s")
    if target_dur is not None:
        if (
            isinstance(target_dur, bool)
            or not isinstance(target_dur, (int, float))
            or not math.isfinite(float(target_dur))
            or target_dur <= 0
        ):
            errors.append(
                f"shotlist.json: target_duration_s must be a positive number, got {target_dur!r}"
            )
        elif all_have_duration and abs(total_duration_s - float(target_dur)) > 0.5:
            errors.append(
                f"shotlist.json: sum(shots[].duration_s)={total_duration_s:.2f}s differs from "
                f"target_duration_s={float(target_dur):.2f}s by more than 0.5s"
            )

    # Validate start_image_from / end_image_from references
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
            if ref_str in all_ref_ids:
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
                    f"'<shot_id>.last_frame', reference ID, or lookbook ID, got '{ref_val}'"
                )

    # Top-level audio (sum credits ONLY when enabled is true!)
    top_audio = data.get("audio")
    if isinstance(top_audio, dict):
        if "estimated_credits" in top_audio and top_audio.get("enabled") is True:
            audio_sum += _num(top_audio.get("estimated_credits"), "audio.estimated_credits")
        _check_prompt_file(top_audio.get("prompt_file"), "audio")
        for track_name, track_obj in top_audio.items():
            if not isinstance(track_obj, dict):
                continue
            enabled = track_obj.get("enabled") is True
            _check_status_and_version(
                track_obj,
                f"audio.{track_name}",
                require_status=enabled,
                count_status=enabled,
            )
            if enabled:
                audio_sum += _num(
                    track_obj.get("estimated_credits"),
                    f"audio.{track_name}.estimated_credits",
                )
            _check_prompt_file(track_obj.get("prompt_file"), f"audio.{track_name}")
            tracks = track_obj.get("tracks")
            if isinstance(tracks, list):
                for tidx, tr in enumerate(tracks):
                    if isinstance(tr, dict):
                        _check_prompt_file(tr.get("prompt_file"), f"audio.{track_name}.tracks[{tidx}]")
                        _check_prompt_file(tr.get("script_file"), f"audio.{track_name}.tracks[{tidx}]")
    elif isinstance(top_audio, list):
        for idx, track_obj in enumerate(top_audio):
            if not isinstance(track_obj, dict):
                continue
            enabled = track_obj.get("enabled") is True
            _check_status_and_version(
                track_obj,
                f"audio[{idx}]",
                require_status=enabled,
                count_status=enabled,
            )
            if enabled:
                audio_sum += _num(
                    track_obj.get("estimated_credits"), f"audio[{idx}].estimated_credits"
                )
            _check_prompt_file(track_obj.get("prompt_file"), f"audio[{idx}]")

    r3_stills_audio = still_sum + audio_sum
    r4_draft_video = video_draft_sum
    r5_final_video = video_final_sum
    planned_total = r2_lookbook + r3_stills_audio + r4_draft_video + r5_final_video

    result["budget"] = {
        "r2_lookbook": _clean_num(r2_lookbook),
        "r3_stills_audio": _clean_num(r3_stills_audio),
        "r4_draft_video": _clean_num(r4_draft_video),
        "r5_final_video": _clean_num(r5_final_video),
        "planned_total": _clean_num(planned_total),
        "campaign_cap": campaign_cap,
        "remaining_planned": (
            _clean_num(campaign_cap - planned_total) if campaign_cap is not None else None
        ),
    }

    if campaign_cap is not None:
        if planned_total > campaign_cap:
            errors.append(
                f"shotlist.json: planned total ({_clean_num(planned_total)} credits across R2–R5) "
                f"exceeds brief.md Campaign cap ({campaign_cap} credits)"
            )
    else:
        warnings.append("brief.md Campaign cap unavailable; skipped shotlist cap comparison")

    return result


def resolve_shotlist_path(target: str | Path) -> Path:
    p = Path(target)
    if p.is_dir():
        return p / "shotlist.json"
    return p


def validate_campaign(
    target: str | Path, *, allow_draft: bool = False
) -> dict[str, Any]:
    """Validate cohesive campaign state (brief.md + optional taste-log.md + shotlist.json)."""
    shotlist_path = resolve_shotlist_path(target)
    errors: list[str] = []
    warnings: list[str] = []

    if not shotlist_path.is_file():
        return {
            "ok": False,
            "file_found": False,
            "campaign_dir": str(shotlist_path.parent),
            "shotlist_path": str(shotlist_path),
            "brief_status": None,
            "taste_log_entries": 0,
            "shot_count": 0,
            "lookbook_count": 0,
            "status_counts": {st: 0 for st in VALID_ASSET_STATUSES},
            "budget": None,
            "warnings": [],
            "errors": [f"shotlist file not found: {shotlist_path}"],
        }

    campaign_dir = shotlist_path.resolve().parent
    repo_root = _CHECK_BRIEF.find_repo_root(shotlist_path)

    # 1. brief.md
    brief_path = campaign_dir / "brief.md"
    brief_status: str | None = None
    campaign_cap: int | None = None
    if not brief_path.is_file():
        errors.append(f"missing required brief.md in campaign directory: {campaign_dir}")
    else:
        brief_report = _CHECK_BRIEF.validate_brief(brief_path)
        brief_status = brief_report.get("status")
        for berr in brief_report.get("errors") or []:
            errors.append(f"brief.md: {berr}")
        for bwarn in brief_report.get("warnings") or []:
            warnings.append(f"brief.md: {bwarn}")
        if brief_status not in {"active", "done"} and not allow_draft:
            errors.append(
                f"brief.md: status is '{brief_status}' "
                "(must be 'active' or 'done'; pass --allow-draft to allow draft)"
            )
        env = brief_report.get("budget_envelope") or {}
        if isinstance(env.get("campaign_cap"), int):
            campaign_cap = env["campaign_cap"]

    # 2. Optional taste-log.md
    taste_log_entries = 0
    taste_path = campaign_dir / "taste-log.md"
    if taste_path.is_file():
        taste_log_entries = _validate_taste_log(taste_path, errors)

    # 3. shotlist.json
    sl = _validate_shotlist(
        shotlist_path, campaign_dir, repo_root, campaign_cap, errors, warnings
    )

    return {
        "ok": len(errors) == 0,
        "file_found": True,
        "campaign_dir": str(campaign_dir),
        "shotlist_path": str(shotlist_path),
        "brief_status": brief_status,
        "taste_log_present": taste_path.is_file(),
        "taste_log_entries": taste_log_entries,
        "shot_count": sl["shot_count"],
        "lookbook_count": sl["lookbook_count"],
        "status_counts": sl["status_counts"],
        "budget": sl["budget"],
        "warnings": warnings,
        "errors": errors,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate campaign brief.md, optional taste-log.md, and shotlist.json."
    )
    parser.add_argument(
        "target",
        help="Path to campaign directory or shotlist.json file.",
    )
    parser.add_argument(
        "--allow-draft",
        action="store_true",
        help="Allow brief.md at status: draft without failing validation.",
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

    report = validate_campaign(args.target, allow_draft=args.allow_draft)

    if args.as_json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        if not report["file_found"]:
            print(f"ERROR: {report['errors'][0]}", file=sys.stderr)
            return 2

        state = "OK" if report["ok"] else "FAIL"
        print(
            f"[{state}] {report['shotlist_path']} "
            f"(brief={report['brief_status']}, shots={report['shot_count']}, "
            f"lookbook={report['lookbook_count']}, taste_log={report['taste_log_entries']} entries)"
        )
        sc = report["status_counts"]
        print(
            f"  Assets: LOCKED={sc['LOCKED']}, IN_REVIEW={sc['IN_REVIEW']}, "
            f"ITERATING={sc['ITERATING']}, DRAFT={sc['DRAFT']}"
        )
        b = report.get("budget")
        if b:
            cap_str = str(b["campaign_cap"]) if b["campaign_cap"] is not None else "?"
            print(
                f"  Budget: R2={b['r2_lookbook']}, R3={b['r3_stills_audio']}, "
                f"R4={b['r4_draft_video']}, R5={b['r5_final_video']} | "
                f"Total={b['planned_total']} / {cap_str} credits"
            )
        for w in report["warnings"]:
            print(f"  WARN: {w}")
        for e in report["errors"]:
            print(f"  ERROR: {e}")

    if not report["file_found"]:
        return 2
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
