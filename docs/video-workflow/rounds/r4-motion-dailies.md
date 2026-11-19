# R4 — Motion Dailies

**Credit spend:** Approved `R4A` and `R4B` `--round-cap`s (typically `~45–90 credits` total across draft clips)
**Owner:** Root Producer + parallel `worker-agent` lanes + fresh `reviewer-agent` Visual Critic
**Outputs:** Pilot clip(s) (`R4A`), full assembled `campaigns/<slug>/media/exports/draft_cut.mp4` (`R4B`), `qc/*-sheet.png` + `qc/*.json`, updated `shotlist.json` and `taste-log.md`

R4 proves motion physics, camera energy, and edited rhythm at low preview cost
(`480p` / `720p` or `seedance_2_5 --draft`) before paying `1080p` master prices
in `R5`. R4 splits cleanly into **4A (Risk-First Pilot)** and **4B (Remaining
Shots & Draft Cut)**.

## Entry Criteria

- `brief.md` is `status: active`; `shotlist.json` passes `make campaign-check`.
- All required start-frame stills (`sNN.still`), `references[]`, and `lookbook[]`
  anchors are `status: "LOCKED"` in `shotlist.json`.
- Director explicitly approved the `R4A` `--round-cap` on Dailies 3.

## R4A — Risk-First Pilot

*Skip `R4A` isolation only when zero shots carry `test_take_check != null` AND
the Director explicitly approved shooting all draft clips together on Dailies 3
(in which case use plain `--round R4 --round-cap <approved_r4_cap>` below).*

1. **Select risky shot(s):** filter `shotlist.json` for `shots[]` with
   `test_take_check != null` (grip, hand/object physics, legible text,
   reflections, comic timing, multi-subject blocking).
2. **Generate preview take(s):** dispatch a fresh `worker-agent` per pilot shot
   writing strictly inside `media/shots/sNN-*`, `prompts/sNN_video_*`, and
   `qc/sNN-*`. Every call runs through `hf_guard.py` using the distinct `R4A`
   bucket (`--round R4A --round-cap <approved_r4a_cap>`) and `draft_params`
   (`480p`/`720p` or `--draft`), anchored to `LOCKED` `sNN.still` + `LOCKED`
   `image_references` and updated for all `TL-NN` rules in `taste-log.md`:
   ```sh
   python3 scripts/hf_guard.py run \
     --campaign campaigns/<slug> \
     --round R4A --round-cap <approved_r4a_cap> \
     --shot s02 --kind video --version 1 [--workflow] \
     --model <model> --prompt-file campaigns/<slug>/prompts/s02_video_v1.txt \
     --out campaigns/<slug>/media/shots/s02-draft-v1.mp4
   ```
3. **Deterministic clip QA + `3×2` sheet (`qa_media.py clip`):**
   ```sh
   make qa-clip \
     FILE=campaigns/<slug>/media/shots/s02-draft-v1.mp4 \
     SHEET=campaigns/<slug>/qc/s02-draft-v1-sheet.png
   ```
   Checks resolution, aspect ratio, FPS, duration, black frames (`>= 0.5 s`),
   `fully_static_clip` (`>= 1.5 s`), and `frozen_tail` (`>= 3.0 s` default via
   `--max-still`, preserving intentional `1.5–2.9 s` closing button holds).
4. **Internal Visual Critic filter (`reviewer-agent`):**
   Fresh read-only `reviewer-agent` (`fork_turns: "none"`, `view_image`) audits
   the `3×2` sheet against `LOCKED` references, `sNN.still`, `continuity_lock`,
   `taste-log.md`, and explicitly verifies `test_take_check.risk` /
   `test_take_check.pass_check`. Auto-retry defects internally within
   `Max auto-retries/asset` and approved `--round-cap`.
5. **Dailies 4A:**
   Auto-open the passing pilot clip via macOS `open` (when enabled) and deliver
   the 4-block [Dailies Packet V1](../interfaces/dailies-packet-v1.md):
   - **1. What to inspect:** `campaigns/<slug>/media/shots/<pilot>.mp4`
   - **2. Filtered internally:** 1-line summary of rejected draft retries
   - **3. Comparative taste questions:** 2–3 plain questions on movement weight,
     camera energy, and realism
   - **4. Cost ticket:** spent so far, remaining `Campaign cap`, exact live
     `R4B` quote for remaining draft shots, and proposed `R4B` `--round-cap`
