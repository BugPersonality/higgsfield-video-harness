# Production Ledger V1

`campaigns/<slug>/tasks.md` holds the topological execution DAG, authoritative
artifact pointers, completion oracle, and active global constraints. Detailed
per-unit outcomes, inputs, disjoint writable paths, locks, and validation steps
live in `campaigns/<slug>/tasks/TNN-<slug>.md`. Both are authored in
[Planning](../phases/planning.md), validated mechanically by
`make ledger-check CAMPAIGN=<slug>` (`scripts/check-ledger.py`), and updated
serially by the Root Orchestrator during [Production](../phases/production.md).

## Ledger Index Schema (`tasks.md`)

```markdown
# Tasks: <short campaign deliverable title>

status: draft | ready | blocked | done
Blocked stop: <missing input/decision and owner; omit unless status: blocked>
Intent: intent.md
Treatment: treatment.md
Shotlist: shotlist.json
Completion: <falsifiable observable condition covering master.mp4, stems/, QA receipts, and budget caps>
Global constraints: <pinned budget caps, autonomy mode, fps/aspect lock, shared audio law, carried CONCERNS>

## Tasks

- [ ] T01: Upload product/character references and record upload UUIDs [reference]
  - Depends on: budget-envelope [effect:spend]
  - Packet: tasks/T01-upload-references.md
- [ ] T02: Generate and QA s01 hero still [still]
  - Depends on: T01
  - Packet: tasks/T02-s01-still.md
- [ ] T03: Generate and QA Pilot s01 draft video [pilot]
  - Depends on: T02, user-stills-gate [effect:approve-stills]
  - Packet: tasks/T03-s01-pilot.md
- [ ] T04: Generate and QA s02 draft video [video]
  - Depends on: T03, user-pilot-gate [effect:approve-pilot]
  - Packet: tasks/T04-s02-draft-video.md
- [ ] T05: Generate 15s instrumental score [audio]
  - Depends on: budget-envelope [effect:spend]
  - Packet: tasks/T05-music-score.md
- [ ] T06: Assemble draft cut and run render QA [assembly]
  - Depends on: T03, T04, T05
  - Packet: tasks/T06-assemble-draft.md
- [ ] T07: Visual and delivery review on final master [qa]
  - Depends on: T06 [acceptance]
  - Packet: tasks/T07-delivery-qa.md
```

### Task Shape Tags

Every task carries one explicit bracketed shape tag:

| Shape tag | Purpose |
| --- | --- |
| `[reference]` | Upload local references via `python3 scripts/hf_guard.py upload --campaign <dir> --file <path> --ref-id <id>` or verify Soul Character IDs (`hf_guard.py run --command soul-id`) |
| `[still]` | Generate and QA one shot's keyframe still (`media/stills/sNN-*`, via `hf_guard.py run --command {generate,product-photoshoot}`) |
| `[audio]` | Generate and QA voiceover (`qa_media.py voice`) or music/SFX stem (`media/audio/*`) |
| `[pilot]` | Generate and QA Wave 2 Risk-First Pilot shot(s) (`test_take_check != null`, or default `s01`) to validate risky failure modes, motion, and `continuity_lock` before parallel batching |
| `[video]` | Generate and QA one shot's draft or final motion clip (`media/shots/sNN-*`) |
| `[assembly]` | Run `scripts/assemble.sh` and `scripts/qa_media.py render` to emit `draft_cut.mp4` or `master.mp4` + `stems/` |
| `[qa]` | Fresh `reviewer-agent` Visual Critic, Delivery Review, or optional `brain_activity` Virality Predictor scoring |

## Stage And Gate Syntax

Dependencies in `Depends on:` use three exact forms:

- **Execution dependency (`T01`):** unannotated task ID gates starting the
  downstream task until `T01` finishes its bounded work and verified receipts
  are reconciled by the Root Orchestrator.
- **Acceptance dependency (`T01 [acceptance]`):** gates final assembly,
  delivery review, or promotion on full acceptance (including Visual Critic
  `PASS`) of `T01`.
- **Effect / human checkpoint gate (`<name> [effect:<action>]`):** blocks
  execution until the named authority or requester approval is explicitly
  satisfied:
  - `budget-envelope [effect:spend]` — satisfied by `intent.md` at `status: ready`
    with valid `Draft cap`, `Final cap`, and `Max auto-retries/shot`.
  - `user-stills-gate [effect:approve-stills]` — required in `checkpointed` mode
    between Wave 1 Stills QA and Wave 2 Pilot generation.
  - `user-pilot-gate [effect:approve-pilot]` — required in `checkpointed` mode
    between Wave 2 Pilot `s01` + VO QA and Wave 3 parallel video generation.
  - `user-draft-gate [effect:approve-draft]` — required between Draft Cut
    review (`draft_cut.mp4`) and `1080p` Final Pass rendering inside `Final cap`.

