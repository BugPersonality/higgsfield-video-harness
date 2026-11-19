# Live Higgsfield CLI & `hf_guard.py` Workflow Patterns

Always inspect live CLI schemas (`higgsfield model get` / `workflow get`) before locking `shotlist.json`, and run `python3 scripts/hf_guard.py --help` (and subcommand `--help`) to confirm local guard options. Every paid campaign job and remote asset upload MUST run through `scripts/hf_guard.py` rather than raw `higgsfield generate create`, `generate workflow`, `upload create`, `product-photoshoot create`, or `soul-id create`.

## 1. Free Read-Only Introspection & Schema Checks

```bash
# Balance and active billing workspace
higgsfield account status --json
higgsfield workspace list --json

# Discover models, workflows, voices, uploads, and presets
higgsfield model list --video
higgsfield model list --image
higgsfield model list --audio
higgsfield workflow list
higgsfield voices list --json
higgsfield upload list --image --size 50 --json
higgsfield preset list soul-v2 --query exposure

# Inspect exact live JSON schemas & CEL validation rules
higgsfield workflow get cinematic_studio_video_4_0 --json
higgsfield model get seedance_2_5 --json
higgsfield workflow get marketing_studio_video --json
higgsfield model get text2image_soul_v2 --json
higgsfield model get elevenlabs_v4 --json
higgsfield model get elevenlabs_music_v2_5 --json
higgsfield model get seed_audio --json
higgsfield model get sonilo_music --json
higgsfield model get mirelo_text_to_audio --json
higgsfield model get brain_activity --json

# Free credit estimation (no job created; avoid passing private local paths here)
higgsfield generate cost workflow cinematic_studio_video_4_0 \
  --mode omni_reference --duration 5 --resolution 480p --json
higgsfield generate cost seedance_2_5 \
  --mode omni_reference --draft true --duration 5 --resolution 720p --json

# Inspect recent jobs or Soul training status (read-only)
higgsfield generate list --json
higgsfield generate get <job_id> --json
higgsfield soul-id list --json
higgsfield soul-id get <soul_id> --json
```

## 2. Reference Upload & Budget Guard (`hf_guard.py`)

Upload each clean brand or product reference through `hf_guard.py upload` so the `upload_id` is logged in `receipts.jsonl`, then record it in `shotlist.json`:

```bash
python3 scripts/hf_guard.py upload \
  --campaign campaigns/<slug> \
  --file campaigns/<slug>/media/references/product_hero.jpg \
  --ref-id ref_product_hero
```

Check remaining credit envelope and gate every paid call via `scripts/hf_guard.py`.
**Parameter boundary rule:** pass `--phase draft|final`, `--model <id>`, `--kind still|video|audio|analysis`, and `--workflow` (for workflow job types) to `hf_guard.py` BEFORE `--`. Pass ONLY model/workflow parameters after `--`—never duplicate `generate create`, `generate workflow`, `product-photoshoot create`, `soul-id create`, `--wait`, `--wait-timeout`, or `--json` after `--` because `hf_guard.py` injects them automatically.

```bash
# Check spent vs remaining Draft cap and Final cap (also: make budget-status CAMPAIGN=<slug>)
python3 scripts/hf_guard.py status --campaign campaigns/<slug>

# Dry-run budget, retry-cap, and cost-estimate check without spending credits
python3 scripts/hf_guard.py preflight \
  --campaign campaigns/<slug> \
  --shot s01 \
  --kind video \
  --phase draft \
  --model cinematic_studio_video_4_0 \
  --workflow \
  -- --mode omni_reference --duration 5 --resolution 480p

# Execute a guarded paid generation (checks cap, retries, timeout list, locks receipts.jsonl)
python3 scripts/hf_guard.py run \
  --campaign campaigns/<slug> \
  --shot s01 \
  --kind video \
  --phase draft \
  --model cinematic_studio_video_4_0 \
  --workflow \
  --prompt-file campaigns/<slug>/prompts/s01_video_v1.txt \
  --out campaigns/<slug>/media/shots/s01-draft-v1.mp4 \
  --wait-timeout 20m \
  -- --mode omni_reference \
     --start-image <still_upload_id> \
     --image-references <hero_product_upload_id> \
     --resolution 480p \
     --aspect_ratio 16:9 \
     --duration 5 \
     --generate_audio true
```

## 3. Cinema Studio 4.0 (`cinematic_studio_video_4_0` Workflow)

Live schema highlights:
- `mode`: `t2v` | `omni_reference` | `video_edit` | `video_extension`
- `resolution`: `480p` | `720p` | `1080p` (no `4k`)
- Limits: `<= 30` images (counting `start_image` and `end_image`), `<= 50` total reference media items; `start_image` and `end_image` are allowed ONLY in `omni_reference`.
- `extension_mode` (`forward` | `backward`) is required ONLY for `video_extension`.

