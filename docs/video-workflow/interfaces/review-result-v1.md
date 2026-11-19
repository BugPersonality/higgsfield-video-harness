# Review Result V1

Every fresh read-only internal QC pass (`reviewer-agent`, `fork_turns: "none"`)
inspecting Lookbook variants (`R2`), keyframe stills (`R3`), `3×2` video contact
sheets (`R4`–`R5`), or assembled renders returns one structured result.

**Internal filter, never human approval:** `reviewer-agent` acts as an Assistant
Director / technical QC filter catching obvious AI defects, continuity breaks,
and `taste-log.md` regressions BEFORE assembling each round's
[Dailies Packet](dailies-packet-v1.md). A `PASS` clears an asset to be shown to
the Director—it **never** marks an asset `LOCKED` or substitutes for human taste
selection.

```text
candidate: <fixed media path, lookbook variant, still, 3x2 contact sheet, or render + job_id>
verdict: PASS | CONCERNS | FAIL | NEEDS_PARENT | REVIEW_HANDOFF_INVALID
findings: <anchored surviving findings grouped by asset/axis, or none>
evidence_boundary: <exact files inspected, images viewed via view_image, qa_media.py JSONs, brief.md, taste-log.md TL-NN anchors, and receipts checked>
reopen_owner: <Worker(<asset_id>) | Root Producer | R0 | R1 | R2 | R3 | R4 | R5 | none>
```

Each surviving finding cites:
1. **Anchor:** exact asset/shot ID (`lb_*`, `s01..sN`), contact-sheet panel
   (`panel 1..6` / timestamp), `qa_media.py` metric, or `taste-log.md` entry
   (`TL-NN`);
2. **Defect class:** one exact code from the closed taxonomy below;
3. **Invariant broken:** which `brief.md` rule, `taste-log.md` steer/never,
   `continuity_lock` clause, `test_take_check`, or media threshold failed;
4. **Smallest repair owner:** narrowest worker or round owner that can close
   the defect without touching `LOCKED` assets;
5. **Falsifier evidence:** exact visual observation (`view_image`), probe value,
   or quote proving the defect.

## Closed Video Defect Taxonomy

Every finding MUST use one of these exact nine codes:

| Code | Meaning | Routing |
| --- | --- | --- |
| `MEDIA_TECH_DEFECT` | Deterministic media/audio failure caught by `scripts/qa_media.py` or `ffprobe`: wrong resolution, aspect ratio, FPS, or duration; black frames (`>= 0.5 s`); `frozen_tail` (`>= 3.0 s` default via `--max-still`, preserving intentional `1.5–2.9 s` closing button holds) or `fully_static_clip` (100% frozen clip `>= 1.5 s`); silent track; audio clipping; master true peak `> -1.0 dBTP` (normalized via `loudnorm=I=-14:TP=-1.5:LRA=11`, targeting `-1.5 dBTP` headroom); integrated loudness outside `-14 LUFS (±1.0 LU)`; or VO exceeding shot window. | `FAIL`; repair locally (assembly/mix) or regenerate owning unlocked asset within `Max auto-retries/asset` (never use `atempo` on VO). |
| `VISUAL_DRIFT_DEFECT` | Subject, product, logo/wordmark, face/hand anatomy, material finish, or `test_take_check.pass_check` diverges from `LOCKED` references or `style-bible.md` (for example extra fingers, melted hardware, glossy leather instead of matte, garbled wordmark). | `FAIL`; refine prompt/references and regenerate owning unlocked asset within `Max auto-retries/asset` and active `--round-cap`. |
| `TASTE_REGRESSION` | Output contradicts an active `More of`, `Change / Steer`, `Never`, or `Approved / LOCKED` rule recorded in `campaigns/<slug>/taste-log.md` (or inherited `brands/<brand>/taste.md`)—for example reverting to glossy neon lighting after `TL-01` recorded `Never: neon rim light`. | `FAIL`; revise prompt/references to honor the latest `TL-<NN>` rule and regenerate the unlocked asset inside retry bounds before showing Dailies. |
| `POLICY_BLOCK` | Higgsfield safety, moderation, or IP/trademark filter rejected generation (`ip_detected`, likeness, brand trademark, or policy refusal). | `FAIL` or `NEEDS_PARENT`; apply anti-IP visual phrasing sanitization (via `video-direction` / `specialist-agent`) or swap offending reference asset. |
| `CONTINUITY_DEFECT` | Cross-shot break across adjacent beats against `continuity_lock`: lighting direction flip, wardrobe/cast drift, product scale jump, active-hand/180-degree axis flip, mismatched environment, or audio seam pop. | `FAIL`; regenerate only the discordant unlocked shot(s) anchored to adjacent `LOCKED` stills/frames, or repair the assembly seam. |
| `BUDGET_CAP` | Required generation or repair exceeds `Campaign cap`, approved `--round-cap`, or `Max auto-retries/asset`, or encounters `asset_locked` on a `LOCKED` asset. | `NEEDS_PARENT`; halt paid calls immediately and surface cleanly to the Root Producer / Director under [Budget Authority](../shared/budget-authority.md). |
| `CONCERN` | Bounded non-blocking craft risk or borderline imperfection remaining after retry budget is spent (for example slight background grain variation on an otherwise strong take). | `CONCERNS`; surfaces transparently in Block 2 (`Filtered internally`) of the Dailies Packet so the Director decides whether to accept or fund a micro re-roll. |
| `FOLLOW_UP` | Optional polish suggestion outside current round requirements that does not violate `brief.md`, `taste-log.md`, or technical thresholds. | Never blocks `PASS`; optional note for later refinement. |
| `REVIEW_HANDOFF_INVALID` | Candidate asset, `qa_media.py` JSON report, `3×2` PNG contact sheet, `brief.md`, `taste-log.md`, or `shotlist.json` is missing, unreadable, or mismatched. | Returned **without** a `PASS`/`FAIL` verdict; names the owner (`Worker(<asset_id>)` or `Root Producer`) that must fix the handoff before re-checking. |

## Verdict Rules

- **`PASS`:** Zero blocking defects (`MEDIA_TECH_DEFECT`, `VISUAL_DRIFT_DEFECT`,
  `TASTE_REGRESSION`, `POLICY_BLOCK`, `CONTINUITY_DEFECT`, `BUDGET_CAP`) and
  zero surviving `CONCERN`s. The asset is clean enough to enter the round's
  **Dailies Packet** for human Director judgment.
- **`CONCERNS`:** Zero blocking technical/policy/taste defects, or a minor
  borderline caveat evaluated by `adjudicator-agent` when remaining round budget
  makes another retry unwise. Must be disclosed honestly in Dailies Block 2.
- **`FAIL`:** One or more blocking defects fixable inside the active round's
  `--round-cap` and `Max auto-retries/asset`. Triggers targeted diagnosis and
  retry—never shown to the Director as an unflagged option.
- **`NEEDS_PARENT`:** `BUDGET_CAP`, `asset_locked`, repeated `POLICY_BLOCK`
  after sanitization, or missing source truth requiring Root Producer recovery
  or a Director decision in Dailies.
- **`REVIEW_HANDOFF_INVALID`:** Broken review package; never downgrade missing
  `qa_media.py` receipts, missing contact sheets, or unreadable `taste-log.md`
  files to `CONCERN` or `FOLLOW_UP`.
