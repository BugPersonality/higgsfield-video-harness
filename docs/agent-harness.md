# Agent Harness

Harness-neutral native delegation and durable execution controls for agentic
video production. [`AGENTS.md`](../AGENTS.md) owns authority and spending walls;
the [Workflow Router](video-workflow/router.md) and its phases own why a control
applies; the selected adapter owns how the host harness provides it.

## Delegation Interface

Brief every delegated lane with its checkable outcome, authoritative input
locators, writable scope (when mutating), and stop or proof boundary without
copying repository-wide policy. Keep each actor inside the **Smart Zone**: one
coherent outcome, bounded files, and primary artifacts—never sprawling prior
chat transcripts or unrelated shot histories.

- **Disjoint shot ownership, not Git worktrees.** Video generation produces
  large gitignored binaries and shares a single campaign spend ledger, so
  parallel mutable lanes share one repository checkout under strict path
  partitioning instead of creating Git worktrees:
  - Parallel shot workers write strictly inside their assigned shot paths:
    `campaigns/<slug>/media/stills/sNN-*`, `campaigns/<slug>/media/shots/sNN-*`,
    `campaigns/<slug>/prompts/sNN_*`, and `campaigns/<slug>/qc/sNN-*`.
  - **Root Orchestrator single-writer ownership.** Only the Root Orchestrator
    mutates `campaigns/<slug>/tasks.md` and `campaigns/<slug>/shotlist.json`
    (recording `upload_id`, `selected_take`, `selected_job_id`, `selected_path`,
    and task completion state). Workers never edit ledger or manifest files.
  - **Serialized spend ledger.** Every paid Higgsfield generation runs through
    `python3 scripts/hf_guard.py`, which serializes writes to
    `campaigns/<slug>/receipts.jsonl` with an exclusive file lock under
    [Budget Authority](video-workflow/shared/budget-authority.md).
- **Slot accounting.** Count every active subagent in the session tree
  (production workers, evidence lanes, visual reviewers, and adjudication lanes)
  against adapter concurrency capacity, always reserving slots for Visual Critic
  review and recovery lanes so a full shot wave cannot deadlock review.
