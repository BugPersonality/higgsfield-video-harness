# T03 — Risk-First Pilot 480p Draft Clip (s02)

## Outcome

Generate the 5-second 480p Risk-First Pilot workflow clip for `s02` (the sole `test_take_check` shot in `storyboard.md` and `shotlist.json`) anchored to the accepted `s02` keyframe still via `scripts/hf_guard.py run --workflow` (`cinematic_studio_video_4_0`, `--mode omni_reference`, estimated 15 credits), run deterministic `qa_media.py clip` checks, and produce the `3x2` contact sheet (`qc/s02-draft-sheet.png`) for independent read-only Visual Critic (`reviewer-agent`) evaluation before batching Wave 4.

## Depends on

- T02 [acceptance]
- budget-envelope [effect:spend]

## Sources

- ../intent.md
- ../script.md
- ../storyboard.md
- ../treatment.md
- ../style-bible.md
- ../shotlist.json
- ../prompts/s02_video_v1.txt

## Provides

- Candidate 480p Risk-First Pilot video clip under `media/shots/s02-draft-take*.mp4`.
- Deterministic QA JSON (`qc/s02-draft.json`) and `3x2` contact sheet (`qc/s02-draft-sheet.png`, gitignored) ready for fresh read-only `reviewer-agent` Visual Critic evaluation of the `s02` `test_take_check`.

## Boundary

Generate only `s02` in `phase=draft` at `480p`. Do not start `s01`/`s03` motion generation or `1080p` final renders, and do not self-approve visual QA — Root Orchestrator dispatches a fresh read-only `reviewer-agent` (Visual Critic) to inspect `qc/s02-draft-sheet.png` via `view_image` and decide `T03 [acceptance]`.

## Mutable owners

- `media/shots/s02-draft-*`
- `qc/s02-draft.json`
- `qc/s02-draft-sheet.png`

## Exclusive locks

- `receipts.jsonl`

## Final validation

- Run `python3 scripts/hf_guard.py run --campaign campaigns/example-product-spot --shot s02 --kind video --phase draft --workflow --model cinematic_studio_video_4_0 --prompt-file campaigns/example-product-spot/prompts/s02_video_v1.txt --out campaigns/example-product-spot/media/shots/s02-draft-take1.mp4 -- --mode omni_reference --resolution 480p --duration 5 --aspect_ratio 16:9`.
- Run `python3 scripts/qa_media.py clip campaigns/example-product-spot/media/shots/s02-draft-take1.mp4 --sheet campaigns/example-product-spot/qc/s02-draft-sheet.png --json` and write stdout to `qc/s02-draft.json` confirming exit code `0`.
- Hand off `qc/s02-draft.json` and `qc/s02-draft-sheet.png` to Root Orchestrator for fresh read-only `reviewer-agent` Visual Critic inspection against the `s02` `test_take_check` (five-finger handle/brass-clasp grip, attached brushed-brass hardware, downward matte leather crease physics, native diegetic audio only).

## Reopen if

Independent Visual Critic rejects `s02` on its `test_take_check` or `qa_media.py clip` fails across 2 bounded auto-retries.
