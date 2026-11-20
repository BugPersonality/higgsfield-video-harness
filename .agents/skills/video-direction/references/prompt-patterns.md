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

## `R3` Multi-Ref Still Assembly Pattern (Location + Cast + Prop)

Lock spatial geography, contact shadows, prop scale, color proportions, and room-light integration in `2k`/`4k` `R3` stills before animating (see [Locations, Buildings & Props](../../video-consistency/references/locations-and-props.md)):

```text
35mm medium-wide frame inside the empty limestone workshop from Image 1 (camera near South doorway facing North-West window). The traveler from Image 2 stands beside the oak workbench facing screen-left, right hand resting naturally near the matte brushed-brass kettle from Image 3. Place the kettle squarely on the oak counter with a soft grounded contact shadow matching the cool 5200K daylight from the North window; keep kettle height roughly 1.3x the stoneware mug beside it. Strictly preserve the kettle's cool satin-brass pigment without warm wood bounce bleed.
PALETTE, stated first: 50% pale warm limestone & matte plaster, 30% aged oak & charcoal wool, 20% muted satin brass & stoneware cream.
Shot on 35mm daylight-balanced 250-speed negative film, fine grain, natural depth of field; tech tail palette: pale limestone 50%, oak & charcoal 30%, satin brass & cream 20%.
```

### Percentage Palette Lock & Anti-Cutout Room-Light Integration

- **Percentage Palette Lock (`R2`/`R3` stills):** Declare exact 3-band color proportions early (`PALETTE, stated first: 45% <dominant>, 35% <secondary>, 20% <accent>`) and mirror the same ratio in the closing technical tail (`tech tail palette: ...`) so multi-scene stills stay grade-locked before post color.
- **Anti-Cutout Room-Light Integration (`R3` stills & `omni_reference` video):** Whenever compositing a `@character` plate into a `@location`, bind the subject physically into the room instead of letting the model add flattering studio light:
  1. **Surface bounce:** name upward bounce off the floor/table opening chin, jaw, or brim shadows.
  2. **Shared lens-to-subject haze:** place the room's air/haze *between the lens and the actor* with slightly lifted blacks so the subject is never crisper than the background.
  3. **Ambient room tint:** state that skin and wardrobe absorb the room's cool/warm cast rather than glowing golden against a cool set.
  4. **Natural wrap & anti-beauty-light (documentary/grounded cinema):** omit artificial key, rim, edge light, god rays, and specular flashes when diffuse or practical light owns the scene. On photochemical/realistic video prompts, explicitly state **`No automatic face brightening or unmotivated beauty lighting`**—let faces fall into true shadow between established practicals or passing streetlamps, paired with `shot on 35mm film, spherical lenses, Kodak Vision3 250D`, `HEAVY VISIBLE 35MM GRAIN`, `soft highlight roll-off, gentle diffusion, imperfect focus, 24fps, 180 degree shutter, natural motion blur, no digital smoothing`.
- **`R3` Cinema Spec Still Skeleton (`Seedream 5.0 Pro`, `2k`, high-continuity narrative):**
  ```text
  Cinematic film still. <1-sentence scene summary>. Location @Image1.
  COMPOSITION: <focal length>, camera height/position, subject crop & foreground/background layers.
  @Image2 — <subject placement, posture, material wear, exact hand contact>.
  @Image3 — CRITICAL CORRECTION (on v2+ retries only): <exact placement/action>, NOT <the v1 failure mode>.
  THE LIGHT & GRADE: <4-part diffuse/motivated lighting>; <lifted blacks / contrast / saturation rules>.
  PALETTE, stated first: 50% <dominant>, 30% <secondary>, 20% <accent>.
  LIGHTING, palette restated: <single/motivated light source + brightest/darkest zones>.
  FOCUS: locked on <exact sharp plane>, aperture wide open; <foreground/background falloff>.
  Shot on 35mm daylight-balanced 250-speed negative film, fine grain; tech tail palette: <same 50%/30%/20% split>. No text, no watermark.
  ```

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

### F. `Seedance 2.5` 2-Shot Hard-Cut Paired Block (`6s = 3s + HARD CUT + 3s`, `omni_reference`)

Pair two adjacent same-set cuts into one `6s` `seedance_2_5` clip (`18 cr.` draft → `96 cr.` `1080p --bitrate_mode high` = `48 cr./cut`) to lock identical grain, exposure, room haze, and prop state across the hard cut:

```text
OUTPUT SETTINGS
TWO SHOTS, 6 SECONDS TOTAL. SHOT A is 3 seconds. SHOT B is 3 seconds. HARD CUT BETWEEN THEM — zero dissolve, fade, or wipe. 24fps, photoreal live action, interior daylight, no dialogue.

REFERENCE ROLES
@Image1 governs the protagonist; @Image2 governs the hero prop; @Image3 governs the room. Preserve 100% of each reference's identity and material finish.

LIGHT INTEGRATION
Broad diffuse room daylight only; upward soft bounce off the pale floor opens chin and brim shadows; room haze sits between lens and actor so blacks stay slightly lifted and skin absorbs the room's cool tint. No key light, rim light, god rays, or specular flash. Identical grade across both shots.

SHOT A (3s) — TACTILE DETAIL
85mm wide open, tight low shot on the prop resting on the floor; only hand and forearm enter frame. Handheld follows the hand rising slightly late behind the lift (unhurried, weighted grip, no gimbal polish).
0:00-0:08 — Prop still on surface.
0:08-1:16 — Hand closes cleanly on prop in one unhurried move, fingers leaving faint clean tracks in surface dust.
1:16-3:00 — Hand lifts prop up out of top frame as handheld camera rises slightly late.

HARD CUT.

SHOT B (3s) — TWO-PLANE REACTION (RESTRAINT)
85mm wide open, near-still handheld. Large completely out-of-focus prop in foreground to one side; protagonist's eyes razor-sharp behind it. Focus stays locked on eyes for the entire shot (no rack focus).
0:00-1:08 — Hand slowly rotates the prop in foreground; eyes track the turn without moving head.
1:08-2:12 — Holds gaze on prop noticeably longer than reading time (engaged gaze, one slow natural blink; never glassy or looking at lens).
2:12-3:00 — One audible exhale through the nose and slight jaw unclench; restrained stillness, zero smile or camera-played emotion.

AUDIO — ONLY THESE SOUNDS EXIST
1. Wide quiet room tone. 2. Soft skin-on-dust friction and fabric creak (Shot A). 3. Quiet breathing and one soft nasal exhale (Shot B).
NO MUSIC. NO BACKGROUND SCORE. Native diegetic sound only. No subtitles, no captions, no on-screen text.

POSITIVE CONSTRAINTS (closing lock — repeat only the 5-8 hardest invariants)
- @Image1, @Image2, @Image3 100% match their references; TWO SHOTS (3s + 3s) with ONE HARD CUT.
- Broad diffuse room light + upward floor bounce + lens-to-subject haze; cool room tint in skin; zero rim/key/god-rays.
- Shot A: hand & forearm only, handheld rising slightly late behind the lift, weighted grip with no rattle.
- Shot B: foreground prop completely out of focus, eyes razor-sharp for full shot (no rack focus), held gaze + one nasal exhale, never looking into lens.
- Identical 35mm 250-speed film grain and grade across both shots; no slow motion, speed ramps, or freeze frame.
```

### G. `Seedance 2.5` Photochemical Multi-Shot / One-Take (`20–30s`, `4–10` Hard Cuts or Unbroken Take)

Use for grounded documentary/cinema narrative scenes (`seedance_2_5`, `omni_reference`) where one shared latent generation locks grain, exposure, weather, vocal timbre, and spatial geography across an entire beat:

```text
PHYSICAL HANDHELD THROUGHOUT. Operator's hands, breathing, and weight shifts drive irregular jolts, sway, bounce, overshoot, and snap-back—even on close-ups and pauses. Critical action stays readable. [Interior option: Keep the horizon level and architectural verticals upright; no camera roll or Dutch angles.] NEVER smooth, NEVER gimbal, NEVER stabilised, NEVER a tripod, NEVER a static hold.

LOOK, do not deviate: shot on 35mm film, spherical lenses, Kodak Vision3 250D. Physically plausible light sources only (window light, practical lamps, passing streetlamps); consistent source direction and shadows as characters and camera move. No automatic face brightening or unmotivated beauty lighting; no artificial rim light. Soft highlight roll-off, gentle diffusion, shallow depth of field, imperfect focus, HEAVY VISIBLE 35MM GRAIN, 24fps, 180 degree shutter, natural motion blur, no digital smoothing.

REFERENCE CONTROL
Image 1 defines ONLY the location—choose camera angles for the action rather than reproducing the reference composition.
Image 2 defines <Character A> (masked two-panel diptych): use the portrait for face and the full-body view for clothing. Render complete natural faces; white masks and reference-sheet layouts never appear.
Audio 1 defines ONLY <Character A>'s vocal timbre (never repeat words from the audio sample).

GEOGRAPHY & BEHAVIORAL LOCKS
Keep all camera positions on <Character A>'s right side of the axis; achieve opposite angles by camera placement, never by horizontally mirroring the image or architecture. [State explicit negative acting/physics anchors: e.g., "No smiling, blinking, or exaggerated horror reactions; bodies are progressively occluded by the doorway wall and never dissolve in place."]

SHOT SEQUENCE (20–30s, HARD CUTS ONLY — or "ONE CONTINUOUS TAKE, 47° fixed lens")
0:00–0:04 — SHOT 1 (47° diagonal FOV, camera at eye height): <blocking + motivated operator step/overshoot>.
HARD CUT.
0:04–0:08 — SHOT 2 (29° diagonal FOV, tight detail): <tactile hand/prop action + brief focus slip and recovery>.
HARD CUT.
0:08–0:14 — SHOT 3 (18° diagonal FOV, frontal ECU, forehead/chin near frame edges): <restrained micro-expression; camera follows a fraction late>.

DIALOGUE (timecoded, overlapping across cuts — omit if silent)
00.0–03.5  SPEAKER A, quiet and tired: "<exact scripted line>"
03.6–06.2  SPEAKER B, off-screen/filtered: "<exact scripted line>"

SOUND: <concrete diegetic foley & room tone>. Exact scripted words; carry conversation naturally across cuts. NO MUSIC. NO BACKGROUND SCORE. No drones, stingers, ad-libs, or subtitles.
```

## Camera Grammar and Geometric Pairs

Default to **one dominant camera move per shot** and specify `Locked-off static tripod shot, horizon level` whenever stillness is intended. For deterministic Higgsfield camera tool routing (Cinema Studio 4.0/3.5/3.0, 3D Jutsu, Draw to Video, Motion Transfer, Reframe), optics recipes, `camera_style`/`speedramp` enums, special rigs, and in-camera transitions, follow [Camera Control](camera-control.md). Match the verb to real 3D optics:

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
