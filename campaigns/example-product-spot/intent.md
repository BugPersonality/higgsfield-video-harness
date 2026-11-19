# Intent: Nord Atelier Soren Weekender — Morning Departure 15s Spot

status: ready

## Purpose & viewer effect

Introduce the **Nord Atelier Soren Weekender 40L** to design-conscious weekend travelers and urban commuters through a 15-second visual hero spot built for homepage autoplay embeds and sound-on YouTube/Vimeo placements. Within the first two seconds, viewers should register the physical honesty of matte full-grain saddle leather and solid brushed brass hardware bathed in quiet morning daylight — leaving an impression of heirloom durability and unhurried travel poise without overt sales copy.

## Subject & visual truth

All visual and material invariants inherit directly from the [Nord Atelier Brand Profile](../../brands/example-brand/brand.md):

- **Product hero:** Soren Weekender 40L in matte full-grain vegetable-tanned Warm Saddle Tan leather (`#8B5A2B`) with hand-burnished dark-espresso seams (`#3A2618`), solid satin-brushed antique brass roller clasps and D-rings (`#B69659`), and a subtle blind-debossed uppercase `NORD ATELIER` wordmark centered 24 mm below the front handle gusset.
- **Traveler framing:** An understated traveler dressed in a matte charcoal wool overcoat (`#2B2E31`) and heather-grey knit cuff interacts with the bag via hands, shoulder lift, and rear three-quarter departure silhouette so the leather weekender remains the unmistakable focal subject across every frame.
- **Physical setting:** One continuous sunlit Nordic limestone-and-glass railway concourse at early golden morning (~4600K directional low sunbeams from screen-left against ~6200K pale limestone shadows).
- **Spoken pronunciation record:** Although this 15-second cut carries zero spoken narration, brand pronunciation is recorded as `Nord Ah-tel-yay` and `SOR-en` for any future localized cutdown.

## Format, audio & delivery

- **Format & pacing:** 15 seconds total across three 5-second shots (`s01`, `s02`, `s03`), `16:9` horizontal aspect ratio, locked `24 fps`.
- **Resolution stages:** `480p` draft motion clips assembled into `media/exports/draft_cut.mp4` for Gate 2 review; approved shots rendered at `1080p` (`1920x1080`) into `media/exports/master.mp4`.
- **Audio architecture:** Zero voiceover. Native diegetic sound generated with each video clip (brass clasp click, leather tension creak, bag lift against limestone, receding footsteps in a stone hall) mixed beneath a single 15-second sparse ambient solo cello and felt upright piano track (`music_vol: 0.14`, mastered to `-14 LUFS (±1.0 LU), true peak <= -1.0 dBTP (target -1.5 dBTP)`).
- **Deliverables:** Final H.264/AAC `master.mp4`, separated video/music/diegetic audio stems under `media/exports/stems/`, contact-sheet visual QA records, and an auditable `receipts.jsonl` spend log.

## Constraints & boundaries

- **Must not:**
  - Depict glossy, patent, or pebbled leather, chrome/silver hardware, or mirror-polished studio sweep backdrops.
  - Ship garbled, foil-stamped, colored, or duplicated `NORD ATELIER` typography or any third-party rail/airline logos, watch marks, or celebrity likenesses.
  - Include spoken voiceover, kinetic text overlays, price badges, percussion/synth bass drops, or music bleed inside raw generative video clips.
  - Speed up audio with `atempo`, fabricate job IDs/receipts, or commit binary media files to Git.
- **Authority & budget envelope:**
  - Autonomy mode: autonomous-draft
  - Draft cap: 140 credits
  - Final cap: 260 credits
  - Max auto-retries/shot: 2
- **Scope & non-goals:**
  - In scope: reference upload, 3 keyframe stills, 3 draft motion clips, 15s instrumental score, assembled `draft_cut.mp4` for requester review, followed by 1080p final renders, final master assembly, and stems export.
  - Non-goals: 9:16 vertical social cutdowns, spoken voiceover localization, custom Soul ID facial actor training, or paid media ad-platform trafficking.

## Success signal

1. **Deterministic & technical pass:** Every selected clip and `master.mp4` passes `scripts/qa_media.py` at locked 24 fps, zero black gaps (`>= 0.5 s`), zero frozen tails (`>= 3.0 s`), and integrated master loudness within `-14 LUFS (±1.0 LU), true peak <= -1.0 dBTP (target -1.5 dBTP)`.
2. **Material & continuity fidelity:** Visual contact-sheet inspection confirms matte Warm Saddle Tan leather, satin-brushed brass clasps, natural human hand anatomy, and consistent screen-left morning daylight across all three shots without any garbled text.
3. **Budget discipline:** Cumulative draft spend stays at or below 140 credits and final 1080p spend stays at or below 260 credits, verified in `receipts.jsonl` with zero unlogged calls or duplicate timeout charges.

## Settled decisions

