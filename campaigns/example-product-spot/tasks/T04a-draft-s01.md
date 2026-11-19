# T04a — Generate 480p Draft Clip (s01)

## Outcome

Running in parallel Wave 4 alongside `T04b` following `s02` Risk-First Pilot acceptance, generate the 5-second 480p draft workflow clip for `s01` (brass clasp closure macro) via `scripts/hf_guard.py run --workflow` (`cinematic_studio_video_4_0`, `--mode omni_reference`, estimated 15 credits), validate deterministically with `qa_media.py clip`, and emit `qc/s01-draft.json` plus `qc/s01-draft-sheet.png` for fresh read-only Visual Critic (`reviewer-agent`) review.

## Depends on

- T02
- T03 [acceptance]
- budget-envelope [effect:spend]

## Sources

- ../intent.md
- ../script.md
- ../storyboard.md
- ../treatment.md
- ../style-bible.md
- ../shotlist.json
- ../prompts/s01_video_v1.txt

## Provides

- Candidate 480p draft video clip under `media/shots/s01-draft-take*.mp4`.
- Deterministic QA JSON (`qc/s01-draft.json`) and `3x2` contact sheet (`qc/s01-draft-sheet.png`) for independent read-only `reviewer-agent` Visual Critic seam audit against `s02`.

## Boundary

Write strictly to `s01` draft paths in `phase=draft` at `480p` respecting `Max auto-retries/shot: 2`. Do not touch `s02` or `s03` files, and do not self-approve visual quality — Root Orchestrator dispatches a fresh read-only `reviewer-agent` (Visual Critic) via `view_image` to verify `T04a [acceptance]`.

## Mutable owners

- `media/shots/s01-draft-*`
- `qc/s01-draft.json`
- `qc/s01-draft-sheet.png`

## Exclusive locks

- `receipts.jsonl`

## Final validation

- Run `python3 scripts/hf_guard.py run --campaign campaigns/example-product-spot --shot s01 --kind video --phase draft --workflow --model cinematic_studio_video_4_0 --prompt-file campaigns/example-product-spot/prompts/s01_video_v1.txt --out campaigns/example-product-spot/media/shots/s01-draft-take1.mp4 -- --mode omni_reference --resolution 480p --duration 5 --aspect_ratio 16:9`.
- Run `python3 scripts/qa_media.py clip campaigns/example-product-spot/media/shots/s01-draft-take1.mp4 --sheet campaigns/example-product-spot/qc/s01-draft-sheet.png --json` and save output to `qc/s01-draft.json` confirming exit code `0`.
- Hand off `qc/s01-draft.json` and `qc/s01-draft-sheet.png` to Root Orchestrator for fresh read-only `reviewer-agent` Visual Critic inspection against the Continuity Lock (`S01 -> S02` seam, clasp latch action, blind-debossed `NORD ATELIER` mark legibility).

## Reopen if

`s01` breaches 2 bounded auto-retries, fails deterministic `qa_media.py clip`, or is rejected by Visual Critic on the `S01 -> S02` Continuity Lock seam.
