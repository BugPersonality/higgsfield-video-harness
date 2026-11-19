#!/usr/bin/env python3
"""Deterministic media QA and 3x2 contact-sheet generator via ffmpeg/ffprobe."""

from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import argparse
import json
import math
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

SAMPLE_W = 160
SAMPLE_H = 90
SAMPLE_FPS = 4
TILE_SIZE = 16
FRAME_BYTES = SAMPLE_W * SAMPLE_H
STILL_DIFF_THRESHOLD = 1.0
SILENT_MEAN_DB_THRESHOLD = -60.0
VOICE_RMS_ACTIVE_DB = -34.0


def _ensure_ffmpeg_tools() -> tuple[str, str]:
    ffmpeg = shutil.which("ffmpeg")
    ffprobe = shutil.which("ffprobe")
    if not ffmpeg or not ffprobe:
        missing = [name for name, path in (("ffmpeg", ffmpeg), ("ffprobe", ffprobe)) if not path]
        raise RuntimeError(f"required tool(s) not found in PATH: {', '.join(missing)}")
    return ffmpeg, ffprobe


def _parse_rational(rate_str: str | None) -> float | None:
    if not rate_str or rate_str == "0/0":
        return None
    if "/" in rate_str:
        num_s, den_s = rate_str.split("/", 1)
        try:
            num, den = float(num_s), float(den_s)
            if den == 0:
                return None
            val = num / den
            return round(val, 4) if val > 0 else None
        except ValueError:
            return None
    try:
        val = float(rate_str)
        return round(val, 4) if val > 0 else None
    except ValueError:
        return None


def _parse_finite_float(val: Any) -> float | None:
    if val is None:
        return None
    try:
        f = float(val)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(f):
        return None
    return round(f, 3)


