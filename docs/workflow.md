# Studio Workflow (`R0` → `R5`)

Run every multi-shot video, commercial, or branded spot through six interactive
rounds between the **Director (human)** and **Production Crew (agents)**. Each
round executes full technical craft internally and stops with one **Dailies
Packet** for Director feedback and explicit next-round credit approval.

For schema shapes and flags, inspect the living fixtures and tools directly:
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
  `brief.md` (`status: draft`), seed `taste-log.md` from brand taste, and verify
  structure with `make brief-check`.
- **Dailies 0:** Short `brief.md` card + seeded taste anchors + `Campaign cap`
  confirmation. After Director confirms, flip `brief.md` to `status: active`
  and re-run `make brief-check`.
- *Done when:* Director confirms `brief.md` (`status: active`) with zero jargon
  and zero requester-owned open questions.

### R1 — Story & Cost Ticket (`0 cr.`)
- **R1A (Concept):** For commercials, run `ad-references` (skip if Director
  supplied an angle or reference spots) → `ad-concepts` (4–5 orthogonal
  swap-tested pitches); for non-commercials, draft 2–3 contrasting treatments.
  Stop with **Dailies 1A** so the Director picks or blends a direction.
- **R1B (Blueprint & Quote):** Run `ad-script` (3-column `Time | Video | Audio`,
  read-aloud budget, mute test) → `ad-storyboard` (`Continuity Lock`,
  `test_take_check`) → `style-bible.md`. Dispatch `evidence-agent` to inspect
  live Higgsfield schemas (`model get` / `workflow get` / `voices list`) and run
  live `higgsfield generate cost` per round. Write `shotlist.json` + initial
  `prompts/` and verify `make campaign-check` (`R2 + R3 + R4 + R5 <= Campaign cap`).
- **Dailies 1B:** Readable story beat-by-beat + exact round-by-round price list
  + approval ask for uploading any local `media/references/` photos and setting
  `R2` (or `R3` if `R2` is skipped) `--round-cap`.
- *Done when:* `make campaign-check` passes and Director approves reference
  uploads (if any) plus the next round's `--round-cap`.

### R2 — Casting & World Lookbook (`~20–45 cr.`, skip if `lookbook: []`)
- **Skip rule:** Skip `R2` automatically when real photos in `media/references/`
  already cover every hero object, character, and location; upload those photos
  at the start of `R3` with `hf_guard.py upload --round R3`.
- **Craft:** Dispatch parallel `worker-agent` lanes to generate 2–3 contrasting
  variants (`--variant A`, `B`, `C`, `--version 1`) per `lookbook[]` entity via
  `hf_guard.py run --round R2 --round-cap <cap>`. Filter AI trash and taste
  regressions via fresh `reviewer-agent`, then build one pixel-labeled grid with
  `make lookbook FILES="..." OUT=campaigns/<slug>/qc/lookbook.png LABELS="A,B,C"`.
- **Dailies 2:** `qc/lookbook.png` (auto-opened on macOS) + comparative picks +
  `R3` Cost Ticket. Upload chosen winners via `hf_guard.py upload --round R2`,
  record `approved_variant`/`approved_upload_id`, and set `status: "LOCKED"`.
- *Done when:* every `lookbook[]` entity is `LOCKED` with a verified upload UUID
  and Director approves `R3` `--round-cap`.

### R3 — Keyframe Stills & Still Animatic (`~30–50 cr.`, `0` video cr.)
- **Craft:** Generate `s01..sN` stills in parallel via `hf_guard.py run --round
  R3 --round-cap <cap>` bound to `LOCKED` UUIDs, `Continuity Lock`, and
  `taste-log.md`. Generate VO (`make qa-voice` — rewrite and regenerate on
  overflow, never `atempo`) and rough music when enabled. Filter via fresh
  `reviewer-agent`, build `qc/stills_strip.png` (`make lookbook`), and build a
  0-video-credit playable movie via `make animatic` (`media/exports/animatic.mp4`).
- **Dailies 3:** `stills_strip.png` + `animatic.mp4` + `R4A` (or `R4`) Cost
  Ticket. Lock approved stills/audio (`status: "LOCKED"`) and upload locked
  stills via `hf_guard.py upload --round R3`.
- *Done when:* Director locks all required stills/audio (judging framing, voice,
  and cut rhythm before spending video credits) and approves `R4A`/`R4` cap.

