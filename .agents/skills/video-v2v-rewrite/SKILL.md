---
name: video-v2v-rewrite
description: "Single-take live-action V2V rewrite workflow (Shoot Once at Home, multi-angle recam, relight, location/outfit/prop swap, Editing Room). Use when the user supplies existing live-action footage and wants AI angle, light, location, wardrobe, or prop rewrites while keeping real acting 1:1."
---

# Video V2V Rewrite (`v2v_one_take`)

Canonical workflow for turning **one locked-off live-action take** into
multi-angle, relit, re-dressed, or location-swapped edits while keeping lips,
gestures, and audio 1:1 synced (`output time t = source time t`).

## Master Take & Chunking Standards

1. **Master footage:** Prefer one wide, locked-off static `4K` take (`~22mm`,
   clean audio, full subject + workspace visible) so virtual cameras have real
   spatial context.
2. **Chunk to tool caps before generating:**
   - **Seedance 2.5 / Genjutsu V2V:** split into **`6–30s`** blocks (`<= 30s`
     hard cap).
   - **Higgsfield Editing Room (desktop web only, `<= 10 min` source upload):**
     use `Cut here` to split into **`2–15s`** for `Change Angle`, `Move Camera`
     (dolly/pan/orbit), and `Relight`; **`2–30s`** (works across cuts) for
     `Swap Person`, `Change Location`, and `Edit With Brush`.
3. **One change per pass, then chain:** Never combine angle + location + outfit
   + prop swaps in one prompt. Chain single-variable passes (e.g., Pass 1
   Location in Genjutsu `Motion transfer` -> Pass 2 Outfit in Genjutsu
   `Objects swap` -> Pass 3 Prop in Genjutsu `Objects swap`).

## Tool Router & Web UI Traps

| Goal | Primary Tool | Mandatory Setting / Trap Guard |
| :--- | :--- | :--- |
| Multi-angle recam (`<= 13` hard cuts in 30s), orbit (`55°->35°`), 360° rotating key light, 3-frame HEX color grade, prop pop-cleanup | **Seedance 2.5** (`video_references` `@Video 1` + `@Image N`) | Verify UI **duration dropdown** matches exact chunk length; reserve `4K` for short hero moves (`<= 10s`) and `1080p` for `15–30s` passes. |
| Location swap keeping full body motion | **Genjutsu** (`hf_mult_motion_control`) — **`Motion transfer`** | Keep `16:9` `1080p` `<= 29s`; attach clean location ref if needed. |
| Outfit or handheld prop swap on existing clip | **Genjutsu** (`hf_mult_motion_control`) — **`Objects swap`** | **Trap:** Recreate/default links open `Motion transfer` — manually switch mode dropdown to **`Objects swap`** before clicking Generate. Pre-build clean isolated prop/outfit stills first. |
| Fast layered timeline edits on raw footage | **Higgsfield Editing Room** (desktop web) | Stack one tool per non-destructive layer; honor `15s` vs `30s` clip caps. |
| Dense room prop appearance/disappearance | **2-step:** `Seedream 5.5` (`2k` dressed frame 1) -> `Seedance 2.5` (`4k` V2V) | Pop props off sequentially (`~0.15s` apart, 1-frame hard pops, zero smoke/morph) so cut-back to raw footage is seamless. |

## Mandatory V2V Prompt Locks (`9-Block Contract`)

1. **`MASTER — PURE COPY OF @Video 1 (HIGHEST PRIORITY)`:** State
   `"Output second = source second. Frame n = frame n. Wherever this prompt and @Video 1 disagree about the person, hands, or timing, @Video 1 wins. The mouth wins over every event in the world. Do not restart a performance when the camera changes."`
2. **`REFERENCE ISOLATION (TAKE ONLY / DON'T TAKE)`:** For every `@Image N`,
   specify exact trait taken (car design, outfit, room architecture) and ban
   inheriting its framing, studio light, pose, or reflections.
3. **Virtual Camera & Eye-Line Lock:** On alternate angles, state
   `DON'T COPY THE ORIGINAL CAMERA`, specify focal length/aperture/orbit path,
   and lock subject gaze to the **original** off-screen camera point so the
   speaker never stares awkwardly into the virtual lens.
4. **Physical vs. Screen-Space Coordinates:** On overhead or reverse cuts,
   explicitly map physical left/right to screen-left/right and specify honest
   furniture occlusion for injected assets.
5. **3D Facial Relief & Zero-Morph Hard Pops:** Protect shadows under brow,
   cheekbones, nostrils, and jaw (anti-flat beauty light); ban fades, dissolves,
   morphs, smoke, sparkles, circular vignettes, or end-of-clip speedup/freeze.
6. **Per-Object + Tone-Curve HEX Grade (when color-grading via V2V):** Supply
   lit/shadow HEX pairs per key object plus 5 tone-curve anchors (`deepest
   shadows -> brightest point`) and exact frame window (`in about 3 frames`).
7. **`PERFORMANCE TRACK` + `SOUND` + `FAILURE / REJECT CRITERIA`:** List key
   gesture timestamps, exact speech/silence windows, and append every observed
   defect from rejected takes into `FAILURE` before re-rolling.

*Done when:* Every V2V chunk keeps `t -> t` speech/gesture sync verified via
actual MP4 playback + `qa_media.py clip` (and `qa_media.py pixel-diff` on
untouched windows), with zero unrequested morphs, vignettes, or mode-trap slips.
