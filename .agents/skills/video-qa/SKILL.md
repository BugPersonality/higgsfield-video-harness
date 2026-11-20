---
name: video-qa
description: "Internal technical/continuity QA and Dailies grid packaging. Use when running qa_media.py probes, 1:1 crop strips, batch audits, or lookbook grids, or filtering defects and taste regressions before Director Dailies."
---

# Video QA

Canonical owner of deterministic media probes (`scripts/qa_media.py`), Dailies
grid packaging, mandatory `1:1` native-pixel crop verification, and the binary
pre-Dailies Visual Critic rubric. Follow
[Pre-Dailies Visual Critic](../../../docs/delegation.md#pre-dailies-visual-critic):
fresh `reviewer-agent` lanes filter defects, continuity breaks, and
`TASTE_REGRESSION`s while leaving `A / B / C` picks and `LOCKED` sign-off solely
to the Director.

## Deterministic Probes & Grid Builders (`scripts/qa_media.py`)

Always pass `--json` when capturing reports for `reviewer-agent` handoffs
(`make qa-*` runs the same checks for human output):

- `scripts/qa_media.py clip <mp4> --sheet <png> [--crops <png>] [--crop-focus thirds|center|left|right] --json` (`make qa-clip`) — probes resolution, FPS, codec, duration, `video_bitrate_kbps`, `hf_edge_energy` (Laplacian sharpness proxy), audio, black gaps (`>= 0.5s`), `frozen_tail`, `fully_static_clip`, warns on `non_standard_dimensions` (`1918×1080`) and `low_video_bitrate`, writes a `3x2` contact sheet, and—when `--crops` is passed—writes an **unscaled `1:1` native-pixel 3-frame crop strip** (default `thirds` sweeps left/center/right).
- `scripts/qa_media.py batch <clip1> <clip2> ... [--strict] --json` (`make qa-batch`) — audits cross-shot resolution, FPS, non-multiple-of-4 dimensions, low `1080p` bitrate, and `hf_sharpness_outlier` warnings (`> 1.5×` clean median) across an `R5` cut before `make assemble`.
- `scripts/qa_media.py voice <wav> --window <sec> --json` (`make qa-voice`) — checks 100ms RMS active speech bounds against the target window.
- `scripts/qa_media.py render <mp4> --sheet <png> [--crops <png>] --json` (`make qa-render`) — enforces `-14 LUFS (±1.0 LU)` and `<= -1.0 dBTP` on `draft_cut.mp4` / `master.mp4`.
- `make lookbook FILES="..." OUT=<png> LABELS="A,B,C"` — burns visual badges onto tiles for `R2` Lookbooks and `R3` stills strips.
- `scripts/qa_media.py slice <sheet.png> --out-dir <dir> --rows 3 --cols 3 [--trim 4] --json` (`make slice-grid`) — splits `2x2`/`3x3` multi-angle sheets (`nano_banana_2_shots`) into standalone PNG tiles before upload.

## Mandatory `1:1` Inspection & Binary QC Rubric

Shrunk `480px` `3x2` sheets hide halos, face melt, distorted teeth, and blotches.
Every `R5` or upscaled handoff MUST include `--crops <png>` (targeting
`--crop-focus center|left|right` onto hero faces for character close-ups) and
`batch --strict --json` before assembly, inspected via vision tool against this
exact verdict mapping:

| Observed Signal (JSON or `1:1` `--crops`) | Verdict | Defect Class | `reopen_owner` & Required Action |
| :--- | :--- | :--- | :--- |
| Missing `qa_media.py` JSON, `3x2` sheet, `R5` `--crops` strip, `R5` `batch --strict`, or `taste-log.md` | `REVIEW_HANDOFF_INVALID` | — | `Worker(<asset_id>)` — produce missing proof; never pass blindly |
| White/dark edge halo, ringing, muddy/plastic face, or eyelid/cheek color blotch on `--crops` | `FAIL` | `MEDIA_TECH_DEFECT` | `Root Producer` — stop upscaling; switch shot to native `1080p` path ([Mastering & Upscaling](../higgsfield-cli/references/mastering-and-upscaling.md)) |
| `non_standard_dimensions` (`1918×1080`), `resolution_mismatch`, or `fps_mismatch` in `batch` | `FAIL` | `MEDIA_TECH_DEFECT` | `Root Producer` — re-render natively at exact `1920×1080` & `fps_target` |
| `hf_sharpness_outlier` (`> 1.5×` clean median) + visible crunch/ringing on `--crops` | `FAIL` | `MEDIA_TECH_DEFECT` | `Root Producer` — replace upscaled outlier with native `1080p` take |
| `hf_sharpness_outlier` (`> 1.5×`) between clean native shots (zero halos/melt on `--crops`) | `CONCERNS` | `CONCERN` | `Root Producer` — confirm genuine scene detail; match via shared 35mm grain if needed |
| `low_video_bitrate` (`< 1800 kbps` at `1080p`) with visible compression softness/banding | `FAIL` | `MEDIA_TECH_DEFECT` | `Worker(<asset_id>)` — re-run with `--bitrate_mode high` (or alternate `1080p` engine) |
| 180° room flip, wrong reverse wall, teleporting door/window, or front-pose mirror clone | `FAIL` | `CONTINUITY_DEFECT` | `Root Producer` — lock missing Reverse Wall (`R2B`) and re-stage `R3` still with `N/E/S/W` `CAM` facing ([Locations & Props](../video-consistency/references/locations-and-props.md#6-spatial--prop-failure-diagnostics)) |
| Prop/building Scale Drift, *Lighting Bake-In*, or off-screen prop bleeding into frame | `FAIL` | `VISUAL_DRIFT_DEFECT` | `Worker(<asset_id>)` — prune off-screen refs, bind Scale Ref / neutral `#808080` prop plate, re-stage `R3` |
| Single handheld prop warps mid-clip while acting, camera, and set stay locked | `FAIL` | `VISUAL_DRIFT_DEFECT` | `Root Producer` — rescue surgically via `hf_mult_replace_object` / `kling4_0 --mode video-edit` (keep take) |
| Camera drifts on static hold, walls bend like rubber, pan edges strobe, or motion freezes stiff | `FAIL` | `VISUAL_DRIFT_DEFECT` | `Worker(<asset_id>)` — apply One Variable Per Re-roll fix ([Camera Control](../video-direction/references/camera-control.md#6-camera-failure-diagnostics)) |
| Face morphs on head turn, alien/warped teeth on smile, lens stare, or wide-shot face collapse | `FAIL` | `CONTINUITY_DEFECT` | `Worker(<asset_id>)` — bind `3/4`/profile + Expression Calibration (`R2B`), bake `40–60%` expression in `2k`/`4k` `R3`, strip face prose from video ([Characters & Expressions](../video-consistency/references/characters-and-expressions.md#6-face--expression-failure-diagnostics)) |
| Mid-clip face likeness softens on an otherwise golden acting take | `FAIL` | `VISUAL_DRIFT_DEFECT` | `Root Producer` — rescue surgically via `kling4_0 --mode video-edit` (bound to canonical `R2A` portrait) or Web Face Swap (keep performance) |

## Three Audit Pillars & Root-Cause Escalation

- **Three visual audit pillars:** Inspect fixed primary artifacts only (`brief.md`,
  `taste-log.md`, `style-bible.md`, `shotlist.json`, `media/references/`,
  candidate images/`3x2` sheets/`1:1` `--crops` strips, `qa_media.py --json`
  reports) across: (1) green `qa_media.py` JSON, (2) `continuity_lock` axes
  (facial bone structure, teeth/eyelid/gaze/expression continuity, 4-wall/reverse
  geography, prop/building scale, absence of *Lighting Bake-In* or off-screen
  bleed, mid/end-frame prop integrity) plus the exact `test_take_check` oracle
  ([Ad Craft Glossary](../../../docs/ad-craft-glossary.md)), and (3) every active
  rule in `taste-log.md`.
- **Root-cause repair vs. honest escalation:** Return
  [Review Result](../../../docs/delegation.md#review-result). Inside
  `Max auto-retries/asset` and `--round-cap`, repair root causes on unlocked
  assets using **One Variable Per Re-roll** and the linked domain diagnostics
  ([Prompting](../video-direction/references/model-prompting.md#symptom-to-fix-prompt-diagnostics),
  [Camera](../video-direction/references/camera-control.md#6-camera-failure-diagnostics),
  [Spatial](../video-consistency/references/locations-and-props.md#6-spatial--prop-failure-diagnostics),
  [Faces](../video-consistency/references/characters-and-expressions.md#6-face--expression-failure-diagnostics),
  [Mastering](../higgsfield-cli/references/mastering-and-upscaling.md#3-step-by-step-r5-mastering--verification-runbook))
  rather than repeating identical prompts. If caps exhaust, surface any
  surviving borderline `CONCERN` openly in one line of Dailies.

*Done when:* every required `qa_media.py` JSON, `3x2` sheet, `R5` `1:1` `--crops`
strip, and `batch --strict` audit is inspected via vision tool, technical trash
and `TASTE_REGRESSION`s are filtered out, and clean Dailies artifacts are ready
for the Director.
