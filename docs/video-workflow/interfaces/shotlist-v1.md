# Live Production Board / Shotlist V1

`campaigns/<slug>/shotlist.json` is the live production manifest connecting
creative direction (`brief.md`, `taste-log.md`, `storyboard.md`,
`style-bible.md`) to live Higgsfield CLI schemas, uploaded reference UUIDs,
Lookbook entities, keyframe stills, video shots, audio tracks, per-asset
`LOCKED` state, and round-by-round credit math.

Authored in [R1B — Story & Cost Ticket](../rounds/r1-story-and-cost.md),
validated mechanically by `make campaign-check CAMPAIGN=<slug>`
(`scripts/check-campaign.py`), updated serially **only** by the Root Producer
after each Dailies checkpoint, and read by `scripts/hf_guard.py` to enforce
`LOCKED` asset immutability (`asset_locked`).

## JSON Structure

```json
{
  "schema_version": 1,
  "campaign": "<slug>",
  "aspect_ratio": "16:9",
  "target_duration_s": 15,
  "fps_target": 24,
  "continuity_lock": {
    "product": "Matte Warm Saddle Tan leather (#8B5A2B), satin-brushed brass square clasps, blind-debossed NORD ATELIER centered 24 mm below front handle gusset",
    "lighting_and_palette": "Screen-left low morning sunlight (~4600K) against cool limestone sky fill (~6200K); matte tones, zero studio sweep glare",
    "space_cast_axis": "Sunlit limestone railway concourse; anonymous traveler in matte charcoal wool coat and heather-grey cuff; right hand closes clasp; left-to-right 180-degree axis"
  },
  "references": [
    {
      "id": "ref_product_front",
      "kind": "product",
      "local_path": "media/references/product_front.jpg",
      "upload_id": null,
      "status": "LOCKED"
    }
  ],
  "lookbook": [
    {
      "id": "lb_concourse_set",
      "kind": "location",
      "prompt_file": "prompts/lb_concourse_set_v1.txt",
      "model": "gpt_image_2_6",
      "variants_requested": 3,
      "status": "DRAFT",
      "approved_variant": null,
      "approved_upload_id": null,
      "estimated_credits": 30
    }
  ],
  "shots": [
    {
      "id": "s01",
      "title": "Opening brass clasp closure macro",
      "duration_s": 5,
      "test_take_check": {
        "risk": "Hand-to-clasp grip anatomy or illegible blind-debossed wordmark during latch closure",
        "pass_check": "Five natural fingers close the square brass clasp smoothly without metal morphing or garbled lettering across panels 1-6"
      },
      "still": {
        "model": "gpt_image_2_6",
        "prompt_file": "prompts/s01_still_v1.txt",
        "references": ["ref_product_front", "lb_concourse_set"],
        "status": "DRAFT",
        "version": 1,
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
        "image_references": ["ref_product_front", "lb_concourse_set"],
        "status": "DRAFT",
        "version": 1,
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
      "prompt": "Sparse acoustic chamber score for solo warm cello and felt upright piano...",
      "status": "DRAFT",
      "version": 1,
      "estimated_credits": 10,
      "selected_file": null,
      "selected_job_id": null
    },
    "voiceover": {
      "enabled": false,
      "model": null,
      "voice_id": null,
      "voice_type": null,
      "status": "DRAFT",
      "version": 1,
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
| `schema_version` | integer | Must be `1`. |
| `campaign` | string | Matches the campaign directory slug. |
| `aspect_ratio` | string | Live schema-verified ratio (`"16:9"`, `"9:16"`, `"1:1"`, etc.) matching `brief.md`. |
| `target_duration_s` | number | Target runtime in seconds; sum of `shots[].duration_s` must match within edit tolerance. |
| `fps_target` | integer | Locked delivery frame rate (`24`, `25`, or `30`) enforced by `scripts/assemble.sh` in **both** `--animatic` and video assembly modes and verified by `scripts/qa_media.py`. |
| `continuity_lock` | object *(optional)* | Three cross-shot invariants inherited from `storyboard.md` / `style-bible.md`: `product`, `lighting_and_palette`, and `space_cast_axis`. |
| `references` | array | Supplied real photos or pre-existing reference assets (may be empty `[]`). |
| `lookbook` | array | Invented objects, characters, or environments designed in `R2` (empty `[]` when `R2` is skipped because all assets are supplied real photos). |
| `shots` | array | Non-empty ordered list of shots (`s01`, `s02`, ...). |
| `audio` | object | Required `music` and `voiceover` sub-objects. |

### Per-Asset Status Machine (`status` & `version`)

Every Lookbook entry, still, video shot, and audio track carries an explicit
`status` (plus integer `version >= 1` on stills, videos, and audio tracks):

| Status | Meaning | `hf_guard.py` behavior |
| --- | --- | --- |
| `DRAFT` | Planned or first-pass generation in progress; not yet presented in Dailies. | Permits guarded generation inside active `--round-cap`. |
| `IN_REVIEW` | Passed internal QC (`qa_media.py` + `reviewer-agent`) and currently presented to the Director in a Dailies Packet. | Paused waiting for Director feedback. |
| `ITERATING` | Director requested a steer; `taste-log.md` updated, `version` incremented (`v2`, `v3`, ...), new versioned `prompt_file` written, and micro-cost approved. | Permits guarded surgical re-roll inside cumulative `--round-cap <round_spent + delta_cap>` using matching `--version <N>` (plus `--variant` for Lookbook). |
| `LOCKED` | Approved by the Director at Dailies. Immutable. | **Refuses both `preflight` and `run` with `asset_locked`** (no `--force-unlock` CLI bypass) unless the Director explicitly unlocks the asset and Root Producer edits `shotlist.json` back to `ITERATING`. |

### Reference Entries (`references[]`)

- `id`: unique snake_case key (`ref_bag_front`, `ref_actor_soul`).
- `kind`: semantic role (`product`, `product_detail`, `product_worn`,
  `character`, `environment`, `style`, `soul_id`).
- `local_path`: relative path under `media/references/`.
- `upload_id`: `null` until uploaded via `python3 scripts/hf_guard.py upload --campaign <dir> --round <R2|R3> --file <path> --ref-id <id>`, then populated by the Root Producer with the Higgsfield upload UUID or Soul ID.
- `status`: optional (`"LOCKED"` for verified supplied source photos).

### Lookbook Entries (`lookbook[]`)

Used in [R2 — Casting & World Lookbook](../rounds/r2-lookbook.md) whenever an
entity is invented rather than supplied as a real photo:

- `id`: unique snake_case key (e.g., `lb_hero_watch`, `lb_protagonist`,
  `lb_concourse_set`); usable inside `shots[].still.references` and
  `shots[].video.image_references` once `LOCKED`.
- `kind`: `character | object | location` (validated mechanically by `scripts/check-campaign.py`).
- `prompt_file`: relative path under `prompts/` (e.g., `prompts/lb_concourse_set_v1.txt`).
- `model`: live Higgsfield image model ID verified via `higgsfield model list --json`.
- `variants_requested`: integer `>= 1` (aligned with `Lookbook variants` in `brief.md`, typically `2` or `3` for `A / B / C` comparison).
- `status`: `DRAFT | IN_REVIEW | ITERATING | LOCKED` (with optional integer `version >= 1`, `title`, and `approved_take`).
- `approved_variant`: `null` until Director selects winning variant (for example `"B"` or relative path under `media/lookbook/`; required non-empty when `status: "LOCKED"`).
- `approved_upload_id`: `null` until Root Producer uploads the approved Lookbook image via `hf_guard.py upload`, then Higgsfield upload UUID used to lock `R3` stills and `R4`/`R5` video shots.
- `estimated_credits`: live `higgsfield generate cost` × `variants_requested`.

### Shot Entries (`shots[]`)

- `id`: zero-padded key (`s01`, `s02`, ...) matching disjoint worker paths
  (`prompts/sNN_*`, `media/stills/sNN-*`, `media/shots/sNN-*`, `qc/sNN-*`).
- `title`: concise beat title aligned with `storyboard.md` / `script.md`.
- `duration_s`: positive duration supported by the live video model schema.
- `test_take_check` (object or `null`, optional): carried from `storyboard.md`
  exclusively for risky shots (grip, physics, legible text, reflection, comic
  timing, multi-subject blocking):
  - `risk`: exact failure mode to falsify in `R4A` Risk-First Pilot;
  - `pass_check`: observable visual condition verified on panels 1–6 by
    `reviewer-agent` (`view_image`).
- `still` (object or `null` for pure text-to-video shots):
  - `model`, `prompt_file`, `references` (resolving to `references[].id` or
    `lookbook[].id`), `status`, `version`, `estimated_credits`,
    `selected_take`, `selected_job_id`.
- `video` (object):
  - `model`: live Higgsfield video model or workflow ID (e.g., `seedance_2_5`,
    `cinematic_studio_video_4_0`).
  - `is_workflow`: boolean (`false` for model `job_set_type` like `seedance_2_5`;
    **`true`** for workflow endpoints like `cinematic_studio_video_4_0`).
  - `mode`: live schema mode verified via `higgsfield model get` /
    `workflow get`. **`cinematic_studio_video_4_0` MUST use `"is_workflow": true`
    and `"mode": "omni_reference"` — never `"mode": "i2v"`.**
  - `prompt_file`, `start_image_from` (`"s01.still"`, `"ref_*"`, `"lb_*"`, or
    `null`), `end_image_from`, `image_references` (resolving to `references[].id`
    or `lookbook[].id`).
  - `status`, `version`.
  - `draft_params`: low-cost preview settings for `R4` (`"resolution": "480p"`
    or `"720p"`, or `"draft": true` on `seedance_2_5`).
  - `final_params`: `1080p` master settings for `R5` (plus optional Cinema
    Studio preset UUIDs extracted into `docs/cinema-presets.json`).
  - `estimated_draft_credits`, `estimated_final_credits`: verified live quotes
    from `higgsfield generate cost`.
  - `selected_take`, `selected_job_id`: updated by Root Producer across `R4`
    draft and `R5` `1080p` final passes.

### Audio Entries (`audio.music`, `audio.voiceover`)

- `audio.music`: `enabled` (bool), `model`, `duration_s`, `prompt` (or
  `prompt_file`), `status` (required when `enabled: true`), `version`,
  `estimated_credits`, `selected_file`, `selected_job_id`.
- `audio.voiceover`: `enabled` (bool), `model`, `voice_id` (verified via
  `higgsfield voices list`), `voice_type`, `status` (required when
  `enabled: true`), `version`, `estimated_credits`, and `tracks[]`. Each entry
  in `tracks[]` specifies `id`, `shot_ids`, `start_s` (cue offset in seconds;
  `window_s` is also supported as a target window / fallback parsed by
  `scripts/assemble.sh`), `script_file`, `status` (required when voiceover is
  enabled), `version`, `selected_file`, and `selected_job_id`.

## Budget Math (`make campaign-check`)

Before presenting **Dailies 1B** (and after any shotlist edit), run
`make campaign-check CAMPAIGN=<slug>` (`scripts/check-campaign.py`) to verify
all prompt paths, reference IDs, `cinematic_studio_video_4_0` workflow wiring,
explicit numeric credit estimates on every `still` (`estimated_credits`) and
`video` (`estimated_draft_credits`, `estimated_final_credits` — no silent `0`
default), required `status` fields on all assets and enabled `audio.*` tracks,
and total campaign budget math against `Campaign cap` in `brief.md`:

```text
r2_lookbook     = sum(item.estimated_credits for item in lookbook)
r3_stills_audio = sum(shot.still.estimated_credits for shot in shots if shot.still)
                + (audio.music.estimated_credits if audio.music.enabled else 0)
                + (audio.voiceover.estimated_credits if audio.voiceover.enabled else 0)
r4_draft_video  = sum(shot.video.estimated_draft_credits for shot in shots)

draft_total     = r2_lookbook + r3_stills_audio + r4_draft_video
final_total     = sum(shot.video.estimated_final_credits for shot in shots)
                + optional_final_analysis_credits

planned_total   = draft_total + final_total <= Campaign cap
```

- **Round Cost Ticket slicing:** Dailies 1B breaks `planned_total` into exact
  per-round quotes (`R2 = r2_lookbook`, `R3 = r3_stills_audio`,
  `R4A = pilot slice of r4_draft_video`, `R4B = remaining r4_draft_video`,
  `R5 = final_total`) so the Director approves one `--round-cap` at a time.
- **Retry & iteration headroom:** target `planned_total <= 75%` of
  `Campaign cap` whenever feasible so internal defect filters and 1–2 surgical
  Director re-rolls fit cleanly without raising `Campaign cap`.
- **Single-writer discipline:** every `prompt_file` must exist on disk, every
  reference key must resolve to `references[].id` or `lookbook[].id`, and only
  the Root Producer edits `shotlist.json`.
