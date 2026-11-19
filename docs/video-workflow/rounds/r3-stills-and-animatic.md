# R3 — Keyframe Stills & Animatic

**Credit spend:** Approved `R3` `--round-cap` (typically `~30–50 credits`; **`0 video credits`**)
**Owner:** Root Producer + parallel `worker-agent` lanes + fresh `reviewer-agent` Visual Critic
**Outputs:** `campaigns/<slug>/qc/stills_strip.png`, `campaigns/<slug>/media/exports/animatic.mp4`, `LOCKED` keyframe stills + rough audio in `shotlist.json`, updated `taste-log.md`

R3 locks composition, lighting continuity, product fidelity, voice cadence, and
cut rhythm **before spending a single video credit**. Every shot's start-frame
still is anchored to `LOCKED` reference/Lookbook UUIDs and compiled with VO and
rough music into a playable **0-video-credit Still Animatic**.

## Entry Criteria

- `brief.md` is `status: active`; `shotlist.json` passes `make campaign-check`.
- Every required `lookbook[]` entity is `status: "LOCKED"` with a valid
  `approved_upload_id` (or `R2` was skipped because `lookbook: []`).
- Every supplied real photo in `references[]` has a valid `upload_id` in
  `shotlist.json`. When `R2` was skipped, upload each real photo at the start
  of `R3` with `--round R3`:
  ```sh
  python3 scripts/hf_guard.py upload \
    --campaign campaigns/<slug> \
    --round R3 \
    --file campaigns/<slug>/media/references/<file.jpg> \
    --ref-id <ref_id>
  ```
- Director explicitly approved `R3`'s `--round-cap` on Dailies 2 (or Dailies 1B
  when `R2` was skipped).

## Step 1 — Parallel Keyframe Still Generation (`s01..sN`)

1. Refresh each unlocked shot's still prompt (`prompts/sNN_still_v<k>.txt`)
   strictly against `brief.md`, all cumulative `TL-NN` entries in
   `taste-log.md`, `style-bible.md`, and `shotlist.json`'s `continuity_lock`.
2. Dispatch parallel `worker-agent` lanes (`fork_turns: "none"`,
   `reasoning_effort: medium`)—one disjoint lane per unlocked still
   (`media/stills/sNN-*`, `prompts/sNN_still_*`, `qc/sNN-still-*`).
3. Every still generation executes through `hf_guard.py run` with mandatory
   `--round R3 --round-cap <approved_r3_cap>` and `--version <N>` (matching
   `shotlist.json`), wired to the `LOCKED` reference and Lookbook
   `upload_id` / `approved_upload_id` values:
   ```sh
   python3 scripts/hf_guard.py run \
     --campaign campaigns/<slug> \
     --round R3 --round-cap <approved_r3_cap> \
     --shot s01 --kind still --version 1 \
     --model <model> --prompt-file campaigns/<slug>/prompts/s01_still_v1.txt \
     --out campaigns/<slug>/media/stills/s01-v1.png
   ```
   Never touch any still already marked `status: "LOCKED"` (`hf_guard.py`
   refuses with `asset_locked`).

## Step 2 — Internal Visual Critic Filter (Stills)

Before stitching the strip, dispatch fresh read-only `reviewer-agent` lane(s)
(`fork_turns: "none"`, `reasoning_effort: high`) inspecting all candidate stills
side by side with `LOCKED` references via `view_image`:

- Verify all three `continuity_lock` invariants (`product`,
  `lighting_and_palette`, `space_cast_axis`), anatomy/label legibility, and
  zero `TASTE_REGRESSION` against `taste-log.md`.
- Auto-retry defective stills internally within `Max auto-retries/asset` and
  the approved `R3` `--round-cap`. Keep a 1-line tally for Dailies Block 2.

## Step 3 — Voiceover (`qa_media.py voice`) & Rough Music

Inside the same approved `R3` `--round-cap`:

- **Voiceover (when `audio.voiceover.enabled: true`):**
  1. Generate VO tracks via `hf_guard.py run --round R3 --round-cap <approved_r3_cap> --kind audio --version 1`
     using phonetic pronunciations from `brand.md` / `brief.md`.
  2. Validate timing immediately via 100ms RMS energy detection:
     ```sh
     make qa-voice FILE=campaigns/<slug>/media/audio/<vo.wav> WINDOW=<window_s>
     ```
  3. **Zero `atempo` rule:** if active speech exceeds `WINDOW`, **never** speed
     up the audio with FFmpeg `atempo`. Tighten the spoken copy in `script.md`
     within `ad-script`'s read-aloud budget and regenerate within retry bounds.
- **Rough music bed (when `audio.music.enabled: true`):**
  Generate the music track via `hf_guard.py run --round R3 --round-cap
  <approved_r3_cap> --kind audio --version 1` matching `taste-log.md` mood and
  `brief.md` taboos.

## Step 4 — Build Storyboard Strip & 0-Credit Still Animatic

Run both local commands (`0 credits`):

1. **Storyboard stills strip (`qc/stills_strip.png`):**
   ```sh
   make lookbook \
     FILES="campaigns/<slug>/media/stills/s01-v1.png campaigns/<slug>/media/stills/s02-v1.png ..." \
     LABELS="S01,S02,..." \
     OUT=campaigns/<slug>/qc/stills_strip.png
   ```
2. **Playable Still Animatic (`media/exports/animatic.mp4`):**
   ```sh
   make animatic CAMPAIGN=<slug> \
     [MUSIC=campaigns/<slug>/media/audio/<music.wav>] \
     [VO=campaigns/<slug>/media/audio/<vo.wav>]
   ```
   `scripts/assemble.sh --animatic` holds each approved still for its exact
   `shotlist.json` `duration_s` at `fps_target`, layered with VO and rough music
   so the Director can run both the **mute test** and full-sound pacing check
   before paying for motion generation.

Root Producer records candidate still/audio paths in `shotlist.json` and flips
them to `status: "IN_REVIEW"`.

## Step 5 — Dailies 3

If `Auto-open dailies: true` on interactive macOS, open both
`campaigns/<slug>/qc/stills_strip.png` and
`campaigns/<slug>/media/exports/animatic.mp4`, then present the 4-block
[Dailies Packet V1](../interfaces/dailies-packet-v1.md):

1. **What to inspect:** `qc/stills_strip.png` (side-by-side continuity check) +
   `media/exports/animatic.mp4` (watch muted once, then with sound).
2. **Filtered internally:** 1-line summary of rejected stills or over-window VO
   takes filtered before Dailies.
3. **Comparative taste questions:** 2–3 plain questions on framing, lighting
   match across cuts, voice warmth/pacing, and which beats feel locked vs need
   adjustment.
4. **Cost ticket:** spent so far, remaining `Campaign cap`, exact live `R4A`
   Risk-First Pilot quote (or full `R4` draft quote if no `test_take_check`
   shots exist), proposed `R4` `--round-cap`, plus exact per-still micro-cost
   for surgical re-rolls before moving to motion.

## Step 6 — Feedback Processing, `LOCK` Winners & Surgical Re-Rolls

Process Director reactions under [Feedback Loop](../shared/feedback-loop.md):

1. Append `### TL-<NN> (R3 — Stills & Animatic)` to `taste-log.md`.
2. **Lock winners immediately:** mark every approved still (`sNN.still`),
   approved VO track, and approved music bed `status: "LOCKED"` in
   `shotlist.json` (and upload any `LOCKED` still needed as a remote start frame
   via `hf_guard.py upload --round R3` if required by the live video workflow).
3. **Iterate ONLY rejected stills:** leave `LOCKED` stills untouched, mark
   rejected shot(s) `status: "ITERATING"`, increment `version` to `2`, author
   `prompts/sNN_still_v2.txt`, confirm exact micro-cost `<delta_cap>`,
   regenerate ONLY those still(s) via `hf_guard.py run --round R3 --round-cap
   <round_spent + delta_cap> --version 2`, re-verify via fresh `reviewer-agent`,
   rebuild `stills_strip.png` + `animatic.mp4`, and present updated Dailies 3.

## Exit Criteria & Next Round

Once all required stills (and rough audio when enabled) are `status: "LOCKED"`,
`make campaign-check CAMPAIGN=<slug>` passes, and the Director approves `R4A`
(or `R4`) `--round-cap`, advance to
[R4 — Motion Dailies](r4-motion-dailies.md).