6. **Capture pilot feedback:** append `### TL-<NN> (R4A — Pilot)` to
   `taste-log.md`. Mark passing pilot take(s) `status: "IN_REVIEW"` → ready for
   draft cut (or surgically re-roll ONLY failed pilot before spending `R4B`).

## R4B — Remaining Shots & Full Draft Cut

1. **Parallel remaining draft renders:** incorporate every motion/camera steer
   from `TL-NN (R4A — Pilot)` into remaining unlocked shots' motion prompts,
   then dispatch parallel `worker-agent` lanes (respecting Codex's 20-thread
   ceiling while reserving reviewer/recovery slots) running `hf_guard.py run
   --round R4B --round-cap <approved_r4b_cap> --version 1` with `draft_params`
   *(or plain `--round R4 --round-cap <approved_r4_cap>` when `R4A` was
   skipped)*.
2. **Per-shot internal QA + Visual Critic:** every clip passes `make qa-clip` +
   fresh `reviewer-agent` (`view_image`) verifying `continuity_lock` across
   adjacent shots and zero `TASTE_REGRESSION`. Auto-retry defects inside
   `Max auto-retries/asset` and `--round-cap`. Root Producer updates
   `selected_take` / `selected_job_id` in `shotlist.json`.
3. **Assemble & master `draft_cut.mp4` (`0 credits`):**
   ```sh
   make assemble CAMPAIGN=<slug> \
     OUT=campaigns/<slug>/media/exports/draft_cut.mp4 \
     [MUSIC=campaigns/<slug>/media/audio/<music.wav>] \
     [VO=campaigns/<slug>/media/audio/<vo.wav>]
   ```
   `scripts/assemble.sh` enforces `shotlist.json`'s `fps_target` lock (in both
   animatic and video assembly modes), audio level law, zero `atempo` on VO,
   and EBU R128 loudness normalization via `loudnorm=I=-14:TP=-1.5:LRA=11`
   targeting `-14 LUFS (±1.0 LU)` and true peak `<= -1.0 dBTP`.
4. **Render-level QA (`qa_media.py render` + Visual Critic):**
   ```sh
   make qa-render \
     FILE=campaigns/<slug>/media/exports/draft_cut.mp4 \
     SHEET=campaigns/<slug>/qc/draft-cut-sheet.png
   ```
   Run a fresh `reviewer-agent` continuity pass on `draft-cut-sheet.png` +
   `qa_media.py render` JSON to confirm zero cross-shot seams or audio defects.
5. **Dailies 4B (Draft Cut + Per-Shot `1080p` Upgrade Prices):**
   Auto-open `campaigns/<slug>/media/exports/draft_cut.mp4` (when enabled) and
   present the 4-block [Dailies Packet V1](../interfaces/dailies-packet-v1.md):
   - **1. What to inspect:** `campaigns/<slug>/media/exports/draft_cut.mp4`
   - **2. Filtered internally:** 1-line summary of rejected takes across `R4B`
   - **3. Comparative taste questions:** 2–3 plain whole-film questions (overall
     pacing/emotion, specific weak shot if any, audio balance)
   - **4. Cost ticket:** spent so far, remaining `Campaign cap`, and a **clear
     per-shot `1080p` upgrade price list for `R5`** (`s01: X cr.`, `s02: Y cr.`,
     `s03: Z cr.`, total `R5` quote, proposed `R5` `--round-cap`), plus draft
     micro-cost if the Director wants to re-roll one specific shot at preview
     price before upgrading.

## Feedback Processing & Exit Criteria

- Append `### TL-<NN> (R4B — Draft Cut)` to `taste-log.md`.
- If the Director wants one shot adjusted before `1080p`: keep approved shots
  untouched, mark ONLY the target shot `status: "ITERATING"`, bump `version` to
  `2`, quote draft micro-cost `<delta_cap>`, re-roll that shot via
  `hf_guard.py run --round <R4A|R4B|R4> --round-cap <round_spent + delta_cap> --version 2`,
  re-assemble `draft_cut.mp4`, and re-present Dailies 4B.
- Once the Director approves `draft_cut.mp4` and explicitly signs off `R5`'s
  `--round-cap` (naming which shots upgrade to `1080p`), advance to
  [R5 — Final Master](r5-mastering.md).
