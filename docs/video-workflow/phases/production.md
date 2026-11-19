# Phase 4 — Production & Delivery

Use once `campaigns/<slug>/tasks.md` is at `status: ready` and passes
`make ledger-check CAMPAIGN=<slug>`. The Root Orchestrator drives execution
wave-by-wave under [Agent Harness](../../agent-harness.md) and
[Codex Adapter](../../agent-harness/codex.md), keeping single-writer ownership
of `tasks.md` and `shotlist.json`.

## Pre-Wave Verification (Zero Credits)

Before dispatching Wave 1, verify workspace and budget readiness via
`evidence-agent` or direct read-only CLI:

1. `higgsfield workspace list` — confirm the active Higgsfield workspace is the
   intended billing workspace.
2. `higgsfield account status` — confirm valid auth and sufficient credit
   balance to cover `Draft cap`.
3. `make budget-status CAMPAIGN=<slug>` — confirm clean `receipts.jsonl`
   baseline and loaded `intent.md` envelope (`status: ready`).
4. Confirm all required local reference photos exist under
   `campaigns/<slug>/media/references/`.

## Wave Execution

Every paid Higgsfield call and tracked upload inside every wave executes
strictly via `python3 scripts/hf_guard.py` (`preflight`, `run --command
{generate,product-photoshoot,soul-id}`, `upload`, `status`) under
[Budget Authority](../shared/budget-authority.md). On multi-minute video
renders, use event-driven waits (`collaboration.wait_agent`) with zero polling
chatter. Respect the Codex 20-subagent ceiling by reserving slots for fresh
`reviewer-agent` Visual Critic inspections and recovery lanes.

### Wave 1 — References & Stills

1. **Upload references (`[reference]`):** dispatch a `worker-agent` (`fork_turns:
   "none"`) to verify local reference files with `ffprobe` and upload each via
   `python3 scripts/hf_guard.py upload --campaign <dir> --file <path> --ref-id <id>`.
   Root Orchestrator persists returned `upload_id` values into `shotlist.json`
   and checks off the task in `tasks.md`.
2. **Generate anchor stills (`[still]`):** fan out disjoint `worker-agent`
   lanes for `s01..sN`, each running `hf_guard.py run --kind still --phase
   draft` into `media/stills/sNN-*` and probing output integrity.
3. **Visual Critic QA:** for each generated still, dispatch a fresh
   `reviewer-agent` (`fork_turns: "none"`) inspecting `media/references/*` and
   the still via `view_image` against `intent.md` and `style-bible.md`. On
   `FAIL`, repair within `Max auto-retries/shot` and max 2 review rounds.
4. **Autonomy branch:**
   - In **`checkpointed`** mode, pause at `user-stills-gate
     [effect:approve-stills]` and present the verified stills before rendering
     any motion clips.
   - In **`autonomous-draft`** mode, advance directly to Wave 2 once all stills
     pass Visual Critic.

### Wave 1.5 — Optional Still Animatic (0 Video Credits)

When scheduled in `tasks.md` (or before paying for multi-shot video renders on
tightly paced spots), build a timed still animatic directly from approved Wave 1
`media/stills/` plus any generated VO/music stems at **zero video-credit cost**:

```sh
make animatic CAMPAIGN=<slug>
```

`scripts/assemble.sh --animatic` exports `campaigns/<slug>/media/exports/animatic.mp4`
locked to each shot's `duration_s` and `fps_target` so the team (or requester at
`user-stills-gate` in `checkpointed` mode) can verify pacing, beat economy, VO
read-aloud fit, and the **mute test** before spending a single video credit.

### Wave 2 — Voiceover & Risk-First Pilot

1. **Voiceover (`[audio]`, when `audio.voiceover.enabled` is true):** generate
   VO track(s) via `hf_guard.py run --kind audio --phase draft` and validate
   active speech duration using 100ms RMS energy:
   ```sh
   make qa-voice FILE=campaigns/<slug>/media/audio/vo_s01.wav WINDOW=<sec>
   ```
   **Hard rule:** never speed up VO with FFmpeg `atempo` to squeeze into a shot
   window. If `qa_media.py voice` reports overflow, tighten script wording and
   regenerate within retry bounds.
2. **Risk-first pilot shots (`[pilot]`):** prioritize every shot in
   `shotlist.json` carrying `test_take_check != null` in Wave 2 (falling back
   to `s01` when no shot is flagged risky). Render each pilot using
   `draft_params` (`480p`/`720p` or `seedance_2_5 --draft`) via
   `hf_guard.py run --kind video --phase draft` to prove the flagged risk
   (`test_take_check.risk` / `test_take_check.pass_check`), motion grammar,
   `continuity_lock`, and native diegetic sound before paying for routine shots
   in Wave 3.
