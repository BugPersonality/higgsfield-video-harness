---
name: higgsfield-cli
description: "Live Higgsfield CLI routing. Use when inspecting model, workflow, voice, or preset schemas, selecting lookbook, still, video, or audio models, or running guarded jobs and uploads through hf_guard.py."
---

# Higgsfield CLI

**Live schema truth.** Query `higgsfield model get <id> --json`, `workflow get <id> --json`, `voices list`, `preset list`, `account status`, and `generate cost` before trusting any static catalog. Live CLI schemas and CEL rules own valid parameters, enums, and limits.

**Guarded spend & locks.** Route every paid job through `python3 scripts/hf_guard.py preflight` / `run` (with `--round {R2,R3,R4,R4A,R4B,R5}`, cumulative `--round-cap`, `--variant` for Lookbook, `--version` for surgical re-rolls), tracked uploads through `hf_guard.py upload --round <R>` (0 cr.), and budget checks through `hf_guard.py status` (see `hf_guard.py --help` and [Workflow](../../../docs/workflow.md#budget--lock-invariants)). Reserve direct CLI and MCP strictly for free read-only reads; see [live workflow gotchas](references/live-workflows.md) for non-obvious CLI traps and recipes.

**Lookbook, stills, and Soul identity (`R2`–`R3`).** Use `hf_guard.py run --command product-photoshoot --model gpt_image_2 --kind lookbook` for mode-enhanced brand shots (`product_shot`, `lifestyle_scene`, `closeup_product_with_person`, `hero_banner`, `ad_creative_pack`), issuing **separate `--count 1` calls per `--variant A|B|C` with distinct `--out` paths** so no variant is dropped. Use `higgsfield model list --image` (e.g., `gpt_image_2_6`) for worlds/keyframes, and `--command soul-id --model soul_2` for recurring character likenesses paired with `text2image_soul_v2`.

**Video, audio, and virality (`R3`–`R5`).** Select `cinematic_studio_video_4_0` (`--workflow`, `--mode omni_reference` for start/end frames, up to 30 images / 50 refs, `480p`/`720p` → `1080p`) for multi-reference cinematography; `seedance_2_5` when native `--draft true` → `--draft_job_id` escalation or `4k` matters; `marketing_studio_video` for UGC/storyboard ads. For audio, pair `higgsfield voices list` with `elevenlabs_v4`/`seed_audio` (VO), `elevenlabs_music_v2_5`/`sonilo_music` (score), and `mirelo_text_to_audio` (SFX). Use `brain_activity` (`--kind analysis`) only as an optional advisory pacing read.

**Web Cinema Studio 4.0 boundaries.** `Emotion Wheel`, `AI Cast`, and interactive light placement exist only in the Web UI (`https://higgsfield.ai/cinema-studio`). Opaque preset UUIDs (`camera_model_id`, `camera_lens_id`, `light_id`, etc.) have no CLI `preset list`: leave them unset (`Auto`) and describe optics/light in prose, or extract UUIDs from a web job via `higgsfield generate get <id> --json` into [`cinema-presets.example.json`](../../../docs/cinema-presets.example.json) shape.
