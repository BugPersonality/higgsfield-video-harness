# T05 — Generate 15s Ambient Score, Assemble 480p Draft Cut, and Gate 2 Review Package

## Outcome

Generate the 15-second sparse solo cello and felt piano underscore via `scripts/hf_guard.py run` (`elevenlabs_music_v2_5`, estimated 10 credits), assemble accepted `s01`–`s03` 480p drafts with normalized audio into `media/exports/draft_cut.mp4` and `media/exports/draft-stems/`, run `qa_media.py render`, and produce the complete Gate 2 draft review package for independent read-only `reviewer-agent` verification prior to requester approval (`user-draft-gate [effect:approve-draft]`).

## Depends on

- T03
- T04a [acceptance]
- T04b [acceptance]
- budget-envelope [effect:spend]

## Sources

- ../intent.md
- ../script.md
- ../storyboard.md
- ../treatment.md
- ../style-bible.md
- ../shotlist.json

## Provides

- Generated 15-second instrumental stem under `media/audio/music-take*.wav`.
- Assembled 15-second 24fps draft cut (`media/exports/draft_cut.mp4`) plus separated stems under `media/exports/draft-stems/`.
- Deterministic render QA report (`qc/draft-cut.json`) and contact sheet (`qc/draft-cut-sheet.png`) for fresh read-only `reviewer-agent` check and Gate 2 requester sign-off.

## Boundary

Complete all work inside the 140-credit Draft cap (`phase=draft`). Do not self-approve visual or editorial acceptance and never begin `1080p` final rendering (`T06`) until a fresh read-only `reviewer-agent` verifies the draft cut and the requester explicitly clears `user-draft-gate [effect:approve-draft]`.

## Mutable owners

- `media/audio/music-*`
- `media/exports/draft_cut.mp4`
- `media/exports/draft-stems/*`
- `qc/draft-cut.json`
- `qc/draft-cut-sheet.png`

## Exclusive locks

- `receipts.jsonl`

## Final validation

- Run `python3 scripts/hf_guard.py run --campaign campaigns/example-product-spot --shot music --kind audio --phase draft --model elevenlabs_music_v2_5 --out campaigns/example-product-spot/media/audio/music-take1.wav -- --duration 15 --force_instrumental true --prompt "Restrained Scandinavian chamber minimalism, solitary warm solo cello and sparse soft felt piano notes, unhurried 68 BPM, airy reverberant hall acoustic, quiet luxury documentary mood"`.
- Run `bash scripts/assemble.sh --campaign campaigns/example-product-spot --manifest campaigns/example-product-spot/shotlist.json --music campaigns/example-product-spot/media/audio/music-take1.wav --music-vol 0.14 --sfx-vol 0.18 --out campaigns/example-product-spot/media/exports/draft_cut.mp4 --stems-dir campaigns/example-product-spot/media/exports/draft-stems`.
- Run `python3 scripts/qa_media.py render campaigns/example-product-spot/media/exports/draft_cut.mp4 --sheet campaigns/example-product-spot/qc/draft-cut-sheet.png --json` and save output to `qc/draft-cut.json` confirming exit code `0`.
- Verify total draft spend `<= 140` credits via `python3 scripts/hf_guard.py status --campaign campaigns/example-product-spot --json` and hand off to Root Orchestrator for fresh read-only `reviewer-agent` check before Gate 2 requester review.

## Reopen if

Music contains percussion, vocals, or jarring tempo breaks across 2 bounded attempts, `qa_media.py render` fails loudness/gap checks, or requester requests creative revisions at Gate 2.
