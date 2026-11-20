# Model Selection, Benchmarks & Web Unlimited-First Routing

Benchmark-grounded routing for choosing **free Web Unlimited (`0 cr.`)**,
**economy CLI drafts**, or **flagship CLI finals** across `R2`–`R5`. Always
confirm live CLI pricing via `higgsfield generate cost` before quoting—credit
snapshots below reflect the `ultra` plan as of `2026-11` and may drift.

## Generation Priority Ladder

Always try cheaper tiers before spending flagship credits:

1. **Web UI `Unlimited` (`0 cr.`) via built-in browser agent (Priority 1):**
   On `ultra` and eligible plans, the **Unlimited (`0 cr.`)** toggle works
   **only** inside the `higgsfield.ai` web app—CLI, API, and MCP always charge
   credits even for Unlimited-eligible models. Whenever a target model has an
   active `Unlimited` toggle on `higgsfield.ai`, prioritize generating through
   the built-in browser subagent first.
2. **Economy CLI drafts (Priority 2):** When the model has no `Unlimited`
   toggle, the Director wants fast parallel CLI batches, or multi-ref counts
   exceed web convenience, run cheap CLI draft models (`0.12–0.5 cr.` stills;
   `5–8.75 cr.` `720p` video or `15 cr.` `seedance_2_5 --draft true`) via
   `hf_guard.py run`.
3. **Flagship CLI finals (Priority 3):** Reserve flagship models and `1080p`
   renders (`35–80 cr.`) strictly for Director-approved `R5` upgrades or
   high-risk multi-reference `R4A` pilots.

## Built-In Browser Agent Protocol (`higgsfield.ai` Unlimited, `0 cr.`)

Use this workflow to capture `0 cr.` Unlimited image or video generations
without violating anti-bot boundaries:

1. **Launch in the user's logged-in browser pane:** delegate to the `browser`
   subagent to open `higgsfield.ai`, select the target model, and verify that
   the **Unlimited** toggle is present and **ON** (`0 credits`).
2. **CAPTCHA / Login handoff (hard rule):** Never attempt to solve, click
   through, or bypass a CAPTCHA, Cloudflare Turnstile, or login wall. Pause
   immediately, notify the Director to complete login or solve the CAPTCHA
   directly in the visible browser pane, and wait for confirmation.
3. **Resume the same browser session:** Once the Director confirms the CAPTCHA
   or login is cleared, call `send_message` on the **existing** browser
   subagent conversation ID (do not spawn a fresh tab/agent) so it continues in
   the cleared session to trigger the Unlimited generation(s) and download the
   outputs.
4. **Ingest into campaign truth:** Move/copy downloaded assets into the
   expected `campaigns/<slug>/media/{lookbook,stills,shots}/` path, run
   `scripts/qa_media.py` and fresh `reviewer-agent` QC, record the selected
   file in `shotlist.json`, and upload approved stills/lookbook winners via
   `hf_guard.py upload --round <R>` (`0 cr.`) so downstream shots stay UUID-locked.
5. **Fallback trigger:** If `Unlimited` is unavailable for the needed model,
   queue wait stalls the round, or the Director prefers speed over `0 cr.`,
   fall back cleanly to Priority 2 (Economy CLI drafts) via `hf_guard.py run`.

*Done when:* asset is saved under `campaigns/<slug>/media/`, passes internal
QC, and (if used as a downstream reference) is uploaded via `hf_guard.py upload`.

## Photorealistic Image Models — Benchmarks & Case Routing

Based on Artificial Analysis Image Arena (blind human preference Elo) and live
Higgsfield CLI pricing:

| Model (`job_type`) | CLI Cost (approx.) | Benchmark Strength | Best Use Case |
| :--- | ---: | :--- | :--- |
| `soul_cinematic` / `text2image_soul_v2` | `0.12 cr.` | Specialized cinematic stills | Ultra-cheap `R2`–`R3` composition, lighting, and angle thumbnails |
| `gpt_image_2_6` (standard) | `0.25 cr.` | Top-tier prompt adherence, geometry, mirrors, multi-ref edits | **Default `R2`–`R3` economy draft** and complex spatial/reflection staging |
| `seedream_5_0_flash` | `0.50 cr.` | Fast clean realism | **Fast `R2`–`R3` photorealistic draft** (7× cheaper than `seedream_5_5`) |
| `seedream_v5_lite` / `nano_banana_2_lite` / `flux_2` | `1.00 cr.` | Solid mid-budget realism | Low-cost Lookbook `A / B / C` exploration when `0.25–0.5 cr.` drifts |
| `nano_banana_2_1` / `nano_banana_pro` | `1.50–2.00 cr.` | Top physical plausibility, lighting coherence & multi-ref blending | **Best value hero stills (`R3`)** blending cast + location + wardrobe refs |
| `flux_3_image` | `2.00 cr.` | Benchmark leader for raw 35mm photographic skin, grain & non-plastic texture | **Hero editorial/35mm portraits & interiors** without heavy multi-ref edits |
| `seedream_v5_pro` | `2.50 cr.` | Strong adherence to long structured prompts, orthographic prop/cast sheets & `%`-palette lock (`<= 10` refs, `2k`) | **Workhorse `R2B` Asset Bibles & `R3` scene keyframes** (30% cheaper than `seedream_5_5`, native ByteDance match for `seedance_2_5`) |
| `gpt_image_2_6` (high quality) | `2.75 cr.` | Complex prompt logic, typography, strict single-item swaps | Hero frames needing exact multi-element control or mirror continuity |
| `seedream_5_5` | `3.50 cr.` | Top commercial/fashion detail & fabric fidelity under close inspection | **Flagship `R3` macro/fashion close-ups** (wool, leather, knit, hero textures) |

