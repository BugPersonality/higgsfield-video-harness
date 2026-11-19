# Codex Harness Adapter

Codex Multi-Agent V2 execution adapter for `higgsfield-video-harness`. Native
Codex tool schemas govern callable fields; field availability alone never grants
spending or acceptance authority under [`AGENTS.md`](../../AGENTS.md#authority).

## Native Map

- **Project configuration sync.** [`.agents/codex-project.toml`](../../.agents/codex-project.toml)
  is the canonical Codex harness source and stays synchronized with
  [`.codex/config.toml`](../../.codex/config.toml) (verified mechanically by
  `make check-instructions`). Both files enable `features.multi_agent_v2 = true`
  and `[agents] enabled = true`.
- **20-subagent concurrency ceiling.** Multi-Agent V2 configures
  `max_concurrent_threads_per_session = 20` and does not use `agents.max_depth`
  (do not add one). The ceiling caps open subagents across the entire session
  tree excluding the root. During parallel shot waves (Wave 1 Stills and Wave 3
  Video), cap active `worker-agent` lanes so slots always remain available for
  `reviewer-agent` Visual Critic inspections and `evidence-agent` recovery
  checks (for example, at most 12 concurrent workers alongside up to 6 reviewers
  and 2 recovery/evidence slots).
- **Fresh-context spawning.** Dispatch every preparation phase owner,
  `evidence-agent`, `specialist-agent`, `worker-agent`, `reviewer-agent`, and
  `adjudicator-agent` via `collaboration.spawn_agent` with
  `fork_turns: "none"`. Pass the role definition from `.agents/roles/*.toml`,
  explicit input locators, disjoint writable paths (for `worker-agent`), and the
  required output contract.
- **Tree inspection and lifecycle tools:**
  - `collaboration.list_agents` — inspect active tree count before fanning out a
    wave or reconciling after interruption.
  - `collaboration.wait_agent` — await returned agent IDs using event-driven
    multi-minute waits; never wait on an idle or already-joined lane.
  - `collaboration.send_message` — send a targeted one-to-one decision delta to
    an active worker without broadcasting to unaffected lanes.
  - `collaboration.followup_task` — wake an idle worker only for bounded repair
    inside its unchanged shot packet, writable scope, and effort tier under
    [Context And Lifetime](../agent-harness.md#context-and-lifetime). To change
    model/effort or switch reviewers, stop the old lane and spawn a fresh one.
- **Single checkout, disjoint paths.** Codex subagents share the parent working
  directory. Do not create Git worktrees for shots; rely on strict shot path
  disjointness (`media/stills/sNN-*`, `media/shots/sNN-*`, `prompts/sNN_*`,
  `qc/sNN-*`), Root Orchestrator single-writer ownership of `tasks.md` and
  `shotlist.json`, and `scripts/hf_guard.py`'s file lock on `receipts.jsonl`.

## Visual QA Via `view_image`

Codex's native `view_image` tool makes independent visual inspection executable
without trusting text-only render logs:

1. Before calling `reviewer-agent`, the producing `worker-agent` (or assembly
   lane) runs `python3 scripts/qa_media.py` (`clip` or `render`) with `--sheet`
   to verify deterministic metrics (`ffprobe`, black/frozen frame checks, audio
   loudness) and emit a `3×2` PNG contact sheet under `campaigns/<slug>/qc/`.
2. The Root Orchestrator spawns a fresh `reviewer-agent` (`fork_turns: "none"`)
   passing strictly:
   - `campaigns/<slug>/intent.md` and `campaigns/<slug>/style-bible.md`;
   - relevant reference photos in `campaigns/<slug>/media/references/`;
   - the generated PNG contact sheet (and still image for Wave 1);
   - the `qa_media.py` JSON output and receipt metadata (`job_id`, `shot_id`).
   Omit builder rationales, retry narratives, and chat history.
3. Inside the fresh lane, `reviewer-agent` calls `view_image` on the reference
   images and the `3×2` contact sheet side by side, checks every visual/brand
   invariant under [Visual Critic Protocol](../video-workflow/shared/review.md#visual-critic-protocol),
   and returns [Review Result V1](../video-workflow/interfaces/review-result-v1.md).

## Channel Routing (CLI vs MCP)

Follow [`AGENTS.md`](../../AGENTS.md#channel-routing-cli-vs-mcp-vs-web-studio)
strictly inside Codex sessions:

| Operation | Authorized channel | Why |
| --- | --- | --- |
| Every paid campaign generation (`generate`, `product-photoshoot`, `soul-id`, `brain_activity`) and reference upload | `higgsfield` CLI wrapped by `python3 scripts/hf_guard.py` (`preflight`, `run --command {generate,product-photoshoot,soul-id}`, `upload`, `status`) | Enforces `Draft cap` / `Final cap`, per-shot retry bounds, reservation-before-submit locking (`status: "reserved"`), and `receipts.jsonl` audit records |
| Free read-only schema, voice, preset, workspace, balance, cost, and job-list checks | Direct `higgsfield` CLI (`--json`) via `evidence-agent` | Machine-parseable JSON output; matches live CLI submission schema 1:1 |
| Quick ad-hoc read-only balance or model checks in chat (no uploads, no budget ledger) | Higgsfield MCP (`[mcp_servers.higgsfield]` in `.codex/config.toml`) | Fast read-only convenience when outside a paid campaign wave |
| Web-only Cinema Studio 4.0 controls or one-time opaque preset UUID extraction | Web Cinema Studio + `higgsfield generate get <job_id> --json` | Captures reusable UUIDs into `docs/cinema-presets.json` (see [`docs/cinema-presets.example.json`](../cinema-presets.example.json)) |

Never route a paid campaign job through Higgsfield MCP or raw `higgsfield
generate create` because both bypass `scripts/hf_guard.py`'s credit cap and
idempotency checks.

## Event-Driven Waits On Video Renders

Higgsfield video generations routinely run 1–6 minutes per clip. Both
`.agents/codex-project.toml` and `.codex/config.toml` embed the event-driven
wait policy directly in `developer_instructions`:

- Use multi-minute event-driven waits (`collaboration.wait_agent`) on active
  subagents and long-running `hf_guard.py` video renders.
- Treat active rendering time as normal progress—never as a stall, timeout
  failure, or silent gap requiring status chatter.
- Do not emit unchanged periodic heartbeats or poll healthy workers for status
  unless the user explicitly requested progress intervals.
- Surface updates to the user only on wave dispatch, material state transitions
  (for example, Pilot `s01` passed QA), required checkpoints (`Gate 1`,
  `approve-stills`, `approve-pilot`, `approve-draft`), budget/policy blockers,
  or final delivery.
- If a CLI render command actually times out or terminates abnormally, enter
  [Parent-Owned Recovery](../video-workflow/shared/transition.md#parent-owned-recovery)
  and inspect `higgsfield generate list --json` before considering any retry.

## Models And Dispatch

Preserve the root session's configured model unless the user selects another.
On `collaboration.spawn_agent`, pass `reasoning_effort` matching the role's
starting tier (`low` for `evidence-agent`, `medium` for `worker-agent`, `high`
for `specialist-agent` and `reviewer-agent`, `xhigh` for `adjudicator-agent`)
alongside `fork_turns: "none"`.

- Escalate reasoning effort (for example, `medium` → `high` on a tricky motion
  repair, or `high` → `xhigh` via `adjudicator-agent` on a disputed Visual
  Critic conflict) by spawning a fresh agent rather than calling
  `followup_task` on the lower-tier lane.
- Keep returned agent IDs recorded in Orchestrator working state across wave
  checkpoints and interruptions so recovery reconciles completed workers once
  from native status, `receipts.jsonl`, and filesystem artifacts without
  double-dispatching paid shots.
