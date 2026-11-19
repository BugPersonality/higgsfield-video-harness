# Agent Harness

Harness-neutral native delegation and durable execution controls for the
**Director (Human) ↔ Production Crew (Agents)** feedback-loop film studio.
[`AGENTS.md`](../AGENTS.md) owns authority and spending walls; the
[Workflow Router](video-workflow/router.md) and its rounds (`R0`–`R5`) own why a
control applies; the selected adapter owns how the host harness provides it.

## Delegation Interface

Brief every delegated lane inside the active round with its checkable outcome,
authoritative input locators (`brief.md`, `taste-log.md`, `style-bible.md`,
`shotlist.json`), disjoint writable paths (when mutating), and stop boundary
without copying repository-wide policy. Keep every actor inside the **Smart
Zone**: one coherent outcome, bounded files, and primary artifacts—never
sprawling prior chat transcripts or unrelated shot histories.

- **Round-scoped disjoint ownership, not Git worktrees.** Video generation
  produces large gitignored binaries and shares one campaign spend ledger, so
  parallel mutable lanes share a single repository checkout under strict path
  partitioning per Lookbook entity or shot:
  - Lookbook workers (`R2`): `campaigns/<slug>/media/lookbook/<id>-*`,
    `campaigns/<slug>/prompts/<id>_*`, `campaigns/<slug>/qc/<id>-*` (Lookbook
    IDs already begin with `lb_`, e.g., `prompts/lb_traveler_v1.txt`).
  - Keyframe still workers (`R3`): `campaigns/<slug>/media/stills/sNN-*`,
    `campaigns/<slug>/prompts/sNN_still_*`, `campaigns/<slug>/qc/sNN-still-*`.
  - Motion workers (`R4`–`R5`): `campaigns/<slug>/media/shots/sNN-*`,
    `campaigns/<slug>/prompts/sNN_video_*`, `campaigns/<slug>/qc/sNN-*`.
  - Audio workers (`R3`–`R5`): `campaigns/<slug>/media/audio/*`,
    `campaigns/<slug>/qc/audio-*`.
  - Assembly workers (`R3`–`R5`): `campaigns/<slug>/media/exports/*`,
    `campaigns/<slug>/qc/render-*` / `campaigns/<slug>/qc/master-*`.
- **Root Producer single-writer ownership.** Only the Root Producer mutates
  `campaigns/<slug>/brief.md`, `campaigns/<slug>/taste-log.md`, and
  `campaigns/<slug>/shotlist.json` (including `upload_id`, `approved_variant`,
  `approved_upload_id`, `selected_take`, `selected_job_id`, `status`, and
  `version`). Subagents never edit brief, taste memory, or shotlist state.
- **Serialized spend & lock guard.** Every paid Higgsfield generation and
  tracked upload executes through `python3 scripts/hf_guard.py` with `--round`
  and `--round-cap`. `hf_guard.py` enforces `Campaign cap`, `--round-cap`,
  `Max auto-retries/asset`, `LOCKED` asset immutability (`asset_locked`), and
  an exclusive file lock on `campaigns/<slug>/receipts.jsonl` under
  [Budget Authority](video-workflow/shared/budget-authority.md).
- **Internal defect filter ≠ Director approval.** Fresh read-only
  `reviewer-agent` lanes (`fork_turns: "none"`) filter technical AI defects,
  continuity breaks, and `taste-log.md` regressions BEFORE assembling each
  round's [Dailies Packet](video-workflow/interfaces/dailies-packet-v1.md).
  `reviewer-agent` NEVER chooses among clean creative options, NEVER marks an
  asset `LOCKED`, and NEVER substitutes for human Director approval.
- **Slot accounting.** Count every open subagent in the session tree
  (`worker-agent`, `evidence-agent`, `specialist-agent`, `reviewer-agent`,
  `adjudicator-agent`) against adapter concurrency capacity, always reserving
  slots for internal Visual Critic filtering and recovery lanes so a parallel
  round cannot deadlock QC.
