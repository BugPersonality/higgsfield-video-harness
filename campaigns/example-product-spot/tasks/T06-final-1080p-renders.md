# T06 — Render Approved 1080p Final Workflow Clips (s01–s03)

## Outcome

Following `T05 [acceptance]` and explicit requester Gate 2 approval (`user-draft-gate [effect:approve-draft]`), render the approved `s01`, `s02`, and `s03` shots at `1080p` via `scripts/hf_guard.py run --workflow` (`cinematic_studio_video_4_0`, `--mode omni_reference`, estimated 240 credits total) within the 260-credit Final cap, validate each clip deterministically via `qa_media.py clip`, and emit `3x2` contact sheets for independent read-only Visual Critic (`reviewer-agent`) sign-off before final assembly (`T07`).

## Depends on

- T05 [acceptance]
- user-draft-gate [effect:approve-draft]
- budget-envelope [effect:spend]

## Sources

- ../intent.md
- ../script.md
- ../storyboard.md
- ../style-bible.md
- ../shotlist.json
- ../prompts/s01_video_v1.txt
- ../prompts/s02_video_v1.txt
- ../prompts/s03_video_v1.txt

## Provides

- Candidate 1080p final video clips under `media/shots/s01-final-*.mp4`, `media/shots/s02-final-*.mp4`, and `media/shots/s03-final-*.mp4`.
- Deterministic clip QA reports (`qc/s01-final.json`, `qc/s02-final.json`, `qc/s03-final.json`) and `3x2` contact sheets (`qc/s01-final-sheet.png`, `qc/s02-final-sheet.png`, `qc/s03-final-sheet.png`) for independent read-only Visual Critic verification.

## Boundary

Require explicit requester clearance of `user-draft-gate [effect:approve-draft]` before running any `phase=final` call. Enforce Final cap `<= 260` credits via `scripts/hf_guard.py`. Do not assemble `master.mp4` or self-approve visual quality — Root Orchestrator dispatches a fresh read-only `reviewer-agent` (Visual Critic) via `view_image` to verify every 1080p contact sheet before recording `T06 [acceptance]`.

## Mutable owners

- `media/shots/s01-final-*`
- `media/shots/s02-final-*`
- `media/shots/s03-final-*`
- `qc/s01-final.json`
- `qc/s02-final.json`
- `qc/s03-final.json`
- `qc/s01-final-sheet.png`
- `qc/s02-final-sheet.png`
- `qc/s03-final-sheet.png`

## Exclusive locks

- `receipts.jsonl`

## Final validation

- Run `python3 scripts/hf_guard.py run --campaign campaigns/example-product-spot --shot s01 --kind video --phase final --workflow --model cinematic_studio_video_4_0 --prompt-file campaigns/example-product-spot/prompts/s01_video_v1.txt --out campaigns/example-product-spot/media/shots/s01-final-take1.mp4 -- --mode omni_reference --resolution 1080p --duration 5 --aspect_ratio 16:9` (and matching calls for `s02`, `s03`).
- Run `python3 scripts/qa_media.py clip` with `--sheet` and `--json` on all three 1080p clips confirming exit code `0`.
- Confirm cumulative final spend `<= 260` credits via `python3 scripts/hf_guard.py status --campaign campaigns/example-product-spot --json` and hand off contact sheets to Root Orchestrator for fresh read-only `reviewer-agent` Visual Critic review.

## Reopen if

Independent Visual Critic rejects any 1080p render for visual regression against the approved 480p draft or remaining Final cap cannot cover a required retry.
