# Skill Authoring

This document owns the structure and authoring rules for repository skills under
`.agents/skills/<name>/`. Mechanical shape invariants are verified by
`make check-instructions` (`scripts/check-instructions.py`) and link integrity
by `make docs-check` (`scripts/check-docs.py`).

## Three Skill Classes

`.agents/skills/` holds three distinct classes with clear invocation and
authoring rules:

| Class | Repository skills | Invocation | `agents/openai.yaml` | Purpose |
| --- | --- | --- | --- | --- |
| **Workflow skills** | `idea-refine`, `grilling` | Explicit user invocation only (`disable-model-invocation: true`) | Required: sets `policy.allow_implicit_invocation: false` | Interactive methods a person invokes directly to sharpen a raw video idea or stress-test a brief/fork before entering or reopening Intake |
| **Commercial pre-production skills** | `ad-references`, `ad-concepts`, `ad-script`, `ad-storyboard` *(bundled from `Dankosik/ad-skills`)* | Model-selected from `description` via [`AGENTS.md`](../AGENTS.md#skill-routing) | Carries `interface` (`display_name`, `short_description`) only; omits `policy` | Structured commercial development pipeline governed by shared vocabulary in [`docs/ad-craft-glossary.md`](ad-craft-glossary.md) |
| **Production decision skills** | `higgsfield-cli`, `video-direction`, `video-consistency`, `video-qa`, `video-assembly` | Model-selected from `description` via [`AGENTS.md`](../AGENTS.md#skill-routing) | Optional | Concise decision-focused craft prose (under 300 lines) loaded only when the active Higgsfield/FFmpeg decision matches its trigger |

When a [Workflow Router](video-workflow/router.md) phase or
[Agent Harness](agent-harness.md) already owns a process rule, link to that
document instead of duplicating the workflow inside a skill.

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
  filter matrices, audit procedures, and worked defect examples in
  `references/*.md` (or skill-local companion files linked conditionally from
  `SKILL.md`). Link each reference at the exact step or decision branch that
  needs it so agents do not load the entire reference set by default.
- **Keep scripts and templates outside skills.** Executable tools live in
  `scripts/`, campaign templates in `campaigns/`, and shared glossaries/presets
  in `docs/` (such as [`docs/ad-craft-glossary.md`](ad-craft-glossary.md) and
  [`docs/cinema-presets.example.json`](cinema-presets.example.json)). Skills
  link to them rather than embedding brittle copies.
- **`agents/openai.yaml` policy boundary.**
  - Workflow skills (`idea-refine`, `grilling`) MUST set
    `policy.allow_implicit_invocation: false` so Codex never auto-triggers
    interactive grilling during autonomous production waves.
  - Commercial pre-production skills (`ad-references`, `ad-concepts`,
    `ad-script`, `ad-storyboard`) carry `interface` (`display_name`,
    `short_description`) only and intentionally omit `policy` so Codex can
    invoke them implicitly during Phase 1 commercial work.

## Frontmatter Rules

- **`name` equals directory name.** Use lowercase hyphenated identifiers
  (`video-direction` in `.agents/skills/video-direction/SKILL.md`).
- **Production decision skills & commercial pre-production skills** carry
  exactly two frontmatter keys (`name` and `description`):

```yaml
---
name: video-qa
description: "Visual and technical verification. Use when inspecting generated stills, video contact sheets via view_image, or ffprobe/loudness receipts to classify defects and decide retry versus escalation."
---
```

- **Workflow skills** add `metadata` (`invocation: user`, `kind: workflow`) and
  `disable-model-invocation: true` matching `agents/openai.yaml`:

```yaml
---
name: grilling
description: "Stress-test a video brief, creative fork, or incomplete intent through paced frontier rounds until shared understanding is reached."
disable-model-invocation: true
metadata:
  invocation: user
  kind: workflow
---
```

- **Crisp routing `description`.** Keep `description` to at most two sentences
  naming the observable trigger (`Use when` / `Use for`) and the exact decision
  owned. Keep sibling triggers cleanly distinguishable:
  - *Commercial pre-production:* `ad-references` (dissecting primary spots into
    transferable mechanisms), `ad-concepts` (product-locked orthogonal premises
    and swap test), `ad-script` (three-column timed script, read-aloud budget,
    and mute test), `ad-storyboard` (continuity-locked `S01..SN` shot list,
    focal entry, and test-take checks);
  - *Production decisions:* `higgsfield-cli` (live CLI discovery, model/audio
    selection, `hf_guard.py`), `video-direction` (still/motion prompting,
    anti-IP phrasing, phonetic VO), `video-consistency` (cross-shot reference
    and visual lock), `video-qa` (`qa_media.py`, `view_image` critique, retry
    vs escalate), `video-assembly` (FFmpeg stitching, still animatic, FPS lock,
    audio level law, `-14 LUFS`, stems export).

## Body And Length Budget

- **Hard ceiling: under 300 lines in `SKILL.md`.** Keep `SKILL.md` concise and
  scannable so loading a skill preserves the actor's **Smart Zone**. Move
  verbose examples, model parameter matrices, or filter-graph recipes into
  `references/*.md`.
- **Teach decisions, not boilerplate.** Focus prose on the judgment criteria,
  non-obvious failure modes, and conditions that switch from the default path to
  a specialized alternative.
- **Never duplicate `AGENTS.md` or live schemas.** Unconditional rules
  (authority, `hf_guard.py` mandate, precedence over external skills) live in
  [`AGENTS.md`](../AGENTS.md#authority). Volatile Higgsfield model parameters
  live in `higgsfield model get <jst> --json`; skills teach how to inspect and
  choose, not hardcoded stale flag lists.
- **Graduate mechanical rules to code.** Any check that can be enforced
  deterministically (frontmatter shape, budget math, loudness thresholds, link
  validity) belongs in `scripts/` and [`Makefile`](../Makefile), not prose
  warnings.

## Validation

After adding or modifying any skill under `.agents/skills/`:

1. Run `make check-instructions` to verify directory-to-`name` parity, required
   frontmatter keys, `agents/openai.yaml` (`policy.allow_implicit_invocation:
   false` on workflow skills; `interface` only without `policy` on bundled
   commercial pre-production skills), and `.codex/config.toml` sync.
2. Run `make docs-check` to verify every relative link and `#heading-anchor`
   between `SKILL.md`, `references/*.md`, and `docs/`.
3. Read sibling `description` fields side by side to confirm zero routing
   overlap.
