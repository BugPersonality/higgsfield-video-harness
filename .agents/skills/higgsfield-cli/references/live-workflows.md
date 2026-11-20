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
2. **`generate cost` traps (auto-upload, workflow `cost_params` & unquotable
   endpoints):** before Director approves uploading private media (`R1`), pass
   only cost-affecting flags or already-uploaded / placeholder UUIDs—never local
   paths under `media/references/`, which `generate cost` auto-uploads.
   `generate cost workflow <name>` accepts only `cost_params` from
   `workflow get <name> --json` (`hf_guard.py` filters these automatically).
   Verify live quoting before committing to `soul-id` (no `soul-id cost`
   command) or `marketing_studio_video --specific_mode from_storyboard` (whose
   live `cost_params` omit `storyboard_id` while validation requires it).
3. **All workflow/model parameter flags use `snake_case`:** pass `--start_image`,
   `--end_image`, `--image_references`, `--video_references`, `--audio_references`,
   `--aspect_ratio`, `--extension_mode`, `--draft_job_id`, `--custom_reference_id`,
   `--voice_id`, `--voice_type`, `--specific_mode`.
4. **Guard boundary & per-variant `product-photoshoot`:** pass `hf_guard.py`
   flags before `--` and only model/workflow params after `--` (never duplicate
   `generate create`, `--wait`, or `--json`). For `product-photoshoot`, run
   separate `--count 1` calls per `--variant A|B|C` with distinct `--out` paths
   so every variant is saved.
5. **Spatial, outpaint, relight, decomposition & prop-rescue CEL traps:**
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
   - `wan3_0` / `wan3_0_prime` forbid combining `--start_image`/`--end_image` with
     `--image_references`; `flux_3_video` forbids mixing `--video_references` with
     any image inputs and caps total images at `10`.
   - `kling_o3_image_reference` requires `--multi_prompt` if and only if
     `--multi_shots true` (`std` `6.25 cr.` / `pro` `10 cr.` for 5s).
   - `hf_mult_replace_object` (`480p`–`1080p`) and `hf_mult_replace_object_flash`
     (Genjutsu Lite, `720p`–`4k`) require **exactly 1** `--video_references`
     and **`>= 1`** `--image_references`.
   - Creating Cinema Studio Elements or `kling_element_ids` is Web-UI only; CLI
     accepts pre-existing `kling_element_ids` or uploaded `--image_references` UUIDs.

## Minimal Guarded Recipes

```bash
# Free read-only schema & cost quote (0 cr.; never pass private local file paths)
higgsfield workflow get cinematic_studio_video_4_0 --json
higgsfield generate cost workflow cinematic_studio_video_4_0 --mode omni_reference --resolution 480p --duration 5 --json

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

# R2 Location / Angle / Relight / Outpaint / Slice / Decompose recipes (Asset Bible expansion)
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

# R3 Keyframe still (surgical v2 re-roll uses cumulative round_spent + delta_cap)
python3 scripts/hf_guard.py run --campaign campaigns/<slug> \
  --shot s02 --kind still --round R3 --round-cap 50 --version 2 \
  --model gpt_image_2_6 --prompt-file campaigns/<slug>/prompts/s02_still_v2.txt \
  --out campaigns/<slug>/media/stills/s02-v2.png -- \
  --aspect_ratio 16:9 --image_references <ref_uuid> --image_references <lb_uuid>

# R4A Motion Pilot -> R4B Batch Draft -> R5 1080p Final (Cinema Studio 4.0)
python3 scripts/hf_guard.py run --campaign campaigns/<slug> \
  --shot s02 --kind video --round R4A --round-cap 20 --version 1 \
  --model cinematic_studio_video_4_0 --workflow \
  --prompt-file campaigns/<slug>/prompts/s02_video_v1.txt \
  --out campaigns/<slug>/media/shots/s02-draft-v1.mp4 -- \
  --mode omni_reference --resolution 480p --duration 5 --aspect_ratio 16:9 \
  --start_image <s02_still_uuid> --image_references <ref_uuid>

# R4B -> R5 Seedance draft (in R5, swap --draft true for --draft_job_id <job_id> --resolution 1080p)
python3 scripts/hf_guard.py run --campaign campaigns/<slug> \
  --shot s01 --kind video --round R4B --round-cap 45 --model seedance_2_5 \
  --prompt-file campaigns/<slug>/prompts/s01_video_v1.txt \
  --out campaigns/<slug>/media/shots/s01-draft-v1.mp4 -- \
  --mode omni_reference --draft true --duration 5 --aspect_ratio 16:9 \
  --start_image <s01_still_uuid>

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
