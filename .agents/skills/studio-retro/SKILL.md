---
name: studio-retro
description: "Post-campaign R6 consolidation (Dream loop): mine raw campaign traces, reconcile contradictions, and propose gated ACE delta patches for studio/, brands/, and skills."
metadata:
  invocation: user
  kind: workflow
disable-model-invocation: true
---

# Studio Retro (`R6` — Consolidation / Dream Loop)

Turn a finished campaign's raw execution traces, review defects, prompt diffs, and `taste-log.md` flips into durable cross-campaign learning without context collapse or memory poisoning.

## 4-Phase Consolidation Protocol

1. **Harvest (0 LLM tokens):** Run `make retro-harvest CAMPAIGN=<slug>` and `make memory-lint`. Inspect the harvested report alongside `campaigns/<slug>/taste-log.md`, `taste-active.md`, and the exact `prompts/` files for any asset that bumped to `v2+` (compare failed `v1` against winning `vN`).
2. **Reflect (Read-Only Root-Cause Triage):** Classify every surfaced lesson into one bucket — discard one-off campaign plot details immediately:
   - *Director workflow/communication preference* → `studio/director.md` (`<= 60` lines)
   - *Cross-campaign brand taste invariant* → `brands/<brand>/taste.md` (`<= 80` lines; check for contradictions with older lines and remove superseded campaign plots)
   - *Model / channel empirical behavior* → `studio/engine-memory.md` (`<= 120` lines; ACE bullet `[ENG-NN]` with `helpful`/`harmful` counter bump, absolute `verified=YYYY-MM-DD`, and `Evidence:`)
   - *Recurring technical defect (`>= 2` campaigns or verified mechanical failure in `qa_media.py` / live CLI)* → graduate directly into `scripts/` or the single owning `.agents/skills/<owner>/` doc, mark the engine bullet `status=graduated_to_code`, and log `### EV-<NN>` with a `Retire / Revisit when` condition in `studio/evolution-log.md`.
3. **Curate (ACE Atomic Deltas Only):** Never ask an LLM to rewrite a long-term memory file from scratch. Apply surgical deltas (`ADD`, `SUPERSEDE`, `BUMP_COUNTER`, `PRUNE`), replace any relative time words with `YYYY-MM-DD`, and cite exact campaign provenance (`src: <slug>#TL-NN`). If an older `EV-NN` rule's `Retire / Revisit when` condition is met, propose deleting it.
4. **Verify & Gate (One-Way Door):** Run `make check` (`check-instructions`, `docs-check`, `memory-lint`, `shellcheck`, `test`) and present **one compact Retro Dailies Diff** (Added / Updated / Superseded / Graduated to Code / Retired) for explicit Director approval before finalizing.

*Done when:* `make check` passes with zero errors, `taste-active.md` is fresh, stale or contradictory memory entries are reconciled, and the Director explicitly approves every long-term memory or harness diff.
