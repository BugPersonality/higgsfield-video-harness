# R2 — Casting & World Lookbook

**Credit spend:** Approved `R2` `--round-cap` (typically `~20–45 credits`; `0 credits` when skipped)
**Owner:** Root Producer + parallel `worker-agent` lanes + fresh `reviewer-agent` QC filter
**Outputs:** `campaigns/<slug>/qc/lookbook.png`, uploaded & `LOCKED` `lookbook[]` UUIDs in `shotlist.json`, updated `taste-log.md`

R2 establishes the exact look of every **invented** object, character, prop, or
environment *before* drawing storyboard keyframes or spending a single video
credit. Instead of guessing one interpretation, the Crew renders **2–3
genuinely contrasting variants (`A / B / C`)** per entity so the Director picks
or blends by eye.

## Automatic Skip Rule

**Skip `R2` automatically** when every hero product, character, and environment
is already supplied as real reference photos under
`campaigns/<slug>/media/references/` (`lookbook: []` in `shotlist.json`). Note
the skip on Dailies 1B and move straight to
[R3 — Keyframe Stills & Animatic](r3-stills-and-animatic.md).

## Entry Criteria

- `brief.md` is `status: active` (`make brief-check` passes).
- `shotlist.json` passes `make campaign-check` with one or more unlocked
  `lookbook[]` entries (`status: "DRAFT"` or `"ITERATING"`).
- The Director explicitly approved the `R2` `--round-cap` on Dailies 1B (or
  approved a micro re-roll `--round-cap` during R2 iteration).
- Workspace and balance verified (`higgsfield workspace list`,
  `higgsfield account status`).

## Step 1 — Upload Prerequisite Real Photos (If Referenced)

If any Lookbook entity builds on a supplied local photo in `media/references/`
whose `upload_id` is still `null`, upload it once through `hf_guard.py`:

```sh
python3 scripts/hf_guard.py upload \
  --campaign campaigns/<slug> \
  --round R2 \
  --file campaigns/<slug>/media/references/<file.jpg> \
  --ref-id <ref_id>
```

Root Producer records the returned `upload_id` in `shotlist.json`.

## Step 2 — Parallel Contrasting Variant Generation (`A / B / C`)

For each unlocked Lookbook entity (`status != "LOCKED"`, where entity IDs
already start with `lb_`, e.g., `lb_traveler`):

1. Craft `variants_requested` (from `brief.md` `Lookbook variants`, typically
   `2` or `3`) **genuinely contrasting** visual interpretations anchored to
   `brief.md`, `taste-log.md`, and `style-bible.md` (for example, `A` = softer
   organic patina, `B` = crisp architectural silhouette, `C` = moodier tactile
   contrast—never three near-identical seeds).
2. Dispatch one fresh `worker-agent` (`fork_turns: "none"`,
   `reasoning_effort: medium`) per unlocked entity inside disjoint paths
   (`media/lookbook/<id>-*`, `prompts/<id>_*`, `qc/<id>-*`).
3. Every paid call MUST execute via `hf_guard.py` with mandatory
   `--round R2 --round-cap <approved_cap>`, `--kind lookbook`, `--variant`
   (`A`, `B`, `C`, bounded by `Lookbook variants` so each option keeps its own
   `1 + Max auto-retries/asset` budget), and `--version 1` matching
   `shotlist.json`:
   ```sh
   python3 scripts/hf_guard.py run \
     --campaign campaigns/<slug> \
     --round R2 --round-cap <approved_cap> \
     --shot <id> --kind lookbook --variant A --version 1 \
     --model <model> --prompt-file campaigns/<slug>/prompts/<id>_v1_A.txt \
     --out campaigns/<slug>/media/lookbook/<id>-v1-A.png

   python3 scripts/hf_guard.py run \
     --campaign campaigns/<slug> \
     --round R2 --round-cap <approved_cap> \
     --shot <id> --kind lookbook --variant B --version 1 \
     --model <model> --prompt-file campaigns/<slug>/prompts/<id>_v1_B.txt \
     --out campaigns/<slug>/media/lookbook/<id>-v1-B.png

   python3 scripts/hf_guard.py run \
     --campaign campaigns/<slug> \
     --round R2 --round-cap <approved_cap> \
     --shot <id> --kind lookbook --variant C --version 1 \
     --model <model> --prompt-file campaigns/<slug>/prompts/<id>_v1_C.txt \
     --out campaigns/<slug>/media/lookbook/<id>-v1-C.png
   ```
   *(Never invoke `hf_guard.py` on an already-`LOCKED` Lookbook entity; both
   `preflight` and `run` refuse with `asset_locked` with no `--force-unlock`
   bypass.)*

