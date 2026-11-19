# T04b — Generate 480p Draft Clip (s03)

## Outcome

Running in parallel Wave 4 alongside `T04a` following `s02` Risk-First Pilot acceptance, generate the 5-second 480p draft workflow clip for `s03` (wide sunlit railway concourse departure) via `scripts/hf_guard.py run --workflow` (`cinematic_studio_video_4_0`, `--mode omni_reference`, estimated 15 credits), validate deterministically with `qa_media.py clip`, and emit `qc/s03-draft.json` plus `qc/s03-draft-sheet.png` for fresh read-only Visual Critic (`reviewer-agent`) review.

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
- ../prompts/s03_video_v1.txt

## Provides

- Candidate 480p draft video clip under `media/shots/s03-draft-take*.mp4`.
- Deterministic QA JSON (`qc/s03-draft.json`) and `3x2` contact sheet (`qc/s03-draft-sheet.png`) for independent read-only `reviewer-agent` Visual Critic seam audit against `s02`.

## Boundary

Write strictly to `s03` draft paths in `phase=draft` at `480p` respecting `Max auto-retries/shot: 2`. Do not touch `s01` or `s02` files, and do not self-approve visual quality — Root Orchestrator dispatches a fresh read-only `reviewer-agent` (Visual Critic) via `view_image` to verify `T04b [acceptance]`.

## Mutable owners

- `media/shots/s03-draft-*`
- `qc/s03-draft.json`
- `qc/s03-draft-sheet.png`

## Exclusive locks

- `receipts.jsonl`

## Final validation

- Run `python3 scripts/hf_guard.py run --campaign campaigns/example-product-spot --shot s03 --kind video --phase draft --workflow --model cinematic_studio_video_4_0 --prompt-file campaigns/example-product-spot/prompts/s03_video_v1.txt --out campaigns/example-product-spot/media/shots/s03-draft-take1.mp4 -- --mode omni_reference --resolution 480p --duration 5 --aspect_ratio 16:9`.
- Run `python3 scripts/qa_media.py clip campaigns/example-product-spot/media/shots/s03-draft-take1.mp4 --sheet campaigns/example-product-spot/qc/s03-draft-sheet.png --json` and save output to `qc/s03-draft.json` confirming exit code `0`.
- Hand off `qc/s03-draft.json` and `qc/s03-draft-sheet.png` to Root Orchestrator for fresh read-only `reviewer-agent` Visual Critic inspection against the Continuity Lock (`S02 -> S03` seam, right-hip bag carry, screen-left sunlight geometry, closing button silhouette).

## Reopen if

`s03` breaches 2 bounded auto-retries, fails deterministic `qa_media.py clip`, or is rejected by Visual Critic on the `S02 -> S03` Continuity Lock seam.