```bash
# Draft 480p omni_reference shot
python3 scripts/hf_guard.py run \
  --campaign campaigns/<slug> \
  --shot s01 \
  --kind video \
  --phase draft \
  --model cinematic_studio_video_4_0 \
  --workflow \
  --prompt-file campaigns/<slug>/prompts/s01_video_v1.txt \
  --out campaigns/<slug>/media/shots/s01-draft-v1.mp4 \
  --wait-timeout 20m \
  -- --mode omni_reference \
     --start-image <still_upload_id> \
     --image-references <hero_product_upload_id> \
     --resolution 480p \
     --aspect_ratio 16:9 \
     --duration 5 \
     --generate_audio true

# Extend an approved clip forward with video_extension
python3 scripts/hf_guard.py run \
  --campaign campaigns/<slug> \
  --shot s02 \
  --kind video \
  --phase draft \
  --model cinematic_studio_video_4_0 \
  --workflow \
  --prompt-file campaigns/<slug>/prompts/s02_video_v1.txt \
  --out campaigns/<slug>/media/shots/s02-draft-v1.mp4 \
  --wait-timeout 20m \
  -- --mode video_extension \
     --extension_mode forward \
     --video-references <s01_job_or_upload_id> \
     --image-references <hero_product_upload_id> \
     --resolution 480p \
     --duration 5
```

### Reusing Opaque Web Cinema Studio Preset UUIDs

`Emotion Wheel`, `AI Cast`, and interactive lighting placement are Web-only. For `camera_model_id`, `camera_lens_id`, `camera_aperture_id`, `genre_id`, `era_id`, `pacing_id`, and `light_id` (which have no CLI `preset list` endpoint):

1. Leave them omitted (`Auto`) and describe optics/lighting in the prompt, OR
2. Configure one reference job in `https://higgsfield.ai/cinema-studio`, inspect it with `higgsfield generate get <job_id> --json`, and save the UUIDs into `docs/cinema-presets.json` following [`docs/cinema-presets.example.json`](../../../../docs/cinema-presets.example.json).

## 4. Seedance 2.5 (`seedance_2_5` Model: Draft → Final)

Live schema highlights:
- `draft` (`true`/`false`) and `draft_job_id` are mutually exclusive.
- `resolution`: `480p` | `720p` | `1080p` | `4k`.
- Same `mode` and 30-image / 50-reference rules as Cinema Studio 4.0.

```bash
# Step 1: Cheap draft preview inside Draft cap
python3 scripts/hf_guard.py run \
  --campaign campaigns/<slug> \
  --shot s01 \
  --kind video \
  --phase draft \
  --model seedance_2_5 \
  --prompt-file campaigns/<slug>/prompts/s01_video_v1.txt \
  --out campaigns/<slug>/media/shots/s01-draft-v1.mp4 \
  --wait-timeout 20m \
  -- --mode omni_reference \
     --draft true \
     --start-image <still_upload_id> \
     --image-references <hero_product_upload_id> \
     --resolution 720p \
     --aspect_ratio 16:9 \
     --duration 5

# Step 2: Escalate approved draft to 1080p or 4k inside Final cap (omit --draft)
python3 scripts/hf_guard.py run \
  --campaign campaigns/<slug> \
  --shot s01 \
  --kind video \
  --phase final \
  --model seedance_2_5 \
  --out campaigns/<slug>/media/shots/s01-final-v1.mp4 \
  --wait-timeout 20m \
  -- --mode omni_reference \
     --draft_job_id <approved_draft_job_id> \
     --resolution 1080p
```

## 5. Marketing Studio, Product Photoshoot, and Soul ID