## Video Models — Benchmarks & Case Routing

**Resolution & escalation truth (why `720p` drafts or `seedance_2_5 --draft` beat dead-end `480p`):**
`cinematic_studio_video_4_0` only supports `480p / 720p / 1080p` (no `360p`) and does **not** expose `--draft_job_id` in CLI, while pixel-upscaling `480p` drafts (`< 1 Mbps`) into `1080p` creates halos, muddy faces, and worse economics than native `1080p`. Cut draft burn by choosing cheap `720p` draft engines (`seedance_2_0_mini`, `kling_4_0_flash`, `wan3_0`) or `seedance_2_5 --draft true` (which escalates natively via `--draft_job_id`). Follow [Mastering & Upscaling](mastering-and-upscaling.md) for every `R4 → R5` upgrade decision.

Based on Artificial Analysis Video Arena (I2V/T2V Elo) and live CLI pricing
(5s clips unless noted):

| Model / Workflow (`job_type`) | CLI Cost (5s) | Refs Supported | Benchmark Strength | Best Use Case |
| :--- | ---: | :--- | :--- | :--- |
| `seedance_2_0_mini` (`480p` / `720p`) | `2.5 cr.` (`4s` = `2 cr.`) / **`5 cr.`** | `start_image`, `end_image`, `image_references` | Fast lightweight Seedance motion | **Default `R4` economy `720p` draft** (3× cheaper than `480p` CS 4.0) to prove rhythm, camera move & edit cut |
| `kling_4_0_flash` (`720p`) | **`7.5 cr.`** | Up to 10 images + `video_references` (`video-edit`, `reference-to-video`) | Fast multi-ref Kling 4.0 choreography | **Default `R4` `720p` draft** before native `1080p` `kling4_0` mastering |
| `wan3_0` (`480p` / `720p` / `1080p`) | `5 cr.` / **`8.75 cr.`** / **`17.5 cr.`** | `start_image`+`end_image` OR `image_references` (mutually exclusive) | **Top Elo leader (~1175)**: natural fabric/light physics & subject stability | **Best value `720p` draft & cheapest native `1080p` master** for calm I2V takes *(verify FPS—may output 30fps)* |
| `kling4_0` (`720p` / `1080p` / `4k`) | `12.5 cr.` / **`18.75 cr.`** (`video-edit` `22.5 cr.`) / `45 cr.` | Up to 10 images (`start`/`end` + `image_references`) + `video_references` + `--dynamic_range hdr` | Top motion stability, facial consistency, multi-ref control & native stereo | **Default value native `1080p` `R5` master** (4.3× cheaper than CS 4.0 `1080p`) and motion-locked `video-edit` rescue |
| `veo3_1_lite` / `veo3_1` (`fast high` 4s / `preview`) | `12 cr.` / **`16 cr.`** (4s fast high) / `32 cr.` | `start_image` / T2V | **Benchmark leader for atmospheric light, DOF & cinema audio** | Moody single-subject atmospheric native `1080p` shots without heavy wardrobe ref stacks |
| `wan3_0_prime` (`720p` / `1080p`) | `15 cr.` / **`30 cr.`** | `start_image`+`end_image` OR `image_references` | Elevated fine skin/fabric micro-detail over `wan3_0` | Premium native `1080p` character portraits and tactile single-subject hero takes |
| `flux_3_video` (`720p` / `1080p` / `2k` / `4k`) | `30 cr.` / **`40 cr.`** | Up to 10 images OR `video_references` (mutually exclusive) | Editorial FLUX 3 color science and crisp single-frame look | Stylized fashion/editorial hero shots prioritizing color grade over long choreography |
| `minimax_h3` / `minimax_h3_max` | `10–12.5 cr.` | `start_image` / refs | **Top-5 Elo (~1161)**: strong character likeness retention | Calm portrait/character shots where face stability matters |
| `seedance_2_5` (`--draft true` → `1080p` / `4k`) | `15 cr.` → **`80 cr.`** (`5s`); `18 cr.` → **`96 cr.`** (`6s` 2-shot = `48 cr./cut`); `140 cr.` `4k` | Up to 30 images / 50 refs (`omni_reference`) + `--draft_job_id` + free `--bitrate_mode high` | **Top-5 Elo (~1160)**: multi-shot narrative, exact draft-to-final latent lock & VFX | **Gold standard `R4 → R5` CLI path** when exact acting/timing must transfer 1:1 into native `1080p` (`--bitrate_mode high`); pair adjacent cuts as `6s` 2-shots (`3s + HARD CUT + 3s`) to halve per-cut cost |
| `cinematic_studio_video_4_0` (`480p` / `720p` / `1080p`) | `15` / `35` / **`80 cr.`** | Up to 30 images / 50 refs (`omni_reference`) + free `--bitrate_mode high` *(no CLI `--draft_job_id`)* | Best multi-reference continuity + native diegetic foley + Web Cinema Studio presets | Direct native `1080p` (`--bitrate_mode high`) hero shots or Web Cinema Studio upgrades—avoid `480p` CLI drafts if you need 1:1 `R5` escalation |

