# Workflow Router

Select the smallest non-direct execution path and current decision owner for a
video request. If [`AGENTS.md`](../../AGENTS.md#direct-work) selects
`Direct Work`, stop routing here.

## Terms

| Term | Meaning |
| --- | --- |
| `Direct Work` | Single-owner local execution under [`AGENTS.md`](../../AGENTS.md#direct-work) with no campaign artifacts (`intent.md`, `treatment.md`, `shotlist.json`, `tasks.md`). |
| `Campaign` | One persisted multi-shot video project living under `campaigns/<slug>/` with its own `intent.md`, creative/production specs, spend ledger (`receipts.jsonl`), and gitignored `media/`. |
| `Shot Unit` | One bounded shot (`s01..sN`) or media deliverable (`reference`, `still`, `audio`, `pilot`, `video`, `assembly`, `qa`) mapped to one task packet (`tasks/TNN-*.md`) with disjoint writable paths. |
| `Budget Envelope` | Requester-authorized spending limits recorded in `intent.md` (`status: ready`): `Autonomy mode`, `Draft cap`, `Final cap`, and `Max auto-retries/shot`, enforced mechanically by `scripts/hf_guard.py`. |
| `Autonomy Mode` | Campaign checkpoint policy selected in `intent.md`: `autonomous-draft` (default) or `checkpointed`. |
| `Draft Cut` | Full low-cost assembled preview (`media/exports/draft_cut.mp4`) rendered inside `Draft cap` (stills + `480p`/`720p` or `seedance_2_5 --draft` clips + draft audio) for holistic review before spending `Final cap`. |
| `Master` | Final high-resolution deliverable (`media/exports/master.mp4`, typically `1080p`, `-14 LUFS`, FPS/aspect locked) plus separated `media/exports/stems/` verified by `qa_media.py render` and Delivery Review. |
| `Smart Zone` | Lean working-context envelope where one actor holds one coherent outcome, bounded files, and primary artifacts without attention degradation from prior chat turns or unrelated shot histories. |
| `Ready Frontier` | Set of tasks in `tasks.md` whose upstream `Depends on` prerequisites and `[effect:...]` gates are satisfied and whose `Mutable owners` and `Exclusive locks` are currently free for dispatch. |

## Path Selection

Choose the lightest path that preserves meaning, consistency, and budget safety:

- **`Direct Work`** — single bounded deliverable with clear scope: schema or
  balance lookup, doc/script edit, local `qa_media.py` / `assemble.sh` run on
  existing clips, or one isolated image/test clip after echoing
  `higgsfield generate cost` and obtaining explicit user confirmation.
- **`Structured` (single-owner campaign)** — small 1–2 shot piece where intent,
  visual truth, and budget envelope must survive across turns or a fresh review
  pass, but parallel multi-worker waves are unnecessary. Still enforces
  `intent.md`, `hf_guard.py`, and `qa_media.py`.
- **`Orchestrated` (multi-agent campaign)** — default for any multi-shot
  commercial, launch video, UGC sequence, or branded spot where cross-shot
  consistency, audio/VO sync, competing *Design It Twice* creative options,
  parallel shot rendering, and fresh multimodal Visual Critic QA matter.

Re-route upward immediately if a `Direct Work` exploration expands into multiple
coordinated shots or recurring paid iterations.

## Macro Phases

The Root Orchestrator conducts Phase 0 Intake directly with the requester until
`campaigns/<slug>/intent.md` is confirmed at `status: ready`. Once `intent.md`
is `ready`, the Root Orchestrator coordinates Phases 1–3 in fresh sessions
(`fork_turns: "none"`) and executes Phase 4 waves under
[Transition](shared/transition.md#cross-phase-continuation).

| Phase | Owner | Primary artifacts | Required gate / review |
| --- | --- | --- | --- |
| Phase 0 — Intake | Root Orchestrator + [`Intake`](phases/intake.md) | `campaigns/<slug>/intent.md` (`status: ready`) | `make intent-check`, Cold-Start Intent Review (fresh `reviewer-agent`), **Gate 1** requester confirmation |
| Phase 1 — Creative Definition | Fresh phase owner + [`Creative Definition`](phases/creative-definition.md) | `treatment.md`, `style-bible.md` *(plus `script.md`, `storyboard.md` on the commercial track)* | Commercial track (`[ad-references]` → `ad-concepts` → `ad-script` → `ad-storyboard`) or non-commercial *Design It Twice*, then fresh Treatment & Style Review (`reviewer-agent`) |
| Phase 2 — Production Design | Fresh phase owner + [`Production Design`](phases/production-design.md) | `shotlist.json`, `prompts/*` | Live schema checks (`evidence-agent`), `higgsfield generate cost` ≤ caps, fresh Shotlist & Budget Review |
| Phase 3 — Planning | Fresh phase owner + [`Planning`](phases/planning.md) | `tasks.md`, `tasks/TNN-*.md` | `make ledger-check`, fresh Task Readiness Review (`reviewer-agent`) |
| Phase 4 — Production & Delivery | Root Orchestrator + [`Production`](phases/production.md) + [Agent Harness](../agent-harness.md) | `media/stills/*`, `media/shots/*`, `media/audio/*`, `media/exports/draft_cut.mp4`, `media/exports/master.mp4`, `stems/`, `qc/*.json`, `receipts.jsonl` | Per-wave `qa_media.py` + Visual Critic (`view_image`), autonomy checkpoints, Final Delivery Review |

Traverse phases in order. Skip a phase only when an existing `status: ready`
artifact already closes its decisions with zero invalidated upstream links.

Inside Phase 1 ([Creative Definition](phases/creative-definition.md)), choose
the creative track matching the campaign:

- **Commercial / product track:** `[ad-references]` (optional) → `ad-concepts`
  → `ad-script` → `ad-storyboard`, governed by the shared commercial craft
  vocabulary in [`docs/ad-craft-glossary.md`](../ad-craft-glossary.md), then
  distilled into `treatment.md` and `style-bible.md`.
- **Non-commercial / aesthetic track:** built-in *Design It Twice* (2–3
  competing `specialist-agent` lanes) → `treatment.md` and `style-bible.md`.

## Phase Selection

Evaluate observable triggers before loading a phase owner:

| Observable trigger | Owner |
| --- | --- |
| New campaign lacks a confirmed `intent.md` at `status: ready`, or viewer meaning, brand truth, spoken pronunciation, `Must not`, autonomy mode, or credit cap changed | [Intake](phases/intake.md) |
| `intent.md` is `ready`, but campaign lacks reviewed `treatment.md` and `style-bible.md` (or a visual/narrative direction fork reopened) | [Creative Definition](phases/creative-definition.md) |
| `treatment.md` and `style-bible.md` are `ready`, but `shotlist.json`, live model params, reference graph, prompt files, or `generate cost` budget proof is missing or stale | [Production Design](phases/production-design.md) |
| `shotlist.json` is `ready`, but `tasks.md` and disjoint `tasks/TNN-*.md` packets do not exist or must be resliced after a mid-pipeline reopen | [Planning](phases/planning.md) |
| `tasks.md` is `ready` and passes `make ledger-check`, or an active production wave resumes after a user gate or recovery | [Production](phases/production.md) |

## Autonomy Modes

Selected explicitly by the requester in `intent.md` (`Constraints & boundaries`
→ `Authority & budget envelope`) and encoded as `[effect:...]` gates in
`tasks.md`:

| Mode | Default? | Checkpoints after Gate 1 | Best for |
| --- | --- | --- | --- |
| **`autonomous-draft`** | **Yes (default)** | Runs Waves 1–4 end-to-end inside `Draft cap` (`480p`/`720p` or `seedance_2_5 --draft`) to deliver a complete reviewed `draft_cut.mp4` + contact sheets + QA report, pausing once at `user-draft-gate [effect:approve-draft]` before unlocking `1080p` Finals inside `Final cap`. | Fast end-to-end iteration where the requester prefers reacting to a full edited cut with sound rather than inspecting intermediate frames. |
| **`checkpointed`** | Opt-in | Pauses at **Wave 1 Stills** (and optional Wave 1.5 Still Animatic via `make animatic`, `user-stills-gate [effect:approve-stills]`), **Wave 2 Risk-First Pilot + VO** (`user-pilot-gate [effect:approve-pilot]`), and before `1080p` Finals (`user-draft-gate [effect:approve-draft]` when draft pass precedes finals). | High-stakes brand hero spots, strict face/product likeness verification, or unfamiliar visual styles where early steering saves batch credits. |

Both modes enforce identical `Draft cap`, `Final cap`, `Max auto-retries/shot`,
`hf_guard.py`, `qa_media.py`, and fresh `reviewer-agent` Visual Critic gates.

### Approval Gates

Use consistent gate names across campaign artifacts, tasks, and user updates:

| Gate | Trigger & Artifact | Active in |
| --- | --- | --- |
| **Gate 1 — Intent** | Requester confirms `intent.md` (`status: ready`) and Budget Envelope before Phase 1–4 start | Both modes |
| **Gate 2 — Draft Cut (`autonomous-draft`) / Stills (`checkpointed`)** | In `autonomous-draft`: `user-draft-gate [effect:approve-draft]` on assembled `draft_cut.mp4` + QA report before unlocking `Final cap`. In `checkpointed`: `user-stills-gate [effect:approve-stills]` on Wave 1 Stills (and optional Wave 1.5 Still Animatic). | Both modes (scope varies by mode) |
| **Gate 3 — Pilot + VO** | `user-pilot-gate [effect:approve-pilot]` on Wave 2 Risk-First Pilot + VO before fanning out routine Wave 3 shots (followed by `user-draft-gate [effect:approve-draft]` before `1080p` finals when a draft cut precedes finals) | `checkpointed` only |
| **Gate 4 — Final Master** | Final Delivery Review (`PASS`), `qa_media.py render`, `media/exports/master.mp4` + `stems/`, and `receipts.jsonl` spend audit closing `tasks.md` at `status: done` | Both modes |

## Conditional Shared Owners

Load a shared protocol immediately before its trigger:

| Trigger | Protocol |
| --- | --- |
| Conducting requester interviews or resolving a blocked taste fork | [Grilling](shared/grilling.md) |
| Deciding persistence, Git vs `media/` boundary, or artifact status transitions | [Artifacts](shared/artifacts.md) |
| Running Cold-Start, Treatment, Shotlist, Readiness, Visual Critic, or Delivery review | [Review](shared/review.md) |
| Crossing phase boundaries, emitting `Blocked Exit`, recovering failures/timeouts, or reopening mid-pipeline | [Transition](shared/transition.md) |
| Checking spend authorization, `hf_guard.py` usage, Draft/Final caps, or `receipts.jsonl` | [Budget Authority](shared/budget-authority.md) |
| Applying shared commercial terms (`primary spot`, `swap test`, `mute test`, `Continuity lock`, `test-take check`) | [Ad Skills Glossary](../ad-craft-glossary.md) |
