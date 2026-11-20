---
name: video-qa
description: "Internal defect and taste-drift filtering plus Dailies grid packaging. Use when running qa_media.py probes or lookbook grids, inspecting Lookbook variants, stills, or contact sheets via view_image, or filtering defects before Director Dailies."
---

# Video QA

**Internal filter before Dailies—taste belongs to the Director.** Follow [Pre-Dailies Visual Critic](../../../docs/delegation.md#pre-dailies-visual-critic): fresh `reviewer-agent` lanes (`fork_turns: "none"`, `view_image`) strip defects, continuity breaks, and `TASTE_REGRESSION`s while leaving `A / B / C` picks and `LOCKED` sign-off solely to the Director.

**Deterministic probes & labeled grids (`scripts/qa_media.py`).** Pass `--json` when capturing reports for `reviewer-agent` handoffs (`make qa-*` runs the same checks for human output):
- `scripts/qa_media.py clip <mp4> --sheet <png> --json` (`make qa-clip`) — probes resolution, FPS, codec, duration, audio, black gaps (`>= 0.5s`), `frozen_tail`, `fully_static_clip`, and writes a `3x2` contact sheet.
- `scripts/qa_media.py voice <wav> --window <sec> --json` (`make qa-voice`) — checks 100ms RMS active speech bounds against the target window.
- `scripts/qa_media.py render <mp4> --sheet <png> --json` (`make qa-render`) — enforces `-14 LUFS (±1.0 LU)` and `<= -1.0 dBTP` on `draft_cut.mp4` / `master.mp4`.
- `make lookbook FILES="..." OUT=<png> LABELS="A,B,C"` — burns crisp visual badges onto tiles for `R2` Lookbooks and `R3` stills strips.
- `scripts/qa_media.py slice <sheet.png> --out-dir <dir> --rows 3 --cols 3 [--trim 4] --json` (`make slice-grid`) — splits `2x2`/`3x3` multi-angle sheets (`nano_banana_2_shots`) into clean standalone PNG tiles before upload.

**Spatial & prop continuity verdict rubric (`view_image`).** Apply this exact mapping on spatial/prop failures:

| Observed Signal (`view_image`) | Verdict | Defect Class | `reopen_owner` & Required Action |
| :--- | :--- | :--- | :--- |
| 180° room flip, wrong reverse wall, teleporting door/window, or front-pose mirror clone | `FAIL` | `CONTINUITY_DEFECT` | `Root Producer` — lock missing Reverse Wall (`R2B`) and re-stage `R3` still with `N/E/S/W` `CAM` facing |
| Prop/building Scale Drift, *Lighting Bake-In*, or off-screen prop bleeding into frame | `FAIL` | `VISUAL_DRIFT_DEFECT` | `Worker(<asset_id>)` — prune off-screen refs, bind Scale Ref / neutral `#808080` prop plate, re-stage `R3` |
| Single handheld prop warps mid-clip while acting, camera, and set stay locked | `FAIL` | `VISUAL_DRIFT_DEFECT` | `Root Producer` — rescue surgically via `hf_mult_replace_object` / `kling4_0 --mode video-edit` (keep take) |

**Three visual audit pillars (`view_image`).** Inspect fixed primary artifacts only (`brief.md`, `taste-log.md`, `style-bible.md`, `shotlist.json`, `media/references/`, candidate images/`3x2` sheets, `qa_media.py --json` reports) across: (1) green `qa_media.py` JSON, (2) `continuity_lock` axes—including 4-wall/reverse-shot spatial accuracy (zero 180° room flips or teleporting doors/windows), consistent prop/building scale, absence of *Lighting Bake-In* or off-screen prop bleed, and mid/end-frame prop integrity—plus the exact `test_take_check` failure/pass oracle ([Ad Craft Glossary](../../../docs/ad-craft-glossary.md)), and (3) compliance with every active rule in `taste-log.md`.

**Root-cause repair vs. honest escalation.** Return [Review Result](../../../docs/delegation.md#review-result) (`REVIEW_HANDOFF_INVALID` if required probes, sheets, or `taste-log.md` are missing). Inside `Max auto-retries/asset` and `--round-cap`, repair root causes on unlocked assets using **One Variable Per Re-roll** and [symptom-to-fix prompt diagnostics](../video-direction/references/model-prompting.md#symptom-to-fix-prompt-diagnostics) (tighten reference role binding, align camera geometry, cut beat overload, anchor gaze, or sanitize IP phrasing) rather than repeating identical prompts; if caps exhaust, surface any surviving borderline `CONCERN` openly in one line of Dailies.
