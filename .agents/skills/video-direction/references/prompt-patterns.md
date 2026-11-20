# Prompt Patterns and Blueprints

## Positive Observable Proxies and `taste-log.md` Translation

Modern DiT video models cannot render internal emotions or abstract adjectives directly, and inline negations (`no shaking`, `not glossy`, `no blur`) prime the forbidden concept in cross-attention. Translate every `taste-log.md` directive and story beat into concrete lighting, material, posture, or camera reality:

| Input (`taste-log.md` or raw idea) | Positive observable prompt translation |
| --- | --- |
| `Approved / LOCKED`: `lb_traveler_hand` | Keep exact `approved_upload_id`; refer functionally (`the traveler's right hand`) without re-describing wardrobe or skin. |
| `More of`: cool misty daylight, stillness | *"Diffuse cool 5200K morning mist from camera-left, generous negative space, locked-off tripod framing."* |
| `Change / Steer`: pull shot 2 wider | *"Medium-wide 35mm framing showing the full stone bench and unobstructed right-hand clasp grip."* |
| `Never`: glossy leather, neon bounce | *"Dry matte vegetable-tanned grain, muted warm-neutral stone palette, soft overcast daylight fill."* |
| `Never`: shaky camera, plastic skin | *"Locked-off static tripod shot, natural matte skin texture with fine pores under diffused window light."* |
| Abstract mood: *"She feels anxious"* | *"Her shoulders stay slightly raised, eyes fixed on the window edge rather than the lens, fingers tightening slowly around the ceramic mug."* |
| Vague action: *"He walks to the window"* | *"He takes three measured steps to the tall window, pauses one beat, and pushes the brass latch open with his right hand."* |

## True `R2` Lookbook Contrast (`A / B / C`)

Vary genuinely orthogonal visual axes while holding product geometry and brand invariants constant:
- **Variant A:** cool diffuse 5200K morning mist from camera-left, generous negative space, dry matte finish, 35mm medium-wide framing.
- **Variant B:** low directional golden sunbeams, higher micro-contrast, closer 85mm intimate crop, warm travertine bounce.
- **Variant C:** architectural one-point symmetry, overcast slate tones, crisp deep-grain tactile close-up, flat neutral fill.

## Video Prompt Blueprints

### A. I2V Motion Prompt (`R4` / `R5`, Delta-Only Over `--start_image`)

Keep static framing, cast identity, wardrobe, and lighting anchored in `--start_image` and `--image_references`; describe only camera trajectory, counted physical action, secondary physics, and diegetic sound:

```text
0-2s: Slow steady dolly push forward as morning mist drifts past the right window; the traveler's right thumb presses the brushed brass clasp with subtle mechanical resistance, gaze staying down on the bag.
2-5s: The clasp clicks open smoothly and the top leather flap settles naturally under its own weight as the camera holds locked-off on the open seam.
Audio: Soft leather flex, single crisp metallic click, quiet indoor room tone.
NO MUSIC. NO BACKGROUND SCORE. Native diegetic sound only.
```

### B. Start Frame + End Frame Interpolation (`--start_image` + `--end_image`)

Keep the spatial delta physically traversable in 5s and choose the camera verb matching the actual perspective shift between frames:

```text
Smooth continuous lateral camera truck to the right matching the perspective reveal from the doorway to the sunlit oak table. The woman takes three unhurried steps across the room, eyes focused ahead on the ceramic vase, never looking at the camera; her wool coat hem sways gently as she comes to a stop beside the table.
Audio: Soft footsteps on timber floorboards, muted wool rustle, quiet sunlit room tone.
NO MUSIC. NO BACKGROUND SCORE. Native diegetic sound only.
```

### C. Omni-Reference / Multi-Ref (`--image_references` / `@Image` / `@Video`)

Assign one explicit job to each attached reference so cross-attention does not bleed traits:

```text
@Image1 as the lead character wearing the exact tailored coat from @Image2, standing inside the wet stone courtyard from @Image3. Follow the slow low-angle lateral tracking pace of @Video1. She looks down at the umbrella handle, opens it in one fluid motion as raindrops bounce off the taut dark canvas, and steps forward toward screen-right.
Audio: Crisp rain patter on stretched fabric and wet stone, muted footsteps.
NO MUSIC. NO BACKGROUND SCORE. Native diegetic sound only.
```

### D. Single-Shot Text-to-Video (T2V, When No Keyframe Still Exists)

