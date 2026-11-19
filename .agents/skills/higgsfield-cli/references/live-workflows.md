# Live Higgsfield CLI & `hf_guard.py` Workflow Patterns

Always inspect live CLI schemas (`higgsfield model get` / `workflow get`) before finalizing `shotlist.json`, and run `python3 scripts/hf_guard.py --help` (and subcommand `--help`) to confirm local guard flags. Every paid campaign job and tracked asset upload MUST run through `scripts/hf_guard.py` with mandatory `--round` and mandatory `--round-cap` rather than raw `higgsfield generate create`, `generate workflow`, `upload create`, `product-photoshoot create`, or `soul-id create`.

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

# Free credit estimation for the upcoming round's Dailies Cost Ticket (avoid private local paths here)
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

## 2. Reference Upload & Two-Layer Budget Guard (`hf_guard.py`)

Upload each clean source brand/product reference (and any Director-selected Lookbook winner needed as an anchor) through `hf_guard.py upload` so the `upload_id` is logged in `receipts.jsonl`, then record it in `shotlist.json`:

```bash
python3 scripts/hf_guard.py upload \
  --campaign campaigns/<slug> \
  --file campaigns/<slug>/media/references/product_hero.jpg \
  --ref-id ref_product_hero \
  --round R2
```

Check remaining credit headroom and gate every paid call via `scripts/hf_guard.py`:
- **Two-layer budget control (both mandatory):** every `hf_guard.py preflight` and `hf_guard.py run` call MUST pass BOTH `--round <R2|R3|R4|R4A|R4B|R5>` (`R4A` for Motion Pilot, `R4B` for Batch Draft Motion) AND `--round-cap <cumulative_cap>` (the cumulative Director-approved ceiling for that round). For a surgical Director-approved re-roll inside an already-started round, increment `--version <N>` and set `--round-cap <round_spent + delta_cap>` (verified from `make budget-status`). `hf_guard.py` checks BOTH `Campaign cap` in `campaigns/<slug>/brief.md` (`status: active`) AND `--round-cap`.
- **`asset_locked` immutability protection (no `--force-unlock` CLI flag):** `hf_guard.py` reads `shotlist.json` and refuses with `asset_locked` whenever the target Lookbook entity, still, video shot, or audio stem has `status: "LOCKED"`. There is **no `--force-unlock` CLI flag**—unlocking happens strictly via the Root Producer editing `shotlist.json` (`"LOCKED"` → `"ITERATING"`) after explicit Director instruction.
- **Parameter boundary rule:** pass `--round R2|R3|R4|R4A|R4B|R5`, `--round-cap <cumulative_cap>`, `--kind lookbook|still|video|audio|analysis`, `--model <id>`, `--workflow` (for workflow endpoints), optional `--variant A|B|C` (for `R2` Lookbook variants), optional `--version <N>` (for surgical re-rolls), and optional `--command product-photoshoot|soul-id` BEFORE `--`. Pass ONLY model/workflow parameters after `--`—never duplicate `generate create`, `generate workflow`, `product-photoshoot create`, `soul-id create`, `--wait`, `--wait-timeout`, or `--json` after `--` because `hf_guard.py` injects them automatically.

```bash
# Check spent vs remaining Campaign cap and per-round spend (also: make budget-status CAMPAIGN=<slug>)
python3 scripts/hf_guard.py status --campaign campaigns/<slug>

# Dry-run Campaign cap, --round-cap, asset_locked, retry-cap, and cost check without spending credits
python3 scripts/hf_guard.py preflight \
  --campaign campaigns/<slug> \
  --shot s01 \
  --kind video \
  --round R4A \
  --round-cap 40 \
  --model cinematic_studio_video_4_0 \
  --workflow \
  -- --mode omni_reference --duration 5 --resolution 480p

# Execute a guarded R4A Motion Pilot generation (checks both caps, asset_locked, retries, timeout list, locks receipts.jsonl)
python3 scripts/hf_guard.py run \
  --campaign campaigns/<slug> \
  --shot s01 \
  --kind video \
  --round R4A \
  --round-cap 40 \
  --model cinematic_studio_video_4_0 \
  --workflow \
  --prompt-file campaigns/<slug>/prompts/s01_video_v1.txt \
  --out campaigns/<slug>/media/shots/s01-r4a-v1.mp4 \
  --wait-timeout 20m \
  -- --mode omni_reference \
     --start-image <s01_still_upload_id> \
     --image-references <hero_product_upload_id> \
     --resolution 480p \
     --aspect_ratio 16:9 \
     --duration 5 \
     --generate_audio true

# Surgical Director-approved re-roll (after Root Producer sets s02.still status -> ITERATING in shotlist.json)
# Pass incremented --version 2 and cumulative --round-cap <round_spent + delta_cap>
python3 scripts/hf_guard.py run \
  --campaign campaigns/<slug> \
  --shot s02 \
  --kind still \
  --round R3 \
  --round-cap 65 \
  --version 2 \
  --model gpt_image_2_6 \
  --prompt-file campaigns/<slug>/prompts/s02_still_v2.txt \
  --out campaigns/<slug>/media/stills/s02-v2.png \
  -- --image-references <hero_product_upload_id> \
     --aspect_ratio 16:9
```

