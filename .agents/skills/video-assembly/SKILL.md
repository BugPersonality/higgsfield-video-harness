---
name: video-assembly
description: "FFmpeg assembly, R3 still animatics, VO timing, and R4/R5 mastering. Use when building still animatics, checking VO windows, cutting FPS-locked clips, mixing to -14 LUFS, applying LUT/grain finishing, exporting stems, or choosing FFmpeg vs. Remotion."
---

# Video Assembly

Canonical owner of `R3` zero-video-credit still animatics, `R4`/`R5` FPS-locked
FFmpeg editing, VO timing validation, the Audio Level Law, `-14 LUFS` mastering,
finishing unification (`LUT` / `GRAIN`), unbaked `stems/`, and the FFmpeg vs.
Remotion compositor boundary.

## `R3` Zero-Video-Credit Still Animatic

Before requesting `R4` motion budget, record `still.selected_take` (and audio
`selected_file`) in `shotlist.json` and run `make animatic CAMPAIGN=<slug>`
(`scripts/assemble.sh --animatic`). Verify `ad-script`'s **mute test**
([Ad Craft Glossary](../../../docs/ad-craft-glossary.md)) first, then layer VO
and rough music so the Director judges framing, voice cadence, and cut rhythm
before spending video credits.

## `R4` / `R5` FPS Lock & Re-Encoded Assembly

- `scripts/assemble.sh` locks clips to `shotlist.json`'s `fps_target` (falling
  back to Clip 1's probed FPS when omitted), scales with `flags=lanczos`, and
  warns whenever clip resolutions or native FPS diverge across inputs (fix
  `1918×1080` upscales or `30fps` takes in a `24fps` cut at the source rather
  than masking with pillarbox padding or pulldown judder).
- Pass `OUT=campaigns/<slug>/media/exports/draft_cut.mp4` during `R4B`
  (`make assemble` defaults to `master.mp4`).
- Honor `storyboard.md`'s `Cut trigger` (`cut-on-action`, `J-cut`, `L-cut`),
  Kuleshov seam meaning, and `[PAUSE Ns]` holds (giving viewers `1.5–2.5s` on
  key turns to complete `2 + 2` per
  [`video-narrative`](../video-narrative/SKILL.md)), and re-encode inside
  `assemble.sh` (`libx264 -crf 18 -pix_fmt yuv420p -g 30`, `aac 192k 48kHz
  stereo`) rather than `-c copy` concat to prevent cut freezes and A/V desync.

## VO Timing, Audio Level Law & `-14 LUFS` Mastering

- Measure VO bounds with `scripts/qa_media.py voice <wav> --window <sec> --json`
  (`make qa-voice`); when speech overflows its window, rewrite copy and
  regenerate instead of speeding up with `atempo`.
- Enforce the **Audio Level Law**: VO at `1.0` (`0 dB`), diegetic SFX `<= 0.20`,
  music `<= 0.16` under VO (`<= 0.35` music-only).
- Master via two-pass `loudnorm=I=-14:TP=-1.5:LRA=11` so `make qa-render` passes
  `-14 LUFS (±1.0 LU)` and `<= -1.0 dBTP`.

## Stems, Finishing Unification & Compositor Boundary

- Every `make assemble` exports clean unbaked `media/exports/stems/`
  (`video_only.mp4`, `diegetic.wav`, `vo.wav`, `music.wav`, normalized clips).
- **Finishing unification:** When blending native `1080p` footage across engines
  or polishing a theatrical cut, apply a shared 3D LUT and subtle temporal 35mm
  grain directly at `0 cr.` via `make assemble CAMPAIGN=<slug> LUT=<grade.cube> GRAIN=4`
  (`scripts/assemble.sh --lut <file.cube> --grain <1..20>`), OR grade exported
  `stems/` in DaVinci Resolve (optionally expanding `1920×1080` clips via
  `topaz_hyperion_2_5` 10-bit ProRes/EXR first; see
  [Mastering & Upscaling](../higgsfield-cli/references/mastering-and-upscaling.md)).
- **FFmpeg vs. Remotion:** Stay on pure FFmpeg by default; cross into Remotion
  or HyperFrames only when `brief.md` requires animated kinetic typography,
  captions, or crisp brand UI overlays (composite overlays last).

*Done when:* `animatic.mp4` (`R3`), `draft_cut.mp4` (`R4B`), or `master.mp4` +
`stems/` (`R5`) builds cleanly with uniform FPS/resolution, VO fits without
`atempo`, and `make qa-render` passes `-14 LUFS (±1.0 LU)` and `<= -1.0 dBTP`.
