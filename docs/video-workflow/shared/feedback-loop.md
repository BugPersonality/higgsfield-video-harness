# Feedback Loop

Defines how the Root Producer translates raw, free-form Director reactions at
every Dailies checkpoint into durable **Taste Memory** (`taste-log.md`),
surgical `shotlist.json` state updates (`LOCKED` vs `ITERATING`), and clean
micro-cost re-rolls—without ever leaking technical mechanics to the human.

## Step 1 — Translate Free-Form Reactions Into `taste-log.md`

Directors react like humans, not spec parsers (*"A's lighting feels right, B's
leather looks too plasticky, pull shot 2 wider so we feel the weight, and keep
the cello"*). Immediately translate every reaction into one append-only
`### TL-<NN> (R<k> — <stage>)` entry in `campaigns/<slug>/taste-log.md`
following [Taste Log V1](../interfaces/taste-log-v1.md):

| Director phrase (example) | `taste-log.md` distillation |
| --- | --- |
| *"Lock shot 1 and shot 3; keep the cello."* | **Approved / LOCKED:** `s01.still`, `s03.still`, `audio.music`. |
| *"Love A's cool misty daylight and quiet stillness."* | **More of:** Cool misty morning light, generous negative space, tactile stillness. |
| *"Shot 2 feels cramped—pull back so the whole bench and right hand read clearly."* | **Change / Steer:** `s02.still` (v2): pull camera 20% wider to frame full bench and unobstructed right-hand clasp grip. |
| *"B's shiny leather looks cheap—never glossy leather."* | **Never:** Glossy specular highlights on leather; synthetic plastic-like sheen. |

- **Preserve ambiguity honestly:** if one reaction contradicts a previous
  `TL-NN` entry or a `brief.md` rule, do not guess—append the clarification or
  surface a crisp `A / B` question in one sentence before spending credits.
- **Propagate immediately:** every downstream `specialist-agent` prompt author,
  `worker-agent`, and fresh `reviewer-agent` MUST receive the updated
  `taste-log.md`. Reverting to any active `Never` or ignoring a `Change / Steer`
  entry becomes a blocking `TASTE_REGRESSION`.

## Step 2 — Update `shotlist.json` (`LOCKED` vs `ITERATING`)

Only the Root Producer edits `campaigns/<slug>/shotlist.json`:

1. **Approved assets → `LOCKED`:**
   - Set `status: "LOCKED"` on every entity, still, audio track, or shot the
     Director approved.
   - For `R2` Lookbook winners, upload the chosen image via `hf_guard.py upload`
     and record both `approved_variant` and `approved_upload_id`.
   - For `R3`–`R5` shots, confirm `selected_take` and `selected_job_id` point to
     the approved file and receipt.
2. **Assets needing a steer or blend → `ITERATING`:**
   - Leave all `LOCKED` assets untouched.
   - Set **only** the steered asset(s) to `status: "ITERATING"`.
   - Increment `version` (`1` → `2`, `2` → `3`, ...).
   - Write a new versioned prompt file (`prompts/<id>_v2.txt` for Lookbook
     entities such as `prompts/lb_traveler_v2.txt`, `prompts/s02_still_v2.txt`,
     `prompts/s02_video_v2.txt`) incorporating the new `TL-NN` steers while
     preserving every `continuity_lock` anchor. Never overwrite `_v1.txt` in
     place so iteration history stays diffable in Git.
3. **Run `make campaign-check CAMPAIGN=<slug>`** to confirm all updated prompt
   paths, reference IDs, and budget totals stay valid.

## Step 3 — Protect `LOCKED` Assets

`LOCKED` assets are protected by both policy and code:

- **Policy ([`AGENTS.md`](../../../AGENTS.md)):** no worker, specialist, or
  reviewer may regenerate, overwrite, or silently replace a `LOCKED` asset.
- **Mechanical guard (`scripts/hf_guard.py`):** on both `preflight` and `run`,
  `hf_guard.py` checks `shotlist.json` and immediately refuses with
  `asset_locked` if the target asset has `status: "LOCKED"`. There is **no
  `--force-unlock` CLI bypass**.
- **Explicit unlock protocol:** if the Director later changes their mind about
  a previously `LOCKED` asset (*"actually, let's redo shot 1 to match the warmer
  light we picked for shot 2"*), the Root Producer explicitly confirms the
  unlock and micro-cost, logs `Supersedes TL-<prev>` in `taste-log.md`, edits
  `shotlist.json` to flip that single asset from `LOCKED` → `ITERATING`
  (bumping `version`), and re-rolls strictly that asset.

## Step 4 — Quote Micro-Cost Before Surgical Re-Rolls

Never spend unapproved credits to act on feedback—even a small 10-credit still
re-roll:

1. Run live `higgsfield generate cost` (via `evidence-agent` or read-only CLI)
   for ONLY the `ITERATING` asset(s) and check current round spend via
   `make budget-status CAMPAIGN=<slug>`.
2. Reply with a compact micro-cost ticket:
   - What stays `LOCKED` (untouched, `0 cr.`)
   - What will be re-rolled in plain visual language (no prompt/flag jargon)
   - Exact live micro-cost + proposed delta `<delta_cap>` (producing new
     cumulative round ceiling `<round_spent + delta_cap>`) vs remaining
     `Campaign cap`
3. Wait for the Director's quick **"Go"** before dispatching `worker-agent` via
   `hf_guard.py run` with the **cumulative** round ceiling and incremented
   version (plus `--variant <A|B|C>` for Lookbook re-rolls):
   ```sh
   python3 scripts/hf_guard.py run \
     --campaign campaigns/<slug> \
     --round <R2|R3|R4|R4A|R4B|R5> \
     --round-cap <round_spent + delta_cap> \
     --shot <asset_id> --kind <lookbook|still|video|audio> \
     [--variant <A|B|C>] --version <N> \
     --model <model> --prompt-file campaigns/<slug>/prompts/<prompt_vN>.txt \
     --out campaigns/<slug>/media/<path>
   ```
   Filter internally via `reviewer-agent`, rebuild the round's preview artifact
   (`lookbook.png`, `stills_strip.png` + `animatic.mp4`, or `draft_cut.mp4`),
   and present updated Dailies.

## Step 5 — Hide All Technical Mechanics

Translate everything crossing the Director boundary into human film language:

| Internal Crew mechanic (never show Director) | Director-facing translation |
| --- | --- |
| *"Switched `s02_still_v2.txt` from `85mm` to `35mm`, added `lb_concourse_set` UUID to `--image-references`, re-ran `gpt_image_2_6`."* | *"Pulled shot 2 wider so the full bench and right-hand grip read clearly while keeping the locked concourse light."* |
| *"`qa_media.py clip` returned `frozen_tail: 3.4s` on take 1; re-prompted timestamped `00:03-00:05` action on `cinematic_studio_video_4_0` `--mode omni_reference`."* | *"Filtered 1 take that froze at the end internally; showing the smooth full-length take."* |
| *"Normalized via `loudnorm=I=-14:TP=-1.5:LRA=11` and ducked music `-18 dB` under VO."* | *"Balanced voice clarity over the cello score at broadcast loudness."* |