## Task Packet Schema (`tasks/TNN-<slug>.md`)

Every task packet MUST contain all **9 required H2 sections** in clear,
self-contained form so a fresh `worker-agent` (`fork_turns: "none"`) can
execute with zero chat history:

```markdown
# TNN — <one-line observable outcome>

## Outcome
<Concrete deliverable produced by this packet and what proves it succeeded.>

## Depends on
<Exact match to tasks.md `Depends on:` targets and stage/effect annotations, or `none`.>

## Sources
<Exact paths to authoritative inputs (`intent.md`, `style-bible.md`, `shotlist.json`, `prompts/sNN_*.txt`, upstream media/reference paths).>

## Provides
<Artifacts, receipts, job IDs, or contact sheets handed back to the Root Orchestrator for downstream consumers.>

## Boundary
<Explicit inclusions, exclusions, credit phase (`draft` or `final`), `Max auto-retries/shot` limit, and stop triggers (`NEEDS_PARENT`).>

## Mutable owners
<Disjoint filesystem paths this worker alone may create or modify (for example `campaigns/<slug>/media/shots/s02-*`, `campaigns/<slug>/qc/s02-*`). Never includes `tasks.md` or `shotlist.json`.>

## Exclusive locks
<Shared serialized resources touched indirectly (for example `campaigns/<slug>/receipts.jsonl` via `scripts/hf_guard.py` file lock, or `none`).>

## Final validation
<Exact local commands run before returning (`python3 scripts/qa_media.py clip ... --sheet ...`, `make qa-voice`, `make qa-render`, etc.) plus required reviewer check.>

## Reopen if
<Objective condition that invalidates this task's output or requires upstream escalation (for example `BUDGET_CAP`, `POLICY_BLOCK`, or `INTENT_GAP`).>
```

## Runtime State And Mechanical Verification

- **Single-writer ledger rule:** only the Root Orchestrator updates `[ ]` →
  `[x]` in `tasks.md`, records `status: ready | blocked | done`, and reconciles
  selected paths/job IDs into `shotlist.json`. Workers route all paid calls and
  uploads through `scripts/hf_guard.py` (`preflight`, `run --command
  {generate,product-photoshoot,soul-id}`, `upload`) which writes
  reservation-before-submit (`status: "reserved"`, `reservation_id`) and
  terminal entries (`completed` / `download_failed` / `rejected` /
  `in_progress`) into `receipts.jsonl`, and return structured results with exact
  output paths, `job_id`/`upload_id`, `receipts.jsonl` entry reference, and
  `qa_media.py` JSON + contact-sheet paths.
- **Mechanical gate (`make ledger-check CAMPAIGN=<slug>`):** runs
  `python3 scripts/check-ledger.py campaigns/<slug>` to verify:
  1. H1 matches `# Tasks: <title>`, valid `status` (`ready`/`done` requires
     upstream `intent.md` at `status: ready`), required header locators
     (`Intent`, `Shotlist`, `Completion`), and valid shape tags;
  2. every task in `tasks.md` links to an existing `tasks/TNN-*.md` packet with
     matching H1 task ID, all 9 required H2 sections, and identical `Depends on`
     tokens;
  3. DAG acyclicity, valid topological wave computation, and the domain
     invariant that every `[video]` or `[pilot]` task depends (directly or
     transitively) on at least one `[still]` or `[reference]` task;
  4. zero overlapping `Mutable owners` among tasks in the same parallel wave
     (shared `Exclusive locks` such as `receipts.jsonl` serialize lock access
     and never waive disjoint `Mutable owners`);
  5. `shotlist.json` `schema_version: 1`, prompt files on disk, valid
     `start_image_from`/`end_image_from` references (`<shot_id>.still`,
     `<shot_id>.last_frame`, or declared `references[]` IDs), valid
     `continuity_lock`/`test_take_check` objects when present, and enabled
     draft/final credit estimates within `intent.md`'s `Draft cap` and
     `Final cap`.
- **Completion rule:** flip `tasks.md` to `status: done` ONLY when every
  required task is `[x]`, `media/exports/master.mp4` + `stems/` pass
  `make qa-render`, Final Delivery Review returns `PASS`, and
  `make budget-status CAMPAIGN=<slug>` confirms spend stayed within both caps.