## 3. R2 Lookbook Variants, Product Photoshoot & Soul ID (`R2` → `R3`)

Use `R2` (`--kind lookbook --round R2 --round-cap <approved_r2_cap>`) to lock world entities (hero product styling, isolated cast portrait, key lighting/environment mood) via contrasting `A / B / C` options before generating full `R3` `s01..sN` keyframe stills.

**Per-variant rule (never `--count 3` with one `--out`):** Never pass `--count 3` with a single `--out` path—`hf_guard.py` saves one file per call, silently discarding variants B and C. Always issue separate guarded calls with `--count 1`, distinct `--variant A` / `B` / `C`, distinct `--out` paths (`...-v1-A.png`, `-B.png`, `-C.png`), contrasting art direction in `--prompt`, and the shared cumulative `--round-cap <approved_r2_cap>`:

```bash
# Variant A — Architectural Morning (distinct --variant A, --count 1, distinct --out)
python3 scripts/hf_guard.py run \
  --campaign campaigns/<slug> \
  --shot lb_product_hero \
  --kind lookbook \
  --round R2 \
  --round-cap 60 \
  --variant A \
  --command product-photoshoot \
  --model gpt_image_2 \
  --out campaigns/<slug>/media/lookbook/lb_product_hero-v1-A.png \
  -- --mode lifestyle_scene \
     --image <hero_product_upload_id> \
     --aspect_ratio 16:9 \
     --count 1 \
     --prompt "Medium three-quarter low angle on pale honed limestone bench in low raking morning sun (~4600K) from screen-left, matte leather pores, clean architectural colonnade depth"

# Variant B — Diffused Nordic Overcast (distinct --variant B, --count 1, distinct --out)
python3 scripts/hf_guard.py run \
  --campaign campaigns/<slug> \
  --shot lb_product_hero \
  --kind lookbook \
  --round R2 \
  --round-cap 60 \
  --variant B \
  --command product-photoshoot \
  --model gpt_image_2 \
  --out campaigns/<slug>/media/lookbook/lb_product_hero-v1-B.png \
  -- --mode product_shot \
     --image <hero_product_upload_id> \
     --aspect_ratio 16:9 \
     --count 1 \
     --prompt "Tight tactile close-up centered on brushed antique brass clasp and saddle stitching under broad soft overhead skylight (~5800K) against raw pale plaster wall, flat matte finish"

# Variant C — Warm Interior Practical (distinct --variant C, --count 1, distinct --out)
python3 scripts/hf_guard.py run \
  --campaign campaigns/<slug> \
  --shot lb_product_hero \
  --kind lookbook \
  --round R2 \
  --round-cap 60 \
  --variant C \
  --command product-photoshoot \
  --model gpt_image_2 \
  --out campaigns/<slug>/media/lookbook/lb_product_hero-v1-C.png \
  -- --mode lifestyle_scene \
     --image <hero_product_upload_id> \
     --aspect_ratio 16:9 \
     --count 1 \
     --prompt "Wide establishing dark oak bench silhouette lit by warm directional interior window and practical (~3600K) with deep espresso shadow falloff and warm brushed brass sheen"

# Train a Soul-2 character reference in R2 (--command soul-id with --model soul_2; 8-10 uniform shots recommended)
python3 scripts/hf_guard.py run \
  --campaign campaigns/<slug> \
  --shot lb_talent_soul \
  --kind lookbook \
  --round R2 \
  --round-cap 60 \
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

# Generate R3 shot still anchored to approved Soul 2.0 ID (do not combine style_id with image_references)
python3 scripts/hf_guard.py run \
  --campaign campaigns/<slug> \
  --shot s01 \
  --kind still \
  --round R3 \
  --round-cap 50 \
  --model text2image_soul_v2 \
  --prompt-file campaigns/<slug>/prompts/s01_still_v1.txt \
  --out campaigns/<slug>/media/stills/s01-v1.png \
  -- --custom_reference_id <soul_id> \
     --aspect_ratio 16:9 \
     --quality 2k
```

