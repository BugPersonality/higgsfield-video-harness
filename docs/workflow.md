# Studio Workflow (`R0` → `R5`)

Run every multi-shot video, commercial, or branded spot through six interactive
rounds between the **Director (human)** and **Production Crew (agents)**. Keep
the Root Producer in one continuous session across `R0`–`R5` so the Director's
verbatim *why* stays a primary source. Each round executes full technical craft
internally and stops with one **Dailies Packet** for taste feedback and
next-round credit approval.

For JSON shapes and CLI flags, inspect the living fixtures and tools directly:
[`campaigns/example-product-spot/`](../campaigns/example-product-spot),
`scripts/check-brief.py`, `scripts/check-campaign.py`, and
`scripts/hf_guard.py --help`.

## The 6 Rounds

### R0 — Brief (`0 cr.`)
- **Craft:** Ground via `evidence-agent` in `higgsfield account status`,
  `workspace list`, `brands/<brand>/{brand.md,taste.md}`, and local photos under
  `media/references/`. Run light [Grilling](grilling.md) (3–5 meaning-only
  questions: viewer effect, brand truth, spoken pronunciation, taboos,
  `Campaign cap`). Scaffold with `make campaign-init`, write plain-language
  `brief.md` (`status: draft`), seed `taste-log.md` from `brands/<brand>/taste.md`
  when present, and run `make brief-check CAMPAIGN=<slug>`.
- **Dailies 0:** Short `brief.md` card + seeded taste anchors + `Campaign cap`
  confirmation. Once confirmed, flip `brief.md` to `status: active` and re-run
  `make brief-check CAMPAIGN=<slug>`.
- *Done when:* Director confirms `Dailies 0`, `brief.md` is `status: active`,
  and `make brief-check` passes with zero jargon and zero requester-owned open
  questions.

### R1 — Story & Cost Ticket (`0 cr.`)
- **R1A (Concept):** For commercials, run `ad-references` (skip if Director
  supplied an angle or reference spots) → `ad-concepts` (4–5 orthogonal
  swap-tested pitches); for non-commercials, draft 2–3 contrasting treatments.
  Stop with **Dailies 1A** so the Director picks or blends a direction.
- **R1B (Blueprint & Quote):** Run `ad-script` (`Time | Video | Audio`,
  read-aloud budget, mute test) → `ad-storyboard` (`Continuity Lock`,
  `test_take_check`) → `style-bible.md`. Dispatch `evidence-agent` to inspect
  live schemas (`model get` / `workflow get` / `voices list`) and run live
  `higgsfield generate cost` per round (using cost-affecting params or UUIDs
  only—never pass private local file paths, which `generate cost` auto-uploads).
  Write `shotlist.json` + initial `prompts/` (choosing each shot's `R4 → R5`
  escalation path upfront per
  [Mastering & Upscaling](../.agents/skills/higgsfield-cli/references/mastering-and-upscaling.md)
  so drafts never dead-end in `480p` upscaling) and verify
  `make campaign-check CAMPAIGN=<slug>` (`R2 + R3 + R4 + R5 <= Campaign cap`).
- **Dailies 1B:** Readable beat-by-beat story + exact round-by-round price list
  + approval ask for uploading local `media/references/` photos (if any) and
  setting `R2` (or `R3` if `R2` is skipped) `--round-cap`.
- *Done when:* Director picks a direction (`1A`), `make campaign-check` passes
  (`1B`), and Director approves reference uploads (if any) plus the next round's
  `--round-cap`.

### R2 — Casting & World Lookbook (`~20–45 cr.`, skip if `lookbook: []`)
- **Skip rule:** Skip `R2` automatically when real photos in `media/references/`
  already cover every hero object, character, and location (`lookbook: []`);
  upload those photos at the start of `R3` via `hf_guard.py upload --round R3`
  and save `references[].upload_id` in `shotlist.json`.
- **Craft:** Upload any approved local `media/references/` photos needed for
  Lookbook generation via `hf_guard.py upload --round R2` (`references[].upload_id`).
  Dispatch parallel `worker-agent` lanes to generate 2–3 contrasting variants
  (`--variant A`, `B`, `C`, `--version 1`) per `lookbook[]` entity via
  `hf_guard.py run --round R2 --round-cap <cap>`. Filter defects and
  `TASTE_REGRESSION`s via fresh `reviewer-agent`, then build one labeled grid
  with `make lookbook FILES="..." OUT=campaigns/<slug>/qc/lookbook.png LABELS="A,B,C"`.
- **Dailies 2:** `qc/lookbook.png` + comparative picks + `R3` Cost Ticket.
  Upload chosen winners via `hf_guard.py upload --round R2`, record
  `approved_variant`, `approved_take`, and `approved_upload_id`, and set
  `status: "LOCKED"` in `shotlist.json`. When the storyboard covers reverse
  angles, multi-angle interiors/buildings, time-of-day shifts, close-up props,
  or recurring characters with head turns and expressive acting, expand the
  locked Master(s) into clean **Reverse Wall / Multi-Angle / State / Scale
  plates** (`3d_jutsu_angles`, `nano_banana_2_shots`, `nano_banana_2_relight`,
  `image_decompose`) and **Character Bible / Expression Calibration plates** (or
  `Soul ID` / Kling Elements) per
  [Locations, Buildings & Props](../.agents/skills/video-consistency/references/locations-and-props.md)
  and
  [Characters & Expressions](../.agents/skills/video-consistency/references/characters-and-expressions.md)
  before staging `R3` stills.
