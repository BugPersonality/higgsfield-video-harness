# Review Result V1

Every fresh independent review (`reviewer-agent`, `fork_turns: "none"`) across
Intake, Creative Definition, Production Design, Planning, Visual Critic QA, and
Final Delivery returns one structured result:

```text
candidate: <fixed artifact path, shot/take path + job_id, contact sheet, or export render>
verdict: PASS | CONCERNS | FAIL | NEEDS_PARENT | REVIEW_HANDOFF_INVALID
findings: <anchored surviving findings grouped by axis or shot, or none>
evidence_boundary: <exact files inspected, contact sheets viewed via view_image, qa_media.py JSONs, and receipts checked>
reopen_owner: <Intake | Creative Definition | Production Design | Planning | Worker(sNN) | Orchestrator | none>
```

Each surviving finding cites:
1. **Anchor:** exact file/section, shot ID (`s01..sN`), contact-sheet panel
   (`panel 1..6` / timestamp), or `qa_media.py` metric;
2. **Defect class:** one exact code from the closed taxonomy below;
3. **Outcome impact:** which `intent.md` invariant, `style-bible.md` rule, or
   technical threshold failed;
4. **Smallest repair/reopen owner:** the narrowest phase or shot worker that
   can close the finding without widening scope;
5. **Falsifier evidence:** exact visual observation (`view_image`), probe value,
   or quote proving the defect.

## Closed Video Defect Taxonomy

Every finding MUST use one of these exact classifications:

| Code | Meaning | Routing |
| --- | --- | --- |
| `MEDIA_TECH_DEFECT` | Deterministic media/audio failure caught by `scripts/qa_media.py` or `ffprobe`: wrong resolution, aspect ratio, FPS, or duration; black frames (`>= 0.5 s`); `frozen_tail` (`>= 3.0 s` default via `--max-still`, preserving intentional `1.5–2.9 s` closing button holds) or `fully_static_clip` (100% frozen clip `>= 1.5 s`); silent track; audio clipping; master true peak `> -1.0 dBTP` (normalized via `loudnorm=I=-14:TP=-1.5:LRA=11`, targeting `-1.5 dBTP` for headroom); integrated loudness outside `-14 LUFS (±1.0 LU)`; or VO exceeding shot window. | `FAIL`; repair locally (assembly/mix) or regenerate owning shot within retry cap (never use `atempo` on VO). |
| `VISUAL_DRIFT_DEFECT` | Subject, product, logo/wordmark, face/hand anatomy, color palette, or material finish diverges from `references/` or `style-bible.md` (for example glossy leather instead of matte, garbled text, extra fingers, wrong hardware color). | `FAIL`; refine prompt/references and regenerate owning shot inside `Max auto-retries/shot`. |
| `POLICY_BLOCK` | Higgsfield safety, moderation, or IP/trademark filter rejected generation (`ip_detected`, likeness, brand trademark, or policy refusal). | `FAIL` or `NEEDS_PARENT`; apply anti-IP visual phrasing sanitization (via `video-direction` / `specialist-agent`) or substitute offending reference asset. |
| `CONTINUITY_DEFECT` | Cross-shot break across adjacent beats: lighting direction flip, wardrobe change, product scale jump, mismatched background architecture, music/foley seam pop, or pacing break. | `FAIL`; regenerate only the discordant shot(s) anchored to adjacent accepted keyframes or repair the assembly seam. |
| `INTENT_GAP` | Missing, ambiguous, or contradicted requester meaning, brand truth, spoken pronunciation, taste fork, or `Must not` boundary that cannot be settled without the user. | `FAIL` / `NEEDS_PARENT`; reopen [Intake](../phases/intake.md) (`reopen_owner: Intake`) with concrete viewer choices. |
| `BUDGET_CAP` | Planned cost or required repair exceeds `Draft cap`, `Final cap`, or `Max auto-retries/shot` in `intent.md`. | `NEEDS_PARENT`; stop paid calls immediately and escalate to Root Orchestrator / requester under [Budget Authority](../shared/budget-authority.md). |
| `CONCERN` | Bounded downstream craft risk or external uncertainty over an otherwise closed candidate (paired with owner and closing check). | `CONCERNS`; permits phase movement without blocking, carried forward into `Global constraints` or `Carried Concerns`. |
| `FOLLOW_UP` | Optional creative polish outside the current packet or acceptance bar that does not falsify any requirement. | Never blocks `PASS`; log as optional post-delivery idea. |
| `REVIEW_HANDOFF_INVALID` | Candidate artifact, `qa_media.py` JSON receipt, `3×2` PNG contact sheet, or authoritative upstream contract is missing, unreadable, or mismatched. | Returned **without** a `PASS`/`FAIL` verdict; names the owner (`Worker(sNN)` or `Orchestrator`) that must fix the handoff before re-reviewing. |

## Verdict Rules

- **Preparation phases** (Cold-Start Intent Review, Treatment & Style Review,
  Shotlist & Budget Review, Task Readiness Review) use `PASS | CONCERNS | FAIL`
  (plus `REVIEW_HANDOFF_INVALID` on broken handoffs).
  - `PASS`: zero blocking defects (`MEDIA_TECH_DEFECT`, `VISUAL_DRIFT_DEFECT`,
    `POLICY_BLOCK`, `CONTINUITY_DEFECT`, `INTENT_GAP`, `BUDGET_CAP`) and zero
    open `CONCERN`s.
  - `CONCERNS`: zero blocking defects; only bounded `CONCERN` entries with named
    owners and closing checks.
  - `FAIL`: one or more blocking defects; owner must repair or reopen before
    moving phases.
- **Production Visual Critic & Final Delivery Review** use
  `PASS | FAIL | NEEDS_PARENT` (plus `REVIEW_HANDOFF_INVALID`).
  - `PASS`: every checked technical metric and `view_image` visual invariant
    passes; `FOLLOW_UP` notes may accompany `PASS`.
  - `FAIL`: one or more in-scope `MEDIA_TECH_DEFECT`, `VISUAL_DRIFT_DEFECT`,
    `POLICY_BLOCK`, or `CONTINUITY_DEFECT` findings solvable inside current
    authority and retry budget.
  - `NEEDS_PARENT`: `INTENT_GAP`, `BUDGET_CAP`, unresolvable `POLICY_BLOCK`, or
    missing upstream proof requiring Root Orchestrator recovery or requester
    escalation.
- **No downgrading:** a missing `qa_media.py` receipt, unreadable contact sheet,
  or unverified brand invariant is never downgraded to `CONCERN` or `FOLLOW_UP`.
