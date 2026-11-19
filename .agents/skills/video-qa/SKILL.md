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

**Three visual audit pillars (`view_image`).** Inspect fixed primary artifacts only (`brief.md`, `taste-log.md`, `style-bible.md`, `shotlist.json`, `media/references/`, candidate images/`3x2` sheets, `qa_media.py --json` reports) across: (1) green `qa_media.py` JSON, (2) `continuity_lock` axes plus the exact `test_take_check` failure/pass oracle ([Ad Craft Glossary](../../../docs/ad-craft-glossary.md)), and (3) compliance with every active rule in `taste-log.md`.

**Root-cause repair vs. honest escalation.** Return [Review Result](../../../docs/delegation.md#review-result) (`REVIEW_HANDOFF_INVALID` if required probes, sheets, or `taste-log.md` are missing). Inside `Max auto-retries/asset` and `--round-cap`, repair root causes on unlocked assets (tighten reference anchors, adjust motion beats, sanitize IP phrasing) rather than repeating identical prompts; if caps exhaust, surface any surviving borderline `CONCERN` openly in one line of Dailies.