3. **Deterministic + Visual Critic QA:** run `make qa-clip
   FILE=campaigns/<slug>/media/shots/<sNN>-draft-t1.mp4
   SHEET=campaigns/<slug>/qc/<sNN>-draft-t1-sheet.png` and dispatch fresh
   `reviewer-agent` (`view_image` on `references/`, the shot's still, and the
   `3×2` contact sheet + `qa_media.py` JSON) verifying all three
   `continuity_lock` invariants and each pilot's `test_take_check.pass_check`.
4. **Autonomy branch:**
   - In **`checkpointed`** mode, pause at `user-pilot-gate
     [effect:approve-pilot]` and present the Risk-First Pilot take(s) + VO +
     contact sheet(s) before fanning out Wave 3.
   - In **`autonomous-draft`** mode, advance directly to Wave 3 once all Wave 2
     pilot shots and VO pass QA.

### Wave 3 — Parallel Routine Shots + Music / SFX

1. **Parallel draft video batch (`[video]`):** dispatch disjoint `worker-agent`
   lanes for all remaining routine shots not rendered in Wave 2 using
   `draft_params` via `hf_guard.py run --kind video --phase draft`. Each worker
   writes strictly inside `media/shots/sNN-*` and `qc/sNN-*`, runs
   `scripts/qa_media.py clip --sheet`, and returns exact output paths, `job_id`,
   and `qa_media.py` JSON.
2. **Music / SFX (`[audio]`):** in parallel, generate enabled music/SFX stems
   via `hf_guard.py run --kind audio --phase draft` into `media/audio/`.
3. **Per-shot Visual Critic & Continuity QA:** dispatch fresh `reviewer-agent`
   lanes (`view_image`) inspecting each shot's `3×2` contact sheet alongside
   `references/` and accepted Pilot `s01` frames to catch both
   `VISUAL_DRIFT_DEFECT` and cross-shot `CONTINUITY_DEFECT`.
