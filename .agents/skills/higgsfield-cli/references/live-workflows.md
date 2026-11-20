# Live Higgsfield CLI Gotchas & Guarded Recipes

Inspect `higgsfield <cmd> --help`, `higgsfield model get <id> --json`,
`higgsfield workflow get <id> --json`, and `python3 scripts/hf_guard.py --help`
for live flags and schemas.

## Non-Obvious CLI Gotchas

1. **`omni_reference` is mandatory for frame/image refs (no `i2v` mode):** both
   `cinematic_studio_video_4_0` (`--workflow`) and `seedance_2_5` (model) default
   `--mode` to `t2v` (valid modes: `t2v`, `omni_reference`, `video_edit`,
   `video_extension`). Pass `--mode omni_reference` whenever supplying
   `--start_image`, `--end_image`, or `--image_references` (and on `seedance_2_5`,
   never combine `--draft true` with `--draft_job_id`). `marketing_studio_video`
   is also a `--workflow`, not a model.
2. **Draft escalation & free `high` bitrate (`seedance_2_5` vs. `cinematic_studio_video_4_0`):**
   `cinematic_studio_video_4_0` CLI does **not** expose `--draft` or
   `--draft_job_id`; use `seedance_2_5` directly whenever an `R4` take must
   escalate 1:1 into `R5` via `--draft_job_id`. `--draft_job_id` accepts only a
   `seedance_2_5 --draft true` job UUID, and CEL still requires supplying
   `--start_image` / `--image_references` whenever `--mode omni_reference` is
   active. On both `seedance_2_5` and `cinematic_studio_video_4_0`, pass
   `--bitrate_mode high` on `1080p` finals (`0 cr.` surcharge vs. `standard`).
3. **Upscaler & finishing CLI gotchas:**
   - `topaz_video` currently rejects `higgsfield generate cost` (`does not
     support alpha v2 cost estimation`); quote and run Topaz Starlight in the
     Higgsfield Web UI or externally.
   - `topaz_hyperion_2_5` (SDR→10-bit ProRes/EXR, not a resolution upscaler)
     rejects video dimensions not divisible by 4 (works on `1920×1080`; fails on
     `854×480` and `1918×1080`).
   - `bytedance_video_upscale` accepts **video job UUIDs** (not raw CloudFront
     URLs) in `--video_references`, rounds `854×480` inputs to `1918×1080`, and
     in `pro` mode injects edge halos on compressed `480p` clips (never upscale
     `480p`—see [Mastering & Upscaling](mastering-and-upscaling.md)).
   - `wan3_0` / `wan3_0_prime` forbid combining `start_image`/`end_image` with
     `image_references` (CEL-enforced) and may output `30fps`; verify FPS before
     mixing into a `24fps` cut.
4. **`generate cost` traps (auto-upload, workflow `cost_params` & unquotable
   endpoints):** before Director approves uploading private media (`R1`), pass
   only cost-affecting flags or already-uploaded / placeholder UUIDs—never local
   paths under `media/references/`, which `generate cost` auto-uploads.
   `generate cost workflow <name>` accepts only `cost_params` from
   `workflow get <name> --json` (`hf_guard.py` filters these automatically).
   Verify live quoting before committing to `soul-id` (no `soul-id cost`
   command), `topaz_video`, or `marketing_studio_video --specific_mode
   from_storyboard` (whose live `cost_params` omit `storyboard_id` while
   validation requires it).
5. **All workflow/model parameter flags use `snake_case`:** pass `--start_image`,
   `--end_image`, `--image_references`, `--video_references`, `--audio_references`,
   `--aspect_ratio`, `--bitrate_mode`, `--dynamic_range`, `--extension_mode`,
   `--draft_job_id`, `--custom_reference_id`, `--voice_id`, `--voice_type`,
   `--specific_mode`.
6. **Guard boundary & per-variant `product-photoshoot`:** pass `hf_guard.py`
   flags before `--` and only model/workflow params after `--` (never duplicate
   `generate create`, `--wait`, or `--json`). For `product-photoshoot`, run
   separate `--count 1` calls per `--variant A|B|C` with distinct `--out` paths
   so every variant is saved.
