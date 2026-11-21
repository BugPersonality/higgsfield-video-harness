# Studio Evolution Log (Self-Improvement Memory)

Meta-memory (SIM) tracking *why* harness rules, validators, and skills were added or changed,
what failure trace triggered them, and when to retire or revisit them as models improve.

### EV-01 (2026-11-20) — Interactive R0–R5 Dailies Loop & Mechanical Lock Guards
- **Trigger trace:** One-shot autonomous generation hid taste misalignment until after credits were burned (`git:509f49e`, `git:92eb285`).
- **Change:** Pivoted to interactive `R0`–`R5` Director ↔ Crew loop with `taste-log.md`, `LOCKED` immutability enforced in `scripts/hf_guard.py`, dual budget walls (`Campaign cap` + `--round-cap`), and minimalist `AGENTS.md` kernel.
- **Expected effect:** Zero unapproved credit spend or accidental overwrites of Director-locked assets.
- **Observed effect:** Verified mechanically in `tests/test_hf_guard.py` and `campaigns/example-product-spot/`.
- **Retire / Revisit when:** Never retire budget/lock walls; simplify round ceremony only for single-shot non-campaign tasks.

### EV-02 (2026-11-20) — Native 1080p Upscale Gate, 1:1 Crop QA & Batch Cut Audit
- **Trigger trace:** Shrunk `480px` `3x2` contact sheets hid bright edge halos, muddy faces, `1918x1080` rounding, and `1.4x–2.0x` Laplacian HF spikes on `480p -> 1080p` generative upscales (`git:77c9fd7`).
- **Change:** Added `--crops` unscaled `1:1` inspection and `batch --strict` to `scripts/qa_media.py`, `480p` pixel-upscale warning to `scripts/check-campaign.py`, and native `1080p` Upscale Gate to `higgsfield-cli`.
- **Expected effect:** Zero upscaler shimmer or resolution/FPS mismatch reaching Dailies 5.
- **Observed effect:** Covered by automated regression tests in `tests/test_qa_and_assemble.py` and `tests/test_check_campaign.py`.
- **Retire / Revisit when:** Generative video upscalers pass blind `1:1` `--crops` and `hf_sharpness_outlier <= 1.3x` checks across `>= 2` production campaigns.

### EV-03 (2026-11-20) — Typed R2B Asset Bible, Spatial Lock & Expression Calibration
- **Trigger trace:** Disconnected reverse-angle generation caused 180° room flips, wardrobe drift, and mid-clip facial morphing on multi-angle spots (`git:cc0f72e`, `git:2b29959`, `git:7d7a976`).
- **Change:** Added typed `R2B` Asset Bible (Reverse Walls, neutral `#808080` prop plates, Expression Calibration), `qa_media.py slice`, and ref-budget/CEL guards in `scripts/check-campaign.py`.
- **Expected effect:** Eliminate 180° room flips, scale drift, and mid-clip face collapse on multi-angle spots.
- **Observed effect:** Validated via `tests/test_check_campaign.py` and `tests/test_qa_and_assemble.py`.
- **Retire / Revisit when:** Native 3D-consistent video generators hold 4-wall geography and reverse angles without explicit Reverse Wall plates across `>= 2` multi-angle campaigns.

### EV-04 (2026-11-21) — 5-Layer Self-Improving Memory, Raw Trace Logging & R6 Retro Loop
- **Trigger trace:** Long multi-round campaigns exposed append-only `taste-log.md` contradiction rot (superseded `LOCKED` entries competing with active ones), campaign-plot leakage into brand taste files, and zero trace visibility for `0 cr.` Web Unlimited runs and Visual Critic verdicts (`git:30d130e`).
- **Change:** Separated `studio/{director,engine-memory,evolution-log}.md` from pure brand taste; added `Supersedes:` + deterministic `scripts/memory_compile.py` (`taste-active.md`), `hf_guard.py log-web`, `qa_media.py log-review`, `scripts/check-memory.py` (`make memory-lint`), `scripts/retro_harvest.py`, `scripts/memory_search.py`, and user-invoked `.agents/skills/studio-retro/`.
- **Expected effect:** Zero contradictory `LOCKED` rules injected into subagents, full visibility into Web Unlimited + Visual Critic defects, and gated cross-campaign learning.
- **Observed effect:** Verified via `tests/test_memory_and_retro.py`, `tests/test_repo_checks.py`, and `make memory-lint`.
- **Retire / Revisit when:** Revisit `taste-active.md` line caps (`80` lines) or add incremental SQLite index caching once a studio archive exceeds `20` campaigns.

### EV-05 (2026-11-21) — Narrative Architecture Skill, Narrative Lock & Blind Viewer Read QC
- **Trigger trace:** Multi-round production campaigns exposed meaning leaks surviving green pixel/continuity QA: cold viewers misreading product category (mistaking a visual metaphor for hardware), zero-delta filler shots cut only after `R4B` motion spend, ambiguous hero-object silhouettes failing `0.1s` recognition on mute, and synthetic prop groupings lacking human truth (`git:46c57f2`).
- **Change:** Added canonical `.agents/skills/video-narrative/` (`Narrative Lock`, `BUT / THEREFORE` causal spine, per-shot `Narrative job` + Deletion Test, `0.1s` instant-read semiotics, `2 + 2` subtext, and runtime-scaled commercial/non-commercial structures), wired `R3`/`R4B` Blind Viewer Read + `NARRATIVE_DEFECT` into `video-qa`, `qa_media.py`, `check-memory.py`, `delegation.md`, and `reviewer-agent`, and added backwards-compatible `narrative_lock` / `narrative_job` checks to `check-campaign.py` plus `State shift` / `Primary misread risk` prompts in `campaign_init.py`.
- **Expected effect:** Catch category misreads, ambiguous `0.1s` objects, and zero-delta filler beats at `0 cr.` (`R1B`/`R3`) before motion spend while keeping creative taste strictly with the Director.
- **Observed effect:** Verified mechanically via `make check`, `tests/test_repo_checks.py`, `tests/test_check_campaign.py`, and `tests/test_memory_and_retro.py`.
- **Retire / Revisit when:** Revisit after `>= 3` multi-shot campaigns; graduate `narrative_lock` or `narrative_job` from soft-optional to warning-level in `check-campaign.py` only if agents routinely omit them.
