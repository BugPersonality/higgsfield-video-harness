# Artifacts

Defines the campaign folder map under `campaigns/<slug>/` (and reusable brand
state under `brands/<brand>/`), the strict boundary between Git-tracked text
contracts and gitignored media binaries, and how assets evolve cleanly across
rounds (`R0`–`R5`).

## Campaign Folder Map

Scaffolded via `make campaign-init SLUG=<slug> [BRAND=<brand>]`
(`scripts/campaign_init.py`):

```text
campaigns/<slug>/
├── brief.md                 # Git-tracked — Direction Brief V1 (R0; status: draft | active | done)
├── taste-log.md             # Git-tracked — Cumulative Taste Memory (append-only TL-01, TL-02, ...)
├── script.md                # Git-tracked — 3-column commercial script (R1B, commercial track)
├── storyboard.md            # Git-tracked — Continuity-locked S01..SN storyboard (R1B, commercial track)
├── style-bible.md           # Git-tracked — Palette, lighting, lens & audio craft rules (R1B)
├── shotlist.json            # Git-tracked — Live Production Board (lookbook[], shots[], audio, LOCKED status)
├── prompts/                 # Git-tracked — Versioned prompts (lb_*_v1.txt, sNN_still_v1.txt, sNN_video_v1.txt)
├── receipts.jsonl           # Git-tracked — Exclusive-locked hf_guard.py spend & upload ledger
├── qc/
│   ├── *.json               # Git-tracked — qa_media.py probe JSONs and Visual Critic records
│   └── *.png                # Gitignored — lookbook.png, stills_strip.png, 3x2 contact sheets
└── media/                   # Gitignored — all binary inputs, renders, audio & exports
    ├── references/          # Real product/character/location photos supplied by Director
    ├── lookbook/            # R2 contrasting A/B/C Lookbook variant PNGs
    ├── stills/              # R3 keyframe start-frame still PNGs (sNN-vK.png)
    ├── shots/               # R4 draft & R5 1080p video clips (sNN-draft-vK.mp4, sNN-final-vK.mp4)
    ├── audio/               # VO tracks, rough/final music beds, SFX
    └── exports/             # animatic.mp4 (R3), draft_cut.mp4 (R4B), master.mp4 + stems/ (R5)
```

### Reusable Brand State (`brands/<brand>/`)

| Path | Tracked in Git? | Purpose |
| --- | --- | --- |
| `brands/<brand>/brand.md` | Yes | Durable brand identity: voice, phonetic pronunciations, physical product invariants, non-negotiable rules |
| `brands/<brand>/taste.md` | Yes | Graduated cross-campaign **Brand Taste Memory** seeded into new campaigns at `R0` and updated only with explicit Director confirmation at `R5` |

## Ownership & Lifecycle Table

| Artifact | Writer | Lifecycle / Validation |
| --- | --- | --- |
| `brief.md` | Root Producer only | `draft` → `active` (after Dailies 0) → `done` (after Final Dailies 5); checked by `make brief-check CAMPAIGN=<slug>` |
| `taste-log.md` | Root Producer only | Append-only `### TL-<NN> (R<k> — <stage>)` entries; never silently erase history |
| `script.md`, `storyboard.md`, `style-bible.md` | `specialist-agent` proposals integrated by Root Producer | Authored in `R1B`; updated in place if story/continuity shifts |
| `shotlist.json` | Root Producer only | Per-asset `status`: `DRAFT` → `IN_REVIEW` → `ITERATING` → `LOCKED` (`version` counter); checked by `make campaign-check CAMPAIGN=<slug>` |
| `prompts/*.txt` | `specialist-agent` / `worker-agent` (disjoint paths) | Strictly versioned (`_v1.txt`, `_v2.txt`); never overwrite prior versions that produced paid receipts |
| `receipts.jsonl` | `scripts/hf_guard.py` (exclusive file lock) | Append-only two-stage (`reserved` → `completed \| download_failed \| rejected \| in_progress`) |
| `media/*`, `qc/*.png` | Disjoint `worker-agent` lanes (`media/references/` by Director) | Gitignored binaries; `LOCKED` media files are immutable unless explicitly unlocked |

## Git vs Media Boundary

- **Git tracks text, never media binaries.** Tracking `brief.md`,
  `taste-log.md`, `script.md`, `storyboard.md`, `style-bible.md`,
  `shotlist.json`, `prompts/`, `qc/*.json`, and `receipts.jsonl` makes every
  creative steer, prompt iteration, internal QC rejection, and credit spent
  diffable and auditable.
- **Keep binaries and secrets out of Git.** `.png`, `.jpg`, `.mp4`, `.mov`,
  `.wav`, and `.mp3` files under `campaigns/<slug>/media/` and preview PNGs
  under `campaigns/<slug>/qc/*.png` stay gitignored. Never commit API keys,
  OAuth tokens, base64-encoded media, or private personal photos.
- **Reference by path, never duplicate.** Link `brands/<brand>/brand.md`,
  `brands/<brand>/taste.md`, `docs/cinema-presets.json`, and
  `prompts/sNN_*.txt` by relative path instead of copy-pasting mutable blocks.

## Surgical Iteration & Version Hygiene

When Director feedback steers a single Lookbook entity, still, or shot:

1. Append the new `TL-<NN>` entry to `taste-log.md` first.
2. Keep every `LOCKED` asset, its `upload_id`, its media file, and all
   `receipts.jsonl` history completely intact.
3. Increment `version` on ONLY the target asset in `shotlist.json` (`status:
   "ITERATING"`), create the next versioned prompt file (`_v2.txt`), and write
   the new render to a matching versioned path (`media/stills/s02-v2.png` or
   `media/shots/s02-draft-v2.mp4`) so old and new takes remain comparable if
   needed.
4. Re-run `make campaign-check CAMPAIGN=<slug>` before dispatching the
   micro-cost re-roll.