def _ffprobe_json(ffprobe: str, media_path: Path) -> dict[str, Any]:
    proc = subprocess.run(
        [
            ffprobe,
            "-v",
            "error",
            "-show_format",
            "-show_streams",
            "-of",
            "json",
            str(media_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"ffprobe failed (exit {proc.returncode}): {proc.stderr.strip()}")
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"ffprobe returned invalid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise TypeError("ffprobe returned unexpected root type")
    return data


def _detect_black_gaps(
    ffmpeg: str, video_path: Path, black_min: float
) -> list[dict[str, float]]:
    proc = subprocess.run(
        [
            ffmpeg,
            "-v",
            "info",
            "-i",
            str(video_path),
            "-vf",
            f"blackdetect=d={black_min}:pix_th=0.10",
            "-an",
            "-f",
            "null",
            "-",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    gaps: list[dict[str, float]] = []
    for m in re.finditer(
        r"black_start:([0-9.]+)\s+black_end:([0-9.]+)\s+black_duration:([0-9.]+)",
        proc.stderr,
    ):
        gaps.append(
            {
                "start": round(float(m.group(1)), 3),
                "end": round(float(m.group(2)), 3),
                "duration": round(float(m.group(3)), 3),
            }
        )
    return gaps


def _max_tile_diff(frame_a: bytes, frame_b: bytes) -> float:
    if frame_a == frame_b:
        return 0.0
    max_diff = 0.0
    for ty in range(0, SAMPLE_H, TILE_SIZE):
        y_end = min(ty + TILE_SIZE, SAMPLE_H)
        for tx in range(0, SAMPLE_W, TILE_SIZE):
            x_end = min(tx + TILE_SIZE, SAMPLE_W)
            total = 0
            count = (y_end - ty) * (x_end - tx)
            for row in range(ty, y_end):
                offset = row * SAMPLE_W
                s_a = frame_a[offset + tx : offset + x_end]
                s_b = frame_b[offset + tx : offset + x_end]
                for pa, pb in zip(s_a, s_b):
                    diff = pa - pb
                    total += diff if diff >= 0 else -diff
            mean_diff = total / count
            max_diff = max(max_diff, mean_diff)
    return max_diff


def _analyze_motion(
    ffmpeg: str,
    video_path: Path,
    duration: float,
    max_still: float,
    max_frozen_tail: float | None = None,
) -> dict[str, Any]:
    proc = subprocess.run(
        [
            ffmpeg,
            "-v",
            "error",
            "-i",
            str(video_path),
            "-vf",
            f"fps={SAMPLE_FPS},scale={SAMPLE_W}:{SAMPLE_H},format=gray",
            "-f",
            "rawvideo",
            "-pix_fmt",
            "gray",
            "-",
        ],
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        err_msg = proc.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"motion sampling failed: {err_msg}")

    raw = proc.stdout
    num_frames = len(raw) // FRAME_BYTES
    if num_frames < 2:
        return {
            "sampled_frames": num_frames,
            "moving_seconds": 0.0,
            "max_still_stretch": 0.0,
            "still_stretches": [],
            "frozen_tail": None,
        }

    dt = 1.0 / SAMPLE_FPS
    diffs: list[float] = []
    prev = raw[0:FRAME_BYTES]
    for i in range(1, num_frames):
        curr = raw[i * FRAME_BYTES : (i + 1) * FRAME_BYTES]
        diffs.append(_max_tile_diff(prev, curr))
        prev = curr

    # Identify contiguous still runs (max_tile_diff < STILL_DIFF_THRESHOLD)
    still_runs: list[dict[str, float]] = []
    run_start_idx: int | None = None
    for idx, d in enumerate(diffs):
        is_still = d < STILL_DIFF_THRESHOLD
        if is_still and run_start_idx is None:
            run_start_idx = idx
        elif not is_still and run_start_idx is not None:
            start_t = run_start_idx * dt
            end_t = idx * dt
            still_runs.append(
                {
                    "start": round(start_t, 3),
                    "end": round(end_t, 3),
                    "duration": round(end_t - start_t, 3),
                    "reaches_end": False,
                }
            )
            run_start_idx = None

    if run_start_idx is not None:
        start_t = run_start_idx * dt
        end_t = max(len(diffs) * dt, duration)
        still_runs.append(
            {
                "start": round(start_t, 3),
                "end": round(end_t, 3),
                "duration": round(end_t - start_t, 3),
                "reaches_end": True,
            }
        )

    long_still = [
        {"start": r["start"], "end": r["end"], "duration": r["duration"]}
        for r in still_runs
        if r["duration"] > max_still
    ]
    max_still_observed = max((r["duration"] for r in still_runs), default=0.0)

    # Compute moving time before any trailing still run
    tail_run = still_runs[-1] if (still_runs and still_runs[-1]["reaches_end"]) else None
    if tail_run is not None:
        tail_start_idx = round(tail_run["start"] / dt)
        moving_before_tail = sum(
            1 for d in diffs[:tail_start_idx] if d >= STILL_DIFF_THRESHOLD
        ) * dt
    else:
        moving_before_tail = sum(1 for d in diffs if d >= STILL_DIFF_THRESHOLD) * dt

    frozen_tail_threshold = max_still if max_frozen_tail is None else max_frozen_tail
    frozen_tail: dict[str, float] | None = None
    if max_still < 60.0 and tail_run is not None and tail_run["duration"] >= frozen_tail_threshold:
        moved_enough = moving_before_tail >= 1.5 or (
            duration > 0 and moving_before_tail >= 0.30 * duration and moving_before_tail > 0
        )
        mostly_frozen = duration > 0 and moving_before_tail > 0 and tail_run["duration"] >= 0.70 * duration
        if moved_enough or mostly_frozen:
            frozen_tail = {
                "start": tail_run["start"],
                "end": tail_run["end"],
                "duration": tail_run["duration"],
                "moving_before_tail": round(moving_before_tail, 3),
                "threshold": frozen_tail_threshold,
            }

    return {
        "sampled_frames": num_frames,
        "moving_seconds": round(
            sum(1 for d in diffs if d >= STILL_DIFF_THRESHOLD) * dt, 3
        ),
        "max_still_stretch": round(max_still_observed, 3),
        "still_stretches": long_still,
        "frozen_tail": frozen_tail,
    }


def _measure_volumedetect(ffmpeg: str, media_path: Path) -> dict[str, float | None]:
    proc = subprocess.run(
        [
            ffmpeg,
            "-v",
            "info",
            "-i",
            str(media_path),
            "-vn",
            "-af",
            "volumedetect",
            "-f",
            "null",
            "-",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    mean_m = re.search(r"mean_volume:\s*([-\d.]+)\s*dB", proc.stderr)
    max_m = re.search(r"max_volume:\s*([-\d.]+)\s*dB", proc.stderr)
    return {
        "mean_volume_db": _parse_finite_float(mean_m.group(1)) if mean_m else None,
        "max_volume_db": _parse_finite_float(max_m.group(1)) if max_m else None,
    }


def _measure_loudness(ffmpeg: str, media_path: Path) -> dict[str, float | None]:
    proc = subprocess.run(
        [
            ffmpeg,
            "-v",
            "info",
            "-i",
            str(media_path),
            "-vn",
            "-af",
            "loudnorm=I=-14:TP=-1:LRA=11:print_format=json",
            "-f",
            "null",
            "-",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    # Extract JSON block containing input_i from stderr
    matches = list(re.finditer(r"\{[^{}]*\"input_i\"[^{}]*\}", proc.stderr, re.DOTALL))
    if not matches:
        return {
            "integrated_lufs": None,
            "true_peak_dbtp": None,
            "lra": None,
            "threshold": None,
        }
    try:
        data = json.loads(matches[-1].group(0))
    except json.JSONDecodeError:
        return {
            "integrated_lufs": None,
            "true_peak_dbtp": None,
            "lra": None,
            "threshold": None,
        }
    return {
        "integrated_lufs": _parse_finite_float(data.get("input_i")),
        "true_peak_dbtp": _parse_finite_float(data.get("input_tp")),
        "lra": _parse_finite_float(data.get("input_lra")),
        "threshold": _parse_finite_float(data.get("input_thresh")),
    }


def _build_contact_sheet(
    ffmpeg: str, video_path: Path, duration: float, sheet_path: Path
) -> None:
    sheet_path.parent.mkdir(parents=True, exist_ok=True)
    t_start = min(0.2, max(0.0, duration * 0.1))
    t_end = max(t_start, duration - 0.2)
    if duration <= 0.4:
        t_start = 0.0
        t_end = max(0.0, duration - 0.02)

    timestamps = [
        t_start + (t_end - t_start) * (i / 5.0) for i in range(6)
    ]

    with tempfile.TemporaryDirectory(prefix="qa_sheet_") as tmp_dir:
        tmp = Path(tmp_dir)
        extracted: list[Path] = []
        for idx, ts in enumerate(timestamps):
            frame_out = tmp / f"f{idx}.png"
            proc = subprocess.run(
                [
                    ffmpeg,
                    "-v",
                    "error",
                    "-ss",
                    f"{ts:.3f}",
                    "-i",
                    str(video_path),
                    "-frames:v",
                    "1",
                    "-vf",
                    "scale=480:-2",
                    "-y",
                    str(frame_out),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            if proc.returncode != 0 or not frame_out.is_file():
                # Retry slightly earlier if seek landed past final keyframe
                fallback_ts = max(0.0, ts - 0.15)
                proc2 = subprocess.run(
                    [
                        ffmpeg,
                        "-v",
                        "error",
                        "-ss",
                        f"{fallback_ts:.3f}",
                        "-i",
                        str(video_path),
                        "-frames:v",
                        "1",
                        "-vf",
                        "scale=480:-2",
                        "-y",
                        str(frame_out),
                    ],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if proc2.returncode != 0 or not frame_out.is_file():
                    raise RuntimeError(
                        f"failed to extract contact sheet frame {idx} at {ts:.3f}s: "
                        f"{proc2.stderr.strip()}"
                    )
            extracted.append(frame_out)

        tile_proc = subprocess.run(
            [
                ffmpeg,
                "-v",
                "error",
                "-i",
                str(tmp / "f%d.png"),
                "-vf",
                "scale=480:-2,tile=3x2",
                "-frames:v",
                "1",
                "-y",
                str(sheet_path),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if tile_proc.returncode != 0 or not sheet_path.is_file():
            raise RuntimeError(
                f"failed to tile 3x2 contact sheet: {tile_proc.stderr.strip()}"
            )


def inspect_clip(
    video_path: Path,
    *,
    sheet_path: Path | None = None,
    max_still: float = 3.0,
    max_frozen_tail: float | None = None,
    black_min: float = 0.5,
    allow_silent: bool = False,
    strict: bool = False,
) -> dict[str, Any]:
    ffmpeg, ffprobe = _ensure_ffmpeg_tools()
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []

    probe = _ffprobe_json(ffprobe, video_path)
    streams = probe.get("streams") or []
    fmt = probe.get("format") or {}

    vstream = next((s for s in streams if s.get("codec_type") == "video"), None)
    astream = next((s for s in streams if s.get("codec_type") == "audio"), None)

    duration = _parse_finite_float(fmt.get("duration"))
    if duration is None and vstream is not None:
        duration = _parse_finite_float(vstream.get("duration"))

    width = int(vstream["width"]) if vstream and vstream.get("width") else None
    height = int(vstream["height"]) if vstream and vstream.get("height") else None
    fps = None
    if vstream:
        fps = _parse_rational(vstream.get("avg_frame_rate")) or _parse_rational(
            vstream.get("r_frame_rate")
        )

    metadata = {
        "duration": duration,
        "width": width,
        "height": height,
        "fps": fps,
        "video_codec": vstream.get("codec_name") if vstream else None,
        "has_audio": astream is not None,
        "audio_codec": astream.get("codec_name") if astream else None,
        "sample_rate": int(astream["sample_rate"])
        if astream and astream.get("sample_rate")
        else None,
        "channels": int(astream["channels"])
        if astream and astream.get("channels")
        else None,
    }

    if vstream is None or not width or not height:
        errors.append({"code": "missing_video_stream", "message": "no valid video stream found"})
    if duration is None or duration <= 0:
        errors.append({"code": "invalid_duration", "message": f"invalid media duration: {duration}"})

    black_gaps: list[dict[str, float]] = []
    motion: dict[str, Any] = {}
    volume: dict[str, float | None] = {"mean_volume_db": None, "max_volume_db": None}
    loudness: dict[str, float | None] = {
        "integrated_lufs": None,
        "true_peak_dbtp": None,
        "lra": None,
        "threshold": None,
    }

    if vstream is not None and duration and duration > 0:
        black_gaps = _detect_black_gaps(ffmpeg, video_path, black_min)
        for gap in black_gaps:
            errors.append(
                {
                    "code": "black_gap",
                    "message": (
                        f"black frame stretch detected: {gap['start']}s–{gap['end']}s "
                        f"({gap['duration']}s >= {black_min}s)"
                    ),
                    **gap,
                }
            )

        motion = _analyze_motion(
            ffmpeg,
            video_path,
            duration,
            max_still,
            max_frozen_tail=max_frozen_tail,
        )
        if max_still < 60.0 and motion.get("moving_seconds", 0.0) == 0.0 and duration >= 1.5:
            errors.append(
                {
                    "code": "fully_static_clip",
                    "message": (
                        f"clip is completely static across {duration}s (moving_seconds=0.0)"
                    ),
                    "duration": duration,
                    "moving_seconds": 0.0,
                }
            )
        for st in motion.get("still_stretches") or []:
            entry = {
                "code": "still_stretch",
                "message": (
                    f"static frame stretch detected: {st['start']}s–{st['end']}s "
                    f"({st['duration']}s > {max_still}s)"
                ),
                **st,
            }
            if strict:
                errors.append(entry)
            else:
                warnings.append(entry)

        ft = motion.get("frozen_tail")
        if ft is not None:
            errors.append(
                {
                    "code": "frozen_tail",
                    "message": (
                        f"frozen I2V tail detected: froze at {ft['start']}s–{ft['end']}s "
                        f"({ft['duration']}s) after {ft['moving_before_tail']}s of motion"
                    ),
                    **ft,
                }
            )

        if sheet_path is not None:
            _build_contact_sheet(ffmpeg, video_path, duration, sheet_path)

    if astream is None:
        if not allow_silent:
            errors.append(
                {"code": "silent_audio", "message": "missing audio stream (pass --allow-silent to permit)"}
            )
    else:
        volume = _measure_volumedetect(ffmpeg, video_path)
        loudness = _measure_loudness(ffmpeg, video_path)
        mean_db = volume["mean_volume_db"]
        if (mean_db is None or mean_db < SILENT_MEAN_DB_THRESHOLD) and not allow_silent:
            errors.append(
                {
                    "code": "silent_audio",
                    "message": (
                        f"audio track is silent (mean_volume={mean_db} dB < "
                        f"{SILENT_MEAN_DB_THRESHOLD} dB)"
                    ),
                    "mean_volume_db": mean_db,
                }
            )

    return {
        "ok": len(errors) == 0,
        "command": "clip",
        "path": str(video_path),
        "sheet": str(sheet_path) if sheet_path else None,
        "metadata": metadata,
        "black_gaps": black_gaps,
        "motion": motion,
        "volume": volume,
        "loudness": loudness,
        "warnings": warnings,
        "errors": errors,
    }


def inspect_render(
    video_path: Path,
    *,
    sheet_path: Path | None = None,
    target_lufs: float = -14.0,
    lufs_tolerance: float = 1.0,
    max_true_peak: float = -1.0,
    max_still: float = 3.0,
    max_frozen_tail: float | None = None,
    black_min: float = 0.5,
    allow_silent: bool = False,
    strict: bool = False,
) -> dict[str, Any]:
    report = inspect_clip(
        video_path,
        sheet_path=sheet_path,
        max_still=max_still,
        max_frozen_tail=max_frozen_tail,
        black_min=black_min,
        allow_silent=allow_silent,
        strict=strict,
    )
    report["command"] = "render"

    duration = report["metadata"].get("duration") or 0.0
    loudness = report["loudness"]
    errors: list[dict[str, Any]] = report["errors"]

    if not allow_silent and duration >= 3.0 and report["metadata"].get("has_audio"):
        lufs = loudness.get("integrated_lufs")
        tp = loudness.get("true_peak_dbtp")
        low = target_lufs - lufs_tolerance
        high = target_lufs + lufs_tolerance
        if lufs is None or not (low <= lufs <= high):
            errors.append(
                {
                    "code": "loudness_out_of_range",
                    "message": (
                        f"integrated loudness {lufs} LUFS outside allowed range "
                        f"[{low:.1f}, {high:.1f}] LUFS"
                    ),
                    "integrated_lufs": lufs,
                    "target_lufs": target_lufs,
                    "tolerance": lufs_tolerance,
                }
            )
        if tp is None or tp > max_true_peak:
            errors.append(
                {
                    "code": "true_peak_exceeded",
                    "message": (
                        f"true peak {tp} dBTP exceeds limit {max_true_peak:.1f} dBTP"
                    ),
                    "true_peak_dbtp": tp,
                    "max_true_peak": max_true_peak,
                }
            )

    report["ok"] = len(errors) == 0
    return report


def inspect_voice(
    audio_path: Path,
    *,
    window: float,
    min_margin_low: float = 2.0,
    min_margin_high: float = 0.2,
) -> dict[str, Any]:
    ffmpeg, ffprobe = _ensure_ffmpeg_tools()
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []

    probe = _ffprobe_json(ffprobe, audio_path)
    streams = probe.get("streams") or []
    fmt = probe.get("format") or {}
    astream = next((s for s in streams if s.get("codec_type") == "audio"), None)

    duration = _parse_finite_float(fmt.get("duration"))
    if duration is None and astream is not None:
        duration = _parse_finite_float(astream.get("duration"))

    metadata = {
        "duration": duration,
        "audio_codec": astream.get("codec_name") if astream else None,
        "sample_rate": int(astream["sample_rate"])
        if astream and astream.get("sample_rate")
        else None,
        "channels": int(astream["channels"])
        if astream and astream.get("channels")
        else None,
    }

    if astream is None:
        errors.append({"code": "missing_audio_stream", "message": "no readable audio stream found"})
        return {
            "ok": False,
            "command": "voice",
            "path": str(audio_path),
            "metadata": metadata,
            "window": window,
            "speech_end": None,
            "loudness": None,
            "warnings": warnings,
            "errors": errors,
        }

    proc = subprocess.run(
        [
            ffmpeg,
            "-v",
            "error",
            "-i",
            str(audio_path),
            "-af",
            (
                "aformat=channel_layouts=mono,aresample=16000,"
                "asetnsamples=n=1600:p=0,astats=metadata=1:reset=1,"
                "ametadata=mode=print:key=lavfi.astats.Overall.RMS_level:file=-"
            ),
            "-f",
            "null",
            "-",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"voice RMS analysis failed: {proc.stderr.strip()}")

    last_active_end: float | None = None
    current_pts_time: float | None = None
    bins_analyzed = 0

    for line in proc.stdout.splitlines():
        pts_m = re.search(r"pts_time:([0-9.]+)", line)
        if pts_m:
            current_pts_time = float(pts_m.group(1))
            continue
        rms_m = re.match(r"lavfi\.astats\.Overall\.RMS_level=(.+)$", line.strip())
        if rms_m and current_pts_time is not None:
            bins_analyzed += 1
            rms_val = _parse_finite_float(rms_m.group(1))
            if rms_val is not None and rms_val > VOICE_RMS_ACTIVE_DB:
                last_active_end = round(current_pts_time + 0.1, 3)

    speech_end = last_active_end if last_active_end is not None else 0.0
    min_allowed = round(window - min_margin_low, 3)
    max_allowed = round(window - min_margin_high, 3)

    if last_active_end is None:
        errors.append(
            {
                "code": "no_speech_detected",
                "message": f"no 100ms audio bin exceeded {VOICE_RMS_ACTIVE_DB} dBFS",
            }
        )
    elif speech_end < min_allowed:
        errors.append(
            {
                "code": "voice_too_short",
                "message": (
                    f"speech ends at {speech_end}s, shorter than minimum "
                    f"{min_allowed}s (window={window}s - {min_margin_low}s)"
                ),
                "speech_end": speech_end,
                "min_allowed": min_allowed,
            }
        )
    elif speech_end > max_allowed:
        errors.append(
            {
                "code": "voice_too_long",
                "message": (
                    f"speech ends at {speech_end}s, longer than maximum "
                    f"{max_allowed}s (window={window}s - {min_margin_high}s)"
                ),
                "speech_end": speech_end,
                "max_allowed": max_allowed,
            }
        )

    loudness = _measure_loudness(ffmpeg, audio_path)

    return {
        "ok": len(errors) == 0,
        "command": "voice",
        "path": str(audio_path),
        "metadata": metadata,
        "window": window,
        "min_allowed": min_allowed,
        "max_allowed": max_allowed,
        "speech_end": speech_end,
        "bins_analyzed": bins_analyzed,
        "loudness": loudness,
        "warnings": warnings,
        "errors": errors,
    }


def _print_human(report: dict[str, Any]) -> None:
    state = "OK" if report["ok"] else "FAIL"
    cmd = report["command"]
    meta = report.get("metadata") or {}
    if cmd in ("clip", "render"):
        loud = report.get("loudness") or {}
        print(
            f"[{state}] {cmd}: {report['path']} "
            f"({meta.get('width')}x{meta.get('height')} @{meta.get('fps')}fps, "
            f"dur={meta.get('duration')}s, codec={meta.get('video_codec')}, "
            f"audio={meta.get('has_audio')}, lufs={loud.get('integrated_lufs')})"
        )
        if report.get("sheet"):
            print(f"  Contact sheet: {report['sheet']}")
    else:
        loud = report.get("loudness") or {}
        print(
            f"[{state}] voice: {report['path']} "
            f"(speech_end={report.get('speech_end')}s, "
            f"allowed=[{report.get('min_allowed')}s, {report.get('max_allowed')}s], "
            f"lufs={loud.get('integrated_lufs')})"
        )
    for w in report.get("warnings") or []:
        print(f"  WARN [{w['code']}]: {w['message']}")
    for e in report.get("errors") or []:
        print(f"  ERROR [{e['code']}]: {e['message']}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Deterministic FFmpeg/ffprobe media QA and 3x2 contact-sheet builder."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # clip
    cl = sub.add_parser("clip", help="Validate a single generated video clip.")
    cl.add_argument("video", help="Path to video file.")
    cl.add_argument("--sheet", default=None, help="Output path for 3x2 PNG contact sheet.")
    cl.add_argument(
        "--max-still", type=float, default=3.0, help="Max static frame duration in seconds (default: 3.0)."
    )
    cl.add_argument(
        "--max-frozen-tail",
        type=float,
        default=None,
        help="Max frozen tail duration in seconds before error (default: matches --max-still).",
    )
    cl.add_argument(
        "--black-min", type=float, default=0.5, help="Minimum black gap duration to flag in seconds (default: 0.5)."
    )
    cl.add_argument("--allow-silent", action="store_true", help="Allow missing or silent audio.")
    cl.add_argument("--strict", action="store_true", help="Treat still_stretch warnings as errors.")
    cl.add_argument("--json", action="store_true", dest="as_json", help="Emit JSON report.")

    # voice
    vo = sub.add_parser("voice", help="Validate VO timing against target shot/spot window.")
    vo.add_argument("audio", help="Path to audio file.")
    vo.add_argument("--window", type=float, required=True, help="Target window duration in seconds.")
    vo.add_argument(
        "--min-margin-low",
        type=float,
        default=2.0,
        help="Minimum allowable undershoot below window in seconds (default: 2.0).",
    )
    vo.add_argument(
        "--min-margin-high",
        type=float,
        default=0.2,
        help="Minimum breathing margin before end of window in seconds (default: 0.2).",
    )
    vo.add_argument("--json", action="store_true", dest="as_json", help="Emit JSON report.")

    # render
    rn = sub.add_parser("render", help="Validate final assembled video render and loudness.")
    rn.add_argument("video", help="Path to assembled master video file.")
    rn.add_argument("--sheet", default=None, help="Output path for 3x2 PNG contact sheet.")
    rn.add_argument("--target-lufs", type=float, default=-14.0, help="Target integrated LUFS (default: -14.0).")
    rn.add_argument("--lufs-tolerance", type=float, default=1.0, help="Allowed +/- LUFS tolerance (default: 1.0).")
    rn.add_argument("--max-true-peak", type=float, default=-1.0, help="Strict max true peak dBTP ceiling (default: -1.0).")
    rn.add_argument(
        "--max-still", type=float, default=3.0, help="Max static frame duration in seconds (default: 3.0)."
    )
    rn.add_argument(
        "--max-frozen-tail",
        type=float,
        default=None,
        help="Max frozen tail duration in seconds before error (default: matches --max-still).",
    )
    rn.add_argument(
        "--black-min", type=float, default=0.5, help="Minimum black gap duration to flag in seconds (default: 0.5)."
    )
    rn.add_argument("--allow-silent", action="store_true", help="Allow missing or silent audio.")
    rn.add_argument("--strict", action="store_true", help="Treat still_stretch warnings as errors.")
    rn.add_argument("--json", action="store_true", dest="as_json", help="Emit JSON report.")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    target_path = Path(args.video if args.command in ("clip", "render") else args.audio)
    if not target_path.is_file():
        msg = f"media file not found: {target_path}"
        if args.as_json:
            print(json.dumps({"ok": False, "error": msg}, indent=2))
        else:
            print(f"ERROR: {msg}", file=sys.stderr)
        return 2

    try:
        if args.command == "clip":
            report = inspect_clip(
                target_path,
                sheet_path=Path(args.sheet) if args.sheet else None,
                max_still=args.max_still,
                max_frozen_tail=args.max_frozen_tail,
                black_min=args.black_min,
                allow_silent=args.allow_silent,
                strict=args.strict,
            )
        elif args.command == "voice":
            if args.window <= 0:
                msg = "--window must be positive"
                if args.as_json:
                    print(json.dumps({"ok": False, "error": msg}, indent=2))
                else:
                    print(f"ERROR: {msg}", file=sys.stderr)
                return 2
            report = inspect_voice(
                target_path,
                window=args.window,
                min_margin_low=args.min_margin_low,
                min_margin_high=args.min_margin_high,
            )
        else:
            report = inspect_render(
                target_path,
                sheet_path=Path(args.sheet) if args.sheet else None,
                target_lufs=args.target_lufs,
                lufs_tolerance=args.lufs_tolerance,
                max_true_peak=args.max_true_peak,
                max_still=args.max_still,
                max_frozen_tail=args.max_frozen_tail,
                black_min=args.black_min,
                allow_silent=args.allow_silent,
                strict=args.strict,
            )
    except RuntimeError as exc:
        if args.as_json:
            print(json.dumps({"ok": False, "error": str(exc)}, indent=2))
        else:
            print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if args.as_json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        _print_human(report)

    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
