# higgsfield-video-harness

**Feedback-loop-first** agentic video production studio for **Codex** + **Higgsfield CLI** + **FFmpeg**.

Great cinema and commercials depend on **emergent visual taste**, not upfront specs. You direct meaning, pick among real visual options (`A / B / C`), react in plain language (*"cooler light, less glossy leather, hold shot 2 longer"*), and approve each round's exact credit cost. Codex handles 100% of the technical craft inside each round and filters AI defects internally before showing you **Dailies**.

## The 6 Interactive Rounds (`R0` → `R5`)

| Round | Crew craft inside the round | Dailies shown to Director | Typical credits |
| --- | --- | --- | --- |
| **R0 — Brief** | Ground in brand/taste/photos/balance; 3–5 meaning questions | Short `brief.md` card + `Campaign cap` | 0 cr. |
| **R1 — Story & Quote** | `ad-references` → `ad-concepts` (4–5 pitches) → `ad-script` → `ad-storyboard` + live `generate cost` | **1A:** Pick/blend pitch · **1B:** Readable story + exact round price list | 0 cr. |
| **R2 — Lookbook** *(skip if all real photos)* | 2–3 contrasting `A / B / C` variants per entity, internal QC filter, `make lookbook` | Labeled `lookbook.png` (`A / B / C`) + `R3` quote | ~20–45 cr. |
| **R3 — Stills & Animatic** | Keyframe stills locked to `LOCKED` UUIDs + `taste-log.md`, VO (`qa_media.py voice`), rough music, `make animatic` | `stills_strip.png` + playable 0-video-credit `animatic.mp4` + `R4A` quote | ~30–50 cr. |
| **R4 — Motion Dailies** | **4A:** Pilot `test_take_check` shot(s) at draft quality · **4B:** Parallel remaining shots + `draft_cut.mp4` | **4A:** Pilot clip · **4B:** Full `draft_cut.mp4` + per-shot `1080p` prices | ~45–90 cr. |
| **R5 — Final Master** | Upgrade only approved shots to `1080p`, re-run QA + Visual Critic, `make assemble` (`-14 LUFS`, `stems/`) | `master.mp4` + `stems/` + spend receipt + brand taste graduation | approved quote |

## Prerequisites & Quick Start

Requires **Codex** (`.codex/config.toml`), authenticated **Higgsfield CLI** (`higgsfield account status`), **FFmpeg/ffprobe**, and **Python 3.11+** (stdlib only).

```bash
# Verify harness, validators, mock spend guard, and synthetic FFmpeg QA offline (0 credits)
make check

# Scaffold a new campaign
make campaign-init SLUG=my-product-spot BRAND=example-brand
```

Drop any real product/reference photos into `campaigns/<date>-<slug>/media/references/`, open Codex, and describe the meaning and viewer feeling you want. Run `make help` for all commands.

## Repository Map

| Path | Role |
| --- | --- |
| [`AGENTS.md`](AGENTS.md) | Always-loaded studio constitution and context pointers |
| [`docs/workflow.md`](docs/workflow.md) | `R0`–`R5` feedback loop, Dailies Packet, Taste Memory, spend & lock rules |
| [`docs/delegation.md`](docs/delegation.md) | Subagent roles, Codex V2 setup, internal Visual Critic, recovery |
| [`docs/grilling.md`](docs/grilling.md) | Relentless meaning-only alignment and taste-fork interview protocol |
| [`docs/writing-for-agents.md`](docs/writing-for-agents.md) | Minimalist instruction & skill authoring rules |
| [`docs/ad-craft-glossary.md`](docs/ad-craft-glossary.md) | Shared vocabulary for the 4 bundled commercial skills |
| [`.agents/roles/`](.agents/roles) & [`.agents/skills/`](.agents/skills) | 4 Codex roles and 11 skills (incl. bundled `ad-references`, `ad-concepts`, `ad-script`, `ad-storyboard`) |
| [`scripts/`](scripts) & [`tests/`](tests) | Mechanical guards (`hf_guard.py`, `qa_media.py`, `assemble.sh`, validators) and stdlib unittest suite |
| [`brands/example-brand/`](brands/example-brand) & [`campaigns/example-product-spot/`](campaigns/example-product-spot) | Reusable brand taste profile and complete living campaign fixture |