7. **Spatial, outpaint, relight, decomposition & prop-rescue CEL traps:**
   - `nano_banana_2_shots`, `outpaint`, `flux_2_pro_outpaint`, `image_background_remover`,
     and workflow `image_decompose` require **exactly 1** `--image_references`
     entry and accept **no `--prompt`** (`flux_2_pro_outpaint` also requires at
     least one non-zero `--expand_left|right|top|bottom`).
   - Single-ref utilities (`outpaint`, `flux_2_pro_outpaint`, `nano_banana_2_shots`,
     `nano_banana_2_relight`, `image_background_remover`, `hf_mult_replace_object*`)
     validate ref counts even during `generate cost`—quote them using an already-uploaded
     UUID, never an unapproved local file path.
   - `nano_banana_2_relight` requires all five flags (`--image_references`,
     `--light_source` using the 26-point 3D cube `[f|m|b][u|m|d][l|m|r]` except `mmm`,
     `--light_quality`, `--color`, `--brightness`).
   - `flux_3_video` forbids mixing `--video_references` with any image inputs
     (`--start_image`, `--end_image`, `--image_references`), and caps total
     images at `10`.
   - `kling_o3_image_reference` requires `--multi_prompt` if and only if
     `--multi_shots true` (`std` `6.25 cr.` / `pro` `10 cr.` for 5s).
   - `hf_mult_replace_object` (`480p`–`1080p`) and `hf_mult_replace_object_flash`
     (Genjutsu Lite, `720p`–`4k`) require **exactly 1** `--video_references`
     and **`>= 1`** `--image_references`.
   - Creating Cinema Studio Elements or `kling_element_ids` is Web-UI only; CLI
     accepts pre-existing `kling_element_ids` or uploaded `--image_references` UUIDs.
8. **Camera workflow CEL, default & cost traps (see [Camera Control](../../video-direction/references/camera-control.md)):**
   - `cinematic_studio_video_3_5` (`--workflow`, `25 cr.` `720p` / `65 cr.` `1080p` for 5s):
     `--camera_style` / `--light_scheme` / `--color_grading` are **mutually exclusive**
     with `--style_prompt` (CEL-enforced); `duration` defaults to **`15`** and
     `prompt_language` defaults to **`zh`**—always pass `--duration 5 --prompt_language en`
     unless a 15s clip or Chinese prompt is intended; `<= 15` total media refs.
   - `cinematic_studio_3_0` (`--workflow`, `25 cr.` `720p` / `65 cr.` `1080p` for 5s,
     supports `4k` + `--speedramp`): `prompt_language` defaults to **`zh`**—pass
     `--prompt_language en`; `<= 15` total media refs. (`cinematic_studio_video_v2`
     accepts `speedramp` in `auto|custom|linear|slowmo|speedup|impact`.)
   - `cinematic_studio_image` (`--workflow`): caps `--image_references` at `<= 4`
     and exposes `camera_focal_length_id` alongside `camera_model_id`, `camera_lens_id`,
     and `camera_aperture_id`.
   - `kling_4_0_flash` omits `--end_image` (use `kling4_0`, `kling_o3_flf`, `seedance_2_5`,
     or `wan3_0` for Start+End bridges; `kling_o3_flf` requires `--start_image` whenever
     `--end_image` is set). `seedance_2_0` and `seedance_2_0_mini` cap total images
     (including start/end) at `<= 9` (`<= 12` total media).
   - `draw_to_video` (`--workflow`, `26 cr.` `720p` / `63.5 cr.` `1080p` for 5s):
     requires **exactly 1** sketch/annotated image in `--image_references` (no `--start_image`/`--end_image`).
   - `reframe` (`--workflow`, `25.5 cr.` `720p` / `63 cr.` `1080p` for 5s):
     requires **exactly 1** `--video_references` (no `--end_image`); reserve for adapting
     an already-locked master to a second aspect ratio rather than replacing native-ratio
     generation or pre-video `outpaint`.