## Quick Round-by-Round Defaults & Stack Presets

- **`R2` Lookbook & `R3` Draft Stills:** Web `Unlimited` (`0 cr.`) first →
  else CLI `soul_location` / `soul_cast` / `text2image_soul_v2` (`0.12 cr.`),
  `gpt_image_2_6` (`0.25 cr.`), or `seedream_5_0_flash` (`0.5 cr.`).
- **`R2B` Asset Bibles & `R3` Locked Hero Stills:** Web `Unlimited` (`0 cr.`)
  if eligible → else **`seedream_v5_pro` (`2.5 cr.`)** (workhorse orthographic
  prop/cast/location bibles & `2k` scene keyframes), `nano_banana_2_1`
  (`1.5 cr.`), `flux_3_image` (`2 cr.`), or **`seedream_5_5` (`3.5 cr.`)**
  reserved for macro/fabric hero close-ups.
- **`R4A` / `R4B` Motion Drafts:** Web `Unlimited` (`0 cr.`) first → else CLI
  `seedance_2_0_mini` (`720p`, `5 cr.`) / `kling_4_0_flash` (`720p`, `7.5 cr.`) /
  `wan3_0` (`720p`, `8.75 cr.`) for clean legible drafts; use **`seedance_2_5`
  `--draft true` (`15 cr.` 5s / `18 cr.` 6s 2-shot)** whenever an `R4A`/`R4B`
  take needs guaranteed 1:1 latent escalation to native `1080p` via
  `--draft_job_id`.
- **`R5` Final Master (`1080p`):** Follow [Mastering & Upscaling](mastering-and-upscaling.md).
  Upgrade unlocked winners **natively at `1080p`**: Web `Unlimited` (`0 cr.`) if
  eligible → `seedance_2_5 --draft_job_id <id> --resolution 1080p --bitrate_mode high`
  (`80 cr.` 5s / `96 cr.` 6s 2-shot) for locked draft takes → `kling4_0`
  (`18.75 cr.`, or `video-edit` `22.5 cr.`) / `wan3_0` (`17.5 cr.`) / `veo3_1`
  (`16 cr.`) / `wan3_0_prime` (`30 cr.`) for high-value native `1080p` →
  `cinematic_studio_video_4_0` (`1080p`, `--bitrate_mode high`, `80 cr.`) for
  direct multi-ref hero shots. Never pixel-upscale `480p` drafts; reserve pixel
  upscaling (`topaz_video` Starlight / SeedVR2 / `bytedance_video_upscale`)
  strictly for clean `>= 720p` sources (`<= 2×`) after passing the 6-rule
  Upscale Gate and a 1-shot `1:1` crop pilot.

### Two Proven 30s Production Stack Presets (Native `1080p`)

1. **Commercial Hybrid (~`250–400 cr.`):** `soul_location`/`soul_cast` (`0.12 cr.`)
   world scout → `seedream_v5_pro` (`2.5 cr.`) + selective `seedream_5_5` (`3.5 cr.`)
   for `R2B`/`R3` → `wan3_0` (`17.5 cr.`) or `kling4_0` (`18.75 cr.`) native
   `1080p` on clean single-beat shots + `seedance_2_5` (`15→80 cr.`, or `18→96 cr.`
   `6s` 2-shot) strictly on `2–3` hero acting or complex-continuity beats.
2. **Cinema / Flagship Narrative (~`650–1,000 cr.`):** `soul_location`/`text2image_soul_v2`
   (`0.12 cr.`) → orthographic `#808080` prop/cast/location bibles + `2k` keyframes
   on `seedream_v5_pro` (`2.5 cr.`) / `seedream_5_5` (`3.5 cr.`) → `seedance_2_5`
   (`--draft true` → `--draft_job_id --resolution 1080p --bitrate_mode high`) in
   paired `6s` 2-shot blocks (`3s + HARD CUT + 3s` = `48 cr./cut`), finished with
   unified post color grade and dedicated foley/sound mix.