```text
Medium-wide 35mm shot, slow steady dolly-in. A watchmaker in his 50s in a charcoal canvas apron sits at an oak workbench, eyes focused intently down on an open brass pocket watch, never looking at the camera. He lifts a tiny steel gear with fine tweezers, pauses one beat, and lowers it into the movement as fine dust motes drift through a cool 5200K morning light shaft from camera-left. Muted wood and brass palette, natural 35mm film grain.
Audio: Quiet workshop room tone, faint mechanical ticking, subtle metallic scrape of tweezers.
NO MUSIC. NO BACKGROUND SCORE. Native diegetic sound only.
```

### E. Native Multi-Shot with Dialogue (Native Multi-Shot Models Only, e.g., Kling 3.0 / Seedance 2.5)

Use colon dialogue syntax (`says ...:`) plus explicit subtitle suppression to prevent burned-in text, keeping every spoken line within the read-aloud WPS budget:

```text
[MASTER PROMPT]
Setting: Quiet late-night diner booth with rain streaking down the glass window.
Lighting & Style: 35mm film grain, warm 3200K practical table lamp from camera-left, cool blue wet-street reflection outside, muted realistic palette.
Characters: [Character A] man in his late 30s in a dark wool jacket; [Character B] woman in her 30s in a slate turtleneck.
Audio Rule: Quiet diner room tone, soft rain on glass, distant clink of porcelain. NO MUSIC. NO BACKGROUND SCORE. Native diegetic sound only. No subtitles, no captions, no on-screen text.

[SHOT 1] (0-4s)
Framing & Camera: Medium two-shot, locked-off static tripod shot.
Action: Character A slides a folded paper map slowly across the laminate table toward Character B, keeping his eyes on the map.

[SHOT 2] (4-8s)
Framing & Camera: Over-the-shoulder close-up on Character B, subtle slow dolly-in, 50mm shallow depth of field.
Action & Dialogue: Character B lifts her eyes to Character A, exhales softly, and says in natural Russian with a calm quiet voice: Мы должны уехать до рассвета.

[SHOT 3] (8-10s)
Framing & Camera: Tight close-up on Character A, locked-off static tripod shot.
Action: Character A gives one slow measured nod as distant car headlights sweep faintly across the wet glass behind him.
```

## Camera Grammar and Geometric Pairs

Default to **one dominant camera move per shot** and specify `Locked-off static tripod shot` whenever stillness is intended. Match the verb to real 3D optics:

| Physical translation (creates 3D parallax) | Optical / fixed-axis move (no new parallax) | Rule of thumb |
| --- | --- | --- |
| **Dolly / Push-in / Pull-out** (camera travels forward/back) | **Zoom** (focal length changes in place) | Use **Dolly** for depth and perspective shifts between start/end frames; reserve **Zoom** for deliberate flat optical magnification. |
| **Truck / Track / Lateral glide** (camera slides sideways) | **Pan** (tripod head pivots left/right) | Use **Truck / Track** whenever occluded background or doorway geometry opens up; **Pan** stretches walls if asked to reveal hidden depth. |
| **Pedestal / Boom / Crane** (camera body rises/drops) | **Tilt** (lens pitches up/down in place) | Use **Pedestal / Crane** to clear foreground tables or shift horizon height. |
| **Locked-off static tripod shot** | **Handheld micro-movement** | State one explicitly; omitting camera phrasing lets the model insert wandering drift. |

**4-part motivated lighting formula** (replaces *"cinematic lighting"*):
`<quality: soft diffused | crisp directional | dappled>` + `<temperature: cool 5200K daylight | warm 3200K tungsten>` + `<source: tall window | overcast sky | table lamp>` + `<direction: from camera-left | backlit rim | overhead practical>`.

## Anti-IP Decomposition and Phonetic VO Rewrites

- **Anti-IP:** Decompose titles, franchises, directors, and third-party brands into materials, geometry, and light:
  - *"Blade Runner cyberpunk city"* → *"wet dark basalt street at night under mist-diffused amber sodium streetlights with low cyan puddle reflections"*.
  - *"Wes Anderson pastel café"* → *"symmetrical one-point interior, muted ochre plaster walls, crisp flat frontal daylight, deadpan framing"*.
- **Phonetic VO:** Keep canonical spelling in `script.md` and post captions; write phonetic pronunciation in TTS prompts per `brand.md` (`"Aethel"` → `"AY-thel"`, `"Kestrel"` → `"KES-trel"`), honoring `<= 2.0 wps` (Russian) / `<= 2.3 wps` (English) after subtracting `[PAUSE Ns]`.
