# Codex Harness Adapter

Codex Multi-Agent V2 execution adapter for `higgsfield-video-harness`. Native
Codex tool schemas govern callable fields; field availability alone never grants
spending, lock-override, or Dailies approval authority under
[`AGENTS.md`](../../AGENTS.md#authority).

## Native Map

- **Project configuration sync.** [`.agents/codex-project.toml`](../../.agents/codex-project.toml)
  is the canonical Codex harness source and stays synchronized with
  [`.codex/config.toml`](../../.codex/config.toml) (verified mechanically by
  `make check-instructions`). Both files enable `features.multi_agent_v2 = true`
  and `[agents] enabled = true`.
- **20-subagent concurrency ceiling.** Multi-Agent V2 configures
  `max_concurrent_threads_per_session = 20` and does not use `agents.max_depth`
  (do not add one). The ceiling caps open subagents across the entire session
  tree excluding the root. During parallel rounds (`R2` Lookbook variants, `R3`
  Stills, `R4B` Draft clips, `R5` `1080p` upgrades), cap active `worker-agent`
  lanes so slots always remain available for internal `reviewer-agent` visual
  filtering and `evidence-agent` recovery checks (for example, at most 12
  concurrent workers alongside up to 6 reviewers and 2 evidence/recovery slots).
- **Fresh-context spawning.** Dispatch every `evidence-agent`,
  `specialist-agent`, `worker-agent`, `reviewer-agent`, and `adjudicator-agent`
  via `collaboration.spawn_agent` with `fork_turns: "none"`. Pass the role
  definition from `.agents/roles/*.toml`, authoritative campaign input locators
  (`brief.md`, `taste-log.md`, `shotlist.json`), disjoint writable paths (for
  `worker-agent`), and the required output schema.
- **Tree inspection and lifecycle tools:**
  - `collaboration.list_agents` — inspect active tree count before fanning out a
    round batch or reconciling after interruption.
  - `collaboration.wait_agent` — await returned agent IDs using event-driven
    multi-minute waits; never wait on an idle or already-joined lane.
  - `collaboration.send_message` — send a targeted one-to-one delta to an active
    worker inside its unchanged writable scope without broadcasting to
    unaffected lanes.
  - `collaboration.followup_task` — wake an idle worker only for bounded repair
    inside its unchanged asset unit, round cap, writable scope, and effort tier
    under [Context And Lifetime](../agent-harness.md#context-and-lifetime). To
    change effort tier, switch to a new asset version after Dailies feedback, or
    run fresh QC, stop the old lane and spawn a fresh one.
- **Single checkout, disjoint paths.** Codex subagents share the parent working
  directory. Do not create Git worktrees per shot; rely on strict per-asset path
  disjointness (`media/lookbook/<id>-*`, `media/stills/sNN-*`,
  `media/shots/sNN-*`, `prompts/*`, `qc/*`), Root Producer single-writer
  ownership of `brief.md`, `taste-log.md`, and `shotlist.json`, and
  `scripts/hf_guard.py`'s exclusive file lock on `receipts.jsonl`.

## Visual Filtering Via `view_image`

Codex's native `view_image` tool powers internal pre-Dailies defect and
taste-regression filtering so broken AI frames never waste the Director's time:

1. Before invoking `reviewer-agent`, the producing `worker-agent` runs
   `scripts/qa_media.py` (`clip`, `render`, or `lookbook`) to verify
   deterministic metrics (`ffprobe`, black/frozen frames, `-14 LUFS`, true peak)
   and produce the visual inspection artifact (individual Lookbook PNGs, still
   PNGs, or `3×2` contact sheets under `campaigns/<slug>/qc/`).
2. The Root Producer spawns a fresh `reviewer-agent` (`fork_turns: "none"`)
   passing strictly:
   - `campaigns/<slug>/brief.md`, `campaigns/<slug>/taste-log.md` (and
     `brands/<brand>/taste.md` when cited), `campaigns/<slug>/style-bible.md`,
     and `campaigns/<slug>/shotlist.json` (`continuity_lock`, `test_take_check`);
   - relevant `LOCKED` references in `media/references/` or `media/lookbook/`;
   - the generated Lookbook variant(s), still(s), or `3×2` contact sheet(s);
   - the `qa_media.py` JSON output and receipt metadata (`job_id`, `asset_id`).
   Omit builder prompt rationales, retry excuses, and Root Producer chat turns.
3. Inside the fresh lane, `reviewer-agent` calls `view_image` on the references
   and candidate frames side by side, checks every technical, continuity, and
   `taste-log.md` invariant under
   [Visual Critic Protocol](../video-workflow/shared/review.md#visual-critic-protocol),
   and returns [Review Result V1](../video-workflow/interfaces/review-result-v1.md).
4. Passing candidates are compiled into the round's visual artifact
   (`qc/lookbook.png`, `qc/stills_strip.png`, `media/exports/animatic.mp4`,
   `media/exports/draft_cut.mp4`, or `media/exports/master.mp4`) for the
   Director's Dailies Packet; rejected takes are auto-retried within
   `Max auto-retries/asset` and `--round-cap`, and summarized in one line under
   Block 2 (`Filtered internally`).

## Channel Routing (CLI vs MCP)

Follow [`AGENTS.md`](../../AGENTS.md#channel-routing-cli-vs-mcp-vs-web-studio)
strictly inside Codex sessions:

| Operation | Authorized channel | Why |
| --- | --- | --- |
| Every paid campaign generation (`generate`, `product-photoshoot`, `soul-id`, `brain_activity`) and tracked upload | `higgsfield` CLI wrapped by `python3 scripts/hf_guard.py` (`preflight` / `run --round {R2,R3,R4,R4A,R4B,R5} --round-cap <N> [--variant <A\|B\|C>] [--version <N>] --command {generate,product-photoshoot,soul-id}`, `upload --round <R>`, `status`) | Enforces `Campaign cap`, mandatory cumulative `--round-cap`, per-variant/version `Max auto-retries/asset`, `asset_locked` on `LOCKED` assets (no `--force-unlock` bypass), fail-closed `corrupt_shotlist`/`corrupt_receipts`, reservation-before-submit locking, and `receipts.jsonl` audit records |
| Free read-only schema, voice, preset, workspace, balance, live `generate cost`, and job-list checks | Direct `higgsfield` CLI (`--json`) via `evidence-agent` | Machine-parseable JSON output matching live CLI submission schemas 1:1 |
| Quick ad-hoc read-only balance or model checks in chat (outside a paid round) | Higgsfield MCP (`[mcp_servers.higgsfield]` in `.codex/config.toml`) | Fast read-only convenience with zero local upload or spend ledger impact |
| Web-only Cinema Studio 4.0 controls (`Emotion Wheel`, `AI Cast`, visual light placement) or one-time opaque preset UUID extraction | Web Cinema Studio + `higgsfield generate get <job_id> --json` | Captures reusable UUIDs into `docs/cinema-presets.json` (see [`docs/cinema-presets.example.json`](../cinema-presets.example.json)) |

Never route a paid campaign call through Higgsfield MCP or raw `higgsfield
generate create` because both bypass `scripts/hf_guard.py`'s `Campaign cap`,
`--round-cap`, `asset_locked`, and double-spend guards.

## macOS `open` Dailies Previewing

Visual taste requires seeing full-resolution grids and hearing real motion/audio
cuts outside a terminal window. When `campaigns/<slug>/brief.md` sets
`Auto-open dailies: true` (under `Constraints & boundaries` →
`Budget & round policy`):

1. After internal QC passes and the round's consolidated visual artifact is
   written on disk, check that the host is interactive macOS
   (`uname -s == Darwin`, non-CI) and open the single primary artifact directly:
   - `R2`: `open campaigns/<slug>/qc/lookbook.png`
   - `R3`: `open campaigns/<slug>/qc/stills_strip.png` and
     `open campaigns/<slug>/media/exports/animatic.mp4`
   - `R4A`: `open campaigns/<slug>/media/shots/<pilot-clip>.mp4`
   - `R4B`: `open campaigns/<slug>/media/exports/draft_cut.mp4`
   - `R5`: `open campaigns/<slug>/media/exports/master.mp4`
2. Immediately deliver the 4-block
   [Dailies Packet V1](../video-workflow/interfaces/dailies-packet-v1.md) in
   chat with the exact file path(s) alongside the opened preview.
3. If `Auto-open dailies: false` or running on a non-macOS / headless shell,
   skip `open` cleanly without warning noise and display the exact local file
   path(s) in Block 1 (`What to inspect`).

## Event-Driven Waits On Video Renders

Higgsfield video generations routinely run 1–6 minutes per clip. Both
`.agents/codex-project.toml` and `.codex/config.toml` embed the event-driven
wait policy directly in `developer_instructions`:

- Use multi-minute event-driven waits (`collaboration.wait_agent`) on active
  subagents and long-running `hf_guard.py` video renders.
- Treat active rendering time as normal progress—never as a stall, timeout
  failure, or silent gap requiring status chatter.
- Do not emit unchanged periodic heartbeats or poll healthy workers for status
  unless the Director explicitly asks for progress intervals.
- Surface updates to the Director only on round dispatch, material milestones
  (for example, Pilot clip ready), end-of-round **Dailies Packets**,
  budget/policy blockers, or final `R5` delivery.
- If a CLI render command actually times out or terminates abnormally, enter
  [Parent-Owned Recovery](../video-workflow/shared/transition.md#parent-owned-recovery)
  and reconcile `higgsfield generate list --json` + `higgsfield generate get`
  before authorizing any retry.

## Models And Dispatch

Preserve the root session's configured model unless the Director selects
another. On `collaboration.spawn_agent`, pass `reasoning_effort` matching the
role's starting tier (`low` for `evidence-agent`, `medium` for `worker-agent`,
`high` for `specialist-agent` and `reviewer-agent`, `xhigh` for
`adjudicator-agent`) alongside `fork_turns: "none"`.

- Escalate reasoning effort (for example, `medium` → `high` on a tricky physics
  repair, or `high` → `xhigh` via `adjudicator-agent` on a disputed QC vs round
  budget trade-off) by spawning a fresh agent rather than calling
  `followup_task` on the lower-tier lane.
- Keep returned agent IDs tracked in Root Producer working state across round
  interruptions so recovery reconciles completed workers once from native
  status, `receipts.jsonl`, and filesystem outputs without double-dispatching
  paid assets.
