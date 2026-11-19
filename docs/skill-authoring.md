# Skill Authoring

This document owns the structure and authoring rules for repository skills under
`.agents/skills/<name>/`. Mechanical shape invariants are verified by
`make check-instructions` (`scripts/check-instructions.py`) and link integrity
by `make docs-check` (`scripts/check-docs.py`).

## Three Skill Classes

`.agents/skills/` holds three distinct classes with explicit invocation and
authoring rules:

| Class | Repository skills | Invocation | `agents/openai.yaml` | Purpose |
| --- | --- | --- | --- | --- |
| **Workflow skills** | `idea-refine`, `grilling` | Explicit user invocation only (`disable-model-invocation: true`) | Required: sets `policy.allow_implicit_invocation: false` | Interactive methods a person invokes directly to sharpen a raw video idea or stress-test meaning and taste forks before or during `R0`/`R1` |
| **Commercial pre-production skills** | `ad-references`, `ad-concepts`, `ad-script`, `ad-storyboard` *(bundled from `Dankosik/ad-skills`)* | Model-selected from `description` via [`AGENTS.md`](../AGENTS.md#skill-routing) | Carries `interface` (`display_name`, `short_description`) only; omits `policy` | Structured commercial development pipeline used in [`R1`](video-workflow/rounds/r1-story-and-cost.md) and governed by shared vocabulary in [`docs/ad-craft-glossary.md`](ad-craft-glossary.md) |
| **Production decision skills** | `higgsfield-cli`, `video-direction`, `video-consistency`, `video-qa`, `video-assembly` | Model-selected from `description` via [`AGENTS.md`](../AGENTS.md#skill-routing) | Optional | Concise decision-focused craft prose (under 300 lines) loaded only when the active Higgsfield, prompting, QC, or FFmpeg decision matches its trigger |

When the [Workflow Router](video-workflow/router.md), a round playbook
(`docs/video-workflow/rounds/r*.md`), or [Agent Harness](agent-harness.md)
already owns a process rule, link to that document instead of duplicating
workflow choreography inside a skill.

## Directory And File Layout

```text
.agents/skills/<name>/
├── SKILL.md              # Required: frontmatter + concise method
├── agents/
│   └── openai.yaml       # Workflow: policy.allow_implicit_invocation: false | Commercial: interface only
└── references/           # Optional: deep tables, examples, or audit flows loaded on demand
    └── <topic>.md
```

- **Load references on demand.** Keep lookup tables, prompt libraries, FFmpeg
  filter matrices, audit checklists, and worked defect examples in
  `references/*.md` (or skill-local companion files linked conditionally from
  `SKILL.md`). Link each reference at the exact step or decision branch that
  needs it so actors stay inside the **Smart Zone**.
- **Keep scripts, glossaries, and templates outside skills.** Executable tools
  live in `scripts/`, example campaigns in `campaigns/`, reusable brand profiles
  and taste files in `brands/`, and shared glossaries/presets in `docs/` (such
  as [`docs/ad-craft-glossary.md`](ad-craft-glossary.md) and
  [`docs/cinema-presets.example.json`](cinema-presets.example.json)). Skills
  link to them rather than embedding brittle copies.
- **`agents/openai.yaml` policy boundary.**
  - Workflow skills (`idea-refine`, `grilling`) MUST set
    `policy.allow_implicit_invocation: false` so Codex never hijacks an active
    round (`R2`–`R5`) with standalone interrogation.
  - Commercial pre-production skills (`ad-references`, `ad-concepts`,
    `ad-script`, `ad-storyboard`) carry `interface` (`display_name`,
    `short_description`) only and intentionally omit `policy` so Codex can load
    them implicitly during `R1` commercial story development.

## Frontmatter Rules

- **`name` equals directory name.** Use lowercase hyphenated identifiers
  (`video-direction` in `.agents/skills/video-direction/SKILL.md`).
- **Commercial pre-production skills & production decision skills** carry
  exactly two frontmatter keys (`name` and `description`):

```yaml
---
name: video-qa
description: "Internal visual and technical defect filtering. Use when inspecting Lookbook variants, stills, 3x2 contact sheets via view_image, or qa_media.py receipts to catch defects and taste-log regressions before Dailies."
---
```

- **Workflow skills** add `metadata` (`invocation: user`, `kind: workflow`) and
  `disable-model-invocation: true` matching `agents/openai.yaml`:

```yaml
---
name: grilling
description: "Stress-test a video brief, meaning fork, or taste trade-off through light meaning-only rounds while keeping all technical mechanics off the Director's frontier."
disable-model-invocation: true
metadata:
  invocation: user
  kind: workflow
---
```

- **Crisp routing `description`.** Keep `description` to at most two sentences
  naming the observable trigger (`Use when` / `Use for`) and the exact decision
  owned. Keep sibling triggers cleanly distinguishable:
  - *Workflow:* `idea-refine` (sharpening a fuzzy video idea into a falsifiable
    viewer bet), `grilling` (meaning-only alignment and comparative taste
    forks);
  - *Commercial pre-production:* `ad-references` (dissecting primary spots into
    timecoded beats & transferable mechanisms), `ad-concepts` (product-locked
    orthogonal premises & swap test), `ad-script` (timed three-column script,
    read-aloud budget & mute test), `ad-storyboard` (continuity-locked
    `S01..SN` shot list, focal entry & test-take checks);
  - *Production decisions:* `higgsfield-cli` (live CLI schemas, model/workflow/audio
    selection, `hf_guard.py --round --round-cap`), `video-direction` (still &
    timestamped motion prompts, anti-IP phrasing, phonetic VO),
    `video-consistency` (cross-shot `LOCKED` Lookbook/reference wiring &
    `continuity_lock`), `video-qa` (`qa_media.py`, `view_image` pre-Dailies
    defect & `TASTE_REGRESSION` filtering), `video-assembly` (0-credit still
    animatic, FPS lock, audio level law, `-14 LUFS`, stems export).

## Body And Length Budget

- **Hard ceiling: under 300 lines in `SKILL.md`** for all decision and
  commercial pre-production skills (enforced by `scripts/check-instructions.py`).
  Keep `SKILL.md` concise and scannable so loading a skill preserves the
  actor's **Smart Zone**. Move verbose matrices or filter-graph recipes into
  `references/*.md`.
- **Teach decisions, not boilerplate.** Focus prose on judgment criteria,
  non-obvious failure modes, and conditions that switch from the default path to
  a specialized alternative.
- **Honor cumulative Taste Memory and `LOCKED` assets.** Every creative,
  prompting, consistency, and QA skill assumes `campaigns/<slug>/taste-log.md`
  (plus `brands/<brand>/taste.md`) is binding and `LOCKED` assets in
  `shotlist.json` are immutable unless explicitly unlocked by the Director.
- **Never duplicate `AGENTS.md` or live schemas.** Unconditional rules
  (authority, `hf_guard.py` mandate, Director ↔ Crew boundary, precedence over
  external skills) live in [`AGENTS.md`](../AGENTS.md#authority). Volatile
  Higgsfield model parameters live in `higgsfield model get <id> --json`; skills
  teach how to inspect and choose rather than hardcoding stale flag lists.
- **Graduate mechanical rules to code.** Any check that can be enforced
  deterministically (frontmatter shape, `brief.md` structure, `shotlist.json`
  budget math, `asset_locked` refusal, loudness thresholds, link validity)
  belongs in `scripts/` and [`Makefile`](../Makefile), not prose warnings.

## Validation

After adding or modifying any skill under `.agents/skills/`:

1. Run `make check-instructions` to verify directory-to-`name` parity, required
   frontmatter keys, `< 300` line limits on decision skills, `agents/openai.yaml`
   (`policy.allow_implicit_invocation: false` on workflow skills; `interface`
   only without `policy` on bundled commercial pre-production skills), and
   `.codex/config.toml` sync.
2. Run `make docs-check` to verify every relative link and `#heading-anchor`
   between `SKILL.md`, `references/*.md`, and `docs/`.
3. Read sibling `description` fields side by side to confirm zero routing
   overlap.
