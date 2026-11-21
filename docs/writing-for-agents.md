# Writing For Agents

Rules for editing `AGENTS.md`, `docs/*.md`, `.agents/roles/*.toml`, and
`.agents/skills/` in this repository. Validate every edit with
`make check-instructions` and `make docs-check`.

## Two Budgets & 3-Layer Progressive Disclosure

- **Context load** is the permanent tax of always-loaded text (`AGENTS.md` and
  model-invoked skill `description` fields). Prune it ruthlessly.
- **Cognitive load** is the human's index of user-invoked skills and docs.
  Spend it only where human agency matters.
- **Strict 3-layer routing:**
  1. **Layer 1 (Always loaded):** `AGENTS.md` (`<= 100` lines; unconditional
     boundaries and pointers only—no model slugs, CLI flags, or deep links into
     `.agents/skills/*/references/`) + concise `SKILL.md` `description` fields
     (`<= 320` chars: leading concept + sharp `Use when` triggers, zero tool
     inventories).
  2. **Layer 2 (Branch-loaded):** `docs/workflow.md` (round mechanics),
     `docs/delegation.md` (subagent/QC protocol), `.agents/roles/*.toml`
     (compact contracts pointing to owning skills—never hardcoded partial CEL
     lists), and `.agents/skills/<name>/SKILL.md` (scannable router + core laws
     under `300` lines).
  3. **Layer 3 (Deep references):** `.agents/skills/<name>/references/*.md`
     loaded exclusively via their owning `SKILL.md` (zero orphan reference files).
- **Sharp context pointers:** a pointer states what the target owns and lists
  one front-loaded trigger per distinct branch (zero synonym fluff). When an
  agent misses a doc, sharpen the pointer wording before inlining prose.

## Canonical Ownership, Leading Words & Pruning

- **One canonical owner per topic (cross-link, never copy-paste):**
  - `video-narrative` → `Narrative Lock`, `BUT / THEREFORE` causal spine,
    per-shot `Narrative job` & Deletion Test, `0.1s` instant-read semiotics,
    `2 + 2` subtext, Blind Viewer Read protocol, non-commercial story arcs.
  - `higgsfield-cli` → Web Unlimited, model benchmarks/pricing, `R4 → R5`
    mastering & Upscale Gate, Web UI vs. CLI boundaries, live CEL traps & recipes.
  - `video-direction` → prompt patterns, optics, camera control/rigs/speedramps,
    model prompt calibration, anti-IP/VO copy, prompt/camera diagnostics.
  - `video-consistency` → `R1B`–`R5` location/building/prop & character/expression
    bibles, reference-count budgets, Soul ID, Motion Control, Intone, continuity
    diagnostics.
  - `video-qa` → `qa_media.py` probes, `1:1` crop inspection, binary QC rubric.
  - `video-assembly` → `R3` still animatics, VO timing, `-14 LUFS` mastering,
    `LUT`/`GRAIN` finishing, stems, Remotion boundary.
- **Co-location & primary sources:** keep related rules in one owning doc rather
  than scattering cross-referenced micro-files, and pass live primary sources
  (human reactions, `brief.md`, `taste-log.md`, probed media) instead of lossy
  handoff summaries.
- **Environment as truth:** `Makefile`, `scripts/* --help`, live `higgsfield`
  CLI schemas, and `campaigns/example-product-spot/` own commands, flags, and
  JSON shapes. Graduate mechanical prohibitions into scripts and tests, then
  delete the prose restatement.
- **Positive prompting:** state the target behavior directly (*"rewrite and
  regenerate overflowing VO"*). Reserve prohibitions for hard guardrails paired
  immediately with the positive target so negation does not prime the banned
  behavior.
- **Leading words & checkable criteria:** repeat compact concepts (`Director`,
  `Dailies`, `Taste Memory`, `LOCKED`, `one-way door`, `fail closed`) instead of
  restating definitions, and end every sequential step or skill with a binary
  `*Done when:*` criterion.
- **No-op test & deletion test:** delete any sentence the model already obeys
  by default, and delete any layer, role, or interface doc that serves only
  hypothetical reuse or duplicates another owner.

## Skill & Role Contracts

Enforced mechanically by `scripts/check-instructions.py`:

- **`AGENTS.md` kernel cap:** `<= 100` lines and zero direct links into
  `.agents/skills/*/references/` (route via the owning `SKILL.md`).
- **Model-invoked decision skills** (`.agents/skills/<name>/SKILL.md`, under
  300 lines): `name` matches directory; `description` (`<= 320` chars) carries
  the leading concept and `Use when` trigger branches; omit
  `disable-model-invocation`; every `references/*.md` file under the skill must
  be linked from `SKILL.md`.
- **User-invoked workflow skills** (`idea-refine`, `grilling`, `studio-retro`):
  set `disable-model-invocation: true` in `SKILL.md` and
  `allow_implicit_invocation: false` in `agents/openai.yaml`; write a concise
  human-facing `description` (`<= 320` chars).
- **Studio & Brand Memory caps** (enforced mechanically by `scripts/check-memory.py`
  / `make memory-lint`): `studio/director.md` `<= 60` lines (private overrides in
  gitignored `studio/director.local.md`), `brands/*/taste.md` `<= 80` lines
  (brand invariants only, zero campaign plot leakage), `studio/engine-memory.md`
  `<= 120` lines (ACE bullets with `helpful`/`harmful`, `verified=YYYY-MM-DD`,
  and 60-day staleness warnings), `studio/evolution-log.md` (`EV-NN` SIM entries
  with `Retire / Revisit when`), and fresh compiled `taste-active.md` (`<= 80`
  lines soft cap) compiled from `taste-log.md` via `make memory-compile`.
- **Roles** (`.agents/roles/*.toml`): every role declares `name` (matching
  filename), `description`, `class` (matching `.agents/role-classes/<class>.md`),
  `output_schema` (with verified `#anchor` in `docs/delegation.md`), and concise
  `instructions`. Keep `.codex/config.toml` synced with
  `.agents/codex-project.toml`.
