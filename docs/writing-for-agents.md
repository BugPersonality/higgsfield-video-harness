# Writing For Agents

Rules for editing `AGENTS.md`, `docs/*.md`, `.agents/roles/*.toml`, and
`.agents/skills/` in this repository. Validate every edit with
`make check-instructions` and `make docs-check`.

## Two Budgets & Context Pointers

- **Context load** is the permanent tax of always-loaded text (`AGENTS.md` and
  model-invoked skill `description` fields). Prune it ruthlessly.
- **Cognitive load** is the human's index of user-invoked skills and docs.
  Spend it only where human agency matters.
- **Sharp context pointers:** a pointer states what the target owns and lists
  one front-loaded trigger per distinct branch (zero synonym fluff). When an
  agent misses a doc, sharpen the pointer wording before inlining prose.

## Hierarchy, Leading Words & Pruning

- **Progressive disclosure:** keep `AGENTS.md` to unconditional boundaries and
  pointers; push round mechanics to `docs/workflow.md`, subagent rules to
  `docs/delegation.md`, and craft decisions to `.agents/skills/<name>/SKILL.md`
  (plus focused `references/*.md` only for non-obvious gotchas).
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
  restating definitions, and end every sequential step with a binary `*Done
  when:*` criterion.
- **No-op test & deletion test:** delete any sentence the model already obeys
  by default, and delete any layer, role, or interface doc that serves only
  hypothetical reuse or duplicates another owner.

## Skill & Role Contracts

Enforced mechanically by `scripts/check-instructions.py`:

- **Model-invoked decision skills** (`.agents/skills/<name>/SKILL.md`, under
  300 lines): `name` matches directory; `description` carries the leading
  concept and `Use when` trigger branches; omit `disable-model-invocation`.
- **User-invoked workflow skills** (`idea-refine`, `grilling`): set
  `disable-model-invocation: true` in `SKILL.md` and `allow_implicit_invocation:
  false` in `agents/openai.yaml`; write a concise human-facing `description`.
- **Roles** (`.agents/roles/*.toml`): every role declares `name` (matching
  filename), `description`, `class` (matching `.agents/role-classes/<class>.md`),
  `output_schema` (with verified `#anchor` in `docs/delegation.md`), and concise
  `instructions`. Keep `.codex/config.toml` synced with
  `.agents/codex-project.toml`.