### R4 — Motion Dailies (`~45–90 cr.`)
- **R4A (Risk-First Pilot):** Shoot shots with `test_take_check != null` first
  at draft settings (`480p`/`720p`/`--draft`) via `hf_guard.py run --round R4A
  --round-cap <r4a_cap>`. Run `make qa-clip` (`3x2` contact sheet) and fresh
  `reviewer-agent`. Stop with **Dailies 4A** (pilot clip + `R4B` Cost Ticket).
  *(Skip `R4A` only when zero shots carry `test_take_check` and Director approved
  batch `--round R4` on Dailies 3.)*
- **R4B (Batch Draft & Cut):** Shoot remaining unlocked shots in parallel via
  `hf_guard.py run --round R4B --round-cap <r4b_cap>`, run `make qa-clip` +
  fresh `reviewer-agent`, and assemble `media/exports/draft_cut.mp4` via
  `make assemble` (`-14 LUFS`, `<= -1.0 dBTP`).
- **Dailies 4B:** Playable `draft_cut.mp4` + **per-shot `1080p` upgrade prices**
  for `R5`. Mark shots kept as-is (no `R5` upgrade) as `LOCKED`; leave shots
  scheduled for `R5` `1080p` upgrade unlocked (`IN_REVIEW` or `ITERATING`,
  bumping `version` if prompt/parameters change) so `hf_guard.py` permits `R5`
  renders.
- *Done when:* Director approves cut rhythm and exact `R5` `1080p` `--round-cap`.

### R5 — Final Master (`1080p`, approved quote)
- **Craft:** Upgrade **only** Director-approved unlocked shots to `1080p` via
  `hf_guard.py run --round R5 --round-cap <r5_cap>`. Run `make qa-clip` + fresh
  `reviewer-agent` on every upgraded clip. Assemble `media/exports/master.mp4`
  and `media/exports/stems/` via `make assemble`, verify `make qa-render`, and
  optionally run `brain_activity` virality analysis if approved.
- **Final Dailies 5:** `master.mp4` + `stems/` + exact spend receipt
  (`make budget-status`) + offer to graduate durable `taste-log.md` rules into
  `brands/<brand>/taste.md`. On sign-off, mark upgraded shots `LOCKED` and flip
  `brief.md` to `done`.
- *Done when:* Director signs off on `master.mp4`, all final assets are
  `LOCKED`, and `brief.md` is `done`.

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
   quote for the **next single round only**, and proposed `--round-cap`.

When the Director reacts:
1. **Distill into `taste-log.md`:** append `### TL-<NN> (R<k> — <stage>)` using
   the canonical bullets checked by `check-campaign.py`:
   - `Approved / LOCKED` · `More of` · `Change / Steer` · `Never`
   *(Surface any contradiction with an earlier `TL-NN` in one `A / B` question
   before spending.)*
2. **Update `shotlist.json` (Root Producer only):** set approved items to
   `LOCKED`; set **only** steered items to `ITERATING`, bump `version` (`1 -> 2`),
   write a new versioned prompt file (`prompts/<id>_v2.txt` without overwriting
   `v1`), and run `make campaign-check`.
3. **Quote surgical micro-cost before re-rolling:** run live `generate cost` for
   only the `ITERATING` asset(s), confirm what stays `LOCKED` (`0 cr.`), and get
   a quick **"Go"** before calling `hf_guard.py` with cumulative
   `--round-cap <current_round_spent + approved_delta_cap>` and `--version <N>`.

## Budget & Lock Invariants

Enforced mechanically by `scripts/hf_guard.py` (never bypassed in prose):
- **Dual wall:** every `preflight` and `run` requires active `brief.md`
  (`Campaign cap`), `--round {R2,R3,R4,R4A,R4B,R5}`, and mandatory cumulative
  `--round-cap`.
- **Per-variant / per-version retries:** `R2` Lookbook options pass
  `--variant A|B|C` (capped at `Lookbook variants`), and surgical re-rolls pass
  `--version <N>` (verified against `shotlist.json`), giving each option/version
  its own `1 + Max auto-retries/asset` attempts.
- **No CLI lock bypass:** `preflight` and `run` refuse `LOCKED` lookbook, still,
  video, and audio assets (`asset_locked`) and fail closed on corrupt
  `shotlist.json` or `receipts.jsonl`. There is no `--force-unlock` flag—only
  Root Producer edits `shotlist.json` (`LOCKED` → `ITERATING`) after explicit
  Director unlock and logs `Supersedes TL-<prev>` in `taste-log.md`.
