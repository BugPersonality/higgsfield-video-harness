# higgsfield-video-harness

**Feedback-loop-first** agentic video production studio for **Codex** + **Higgsfield CLI** + **FFmpeg**.

Unlike software engineering—where a spec can freeze upfront and agents can code
autonomously behind a compiler—great cinema and commercials depend on **emergent
visual taste**. You do not know the exact shade of light, casting presence, or
cutting rhythm until you see and hear real options.

This harness separates roles cleanly like a real film set:

- **You are the Director:** you set meaning, pick between concrete visual/story
  options (`A / B / C`), react in plain language (*"less glossy, cooler light,
  slower push on shot 2"*), approve each round's exact credit cost, and lock
  what works (`LOCKED`). You never touch prompts, model IDs, UUIDs, or FFmpeg.
- **Agents are the Production Crew:** inside every round, Codex handles 100% of
  the technical work—commercial pre-production (`ad-references`, `ad-concepts`,
  `ad-script`, `ad-storyboard`), live Higgsfield CLI schema inspection,
  parallel variant rendering, deterministic `ffprobe`/`loudnorm` checks,
  internal **Visual Critic** defect filtering (`view_image` on `3×2` contact
  sheets), 0-video-credit still animatics, and FFmpeg mastering.
- **Cumulative Taste Memory (`taste-log.md`):** every reaction you give is
  distilled into persistent `Approved / LOCKED`, `More of`, `Change / Steer`,
  and `Never` rules that guide every downstream prompt and Visual Critic
  check—and graduate into reusable `brands/<brand>/taste.md` across campaigns.
- **Code enforces the money & lock walls:** `scripts/hf_guard.py` enforces BOTH
  the total `Campaign cap` AND per-round `--round-cap`, prevents double-charges
  on timeouts, and refuses to overwrite `LOCKED` assets.

## The 6 Interactive Production Rounds (`R0` → `R5`)

There is **no blind end-to-end autonomous mode**. Every round ends with a
compact **Dailies Packet** (1 visual artifact + 1-line internal QC summary +
2–3 comparative taste questions + exact `generate cost` for the next round):

| Round | Crew work inside the round | What you see (*Dailies*) | Typical cost |
| --- | --- | --- | --- |
| **R0 — Direction Seed** | Grounds in brand profile, `taste.md`, balance, and local photos; 3–5 meaning-only questions | Short `brief.md` card (meaning, taboos, `Campaign cap`) | 0 cr. |
| **R1 — Story & Cost Ticket** | `ad-references` → `ad-concepts` (4–5 swap-tested pitches) → `ad-script` (3-column, mute test, read-aloud budget) → `ad-storyboard` (`Continuity Lock` + `Test-take checks`) + live `generate cost` | **1A:** Pick/blend 1 of 4–5 pitches<br>**1B:** Readable story + **exact round-by-round price list** | 0 cr. |
| **R2 — Casting & World Lookbook** *(skipped if all objects are real photos)* | Generates **2–3 contrasting variants (`A / B / C`)** per invented object/character/location, filters AI defects internally, stitches one grid (`make lookbook`) | **1 Lookbook PNG (`A / B / C`)** + next-round cost; pick/blend → `LOCKED` | ~20–45 cr. |
| **R3 — Keyframe Stills & Animatic** | Generates `s01..sN` stills locked to `LOCKED` UUIDs + `taste-log.md`, generates VO (`qa_media.py voice`) + rough music, builds `stills_strip.png` + **`animatic.mp4`** | **Storyboard Strip + playable Still Animatic** (judge framing, rhythm & voice *before spending 1 video credit!*) | ~30–50 cr. *(0 video cr.)* |
| **R4 — Motion Dailies** | **4A:** Shoots risky `test_take_check` shot(s) first at `480p`/`720p`/`--draft` + internal QA.<br>**4B:** Parallel remaining shots + `draft_cut.mp4` (`-14 LUFS`) | **4A:** Pilot clip<br>**4B:** Full **`draft_cut.mp4`** + per-shot `1080p` upgrade cost | ~45–90 cr. |
| **R5 — Final Master (`1080p`)** | Upgrades only approved shots to `1080p`, re-runs QA + Visual Critic, exports `master.mp4` + `stems/` (ready for optional DaVinci grading) | **`master.mp4` + `stems/` + spend receipt** + optional graduation of `taste-log.md` → `brands/<brand>/taste.md` | approved final quote |

## Prerequisites

- **Codex** (Multi-Agent V2 configured in `.codex/config.toml`)
- **Higgsfield CLI** (`higgsfield`) authenticated to your workspace:
  ```bash
  curl -fsSL https://raw.githubusercontent.com/higgsfield-ai/cli/main/install.sh | sh
  higgsfield auth login
  higgsfield account status
  ```
- **FFmpeg & ffprobe** (`brew install ffmpeg` on macOS)
- **Python 3.11+** (standard library only — zero pip packages required)

## Quick Start

```bash
# 1. Verify the entire harness offline (0 credits)
make check

# 2. Scaffold a new campaign
make campaign-init SLUG=my-product-spot BRAND=example-brand

# 3. Drop any real product/reference photos into media/references/
# 4. Open Codex in this repository and describe the meaning & goal of your spot
```

## Repository Map

| Path | Role |
| --- | --- |
| [`AGENTS.md`](AGENTS.md) | Studio constitution: Director ↔ Crew boundary, `taste-log.md`, `LOCKED` immutability, `hf_guard.py` rules |
| [`.agents/roles/`](.agents/roles) | 5 Codex subagent roles (`evidence`, `specialist`, `worker`, `reviewer` as internal defect filter, `adjudicator`) |
| [`.agents/skills/`](.agents/skills) | 11 bundled skills: intake (`idea-refine`, `grilling`), commercial craft (`ad-references`, `ad-concepts`, `ad-script`, `ad-storyboard` from [`ad-skills`](https://github.com/Dankosik/ad-skills)), and video production (`higgsfield-cli`, `video-direction`, `video-consistency`, `video-qa`, `video-assembly`) |
| [`docs/video-workflow/router.md`](docs/video-workflow/router.md) | Feedback-loop workflow (`R0`–`R5`), interfaces (`brief-v1`, `taste-log-v1`, `dailies-packet-v1`, `shotlist-v1`, `review-result-v1`), shared protocols |
| [`docs/ad-craft-glossary.md`](docs/ad-craft-glossary.md) | Shared commercial craft vocabulary (swap test, mute test, read-aloud budget, Continuity Lock, Test-take check) |
| [`scripts/`](scripts) | Mechanical guards & tools (`check-brief.py`, `check-campaign.py`, `hf_guard.py`, `qa_media.py` incl. `lookbook`, `assemble.sh` incl. `--animatic`, `campaign_init.py`, `check-instructions.py`, `check-docs.py`) |
| [`brands/example-brand/`](brands/example-brand) | Reusable brand identity (`brand.md`) + graduated brand taste memory (`taste.md`) |
| [`campaigns/example-product-spot/`](campaigns/example-product-spot) | Complete worked feedback-loop campaign (`brief.md`, `taste-log.md`, `script.md`, `storyboard.md`, `style-bible.md`, `shotlist.json`, `prompts/`) |
| [`tests/`](tests) | Stdlib `unittest` suite covering every validator, mock `hf_guard`, synthetic FFmpeg QA, `lookbook`, `--animatic`, and assembly |
