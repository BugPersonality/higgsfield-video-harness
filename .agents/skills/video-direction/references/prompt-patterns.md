# Lookbook, Still, Motion, Anti-IP, and Phonetic Prompt Patterns

Read `campaigns/<slug>/taste-log.md` (and `brands/<brand>/taste.md` when present) before writing `campaigns/<slug>/prompts/lb_*`, `sNN_still_v*.txt`, `sNN_video_v*.txt`, or voiceover prompts.

## 1. Taste-Log Steering & `R2` Lookbook Variant Contrast (`A / B / C`)

Convert every Director note from `taste-log.md` (`Approved / LOCKED`, `More of`, `Change / Steer`, and `Never`) into positive physical language before writing prompts—never paste raw `"no glossy"` or `"never neon"` strings into image/video prompts:

| `taste-log.md` directive | Positive prompt steering applied in `R2`–`R5` |
| --- | --- |
| **Approved / LOCKED:** `lb_product_hero` Variant A (`LOCKED`); matte saddle leather + antique brass finish | preserve exact `approved_upload_id` geometry, blind-debossed wordmark placement, and raking morning key side unchanged across all downstream prompts |
| **More of:** `tactile leather pores and quiet architectural breathing room` | `low-angle raking key light highlighting fine dry leather grain; generous clean limestone negative space on frame-left` |
| **Change / Steer:** `warmer daylight key (~4600K) rather than cold sterile hospital white` | `low morning sun (~4600K) slanting from screen-left against soft cool limestone bounce fill (~6200K)` |
| **Never:** `glossy high-spec studio chrome or hyper-saturated commercial punch` | `dry matte vegetable-tanned finish, satin-brushed antique brass hardware, muted Nordic natural-light contrast` |

When generating `R2` Lookbook `A / B / C` variants for a hero entity (`lookbook[]`), keep core product/brand invariants identical across all three while contrasting genuinely orthogonal visual axes so the Director makes a real taste choice:

| Variant | Lighting mood & temperature | Texture & styling finish | Framing distance & backdrop |
| --- | --- | --- | --- |
| **Variant A — Architectural Morning** | Low raking screen-left sun (~4600K) with crisp soft-edged shadows and cool stone fill | Dry matte leather pores, subtle organic 35mm grain, heavy matte wool cuff | Medium three-quarter low angle on pale honed limestone bench with clean colonnade depth |
| **Variant B — Diffused Nordic Overcast** | Broad soft overhead skylight (~5800K), wrap-around low-contrast tonal gradations | Ultra-tactile flat matte surface micro-detail, zero specular hot spots, raw linen drape | Tight tactile close-up centered on brass clasp and saddle stitching against pale plaster wall |
| **Variant C — Warm Interior Practical** | Warm directional window/tungsten mix (~3600K) with rich espresso falloff in shadow | Deepened saddle-tan patina, warm brushed brass sheen, quiet dark oak architectural grain | Wide establishing shelf/bench composition showing full bag silhouette with atmospheric depth |

## 2. Seven-Part `R3` Still Keyframe Template

Use positive photographic language only. Lock every physical invariant from `brand.md`, `style-bible.md`, `taste-log.md`, and `R2` `LOCKED` Lookbook entities in the still so the `R4`/`R5` motion prompt does not have to restate it:

1. **Shot scale & framing:** medium close-up, three-quarter low angle, subject positioned on right-third intersection with generous clean negative space on the left.
2. **Subject & product invariants:** matte full-grain vegetable-tanned Warm Saddle Tan leather weekender bag with dark-espresso tonal saddle stitching and solid satin-brushed antique brass square roller clasp; subtle blind-debossed uppercase mark below top front handle gusset.
3. **Action, pose & hand truth:** one natural human hand with relaxed anatomically accurate fingers resting lightly over the brass clasp tongue, sleeve of charcoal heavy wool overcoat and heather-grey knit cuff visible at wrist.
4. **Environment & props:** honed pale limestone station bench inside a quiet sunlit Nordic railway concourse, clean architectural columns receding into soft depth.
5. **Lighting & atmosphere:** low directional morning sunlight (~4600K) entering from screen-left, casting crisp soft-edged raking shadows across fine leather pores against cool indirect limestone fill (~6200K).
6. **Camera, lens & film texture:** 50mm prime lens at f/2.8, shallow tactile depth of field focused on the brass clasp, subtle organic 35mm film grain, gentle highlight roll-off.
7. **Color palette & finish:** restrained Nordic palette of saddle tan, deep espresso, antique brass, limestone chalk, and morning slate; natural photographic contrast with clean highlights.

## 3. Timestamped `R4`/`R5` I2V Motion Templates (5s and 10s)

Describe ONLY movement, physics, and camera trajectory. Do NOT re-describe static lighting, colors, wardrobe, or background already locked in `--start-image`. End every non-UGC video prompt with the literal audio isolation directive.