## 4. Cinema Studio 4.0 (`cinematic_studio_video_4_0` Workflow: `R4A` → `R4B` → `R5`)

Live schema highlights:
- `mode`: `t2v` | `omni_reference` | `video_edit` | `video_extension`
- `resolution`: `480p` | `720p` | `1080p` (no `4k`)
- Limits: `<= 30` images (counting `start_image` and `end_image`), `<= 50` total reference media items; `start_image` and `end_image` are allowed ONLY in `omni_reference`.
- `extension_mode` (`forward` | `backward`) is required ONLY for `video_extension`.

```bash
# R4A Motion Pilot: 480p omni_reference hero/risk shot inside R4A --round-cap
python3 scripts/hf_guard.py run \
  --campaign campaigns/<slug> \
  --shot s01 \
  --kind video \
  --round R4A \
  --round-cap 40 \
  --model cinematic_studio_video_4_0 \
  --workflow \
  --prompt-file campaigns/<slug>/prompts/s01_video_v1.txt \
  --out campaigns/<slug>/media/shots/s01-r4a-v1.mp4 \
  --wait-timeout 20m \
  -- --mode omni_reference \
     --start-image <s01_still_upload_id> \
     --image-references <hero_product_upload_id> \
     --resolution 480p \
     --aspect_ratio 16:9 \
     --duration 5 \
     --generate_audio true

# R4B Batch Draft Motion: forward extension from an approved clip inside R4B --round-cap
python3 scripts/hf_guard.py run \
  --campaign campaigns/<slug> \
  --shot s02 \
  --kind video \
  --round R4B \
  --round-cap 120 \
  --model cinematic_studio_video_4_0 \
  --workflow \
  --prompt-file campaigns/<slug>/prompts/s02_video_v1.txt \
  --out campaigns/<slug>/media/shots/s02-r4b-v1.mp4 \
  --wait-timeout 20m \
  -- --mode video_extension \
     --extension_mode forward \
     --video-references <s01_job_or_upload_id> \
     --image-references <hero_product_upload_id> \
     --resolution 480p \
     --duration 5

# R5 Final Master: 1080p upgrade on Director-approved R4 recipe inside R5 --round-cap
python3 scripts/hf_guard.py run \
  --campaign campaigns/<slug> \
  --shot s01 \
  --kind video \
  --round R5 \
  --round-cap 260 \
  --model cinematic_studio_video_4_0 \
  --workflow \
  --prompt-file campaigns/<slug>/prompts/s01_video_v1.txt \
  --out campaigns/<slug>/media/shots/s01-r5-v1.mp4 \
  --wait-timeout 20m \
  -- --mode omni_reference \
     --start-image <s01_still_upload_id> \
     --image-references <hero_product_upload_id> \
     --resolution 1080p \
     --aspect_ratio 16:9 \
     --duration 5 \
     --generate_audio true
```

### Reusing Opaque Web Cinema Studio 4.0 Preset UUIDs

`Emotion Wheel`, `AI Cast`, and interactive visual lighting placement are Web-only at `https://higgsfield.ai/cinema-studio`. For `camera_model_id`, `camera_lens_id`, `camera_aperture_id`, `genre_id`, `era_id`, `pacing_id`, and `light_id` (which have no CLI `preset list` endpoint):

1. Leave them omitted (`Auto`) and describe optics/lighting in the prompt, OR
2. Configure one reference job in `https://higgsfield.ai/cinema-studio`, inspect it with `higgsfield generate get <job_id> --json`, and save the UUIDs into `docs/cinema-presets.json` following [`docs/cinema-presets.example.json`](../../../../docs/cinema-presets.example.json).

## 5. Seedance 2.5 (`seedance_2_5` Model: `R4A`/`R4B` Draft → `R5` Final)

Live schema highlights:
- `draft` (`true`/`false`) and `draft_job_id` are mutually exclusive.
- `resolution`: `480p` | `720p` | `1080p` | `4k`.
- Same `mode` and 30-image / 50-reference rules as Cinema Studio 4.0.