- *Done when:* every `lookbook[]` entity is `LOCKED` with a verified
  `approved_upload_id` (or `R2` is skipped with `lookbook: []`) and Director
  approves `R3` `--round-cap`.

### R3 — Keyframe Stills & Still Animatic (`~30–50 cr.`, `0` video cr.)
- **Craft:** If `R2` was skipped, upload approved local `media/references/` via
  `hf_guard.py upload --round R3` (`references[].upload_id`). Generate `s01..sN`
  stills in parallel via `hf_guard.py run --round R3 --round-cap <cap>` bound to
  `LOCKED` UUIDs, `Continuity Lock`, and `taste-log.md`. Generate enabled VO
  (verify with `scripts/qa_media.py voice <wav> --window <sec> --json`; rewrite
  copy and regenerate on overflow rather than speeding up with `atempo`) and
  enabled rough music. Filter via fresh `reviewer-agent`, record
  `still.selected_take` and audio `selected_file` in `shotlist.json`, build
  `qc/stills_strip.png` (`make lookbook`), and render `media/exports/animatic.mp4`
  via `make animatic CAMPAIGN=<slug>` (`0` video credits).
- **Dailies 3:** `stills_strip.png` + `animatic.mp4` + `R4A` (or `R4` if zero
  shots carry `test_take_check`) Cost Ticket. Lock approved stills/audio
  (`status: "LOCKED"`) and upload locked stills via `hf_guard.py upload --round R3`.
- *Done when:* Director locks all required stills and audio after reviewing
  `animatic.mp4`, locked stills are uploaded, and Director approves `R4A`/`R4`
  `--round-cap`.

### R4 — Motion Dailies (`~45–90 cr.`)
- **Draft-to-Final planning:** Plan `R5` escalation *before* shooting `R4` (see
  [Mastering & Upscaling](../.agents/skills/higgsfield-cli/references/mastering-and-upscaling.md)).
  Prefer Web `Unlimited` (`0 cr.`) first, then `720p` economy drafts
  (`seedance_2_0_mini`, `kling_4_0_flash`, `wan3_0`), or **`seedance_2_5`
  `--draft true`** when an approved take must escalate 1:1 into native `1080p`
  via `--draft_job_id` (CLI `cinematic_studio_video_4_0` omits `--draft_job_id`).
- **R4A (Risk-First Pilot):** Shoot shots with `test_take_check != null` first
  at draft settings (`720p` or `seedance_2_5 --draft true`) via `hf_guard.py
  run --round R4A --round-cap <r4a_cap>`. Probe with `scripts/qa_media.py clip
  <mp4> --sheet <png> --json` and inspect via fresh `reviewer-agent`. Stop with
  **Dailies 4A** (pilot clip + `R4B` Cost Ticket). *(Skip `R4A` only when zero
  shots carry `test_take_check` and Director approved batch `--round R4` on
  Dailies 3.)*
- **R4B (Batch Draft & Cut):** Shoot remaining unlocked shots in parallel via
  `hf_guard.py run --round R4B --round-cap <r4b_cap>` (or `--round R4` when
  `R4A` was skipped). Probe each clip (`qa_media.py clip --sheet <png> --json`),
  filter via fresh `reviewer-agent`, record `video.selected_take` in
  `shotlist.json`, and assemble `draft_cut.mp4` via `make assemble
  CAMPAIGN=<slug> OUT=campaigns/<slug>/media/exports/draft_cut.mp4` (`-14 LUFS`,
  `<= -1.0 dBTP`).
- **Dailies 4B:** Playable `draft_cut.mp4` + **per-shot native `1080p` upgrade
  prices** for `R5` (never offer `480p → 1080p` pixel upscaling as a budget
  shortcut; quote native `1080p` options such as Web `Unlimited`, `kling4_0`,
  `wan3_0`, or `seedance_2_5 --draft_job_id`). Mark shots kept as-is (no `R5`
  upgrade) `LOCKED`; keep shots scheduled for `R5` `1080p` upgrade unlocked
  (`IN_REVIEW` or `ITERATING`, bumping `version` if prompt/parameters change) so
  `hf_guard.py` permits `R5`.
- *Done when:* pilot passes Dailies 4A (when applicable), Director approves cut
  rhythm in `draft_cut.mp4`, kept shots are `LOCKED`, upgrade targets stay
  unlocked, and Director approves `R5` `--round-cap`.

