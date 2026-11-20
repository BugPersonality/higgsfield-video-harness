# Model Prompt Calibration and Failure Diagnostics

Engine-specific prompt tuning and root-cause repair rules for `R4`/`R5` motion prompts and isolated video tasks. Always verify live parameters via `higgsfield model get <id> --json` / `workflow get <id> --json` and cost routing in [Model Selection](../../higgsfield-cli/references/model-selection.md).

## Model-by-Model Prompt Calibration

| Model / Family | Word Sweet Spot | Preferred Syntax & Prompt Focus | Primary Strength | Failure Mode When Overshot / Misprompted |
| --- | --- | --- | --- | --- |
| `seedance_2_0_mini` / `seedance_2_5` | **30–60 words** | Concise delta-only motion/environment modifier + explicit `@Image` / `@Video` / `@Audio` role binding | Multi-ref continuity (up to 12–30 refs), draft-to-final escalation, strong multilingual lip-sync | Restating reference appearance in text causes cross-attention conflict, warping, and jitter |
| `cinematic_studio_video_4_0` | **40–75 words** | Strict separation: optics/light/cast locked in `R3` still + `omni_reference`; video prompt carries micro-beats, camera track, and foley | Flagship multi-ref coherence (up to 30–50 refs) and clean native diegetic foley | Re-describing static scene elements or stuffing >2 beats per 5s blurs hand/product mechanics |
| `wan3_0` / `wan3_0_prime` | **50–80 words** | Literal physical cause-and-effect verbs, weight, fabric/light reaction; zero metaphors | Top natural physics (cloth, water, light), smooth calm single takes, best draft quality/cost | Abstract poetic prose dilutes physical action weight; >100 words softens motion timing |
| `veo3_1` / `veo3_1_lite` | **40–75 words** (3–5 sentences) | Technical DP syntax: focal length, framing, 4-part lighting, single camera move, explicit grounded audio | Atmospheric lighting, shallow DOF, top English native audio, Ingredients & First/Last Frame | Narrative over-explaining >100 words blends clauses and drops camera moves; quoted dialogue without anti-subtitle line burns captions |
| `kling_o3` / `kling_3_0` | **60–90 words** (or Master + Shots) | Natural-language sequential action chains; native Multi-Shot via `[MASTER PROMPT]` + `[SHOT 1..N]` with durations | Native Multi-Shot (up to 6 shots), Elements consistency, expressive performance & multilingual dialogue | Comma-separated keyword soup; >120 words triggers late-clip action freeze / token exhaustion |
| `minimax_h3` / `minimax_h3_max` | **45–75 words** | `[Camera] + [Subject + Gaze Anchor] + [Physical Event] + [Light/Sound]`; strict One-Move Rule | High facial likeness retention, nuanced expression, coherent body physics | Missing Gaze Anchor triggers lens stare; compound camera moves warp background |
| Runway Gen-4 / Gen-4.5 *(external)* | **30–60 words** (I2V) | **CCR** (`Camera -> Character -> Reaction`), strictly positive phrasing, zero static re-description | Crisp sequential I2V motion following over clean keyframes | Inline negative prompts backfire; source still defects magnify in motion |
| Luma Ray 3 / 3.2 *(external)* | **40–70 words** | Direct transformation intent paired with Start/End keyframes and `cref` | Reasoning-driven keyframe bridges and surgical scene modification | Packing unrelated events into one pass breaks interpolation |
| LTX-2 *(external)* | **60–110 words** (4–8 sentences) | Strictly **one flowing present-tense paragraph**, chronological order with interwoven audio | Fast chronological audio-video takes | Bullet lists, comma tags, or past tense stall motion calculation |
| Sora 2 *(external)* | **50–90 words** | Counted action beats (`takes four steps, pauses, pulls curtain in final second`) + material physics | Coherent multi-second temporal continuity and physical interaction | Vague single verbs (`walks`, `jumps`) cede choreography to random rewrites |

## Language, Structure, and Negation Rules

1. **English direction, native dialogue:** Write camera, framing, physics, lighting, and acoustic direction in precise English (dense VLM training captions align sharpest in English; Simplified Chinese is equally sharp for East Asian cultural aesthetics on Kling/Wan/Seedance). Keep spoken character dialogue in its target language with explicit attribution (`says in natural Russian, quiet steady voice: ...`).
2. **Structured thinking vs. raw JSON:** Text encoders (T5 / UMT5 / MLLM) gain **no hidden neural boost** from raw JSON brackets—punctuation consumes token budget. Use JSON or labeled blocks internally as a checklist or pipeline schema, then feed clean prose (or explicit `[SHOT]` / `0-2s` blocks on models that support them) to the video engine.
3. **Positive phrasing vs. narrow explicit exclusions:** Express every visual, lighting, texture, and camera preference as its **positive physical target** (`locked-off tripod shot`, `matte grain`, `soft overcast daylight`). Reserve explicit `No ...` lines strictly for:
   - suppressing native score (`NO MUSIC. NO BACKGROUND SCORE. Native diegetic sound only.`);
   - suppressing burned-in captions on dialogue shots (`No subtitles, no captions, no on-screen text.`);
   - short technical artifacts inside a dedicated API `negative_prompt` field when exposed (`subtitles, captions, watermark, flicker`).