- **Recovery ownership.** Trigger
  [Parent-Owned Recovery](video-workflow/shared/transition.md#parent-owned-recovery)
  on native failure, `hf_guard.py` refusal (`NEEDS_PARENT`), `POLICY_BLOCK`,
  `asset_locked`, or repeated uninformative takes—never on quiet multi-minute
  render time. Before replacing a worker or retrying a timed-out job, preserve
  partial artifacts, reconcile `higgsfield generate list --json` and
  `receipts.jsonl`, and confirm descendant termination natively.

## Context And Lifetime

Every delegated lane starts with fresh history (`fork_turns: "none"` where
supported). A fresh actor receives project instructions plus a bounded brief
naming its round unit, accepted input files (`brief.md`, `taste-log.md`,
relevant references), writable paths (if mutable), and output contract—never
prior Root Producer chat turns or builder rationales.

| Actor | Role carrier | Lifetime | History boundary |
| --- | --- | --- | --- |
| Root Producer | Root session | Entire campaign (`R0`–`R5`); single writer of `brief.md`, `taste-log.md`, `shotlist.json`, and all Director **Dailies Packets** | Retains Director conversation for meaning, taste synthesis, and round cost sign-off |
| Evidence Lane | [`evidence-agent`](../.agents/roles/evidence-agent.toml) | One bounded read-only lookup (account/workspace, `brands/`, local photos, live CLI schemas, per-round `generate cost`, `ffprobe`/`receipts.jsonl`) | Fresh (`fork_turns: "none"`); never spends credits or makes taste choices |
| Creative / Craft Specialist | [`specialist-agent`](../.agents/roles/specialist-agent.toml) | One contrasting concept/treatment lane (`R1A`), script/storyboard/style-bible craft brief (`R1B`), prompt engineering, or anti-IP rewrite | Fresh (`fork_turns: "none"`); strictly read-only; reads `brief.md` + `taste-log.md` |
| Production Worker | [`worker-agent`](../.agents/roles/worker-agent.toml) | One Lookbook entity, shot still/clip, audio stem, or assembly unit inside its round's approved `--round-cap` | Fresh (`fork_turns: "none"`); disjoint asset paths only; routes all spend via `hf_guard.py` |
| Internal QC Filter | [`reviewer-agent`](../.agents/roles/reviewer-agent.toml) | One pre-Dailies visual/technical audit (Lookbook variants, stills, `3×2` contact sheets, renders) | Fresh (`fork_turns: "none"`); zero builder rationale; filters noise, never replaces Director taste |
| Conflict Adjudicator | [`adjudicator-agent`](../.agents/roles/adjudicator-agent.toml) | One surviving conflict between internal QC findings, `taste-log.md`, and remaining round budget | Fresh (`fork_turns: "none"`); read-only; never hides defects from Dailies |

- **Reuse vs. respawn.** Reuse an active `worker-agent` only for bounded repair
  inside its unchanged asset unit, writable paths, round cap, and effort tier;
  stop it once its receipt is reconciled. When Director feedback changes the
  asset target (`version` bump), narrows writable scope, escalates effort tier,
  or requires independent QC, stop the old child, reconcile its outputs and
  receipts, and spawn a fresh actor.
- **Targeted delta updates.** If a mid-round check adjusts an input for one
  active worker inside its unchanged writable scope, message only that worker
  directly rather than broadcasting to unaffected asset lanes.

## Model And Effort Tiering

Pass model and reasoning effort in native tool fields and match capability to
judgment ambiguity, spend risk, and interacting visual/narrative invariants.
Project role definitions live under [`.agents/roles/`](../.agents/roles) and
share base contracts in [`.agents/role-classes/`](../.agents/role-classes).

| Role | Default effort | Primary workload |
| --- | --- | --- |
| [`evidence-agent`](../.agents/roles/evidence-agent.toml) | `low` | Live Higgsfield CLI schema/voice/cost quotes per round, balance/workspace check, `brands/` and reference inventory, `ffprobe`/`receipts.jsonl` audit |
| [`worker-agent`](../.agents/roles/worker-agent.toml) | `medium` | Single Lookbook entity, still, video, or audio job via `hf_guard.py`, `qa_media.py` probes, `make lookbook`, `make animatic`, `make assemble` |
| [`specialist-agent`](../.agents/roles/specialist-agent.toml) | `high` | Orthogonal `ad-concepts` pitches, 3-column scripts, continuity-locked storyboards, contrasting Lookbook briefs, complex motion prompting, anti-IP rewrites |
| [`reviewer-agent`](../.agents/roles/reviewer-agent.toml) | `high` | Pre-Dailies Visual Critic (`view_image`) defect, `continuity_lock`, `test_take_check`, and `TASTE_REGRESSION` filtering |
| [`adjudicator-agent`](../.agents/roles/adjudicator-agent.toml) | `xhigh` | Resolving surviving conflicts between internal QC findings, `brief.md` / `taste-log.md`, and remaining round budget |

Raise effort when signals conflict or a failed take exposes a missed visual,
physics, or taste invariant, retaining the higher tier through repair. Honor
explicit user-selected models within their requested scope. Never use a higher
effort tier as a substitute for missing schema facts, missing `qa_media.py`
probes, or a bypassed `hf_guard.py` check.

## Subagent Output Envelopes

Every role in [`.agents/roles/`](../.agents/roles) declares a named
`output_schema` so the Root Producer parses results deterministically without
chat archaeology. (`reviewer-agent` returns
[Review Result V1](video-workflow/interfaces/review-result-v1.md).)

### Evidence Result V1

Returned by [`evidence-agent`](../.agents/roles/evidence-agent.toml):

```text
question: <exact read-only discovery question answered>
commands_run: <exact CLI or probe commands executed>
locators: <file paths, brand/taste paths, model/workflow IDs, or receipt ranges>
findings: <exact JSON excerpts, live generate cost figures per round, or media metrics>
gaps: <none | exact missing file, unauthenticated workspace, or unavailable schema field>
```

### Specialist Result V1

Returned by [`specialist-agent`](../.agents/roles/specialist-agent.toml):

```text
discipline_or_angle: <concept engine | script | storyboard | lookbook contrast | prompt repair | anti-IP rewrite>
taste_anchors_applied: <TL-NN IDs and LOCKED asset IDs honored>
proposal: <concrete creative option(s), script/storyboard draft, or prompt text>
tradeoffs_accepted: <what visual, pacing, or cost trade-off this proposal makes>
blocker_or_gap: <none | exact missing brief.md truth or upstream asset gap>
```

### Worker Result V1

Returned by [`worker-agent`](../.agents/roles/worker-agent.toml):

```text
round: <R2 | R3 | R4A | R4B | R5>
asset_id: <lookbook id | sNN.still | sNN.video | audio.music | audio.voiceover | export>
status: DONE | NEEDS_PARENT
outputs: <exact media, prompt, and QC file paths written inside assigned disjoint scope>
receipts: <reservation_id, job_id or upload_id, estimated_credits, actual_credits, attempt>
qa_summary: <scripts/qa_media.py JSON summary and contact-sheet / lookbook PNG path, or n/a for upload>
blocker: <none | BUDGET_CAP | asset_locked | POLICY_BLOCK | retry_cap_exhausted | exact error>
```

### Adjudication Result V1

Returned by [`adjudicator-agent`](../.agents/roles/adjudicator-agent.toml):

```text
conflict: <exact internal QC finding vs remaining round budget or taste-log trade-off>
evidence_weighed: <review-result-v1 anchors, qa_media.py metrics, receipts.jsonl remaining round headroom>
policy_anchors: <brief.md Must not / tie-breakers and taste-log.md TL-NN rules>
disposition: <retry_within_round_cap | surface_in_dailies_with_concern | pause_for_director_decision>
reopen_owner: <Worker(<asset_id>) | Root Producer | none>
```

## Nested Execution

Each delegating parent owns its subtree: retain child identities, assign
disjoint writable paths (never mutated concurrently by the parent), integrate
receipts serially into `shotlist.json` and `taste-log.md`, and join or stop
descendants before compiling the round's Dailies Packet.

- Production `worker-agent` lanes are leaf executors: they never spawn child
  agents, never touch `LOCKED` assets, never edit `brief.md` / `taste-log.md` /
  `shotlist.json`, never self-approve visual QA, and return `NEEDS_PARENT`
  immediately if `hf_guard.py` refuses on `Campaign cap`, `--round-cap`,
  `Max auto-retries/asset`, or `asset_locked`.
- Never mix control planes inside one campaign (for example, triggering paid
  renders from both CLI workers and ad-hoc MCP calls).

## Select One Adapter

| Current harness | Adapter |
| --- | --- |
| Codex App or Codex CLI (Multi-Agent V2) | [Codex](agent-harness/codex.md) |

All adapters preserve identical [Authority](../AGENTS.md#authority), disjoint
asset ownership, [Budget Authority](video-workflow/shared/budget-authority.md),
[Feedback Loop](video-workflow/shared/feedback-loop.md),
[Review](video-workflow/shared/review.md), and
[Transition](video-workflow/shared/transition.md) semantics. If a required
native capability (such as `view_image` multimodal inspection or fresh-context
subagents) is unavailable in the active host, report the capability gap rather
than skipping internal Visual Critic filtering or collapsing fresh review into
the builder thread.
