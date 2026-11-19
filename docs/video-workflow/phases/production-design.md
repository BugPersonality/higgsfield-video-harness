# Phase 2 — Production Design

Use once `intent.md`, `treatment.md`, and `style-bible.md` are at
`status: ready` and the campaign lacks a reviewed `shotlist.json`, prompt pack,
and verified credit budget proof. Runs in a fresh phase session
(`fork_turns: "none"`) with zero prior chat history and spends **zero** credits
(all Higgsfield calls in Phase 2 are free read-only schema and cost queries).

## Steps

1. **Discover live Higgsfield schemas via `evidence-agent`.**
   - Never guess model IDs, flag names, duration limits, voice IDs, or credit
     costs from memory. Dispatch a fresh read-only `evidence-agent`
     (`fork_turns: "none"`, `reasoning_effort: low`) to inspect live CLI
     surfaces (loading skill `higgsfield-cli` when selecting models/workflows):
     - `higgsfield model list --json` and `higgsfield model get <jst> --json`
       for candidate still, video, audio, and optional analysis (`brain_activity`)
       models;
     - `higgsfield workflow list` and `higgsfield workflow get <name>` if any
       beat uses a workflow (`is_workflow: true`);
     - `higgsfield voices list` if `audio.voiceover.enabled` is true;
     - `docs/cinema-presets.json` (if present, structured per
       [`docs/cinema-presets.example.json`](../../cinema-presets.example.json))
       whenever `cinematic_studio_video_4_0` reuses extracted Cinema Studio 4.0
       preset UUIDs (remember: Web-only Cinema Studio controls like Emotion
       Wheel / AI Cast have no CLI flag, and opaque preset UUIDs have no CLI
       listing command—either leave unset as `Auto` or load verified UUIDs from
       `docs/cinema-presets.json`).
   - Verify exact live parameter names, supported durations, resolutions
     (`480p`/`720p` or `seedance_2_5 --draft` vs `1080p`), aspect ratios, and
     reference roles (`--image`, `--start-image`, `--end-image`,
     `omni_reference`, `soul_id`).

2. **Author `shotlist.json`, reference graph, and prompt templates.**
   - Build `campaigns/<slug>/shotlist.json` conforming strictly to
     [Shotlist Schema V1](../interfaces/shotlist-v1.md):
     - when `campaigns/<slug>/storyboard.md` (and `script.md`) exist from Phase
       1's commercial track, translate them **1-to-1** without dropping craft
       constraints:
       | Storyboard / Script field | `shotlist.json` & prompt mapping |
       | --- | --- |
       | `Continuity Lock` (Product, Lighting & palette, Space/cast/axis) | Top-level `continuity_lock` (`product`, `lighting_and_palette`, `space_cast_axis`) + shared prompt anchors |
       | `Start frame` (+ `Focal entry`) | `shots[].still.prompt_file` (`prompts/sNN_still_v1.txt`) |
       | `Action` (+ motivated camera move & `Cut trigger`) | `shots[].video.prompt_file` (`prompts/sNN_video_v1.txt`) |
       | `End frame` | Optional `shots[].video.end_image_from` reference or next-shot `Start frame` handoff |
       | `Test-take check` (risky shots only) | `shots[].test_take_check` (`{"risk": "...", "pass_check": "..."}` or `null`) |
       | `Read-aloud budget` + `[PAUSE Ns]` + `Audio sync` | `audio.voiceover.tracks[]` (`window_s`, `script_file`) validated by `scripts/qa_media.py voice --window` |
     - wire every local asset under `media/references/` into `references[]`
       with `upload_id: null`;
     - wire every shot `s01..sN` with its `still` keyframe anchor and `video`
       `start_image_from` (`"<shot_id>.still"`), `end_image_from`, and
       `image_references` (applying `video-consistency` craft rules so product,
       face, lighting, and wardrobe stay locked across cuts);
     - define both low-cost `draft_params` (`480p`/`720p` or `seedance_2_5
       --draft`) and high-resolution `final_params` (`1080p`);
     - configure `audio.music` and `audio.voiceover`.
   - Write versioned prompt files under `campaigns/<slug>/prompts/`
     (`sNN_still_v1.txt`, `sNN_video_v1.txt`, plus `vo_script_v1.txt` /
     `music_v1.txt` if file-backed), applying `video-direction` craft rules:
     - timestamped single-axis motion beats matching `style-bible.md` and
       `continuity_lock`;
     - raw-clip diegetic footer (`NO MUSIC. NO BACKGROUND SCORE. Native diegetic
       sound only.`) when music is mixed separately in assembly;
     - anti-IP visual phrasing (zero celebrity names or third-party trademarks);
     - phonetic brand/product spellings and strict words-per-second pacing
       budgets (`<= 2.0 words/s` Russian / longer-word languages, `<= 2.3
       words/s` English, respecting explicit `[PAUSE Ns]` holds) for every VO
       segment so spoken delivery fits its `qa_media.py voice` window naturally
       without `atempo`.