### I1 — Purely visual and diegetic storytelling without voiceover or text overlays
- **Binding:** hard
- **Decision:** Carry the entire 15-second arc through tactile photography, native foley, and sparse acoustic cello/piano score with zero voiceover and zero baked-in promotional text overlays.
- **Rejected:** Narrated leather-craft voiceover or animated tagline lower-thirds.
- **Why:** Spoken ad copy undercuts the quiet Scandinavian restraint defined in the Nord Atelier brand profile, and baked-in typography increases generative text-artifact risk.

### I2 — Single continuous sunlit railway concourse across all three shots
- **Binding:** hard
- **Decision:** Stage all three 5-second shots inside the same limestone-and-glass Nordic train hall during low morning sunlight, moving from hardware macro (`s01`) to bench lift (`s02`) to wide colonnade departure (`s03`).
- **Rejected:** Multi-location travel montage spanning apartment, taxi, airport terminal, and boutique hotel.
- **Why:** Three 5-second shots establish stronger craft conviction inside one coherent architectural space and dramatically improve cross-shot product and lighting consistency.

### I3 — Autonomous 480p draft cut before Gate 2 final 1080p approval
- **Binding:** default
- **Decision:** Execute stills, 480p motion drafts, instrumental score, and assembled `draft_cut.mp4` end-to-end inside the 140-credit Draft cap, pausing once for requester approval before spending Final cap credits on 1080p renders.
- **Rejected:** Direct 1080p first-pass rendering or pausing after every individual shot before viewing the cut sequence.
- **Why:** Reviewing the complete 15-second rhythm with audio at 480p costs less than one-third of final render spend while exposing pacing or continuity issues early.

## Concrete viewer scenarios

- **Muted homepage autoplay (0–3 s):** A prospective customer opens the Nord Atelier site with browser audio muted. Within the opening two seconds, directional golden morning sun across fine matte leather grain and a hand latching a solid brushed brass clasp immediately communicate tangible build quality without needing captions or narration.
- **Sound-on 15-second desktop playback:** With speakers on, the viewer hears a crisp metallic brass click and subtle leather flex in `s01`, the weighted rustle of wool coat and bag lift off a limestone bench in `s02`, and unhurried footsteps echoing down the sunlit concourse in `s03` while a solo cello harmonic blooms gently below the foley rather than drowning it.
- **Pause-frame brand audit:** Pausing any frame across `s01`–`s03` reveals consistent `#8B5A2B` saddle leather color, square brushed-brass clasps, anatomically accurate fingers, and either a clean blind-debossed `NORD ATELIER` mark or the unmarked side face — zero distorted lettering or flickering hardware.

## Preferences & delegated choices

- **Camera grammar & lens focal lengths:** Delegated to Creative Definition and Production Design, honoring slow single-axis movement and 35mm organic film grain.
- **Exact Higgsfield model parameters & audio filter chain:** Delegated to Production Design and Assembly workers against live CLI schemas and FFmpeg target loudness constraints.
- **Exact cello/piano harmonic progression:** Delegated to Audio production within the sparse 68 BPM acoustic chamber brief (no percussion, no vocals).

## Assumptions & reopen triggers

- **A1 — Daylight product reference set available:** Three unobstructed daylight photographs of the Soren Weekender 40L (`bag_hero_front.jpg`, `clasp_macro.jpg`, `bag_worn_profile.jpg`) are placed in `media/references/` prior to Wave 1 upload — **Reopen if:** any supplied reference exhibits harsh flash glare, missing clasp detail, or a mismatched leather colorway requiring replacement photos.
- **A2 — Single generative instrumental stem fits the 15s arc:** One 15-second solo cello and felt piano track generated via Higgsfield audio delivers an unhurried rising sustain without percussion or abrupt cadence shifts — **Reopen if:** two bounded audio generations still contain percussion, vocals, or jarring tempo breaks, requiring requester sign-off on an external licensed music stem.

## Terminology

- **Soren Weekender 40L:** Nord Atelier flagship 40-liter carry-on leather duffel (`SOR-en`), crafted in matte Warm Saddle Tan full-grain leather with brushed brass clasps.
- **Nord Atelier:** Brand name spoken as `Nord Ah-tel-yay`, blind-debossed in uppercase below the front top handle gusset.
- **Gate 2 (Draft Review):** Requester checkpoint after inspecting `media/exports/draft_cut.mp4` and visual QA sheets, authorizing 1080p final renders up to the Final cap.

## Open questions

- **Q1 — Diegetic hall room-tone ducking floor during final 2-second cello decay:** Owner: assembly-worker | Fallback: hold diegetic station room tone at `-22 dBFS` under the `-18 dBFS` cello harmonic decay so footsteps remain audible through fade-out | Reopen if: `scripts/qa_media.py render` flags integrated loudness outside `-14 LUFS (±1.0 LU)` or true peaks above `-1.0 dBTP` (target `-1.5 dBTP`).