- **Recovery ownership.** Trigger
  [Parent-Owned Recovery](video-workflow/shared/transition.md#parent-owned-recovery)
  on native failure, budget/retry refusal (`NEEDS_PARENT`), policy block, or
  repeated uninformative takes—never on quiet multi-minute render time. Before
  replacing a worker or retrying a timed-out job, preserve partial artifacts,
  reconcile `higgsfield generate list --json` and `receipts.jsonl`, and confirm
  descendant termination natively.

## Context And Lifetime

Every delegated lane starts with fresh history (`fork_turns: "none"` where
supported). A fresh actor receives project instructions plus a bounded brief
naming its phase or packet, accepted input files, writable paths, and expected
result—excluding prior coordinator chat turns, earlier phase deliberations, and
builder rationale.

| Actor | Role carrier | Lifetime | History boundary |
| --- | --- | --- | --- |
| Root Orchestrator | Root session | Entire campaign (`Intake` through `Delivery`); owns `intent.md`, `tasks.md`, and `shotlist.json` | Retains user conversation for meaning and checkpoints |
| Preparation Phase Owner | Fresh subagent (`fork_turns: "none"`) | One macro phase (`Creative Definition`, `Production Design`, or `Planning`) including its repairs | Fresh per phase; reads only `status: ready` upstream artifacts |
| Evidence Lane | `evidence-agent` | One bounded read-only lookup (`model get`, `voices list`, `generate cost`, asset/receipt audit) and tightly related follow-ups | Fresh (`fork_turns: "none"`); never spends credits |
| Creative / Craft Specialist | `specialist-agent` | One *Design It Twice* creative lane or one bounded craft brief (prompting, consistency, phonetic VO, anti-IP) | Fresh (`fork_turns: "none"`); strictly read-only |
| Production Worker | `worker-agent` | One task packet (`TNN`) and its bounded in-shot retries within `Max auto-retries/shot` | Fresh (`fork_turns: "none"`); disjoint shot paths only |
| Independent Reviewer | `reviewer-agent` | One fixed review boundary (Cold-Start Intent, Treatment, Shotlist, Readiness, Visual Critic, or Delivery) | Fresh (`fork_turns: "none"`); zero builder narrative |
| Conflict Adjudicator | `adjudicator-agent` | One surviving evidence-backed conflict (e.g., visual defect vs remaining credit cap) | Fresh (`fork_turns: "none"`); read-only |

- **Reuse vs. respawn.** Reuse an active `worker-agent` only for bounded repair
  inside its unchanged shot packet, writable paths, and capability tier; stop it
  once its receipt is reconciled. When a change alters the shot outcome, narrows
  writable scope, changes model/effort tier, or requires independent judgment,
  stop the old child, reconcile its outputs and receipts, and spawn a fresh
  actor.
- **Targeted delta updates.** If a mid-wave decision updates an input for one
  active child inside its unchanged outcome and writable scope, message only
  that affected child directly with the decision delta and updated locator
  rather than broadcasting to unaffected shot lanes.

## Model And Effort Tiering

Pass model and reasoning effort in native tool fields and match capability to
judgment ambiguity, spend risk, and interacting visual/narrative invariants.
Project role definitions live under [`.agents/roles/`](../.agents/roles) and
share base contracts in [`.agents/role-classes/`](../.agents/role-classes).

| Role | Default effort | Primary workload |
| --- | --- | --- |
| [`evidence-agent`](../.agents/roles/evidence-agent.toml) | `low` | Live Higgsfield CLI schema/voice/cost lookups, workspace checks, `ffprobe` / `receipts.jsonl` reduction |
| [`worker-agent`](../.agents/roles/worker-agent.toml) | `medium` | Single-packet generation via `hf_guard.py`, `qa_media.py` execution, contact-sheet creation, FFmpeg assembly |
| [`specialist-agent`](../.agents/roles/specialist-agent.toml) | `high` | *Design It Twice* creative treatments, style grammar, complex multi-reference motion prompting, anti-IP sanitization |
| [`reviewer-agent`](../.agents/roles/reviewer-agent.toml) | `high` | Cold-Start Intent Review, Treatment/Shotlist/Readiness review, Visual Critic (`view_image`), Final Delivery Review |
| [`adjudicator-agent`](../.agents/roles/adjudicator-agent.toml) | `xhigh` | Resolving surviving conflicts between QA findings, `intent.md` tie-breakers, and credit ceilings |

Raise effort when signals conflict or a failed take exposes a missed visual or
continuity invariant, retaining the higher tier through repair. Honor explicit
user-selected models within their requested scope. Never use a higher effort
tier as a substitute for missing schema facts, missing `qa_media.py` probes, or
a bypassed budget guard.

## Subagent Output Envelopes

Every role in [`.agents/roles/`](../.agents/roles) declares a named
`output_schema` so parent actors parse results deterministically without chat
archaeology:

| Schema | Role | Required fields |
| --- | --- | --- |
| `evidence-result-v1` | `evidence-agent` | `question`, `commands_run`, `locators`, `findings` (exact JSON excerpts / metrics), `gaps` (`none` or exact missing source) |
| `specialist-result-v1` | `specialist-agent` | `discipline_or_pressure`, `proposal` ([Candidate Proposal V1](video-workflow/interfaces/treatment-v1.md#candidate-proposal-v1) or bounded craft artifact), `tradeoffs_accepted`, `blocker_or_gap` (`none` or upstream gap) |
| `worker-result-v1` | `worker-agent` | `task_id`, `status` (`DONE \| NEEDS_PARENT`), `outputs` (exact media/prompt/QC paths), `receipts` (`reservation_id`, `job_id`/`upload_id`, `credits`, `attempt`), `qa_summary` (`qa_media.py` JSON + contact-sheet path), `blocker` (`none` or exact refusal/defect) |
| `review-result-v1` | `reviewer-agent` | Canonical [Review Result V1](video-workflow/interfaces/review-result-v1.md): `candidate`, `verdict`, `findings`, `evidence_boundary`, `reopen_owner` |
| `adjudication-result-v1` | `adjudicator-agent` | `conflict`, `evidence_weighed`, `intent_anchors` (`I<n>` / tie-breakers), `disposition` (narrowest binding resolution or `INTENT_GAP` / `BUDGET_CAP` blocker), `reopen_owner` |

## Nested Execution

Each delegating parent owns its subtree: retain child identities, assign
disjoint writable paths (never mutated concurrently by the parent), integrate
receipts serially into `shotlist.json` and `tasks.md`, and join or stop
descendants before closing a wave or releasing scope.

- Preparation phase owners may dispatch read-only `evidence-agent`,
  `specialist-agent`, and `reviewer-agent` descendants directly when native
  nesting permits; if a host harness restricts nesting depth, the Root
  Orchestrator dispatches the bounded read-only lane on the phase owner's behalf
  and relays the raw result without substituting its own judgment.
- Production `worker-agent` lanes are leaf executors: they never spawn child
  agents, never self-approve visual QA, and return `NEEDS_PARENT` immediately
  when `hf_guard.py` refuses on budget or retry cap or when an upstream artifact
  is invalid.
- Never mix control planes inside one campaign (for example, triggering paid
  renders from both CLI workers and ad-hoc MCP calls).

## Select One Adapter

| Current harness | Adapter |
| --- | --- |
| Codex App or Codex CLI (Multi-Agent V2) | [Codex](agent-harness/codex.md) |

All adapters preserve the exact same [Authority](../AGENTS.md#authority),
disjoint shot ownership, [Budget Authority](video-workflow/shared/budget-authority.md),
[Review](video-workflow/shared/review.md), and
[Transition](video-workflow/shared/transition.md) semantics. If a required
native capability (such as `view_image` multimodal inspection or fresh-context
subagents) is unavailable in the active host, report the capability gap rather
than skipping Visual Critic QA or collapsing fresh review into the builder
thread.
