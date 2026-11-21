# Studio Engine Memory (ACE Playbook)

Empirical model and pipeline observations tracked with ACE delta counters (`helpful` / `harmful`),
absolute verification dates (`YYYY-MM-DD`), and lifecycle status (`active`, `stale`, `graduated_to_code`, `archived`).
Keep under 120 lines; `scripts/check-memory.py` flags `active` rules older than 60 days for re-verification.

## Image & Video Models

- [ENG-01] model=bytedance_video_upscale | helpful=0 | harmful=3 | verified=2026-11-20 | status=graduated_to_code
  Upscaling `< 1 Mbps` `480p` drafts to `1080p` creates bright edge halos, muddy faces, `1.4x–2.0x` Laplacian oversharpening, and temporal shimmer. Always master flagship hero shots in native `1080p`; enforced by `qa_media.py batch --strict`, `--crops`, and `check-campaign.py`.
  Evidence: `git:77c9fd7`, `.agents/skills/higgsfield-cli/references/mastering-and-upscaling.md`

- [ENG-02] model=seedream_5_5 | helpful=5 | harmful=0 | verified=2026-11-21 | status=active
  Delivers unretouched 35mm / ARRI live-action skin, fabric, and architectural stone textures without painterly smoothing; strong primary anchor for `R2`/`R3` photorealistic stills (including `Seedream 5.0 Pro` on Web Unlimited).
  Evidence: `.agents/skills/higgsfield-cli/references/model-selection.md`

- [ENG-03] model=gpt_image_2_6 | helpful=0 | harmful=2 | verified=2026-11-20 | status=active
  Tends toward smoothed, painterly/illustrated skin and interior surfaces with heavy orange-vs-blue contrast on residential interiors; avoid for photorealistic live-action commercials.
  Evidence: `.agents/skills/higgsfield-cli/references/model-selection.md`

- [ENG-04] model=wan3_0 | helpful=4 | harmful=0 | verified=2026-11-20 | status=active
  Native `1920x1080` renders hold clean facial and fabric temporal stability without upscaler shimmer at economy CLI fallback pricing; pairs cleanly with `cinematic_studio_video_4_0` after per-shot color matching and shared `grain=2.0`.
  Evidence: `.agents/skills/higgsfield-cli/references/mastering-and-upscaling.md`

- [ENG-05] model=cinematic_studio_video_4_0 | helpful=3 | harmful=1 | verified=2026-11-20 | status=active
  Strong flagship native `1080p` hero motion and multi-beat choreography (`omni_reference`), but can output slightly lifted shadows and lower saturation vs. `wan3_0`; unify contrast and white balance per shot before applying a shared 3D LUT.
  Evidence: `.agents/skills/video-assembly/SKILL.md`

## Channels & Finishing Pipelines

- [ENG-06] model=higgsfield_web_unlimited | helpful=6 | harmful=0 | verified=2026-11-21 | status=active
  Default `0 cr.` visual channel on Unlimited-eligible plans; confirm the UI shows `Unlimited` ON / `0 credits` before queuing and log every run via `scripts/hf_guard.py log-web` so retries and model failures stay visible to `retro_harvest.py`.
  Evidence: `.agents/skills/higgsfield-cli/references/model-selection.md`

- [ENG-07] model=remotion_prores4444_endcard | helpful=2 | harmful=0 | verified=2026-11-20 | status=active
  Export transparent brand wordmark/endcards as `1080p` ProRes 4444 (`yuva444p10le`) and composite them **after** creative 3D LUT grading so exact brand colors and typography never shift.
  Evidence: `.agents/skills/video-assembly/SKILL.md`
