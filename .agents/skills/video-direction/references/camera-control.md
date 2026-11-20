# Camera Control, Optics & Motion Routing Playbook

Executable decision spec for choosing **which Higgsfield camera tool to use, when, why, and how to direct optics, camera moves, rigs, speedramps, and transitions** without morphing, drift, or credit waste. Always verify live flags and prices via `higgsfield workflow get <id> --json`, `model get <id> --json`, and `generate cost`—credit snapshots below reflect the `ultra` plan (`2026-11`, 5s clips).

## 1. Four Hard Camera Invariants

1. **Hero Frame First & Delta Separation:** Lock framing, focal length, lens character, aperture feel, lighting, and perspective in `2k`/`4k` `R3` stills before animating (I2V amplifies still flaws). In video prompts, describe **only temporal delta** (camera trajectory, counted action, secondary physics, diegetic audio)—never re-describe static appearance or room layout.
2. **Zero Double-Command:** When a mechanical control owns the camera—Web Cinema Studio movement preset/`#` tag, CLI `--camera_style`, `--speedramp`, `Draw To Video` arrows, or `@Video` motion transfer—**omit competing camera movement instructions from prompt text**. Let the mechanical layer own the trajectory while prose drives subject action, physics, and audio (keep at most a neutral stabilizer like `horizon level`).
3. **One-Move Rule & Explicit Stillness:** Direct **one dominant camera axis per 5s shot**. When stacking UI presets (`Mix` / `#` tags in Web Cinema Studio), combine at most **2 compatible axes** (e.g. `Slow Truck Right` + `Subtle Crane Up`) and respect selection order, which governs trajectory sequence. Whenever a static frame is intended, state `Locked-off static tripod shot, horizon level` explicitly—omitting camera phrasing lets DiT models inject wandering drift.
4. **3D Parallax vs. Nodal Optics:** Match camera verbs to real 3D geometry ([Camera Grammar](prompt-patterns.md#camera-grammar-and-geometric-pairs))—use `Dolly` (not `Zoom`), `Truck`/`Track` (not `Pan`), and `Pedestal`/`Crane` (not `Tilt`) whenever perspective or occluded background shifts; reserve `Zoom`/`Pan`/`Tilt` for fixed-axis optical/nodal moves.

## 2. Deterministic Camera Tool-Routing Algorithm

Evaluate each shot top-to-bottom and take the **first matching branch**:

1. **IF replicating an exact real-world camera path or choreography from reference footage** → **Motion Transfer:**
   - **Scene + camera + choreography transfer onto 1+ asset refs:** `hf_mult_motion_control` / `hf_mult_motion_control_flash` (**Genjutsu**, CEL: `== 1` `video_references`, `>= 1` `image_references`) OR `seedance_2_5 --mode omni_reference` with `@Video1` (`"Follow the exact camera trajectory and pacing of @Video1"`).
   - **Human performance + framing transfer from reference video onto 1 character image:** workflow `kling3_0_motion_control` (`10 cr.` `std` / `15 cr.` `pro`; CEL: `== 1` `image_references` + `== 1` `video_references`, `--background_source input_image|input_video`).
   - **Re-rendering an approved draft's locked camera natively at `1080p`:** `kling4_0 --mode video-edit --resolution 1080p` (`22.5 cr.`) or grayscale depth extraction via `depth_anything_video` (`7.57 cr.`, `--colormap grayscale --variant VDA-Large`).
2. **ELSE IF building a complex/impossible 3D trajectory from scratch** (flythrough through doorways, tight multi-angle architectural orbit, custom handheld path that text prompts distort) → **Web `3D Scene Builder` (`3D Jutsu`) → Video Render:**
   - Block simple geometry + `Look at` target + FOV in Higgsfield `3D Jutsu` (or pair a phone via **QR code** to record real physical handheld/dolly motion live into the 3D set).
   - Export the previz MP4 and pass it as `@Video1` into `seedance_2_5 --mode omni_reference` (or `hf_mult_motion_control`) with locked `R2`/`R3` image refs so final pixels inherit the exact 3D camera track 1:1.
3. **ELSE IF bridging two exact target compositions** (e.g. establishing wide → locked product/hero end-frame) → **Start + End Frame Interpolation:**
   - Generate matched `2k`/`4k` Start and End plates first (`3d_jutsu_angles`, Web `Angles` 360° swivel, or sliced `nano_banana_2_shots` tiles via `make slice-grid`).
   - Animate with `--start_image` + `--end_image` (`seedance_2_5`, `kling4_0`, `kling_o3_flf` [dedicated FLF + multi-shot; CEL: `end_image` requires `start_image`], `wan3_0`, `cinematic_studio_video_4_0`; note `kling_4_0_flash` omits `--end_image`). Keep physical distance traversable within clip duration and match camera verb to the real 3D perspective shift.
4. **ELSE IF delivering 2–6 cohesive cuts inside ONE shared location** → **Native Multi-Shot:**
   - Use `kling_o3_image_reference --multi_shots true --multi_prompt [...]`, `kling_o3_flf --multi_shots true`, `kling4_0`, `cinematic_studio_video_3_5` / `cinematic_studio_3_0` (`--multi_shots true --multi_shot_mode auto|custom`), or `seedance_2_5` so shared latent space preserves lighting, walls, and wardrobe across cuts.
5. **ELSE IF needing deterministic optical gear, stylized camera presets, `camera_style`, `speedramp`, or social hypermotion templates** → **Cinema Studio / Hypermotion Family:**
   - **Web Cinema Studio 4.0 (`https://higgsfield.ai/cinema-studio`) & `cinematic_studio_image`:** Director's Panel with 30+ movement presets (`#` shortcut), camera body/lens/aperture, `pacing_id` (`Single Shot` / `Calm` / `Dynamic` / `Chaotic`), era (`1960s–2020s`), custom light placement, up to 30s, and `forward`/`backward` extension. For `R3` stills, workflow `cinematic_studio_image` (`<= 4` `image_references`) additionally exposes `camera_focal_length_id`. *(CLI boundary: preset UUIDs are absent from `preset list`—configure once in Web and extract via `higgsfield generate get <id> --json` into [`docs/cinema-presets.json`](../../../../docs/cinema-presets.example.json) shape, or leave `Auto` and describe optics in prose.)*
   - **CLI Cinema Studio 3.5 (`cinematic_studio_video_3_5`, `25 cr.` `720p` / `65 cr.` `1080p`):** When you need explicit CLI `--camera_style` (9 styles in Section 4B) + `--light_scheme` (`soft_cross|contre_jour|overhead_fall|window|practicals|silhouette`) + `--color_grading` (`naturalistic_clean|bleached_warm|hyper_neon|teal_orange_epic|sodium_decay|cold_steel|bleach_bypass|classic_bw`). **CEL/default traps:** `camera_style`/`light_scheme`/`color_grading` are mutually exclusive with `style_prompt`; `duration` defaults to **`15`** and `prompt_language` defaults to **`zh`**—always pass `--duration 5 --prompt_language en` explicitly.
   - **CLI Cinema Studio 3.0 / V2 (`cinematic_studio_3_0`, `25 cr.` `720p` / `65 cr.` `1080p`; `cinematic_studio_video_v2`):** When you need explicit CLI `--speedramp` (Section 4C) or `4k` output (`3_0`). Pass `--prompt_language en` on `3_0`.
   - **Social / Product Hypermotion (`marketing_studio_v2_video --type hypermotion`):** One-tap kinetic product/social camera templates discoverable via `higgsfield preset list marketing-studio-v2 --type hypermotion` (CEL: `== 1` `input_images`, `duration` `5–15`, `style_id` and `preset_id` mutually exclusive).
6. **ELSE IF directing a single-object trajectory or simple 2D sweep visually without prose ambiguity** → **Draw To Video (`draw_to_video`, `26 cr.` `720p` / `63.5 cr.` `1080p`):**
   - CEL: `== 1` sketch/annotated image in `image_references`. Draw minimal, short, non-overlapping arrows (single arrow on object = local motion; parallel canvas arrows = pan/track; radial outward arrows = zoom). Pair with concise style/atmosphere text only.
7. **ELSE (default for ~70% of commercial shots: clean single-move narrative or product beat)** → **Locked `R3` Keyframe + I2V Delta Prompt:**
   - Route per [Model Selection](../../higgsfield-cli/references/model-selection.md): Web `Unlimited` (`0 cr.`) first → economy `720p` draft (`seedance_2_0_mini`, `kling_4_0_flash`, `wan3_0`) or `seedance_2_5 --draft true` (`15 cr.` when 1:1 `--draft_job_id` escalation is required) → native `1080p` master (`kling4_0`, `wan3_0`, `veo3_1`, `seedance_2_5 --draft_job_id --bitrate_mode high`, `cinematic_studio_video_4_0 --bitrate_mode high`).
8. **Post-generation aspect-ratio adaptation or pan cleanup (only on already-locked clips):**
   - **`reframe` (`--workflow`, CEL: `== 1` `video_references`):** Adapts a finalized clip across `16:9` / `9:16` / `21:9` / `1:1` without re-rolling action. Priced at `25.5 cr.` (`720p`) / `63 cr.` (`1080p`) per 5s—generate in the target ratio or `outpaint` stills pre-video whenever possible; reserve `reframe` strictly for second-ratio delivery of an irreplaceable master.
   - **`video_deflicker` / `fps_boost`:** Use `video_deflicker` on clean native clips with mild lighting/texture shimmer; avoid `fps_boost` on fast hands, hair, or fabric snaps (optical-flow ghosting).

## 3. Optics Playbook (Lock Before Motion)

Keep all shots inside one location within **one coherent lens family** (`24–35mm` for wide/medium coverage, `50–85mm` for close-ups); unmotivated jumps from `14mm` to `85mm` break spatial realism.

### A. Focal Length × Motion × Risk

| Focal Length | Optical & Psychological Effect | Best Camera Moves | Failure Risk |
| :--- | :--- | :--- | :--- |
| **Ultra-Wide (`8–14mm`)** | Exaggerated foreground scale, edge distortion, frantic energy / claustrophobia | `FPV Drone`, `Snorricam`, `Crash Zoom`, aggressive POV tracking | Corner wall bending; avoid on calm human portraits |
| **Wide (`18–24mm`)** | Strong 3D parallax, readable architecture, grand scale | `Dolly In/Out`, `Truck`, `Crane Up/Down`, `Helicopter` | Tilted horizon if `horizon level` is omitted |
| **Classic Cinema (`35mm`)** | Natural human field of view, grounded presence in room | `Slow Dolly`, `Lateral Track`, `Handheld` (`intimate_observer`), `Static` | **Lowest artifact risk**—default workhorse for AI video |
| **Standard (`50mm`)** | Undistorted faces, gentle background compression | `Slow Push-In`, `Locked-off Tripod`, `45–90° Arc` | Default for dialogue, OTS, and tabletop product shots |
| **Telephoto (`75–85mm+`)** | Flat compressed background, strong subject isolation & emotional intimacy | `Locked-off Tripod`, micro-`Dolly In`, very slow `Arc` | **High warp risk on fast pans/orbits** (shallow DOF + compression tears background) |

### B. Aperture (`f/`-Stop) as Stability Lever

- **`f/1.4` (Wide Open):** Extreme shallow DOF and creamy bokeh; hides distant background micro-shimmer on portraits, but focus plane can breathe during complex camera travel.
- **`f/4` (Moderate — default):** Crisp subject with legible, non-distracting environment; best balance for 70% of narrative and commercial shots.
- **`f/11` (Deep Focus):** Front-to-back sharpness; required for complex tracking shots, `Crane`/`Helicopter`, architecture, and two-plane staging where background detail must stay solid.

### C. Camera Bodies, Glass & Ready-to-Use Recipes

| Visual Goal | Camera Body | Lens / Glass | Focal & Aperture | Motion Pairing |
| :--- | :--- | :--- | :--- | :--- |
| **Commercial Macro / Product Hero** | Modern Digital (`ARRI Alexa`) | `Clean Sharp` / `ARRI Signature Prime` | `50mm`, `f/4` | `Locked-off` or `Slow Dolly In` (`Robo Arm` for kinetic reveal) |
| **Gritty Urban Night / Action** | `RED V-Raptor` or `Sony Venice` | `Anamorphic` (`Hawk V-Lite` — oval bokeh, horizontal flares) | `35–50mm`, `f/1.4` | `Tracking` or `Handheld` (`documentary_snap`) |
| **Intimate Portrait / Memory** | `35mm Film` (`8mm` for lo-fi) | `Cooke` (warm skin roll-off) or `Helios` / `Halation Vintage` (swirly bokeh / glow) | `75–85mm`, `f/1.4–f/2.8` | `intimate_observer` or subtle `Slow Push-In` |
| **Epic Landscape / World-Building** | `IMAX` / Large Format | `Clean Sharp` / `Panavision Spherical` | `18–24mm`, `f/11` | `Crane Up` or `Helicopter Shot` |

*(Pairing `35mm`/`8mm` film stock or Era `1970s–1990s` in Cinema Studio introduces natural organic grain that masks subtle diffusion micro-artifacts better than sterile high-gloss digital presets.)*

## 4. Moves, Rigs, `camera_style`, Speedramps & Transitions

### A. Motivated Move Matrix & Special Rigs

| Move / Rig | Narrative / Commercial Job | Preconditions for Clean Execution |
| :--- | :--- | :--- |
| **`Locked-off static tripod`** | Product legibility, deadpan timing, letting in-frame acting carry the beat | Default whenever subject motion already fills the frame; state explicitly |
| **`Slow Dolly In` / `Out`** | Intimacy, tension, realization (`In`); context reveal, solitude (`Out`) | `35–50mm`, calm pace; add `eases smoothly into a gentle hold` to avoid abrupt clip stops |
| **`Lateral Truck` / `Tracking`** | Spatial reveal past foreground occlusion; pacing alongside a walking subject | Match camera speed to subject stride; keep foreground occluders simple |
| **`45–90° Arc` vs. `360 Orbit`** | Hero product or fashion showcase | **Prefer `45–90° Arc`** in 5s over full `360 Orbit` (360° forces rapid unobserved-back hallucination unless anchored via `3D Jutsu` or multi-angle `R2` plates) |
| **`Crane Up/Down` / `Pedestal`** | Clearing foreground surfaces; shifting between intimate detail and room/site scale | `18–35mm`, `f/4–f/11`, explicit `horizon level` |
| **`Robo Arm` (Bolt/KUKA)** | High-precision luxury product whip/stop trajectories | Clean studio/uncluttered backdrop; single hero object; use Cinema Studio preset |
| **`FPV Drone` / `Helicopter`** | High-energy spatial opener or architectural flythrough | `14–24mm`, `f/11`; use `3D Jutsu` previz whenever threading tight openings |
| **`Snorricam`** | Panic, disorientation, claustrophobic subjective intensity | Wide lens (`14–24mm`), face anchored centered, clear separation between actor and background |
| **`Bullet Time` / `Dolly Zoom`** | Stylized time-freeze showcase / sudden psychological dread (Vertigo) | Stationary or slow-mo hero subject; clean foreground/background depth separation; use native preset rather than prose alone |
| **`Crash Zoom` / `Whip Pan` / `Dutch Angle`** | 0–2s hook, comedic punch, kinetic cut, or visual unease | Keep duration tight; plan cut point at peak blur for `Whip Pan` |
| **`Push to Glass` / `Head Tracking`** | Barrier-crossing scene reveal / locked subject-centered action follow | Keep barrier surface simple (`Push to Glass`); use `Head Tracking` on uncluttered backgrounds to avoid edge smearing |

### B. Live CLI `--camera_style` (`cinematic_studio_video_3_5`)

Use only when `style_prompt` is omitted (CEL mutually exclusive):
- `classic_static` — rigid tripod stillness.
- `silent_machine` — clinical, motorized, zero-jitter tracking (thriller, tech, architecture).
- `one_take` — unbroken single-shot continuity across movement.
- `epic_scale` — sweeping, grand-scale establishing moves.
- `intimate_observer` — subtle, restrained human handheld for drama and dialogue.
- `impossible_camera` — non-physical virtual trajectories (threading tight gaps/surfaces).
- `documentary_snap` — reactive real-time handheld energy.
- `raw_chaos` — frantic, high-energy handheld action.
- `dreamy_flow` — floating, slowed, lyrical drift.

### C. Live CLI `--speedramp` (`cinematic_studio_3_0` vs. `cinematic_studio_video_v2`)

- **`cinematic_studio_3_0` enums:** `auto`, `linear`, `slowmo`, `super_slowmo`, `speedup`, `fast_to_slowmo` (hero impact/pour climax), `slowmo_to_fast`, `impact` (kinetic contact accent).
- **`cinematic_studio_video_v2` enums:** `auto`, `custom`, `linear`, `slowmo`, `speedup`, `impact`. *(Web Cinema Studio also exposes `Flash In`, `Flash Out`, `Bullet Time`, and `Ramp Up`.)*

### D. In-Camera Transitions (Zero Post `xfade` Band-Aids)

- **Whip Pan Bridge:** End Shot A with `fast whip pan right into heavy horizontal motion blur`; open Shot B with `fast whip pan arriving from the left, settling smoothly onto <subject>`. Cut cleanly on 2–3 peak-blur frames.
- **Foreground Wipe:** Track Shot A laterally behind a dark vertical occluder (pillar, doorway frame) until frame fills; emerge Shot B in the same lateral direction from a matching dark edge.
- **Match-on-Direction:** Pair equal-velocity moves (`slow dolly-in` → `slow dolly-in` closer scale) respecting the `180°` axis and `30°` scale/angle shift.

## 5. Execution Rules & Engine Calibration

- **Speed Contrast Law:** Never pair a sprinting/explosive subject with fast multi-axis camera travel over a high-frequency background. Contrast states: stationary subject + expressive camera, OR dynamic subject (counted mechanical steps, `1–2` beats per 5s) + locked tripod or pace-matched tracking.
- **Gaze Anchor & Horizon Lock:** Include an explicit **Gaze Anchor** on every non-UGC human shot (`eyes focused down on the clasp, never looking at the camera`) so camera motion never triggers vlog-style lens stare. Add `tripod fixed, horizon level` on pans, tilts, trucks, and pedestals.
- **Optimal Video Reference Budget (`2–4` Visible Refs):** Exceeding `5–6` image references freezes optical flow into a stiff "living photo" and bleeds pigments. Bind `1` `R3` `--start_image` + `1–2` highest-risk canonical `R2` refs + optional `1` `--end_image`, and pre-lock a **Reverse Wall plate** (`3d_jutsu_angles`) for any OTS, 180° reverse, or mirror shot ([Locations, Buildings & Props](../../video-consistency/references/locations-and-props.md)).
- **Camera-First Engine Selection** (full prompt calibration in [Model Prompting](model-prompting.md)):
  - **`seedance_2_5`** (`30–60w`): Best CLI workflow for 1:1 draft-to-final camera lock (`--draft true` → `--draft_job_id --bitrate_mode high`), `3D Jutsu` `@Video1` tracking, and `video_extension` (`forward`/`backward`).
  - **`cinematic_studio_video_4_0`** (`40–75w`): Best Web Director's Panel presets, up to 30s single takes, and native diegetic foley (`--bitrate_mode high`).
  - **`kling4_0` / `kling_o3_image_reference`** (`60–90w`): Best value native `1080p` (`18.75 cr.`), action physics, native `--multi_shots true`, and `video-edit` motion-locked rescues (`22.5 cr.`).
  - **`veo3_1`** (`40–75w`): Top atmospheric light, natural shallow DOF, and smooth single-subject cinema glides (CLI: `start_image` only).
  - **`wan3_0` / `wan3_0_prime`** (`50–80w`): Top natural fabric/water/light physics on calm shots (CEL: never mix `start_image`/`end_image` with `image_references`; verify FPS—may output `30fps`).
  - **`minimax_h3`** (`45–75w`): Strong facial likeness retention on calm pushes (strict One-Move Rule + Gaze Anchor).
  - **`flux_3_video`** (`40–70w`): Crisp editorial color grade on calm fashion/product takes (CEL: images and `video_references` are mutually exclusive).
- **Cheap Trajectory Validation & Full-Clip Review:** Validate camera path first on Web `Unlimited` (`0 cr.`) or cheap `720p` / `--draft true` runs. Inspect the **entire clip** (start, middle, end—check frame edges for wobble/shimmer, not just Frame 1). Generate 1–2s handles when pacing allows so post assembly can trim weak tails. Change **One Variable Per Re-roll** on retries.

## 6. Camera Failure Diagnostics

| Observed Camera Defect | Root Cause | Exact Fix (One Variable Per Re-roll) |
| :--- | :--- | :--- |
| **Unwanted floating drift on static shot** | Camera behavior omitted from prompt/preset | Add `Locked-off static tripod shot, horizon level` or select `Static` / `classic_static` |
| **Rubber-bending walls or floor warp** | `Pan`/`Zoom` used for 3D parallax OR `Start → End` jump exceeds 5s | Switch verb to `Lateral truck` / `Slow dolly-in`, shorten spatial delta, or route via `3D Jutsu` previz |
| **Camera ignores text or jitters violently** | Active UI preset / `--camera_style` / `@Video1` conflicts with prose camera verbs | Enforce **Zero Double-Command**—remove camera verbs from prose and keep prompt within model word sweet spot |
| **Stiff "living photo" (frozen camera)** | Reference overload (`> 5` images) or static scene restated in motion text | Prune to `2–4` visible refs and strip all static wardrobe/set description from video prompt |
| **Pan edge shimmer / strobe on brick, leaves, or mesh** | Fast pan over high-frequency pattern at `f/11` or FPS mismatch | Slow move (`Calm`), widen aperture (`f/2.8–f/4`), verify `24fps` parity, or run `video_deflicker` on clean native output |
| **Abrupt halt or speed jerk at end of clip** | Unbuffered trajectory hitting 5s boundary | Add easing (`eases smoothly into a gentle hold`), apply `--speedramp fast_to_slowmo`, or trim 0.5–1s tail in assembly |
| **Subject stares at lens during orbit/dolly** | Missing eyeline anchor | Add explicit **Gaze Anchor** (`eyes fixed on <object>, never looking at the camera`) |
| **Great camera move, but 1 prop/object morphs** | Diffusion drift on moving detail | Keep the golden camera take—rescue surgically via `hf_mult_replace_object` (Genjutsu) or `kling4_0 --mode video-edit` |
| **Reverse shot flips room 180°** | Missing Reverse Wall plate or camera-relative left/right text | Lock Reverse Wall (`3d_jutsu_angles`) from `N/E/S/W` map and re-stage `R3` still |

*Done when:* every shot is routed through Section 2's top matching camera tool, locks optics inside one coherent lens family in `R3`, obeys the One-Move Rule and Zero Double-Command, keeps `2–4` visible refs with explicit Gaze Anchor and parallax-accurate verbs, and passes full-clip edge-stability review before native `1080p` mastering.
