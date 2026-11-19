# Review

Internal pre-Dailies technical QC and `taste-log.md` regression filtering
performed by a fresh, read-only `reviewer-agent`. Every review returns
[Review Result V1](../interfaces/review-result-v1.md).

## Internal QC Filter vs Director Taste Sign-Off

The Feedback-Loop Studio separates two distinct judgments so neither corrupts
the other:

| Judgment | Owner | Purpose | Can mark `LOCKED`? |
| --- | --- | --- | --- |
| **Internal QC & Taste-Drift Filter** | Fresh read-only `reviewer-agent` (`fork_turns: "none"`) + `scripts/qa_media.py` | Catch broken anatomy, melted products, frozen frames, loudness violations, `continuity_lock` breaks, failed `test_take_check`s, and `TASTE_REGRESSION`s **before** showing Dailies—so the Director never wastes eyes on AI trash. | **Never.** `PASS` only clears an asset to enter the Dailies Packet. |
| **Creative Taste & Locking Authority** | **Director (Human)** at each round's Dailies Packet | Choose among clean contrasting options (`A / B / C`), judge emotional resonance, charisma, lighting feel, and pacing, steer via `taste-log.md`, approve `--round-cap`, and mark winners `LOCKED`. | **Yes (sole authority).** |

`reviewer-agent` MUST NEVER drop a clean contrasting variant because it prefers
another aesthetic, NEVER guess the Director's taste beyond explicit `brief.md`
and `taste-log.md` rules, and NEVER substitute for human Dailies approval.

## Independence And Fresh Context

- **Always fresh (`fork_turns: "none"`).** Dispatch every internal review to a
  fresh read-only `reviewer-agent` (`reasoning_effort: high`). A producing
  `worker-agent` or prompt author never self-approves its own renders.
- **Zero builder rationale.** Pass strictly:
  1. the fixed candidate(s) (Lookbook variant PNGs, keyframe stills, `3×2`
     contact sheets, or assembled render + sheet);
  2. authoritative truth (`campaigns/<slug>/brief.md`,
     `campaigns/<slug>/taste-log.md`, cited `brands/<brand>/brand.md` and
     `brands/<brand>/taste.md`, `style-bible.md`, `shotlist.json`, and
     `LOCKED` reference/Lookbook images);
  3. objective probe data (`scripts/qa_media.py` JSON output and receipt
     metadata: `job_id`, `asset_id`).
  **Omit** prompt author justifications, retry stories, and Root Producer chat
  turns.
- **Read-only boundary.** `reviewer-agent` never edits files, never runs paid
  generations, and never changes `shotlist.json` status. Missing candidate
  files, `qa_media.py` JSONs, contact sheets, or `taste-log.md` return
  `REVIEW_HANDOFF_INVALID` without downgrading.

## Visual Critic Protocol

Every visual/audio deliverable across `R2`–`R5` passes a two-layer internal
filter before entering a Dailies Packet:

### Layer 1 — Deterministic Media Gate (`scripts/qa_media.py`)

- **Video clips (`R4A`, `R4B`, `R5`):**
  ```sh
  make qa-clip FILE=<path.mp4> SHEET=<campaigns/<slug>/qc/sNN-tK-sheet.png>
  ```
  Verifies resolution, aspect ratio, FPS, duration, audio stream health, black
  frames (`>= 0.5 s`), **`fully_static_clip`** (hard error on 100% frozen clips
  `>= 1.5 s`), and **`frozen_tail`** (`>= 3.0 s` default via `--max-still`,
  preserving intentional `1.5–2.9 s` closing button holds), and renders a `3×2`
  evenly sampled PNG contact sheet.
- **Voiceover tracks (`R3`):**
  ```sh
  make qa-voice FILE=<path.wav> WINDOW=<sec>
  ```
  Measures active speech duration using 100ms RMS energy against `WINDOW`. If
  speech overflows, tighten script copy and regenerate—**never** apply FFmpeg
  `atempo`.
- **Assembled cuts (`draft_cut.mp4` in `R4B`, `master.mp4` in `R5`):**
  ```sh
  make qa-render FILE=<path.mp4> SHEET=<campaigns/<slug>/qc/render-sheet.png>
  ```
  Verifies all clip metrics plus broadcast loudness normalized via
  `loudnorm=I=-14:TP=-1.5:LRA=11`: integrated loudness within **`-14 LUFS
  (±1.0 LU)`** and true peak **`<= -1.0 dBTP`** (targeting `-1.5 dBTP` headroom),
  plus a full-spot contact sheet.
- **Comparison grids (`R2` Lookbook, `R3` Stills Strip):**
  ```sh
  make lookbook FILES="..." LABELS="A,B,C" OUT=<out.png>
  ```
  Produces clean, uniformly labeled comparison boards for Dailies.