## Symptom-to-Fix Prompt Diagnostics

On `ITERATING` retries (`v1 -> v2`), apply **One Variable Per Re-roll**: diagnose the primary defect below and change only that single axis while holding working anchors constant.

| Observed Defect on Clip / Contact Sheet | Root Cause | Surgical Prompt / Conditioning Fix |
| --- | --- | --- |
| **Face, wardrobe, or product morphs in I2V** | Video prompt re-described static frame details OR camera move is too aggressive | Strip static appearance/background text from the video prompt; keep only motion delta; keep original source UUIDs in `--image_references` |
| **Unwanted floating camera drift or jitter** | Camera behavior omitted, letting the model inject statistical average motion | Add `Locked-off static tripod shot` (or constrain to one slow continuous move) |
| **Subject stares awkwardly into the lens** | Training-data prior (vlogs/interviews) without a specified eyeline | Add an explicit Gaze Anchor (`eyes focused down on the clasp, looking off-camera left, never looking at the camera`) |
| **Walls stretch, bend, or morph between Start and End frames** | Camera verb contradicts frame parallax (`pan`/`zoom` used for lateral/depth shift) OR spatial jump exceeds 5s | Replace `pan` → `lateral truck`, `zoom` → `slow dolly-in`; reduce physical distance between `--start_image` and `--end_image` |
| **Action rushes, collides, or freezes near the end** | Beat overload (>2 beats per 5s) OR prompt exceeded model word sweet spot | Cut to 1–2 counted physical beats inside the model's sweet spot; break complex choreography into separate shots |
| **Plastic / glossy "AI look"** | Empty buzzwords (`cinematic`, `hyperrealistic`, `4k`) without real optics, motivated light, or secondary physics | Replace buzzwords with focal length (`35mm`/`50mm`), 4-part motivated lighting, matte surface cues, and secondary physics (dust, cloth weight, breathing) |
| **Burned-in gibberish subtitles on dialogue shot** | Quoted speech triggered on-screen text rendering | Switch from `"..."` to colon syntax (`Character says in natural <Lang>: ...`) and append `No subtitles, no captions, no on-screen text.` |
| **Unwanted generic background music** | Audio layer left unspecified or purely negative without concrete diegetic sound | Specify concrete foley + room tone first, then close with `NO MUSIC. NO BACKGROUND SCORE. Native diegetic sound only.` |
| **Color or texture bleeds between two objects** | Multi-subject attribute bleeding inside one long clause or too many reference images (`> 5`) | Reduce to one primary subject, prune `image_references` to **2–4 visible essentials** with explicit isolated `@ImageN` roles, and lock isolated pigments on the `R3` still |
| **Reverse shot invents a new room or flips furniture 180°** | Single establishing plate lacked opposite-wall data or prompt used camera-relative left/right | Lock a dedicated **Reverse Wall plate** (`3d_jutsu_angles` / `nano_banana_2_1`) from the `N/E/S/W` Spatial Map and re-stage the `R3` still ([Locations & Props](../../video-consistency/references/locations-and-props.md)) |
| **Prop/building changes size across cuts (`Scale Drift`) or carries wrong shadow color (`Lighting Bake-In`)** | Prop ref lacked a scale benchmark, carried colored/harsh light, or sat on cluttered background | Re-anchor prop on `#808080` matte mid-gray under diffused `5000–5600K` light + add a **Scale Reference** plate (or neutralize with `nano_banana_2_relight` / `image_decompose`) |
| **Video freezes into a stiff "living photo" on multi-ref** | Reference overload (`> 5–6` images) or redundant/off-screen refs over-constrained optical flow | Keep only **2–4 visible references** (`start_image` + 1–2 highest-risk canonical refs + optional `end_image`) and strip static appearance prose from the motion prompt |
| **Silent failure / `ip_detected` moderation block** | Franchise, celebrity, director, or third-party brand cue in prompt or keyframe | Decompose into raw materials, geometry, and light; if still blocked, soften `--start_image` to `--image_references` or regenerate the `R3` still |
