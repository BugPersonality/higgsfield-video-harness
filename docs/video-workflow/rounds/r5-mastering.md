# R5 — Final Master (`1080p`)

**Credit spend:** Approved `R5` `--round-cap` (exact `1080p` upgrade quote from Dailies 4B + optional retry headroom)
**Owner:** Root Producer + parallel `worker-agent` lanes + fresh `reviewer-agent` Delivery QC
**Outputs:** `campaigns/<slug>/media/exports/master.mp4`, `campaigns/<slug>/media/exports/stems/`, `qc/master-sheet.png` + `qc/master-qa.json`, `brief.md` (`status: done`), final `taste-log.md`, optional graduation to `brands/<brand>/taste.md`

R5 upgrades **only** Director-approved shots to `1080p` using proven prompt and
reference recipes from `R4`, re-verifies every upgraded frame against
`continuity_lock` and `taste-log.md`, exports broadcast-clean `master.mp4` +
separated `stems/`, and graduates durable brand taste learnings.

## Entry Criteria

- `brief.md` is `status: active`; `shotlist.json` passes `make campaign-check`.
- `draft_cut.mp4` was reviewed and approved by the Director on **Dailies 4B**.
- The Director explicitly signed off the `R5` `--round-cap` and which shots
  upgrade to `1080p`.
- `make budget-status CAMPAIGN=<slug>` confirms remaining `Campaign cap` covers
  the `R5` `--round-cap`.

## Step 1 — Targeted `1080p` Upgrades (Approved Shots Only)

1. Identify strictly the shots approved for `1080p` upgrade. Never re-render
   any shot the Director marked `status: "LOCKED"` as-is (`hf_guard.py` enforces
   this mechanically via `asset_locked`).
2. Dispatch parallel `worker-agent` lanes (`fork_turns: "none"`,
   `reasoning_effort: medium`) inside disjoint paths (`media/shots/sNN-*`,
   `qc/sNN-*`) executing `hf_guard.py run --round R5 --round-cap
   <approved_r5_cap>` with `shot.video.final_params` (`"resolution": "1080p"`,
   plus optional extracted Cinema Studio preset UUIDs from
   `docs/cinema-presets.json`), anchored to `LOCKED` `sNN.still` and `LOCKED`
   `image_references`.

## Step 2 — Re-Verify Every `1080p` Take

High-resolution renders can introduce subtle new motion drift, texture shine,
or hand glitches that were absent at `480p`/`720p`. Never assume a `1080p`
upgrade matches the draft take:

1. Run deterministic QA on every upgraded clip:
   ```sh
   make qa-clip \
     FILE=campaigns/<slug>/media/shots/sNN-final-v1.mp4 \
     SHEET=campaigns/<slug>/qc/sNN-final-v1-sheet.png
   ```
2. Dispatch a fresh read-only `reviewer-agent` (`fork_turns: "none"`,
   `reasoning_effort: high`, `view_image`) inspecting each `1080p` `3×2` sheet
   against `LOCKED` stills, approved draft cut continuity, `continuity_lock`,
   `test_take_check`, and `taste-log.md` (catching any `VISUAL_DRIFT_DEFECT`,
   `CONTINUITY_DEFECT`, or `TASTE_REGRESSION`).
3. Auto-retry defective `1080p` takes within `Max auto-retries/asset` and
   approved `R5` `--round-cap` (if budget is tight on a borderline take,
   consult `adjudicator-agent` before spending the final retry).
4. Root Producer records passing `1080p` `selected_take` and `selected_job_id`
   in `shotlist.json`.

## Step 3 — Master Assembly, Stems Export & Final QA

1. Assemble `master.mp4` and separated `stems/` (`0 credits`):
   ```sh
   make assemble CAMPAIGN=<slug> \
     OUT=campaigns/<slug>/media/exports/master.mp4 \
     STEMS=campaigns/<slug>/media/exports/stems \
     [MUSIC=campaigns/<slug>/media/audio/<music.wav>] \
     [VO=campaigns/<slug>/media/audio/<vo.wav>]
   ```
   Produces FPS-locked `master.mp4` mastered via `loudnorm=I=-14:TP=-1.5:LRA=11`
   (`-14 LUFS ± 1.0 LU`, true peak `<= -1.0 dBTP`) alongside clean separated
   stems under `media/exports/stems/` ready for optional DaVinci Resolve
   grading or localization.
2. Run deterministic render validation (`0 credits`):
   ```sh
   make qa-render \
     FILE=campaigns/<slug>/media/exports/master.mp4 \
     SHEET=campaigns/<slug>/qc/master-sheet.png
   ```
3. Run a fresh read-only `reviewer-agent` Final Delivery QC check (`view_image`
   on `master-sheet.png` + `qa_media.py render` JSON + `brief.md` +
   `taste-log.md` + `receipts.jsonl`).
4. **Optional Virality Predictor (`brain_activity`):** only if requested by the
   Director and quoted inside the approved `R5` `--round-cap`, run
   `brain_activity` through `hf_guard.py --round R5 --round-cap <cap>` and
   distill plain-language hook/retention highlights for Final Dailies.

## Step 4 — Final Dailies 5

If `Auto-open dailies: true` on interactive macOS, run
`open campaigns/<slug>/media/exports/master.mp4`, then present the final
4-block [Dailies Packet V1](../interfaces/dailies-packet-v1.md):

1. **What to inspect:** `campaigns/<slug>/media/exports/master.mp4` +
   `campaigns/<slug>/media/exports/stems/` (and plain-language Virality
   Predictor takeaways if run).
2. **Filtered internally:** 1-line summary of any `1080p` retries filtered
   internally and confirmation that loudness, framing, and continuity checks
   passed.
3. **Comparative taste questions:**
   - Does the finished master hit the intended viewer feeling, or is there any
     single shot you want surgically tweaked?
   - **Brand taste graduation:** propose 2–4 durable rules from
     `campaigns/<slug>/taste-log.md` to graduate into
     `brands/<brand>/taste.md` (asking explicit confirmation before editing
     brand-wide taste memory).
4. **Cost ticket (Final Spend Audit):** output summary from
   `make budget-status CAMPAIGN=<slug>` showing exact spent credits by round
   (`R2`–`R5`), total spent vs `Campaign cap`, remaining unused credits, and
   `0 credits` needed unless the Director requests a post-master surgical tweak.

## Step 5 — Closure & Brand Taste Graduation

Upon Director sign-off of Final Dailies 5:

1. Mark all final shots and audio tracks `status: "LOCKED"` in `shotlist.json`.
2. Append `### TL-<NN> (R5 — Master)` to `campaigns/<slug>/taste-log.md`.
3. Flip `campaigns/<slug>/brief.md` to `status: done` and verify:
   ```sh
   make brief-check CAMPAIGN=<slug>
   make campaign-check CAMPAIGN=<slug>
   ```
4. **Graduate brand taste (only confirmed rules):** append the Director-approved
   cross-campaign rules to `brands/<brand>/taste.md` with campaign slug + date
   attribution (following [Taste Log V1](../interfaces/taste-log-v1.md#graduation-to-brand-taste-memory)).
   Leave one-off campaign plot or shot fixes local to `campaigns/<slug>/taste-log.md`.
