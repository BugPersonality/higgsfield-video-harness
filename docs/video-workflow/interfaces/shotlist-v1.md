# Shotlist Schema V1

`campaigns/<slug>/shotlist.json` is the executable production manifest binding
the creative treatment to live Higgsfield CLI schemas, uploaded reference UUIDs,
prompt files, draft/final parameter sets, credit estimates, and selected takes.
Authored in [Production Design](../phases/production-design.md), validated by
`make ledger-check CAMPAIGN=<slug>` (`scripts/check-ledger.py`), and updated
serially by the Root Orchestrator during [Production](../phases/production.md).

## JSON Structure

```json
{
  "schema_version": 1,
  "campaign": "<slug>",
  "aspect_ratio": "16:9",
  "target_duration_s": 15,
  "fps_target": 24,
  "autonomy_mode": "autonomous-draft",
  "continuity_lock": {
    "product": "Matte Warm Saddle Tan leather (#8B5A2B), satin-brushed brass square clasps, blind-debossed NORD ATELIER centered 24 mm below front handle gusset",
    "lighting_and_palette": "Screen-left low morning sunlight (~4600K) against cool limestone sky fill (~6200K); matte tones, zero glossy studio glare",
    "space_cast_axis": "Single sunlit limestone railway concourse; traveler in matte charcoal wool coat and heather-grey cuff; right hand closes clasp; consistent screen-left-to-right 180-degree axis"
  },
  "references": [
    {
      "id": "ref_product_front",
      "kind": "product",
      "local_path": "media/references/product_front.jpg",
      "upload_id": null
    }
  ],
  "shots": [
    {
      "id": "s01",
      "title": "Opening macro hero beat",
      "duration_s": 5,
      "test_take_check": {
        "risk": "Hand-to-clasp grip anatomy or illegible blind-debossed wordmark during latch closure",
        "pass_check": "Five natural fingers close the square brass clasp smoothly without metal morphing or garbled lettering across panels 1-6"
      },
      "still": {
        "model": "gpt_image_2_6",
        "prompt_file": "prompts/s01_still_v1.txt",
        "references": ["ref_product_front"],
        "estimated_credits": 10,
        "selected_take": null,
        "selected_job_id": null
      },
      "video": {
        "model": "cinematic_studio_video_4_0",
        "is_workflow": true,
        "mode": "omni_reference",
        "prompt_file": "prompts/s01_video_v1.txt",
        "start_image_from": "s01.still",
        "end_image_from": null,
        "image_references": ["ref_product_front"],
        "draft_params": {
          "resolution": "480p",
          "duration": 5,
          "aspect_ratio": "16:9"
        },
        "final_params": {
          "resolution": "1080p",
          "duration": 5,
          "aspect_ratio": "16:9"
        },
        "estimated_draft_credits": 15,
        "estimated_final_credits": 80,
        "selected_take": null,
        "selected_job_id": null
      }
    }
  ],
  "audio": {
    "music": {
      "enabled": true,
      "model": "elevenlabs_music_v2_5",
      "duration_s": 15,
      "prompt": "Sparse acoustic chamber score...",
      "estimated_credits": 10,
      "selected_file": null
    },
    "voiceover": {
      "enabled": false,
      "model": null,
      "voice_id": null,
      "voice_type": null,
      "estimated_credits": 0,
      "tracks": []
    }
  }
}
```

## Field Reference

### Top-Level Fields

| Field | Type | Rule |
| --- | --- | --- |
| `schema_version` | integer | Must be `1` |
| `campaign` | string | Matches the campaign directory slug |
| `aspect_ratio` | string | Live schema-verified ratio (for example `"16:9"`, `"9:16"`, `"1:1"`) matching `intent.md` |
| `target_duration_s` | number | Target runtime in seconds; sum of `shots[].duration_s` must match within edit tolerance |
| `fps_target` | integer | Locked delivery frame rate (`24`, `25`, or `30`) enforced by `scripts/assemble.sh` and `scripts/qa_media.py` |
| `autonomy_mode` | string | Must match `intent.md` (`"autonomous-draft"` or `"checkpointed"`) |
| `continuity_lock` | object *(optional)* | Cross-shot visual invariants inherited verbatim from `storyboard.md` / `style-bible.md`: `product`, `lighting_and_palette`, and `space_cast_axis` |
| `references` | array | Reference asset table (may be empty if no reference assets are used) |
| `shots` | array | Non-empty ordered list of shot objects (`s01`, `s02`, ...) |
| `audio` | object | Required `music` and `voiceover` sub-objects |

### Reference Entries (`references[]`)

- `id`: unique snake_case identifier (for example `ref_bag_front`, `ref_actor_soul`).
- `kind`: semantic role (`product`, `product_detail`, `product_worn`, `character`, `environment`, `style`, `soul_id`).
- `local_path`: path relative to `campaigns/<slug>/` (under `media/references/`).
- `upload_id`: `null` before Wave 1; populated by the Root Orchestrator with the Higgsfield upload UUID or Soul ID once uploaded via `python3 scripts/hf_guard.py upload --campaign <dir> --file <path> --ref-id <id>`.