```bash
# Marketing Studio storyboard/product ad video (workflow)
python3 scripts/hf_guard.py run \
  --campaign campaigns/<slug> \
  --shot s01 \
  --kind video \
  --phase draft \
  --model marketing_studio_video \
  --workflow \
  --prompt-file campaigns/<slug>/prompts/ugc_spot_v1.txt \
  --out campaigns/<slug>/media/shots/s01-draft-v1.mp4 \
  --wait-timeout 20m \
  -- --specific_mode from_storyboard \
     --resolution 720p \
     --duration 15

# Brand product photoshoot still (--command product-photoshoot with --model gpt_image_2)
python3 scripts/hf_guard.py run \
  --campaign campaigns/<slug> \
  --shot s01 \
  --kind still \
  --phase draft \
  --command product-photoshoot \
  --model gpt_image_2 \
  --out campaigns/<slug>/media/stills/s01-v1.png \
  -- --mode lifestyle_scene \
     --image <hero_product_upload_id> \
     --aspect_ratio 16:9 \
     --count 2 \
     --prompt "Morning limestone bench in soft architectural daylight"

# Train a Soul-2 character reference (--command soul-id with --model soul_2; 8-10 uniform shots recommended)
python3 scripts/hf_guard.py run \
  --campaign campaigns/<slug> \
  --shot talent_soul \
  --kind still \
  --phase draft \
  --command soul-id \
  --model soul_2 \
  -- --name TalentName \
     --soul-2 \
     --image <ref01_upload_id> --image <ref02_upload_id> \
     --image <ref03_upload_id> --image <ref04_upload_id> \
     --image <ref05_upload_id> --image <ref06_upload_id> \
     --image <ref07_upload_id> --image <ref08_upload_id>

# Poll Soul training status (free read-only)
higgsfield soul-id wait <soul_id> --json

# Generate character still with Soul 2.0 (do not combine style_id with image_references)
python3 scripts/hf_guard.py run \
  --campaign campaigns/<slug> \
  --shot s01 \
  --kind still \
  --phase draft \
  --model text2image_soul_v2 \
  --prompt-file campaigns/<slug>/prompts/s01_still_v1.txt \
  --out campaigns/<slug>/media/stills/s01-v1.png \
  -- --custom_reference_id <soul_id> \
     --aspect_ratio 16:9 \
     --quality 2k
```

## 6. Audio Models (VO, Score, SFX)

Always verify live voice IDs with `higgsfield voices list --json` first (`preset` for built-in voices, `element` for cloned voices).

```bash
# Eleven v4 voiceover / dialogue (live param: dialogue array)
python3 scripts/hf_guard.py run \
  --campaign campaigns/<slug> \
  --shot vo01 \
  --kind audio \
  --phase draft \
  --model elevenlabs_v4 \
  --out campaigns/<slug>/media/audio/vo01.wav \
  -- --dialogue '[{"text":"Nord Ah-tel-yay. Built for unhurried mornings.","voice_id":"<voice_id>"}]' \
     --stability 0.55 \
     --similarity_boost 0.75

# Seed Audio 1.0 voiceover (voice_id + voice_type must be paired; no image_references with voice)
python3 scripts/hf_guard.py run \
  --campaign campaigns/<slug> \
  --shot vo01 \
  --kind audio \
  --phase draft \
  --model seed_audio \
  --out campaigns/<slug>/media/audio/vo01.wav \
  -- --voice_id <voice_id> \
     --voice_type preset \
     --format wav \
     --sample_rate 48000 \
     --prompt "Nord Ah-tel-yay. Built for unhurried mornings."

# ElevenLabs Music v2.5 instrumental score (do not pass lyrics when force_instrumental is true)
python3 scripts/hf_guard.py run \
  --campaign campaigns/<slug> \
  --shot music01 \
  --kind audio \
  --phase draft \
  --model elevenlabs_music_v2_5 \
  --out campaigns/<slug>/media/audio/music01.wav \
  -- --duration 15 \
     --force_instrumental true \
     --prompt "Sparse intimate solo cello and felt upright piano, 68 BPM, warm Nordic daylight, clean decay"

# Sonilo Music score alternative
python3 scripts/hf_guard.py run \
  --campaign campaigns/<slug> \
  --shot music01 \
  --kind audio \
  --phase draft \
  --model sonilo_music \
  --out campaigns/<slug>/media/audio/music01.wav \
  -- --duration 15 \
     --prompt "Minimalist acoustic underscore with gentle cello sustain"

# Mirelo Text to Audio (diegetic SFX / foley)
python3 scripts/hf_guard.py run \
  --campaign campaigns/<slug> \
  --shot sfx01 \
  --kind audio \
  --phase draft \
  --model mirelo_text_to_audio \
  --out campaigns/<slug>/media/audio/sfx01.wav \
  -- --duration 5 \
     --prompt "Crisp solid brass buckle click followed by soft thick vegetable-tanned leather flex in a quiet stone hall"
```

## 7. Virality Predictor (`brain_activity` Advisory Read)

`brain_activity` is a `text` model taking a required `medias` array (uploaded rough cut). Treat its output as advisory Layer 3 QA signal alongside deterministic probes and Visual Critic review—never as an autonomous pass/fail gate overriding `intent.md`.

```bash
# Upload assembled rough cut via hf_guard.py upload, then run brain_activity under hf_guard.py run
UPLOAD_ID=$(python3 scripts/hf_guard.py upload \
  --campaign campaigns/<slug> \
  --file campaigns/<slug>/media/exports/draft_cut.mp4 \
  --ref-id draft_cut \
  | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d.get("upload_id") or d.get("id",""))')

python3 scripts/hf_guard.py run \
  --campaign campaigns/<slug> \
  --shot qa_virality \
  --kind analysis \
  --phase draft \
  --model brain_activity \
  -- --medias "[\"$UPLOAD_ID\"]"
```
