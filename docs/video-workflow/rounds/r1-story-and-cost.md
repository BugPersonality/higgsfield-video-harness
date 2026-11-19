# R1 — Story & Cost Ticket

**Credit spend:** `0 credits`
**Owner:** Root Producer + fresh read-only `specialist-agent` & `evidence-agent` lanes
**Outputs:** `script.md`, `storyboard.md` *(commercial track)*, `style-bible.md`, `prompts/*`, `shotlist.json` (`make campaign-check`), updated `taste-log.md`

R1 turns the active `brief.md` into a Director-chosen story and a live-priced,
round-by-round **Cost Ticket**—before spending a single credit. R1 runs in two
fast, zero-credit checkpoints: **R1A (Concept Selection)** and **R1B (Readable
Story & Cost Ticket)**.

## R1A — Contrasting Concepts / Treatments

Select the creative track matching the campaign:

### Commercial / Product Track

Governed by shared craft vocabulary in
[`docs/ad-craft-glossary.md`](../../ad-craft-glossary.md):

1. **Optional `ad-references`:** when the campaign benefits from real craft
   benchmarks (and the Director did not already supply them), load
   `ad-references` to dissect verifiable **primary spots** into **timecoded
   beats**, **brand entry** timing, and **transferable mechanisms**.
2. **`ad-concepts` (mandatory for commercials):** dispatch 2–3 fresh read-only
   `specialist-agent` lanes (`fork_turns: "none"`, `reasoning_effort: high`)
   reading `brief.md`, `taste-log.md`, `brands/<brand>/brand.md`, and optional
   transferable mechanisms to produce **4–5 genuinely orthogonal,
   product-locked pitches** running on distinct **dramatic engines**—every
   concept adversarially verified with the **swap test**.

### Non-Commercial / Editorial Track

Dispatch 2–3 fresh read-only `specialist-agent` lanes (`fork_turns: "none"`,
`reasoning_effort: high`) reading `brief.md` and `taste-log.md` to propose
**2–3 genuinely contrasting visual treatments** (distinct dramatic engines,
lighting philosophies, and pacing rhythms—never minor paraphrases of one idea).

### Dailies 1A — Concept Pick (`0 credits`)

Present a 4-block [Dailies Packet V1](../interfaces/dailies-packet-v1.md):

1. **What to inspect:** 4–5 crisp plain-language pitches (`A / B / C / D [/ E]`)
   on the commercial track (or 2–3 contrasting treatments on the non-commercial
   track), each with a one-sentence visual pitch, emotional arc, and concrete
   opening beat.
2. **Filtered internally:** 1-line summary of swap-test eliminations or
   `Must not` / `taste-log.md` rejections filtered before presentation.
3. **Comparative taste questions:** 2–3 plain questions asking which pitch (or
   blend of two pitches) hits the right nerve, and what instincts to amplify or
   kill.
4. **Cost ticket:** `0 credits spent`; writing the full beat-by-beat script,
   storyboard, and exact live price list in `R1B` costs **`0 credits`**.