Repair deterministic `MEDIA_TECH_DEFECT` failures before spending multimodal
review effort on single clips (at `R4B`/`R5` render assembly, run deterministic
QA and Visual Critic together on the fixed export).

### Layer 2 — Multimodal Visual Critic (`view_image`)

Fresh `reviewer-agent` calls Codex `view_image` on `LOCKED` references
alongside candidate Lookbook PNGs, stills, or `3×2` contact sheets, checking:

1. **All three `continuity_lock` invariants (`shotlist.json`):**
   - *Product:* physical form, matte/satin/gloss finish, scale against hands,
     label/wordmark facing and legibility (`VISUAL_DRIFT_DEFECT`).
   - *Lighting & palette:* key-light side (`screen left`/`right`/`overhead`),
     color temperature, shadow roll-off, palette anchors (`CONTINUITY_DEFECT` /
     `VISUAL_DRIFT_DEFECT`).
   - *Space, cast & axis:* environment architecture, cast/wardrobe markers,
     active hand, screen travel direction, and 180-degree axis across adjacent
     shots (`CONTINUITY_DEFECT`).
2. **`taste-log.md` regression check (`TASTE_REGRESSION`):**
   - Verify the candidate honors every active `More of`, `Change / Steer`, and
     `Never` rule in `campaigns/<slug>/taste-log.md` (and `brands/<brand>/taste.md`).
   - Any reversion to a Director-rejected style or ignored steer fails with
     `TASTE_REGRESSION`.
3. **Risky-shot `test_take_check` (`R4A` Pilot & `R5` `1080p` re-check):**
   - Whenever `shotlist.json` declares `test_take_check != null`, explicitly
     falsify `test_take_check.risk` and confirm `test_take_check.pass_check`
     across contact-sheet panels 1–6.
4. **Anatomy, physics & `Must not` compliance:**
   - Natural fingers/hands/faces, believable object gravity and creases, zero
     temporal morphing across panels 1–6, and zero `brief.md` `Must not`
     violations.

Emit [Review Result V1](../interfaces/review-result-v1.md) citing exact panel
numbers (`panel 1..6`), `TL-NN` rules, `continuity_lock` clauses, and
`qa_media.py` metrics.

## Internal Retry Bounds & `adjudicator-agent`

- **Bounded auto-retries:** internal defect repairs are bounded simultaneously
  by `Max auto-retries/asset` in `brief.md` and the active round's approved
  `--round-cap`. Never silently retry past either limit.
- **Diagnose before regenerating:** fix the root cause (prompt beat, reference
  anchoring, anti-IP wording) before re-running `hf_guard.py`; never repeat an
  identical broken call.
- **Fresh recheck:** every regenerated take gets a fresh `qa_media.py` report +
  fresh `reviewer-agent` pass.
- **Honest conflict adjudication (`adjudicator-agent`):** only when an internal
  QC finding conflicts with remaining round budget (for example, whether a
  borderline take is worth spending the final retry or should be surfaced
  honestly in Dailies with a `CONCERN` note), dispatch one fresh read-only
  `adjudicator-agent` (`reasoning_effort: xhigh`,
  [Adjudication Result V1](../../agent-harness.md#adjudication-result-v1)).
  Never hide a real defect from the Director.

## Pre-Dailies Filter Map

| Round | Filtered artifact | Layer 1 (`qa_media.py`) | Layer 2 (`reviewer-agent` `view_image`) |
| --- | --- | --- | --- |
| `R2` | Lookbook variants `A / B / C` | `lookbook` grid after filtering | Reference fidelity, anatomy, `Must not`, `TASTE_REGRESSION` |
| `R3` | Keyframe stills `s01..sN`, VO, `animatic.mp4` | `voice` (100ms RMS, zero `atempo`), `lookbook` strip | `LOCKED` Lookbook/reference match, `continuity_lock`, `TASTE_REGRESSION` |
| `R4A` | Pilot clip(s) (`test_take_check != null`) | `clip` (`fully_static_clip`, `frozen_tail >= 3.0s`, `3×2` sheet) | `test_take_check` pass/fail, `continuity_lock`, `TASTE_REGRESSION` |
| `R4B` | Remaining draft clips + `draft_cut.mp4` | `clip` per shot + `render` (`-14 ± 1.0 LUFS`, `<= -1.0 dBTP`) | Cross-shot continuity, `continuity_lock`, `TASTE_REGRESSION` |
| `R5` | Upgraded `1080p` clips + `master.mp4` | `clip` per upgraded shot + `render` (`-14 ± 1.0 LUFS`, `<= -1.0 dBTP`) | Resolution-upgrade drift vs `LOCKED` stills/drafts, `continuity_lock`, `TASTE_REGRESSION` |
