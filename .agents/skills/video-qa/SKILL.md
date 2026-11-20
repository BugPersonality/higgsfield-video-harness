---
name: video-qa
description: "Internal defect and taste-drift filtering plus Dailies grid packaging. Use when running qa_media.py probes, 1:1 full-res crop sheets, or lookbook grids, inspecting Lookbook variants, stills, contact sheets, or R5/upscale 1:1 crops via view_image, or filtering defects before Director Dailies."
---

# Video QA

**Internal filter before Dailies—taste belongs to the Director.** Follow [Pre-Dailies Visual Critic](../../../docs/delegation.md#pre-dailies-visual-critic): fresh `reviewer-agent` lanes (`fork_turns: "none"`, `view_image`) strip defects, continuity breaks, and `TASTE_REGRESSION`s while leaving `A / B / C` picks and `LOCKED` sign-off solely to the Director.

**Deterministic probes & labeled grids (`scripts/qa_media.py`).** Pass `--json` when capturing reports for `reviewer-agent` handoffs (`make qa-*` runs the same checks for human output):
- `scripts/qa_media.py clip <mp4> --sheet <png> [--crops <png>] [--crop-focus thirds|center|left|right] --json` (`make qa-clip`) — probes resolution, FPS, codec, duration, `video_bitrate_kbps`, `hf_edge_energy` (Laplacian sharpness proxy), audio, black gaps (`>= 0.5s`), `frozen_tail`, `fully_static_clip`, warns on `non_standard_dimensions` (`1918×1080`) and `low_video_bitrate`, writes a `3x2` contact sheet, and—when `--crops` is passed—writes an **unscaled `1:1` native-pixel 3-frame crop strip** (default `thirds` sweeps left/center/right).
- `scripts/qa_media.py batch <clip1> <clip2> ... [--strict] --json` (`make qa-batch`) — audits cross-shot resolution, FPS, non-multiple-of-4 dimensions, low `1080p` bitrate, and `hf_sharpness_outlier` warnings (`> 1.5×` clean median) across an `R5` cut before `make assemble`.
- `scripts/qa_media.py voice <wav> --window <sec> --json` (`make qa-voice`) — checks 100ms RMS active speech bounds against the target window.
- `scripts/qa_media.py render <mp4> --sheet <png> [--crops <png>] --json` (`make qa-render`) — enforces `-14 LUFS (±1.0 LU)` and `<= -1.0 dBTP` on `draft_cut.mp4` / `master.mp4`.
- `make lookbook FILES="..." OUT=<png> LABELS="A,B,C"` — burns crisp visual badges onto tiles for `R2` Lookbooks and `R3` stills strips.
- `scripts/qa_media.py slice <sheet.png> --out-dir <dir> --rows 3 --cols 3 [--trim 4] --json` (`make slice-grid`) — splits `2x2`/`3x3` multi-angle sheets (`nano_banana_2_shots`) into clean standalone PNG tiles before upload.

**Mandatory `1:1` native-pixel inspection & binary `R5` / upscale rubric.** Shrunk `480px` `3x2` sheets hide halos, face melt, and blotches. Every `R5` or upscaled handoff MUST include `--crops <png>` (and `batch --strict --json` before assembly) inspected via `view_image` against this exact verdict mapping:

| Observed Signal (JSON or `1:1` `--crops`) | Verdict | Defect Class | `reopen_owner` & Required Action |
| :--- | :--- | :--- | :--- |
| Missing `qa_media.py` JSON, `3x2` sheet, `R5` `--crops` strip, or `taste-log.md` | `REVIEW_HANDOFF_INVALID` | — | `Worker(<asset_id>)` — produce missing proof; never pass blindly |
| White/dark edge halo, ringing, muddy/plastic face, or eyelid/cheek color blotch on `--crops` | `FAIL` | `MEDIA_TECH_DEFECT` | `Root Producer` — stop upscaling; switch shot to native `1080p` path |
| `non_standard_dimensions` (`1918×1080`), `resolution_mismatch`, or `fps_mismatch` in `batch` | `FAIL` | `MEDIA_TECH_DEFECT` | `Root Producer` — re-render natively at exact `1920×1080` & `fps_target` |
| `hf_sharpness_outlier` (`> 1.5×` clean median) + visible crunch/ringing on `--crops` | `FAIL` | `MEDIA_TECH_DEFECT` | `Root Producer` — replace upscaled outlier with native `1080p` take |
| `hf_sharpness_outlier` (`> 1.5×`) between clean native shots (zero halos/melt on `--crops`) | `CONCERNS` | `CONCERN` | `Root Producer` — confirm genuine scene detail; match via shared 35mm grain if needed |
| `low_video_bitrate` (`< 1800 kbps` at `1080p`) with visible compression softness/banding | `FAIL` | `MEDIA_TECH_DEFECT` | `Worker(<asset_id>)` — re-run with `--bitrate_mode high` (or alternate `1080p` engine) |
| 180° room flip, wrong reverse wall, teleporting door/window, or front-pose mirror clone | `FAIL` | `CONTINUITY_DEFECT` | `Root Producer` — lock missing Reverse Wall (`R2B`) and re-stage `R3` still with `N/E/S/W` `CAM` facing |
| Prop/building Scale Drift, *Lighting Bake-In*, or off-screen prop bleeding into frame | `FAIL` | `VISUAL_DRIFT_DEFECT` | `Worker(<asset_id>)` — prune off-screen refs, bind Scale Ref / neutral `#808080` prop plate, re-stage `R3` |
| Single handheld prop warps mid-clip while acting, camera, and set stay locked | `FAIL` | `VISUAL_DRIFT_DEFECT` | `Root Producer` — rescue surgically via `hf_mult_replace_object` / `kling4_0 --mode video-edit` (keep take) |

**Three visual audit pillars (`view_image`).** Inspect fixed primary artifacts only (`brief.md`, `taste-log.md`, `style-bible.md`, `shotlist.json`, `media/references/`, candidate images/`3x2` sheets/`1:1` `--crops` strips, `qa_media.py --json` reports) across: (1) green `qa_media.py` JSON, (2) `continuity_lock` axes—including 4-wall/reverse-shot spatial accuracy (zero 180° room flips or teleporting doors/windows), consistent prop/building scale, absence of *Lighting Bake-In* or off-screen prop bleed, and mid/end-frame prop integrity—plus the exact `test_take_check` failure/pass oracle ([Ad Craft Glossary](../../../docs/ad-craft-glossary.md)), and (3) compliance with every active rule in `taste-log.md`.

**Root-cause repair vs. honest escalation.** Return [Review Result](../../../docs/delegation.md#review-result) (`REVIEW_HANDOFF_INVALID` if required probes, sheets, `R5` `--crops` strips, or `taste-log.md` are missing). Inside `Max auto-retries/asset` and `--round-cap`, repair root causes on unlocked assets using **One Variable Per Re-roll** and [symptom-to-fix prompt diagnostics](../video-direction/references/model-prompting.md#symptom-to-fix-prompt-diagnostics) (tighten reference role binding, align camera geometry, cut beat overload, anchor gaze, sanitize IP phrasing, or switch from pixel upscaling to native `1080p` per [Mastering & Upscaling](../higgsfield-cli/references/mastering-and-upscaling.md)) rather than repeating identical prompts; if caps exhaust, surface any surviving borderline `CONCERN` openly in one line of Dailies.
