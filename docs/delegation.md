# Delegation & Internal QC

Keep every actor in the **Smart Zone**: one coherent outcome, bounded files,
primary artifacts (`brief.md`, `taste-log.md`, `style-bible.md`, `shotlist.json`),
and fresh history (`fork_turns: "none"` where supported). Keep the **Root
Producer** in one continuous session across `R0`–`R5` so the Director's verbatim
*why* stays a primary source, delegating AFK parallel craft and unbiased QC to
fresh subagents.

## Roles & Ownership

Four native Codex roles live in [`.agents/roles/`](../.agents/roles) (Multi-Agent
V2 configured in [`.codex/config.toml`](../.codex/config.toml), 20-thread
session ceiling; always reserve slots for Visual Critic QC and recovery):

| Role | Effort | Owns |
| --- | --- | --- |
| `evidence-agent` | `low` | Read-only live Higgsfield schemas, `generate cost`, account/workspace checks, `brands/` & photo discovery, `ffprobe`/`receipts.jsonl` reduction |
| `specialist-agent` | `high` | Read-only contrasting concepts, 3-column scripts, continuity-locked storyboards, prompt architecture, anti-IP rewrites |
| `worker-agent` | `medium` | Mutable leaf execution for one Lookbook entity, still, clip, audio stem, or assembly unit inside disjoint paths via `hf_guard.py`, `qa_media.py`, `assemble.sh` |
| `reviewer-agent` | `high` | Fresh read-only pre-Dailies Visual Critic (`view_image`) filtering technical trash, continuity breaks, and `TASTE_REGRESSION`s |

- **Disjoint asset paths (no Git worktrees for binaries):** parallel workers
  write strictly to assigned paths (`media/lookbook/<id>-*`, `media/stills/sNN-*`,
  `media/shots/sNN-*`, `media/audio/*`, `media/exports/*`, `prompts/<id>_*`,
  `qc/<id>-*`). Only the **Root Producer** edits `brief.md`, `taste-log.md`, and
  `shotlist.json`. `hf_guard.py` serializes `receipts.jsonl` under `flock`.
- **Freshness & reuse:** start every subagent with `fork_turns: "none"` (no
  parent chat turns or builder rationales). Reuse a `worker-agent` only for
  bounded repair inside its unchanged asset, writable paths, and `--round-cap`;
  spawn a fresh actor when `version` bumps, scope changes, or independent QC runs.
- **Codex tools:** use `view_image` on `lookbook.png`, stills, and `3x2` contact
  sheets; run `open <artifact>` on macOS before posting Dailies when
  `Auto-open dailies: true`. Keep paid campaign jobs strictly on `higgsfield`
  CLI via `hf_guard.py`—never mix paid MCP calls into a campaign.

## Pre-Dailies Visual Critic

Before assembling any Dailies Packet for generated media (`R2`–`R5`), spawn a
fresh read-only `reviewer-agent` (`fork_turns: "none"`) with only primary inputs
(`brief.md`, `taste-log.md`, `shotlist.json`, `qa_media.py` JSON, reference
photos, and `lookbook.png`/stills/`3x2` contact sheets via `view_image`)—never
builder self-review prose.

- **Filter defects, never taste:** reject obvious AI/technical defects
  (`MEDIA_TECH_DEFECT`, `VISUAL_DRIFT_DEFECT`, `TASTE_REGRESSION`,
  `CONTINUITY_DEFECT`, `POLICY_BLOCK`, `BUDGET_CAP`). Never pick among clean
  creative options or mark an asset `LOCKED`.
- **Fail closed on missing proof:** return `REVIEW_HANDOFF_INVALID` whenever
  required `qa_media.py` JSON, `taste-log.md`, or contact sheets are missing.
- **Honest escalation:** fix root causes inside `Max auto-retries/asset` and
  `--round-cap` (tighten anchors, adjust motion beats, sanitize IP phrasing).
  When retries or round cap exhaust, surface any surviving borderline `CONCERN`
  openly in one line of Dailies for the Director's call.

## Parent-Owned Recovery

Technical obstacles belong to the Root Producer, never the Director:
- **Zero double-spend on timeouts/interruptions:** `hf_guard.py` keeps timed-out
  or ambiguous jobs reserved (`in_progress`) and reconciles via `generate get`/
  `wait`/`list` (or `soul-id get`/`wait`) on retry. Reconcile `receipts.jsonl`
  and `higgsfield generate list --json` before replacing a stalled worker.
- **Bound no-progress loops:** diagnose the root cause before each retry rather
  than repeating identical prompts/inputs. On `BUDGET_CAP`, `asset_locked`,
  `retry_limit_exceeded`, or repeated `POLICY_BLOCK`, workers return
  `NEEDS_PARENT` immediately.

## Output Envelopes

### Evidence Result
```text
question: <read-only discovery question>
commands_run: <exact CLI or probe commands>
locators: <paths, model/workflow IDs, receipt ranges>
findings: <exact JSON excerpts, live generate cost, or media metrics>
gaps: <none | missing file, auth gap, or unavailable schema field>
```

### Specialist Result
```text
angle: <concept | script | storyboard | lookbook contrast | prompt repair | anti-IP>
taste_anchors: <TL-NN IDs and LOCKED asset IDs honored>
proposal: <creative options, script/storyboard draft, or prompt text>
tradeoffs: <visual, pacing, or cost trade-off>
gaps: <none | missing brief.md truth or upstream asset>
```

### Worker Result
```text
round: <R2 | R3 | R4 | R4A | R4B | R5>
asset_id: <lookbook id | sNN.still | sNN.video | audio | export>
status: DONE | NEEDS_PARENT
outputs: <media, prompt, and QC paths written inside disjoint scope>
receipts: <reservation_id, job_id or upload_id, credits, attempt>
qa_summary: <qa_media.py JSON summary and contact-sheet/lookbook path>
blocker: <none | BUDGET_CAP | asset_locked | POLICY_BLOCK | retry_limit_exceeded | error>
```

### Review Result
```text
candidate: <round and exact asset/sheet paths inspected>
verdict: PASS | CONCERNS | FAIL | REVIEW_HANDOFF_INVALID
findings: <anchor, defect class (MEDIA_TECH_DEFECT | VISUAL_DRIFT_DEFECT | TASTE_REGRESSION | CONTINUITY_DEFECT | POLICY_BLOCK | BUDGET_CAP | CONCERN | FOLLOW_UP), impact, or none>
evidence_boundary: <files, qa_media.py reports, and images inspected via view_image>
reopen_owner: <Worker(<asset_id>) | Root Producer | none>
```
