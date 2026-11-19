# Phase 3 — Planning

Use once `shotlist.json` and `prompts/*` have cleared Phase 2 review and the
campaign needs a ready [Production Ledger V1](../interfaces/task-ledger-v1.md)
(`campaigns/<slug>/tasks.md` + `campaigns/<slug>/tasks/TNN-*.md`), or when a
mid-pipeline reopen requires reslicing invalidated tasks. Runs in a fresh phase
session (`fork_turns: "none"`) with zero prior chat history.

## Steps

1. **Slice `shotlist.json` into a topological DAG and disjoint task packets.**
   - Author `campaigns/<slug>/tasks.md` (`status: draft`, `# Tasks: <title>`)
     and one packet `campaigns/<slug>/tasks/TNN-<slug>.md` per task containing
     all **9 required H2 sections** (`Outcome`, `Depends on`, `Sources`,
     `Provides`, `Boundary`, `Mutable owners`, `Exclusive locks`,
     `Final validation`, `Reopen if`).
   - Use exact task shape tags (`[reference]`, `[still]`, `[audio]`, `[pilot]`,
     `[video]`, `[assembly]`, `[qa]`) and obey the structural domain invariant
     enforced by `scripts/check-ledger.py`:
     - every `[pilot]` or `[video]` task MUST depend (directly or transitively)
       on at least one `[still]` or `[reference]` task.
   - **Wave 1.5 (optional 0-video-credit Still Animatic):** when pacing, beat
     durations, or the **mute test** benefit from early verification before
     spending video credits, schedule an optional `[assembly]` animatic task
     (`make animatic CAMPAIGN=<slug>` / `scripts/assemble.sh --animatic`) after
     Wave 1 Stills (and VO/music if ready) to produce
     `media/exports/animatic.mp4` with zero video spend.
   - **Wave 2 (Risk-First Pilot prioritization):** schedule any shots carrying
     `test_take_check != null` in `shotlist.json` as `[pilot]` task(s) in Wave
     2 (`480p`/`720p` or `seedance_2_5 --draft`) so risky grip, physics, text,
     reflection, or blocking failure modes are proven BEFORE committing batch
     credits to routine shots in Wave 3. When no shot carries
     `test_take_check`, keep `s01` as the default Wave 2 `[pilot]`.
   - Partition `Mutable owners` strictly across parallel tasks in the same wave
     so concurrent `worker-agent` lanes never collide on disk:
     - per-shot tasks own only `media/stills/sNN-*`, `media/shots/sNN-*`,
       `prompts/sNN_*`, and `qc/sNN-*`;
     - never list `tasks.md` or `shotlist.json` in a worker's `Mutable owners`
       (those remain single-writer owned by the Root Orchestrator);
     - list `receipts.jsonl` under `Exclusive locks` (serialized by
       `scripts/hf_guard.py`) when parallel tasks submit paid jobs, or serialize
       only genuinely conflicting outputs.
   - Carry active `Global constraints` from `intent.md`, `style-bible.md`, and
     any forwarded Phase 1/2 `CONCERN`s (caps, autonomy mode, FPS/aspect lock,
     raw-clip `NO MUSIC` rule, Git vs `media/` boundary).

2. **Bind `[effect:...]` gates strictly to `Autonomy mode`.**
   - Read `Autonomy mode` from `intent.md` and `shotlist.json` (both must
     match):
     - **Both modes:** gate paid generation on `budget-envelope [effect:spend]`
       (satisfied by `intent.md` at `status: ready`) and gate `1080p` Final Pass
       rendering on `user-draft-gate [effect:approve-draft]` after Draft Cut
       assembly and review.
     - **`autonomous-draft` (default):** no human pause between Wave 1 Stills,
       optional Wave 1.5 Still Animatic, Wave 2 Risk-First Pilot + VO, Wave 3
       parallel routine shots + music, and Wave 4 Draft Cut assembly/QA—only
       automated `qa_media.py` + fresh Visual Critic (`reviewer-agent`) gates
       until `user-draft-gate [effect:approve-draft]`.
     - **`checkpointed`:** additionally place
       `user-stills-gate [effect:approve-stills]` after Wave 1 Stills QA (and
       optional Wave 1.5 Still Animatic), and
       `user-pilot-gate [effect:approve-pilot]` after Wave 2 Risk-First Pilot +
       VO QA before fanning out routine shots in Wave 3.
   - Use `TNN [acceptance]` on final assembly/delivery dependencies that require
     full Visual Critic + technical QA clearance before moving to delivery.

3. **Run the mechanical gate (`make ledger-check`).**
   - Execute:
     ```sh
     make ledger-check CAMPAIGN=<slug>
     ```
   - Fix every error reported by `scripts/check-ledger.py` (header format,
     packet sync, missing sections, DAG cycle, missing still/reference ancestor,
     parallel `Mutable owners` collision, or budget cap overflow) and inspect
     the printed topological execution waves to confirm real parallelism in
     Wave 1 (Stills) and Wave 3 (Video + Audio).

4. **Run fresh Task Readiness Review and flip to `status: ready`.**
   - Dispatch one fresh read-only `reviewer-agent` (`fork_turns: "none"`,
     `reasoning_effort: high`) running
     [Task Readiness Review](#task-readiness-review) under
     [Review](../shared/review.md), passing `intent.md`, `treatment.md`,
     `style-bible.md`, `shotlist.json`, `tasks.md`, `tasks/TNN-*.md`, and the
     `make ledger-check` output.
   - Repair confirmed findings in place (max 2 rounds), flip `tasks.md` to
     `status: ready`, re-run `make ledger-check CAMPAIGN=<slug>` to verify
     `ready` invariants, and return
     [Transition Result V1](../shared/transition.md#transition-result-v1) naming
     [Production](production.md) as `next_owner` (along with the one-screen
     wave overview for the Root Orchestrator).

## Task Readiness Review

Read-only review adapter for fixed `campaigns/<slug>/tasks.md`,
`campaigns/<slug>/tasks/TNN-*.md`, and `make ledger-check` output. Return
[Review Result V1](../interfaces/review-result-v1.md):

1. **Shotlist coverage:** verify every reference in `references[]`, every
   still and video in `shots[]`, enabled music/voiceover tracks, draft
   assembly, final `1080p` pass, stems export, and Final Delivery Review map to
   explicit tasks with zero dropped deliverables.
2. **Autonomy gate fidelity:** confirm `[effect:...]` gates match `intent.md`'s
   `Autonomy mode` (`autonomous-draft` vs `checkpointed`) and that `Final cap`
   renders cannot start before draft approval.
3. **Disjoint ownership & wave safety:** confirm concurrent wave tasks write to
   strictly disjoint paths, never write `tasks.md` or `shotlist.json`, and
   route every paid generation through `scripts/hf_guard.py`.
4. **Cold-start packet executability:** verify a fresh `worker-agent` reading
   only `tasks/TNN-*.md` and its cited `Sources` has exact commands
   (`hf_guard.py`, `qa_media.py`, `assemble.sh`), explicit retry/phase bounds,
   and falsifiable `Final validation` criteria.

Return `PASS`, `CONCERNS`, or `FAIL`.