### 5-Second Two-Beat Product Macro (`s01`)

```text
0-2s: The traveler's thumb presses the solid brass roller clasp smoothly into place until the tongue clicks seated, gently compressing the supple leather strap beneath.
2-5s: The hand relaxes and glides slightly along the top handle while a slow, steady 5-degree micro push-in tracks along the horizontal seam line; faint dust motes drift through the morning sunbeam.
Camera stays locked on a fluid single-axis track with calm, deliberate cadence.
NO MUSIC. NO BACKGROUND SCORE. Native diegetic sound only.
```

### 10-Second Continuous Narrative Progression (`s02`)

```text
0-3s: The traveler grips both rolled leather handles firmly and lifts the weighted weekender smoothly off the stone bench, the leather sides settling naturally under realistic gravity.
3-7s: The traveler turns smoothly toward screen-right and swings the bag slightly as they take three unhurried strides down the sunlit hall, the heavy wool coat hem swaying in sync with each step.
7-10s: The camera glides backward at matching walking pace, holding steady medium framing as the traveler continues deeper into the concourse.
Single continuous uninterrupted camera glide; realistic cloth and leather weight throughout.
NO MUSIC. NO BACKGROUND SCORE. Native diegetic sound only.
```

## 4. Positive Phrasing Replacements (Visual Attributes)

Generative models attend to nouns even when preceded by `"no"` or `"avoid"`. Replace visual negatives (and `taste-log.md` `Never` entries) with positive photographic equivalents (keep `"NO MUSIC. NO BACKGROUND SCORE. Native diegetic sound only."` as the explicit audio isolation guard):

| Weak negative phrasing | Strong positive replacement |
| --- | --- |
| `no blur, not out of focus` | `razor-sharp focal plane on the brass clasp with crisp surface micro-texture` |
| `no extra fingers, no mutated hands` | `relaxed natural hand with five proportional fingers gripping the handle cleanly` |
| `no plastic or glossy look` | `dry matte vegetable-tanned leather finish with fine organic pores and gentle specular roll-off` |
| `no camera shake` | `stabilized cinema dolly track moving on a single smooth horizontal axis` |
| `no clutter or messy background` | `minimal architectural limestone colonnade with generous clean negative space` |
| `no weird text or garbled logos` | `clean unmarked brushed-metal and plain stone surfaces throughout the background` |
| `no overly saturated neon colors` | `muted natural daylight palette with restrained tonal contrast and neutral skin tones` |

## 5. Anti-IP Sanitization & Fallback Rewrites

Strip recognizable franchises, celebrities, director names, movie titles, and third-party brand trademarks before submitting:

| Triggering input (`ip_detected` risk) | Sanitized visual equivalent |
| --- | --- |
| `Shot like a Wes Anderson movie in Grand Central Terminal` | `Symmetrical architectural framing in a sunlit neoclassical limestone railway concourse with warm pastel stone tones` |
| `Model resembling Timothée Chalamet wearing a Rolex Submariner` | `Slender man in his late twenties with tousled dark wavy hair wearing a minimal unmarked matte steel mechanical watch` |
| `AirPods Max on an Apple MacBook Pro displaying Figma UI` | `Minimal anodized matte-silver over-ear headphones beside a closed unbranded brushed-aluminum laptop on pale oak` |
| `Star Wars holographic glow with Cyberpunk 2077 neon` | `Soft volumetric morning light shafts cutting through cool atmospheric haze over dark architectural concrete` |

**Start-frame fingerprint fallback:** If a sanitized prompt still returns `ip_detected` on an image-to-video job, the pixel anchor in `--start-image` is likely triggering the matcher. Switch the reference binding from strict `--start-image <id>` to softer `--image-references <id>` (short alias `--image <id>`) in `omni_reference` mode, or regenerate the still keyframe removing the recognizable prop/silhouette.

## 6. Phonetic VO Spelling vs. Canonical Captions

Keep canonical spelling in `brief.md`, `script.md`, Dailies notes, and subtitle tracks; pass phonetic cues to `elevenlabs_v4` or `seed_audio` prompts so spoken pronunciation lands cleanly on take 1:

| Canonical caption / script text | Phonetic VO prompt text |
| --- | --- |
| `Nord Atelier — the Soren Weekender.` | `Nord Ah-tel-yay — the SOR-en Weekender.` |
| `Crafted by Aesop & Loewe-inspired artisans` *(avoid third-party names!)* | *(Replace brand reference first, then phoneticize owned name)* `Crafted in Stockholm for quiet daily travel.` |
| `Built on SQLite and NVMe storage` | `Built on Sequel-Lite and N-V-M-E storage` |
| `Powered by APIs for EMEA teams` | `Powered by A-P-I's for Eh-MEE-ah teams` |
