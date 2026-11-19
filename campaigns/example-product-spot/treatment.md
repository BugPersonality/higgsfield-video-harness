# Treatment: Nord Atelier Soren Weekender — Morning Departure 15s Spot

status: ready
Intent: [intent.md](intent.md)
Brand: [Nord Atelier Brand Profile](../../brands/example-brand/brand.md)
Style Bible: [style-bible.md](style-bible.md)

## Design It Twice — Competing Creative Lanes

### Lane A — Tactile Slow Cinema (Selected)

Three unhurried 5-second movements unfolding in continuous chronological sequence inside a sunlit Scandinavian limestone-and-glass railway concourse:

1. **`s01` — Tactile Clasp & Grain (0–5 s):** Macro close-up anchored on the Soren Weekender 40L resting on a sunlit limestone bench. Low golden morning sunlight rakes across matte saddle leather grain and dark-espresso saddle stitching while the traveler's hand closes the satin-brushed antique brass roller clasp with a crisp physical click.
2. **`s02` — Weighted Lift (5–10 s):** Medium 50mm side profile. The traveler in a matte charcoal wool overcoat gathers the rolled leather handles, lifting the packed 40L duffel smoothly off the pale stone bench and settling the waxed-canvas strap onto their shoulder as the bag displays real material weight and soft structured slouch.
3. **`s03` — Colonnade Departure (10–15 s):** Wide 35mm architectural frame down the lofty sunlit concourse. From a composed rear three-quarter angle, the traveler walks steadily away from camera toward tall arched glass windows flooded with golden morning haze, the Warm Saddle Tan weekender catching directional rim light against cool stone columns.

**Strengths:** Honors Nord Atelier's quiet restraint tie-breaker, showcases authentic leather texture in the critical 0–2 s muted autoplay window, keeps lighting/wardrobe continuity tight across three connected shots, and leaves 55 credits of retry buffer inside the 140-credit Draft cap.

### Lane B — Rapid Editorial Montage (Steelman Rejected)

A brisk 15-second architectural travel montage composed of six 2.5-second rhythmic cuts: polished brogue stepping onto travertine, mechanical watch glance, leather handle grip, brass zipper pull, reflection passing train-hall glass, and wide platform doors closing — driven by crisp rhythmic percussive foley and swift dolly whip-pans.

**Strongest case for Lane B:** Delivers heightened kinetic energy and rapid visual novelty well suited to short-form social feeds where viewers scroll within two seconds.

**Why rejected:** Splitting 15 seconds into six micro-shots doubles still and video generation volume (pushing draft + retry costs past the 140-credit Draft cap), increases cross-shot hardware and leather-shade drift across disparate angles, and directly conflicts with `I2` (single continuous morning concourse) and Nord Atelier's default tie-breaker favoring unhurried 4–5 second shots over rapid montage.

## Creative Decisions

### D1 — Three-shot 5-second slow-cinema cadence
- **Decision:** Lock the 15-second narrative to exactly three 5-second shots (`s01` macro clasp -> `s02` medium bench lift -> `s03` wide architectural departure) with one deliberate camera motion per shot.
- **Rejected:** Six 2.5-second rapid editorial cuts with whip-pan transitions (Lane B).
- **Why:** Five full seconds per shot allows natural physical weight, tactile sound decay, and optical filmic presence to land while keeping total draft spend at 85 credits (55 credits below cap).
- **Reopen if:** Gate 2 requester review finds the 5-second opening macro holds too long before revealing full bag silhouette.

### D2 — Hand, shoulder, and rear three-quarter traveler framing
- **Decision:** Keep the traveler framed through hands (`s01`), torso/shoulder profile (`s02`), and rear three-quarter silhouette (`s03`) rather than direct frontal facial close-ups.
- **Rejected:** Casting a front-facing recurring spokesperson or training a custom Soul Character ID.
- **Why:** Keeps the Soren Weekender 40L as the singular hero in every frame, eliminates cross-shot facial drift without extra identity-training overhead, and maintains timeless understated anonymity.
- **Reopen if:** Requester expands campaign scope to feature a named brand ambassador requiring facial continuity.

## Beat-to-Shot Map

| Shot | Duration | Scale & Lens | Visual Action | Diegetic Audio Anchor | Score Contour |
| --- | --- | --- | --- | --- | --- |
| `s01` | 5 s | Macro close-up, 85mm | Fingers latch brushed brass clasp on matte saddle leather in morning sun | Crisp metallic latch snap, soft leather creak | Near-silent entry; faint felt-piano breath at 4.0 s |
| `s02` | 5 s | Medium profile, 50mm | Traveler lifts Soren Weekender from limestone bench onto wool shoulder | Leather handle tension, wool coat rustle, gentle stone scrape | Warm solo cello note enters cleanly at 5.5 s |
| `s03` | 5 s | Wide architectural, 35mm | Traveler strides away down sunlit stone colonnade toward glass light | Measured footsteps echoing gently in tall stone hall | Cello + piano harmonic blooms softly and resolves at 14.5 s |

## Audio & Music Architecture

- **Voiceover posture:** Disabled (`0.0 wps`, zero spoken VO per `I1` in [intent.md](intent.md)). The spot carries brand identity and product proof purely through tactile picture and physical sound; brand pronunciation (`Nord Ah-tel-yay`, `SOR-en`) stays documented for future localized cuts.
- **Diegetic foley law:** Every generative motion prompt ends verbatim with `NO MUSIC. NO BACKGROUND SCORE. Native diegetic sound only.` so raw video outputs deliver crisp, isolated physical foley (solid brass clasp click, leather tension flex, wool coat rustle, limestone hall footsteps) without baked-in music bleed.
- **Music contour & ducking hierarchy:** One sparse 15-second instrumental stem (solo warm cello and muted felt upright piano at 68 BPM, acoustic chamber register). The opening 4.0 seconds remain purely diegetic so the brass clasp click lands in quiet room tone; a muted felt-piano note enters at `0:04.0`, solo cello blooms gently under `s02` (`0:05.5`), and the chord resolves naturally by `0:14.8`. In final mix (`scripts/assemble.sh`), music stays strictly at `music_vol: 0.14` (`<= 0.35`) beneath diegetic peaks (`sfx_vol: 0.18`), mastered to `-14 LUFS (±1.0 LU), true peak <= -1.0 dBTP (target -1.5 dBTP)`.
