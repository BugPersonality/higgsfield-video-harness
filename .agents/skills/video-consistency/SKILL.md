---
name: video-consistency
description: "Two-step cross-shot identity and continuity locking. Use when anchoring R2 Lookbook entities, wiring approved_upload_id and references[] into R3 stills and R4/R5 omni_reference motion, bridging frames, or training Soul-2 IDs."
---

# Video Consistency

**Continuity Lock & Taste Memory.** Enforce the three-part **Continuity lock** ([Ad Craft Glossary](../../../docs/ad-craft-glossary.md)) carried into `shotlist.json` alongside `taste-log.md`: **Product** (form, finish, label facing, scale), **Lighting & palette** (fixed key side, quality, color temperature), and **Space, cast & axis** (layout, cast markers, active hand, screen direction, 180-degree axis).

**Two-step anchoring (`R2` → `R3` → `R4`/`R5`).** Upload clean source product photos once via `hf_guard.py upload` (`references[].upload_id`). Lock `R2` Lookbook winners (`lookbook[].approved_upload_id`, `status: "LOCKED"`), wire both source `references[]` and `LOCKED` Lookbook UUIDs into every `R3` still, then bind each `LOCKED` still as `--start_image` alongside the original UUIDs in `--image_references` across `R4`/`R5`. Keep source photographs as the primary product anchor rather than compressed video screenshots.

**Character isolation (`R2` before `R3`).** Lock any invented human talent as an isolated `R2` Lookbook portrait *without* the hero product first, then stage product interaction in `R3` stills so facial likeness and object geometry never compete in one pass.

**Topology & frame bridges.** Use a single 3-panel storyboard sheet (`marketing_studio_video` `from_storyboard`) for fast UGC energy; use per-shot `R3` stills + `omni_reference` (`--start_image` + `--image_references`) for precision commercials with cut-by-cut Dailies. Bridge continuous cuts via `--start_image` + `--end_image` or an extracted final frame (keeping original `references[]` in `--image_references`).

**Soul-2 training (`R2`).** Train a Soul ID (`hf_guard.py run --campaign <dir> --shot <lb_id> --command soul-id --model soul_2 --kind lookbook --round R2 --round-cap <N> -- --name <Name> --soul-2 ...`) when recurring talent crosses many angles/outfits. Supply 8–10 uniform, evenly lit medium-close/chest-up photos (within the 5–20 CLI range) and target `text2image_soul_v2` via `--custom_reference_id` (note: `text2image_soul_v2` forbids pairing `--style_id` with `--image_references`).