3. **Verify live credit cost against `Draft cap` and `Final cap`.**
   - Query `higgsfield generate cost` (via `evidence-agent` or read-only CLI)
     for every still, draft video, final video, music/VO track, and optional
     `brain_activity` analysis call; populate `estimated_credits`,
     `estimated_draft_credits`, and `estimated_final_credits` in
     `shotlist.json`.
   - Prove both inequalities from
     [Shotlist Budget Math](../interfaces/shotlist-v1.md#budget-math):
     - `Draft pass estimate <= Draft cap` (preferring `<= 75%` of `Draft cap`
       for bounded retry headroom);
     - `Final pass estimate <= Final cap`.
   - If estimates exceed either cap, optimize craft inside `intent.md` bounds
     (for example, draft resolution, model selection, or beat consolidation
     permitted by `Binding: default`). If no valid plan fits inside
     `Binding: hard` invariants, emit a
     [Blocked Exit](../shared/transition.md#blocked-exit) (`BUDGET_CAP`)
     showing exact per-shot costs and concrete options (`Option A`: raise cap,
     `Option B`: trim duration/shot count) without spending any credits.

4. **Run fresh Shotlist & Budget Review.**
   - Dispatch one fresh read-only `reviewer-agent` (`fork_turns: "none"`,
     `reasoning_effort: high`) running
     [Shotlist And Budget Review](#shotlist-and-budget-review) under
     [Review](../shared/review.md), passing `intent.md`, `treatment.md`,
     `style-bible.md`, `shotlist.json`, `prompts/*`, and `evidence-agent`'s
     live schema + `generate cost` receipts.
   - Repair confirmed defects in place (max 2 rounds), then return
     [Transition Result V1](../shared/transition.md#transition-result-v1) naming
     [Planning](planning.md) as `next_owner`.

## Shotlist And Budget Review

Read-only review adapter for fixed `campaigns/<slug>/shotlist.json` and
`campaigns/<slug>/prompts/*`. Return
[Review Result V1](../interfaces/review-result-v1.md):

1. **Schema & live-CLI parity:** verify `schema_version: 1`, valid JSON,
   every `model`, `mode`, `duration`, `resolution`, `aspect_ratio`, and
   `voice_id` matches the live `higgsfield model get` / `workflow get` /
   `voices list` receipts (zero invented flags or stale aliases).
2. **Reference graph, continuity & storyboard parity:** confirm every
   `prompt_file` exists on disk, every `references` / `image_references` key
   resolves to `references[]`, every `start_image_from` / `end_image_from`
   resolves to a defined `<shot_id>.still`, and cross-shot lighting/subject
   anchors match `style-bible.md`. When `storyboard.md` / `script.md` exist,
   verify `continuity_lock`, `Start frame` / `Action` / `End frame` prompt
   translation, `shots[].test_take_check` carry-over on risky shots, and VO
   window alignment with `Read-aloud budget` and `[PAUSE Ns]`.
3. **Prompt & audio hygiene:** check all prompt files for `Must not` compliance,
   anti-IP wording, `NO MUSIC. NO BACKGROUND SCORE.` footer (when mixing music
   separately), phonetic brand pronunciations, and realistic VO window lengths.
4. **Budget arithmetic:** independently sum still + draft video + audio credits
   against `Draft cap` and final video + final audio/analysis credits against
   `Final cap`, flagging zero retry headroom as `CONCERN` and any cap breach as
   `FAIL` (`BUDGET_CAP`).

Return `PASS`, `CONCERNS`, or `FAIL`.
