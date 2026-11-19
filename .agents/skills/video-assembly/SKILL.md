---
name: video-assembly
description: "FFmpeg assembly, R3 still animatics, VO timing checks, and R4/R5 audio mastering. Use when building zero-video-credit still animatics, checking VO timing, cutting clips with FPS lock, enforcing the audio level law, mastering to -14 LUFS, exporting stems, or choosing FFmpeg versus Remotion."
---

# Video Assembly

**`R3` zero-video-credit still animatic.** Before requesting `R4` motion budget, record `still.selected_take` (and audio `selected_file`) in `shotlist.json` and run `make animatic CAMPAIGN=<slug>` (`scripts/assemble.sh --animatic`). Verify `ad-script`'s **mute test** ([Ad Craft Glossary](../../../docs/ad-craft-glossary.md)) first, then layer VO and rough music so the Director judges framing, voice cadence, and cut rhythm before spending video credits.

**FPS lock, motivated cuts & re-encoded concat (`R4`/`R5`).** `scripts/assemble.sh` locks clips to `shotlist.json`'s `fps_target` (falling back to Clip 1's probed FPS when omitted), avoiding 3:2 pulldown judder on `24fps` motion. Pass `OUT=campaigns/<slug>/media/exports/draft_cut.mp4` during `R4B` (`make assemble` defaults to `master.mp4`). Honor `storyboard.md`'s `Cut trigger` (`cut-on-action`, `J-cut`, `L-cut`) and `[PAUSE Ns]` holds, and re-encode inside `assemble.sh` (`libx264 -crf 18 -pix_fmt yuv420p -g 30`, `aac 192k 48kHz stereo`) rather than `-c copy` concat to prevent cut freezes and A/V desync.

**VO timing, Level Law & mastering.** Measure VO bounds with `scripts/qa_media.py voice <wav> --window <sec> --json` (`make qa-voice`); when speech overflows its window, tighten copy and regenerate instead of using `atempo`. Mix with VO at `1.0` (`0 dB`), diegetic SFX `<= 0.20`, music `<= 0.16` under VO (`<= 0.35` music-only), and master via two-pass `loudnorm=I=-14:TP=-1.5:LRA=11` so `make qa-render` passes `-14 LUFS (±1.0 LU)` and `<= -1.0 dBTP`.

**Stems & compositor boundary.** Every `make assemble` exports clean unbaked `media/exports/stems/` (`video_only.mp4`, `diegetic.wav`, `vo.wav`, `music.wav`, normalized clips) for optional DaVinci Resolve finishing. Stay on pure FFmpeg by default; cross into Remotion or HyperFrames only when `brief.md` requires animated kinetic typography, captions, or crisp brand UI overlays.
