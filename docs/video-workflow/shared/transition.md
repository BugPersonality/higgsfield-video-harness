# Transition

Governs macro-phase movement, `Blocked Exit` handoffs, `Parent-Owned Recovery`
(including Higgsfield timeout and double-spend protection), and surgical
mid-pipeline reopens.

## Cross-Phase Continuation

After [Intake](../phases/intake.md) confirms `campaigns/<slug>/intent.md` at
`status: ready` (passing `make intent-check CAMPAIGN=<slug>`), the Root
Orchestrator dispatches preparation phases serially, each in a fresh subagent
(`fork_turns: "none"`):

1. Dispatch [Creative Definition](../phases/creative-definition.md) with
   `intent.md` and `brands/` / `media/references/` locators. Wait for its
   reviewed [Transition Result V1](#transition-result-v1) confirming
   `treatment.md` and `style-bible.md` at `status: ready`.
2. Dispatch [Production Design](../phases/production-design.md) with
   `intent.md`, `treatment.md`, and `style-bible.md`. Wait for its reviewed
   receipt confirming `shotlist.json`, prompts, and verified `generate cost`
   budget fit.
3. Dispatch [Planning](../phases/planning.md) with `intent.md`, `treatment.md`,
   `style-bible.md`, and `shotlist.json`. Wait for its reviewed receipt
   confirming `tasks.md` + `tasks/TNN-*.md` passing `make ledger-check`.
4. Once `tasks.md` is `status: ready`, the Root Orchestrator drives
   [Production](../phases/production.md) wave-by-wave (respecting
   `Autonomy mode` gates and `Budget Authority`).

A preparation phase owner owns its artifact, bounded research (`evidence-agent`),
creative lanes (`specialist-agent`), fresh review (`reviewer-agent`), and
repairs. If a phase returns `status: blocked`, the Root Orchestrator pauses
dependent phases and routes directly to `reopen_owner` (typically Intake for
requester meaning or taste forks).

## Blocked Exit

Use `Blocked Exit` (`status: blocked`) ONLY when a required decision, missing
asset, irreversible taste fork, or hard budget/policy boundary cannot be closed
inside current phase authority. Never emit a blocked exit for ordinary craft
choices or technical obstacles.

When emitting a blocked exit, record structured `Blocked decisions` (`B1..Bn`)
in the owning artifact (for example `treatment.md`) or inline in
`Transition Result V1`:

- State the exact **conflict or missing input** anchored to `intent.md` or live
  CLI output (`generate cost`, `model get`, moderation error).
- Present 2–3 concrete viewer-visible or budget options (`Option A` /
  `Option B`) with clear trade-offs—never raw model flags.
- Hold conditional sub-questions in `Follow-up if <option>` lines so Intake
  asks them only if the requester chooses that branch.
- Name the exact `reopen_owner` (`Intake`, `Production Design`, or requester
  external asset action) and preserve all already-valid work on disk.

## Parent-Owned Recovery

Obstacles—API timeouts, HTTP 429 rate limits, `ip_detected` moderation blocks,
server parameter `adjustments`, or a bad first take—are **not** blockers. Every
delegated blocker (`NEEDS_PARENT`), worker failure, or exhausted local retry
belongs to the requesting parent (Root Orchestrator):

1. **Mandatory timeout / double-spend reconciliation.** Before retrying ANY
   timed-out, dropped, or interrupted paid Higgsfield call:
   - Run `higgsfield generate list --json` (via `evidence-agent` or read-only
     CLI) and inspect `campaigns/<slug>/receipts.jsonl`.
   - Match by prompt hash, model, timestamp, and parameters to check whether
     Higgsfield already accepted, queued, or completed the job remotely.
   - If the remote job exists, **never submit a second paid call**: wait on or
     download the existing `job_id`, record/reconcile it in `receipts.jsonl`
     and `shotlist.json`, and run `scripts/qa_media.py`.
   - Only when `generate list --json` confirms no matching job was created may
     the parent authorize a fresh `scripts/hf_guard.py` attempt.
2. **Diagnose before spending another take.** A blind identical retry wastes
   credits. Match the recovery action to the defect class:
   - `MEDIA_TECH_DEFECT` (bad FPS, black tail, loudness miss) → fix locally in
     `assemble.sh` / trim if valid, or adjust motion prompt pacing / model
     params before regenerating; for over-window VO, tighten script word count
     and regenerate (never use `atempo`).
   - `VISUAL_DRIFT_DEFECT` → strengthen reference wiring (`image_references`,
     `start_image_from`), tighten negative material cues, or raise worker
     guidance via `specialist-agent` (`video-direction` / `video-consistency`).
   - `POLICY_BLOCK` (`ip_detected` / likeness / trademark) → dispatch
     `specialist-agent` to rewrite prompts using pure visual descriptors free
     of brand/celebrity triggers or substitute the flagged reference image.
   - `HTTP 429` / transient API failure → respect backoff and reduce concurrent
     submissions without burning a retry slot in `Max auto-retries/shot`.
   - `BUDGET_CAP` or exhausted `Max auto-retries/shot` → stop paid calls for
     that shot immediately, preserve all passing shots, and escalate cleanly to
     the requester (or `adjudicator-agent` if a trade-off inside remaining cap
     is disputed).
3. **No progress-free cycling.** Changing actor, worker, or reasoning effort
   without new diagnostic evidence does not reset retry or repair allowances.
   When no authorized probe or remaining budget can close a confirmed defect,
   retain `Blocked` with exact receipts, spent credits, and the smallest
   decision needed from the requester—never fabricate a `PASS`.

## Mid-Pipeline Reopen

When requester feedback (for example at Gate 2 Stills, Pilot `s01`, or Draft
Cut review) or a surviving `INTENT_GAP` requires changing `intent.md` after
production has already begun:

1. Pause active dependent workers and reconcile any in-flight receipts into
   `receipts.jsonl` and `shotlist.json`.
2. Reopen [Intake](../phases/intake.md) (flipping `intent.md` `ready` → `draft`,
   reconciling changes in place with stable `I<n>` / `A<n>` IDs, re-running
   `make intent-check CAMPAIGN=<slug>`, confirming material deltas, and flipping
   back to `ready`).
3. **Surgical downstream invalidation (never wipe accepted work):**
   - Identify strictly which shots, prompts, or audio stems are invalidated by
     the intent delta.
   - Keep every unaffected accepted still, video take, `upload_id`, and
     `receipts.jsonl` record intact.
   - Re-run only the invalidated downstream owners (for example, update `s02`
     prompt + `shotlist.json`, add a new repair task in `tasks.md` passing
     `make ledger-check`, regenerate `s02`, re-run Visual Critic on `s02` +
     continuity check against `s01`/`s03`, and re-assemble).

## Transition Result V1

Every macro phase returns one concise durable receipt to the Root Orchestrator:

```text
status: ready | blocked | skipped
owner: <Intake | Creative Definition | Production Design | Planning | Production>
result: <primary artifact path(s) produced or verified>
review: <Review Result V1 verdict + anchor, or none when skipped>
movement_evidence: <mechanical check + review clearance proving next phase may act>
reopen_owner: <owner or none>
next_owner: <next phase or none>
```