```bash
# R4A: Cheap draft pilot preview inside R4A --round-cap (use --round R4B for batch shots)
python3 scripts/hf_guard.py run \
  --campaign campaigns/<slug> \
  --shot s01 \
  --kind video \
  --round R4A \
  --round-cap 40 \
  --model seedance_2_5 \
  --prompt-file campaigns/<slug>/prompts/s01_video_v1.txt \
  --out campaigns/<slug>/media/shots/s01-r4a-v1.mp4 \
  --wait-timeout 20m \
  -- --mode omni_reference \
     --draft true \
     --start-image <s01_still_upload_id> \
     --image-references <hero_product_upload_id> \
     --resolution 720p \
     --aspect_ratio 16:9 \
     --duration 5

# R5: Escalate Director-approved R4 draft to 1080p or 4k inside R5 --round-cap (omit --draft)
python3 scripts/hf_guard.py run \
  --campaign campaigns/<slug> \
  --shot s01 \
  --kind video \
  --round R5 \
  --round-cap 260 \
  --model seedance_2_5 \
  --out campaigns/<slug>/media/shots/s01-r5-v1.mp4 \
  --wait-timeout 20m \
  -- --mode omni_reference \
     --draft_job_id <approved_r4_job_id> \
     --resolution 1080p
```

## 6. Marketing Studio (`marketing_studio_video` Workflow)

```bash
# Marketing Studio storyboard/product ad video (R4B batch draft cut inside R4B --round-cap)
python3 scripts/hf_guard.py run \
  --campaign campaigns/<slug> \
  --shot s01 \
  --kind video \
  --round R4B \
  --round-cap 120 \
  --model marketing_studio_video \
  --workflow \
  --prompt-file campaigns/<slug>/prompts/ugc_spot_v1.txt \
  --out campaigns/<slug>/media/shots/s01-r4b-v1.mp4 \
  --wait-timeout 20m \
  -- --specific_mode from_storyboard \
     --resolution 720p \
     --duration 15
```

## 7. Audio Models (VO, Score, SFX — `R3` Animatic or `R4A`/`R4B` Draft Cut)

Always verify live voice IDs with `higgsfield voices list --json` first (`preset` for built-in voices, `element` for cloned voices). Pass `--round R3` when cutting VO/score early for an `R3` still animatic, `--round R4A` for pilot VO/SFX, or `--round R4B` for full batch Draft Cut audio—always with mandatory `--round-cap <cumulative_cap>`:

```bash
# Eleven v4 voiceover / dialogue (live param: dialogue array)
python3 scripts/hf_guard.py run \
  --campaign campaigns/<slug> \
  --shot vo01 \
  --kind audio \
  --round R4A \
  --round-cap 40 \
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
  --round R4A \
  --round-cap 40 \
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
  --round R4B \
  --round-cap 120 \
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
  --round R4B \
  --round-cap 120 \
  --model sonilo_music \
  --out campaigns/<slug>/media/audio/music01.wav \
  -- --duration 15 \
     --prompt "Minimalist acoustic underscore with gentle cello sustain"

# Mirelo Text to Audio (diegetic SFX / foley)
python3 scripts/hf_guard.py run \
  --campaign campaigns/<slug> \
  --shot sfx01 \
  --kind audio \
  --round R4B \
  --round-cap 120 \
  --model mirelo_text_to_audio \
  --out campaigns/<slug>/media/audio/sfx01.wav \
  -- --duration 5 \
     --prompt "Crisp solid brass buckle click followed by soft thick vegetable-tanned leather flex in a quiet stone hall"
```

## 8. Virality Predictor (`brain_activity` Advisory Read)

`brain_activity` is a `text` model taking a required `medias` array (uploaded cut). Treat its output as an optional advisory pacing signal alongside deterministic `qa_media.py` probes, internal Visual Critic filtering, and human Director Dailies—never as an autonomous pass/fail gate overriding `brief.md` or `taste-log.md`.

```bash
# Upload assembled R4B rough cut via hf_guard.py upload, then run brain_activity under hf_guard.py run
UPLOAD_ID=$(python3 scripts/hf_guard.py upload \
  --campaign campaigns/<slug> \
  --file campaigns/<slug>/media/exports/draft_cut.mp4 \
  --ref-id draft_cut \
  --round R4B \
  | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d.get("upload_id") or d.get("id",""))')

python3 scripts/hf_guard.py run \
  --campaign campaigns/<slug> \
  --shot qa_virality \
  --kind analysis \
  --round R4B \
  --round-cap 120 \
  --model brain_activity \
  -- --medias "[\"$UPLOAD_ID\"]"
```