## Step 3 — Internal Defect & Taste-Drift Filtering

Before building the Dailies grid, dispatch a fresh read-only `reviewer-agent`
(`fork_turns: "none"`, `reasoning_effort: high`) inspecting every generated
variant via `view_image` alongside `brief.md`, `taste-log.md`, `style-bible.md`,
and any real reference photos:

- Reject broken anatomy, melted geometry, garbled text, `POLICY_BLOCK`, or
  `TASTE_REGRESSION` against `taste-log.md`.
- Auto-retry defective variants internally inside `Max auto-retries/asset` and
  approved `--round-cap`, logging what was filtered for Block 2 of Dailies.
- Remember: `reviewer-agent` **filters defects only**—never drops a clean
  contrasting option or picks a winner on the Director's behalf.

## Step 4 — Build Lookbook Grid (`make lookbook`)

Stitch clean `A / B / C` variants into one crisp labeled PNG grid via
`scripts/qa_media.py lookbook`:

```sh
make lookbook \
  FILES="campaigns/<slug>/media/lookbook/<id>-v1-A.png campaigns/<slug>/media/lookbook/<id>-v1-B.png campaigns/<slug>/media/lookbook/<id>-v1-C.png" \
  LABELS="A,B,C" \
  OUT=campaigns/<slug>/qc/lookbook.png
```

Root Producer flips presented Lookbook entries to `status: "IN_REVIEW"` in
`shotlist.json`.

## Step 5 — Dailies 2

If `Auto-open dailies: true` on interactive macOS, run
`open campaigns/<slug>/qc/lookbook.png`, then present the 4-block
[Dailies Packet V1](../interfaces/dailies-packet-v1.md):

1. **What to inspect:** `campaigns/<slug>/qc/lookbook.png` (`A / B / C`).
2. **Filtered internally:** 1-line summary of rejected AI defects filtered
   before building the grid.
3. **Comparative taste questions:** 2–3 jargon-free questions asking which
   variant wins (or which traits to blend) and what to ban permanently.
4. **Cost ticket:** spent so far, remaining `Campaign cap`, exact live `R3`
   quote (keyframe stills + rough audio + 0-credit animatic), proposed `R3`
   `--round-cap`, plus per-variant micro-cost if the Director wants a blend or
   re-roll before locking.

## Step 6 — Feedback Processing, Upload & `LOCK`

Process the Director's reaction under
[Feedback Loop](../shared/feedback-loop.md):

1. Append `### TL-<NN> (R2 — Lookbook)` to `campaigns/<slug>/taste-log.md`
   recording `Approved / LOCKED`, `More of`, `Change / Steer`, and `Never`.
2. **For each approved entity:**
   - Upload the winning PNG via `hf_guard.py upload`:
     ```sh
     python3 scripts/hf_guard.py upload \
       --campaign campaigns/<slug> \
       --round R2 \
       --file campaigns/<slug>/media/lookbook/<winning-file>.png \
       --ref-id <id>
     ```
   - Update `shotlist.json` (`approved_variant`, `approved_upload_id`,
     `status: "LOCKED"`). That entity is now immutable.
3. **For any entity needing a blend or re-roll:**
   - Keep already-`LOCKED` entities untouched.
   - Mark only the rejected entity `status: "ITERATING"`, bump `version` to `2`
     in `shotlist.json`, write versioned prompt(s) (`prompts/<id>_v2_A.txt`,
     ...), quote exact micro-cost `<delta_cap>`, and confirm the new cumulative
     ceiling (`<round_spent + delta_cap>`):
     ```sh
     python3 scripts/hf_guard.py run \
       --campaign campaigns/<slug> \
       --round R2 --round-cap <round_spent + delta_cap> \
       --shot <id> --kind lookbook --variant A --version 2 \
       --model <model> --prompt-file campaigns/<slug>/prompts/<id>_v2_A.txt \
       --out campaigns/<slug>/media/lookbook/<id>-v2-A.png
     ```
   - Re-run internal QC, rebuild `qc/lookbook.png`, and re-present Lookbook
     Dailies for ONLY that entity.

## Exit Criteria & Next Round

Once every `lookbook[]` entry is `status: "LOCKED"` with a populated
`approved_upload_id`, `make campaign-check CAMPAIGN=<slug>` passes, and the
Director approves `R3`'s `--round-cap`, advance to
[R3 — Keyframe Stills & Animatic](r3-stills-and-animatic.md).