Capture the Director's selection/blend in `taste-log.md` (`TL-NN (R1A — Concept
Pick)`) under [Feedback Loop](../shared/feedback-loop.md) before entering `R1B`.

## R1B — Script, Storyboard, Live Schemas & Cost Ticket

1. **Craft the story & visual bible** (via fresh `specialist-agent` lanes
   reading `brief.md` and updated `taste-log.md`):
   - *Commercial track:*
     - `ad-script` → `campaigns/<slug>/script.md`: timed **three-column script**
       (`Time | Video | Audio`), verified against the **read-aloud budget**
       (`<= 2.3 wps` EN / `<= 2.0 wps` longer-word languages after subtracting
       `[PAUSE Ns]`) and the **mute test** (core product claim survives with
       audio muted).
     - `ad-storyboard` → `campaigns/<slug>/storyboard.md`: numbered shots
       (`S01..SN`), **focal entry**, **motivated cuts**, top-level
       **Continuity lock** (`product`, `lighting_and_palette`,
       `space_cast_axis`), and explicit **Test-take check** (`risk` +
       `pass_check`) on every risky shot (grip, physics, legible text,
       reflections, comic timing, multi-subject blocking).
   - *Non-commercial track:* concise shot-by-shot beat sheet aligned with
     `continuity_lock` and any risky-shot `test_take_check` flags.
   - Author `campaigns/<slug>/style-bible.md` and version-1 prompt files under
     `campaigns/<slug>/prompts/` (`<id>_v1.txt` for invented Lookbook entities
     such as `lb_traveler_v1.txt`, `sNN_still_v1.txt`, `sNN_video_v1.txt`) using
     `video-direction` and `video-consistency` (including phonetic VO spellings
     from `brand.md` and anti-IP visual phrasing).
2. **Live CLI schema & exact per-round pricing (`evidence-agent`):**
   Dispatch a fresh read-only `evidence-agent` (`fork_turns: "none"`) using
   `higgsfield-cli` to verify live schemas (`higgsfield model get`,
   `workflow get`, `voices list`) and run live `higgsfield generate cost` for
   every planned asset across `R2`, `R3`, `R4A`, `R4B`, and `R5`.
   - Confirm `cinematic_studio_video_4_0` uses `"is_workflow": true` and
     `"mode": "omni_reference"` (never `"mode": "i2v"`).
   - Confirm whether `lookbook[]` is populated (invented entities requiring
     `R2`) or empty `[]` (all objects/characters/sets already supplied as real
     photos → `R2` skipped automatically).
3. **Assemble & validate `shotlist.json`:**
   Root Producer writes `campaigns/<slug>/shotlist.json` conforming to
   [Shotlist V1](../interfaces/shotlist-v1.md) (every asset at `status: "DRAFT"`,
   `version: 1`; `planned_total = draft_total + final_total <= Campaign cap`,
   targeting `<= 75%` headroom for internal retries and surgical re-rolls). Run:
   ```sh
   make campaign-check CAMPAIGN=<slug>
   ```
   If live quotes exceed `Campaign cap`, trim shot count, lookbook breadth, or
   model tier inside `brief.md` bounds—or surface the exact budget trade-off on
   Dailies 1B before spending a credit.

### Dailies 1B — Readable Story + Round-by-Round Cost Ticket (`0 credits`)

Present a 4-block [Dailies Packet V1](../interfaces/dailies-packet-v1.md):

1. **What to inspect:** plain-language beat-by-beat walkthrough of the story
   (`script.md` + `storyboard.md` visual moments, spoken lines if any, and
   which risky shot(s) will be piloted first in `R4A`) + whether `R2` Lookbook
   is needed or automatically skipped.
2. **Filtered internally:** 1-line summary of mute-test, read-aloud-budget,
   continuity-lock, and `make campaign-check` verification (`0 credits spent`).
3. **Comparative taste questions:** 2–3 plain story/pacing questions (e.g.,
   opening hook clarity, spoken line tone, closing button feel—zero model or
   flag jargon).
4. **Cost ticket:**
   - **Spent so far:** `0 credits` | **Campaign cap:** `<Cap> credits`
   - **Full round-by-round live price table:** `R2` (or `0 cr. — skipped`),
     `R3` (stills + rough audio + 0-credit animatic), `R4A` (pilot),
     `R4B` (remaining draft clips), `R5` (`1080p` upgrades), and planned total
     vs `Campaign cap`.
   - **Explicit go/no-go approval** for the next single round's `--round-cap`:
     `R2` (when `lookbook[]` is non-empty) or `R3` (when `R2` is skipped).

## Exit Criteria & Next Round

- Log Director story feedback in `taste-log.md` (`TL-NN (R1B — Story & Cost)`),
  reconcile any script/shot tweaks in `shotlist.json`, and re-run
  `make campaign-check CAMPAIGN=<slug>`.
- Once the Director explicitly approves the next round's `--round-cap`:
  - If `lookbook[]` is non-empty → advance to [R2 — Casting & World Lookbook](r2-lookbook.md).
  - If `lookbook[]` is empty (all references are supplied real photos) → skip
    `R2` and advance directly to [R3 — Keyframe Stills & Animatic](r3-stills-and-animatic.md).
