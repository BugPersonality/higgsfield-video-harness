# Transition

Governs round-to-round handoffs (`R0` → `R5`), surgical single-asset
re-iteration without disturbing `LOCKED` work, mid-campaign direction pivots,
and **Parent-Owned Recovery** (timeouts, HTTP 429 rate limits, `ip_detected`
moderation blocks, and duplicate-spend prevention).

## Round Handoffs (`R0` → `R5`)

Every round ends with a [Dailies Packet V1](../interfaces/dailies-packet-v1.md)
and **waits for the Director** before spending credits in the next round. There
is never a silent automatic jump across paid rounds.

| Completed round | Gate before advancing | Next round |
| --- | --- | --- |
| `R0` — Direction Seed | Dailies 0 confirmed; `brief.md` at `status: active` (`make brief-check`); `taste-log.md` seeded | [R1 — Story & Cost Ticket](../rounds/r1-story-and-cost.md) |
| `R1A` — Concept Pick | Director picks/blends pitch; logged in `taste-log.md` | `R1B` inside [R1](../rounds/r1-story-and-cost.md) |
| `R1B` — Story & Cost Ticket | `shotlist.json` passes `make campaign-check`; Director approves next single round's `--round-cap` | [R2 — Lookbook](../rounds/r2-lookbook.md) *(or skip to [R3](../rounds/r3-stills-and-animatic.md) when `lookbook: []`)* |
| `R2` — Lookbook | All `lookbook[]` entities uploaded & `LOCKED`; `taste-log.md` updated; Director approves `R3` `--round-cap` | [R3 — Keyframe Stills & Animatic](../rounds/r3-stills-and-animatic.md) |
| `R3` — Stills & Animatic | All stills (& rough audio) `LOCKED`; `taste-log.md` updated; Director approves `R4A` (or `R4`) `--round-cap` | [R4 — Motion Dailies](../rounds/r4-motion-dailies.md) |
| `R4A` — Risk-First Pilot | Pilot clip(s) approved; `taste-log.md` updated; Director approves `R4B` `--round-cap` | `R4B` inside [R4](../rounds/r4-motion-dailies.md) |
| `R4B` — Draft Cut | `draft_cut.mp4` approved; Director approves `R5` `1080p` upgrade list & `--round-cap` | [R5 — Final Master](../rounds/r5-mastering.md) |
| `R5` — Final Master | Final Dailies 5 approved; all assets `LOCKED`; `brief.md` → `status: done`; confirmed rules graduated to `brands/<brand>/taste.md` | Complete |

Before closing any round and presenting Dailies, the Root Producer joins or
stops all active `worker-agent` and `reviewer-agent` descendants and reconciles
all terminal receipts in `receipts.jsonl` and `shotlist.json`.

## Surgical Single-Asset Re-Iteration

Most Director feedback affects **one entity or shot** while everything else is
already working. Never wipe or re-render a whole round when a surgical re-roll
closes the feedback:

1. **Preserve every `LOCKED` asset:** keep all `LOCKED` Lookbook UUIDs, stills,
   clips, and audio stems untouched (`hf_guard.py` enforces this mechanically
   via `asset_locked`).
2. **Capture the steer:** append `### TL-<NN>` in `campaigns/<slug>/taste-log.md`
   via [Feedback Loop](feedback-loop.md).
3. **Bump version & prompt:** flip ONLY the target asset in `shotlist.json` to
   `status: "ITERATING"`, increment `version`, write the versioned prompt file
   (`_v2.txt`, `_v3.txt`), and run `make campaign-check CAMPAIGN=<slug>`.
4. **Confirm exact micro-cost:** quote live `higgsfield generate cost` for ONLY
   that asset, read current spend for its round bucket (`R2`, `R3`, `R4A`,
   `R4B`, `R4`, or `R5`) from `make budget-status CAMPAIGN=<slug>`, and obtain
   Director approval for `<delta_cap>` (raising the round's cumulative ceiling
   to `<round_spent + delta_cap>`).