### R5 — Final Master (`1080p`, approved quote)
- **Craft:** Upgrade **only** Director-approved unlocked shots to **native
  `1080p`** via `hf_guard.py run --round R5 --round-cap <r5_cap>` following the
  5-step runbook in
  [Mastering & Upscaling](../.agents/skills/higgsfield-cli/references/mastering-and-upscaling.md)
  (Web `Unlimited`, `seedance_2_5 --draft_job_id --bitrate_mode high`,
  `kling4_0` / `wan3_0` / `veo3_1` / `wan3_0_prime`, `kling4_0 --mode
  video-edit` motion-locked rescue, or direct `cinematic_studio_video_4_0`
  `--bitrate_mode high`). Never pixel-upscale `480p` drafts; pixel upscaling
  is allowed only for clean `>= 720p` inputs (`<= 2×`) after passing all 6
  Upscale Gate checks and a 1-shot `1:1` `--crops` pilot. Probe every upgraded
  clip with **`qa_media.py clip <mp4> --sheet <sheet.png> --crops <crops.png>
  --json`**, run **`qa_media.py batch <r5_clips...> --strict --json`** to audit
  cross-shot resolution/FPS/`hf_edge_energy` consistency, filter via fresh
  `reviewer-agent` (inspecting both `3x2` sheets and `1:1` native-pixel crops),
  update `video.selected_take` in `shotlist.json`, assemble `master.mp4` +
  `stems/` via `make assemble CAMPAIGN=<slug>`, and verify `make qa-render
  FILE=campaigns/<slug>/media/exports/master.mp4` (plus optional
  `brain_activity` virality analysis if approved).
- **Final Dailies 5:** `master.mp4` + `stems/` + spend receipt
  (`make budget-status CAMPAIGN=<slug>`) + offer to graduate durable
  `taste-log.md` rules into `brands/<brand>/taste.md`. On sign-off, mark
  upgraded shots `LOCKED` and flip `brief.md` to `status: done`.
- *Done when:* Director signs off on `master.mp4`, `make qa-render` passes, all
  final assets are `LOCKED`, and `brief.md` is `status: done`.

## Dailies Packet & Feedback Loop

Every round terminates in four compact blocks:
1. **What to inspect** — one consolidated artifact (`lookbook.png`,
   `stills_strip.png` + `animatic.mp4`, pilot clip, `draft_cut.mp4`, or
   `master.mp4` + `stems/`). On macOS with `Auto-open dailies: true`, run
   `open <artifact>` right before posting.
2. **Filtered internally** — one plain sentence summarizing defects or taste
   regressions caught internally, or honestly surfacing any surviving borderline
   concern after retries exhaust.
3. **Comparative taste questions** — 2–3 jargon-free questions inviting `A / B / C`
   picks, blends, or visceral reactions.
4. **Cost ticket** — spent so far, remaining `Campaign cap`, exact itemized live
   quote for the **next single round only**, and proposed round cap (enforced
   internally via `--round-cap`).

When the Director reacts:
1. **Distill into `taste-log.md`:** append `### TL-<NN> (R<k> — <stage>)` using
   the canonical bullets checked by `check-campaign.py`:
   - `Approved / LOCKED` · `More of` · `Change / Steer` · `Never`
   *(Surface any conflict with an earlier `TL-NN` as one `A / B` question before
   spending.)*
2. **Update `shotlist.json` (Root Producer only):** set approved items to
   `LOCKED`; set **only** steered items to `ITERATING`, bump `version` (`1 -> 2`),
   write a new versioned prompt file (`prompts/<id>_v2.txt`, keeping `v1`
   intact), and run `make campaign-check CAMPAIGN=<slug>`.
3. **Quote surgical micro-cost before re-rolling:** run live `generate cost` for
   only the `ITERATING` asset(s), confirm what stays `LOCKED` (`0 cr.`), and get
   a quick **"Go"** before calling `hf_guard.py` with cumulative
   `--round-cap <current_round_spent + approved_delta_cap>` (checked via
   `make budget-status`) and `--version <N>`.

## Budget & Lock Invariants

Enforced mechanically by `scripts/hf_guard.py` (never bypassed in prose):
- **Dual wall:** every `preflight` and `run` requires active `brief.md`
  (`Campaign cap`), `--round {R2,R3,R4,R4A,R4B,R5}`, and mandatory cumulative
  `--round-cap`.
- **Per-variant / per-version retries:** `--variant A|B|C` is allowed only when
  `--kind lookbook` (capped at `Lookbook variants`), and surgical re-rolls pass
  `--version <N>` (matched against `shotlist.json`), granting each option or
  version its own `1 + Max auto-retries/asset` attempts.
- **No CLI lock bypass:** `preflight` and `run` refuse `LOCKED` lookbook, still,
  video, and audio assets (`asset_locked`) and fail closed on corrupt
  `shotlist.json` or `receipts.jsonl`. There is no `--force-unlock` flag—only
  Root Producer edits `shotlist.json` (`LOCKED` → `ITERATING`, bumping `version`)
  after explicit Director approval and logs `Supersedes TL-<prev>` in
  `taste-log.md`.