9. **Character, expression, Motion Control & Intone CEL traps:**
   - `text2image_soul_v2` and `soul_cinematic` (`0.12 cr.`) both cap
     `--image_references` at `<= 1`; `text2image_soul_v2` also forbids combining
     `--style_id` with `--image_references`. `higgsfield soul-id create` accepts
     `5–20` `--image` inputs in CLI (`20–80` in Web UI) and has no `soul-id cost`
     subcommand yet—verify cost in Web before running.
   - `kling3_0_motion_control` is a **`--workflow`** (`10 cr.` `std` / `15 cr.`
     `pro` for 5s) accepting **no `--prompt`**, requiring **exact `1`**
     `--image_references` and **exact `1`** `--video_references`, plus
     `--background_source input_image|input_video`. Its `cost_params` require
     `--duration <sec>` while execution `params` omit it—pass `--duration`
     after `--` in `hf_guard.py` (which sends it to `generate cost workflow`
     and strips cost-only params before `generate workflow`—same for
     `voice_change`, `dubbing`, and `marketing_studio_v2_reference2video`).
   - `hf_mult_motion_control` (Genjutsu) and `hf_mult_motion_control_flash`
     (Genjutsu Lite) require **`>= 1`** `--image_references` and **exact `1`**
     `--video_references` (`480p|720p|1080p`), accept optional `--prompt`, and
     validate ref counts even during `generate cost` (quote with uploaded UUIDs).
   - `intone` (Higgsfield Intone) validates ref counts even during
     `generate cost` (quote with uploaded UUIDs): requires `1–6`
     `--audio_references` AND either `1–2` `--character_images` (plus optional
     `--location_image`) **OR** exactly `2` `--image_references` (character
     first, location second) with neither `--character_images` nor
     `--location_image` set. None of `kling3_0_motion_control`,
     `hf_mult_motion_control*`, or `intone` accept `--start_image`/`--end_image`.
   - `nano_banana_2_ai_stylist` requires `--image_references` plus at least one
     of `--outfit_preset_ids` or `--user_outfit_ids`; `nano_banana_2_skin_enhancer`
     requires `--image_references` and `--preset_id`.

## Minimal Guarded Recipes

