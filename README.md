# higgsfield-video-harness

Intent-first agentic video production harness for **Codex** + **Higgsfield CLI** + **FFmpeg**.

Inspired by the spec-first, multi-agent engineering architecture of
[`rust-service-template-rest`](https://github.com/Dankosik/rust-service-template-rest),
adapted from deterministic software delivery to cinematic generative video:

- **You own meaning, brand truth, and budget ceilings** — captured once in a
  verified `campaigns/<slug>/intent.md` through structured frontier grilling
  (zero prompt-engineering, CLI flags, or codec trivia on your plate).
- **Agents own craft and execution** — fresh-context creative treatments
  (*Design It Twice*), live Higgsfield CLI schema discovery, reference-locked
  stills and video shots, automated deterministic + multimodal visual QA
  (`ffprobe` + 3×2 contact sheets inspected via Codex `view_image`), audio
  mixing, and FFmpeg assembly.
- **Code enforces the money and quality walls** — `scripts/hf_guard.py` hard-caps
  credit spend and prevents double-charges on timeouts; `scripts/check-intent.py`,
  `scripts/check-ledger.py`, and `scripts/qa_media.py` turn workflow rules into
  executable gates.

## Prerequisites

- **Codex** (with Multi-Agent V2 enabled via `.codex/config.toml`)
- **Higgsfield CLI** (`higgsfield`) authenticated to your workspace:
  ```bash
  curl -fsSL https://raw.githubusercontent.com/higgsfield-ai/cli/main/install.sh | sh
  higgsfield auth login
  higgsfield account status
  ```
- **FFmpeg & ffprobe** (`brew install ffmpeg` on macOS)
- **Python 3.11+** (standard library only — zero pip packages required for core tools)
- *(Optional)* Official Higgsfield skills alongside this harness:
  ```bash
  npx skills add higgsfield-ai/skills
  ```
- *(Optional)* Higgsfield MCP login for quick read-only balance/model checks:
  ```bash
  codex mcp login higgsfield
  ```

## How a Campaign Runs

1. **Scaffold a campaign:**
   ```bash
   make campaign-init SLUG=my-product-spot
   ```
   Place your product/reference photos in `campaigns/<YYYY-MM-DD>-my-product-spot/media/references/`.
2. **Start Codex in this repo** and describe what you want in plain language
   (meaning, audience, feeling, budget cap).
3. **Phase 0 — Intake (`intent.md`):** Codex grounds in live schemas and brand
   files, interviews you in short frontier rounds, validates `intent.md` with
   `make intent-check`, runs a fresh Cold-Start Intent Review, and asks you to
   confirm **Gate 1**.
4. **Phases 1–4 — Autonomous Production:**
   - **Creative Definition:** for commercial/product spots, runs the bundled
     commercial craft pipeline (`ad-references` → `ad-concepts` with swap test
     → `ad-script` with read-aloud budget & mute test → `ad-storyboard` with
     **Continuity Lock** and **Test-take checks**); for non-commercial/art
     pieces, runs competing `specialist-agent` lanes (*Design It Twice*) into
     `treatment.md` and `style-bible.md`.
   - **Production Design:** translates `storyboard.md` / `treatment.md` into
     `shotlist.json` (`continuity_lock`, `test_take_check`, start/end frames)
     against live `higgsfield model get` schemas and verifies `generate cost` ≤
     your credit cap.
   - **Planning:** topological `tasks.md` + task packets verified by `make ledger-check`.
   - **Production & Delivery:**
     - **Wave 1 (Stills + optional 0-video-credit Still Animatic):** builds
       reference-locked stills and optionally assembles a timed still animatic
       (`make animatic`) to check rhythm and mute-test before spending video
       credits.
     - **Wave 2 (Risk-First Pilot + VO):** shoots risky shots flagged with
       `test_take_check` first at `480p`/`--draft` before committing to full
       batch rendering.
     - In **`autonomous-draft`** mode (default), agents run end-to-end within
       your `Draft cap` (`480p`/`720p` or `seedance_2_5 --draft`) to produce a
       full assembled `draft_cut.mp4` + QA report before asking for your
       feedback, then render `1080p` finals only on approved shots.
     - In **`checkpointed`** mode, agents pause briefly at **Stills** and
       **Pilot + VO** before parallel batch generation.
5. **Delivery:** you receive `media/exports/master.mp4`, clean audio/video stems
   in `media/exports/stems/` (ready for optional 15-minute color grading in
   DaVinci Resolve), and an auditable `receipts.jsonl` spend ledger.

## Repository Map

| Path | Role |
| --- | --- |
| [`AGENTS.md`](AGENTS.md) | Constitution: authority, budget walls, channel routing, validation budget |
| [`.agents/roles/`](.agents/roles) | 5 typed Codex subagent roles (`evidence`, `specialist`, `worker`, `reviewer`, `adjudicator`) |
| [`.agents/skills/`](.agents/skills) | 11 bundled skills: workflow (`idea-refine`, `grilling`), commercial pre-production (`ad-references`, `ad-concepts`, `ad-script`, `ad-storyboard` from [`ad-skills`](https://github.com/Dankosik/ad-skills)), and video production (`higgsfield-cli`, `video-direction`, `video-consistency`, `video-qa`, `video-assembly`) |
| [`docs/ad-craft-glossary.md`](docs/ad-craft-glossary.md) | Shared commercial craft vocabulary (swap test, mute test, read-aloud budget, Continuity Lock, Test-take check) |
| [`docs/video-workflow/router.md`](docs/video-workflow/router.md) | Macro-phase workflow router, interfaces, phases, shared protocols |
| [`docs/agent-harness.md`](docs/agent-harness.md) | Delegation contract, fresh-context rules, Codex V2 adapter |
| [`scripts/`](scripts) | Mechanical verifiers (`check-intent.py`, `check-ledger.py`, `check-instructions.py`, `check-docs.py`), `hf_guard.py`, `qa_media.py`, `assemble.sh`, `campaign_init.py` |
| [`brands/example-brand/brand.md`](brands/example-brand/brand.md) | Reusable brand identity, product invariants, pronunciation guide |
| [`campaigns/example-product-spot/`](campaigns/example-product-spot) | Complete worked reference campaign passing all mechanical gates |
| [`tests/`](tests) | Stdlib `unittest` suite exercising every validator, mock `hf_guard`, synthetic FFmpeg QA, and assembly |

## Quick Verification

Run the entire offline verification suite right after cloning (zero credits spent):

```bash
make check
```

See `make help` for individual campaign and QA commands.
