# T02 — Generate Reference-Locked Keyframe Stills (s01–s03)

## Outcome

Generate reference-locked 16:9 keyframe stills for `s01`, `s02`, and `s03` using `gpt_image_2_6` through `scripts/hf_guard.py run` (estimated 30 credits total), probe output dimensions, and write candidate take metadata (`qc/s01-still.json`, `qc/s02-still.json`, `qc/s03-still.json`) for independent read-only Visual Critic (`reviewer-agent`) review before Root Orchestrator acceptance.

## Depends on

- T01
- budget-envelope [effect:spend]

## Sources

- ../intent.md
- ../style-bible.md
- ../storyboard.md
- ../shotlist.json
- ../prompts/s01_still_v1.txt
- ../prompts/s02_still_v1.txt
- ../prompts/s03_still_v1.txt

## Provides

- Candidate keyframe still images under `media/stills/s01-take*.png`, `media/stills/s02-take*.png`, and `media/stills/s03-take*.png`.
- Technical probe and receipt records in `qc/s01-still.json`, `qc/s02-still.json`, and `qc/s03-still.json` ready for fresh read-only `reviewer-agent` visual inspection (`view_image`).

## Boundary

Stay strictly within `phase=draft` and `Max auto-retries/shot: 2` (max 3 total attempts per still). Do not generate video motion clips or audio stems, and do not self-approve visual quality — Root Orchestrator dispatches a fresh read-only `reviewer-agent` (Visual Critic) to inspect candidate stills via `view_image` and record acceptance in `shotlist.json`.

## Mutable owners

- `media/stills/s01-*`
- `media/stills/s02-*`
- `media/stills/s03-*`
- `qc/s01-still.json`
- `qc/s02-still.json`
- `qc/s03-still.json`

## Exclusive locks

- `receipts.jsonl`

## Final validation

- Run `python3 scripts/hf_guard.py run --campaign campaigns/example-product-spot --shot s01 --kind still --phase draft --model gpt_image_2_6 --prompt-file campaigns/example-product-spot/prompts/s01_still_v1.txt --out campaigns/example-product-spot/media/stills/s01-take1.png` (and matching calls for `s02`, `s03` with resolved reference `upload_id` flags).
- Confirm all three still outputs exist with non-zero bytes and 16:9 image dimensions via `ffprobe`.
- Confirm cumulative draft spend stays within Draft cap (`python3 scripts/hf_guard.py status --campaign campaigns/example-product-spot --json`).
- Hand off candidate still paths and `qc/s0*-still.json` to Root Orchestrator for fresh read-only `reviewer-agent` Visual Critic review (`view_image`) against Nord Atelier Continuity Lock invariants.

## Reopen if

Independent Visual Critic rejects any still after 2 bounded auto-retries on leather hue, brass hardware, hand anatomy, or blind-debossed wordmark legibility.