4. **Bounded recovery:** if any worker hits timeout, `HTTP 429`,
   `POLICY_BLOCK`, `VISUAL_DRIFT_DEFECT`, or `BUDGET_CAP`, apply
   [Parent-Owned Recovery](../shared/transition.md#parent-owned-recovery)
   (always checking `higgsfield generate list --json` before retrying any
   timed-out render) and escalate surviving conflicts to `adjudicator-agent`.
5. Root Orchestrator serially records accepted draft `selected_take` /
   `selected_job_id` in `shotlist.json` and marks completed tasks `[x]` in
   `tasks.md`.

### Wave 4 — Draft Assembly, Gate Approval, Final `1080p` Pass & Delivery

1. **Assemble Draft Cut (`[assembly]`):** run `scripts/assemble.sh` via
   Makefile (`video-assembly` skill owns FPS lock, audio level law, and master
   loudness normalization via `loudnorm=I=-14:TP=-1.5:LRA=11`):
   ```sh
   make assemble CAMPAIGN=<slug> OUT=campaigns/<slug>/media/exports/draft_cut.mp4
   make qa-render FILE=campaigns/<slug>/media/exports/draft_cut.mp4 SHEET=campaigns/<slug>/qc/draft-cut-sheet.png
   ```
2. **Draft Delivery Review (`[qa]`):** dispatch fresh `reviewer-agent`
   running [Delivery Review](#delivery-review) on `draft_cut.mp4`, its contact
   sheet, `qa_media.py render` JSON, and `intent.md`.
3. **Optional Virality Predictor (`brain_activity`):** when requested in
   `intent.md` or approved within budget, run Higgsfield `brain_activity` via
   `hf_guard.py run --kind analysis` on the cut to collect hook, attention, and
   retention diagnostics (video-in/text-out analysis).
4. **Draft Approval Gate (`user-draft-gate [effect:approve-draft]`):**
   - Present `media/exports/draft_cut.mp4`, contact sheets, `qa_media.py`
     summary, optional `brain_activity` diagnostics, and
     `make budget-status CAMPAIGN=<slug>` (Draft credits spent vs remaining,
     plus projected `1080p` Final cost vs `Final cap`).
   - Wait for explicit requester approval before unlocking `Final cap` spend.
5. **Final `1080p` Pass (`--phase final`):**
   - Confirm `higgsfield account status` covers `Final cap`.
   - Render approved shots using `final_params` (`1080p`) via parallel disjoint
     `worker-agent` lanes calling `hf_guard.py run --kind video --phase final`,
     running `make qa-clip` + fresh Visual Critic (`view_image`) on every
     `1080p` take (never assuming `1080p` matches `480p` without verifying!).
   - Re-run final assembly and render QA to export the master and separated
     stems (for optional DaVinci Resolve grading):
     ```sh
     make assemble CAMPAIGN=<slug>
     make qa-render FILE=campaigns/<slug>/media/exports/master.mp4 SHEET=campaigns/<slug>/qc/master-sheet.png
     ```
   - Run Final [Delivery Review](#delivery-review) (`reviewer-agent`,
     `fork_turns: "none"`) on `media/exports/master.mp4` + `stems/` +
     `qa_media.py render` JSON + `receipts.jsonl`.

## Human Feedback And Reopen Protocol

When the requester requests changes at Stills, Pilot, or Draft Cut review,
classify the feedback and reopen ONLY the smallest affected layer—never discard
unaffected accepted shots or receipts:

| Feedback class | Example | Action |
| --- | --- | --- |
| **Local shot craft tweak** | "Slow the camera slightly on `s02`" or "Fix finger grip on `s01`" | Keep `intent.md` and `treatment.md` intact; write `prompts/sNN_video_v2.txt`, regenerate only that shot inside remaining `Draft cap`, re-run Visual Critic + re-assemble `draft_cut.mp4`. |
| **Style or beat adjustment** | "Swap `s03` from wide colonnade to tighter profile" | Reopen `treatment.md` / `style-bible.md` and `shotlist.json` strictly for `s03`, preserve accepted `s01` and `s02`, update `tasks.md` (`make ledger-check`), regenerate `s03`, and re-assemble. |
| **Meaning, brand truth, audio, or budget change** | "Add a spoken tagline", "Change leather finish", or "Raise `Final cap`" | Reopen [Intake](intake.md) step 6 (`intent.md` `ready` → `draft`, stable `I<n>`/`A<n>` IDs, `make intent-check`, confirm delta, flip back to `ready`), then surgically invalidate and re-run only the affected shots/audio under [Mid-Pipeline Reopen](../shared/transition.md#mid-pipeline-reopen). |

## Delivery And Completion Summary

Flip `campaigns/<slug>/tasks.md` to `status: done` ONLY after Final Delivery
Review returns `PASS`, `make qa-render` passes, and
`make budget-status CAMPAIGN=<slug>` confirms compliance with both caps. Present
a concise completion summary containing:

- **Master video:** `campaigns/<slug>/media/exports/master.mp4` (resolution,
  FPS, duration, integrated LUFS, true peak);
- **Separated stems:** `campaigns/<slug>/media/exports/stems/` (clean video,
  diegetic/VO, and music stems ready for optional color grading or mastering);
- **Selected shot provenance:** shot-by-shot `selected_job_id` table from
  `shotlist.json`;
- **QA receipts:** `qc/*.json` summaries, Final Delivery Review verdict, and
  optional `brain_activity` score report;
- **Spend audit:** `Draft cap` spent/remaining and `Final cap` spent/remaining
  directly from `receipts.jsonl` (`make budget-status CAMPAIGN=<slug>`).

## Delivery Review

Read-only review adapter for fixed `media/exports/draft_cut.mp4` or
`media/exports/master.mp4`, its `3×2` contact sheet, `stems/`, `qa_media.py
render` JSON, `shotlist.json`, `receipts.jsonl`, and `intent.md`. Return
[Review Result V1](../interfaces/review-result-v1.md):

1. **Technical render gate (`MEDIA_TECH_DEFECT`):** verify locked FPS, exact
   aspect ratio and target resolution, duration match, zero black frames
   (`>= 0.5 s`), zero `frozen_tail` violations (`>= 3.0 s` default via
   `--max-still`, preserving intentional `1.5–2.9 s` closing button holds), zero
   `fully_static_clip` errors (100% frozen clip `>= 1.5 s`), master normalized
   with `loudnorm=I=-14:TP=-1.5:LRA=11` verified by `qa_media.py render` at
   `-14 LUFS (±1.0 LU)` and true peak `<= -1.0 dBTP` (targeting `-1.5 dBTP` for
   headroom), and valid `stems/` outputs.
2. **Visual & continuity audit (`VISUAL_DRIFT_DEFECT` / `CONTINUITY_DEFECT`):**
   inspect `references/*` and the render contact sheet via `view_image` against
   `style-bible.md`'s Cross-Shot Continuity Checklist and `intent.md`'s
   `Concrete viewer scenarios` and `Must not` rules.
3. **Provenance & budget integrity (`BUDGET_CAP` / `REVIEW_HANDOFF_INVALID`):**
   verify every selected shot in `shotlist.json` maps to a real `job_id` in
   `receipts.jsonl` and total spend sits within `Draft cap` (for draft cut) and
   `Final cap` (for master).
4. **Intent closure (`INTENT_GAP`):** verify every `Success signal` criterion
   in `intent.md` is demonstrably met.

Return `PASS` (optionally with non-blocking `FOLLOW_UP` notes), `FAIL` naming
smallest repair owner, or `NEEDS_PARENT` on `INTENT_GAP` / `BUDGET_CAP`.
