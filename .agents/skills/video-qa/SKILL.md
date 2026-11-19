---
name: video-qa
description: "Internal defect and taste-drift filtering plus Dailies grid packaging. Use when running qa_media.py probes or lookbook grids, inspecting Lookbook variants, stills, or contact sheets via view_image, or filtering defects before Director Dailies."
---

# Video QA

**Internal filter before Dailies—taste belongs to the Director.** Fresh read-only `reviewer-agent` lanes (`fork_turns: "none"`, `view_image`, see [Delegation](../../../docs/delegation.md#pre-dailies-visual-critic)) strip technical/AI trash, continuity breaks, and `TASTE_REGRESSION`s before assembling each round's Dailies Packet, leaving `A / B / C` picks and `LOCKED` sign-off solely to the Director.

**Deterministic probes & labeled grids (`scripts/qa_media.py`).** Run probes before visual review, then stitch passing options:
- `make qa-clip FILE=<mp4> SHEET=<png>` — probes resolution, FPS, codec, duration, audio, black gaps (`>= 0.5s`), `frozen_tail`, `fully_static_clip`, and renders a `3x2` contact sheet.
- `make qa-voice FILE=<wav> WINDOW=<sec>` — checks 100ms RMS active speech bounds against target window.
- `make qa-render FILE=<mp4> SHEET=<png>` — enforces `-14 LUFS (±1.0 LU)` and `<= -1.0 dBTP` on `draft_cut.mp4` / `master.mp4`.
- `make lookbook FILES="..." OUT=<png> LABELS="A,B,C"` — burns crisp visual badges onto tiles for `R2` Lookbooks and `R3` stills strips.

**Fresh Visual Critic audit (`view_image`).** Pass only fixed primary artifacts (`brief.md`, `taste-log.md`, `style-bible.md`, `shotlist.json`, `media/references/`, candidate images/`3x2` sheets, `qa_media.py` JSON) with zero builder rationale. Verify all three pillars: (1) green `qa_media.py` JSON, (2) `continuity_lock` axes and exact `test_take_check` failure/pass oracle ([Ad Craft Glossary](../../../docs/ad-craft-glossary.md)), and (3) compliance with `Approved / LOCKED`, `More of`, `Change / Steer`, and `Never` rules in `taste-log.md`.

**Root-cause repair vs. honest escalation.** Return [Review Result](../../../docs/delegation.md#review-result) (`REVIEW_HANDOFF_INVALID` if probes, sheets, or `taste-log.md` are missing). Inside `Max auto-retries/asset` and `--round-cap`, fix root causes on unlocked assets (adjust motion beats, tighten reference anchors, sanitize IP phrasing) rather than repeating identical prompts. When retries or caps exhaust, surface any surviving borderline `CONCERN` honestly in one line of Dailies.
