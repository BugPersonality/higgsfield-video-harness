---
name: video-direction
description: "Taste-aligned lookbook, still, and motion prompt craft. Use when authoring R2 Lookbook A/B/C variants, R3 keyframe stills, R4/R5 I2V motion prompts, anti-IP rewrites, or phonetic voiceover copy."
---

# Video Direction

**Taste Memory first.** Read `campaigns/<slug>/taste-log.md` (and `brands/<brand>/taste.md`) before writing any prompt. Honor every `Approved / LOCKED` anchor and turn active `More of`, `Change / Steer`, and `Never` lines into positive photographic, lighting, or kinetic cues.

**True `R2` Lookbook contrast (`A / B / C`).** Hold brand/product invariants constant while varying genuinely meaningful visual axes (lighting mood/temperature, material finish, camera distance, architectural backdrop) so the Director gets a real choice rather than synonym paraphrases; see [prompt patterns](references/prompt-patterns.md).

**Separate stills from motion (`R3` → `R4`/`R5`).** Keyframe stills lock composition, lens feel, lighting direction, wardrobe, architecture, and product truth. I2V motion prompts describe only subject movement, micro-physics, and camera trajectory without re-describing static frame elements. Map `storyboard.md` `Start frame` → `R3` still, `Action` → `R4`/`R5` motion prompt, `End frame` → `--end_image` or next-shot handoff.

**Pacing & audio isolation.** Match choreography to duration: single continuous takes for slow reveals or performance; timestamped micro-beats (`0-2s`, `2-4s`, `4-5s`) only when distinct staged actions land on intervals (at most two physical beats per 5s). End every non-UGC video prompt with the literal line `"NO MUSIC. NO BACKGROUND SCORE. Native diegetic sound only."` so native foley stays clean under mastered music and VO.

**Positive anti-IP phrasing, VO budget & typography.** Replace franchises, celebrities, movie titles, and third-party brand props with raw materials, silhouettes, and lighting; phrase every `Never` rule as its positive visual opposite. On `ip_detected`, sanitize prompt copy first and soften `--start_image` to `--image`/`--image_references` or regenerate the keyframe. Enforce `ad-script`'s **read-aloud budget** ([Ad Craft Glossary](../../../docs/ad-craft-glossary.md): `<= 2.0 wps` Russian, `<= 2.3 wps` English after subtracting `[PAUSE Ns]`), spell brand names phonetically in VO prompts, and composite fine typography/UI in post rather than inside video generations.
