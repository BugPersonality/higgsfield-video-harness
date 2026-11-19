# Style Bible: Nord Atelier — Morning Departure 15s Spot

status: ready
Intent: [intent.md](intent.md)
Treatment: [treatment.md](treatment.md)
Brand: [Nord Atelier Brand Profile](../../brands/example-brand/brand.md)

## Lighting & Color Temperature

- **Primary key:** Natural low-angle Nordic morning sunlight (~4600K) streaming through tall arched iron-and-glass station windows from **screen-left** across all three shots. Maintain consistent screen-left key direction across `s01`, `s02`, and `s03`.
- **Ambient fill:** Cool indirect architectural sky bounce (~6200K) reflected off pale honed limestone walls and vaulted plaster ceilings.
- **Atmosphere:** Subtle natural morning air haze illuminated by directional window shafts, maintaining quiet architectural realism rather than glossy studio sweeps or stylized neon rim lighting.

## Palette & Material Fidelity

- **Leather (`#8B5A2B` / `#3A2618`):** Matte full-grain vegetable-tanned saddle leather with visible fine pores, natural micro-creasing along strap folds, and hand-burnished dark-espresso edges that absorb light softly.
- **Hardware (`#B69659`):** Satin-brushed antique solid brass clasps, D-rings, and zipper pulls catching muted warm directional edge highlights.
- **Environment & wardrobe (`#E8E3DA` / `#5C6773` / `#2B2E31`):** Pale matte limestone bench and tiled travertine floor, cool morning slate shadows, matte heavy charcoal wool overcoat with a muted heather-grey knit cuff.

## Film Texture, Optics & Frame Rate

- **Stock aesthetic:** 35mm Kodak Vision3 250D feel — fine organic luminance grain, creamy highlight roll-off in sunlit window zones, and luminous open shadow depth.
- **Lens progression:**
  - `s01`: 85mm macro-feel shallow depth of field (`f/2.8`) separating crisp leather stitching and brass clasp from soft sunlit limestone background.
  - `s02`: 50mm classic medium frame (`f/2.8`) preserving honest leather silhouette and natural architectural perspective.
  - `s03`: 35mm architectural wide (`f/4.0`) emphasizing towering glass clerestory arches and calm negative space around the receding traveler.
- **Cadence:** Strict `24 fps` delivery lock with natural 180-degree shutter motion blur.

## Camera Grammar

- **One motivated movement per shot:**
  - `s01`: Ultra-slow subtle push-in (~3% framing creep) tracking the tactile clasp closure.
  - `s02`: Gentle horizontal lateral tracking slide rising smoothly with the weighted lift of the weekender.
  - `s03`: Locked-tripod wide architectural hold with a barely perceptible slow dolly-in as the traveler walks away into light.
- **Forbidden moves:** Whip pans, handheld jitter, rapid zooms, artificial drone orbits, or multi-axis floating sweeps.

## Audio Design & Level Law

- **Raw video clip rule:** Every video motion prompt ends verbatim with `NO MUSIC. NO BACKGROUND SCORE. Native diegetic sound only.` so Higgsfield generates pure foley (clasp snap, leather flex, wool coat rustle, resonant concourse footsteps) without baked-in music bleed.
- **Underscore brief:** One 15-second instrumental stem (`elevenlabs_music_v2_5`) — solo warm cello and muted felt upright piano at 68 BPM, acoustic chamber register.
- **Mix targets (`scripts/assemble.sh` + `scripts/qa_media.py render`):**
  - Music bed gain: `0.14` (`--music-vol 0.14`)
  - Diegetic SFX bed gain: `0.18` (`--sfx-vol 0.18`)
  - Final master mastering target: `-14 LUFS (±1.0 LU), true peak <= -1.0 dBTP (target -1.5 dBTP)`, 48 kHz stereo AAC.

## Negative Constraints & Anti-IP Phrasing

- **Positive sensory phrasing in generation prompts:** Generative image and video models frequently attend to negated nouns. Translate every brand taboo into positive material and architectural phrasing inside `prompts/*.txt` (for example, write *"velvety matte full-grain leather with diffuse light absorption"* instead of *"never glossy"*, *"unadorned honed limestone arches and bare iron-framed glass"* instead of *"no transit signs or logos"*, and *"cropped strictly from shoulder line to mid-thigh"* instead of *"no visible face"*). Reserve literal negation exclusively for the audio-isolation directive `NO MUSIC. NO BACKGROUND SCORE. Native diegetic sound only.`
- **Anti-IP abstraction:** Describe the setting strictly as a classic Scandinavian honed-limestone and dark-iron glass railway concourse (never naming Stockholm Central, SJ, or real European rail operators), keep the traveler anonymous and wardrobe completely unbranded (heavy matte charcoal wool coat and plain heather-grey rib-knit cuff — never naming fashion houses, watchmakers, or actors), and reference only the client's own `NORD ATELIER` blind-debossed wordmark on front-angle `s01`.

## Cross-Shot Continuity Checklist

Every candidate still and 3x2 video contact sheet is inspected by an independent, fresh read-only Visual Critic (`reviewer-agent` via `view_image`, never self-approved by the generating worker) against all five invariants:

1. Saddle-tan matte leather hue matches across `s01` -> `s02` -> `s03` with diffuse natural grain.
2. Hardware stays square satin-brushed antique brass across every angle and motion frame.
3. Blind-debossed `NORD ATELIER` mark is sharp and properly spelled when visible (`s01`), and cleanly absent on non-front angles (`s02`, `s03`).
4. Traveler wears the same matte charcoal wool coat and heather-grey knit cuff in every shot, with five anatomically natural fingers and realistic joint motion in `s01` and `s02`.
5. Directional 4600K warm morning sun originates consistently from screen-left across all three shots with zero 180-degree axis flip.