### Shot Entries (`shots[]`)

- `id`: stable zero-padded shot key (`s01`, `s02`, ...), matching `prompts/sNN_*`, `media/stills/sNN-*`, `media/shots/sNN-*`, and `qc/sNN-*`.
- `title`: concise beat title aligned with `treatment.md` (and `storyboard.md` when present).
- `duration_s`: positive duration in seconds supported by the chosen video model's live `higgsfield model get` schema.
- `test_take_check` (object or `null`, optional): carried from `storyboard.md`'s **Test-take check** exclusively for shots with execution risk (grip, physics, legible text, reflections, tight comic timing, multi-subject blocking):
  - `risk`: exact failure mode to falsify before batch rendering;
  - `pass_check`: observable visual condition that proves the trial take passed.
  Shots with `test_take_check != null` are prioritized in Wave 2 (Risk-First Pilot) and explicitly verified by `reviewer-agent` Visual Critic (`view_image`). Routine shots omit the field or set it to `null`.
- `still` (object or `null` for pure text-to-video shots):
  - `model`: live Higgsfield image model ID (verified via `higgsfield model list --json`).
  - `prompt_file`: relative path to text prompt file (for example `prompts/s01_still_v1.txt`).
  - `references`: array of `references[].id` keys wired to the still generator.
  - `estimated_credits`: quote from `higgsfield generate cost`.
  - `selected_take` / `selected_job_id`: `null` until accepted by Visual Critic, then updated by Root Orchestrator to the relative path under `media/stills/` and Higgsfield job UUID.
- `video` (object):
  - `model`: live Higgsfield video model or workflow ID (for example `seedance_2_5`, `cinematic_studio_video_4_0`).
  - `is_workflow`: boolean (`false` for model `job_set_type` such as `seedance_2_5`, `true` for workflow endpoints such as `cinematic_studio_video_4_0`).
  - `mode`: live schema mode verified via `higgsfield model get` / `workflow get` (`omni_reference`, `t2v`, `video_edit`, `video_extension`, etc.; `cinematic_studio_video_4_0` uses `"is_workflow": true` with `"mode": "omni_reference"`—never `"mode": "i2v"`).
  - `prompt_file`: relative path to motion prompt file (for example `prompts/s01_video_v1.txt`).
  - `start_image_from` / `end_image_from`: reference pointer (`"s01.still"`, another shot's still/last-frame, a `ref_*` ID, or `null`).
  - `image_references`: array of `references[].id` keys passed for identity/product lock.
  - `draft_params`: low-cost preview parameters (`"resolution": "480p"` or `"720p"`, or `"draft": true` on `seedance_2_5`).
  - `final_params`: high-resolution master parameters (`"resolution": "1080p"`, optional Cinema Studio preset UUIDs from `docs/cinema-presets.json`).
  - `estimated_draft_credits` / `estimated_final_credits`: verified quotes from `higgsfield generate cost`.
  - `selected_take` / `selected_job_id`: `null` until accepted; updated by Root Orchestrator across draft and final passes.

### Audio Entries (`audio.music`, `audio.voiceover`)

- `audio.music`: `enabled` (bool), `model`, `duration_s`, `prompt` (or `prompt_file`), `estimated_credits`, `selected_file` (relative path under `media/audio/` once accepted).
- `audio.voiceover`: `enabled` (bool), `model`, `voice_id` (verified via `higgsfield voices list`), `voice_type`, `estimated_credits`, and `tracks[]` (when enabled, each track specifies `id`, `shot_ids`, `window_s`, `script_file`, `selected_file`, `selected_job_id`).

## Budget Math

Every `shotlist.json` must satisfy both spend envelopes declared in `intent.md`
**before** Planning or Production begins (verified by `higgsfield generate cost`
and checked mechanically by `scripts/check-ledger.py`):

```text
Draft pass estimate:
  sum(shot.still.estimated_credits for shot in shots if shot.still)
+ sum(shot.video.estimated_draft_credits for shot in shots)
+ (audio.music.estimated_credits if audio.music.enabled else 0)
+ (audio.voiceover.estimated_credits if audio.voiceover.enabled else 0)
<= Draft cap

Final pass estimate:
  sum(shot.video.estimated_final_credits for shot in shots)
+ final_audio_or_analysis_credits (for example optional brain_activity Virality Predictor)
<= Final cap
```

- **Retry headroom rule:** target first-pass Draft estimate at `<= 75%` of
  `Draft cap` whenever feasible so bounded retries (`Max auto-retries/shot`) do
  not immediately halt the wave. If first-pass estimates alone exceed either
  cap, optimize craft inside `intent.md` bounds or emit a `Blocked Exit`
  (`BUDGET_CAP`) before spending a single credit.
- **No silent edits:** every `prompt_file` referenced in `shotlist.json` must
  exist on disk, every `references` / `image_references` key must resolve to
  `references[].id`, and only the Root Orchestrator updates runtime selection
  fields (`upload_id`, `selected_take`, `selected_job_id`, `selected_file`).
