# Artifacts

Defines what campaign state persists under `campaigns/<slug>/`, how Git and
gitignored `media/` separate text contracts from binary renders, and how
artifacts transition cleanly across phases and mid-pipeline reopens.

## Campaign Artifact Map

Every structured or orchestrated campaign lives under `campaigns/<slug>/`:

| Path | Tracked in Git? | Owner | Purpose |
| --- | --- | --- | --- |
| `intent.md` | Yes | Root Orchestrator ([Intake](../phases/intake.md)) | Requester meaning, visual truth, `Must not`, Budget Envelope, `I<n>`, `A<n>` ([Video Intent V1](../interfaces/intent-v1.md)) |
| `treatment.md`, `style-bible.md` | Yes | Phase 1 ([Creative Definition](../phases/creative-definition.md)) | Competing creative lanes, `D<n>` decisions, beat map, lighting/palette/audio/continuity grammar ([Treatment V1](../interfaces/treatment-v1.md)) |
| `script.md`, `storyboard.md` *(optional commercial track)* | Yes | Phase 1 (`ad-script`, `ad-storyboard`) | Timed three-column script (`read-aloud budget`, `mute test`) and continuity-locked `S01..SN` storyboard (`Continuity Lock`, `Test-take check`) |
| `shotlist.json` | Yes | Phase 2 authoring / Root Orchestrator runtime updates | Live model schemas, `continuity_lock`, `test_take_check`, reference UUID graph, draft/final params, credit quotes, selected takes ([Shotlist V1](../interfaces/shotlist-v1.md)) |
| `tasks.md`, `tasks/TNN-*.md` | Yes | Phase 3 authoring / Root Orchestrator runtime updates | Topological DAG, `[effect:...]` gates, disjoint `Mutable owners`, locks, validation oracles ([Production Ledger V1](../interfaces/task-ledger-v1.md)) |
| `prompts/*.txt` | Yes | Phase 2 authoring / shot worker bounded revisions | Versioned still prompts (`sNN_still_v1.txt`), motion prompts (`sNN_video_v1.txt`), VO scripts, and music prompts |
| `qc/*.json` | Yes | Workers / Reviewers | Deterministic `scripts/qa_media.py` probe reports and structured Visual Critic JSON/text logs |
| `receipts.jsonl` | Yes | `scripts/hf_guard.py` (exclusive lock) | Append-only reservation-before-submit (`status: "reserved"`, `reservation_id`) and terminal (`completed`, `download_failed`, `rejected`, `in_progress`) audit log recording `ts`, `shot`, `kind`, `phase`, `model`, `is_workflow`, `params_hash`, `job_id`/`upload_id`, `estimated_credits`, `actual_credits`, `credits`, `url`, `out`, and `attempt` |
| `qc/*.png` | **No (gitignored)** | `scripts/qa_media.py` | Generated `3×2` contact sheets inspected by `reviewer-agent` via `view_image` |
| `media/references/*` | **No (gitignored)** | Requester | Source product, character, or environment photos uploaded in Wave 1 |
| `media/stills/*`, `media/shots/*`, `media/audio/*` | **No (gitignored)** | Disjoint `worker-agent` lanes | Raw generated stills, draft/final video takes, VO tracks, and music/SFX stems |
| `media/exports/animatic.mp4`, `draft_cut.mp4`, `master.mp4`, `stems/` | **No (gitignored)** | Assembly worker (`scripts/assemble.sh`) | Optional 0-video-credit still animatic, assembled preview cut, final `1080p` master, and separated stems for optional grading |

## Artifact Lifecycle V1

Use one explicit status on every decision or ledger artifact (`intent.md`,
`treatment.md`, `style-bible.md`, `tasks.md`):

| Status | Meaning | Permitted consumers |
| --- | --- | --- |
| `draft` | Currently being authored, grilled, or repaired. | Authoring owner and pre-gate reviewers only; never consumed by downstream phases or `hf_guard.py`. |
| `ready` | All owned decisions are closed, mechanical checks pass, and independent review cleared. | Authorized for downstream phases (`intent.md` at `ready` unlocks Phase 1 and `hf_guard.py` budget authority). |
| `blocked` | A required upstream decision, taste fork (`B1..Bn`), brand asset, or budget/capability limit prevents safe progress. | Returns to Root Orchestrator / named `reopen_owner`; downstream phases pause on blocked branches. |
| `done` | Execution, final `qa_media.py render`, Final Delivery Review (`PASS`), and budget audit are complete (`tasks.md` only). | Read-only historical delivery record; status alone never substitutes for QA receipts. |

Only the owning phase or Root Orchestrator flips an artifact's `status`. Any
material upstream change moves affected `ready` artifacts back to `draft` or
`blocked` before edits begin so an interrupted session cannot read stale truth.

## Git vs Media Boundary

- **Git tracks text, never media binaries.** Keeping `intent.md`,
  `treatment.md`, `style-bible.md`, `shotlist.json`, `tasks.md`, `prompts/`,
  `qc/*.json`, and `receipts.jsonl` in Git makes every creative iteration,
  prompt refinement, QA failure, and credit spend diffable and auditable.
- **Binary artifacts stay gitignored.** Keep `.png`, `.jpg`, `.mp4`, `.mov`,
  `.wav`, and `.mp3` outputs under `campaigns/<slug>/media/` and contact-sheet
  `.png`s under `campaigns/<slug>/qc/` (gitignored). Never embed base64 images,
  private personal face photos, API keys, or OAuth tokens into Git-tracked
  files.
- **No silent copy-paste of live schemas.** Reference `brands/<brand>/brand.md`,
  `docs/cinema-presets.json`, and `prompts/sNN_*.txt` by relative path rather
  than duplicating mutable text across multiple artifacts.

## In-Place Reopen Discipline

When requester feedback, a Visual Critic `INTENT_GAP`, or a `Blocked Exit`
changes scope, brand truth, audio, or shot specs mid-campaign:

1. **Reconcile in place.** Update the authoritative active section of the
   owning artifact (`intent.md`, `treatment.md`, `style-bible.md`,
   `shotlist.json`, or `tasks.md`) rather than appending contradicting addenda
   at the bottom.
2. **Preserve ID stability.** Never renumber surviving `I<n>`, `A<n>`, `D<n>`,
   `s01..sN`, or `TNN` identifiers. Add new sequential IDs and mark overturned
   decisions explicitly (`Superseded by I<m>` or `Superseded by D<m>`).
3. **Preserve valid shots and receipts.** Never delete `receipts.jsonl` entries
   or discard accepted unaffected stills/shots in `media/`. Version updated
   prompt files (`prompts/s02_video_v2.txt`), update `shotlist.json` only for
   invalidated shots, and re-run mechanical checks (`make intent-check`,
   `make ledger-check`) before resuming under [Review](review.md) and
   [Transition](transition.md#mid-pipeline-reopen).