```bash
# Free read-only schema & cost quote (0 cr.; never pass private local file paths)
higgsfield model get seedance_2_5 --json
higgsfield generate cost seedance_2_5 --mode omni_reference --draft true --duration 5 --prompt "test" --start_image <uploaded_uuid> --json
higgsfield generate cost kling4_0 --mode reference-to-video --resolution 1080p --duration 5 --prompt "test" --start_image <uploaded_uuid> --json

# Tracked upload (0 cr.; --round R2 for Lookbook, R3 for skipped-R2 photos or locked stills)
python3 scripts/hf_guard.py upload --campaign campaigns/<slug> \
  --file campaigns/<slug>/media/references/hero.jpg --ref-id ref_hero --round R2

# R2 Lookbook per-variant product-photoshoot (repeat for --variant B, C)
python3 scripts/hf_guard.py run --campaign campaigns/<slug> \
  --shot lb_product_hero --kind lookbook --round R2 --round-cap 35 \
  --variant A --version 1 --command product-photoshoot --model gpt_image_2 \
  --out campaigns/<slug>/media/lookbook/lb_product_hero-v1-A.png -- \
  --mode lifestyle_scene --count 1 --image <ref_uuid> \
  --prompt "Cool misty morning limestone bench, matte brushed texture"

# R2 Lookbook world/cast still (gpt_image_2_6)
python3 scripts/hf_guard.py run --campaign campaigns/<slug> \
  --shot lb_traveler --kind lookbook --round R2 --round-cap 35 \
  --variant A --version 1 --model gpt_image_2_6 \
  --prompt-file campaigns/<slug>/prompts/lb_traveler_v1.txt \
  --out campaigns/<slug>/media/lookbook/lb_traveler-v1-A.png -- --aspect_ratio 16:9

# R2 Location / Angle / Relight / Decompose recipes (Asset Bible expansion)
python3 scripts/hf_guard.py run --campaign campaigns/<slug> \
  --shot lb_room_master --kind lookbook --round R2 --round-cap 35 \
  --variant A --version 1 --model soul_location \
  --prompt-file campaigns/<slug>/prompts/lb_room_v1.txt \
  --out campaigns/<slug>/media/lookbook/lb_room_master-v1-A.png -- --aspect_ratio 16:9

python3 scripts/hf_guard.py run --campaign campaigns/<slug> \
  --shot lb_room_reverse --kind lookbook --round R2 --round-cap 35 \
  --variant A --version 1 --model 3d_jutsu_angles \
  --prompt-file campaigns/<slug>/prompts/lb_room_reverse_v1.txt \
  --out campaigns/<slug>/media/lookbook/lb_room_reverse-v1-A.png -- \
  --aspect_ratio 16:9 --resolution 2k --image_references <room_master_uuid>

python3 scripts/hf_guard.py run --campaign campaigns/<slug> \
  --shot lb_room_night --kind lookbook --round R2 --round-cap 35 \
  --variant A --version 1 --model nano_banana_2_relight \
  --out campaigns/<slug>/media/lookbook/lb_room_night-v1-A.png -- \
  --image_references <room_master_uuid> --light_source fml \
  --light_quality soft --color "#f5b87a" --brightness 35

# R2 Outpaint mismatched client photo / mint 3x3 angle sheet & slice clean 2K tiles
python3 scripts/hf_guard.py run --campaign campaigns/<slug> \
  --shot lb_room_wide --kind lookbook --round R2 --round-cap 35 \
  --variant A --version 1 --model outpaint \
  --out campaigns/<slug>/media/lookbook/lb_room_wide-v1-A.png -- \
  --aspect_ratio 16:9 --image_references <client_photo_uuid>

python3 scripts/hf_guard.py run --campaign campaigns/<slug> \
  --shot lb_room_sheet --kind lookbook --round R2 --round-cap 35 \
  --variant A --version 1 --model nano_banana_2_shots \
  --out campaigns/<slug>/media/lookbook/lb_room_sheet-v1-A.png -- \
  --aspect_ratio 16:9 --image_references <room_master_uuid>
# Slice 3x3 sheet into clean standalone tiles before uploading winners via hf_guard.py upload:
make slice-grid FILE=campaigns/<slug>/media/lookbook/lb_room_sheet-v1-A.png \
  OUT_DIR=campaigns/<slug>/media/lookbook/tiles ROWS=3 COLS=3 TRIM=4 PREFIX=loc_room

python3 scripts/hf_guard.py run --campaign campaigns/<slug> \
  --shot lb_prop_clean --kind lookbook --round R2 --round-cap 35 \
  --variant A --version 1 --model image_decompose --workflow \
  --out campaigns/<slug>/media/lookbook/lb_prop_clean-v1-A.png -- \
  --mode granular --image_references <cluttered_photo_uuid>

# R4/R5 Continuous same-set extension (Seedance 2.5 video_extension)
python3 scripts/hf_guard.py run --campaign campaigns/<slug> \
  --shot s03 --kind video --round R4B --round-cap 40 --version 1 \
  --model seedance_2_5 --prompt-file campaigns/<slug>/prompts/s03_ext_v1.txt \
  --out campaigns/<slug>/media/shots/s03-draft-v1.mp4 -- \
  --mode video_extension --extension_mode forward --resolution 720p --duration 5 \
  --video_references <s02_job_id> --image_references <canonical_prop_uuid>

# R4/R5 Surgical prop rescue inside an approved clip (Genjutsu / Genjutsu Lite)
python3 scripts/hf_guard.py run --campaign campaigns/<slug> \
  --shot s02 --kind video --round R5 --round-cap 100 --version 2 \
  --model hf_mult_replace_object \
  --prompt-file campaigns/<slug>/prompts/s02_prop_fix_v2.txt \
  --out campaigns/<slug>/media/shots/s02-1080p-v2.mp4 -- \
  --resolution 1080p --video_references <locked_clip_job_id> \
  --image_references <canonical_prop_uuid>

# R4/R5 Camera-style / speedramp / motion-transfer / post-reframe workflows
python3 scripts/hf_guard.py run --campaign campaigns/<slug> \
  --shot s04 --kind video --round R4B --round-cap 60 --version 1 \
  --model cinematic_studio_video_3_5 --workflow \
  --prompt-file campaigns/<slug>/prompts/s04_video_v1.txt \
  --out campaigns/<slug>/media/shots/s04-draft-v1.mp4 -- \
  --resolution 720p --duration 5 --aspect_ratio 16:9 --prompt_language en \
  --camera_style intimate_observer --light_scheme window \
  --start_image <s04_still_uuid>

python3 scripts/hf_guard.py run --campaign campaigns/<slug> \
  --shot s05 --kind video --round R4B --round-cap 60 --version 1 \
  --model cinematic_studio_3_0 --workflow \
  --prompt-file campaigns/<slug>/prompts/s05_video_v1.txt \
  --out campaigns/<slug>/media/shots/s05-draft-v1.mp4 -- \
  --resolution 720p --duration 5 --aspect_ratio 16:9 --prompt_language en \
  --speedramp fast_to_slowmo --start_image <s05_still_uuid>

python3 scripts/hf_guard.py run --campaign campaigns/<slug> \
  --shot s06 --kind video --round R4B --round-cap 60 --version 1 \
  --model hf_mult_motion_control \
  --prompt-file campaigns/<slug>/prompts/s06_motion_v1.txt \
  --out campaigns/<slug>/media/shots/s06-draft-v1.mp4 -- \
  --resolution 720p --video_references <previz_or_ref_video_uuid> \
  --image_references <s06_still_uuid> --image_references <canonical_prop_uuid>

python3 scripts/hf_guard.py run --campaign campaigns/<slug> \
  --shot s04 --kind video --round R5 --round-cap 120 --version 2 \
  --model reframe --workflow \
  --out campaigns/<slug>/media/shots/s04-9x16-v2.mp4 -- \
  --resolution 1080p --aspect_ratio 9:16 --video_references <locked_16x9_job_id>

# R2 Cast Lookbook (0.12 cr.) & R4/R5 Acting Transfer (Kling 3.0 Motion Control workflow, 10/15 cr. 5s)
python3 scripts/hf_guard.py run --campaign campaigns/<slug> \
  --shot cast_lead_front --kind lookbook --round R2 --round-cap 35 \
  --variant A --version 1 --model soul_cast \
  --prompt-file campaigns/<slug>/prompts/cast_lead_v1.txt \
  --out campaigns/<slug>/media/lookbook/cast_lead-v1-A.png -- --aspect_ratio 16:9

# No --prompt on CLI kling3_0_motion_control; --duration is cost-only and stripped automatically on exec by hf_guard.py
python3 scripts/hf_guard.py run --campaign campaigns/<slug> \
  --shot s04 --kind video --round R4B --round-cap 40 --version 1 \
  --model kling3_0_motion_control --workflow \
  --out campaigns/<slug>/media/shots/s04-motion-v1.mp4 -- \
  --duration 5 --mode pro --background_source input_image \
  --image_references <s04_still_uuid> --video_references <actor_driver_uuid>

# R4/R5 Audio-driven talking & lip-sync (Higgsfield Intone, 1-2 character_images + 1-6 audio_references)
python3 scripts/hf_guard.py run --campaign campaigns/<slug> \
  --shot s05 --kind video --round R5 --round-cap 100 --version 1 \
  --model intone --prompt-file campaigns/<slug>/prompts/s05_intone_v1.txt \
  --out campaigns/<slug>/media/shots/s05-intone-1080p-v1.mp4 -- \
  --aspect_ratio 16:9 --resolution 1080p --bitrate_mode high \
  --character_images <cast_front_uuid> --character_images <cast_smile_uuid> \
  --location_image <loc_master_uuid> --audio_references <vo_line_uuid>

# R3 Keyframe still (surgical v2 re-roll uses cumulative round_spent + delta_cap)
python3 scripts/hf_guard.py run --campaign campaigns/<slug> \
  --shot s02 --kind still --round R3 --round-cap 50 --version 2 \
  --model gpt_image_2_6 --prompt-file campaigns/<slug>/prompts/s02_still_v2.txt \
  --out campaigns/<slug>/media/stills/s02-v2.png -- \
  --aspect_ratio 16:9 --image_references <ref_uuid> --image_references <lb_uuid>

# R3 Keyframe still enhancement before R4 video (2k/4k still upscale, exactly 1 image_references)
python3 scripts/hf_guard.py run --campaign campaigns/<slug> \
  --shot s02 --kind still --round R3 --round-cap 50 --version 3 \
  --model bytedance_image_upscale \
  --out campaigns/<slug>/media/stills/s02-v3-4k.png -- \
  --resolution 4k --image_references <s02_still_uuid>

# R4A Motion Pilot -> R5 Native 1080p Final (Seedance 2.5 latent escalation, preserves exact draft motion)
python3 scripts/hf_guard.py run --campaign campaigns/<slug> \
  --shot s02 --kind video --round R4A --round-cap 20 --version 1 \
  --model seedance_2_5 --prompt-file campaigns/<slug>/prompts/s02_video_v1.txt \
  --out campaigns/<slug>/media/shots/s02-draft-v1.mp4 -- \
  --mode omni_reference --draft true --duration 5 --aspect_ratio 16:9 \
  --start_image <s02_still_uuid> --image_references <ref_uuid>

# Note: CEL requires keeping --start_image / refs when --mode omni_reference is set
python3 scripts/hf_guard.py run --campaign campaigns/<slug> \
  --shot s02 --kind video --round R5 --round-cap 100 --version 1 \
  --model seedance_2_5 --prompt-file campaigns/<slug>/prompts/s02_video_v1.txt \
  --out campaigns/<slug>/media/shots/s02-1080p-v1.mp4 -- \
  --mode omni_reference --draft_job_id <seedance_draft_job_id> \
  --start_image <s02_still_uuid> --image_references <ref_uuid> \
  --resolution 1080p --bitrate_mode high --duration 5 --aspect_ratio 16:9

# R4B 720p Draft -> R5 Value Native 1080p (Kling 4.0: 7.5 cr. flash draft -> 18.75 cr. native 1080p)
python3 scripts/hf_guard.py run --campaign campaigns/<slug> \
  --shot s01 --kind video --round R4B --round-cap 40 --version 1 \
  --model kling_4_0_flash --prompt-file campaigns/<slug>/prompts/s01_video_v1.txt \
  --out campaigns/<slug>/media/shots/s01-draft-v1.mp4 -- \
  --mode reference-to-video --resolution 720p --duration 5 --aspect_ratio 16:9 \
  --start_image <s01_still_uuid> --image_references <ref_uuid>

python3 scripts/hf_guard.py run --campaign campaigns/<slug> \
  --shot s01 --kind video --round R5 --round-cap 100 --version 1 \
  --model kling4_0 --prompt-file campaigns/<slug>/prompts/s01_video_v1.txt \
  --out campaigns/<slug>/media/shots/s01-1080p-v1.mp4 -- \
  --mode reference-to-video --resolution 1080p --duration 5 --aspect_ratio 16:9 \
  --start_image <s01_still_uuid> --image_references <ref_uuid>

# R4B 720p -> R5 Native 1080p Single-Frame I2V (Wan 3.0: 8.75 cr. -> 17.5 cr.; never mix start_image + image_references)
python3 scripts/hf_guard.py run --campaign campaigns/<slug> \
  --shot s05 --kind video --round R5 --round-cap 100 --version 1 \
  --model wan3_0 --prompt-file campaigns/<slug>/prompts/s05_video_v1.txt \
  --out campaigns/<slug>/media/shots/s05-1080p-v1.mp4 -- \
  --resolution 1080p --duration 5 --aspect_ratio 16:9 --start_image <s05_still_uuid>

# R5 Motion-Locked Native 1080p Rescue (re-render a golden 480p take natively instead of upscaling; 22.5 cr.)
python3 scripts/hf_guard.py run --campaign campaigns/<slug> \
  --shot s03 --kind video --round R5 --round-cap 100 --version 1 \
  --model kling4_0 --prompt-file campaigns/<slug>/prompts/s03_video_v1.txt \
  --out campaigns/<slug>/media/shots/s03-1080p-v1.mp4 -- \
  --mode video-edit --resolution 1080p --duration 5 --aspect_ratio 16:9 \
  --video_references <draft_job_id> --image_references <s03_still_uuid> --image_references <ref_uuid>

# R5 Depth-Map Extraction for Motion-Guided Native Re-Render (7.57 cr.)
python3 scripts/hf_guard.py run --campaign campaigns/<slug> \
  --shot s03 --kind video --round R5 --round-cap 100 --version 2 \
  --model depth_anything_video \
  --out campaigns/<slug>/media/shots/s03-depth-720p.mp4 -- \
  --colormap grayscale --variant VDA-Large --resolution 720p --video_references <draft_job_id>

# R5 Direct Native 1080p Hero (Cinema Studio 4.0, always --bitrate_mode high)
python3 scripts/hf_guard.py run --campaign campaigns/<slug> \
  --shot s04 --kind video --round R5 --round-cap 100 --version 1 \
  --model cinematic_studio_video_4_0 --workflow \
  --prompt-file campaigns/<slug>/prompts/s04_video_v1.txt \
  --out campaigns/<slug>/media/shots/s04-1080p-v1.mp4 -- \
  --mode omni_reference --resolution 1080p --bitrate_mode high --duration 5 \
  --aspect_ratio 16:9 --start_image <s04_still_uuid> --image_references <ref_uuid>

# R5 Selective Pixel Upscale Pilot (ONLY clean >=720p source, <=2x, matched --fps, job UUID, 1-shot 1:1 crop check first)
python3 scripts/hf_guard.py run --campaign campaigns/<slug> \
  --shot s06 --kind video --round R5 --round-cap 100 --version 1 \
  --model bytedance_video_upscale \
  --out campaigns/<slug>/media/shots/s06-1080p-pilot.mp4 -- \
  --model_version standard --preset aigc --resolution 1080p --fps 24 \
  --video_references <clean_720p_job_id>

# R5 Pre-Assembly QA: per-clip 1:1 crops + cross-shot batch audit (0 cr.)
python3 scripts/qa_media.py clip campaigns/<slug>/media/shots/s02-1080p-v1.mp4 \
  --sheet campaigns/<slug>/qc/s02_r5_sheet.png \
  --crops campaigns/<slug>/qc/s02_r5_crops.png --json
python3 scripts/qa_media.py batch campaigns/<slug>/media/shots/s01-1080p-v1.mp4 \
  campaigns/<slug>/media/shots/s02-1080p-v1.mp4 --strict --json

# R3 Audio: VO (`higgsfield voices list`) and score
python3 scripts/hf_guard.py run --campaign campaigns/<slug> \
  --shot vo01 --kind audio --round R3 --round-cap 50 \
  --model text2speech_v2 --out campaigns/<slug>/media/audio/vo01-v1.wav -- \
  --variant elevenlabs --voice_id <voice_id> --voice_type preset \
  --prompt "Nord Ah-tel-yay. Built to carry real weight."

python3 scripts/hf_guard.py run --campaign campaigns/<slug> \
  --shot music01 --kind audio --round R3 --round-cap 50 \
  --model elevenlabs_music_v2_5 --out campaigns/<slug>/media/audio/music-v1.mp3 -- \
  --prompt "Sparse warm solo cello and felt piano, 15 seconds, no drums" --duration 15
```
