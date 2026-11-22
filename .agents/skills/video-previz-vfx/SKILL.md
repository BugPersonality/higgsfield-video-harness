---
name: video-previz-vfx
description: "Spatial blocking, 3D previz (Blender/3D Jutsu), photoreal 4K creatures (Clay->Macro->Flash), 360-degree/mannequin face swaps, and deterministic VFX compositing with pixel-diff QA. Use when shots involve creatures, complex 15-30s blocking, mirrors/loops, or live-action VFX integration."
---

# Previz, 3D Blocking & VFX (`previz_3d_vfx`)

Canonical runbook for **spatial blocking before video spend**, **photoreal 4K
creatures**, **VFX plate integration**, and **deterministic tracking +
pixel-diff verification**.

## 1. Progressive 4-Tier Spatial Blocking Gate (`R1B`)

Choose the lightest tier that guarantees geometry will not break in `R4`:

1. **Tier 1 (Zero-3D Pre-Vis):** Generate cheap B&W pencil/ink storyboard
   sheets (`Seedream 5.5`, 1 sheet per call) for shot count/hand causality,
   plus an **overhead flat schematic blocking map** (`Seedream 5.0 Pro`, exact
   `X%/Y%` coordinates on white, zero shading/labels) or a rough 2-figure
   blocking sketch attached **last** in inputs (`@diagram_coach`).
2. **Tier 2 (Plate Blocking):** On busy location plates, paint a flat **green
   clay-render placeholder** (`Seedream 5.5`) at exact perspective, scale, and
   contact shadow to lock hero vehicles/objects; use red **editorial exclusion
   marks** to strip unwanted foreground clutter cleanly.
3. **Tier 3 (Browser 3D Previz):** Use **3D Jutsu** for multi-room camera paths
   without local Blender.
4. **Tier 4 (Blender Previz via `@higgsfield /use-blender`):** Build `15–30s`
   blocking videos (`@Video`) using **Color-Coded Role & Facing Legends**
   (`GREEN vertical face = front`, `RED vertical face = back`, role colors per
   group) and explicitly warn: `"IGNORE flat placeholder colors — never
   translate a marker color into wardrobe."`
- **Hard Rule — Diagram Separation:** Annotated frames with circles/arrows go
  **only to the LLM prompt writer**; never pass raw markup diagrams into
  `Seedance` (feed only clean layout composites or 3D blockouts).

## 2. Photoreal 4K Creatures & Heavy Props (`Clay -> Macro -> Flash`)

*"The weirder the creature or prop, the more boring the reference photo must
be."* (Applies to creatures and bespoke heavy props; **rooms skip clay** and
originate directly in `Soul Cinema` for natural wear/imperfection.)

1. **Grey Clay Sculpt:** Matte dark-grey clay (`3:4` pose + `16:9` 3-view on
   pure black, feet aligned) in `Seedream 5.5` / `Recraft 4.1` to lock
   silhouette/anatomy.
2. **Biological Face Source:** Real wildlife/anatomy photo (`Soul 2`, `16:9`).
3. **1:1 Edge-to-Edge Macro Material Swatches:** Hard direct flash `1:1` photos
   for each surface (bone, tendon, scales, eyes, patina — `Soul 2`).
4. **"Makeup Test" Boring Flash Photo (`Seedream 5.5`):** Map `@Image 1`
   (clay) + face + swatches into an unstylized frontal-flash photo against a
   dark-grey paper backdrop with hard shadow (`No gloss, CG, or game look`).
5. **Draft Cheap -> Finalize 4K:** Test 3–4 takes in `Seedance 2.5` `480p Draft`
   (`3 cr./s`), then finalize the winner in native `4K` (~64% savings + `2x`
   clean `1080p` punch-in crop via `assemble.sh` `crop_4k_punchin`).
6. **Real-Animal Biomechanics:** Direct creature motion by blending real
   species physics (e.g., ostrich stabilized head + cassowary heavy torso +
   monitor-lizard S-wave tail + kicked soil clods) instead of "monster runs."

## 3. Live-Action VFX, Impossible Shots & Cloud `/gpu` Discipline

- **360° Actor Head + 2-Step Mannequin Face Swap:** Capture a slow `360°`
  head-turn clip (`@char_head_360`) in even light; blur the stand-in's head on
  the plate, or run a Pass-1 **featureless matte-grey mannequin head** before
  Pass-2 face + VFX integration.
- **Pixel-Preservation & Optical Match:** State `"Every pixel outside the
  creature and its shadow comes from the source footage unchanged"`, match
  defocus blur radius, and clamp deepest blacks to surrounding background
  elements.
- **Impossible Shots:**
  - *Droste Endless Loop:* Pass `@Image 1` as both first and last frame, verify
    loop coordinates in Blender, and add `"Keep motion alive throughout — do
    not freeze toward the end."`
  - *Impossible Mirror:* Build an open doorway into a mirrored twin room with a
    brief previz light pulse marking plane crossing.
  - *Hidden Occlusion Cuts:* Route single-take scale jumps through opaque dark
    occlusions + `"The Wall Rule"` (keep transparent housings opaque until the
    subject approaches).
- **Deterministic Tracking & Post-VFX (`Blender` / `AE` / Python):** Anchor
  overlays/X-ray/HUD passes with `SAM 2` (masks, `+10 px` matte expansion) +
  `MediaPipe` (joints + exit velocity extrapolation) + temporal `Video Depth
  Anything` (avoids ~4x per-frame flicker), working in camera-origin space
  (`35mm`). Always disable silent AE color management and verify untouched
  pass-through frames with **`qa_media.py pixel-diff`**!
- **4 Cloud `/gpu` Habits:** (1) Require explicit price quote + approval before
  starting; (2) verify Frame 1 parity against local before batching; (3) upload
  only scripts/meshes/decals; (4) render every revision into a fresh folder and
  run provenance checks before assembly, releasing GPUs immediately on finish.

*Tool availability fallback:* Before choosing Tier 4 local Blender/AE/Python
trackers, check installed local tools (`which blender`, After Effects, GPU
access). If Blender or AE is not installed locally, stay on **Tiers 1–3**
(`Seedream 5.5` B&W storyboards, `X/Y%` maps, Clay placeholders, browser
**3D Jutsu**, `Seedance 2.5`, and FFmpeg + `qa_media.py pixel-diff`) which run
100% with the built-in harness stack.

*Done when:* Spatial blocking is locked before video spend, creature/VFX plates
match plate blur/black-floor, and `qa_media.py pixel-diff` + fresh
`reviewer-agent` MP4 inspection pass cleanly.
