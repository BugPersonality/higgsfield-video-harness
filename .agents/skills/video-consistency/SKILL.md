---
name: video-consistency
description: "Cross-shot character, expression, location, building, and prop continuity. Use when planning R2 Character/Asset Bibles, budgeting reference counts, wiring UUIDs into R3/R4/R5, slicing angle grids, using Motion Control/Intone/Soul ID, or routing real actors."
---

# Video Consistency

Canonical owner of cross-shot **location, building, prop, character, and facial
expression** continuity across `R1B`–`R5`, backed by mechanical validation in
`make campaign-check`.

## Reference Map

Load the runbook matching the entity you are locking (or both for character-in-set
scenes):

| Need | Reference |
| --- | --- |
| Interiors, buildings, reverse walls, neutral `#808080` props, scale/state plates, `N/E/S/W` Spatial Map, `nano_banana_2_relight` 26-point cube & spatial diagnostics | [`references/locations-and-props.md`](references/locations-and-props.md) |
| Character Bibles (Tier 1–3), *Identity ≠ Mimicry* law, Expression Calibration, `Soul ID` / Kling Elements, `Motion Control` driving-video specs, `Intone` lip-sync, real-actor routing & face diagnostics | [`references/characters-and-expressions.md`](references/characters-and-expressions.md) |

## Cross-Cutting Continuity Laws

- **Reference Budget Law (enforced by `check-campaign.py`):** Never confuse
  library/training size with per-shot inputs—excess refs cause attention dilution,
  pigment bleed, and stiff "living photo" motion:
  - **`R3` Stills:** **`3–5` visible refs** (warns `> 6`), picking `1–2`
    angle/expression-matched cast plates.
  - **`R4` / `R5` Video:** **`2–4` visible refs** (max **`5`**, warns `> 5`):
    `1` locked `R3` `--start_image` + `1–2` highest-risk canonical `R2` UUIDs +
    optional `1` `--end_image`.
  - **Visibility Pruning & Noun Pairing:** Omit all off-screen props, walls, and
    unused angles, and always pair every `@ImageN` tag with its concrete noun
    (`the kettle from @Image2`).
- **Canonical Source Law (Zero Photocopy Cascade):** Never chain compressed
  video screenshots (`.last_frame`) shot-over-shot without canonical `R2` Master
  UUIDs in `--image_references`.
- **Clean Neutral Masters & Grid Slicing:** Shoot `R2A` location masters empty
  (**Empty Set Law**) and `R2A` prop/cast masters on flat `#808080` matte
  mid-gray under soft diffused `5000–5600K` light (kills *Lighting Bake-In*),
  with characters in a static relaxed `50–85mm` pose (**Static Pose Rule**).
  Always slice `2x2`/`3x3` angle sheets (`nano_banana_2_shots`) via
  `make slice-grid` before uploading standalone PNG tiles—never pass raw grids
  to video models.

## Round-by-Round Pipeline (`R1B` → `R5`)

1. **`R1B` — Triage & Spatial/Cast Blueprint (`0 cr.`):** Run Fast Triage in
   both runbooks. Write an absolute `N / E / S / W` Spatial Map, one verbatim
   `Immutable Identity Block` (for `R3` stills only), and per-shot `CAM` facing
   wall, `FRAMING` (`MCU` preferred for acting), `EXPRESSION (START → END)`,
   `GAZE ANCHOR`, and mutable `PROP STATE` in `storyboard.md` / `shotlist.json`,
   prefixing IDs (`cast_<name>_*`, `loc_<set>_*`, `bldg_<name>_*`, `prop_<item>_*`).
   Verify `make campaign-check`.
2. **`R2A` — Lock Masters (Unlimited-First):** Generate `A / B / C` Masters under
   `media/lookbook/{characters,locations,props}/`, filter via `reviewer-agent`,
   normalize mismatched client ratios via `outpaint` / `flux_2_pro_outpaint`,
   and lock `approved_upload_id`s.
3. **`R2B` — Expand Only Triggered Plates (`variants_requested: 1`):** Derive
   Reverse Walls, `3/4` + soft-profile (`60–80°`) cast angles, Expression
   Calibration plates (natural open-teeth smile + speaking mouth), body/scale/state
   plates, or relight/stylist/skin/cutout variants strictly from locked `R2A`
   Master UUIDs. Train `Soul ID` or Web Kling Elements only for Tier 3
   multi-outfit / 15+ scene heroes.
4. **`R3` — Stage `2k`/`4k` Keyframes:** Assemble set + cast + visible props
   (`3–5` refs), **bake 40–60% of the shot's target expression** into the still,
   render `WS` at `2k`/`4k` with close-up `R2A` face attached (*anti-Wide-Shot
   Face Collapse*), and lock/upload stills before spending video credits.
5. **`R4` / `R5` — Delta Motion, Acting Transfer & Surgical Rescue:** Strip
   static appearance and facial-feature prose from video prompts (**Two-Details
   Rule**), direct acting via timed FACS micro-beats + Gaze Anchor in `4–6s`
   clips (or native multi-shot inside one room), route consented real actors
   hitting `Seedance` moderation to `kling4_0` / `kling3_0_motion_control` /
   `soul-id` / `intone`, use `kling3_0_motion_control` / `hf_mult_motion_control*`
   for exact performance transfer and `intone` for audio-first lip-sync, and
   rescue single drifted props (`hf_mult_replace_object*`) or softened mid-clip
   faces (`kling4_0 --mode video-edit` / Web Face Swap) instead of discarding
   golden takes.

*Done when:* `make campaign-check` passes cleanly, every triggered `R2A`/`R2B`
plate is `LOCKED` with verified UUIDs, every `R3` (`3–5` refs) and `R4`/`R5`
(`2–4` refs, max `5`) shot binds only visible canonical anchors with `@ImageN`
nouns, and `reviewer-agent` passes facial, spatial, reflection, scale, and
prop-state continuity across cuts.
