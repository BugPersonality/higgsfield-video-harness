# Review

Fresh, adversarial, independent verification across both pre-production
contracts and generated visual/audio media. Every review returns
[Review Result V1](../interfaces/review-result-v1.md).

## Independence And Fresh Context

- **Always fresh (`fork_turns: "none"`).** Dispatch every review to a fresh
  read-only `reviewer-agent` (`reasoning_effort: high`). A builder, phase
  author, or shot `worker-agent` never self-approves its own work.
- **Zero builder narrative anchoring.** Supply strictly:
  1. the fixed candidate (artifact file, still image, `3×2` PNG contact sheet,
     or rendered video + contact sheet);
  2. the authoritative upstream requirements (`intent.md`, `style-bible.md`,
     `shotlist.json`, `brands/<brand>/brand.md`, and `media/references/*`);
  3. objective execution proof (`qa_media.py` JSON receipts, `generate cost`
     outputs, `make intent-check` / `make ledger-check` results).
  **Omit** author rationales, retry stories, self-review assurances, and prior
  chat history so builder framing cannot bias falsification.
- **Read-only boundary.** `reviewer-agent` never edits artifacts, never runs
  paid generations, never performs repairs, and never transitions phase status.
  If required evidence or candidate files are missing, return
  `REVIEW_HANDOFF_INVALID` naming the owner that must fix the handoff.

## Visual Critic Protocol

Every visual deliverable (Wave 1 Stills, Wave 2 Risk-First Pilot, Wave 3
Routine Shots, Draft Cut, and Final Master) passes a two-layer gate:

1. **Deterministic media gate first (`scripts/qa_media.py`).**
   - For stills/clips: `make qa-clip FILE=<path.mp4> SHEET=<qc/sNN-tK-sheet.png>`
     probes resolution, aspect ratio, FPS, duration, audio presence, black
     frames (`>= 0.5 s`), `frozen_tail` (`>= 3.0 s` default via `--max-still`,
     preserving intentional `1.5–2.9 s` closing button holds), and
     `fully_static_clip` (hard error for 100% frozen clips `>= 1.5 s`), and
     generates a `3×2` evenly sampled PNG contact sheet.
   - For voiceover: `make qa-voice FILE=<path.wav> WINDOW=<sec>` checks active
     speech duration using 100ms RMS energy against the shot window.
   - For assembled cuts: `make qa-render FILE=<path.mp4> SHEET=<qc/render-sheet.png>`
     additionally checks master loudness normalized via
     `loudnorm=I=-14:TP=-1.5:LRA=11` — verified at `-14 LUFS (±1.0 LU)` and
     true peak `<= -1.0 dBTP` (targeting `-1.5 dBTP` for headroom) — plus
     full-spot contact sheet frames.
   - If a deterministic `MEDIA_TECH_DEFECT` fails on a single shot, repair or
     regenerate before spending Visual Critic review effort (at Draft/Final
     Delivery, run deterministic QA and Visual Critic together on the fixed
     cut).
2. **Multimodal Visual Critic (`view_image`).**
   - Pass `campaigns/<slug>/media/references/*`, the candidate still or `3×2`
     PNG contact sheet, the `qa_media.py` JSON receipt, `intent.md`,
     `style-bible.md`, and `shotlist.json` (including `continuity_lock` and the
     shot's `test_take_check` when present) to a fresh `reviewer-agent`.
   - `reviewer-agent` inspects the reference images and candidate frames
     directly with Codex `view_image`, auditing:
     - **Continuity Lock (all three invariants):**
       1. *Product:* physical form, finish, scale, label/wordmark facing and
          legibility (`VISUAL_DRIFT_DEFECT`);
       2. *Lighting & palette:* fixed key-light side (`screen left` /
          `screen right` / `overhead` / `back`), light quality, color
          temperature, and hex palette anchors (`CONTINUITY_DEFECT` /
          `VISUAL_DRIFT_DEFECT`);
       3. *Space, cast & axis:* location layout, cast/wardrobe markers, active
          hand, screen direction, and 180-degree axis across adjacent accepted
          shots (`CONTINUITY_DEFECT`);
     - **Risk-shot `test_take_check`:** whenever `shotlist.json` declares
       `test_take_check != null` on the shot, explicitly falsify
       `test_take_check.risk` and verify `test_take_check.pass_check` across
       contact-sheet panels 1–6 (failing with `VISUAL_DRIFT_DEFECT` or
       `CONTINUITY_DEFECT` if the pass check does not clearly hold);
     - hand/limb anatomy, physics weight, temporal morphing across panels 1–6,
       and compliance with every `Must not` rule in `intent.md`
       (`VISUAL_DRIFT_DEFECT` or `INTENT_GAP`).
   - Emit [Review Result V1](../interfaces/review-result-v1.md) citing exact
     contact-sheet panels (`panel 1..6`), `continuity_lock` clauses,
     `test_take_check.pass_check` outcomes, and reference anchors in
     `evidence_boundary`.

## Repair Bounds And Escalation

- **Max 2 bounded repair rounds.** Allow at most **two** repair rounds per
  anchored defect class on one fixed candidate, simultaneously bounded by
  `Max auto-retries/shot` and `Draft cap` / `Final cap` under
  [Budget Authority](budget-authority.md).
- **Verify before repairing.** On `FAIL`, the owning phase or Root Orchestrator
  verifies every finding's citation, `qa_media.py` metric, or contact-sheet
  panel against primary sources. Never self-approve past `FAIL`.
- **Fresh recheck.** After repairing an artifact or regenerating a shot take
  (producing a new `qa_media.py` JSON + contact sheet), dispatch a fresh
  `reviewer-agent` on the repaired candidate. If two repair rounds still fail
  to close the finding or yield no discriminating improvement, stop cycling and
  enter [Parent-Owned Recovery](transition.md#parent-owned-recovery).
- **Conflict escalation (`adjudicator-agent`).** When a genuine evidence-backed
  conflict survives between Visual Critic findings, `intent.md` tie-breakers,
  and remaining credit budget (for example, a minor continuity flaw on the last
  available retry vs `Binding: hard` product fidelity), dispatch one read-only
  `adjudicator-agent` (`reasoning_effort: xhigh`). The adjudicator weighs
  competing evidence strictly against `intent.md` and returns either the
  narrowest defensible disposition or an `INTENT_GAP` / `BUDGET_CAP` blocker
  for the requester.

## Review Route

| Fixed boundary | Phase adapter | Verdict domain |
| --- | --- | --- |
| Draft `intent.md` (before Gate 1) | [Cold-Start Intent Review](../phases/intake.md#cold-start-intent-review) | `PASS \| CONCERNS \| FAIL` |
| `treatment.md` + `style-bible.md` | [Treatment And Style Review](../phases/creative-definition.md#treatment-and-style-review) | `PASS \| CONCERNS \| FAIL` |
| `shotlist.json` + `prompts/*` + budget proof | [Shotlist And Budget Review](../phases/production-design.md#shotlist-and-budget-review) | `PASS \| CONCERNS \| FAIL` |
| `tasks.md` + `tasks/TNN-*.md` + `ledger-check` | [Task Readiness Review](../phases/planning.md#task-readiness-review) | `PASS \| CONCERNS \| FAIL` |
| Stills, Risk-First Pilot, Routine Shot takes | [Visual Critic Protocol](#visual-critic-protocol) | `PASS \| FAIL \| NEEDS_PARENT` |
| Assembled `draft_cut.mp4` / `master.mp4` + `stems/` | [Delivery Review](../phases/production.md#delivery-review) | `PASS \| FAIL \| NEEDS_PARENT` |