5. **Execute & re-filter:** dispatch one fresh `worker-agent` inside that
   asset's disjoint paths via `hf_guard.py run --round <R2|R3|R4|R4A|R4B|R5>
   --round-cap <round_spent + delta_cap> --version <N>` (plus
   `--variant <A|B|C>` for `--kind lookbook`; keeping `R4A` pilot and `R4B`
   batch in their distinct buckets), run `scripts/qa_media.py`, and run a fresh
   `reviewer-agent` (`view_image`) checking both the updated asset and its
   continuity against adjacent `LOCKED` shots.
6. **Rebuild preview & re-present Dailies:** refresh the single consolidated
   preview artifact (`lookbook.png`, `stills_strip.png` + `animatic.mp4`, or
   `draft_cut.mp4`) and present a compact updated Dailies Packet.

## Mid-Campaign Direction Pivot

If Director feedback changes a fundamental invariant in `brief.md` (meaning,
aspect ratio, runtime, spoken pronunciation, `Must not`, or `Campaign cap`):

1. Stop active dependent workers and reconcile all in-flight `receipts.jsonl`
   entries first.
2. Update `brief.md` in place (re-running `make brief-check CAMPAIGN=<slug>`)
   and append a `Supersedes TL-<prev>` entry in `taste-log.md`.
3. Invalidate **strictly** the affected downstream assets (explicitly unlocking
   any `LOCKED` asset only with Director confirmation), preserve unaffected
   `LOCKED` assets and `receipts.jsonl`, re-price via `evidence-agent`, verify
   `make campaign-check`, and resume from the earliest invalidated round.

## Parent-Owned Recovery

Obstacles—API timeouts, HTTP 429 rate limits, `ip_detected` moderation blocks,
server parameter adjustments, or a defective first take—are **not** blockers.
Every `NEEDS_PARENT` return, worker crash, or exhausted local retry belongs to
the Root Producer:

1. **Mandatory timeout / double-spend reconciliation (`generate list` + `generate get`).**
   Before retrying **any** timed-out, dropped, or interrupted paid call:
   - Run `higgsfield generate list --json` (via `evidence-agent` or read-only
     CLI) and inspect `campaigns/<slug>/receipts.jsonl` for open
     `status: "reserved"` records.
   - Match by `params_hash`, model, prompt, and timestamp to verify whether
     Higgsfield already accepted, queued, or completed the job remotely.
   - If a remote `job_id` exists, inspect it with
     `higgsfield generate get <job_id> --json` and **never submit a second paid
     call**: wait on or download the existing job output, reconcile the
     terminal receipt in `receipts.jsonl` and `shotlist.json`, and run
     `scripts/qa_media.py`.
   - Authorize a fresh `hf_guard.py run` attempt **only** after
     `generate list --json` confirms no matching remote job was created.
2. **Match recovery strictly to the defect class:**
   - **`HTTP 429` / transient API error:** back off cleanly and reduce parallel
     worker fan-out; transient transport errors before remote acceptance do not
     consume a creative retry slot.
   - **`POLICY_BLOCK` (`ip_detected` / likeness / trademark):** dispatch a fresh
     `specialist-agent` (`video-direction`) to rewrite prompts using pure visual
     descriptors free of brand/celebrity triggers, or swap the flagged reference
     image before retrying inside `Max auto-retries/asset`.
   - **`MEDIA_TECH_DEFECT`:** fix local FPS/loudness/cut issues in
     `scripts/assemble.sh` when clip frames are healthy; for `frozen_tail`,
     `fully_static_clip`, or black frames, tighten timestamped motion beats
     before regenerating; for over-window VO, trim spoken words and regenerate
     (**never** apply `atempo`).
   - **`VISUAL_DRIFT_DEFECT` / `CONTINUITY_DEFECT` / `TASTE_REGRESSION`:**
     strengthen `LOCKED` reference wiring (`image_references`,
     `start_image_from`), tighten prompt cues against the broken `TL-NN` or
     `continuity_lock` clause, and regenerate inside `Max auto-retries/asset`
     and `--round-cap`.
   - **`asset_locked` refusal:** halt that worker immediately—`hf_guard.py`
     has no `--force-unlock` bypass and must never be circumvented. Verify
     whether the worker targeted the wrong asset ID or whether the Director
     needs to explicitly confirm unlocking the asset so the Root Producer can
     move `shotlist.json` from `LOCKED` → `ITERATING` (and bump `version`).
   - **`BUDGET_CAP` or exhausted `Max auto-retries/asset`:** stop paid calls
     for that asset immediately, preserve all passing/locked assets, consult
     `adjudicator-agent` if a borderline take might be surfaced with a
     `CONCERN`, or surface the exact spend status and options to the Director
     in Dailies.
3. **No progress-free cycling:** swapping workers or raising reasoning effort
   without new diagnostic evidence never resets `Max auto-retries/asset` or
   `--round-cap`. Never fabricate a `PASS` or hide an unclosed defect from the
   Director.
