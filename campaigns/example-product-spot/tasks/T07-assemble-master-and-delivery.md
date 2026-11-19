# T07 — Assemble 1080p Master & Stems and Prepare Final Delivery Review

## Outcome

Assemble the accepted `1080p` clips (`s01`, `s02`, `s03`) and approved 15-second ambient score into `media/exports/master.mp4` (`1920x1080`, 24 fps, H.264/AAC, `-14 LUFS (±1.0 LU)`, true peak `<= -1.0 dBTP`) plus separated stems under `media/exports/stems/`, run deterministic `qa_media.py render`, and submit the complete delivery bundle (`qc/master-qa.json`, `qc/master-sheet.png`, `receipts.jsonl`) to a fresh read-only `reviewer-agent` for final Delivery Review.

## Depends on

- T05
- T06 [acceptance]

## Sources

- ../intent.md
- ../script.md
- ../storyboard.md
- ../style-bible.md
- ../shotlist.json

## Provides

- Delivery master (`media/exports/master.mp4`) and separated stems (`media/exports/stems/`).
- Deterministic render QA report (`qc/master-qa.json`) and contact sheet (`qc/master-sheet.png`) ready for independent read-only `reviewer-agent` Delivery Review.

## Boundary

Zero paid Higgsfield calls occur in this task. Do not self-approve final delivery — Root Orchestrator dispatches a fresh read-only `reviewer-agent` for Delivery Review verifying `intent.md` success criteria, loudness/technical pass, visual continuity, spend receipts, and clean Git status before final handoff.

## Mutable owners

- `media/exports/master.mp4`
- `media/exports/stems/*`
- `qc/master-qa.json`
- `qc/master-sheet.png`

## Exclusive locks

- none

## Final validation

- Run `bash scripts/assemble.sh --campaign campaigns/example-product-spot --manifest campaigns/example-product-spot/shotlist.json --out campaigns/example-product-spot/media/exports/master.mp4 --stems-dir campaigns/example-product-spot/media/exports/stems --music-vol 0.14 --sfx-vol 0.18`.
- Run `python3 scripts/qa_media.py render campaigns/example-product-spot/media/exports/master.mp4 --sheet campaigns/example-product-spot/qc/master-sheet.png --json` and save output to `qc/master-qa.json` confirming exit code `0`, `-14 LUFS (±1.0 LU)`, and true peak `<= -1.0 dBTP`.
- Confirm cumulative draft spend `<= 140` credits and final spend `<= 260` credits via `python3 scripts/hf_guard.py status --campaign campaigns/example-product-spot --json` and zero tracked binary commits via `git status`.
- Hand off `qc/master-qa.json`, `qc/master-sheet.png`, and `receipts.jsonl` to Root Orchestrator for fresh read-only `reviewer-agent` Delivery Review.

## Reopen if

`qa_media.py render` fails loudness, true-peak, black-gap, or frozen-tail checks, or fresh read-only `reviewer-agent` flags any `intent.md` or Continuity Lock defect during Delivery Review.
