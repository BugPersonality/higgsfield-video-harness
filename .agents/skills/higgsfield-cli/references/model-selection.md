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
   `2.5–5 cr.` `480p` video) via `hf_guard.py run`.
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
| `gpt_image_2_6` (high quality) | `2.75 cr.` | Complex prompt logic, typography, strict single-item swaps | Hero frames needing exact multi-element control or mirror continuity |
| `seedream_5_5` | `3.50 cr.` | Top commercial/fashion detail & fabric fidelity under close inspection | **Flagship `R3` hero stills** (wool, leather, knit, product close-ups) |

## Video Models — Benchmarks & Case Routing

**Resolution truth (why switching draft model beats `<480p`):**
`cinematic_studio_video_4_0` only supports `480p / 720p / 1080p` (no `360p`).
Only `gemini_omni_flash_1_1` and `gemini_omni_flash_1_2` expose `360p`, and
their `360p` (8s) jobs cost `6–8 cr.`—more expensive than `seedance_2_0_mini`
at `480p` (`2.5 cr.`). Cut draft burn by **switching draft model**, not chasing
sub-`480p` resolutions.

Based on Artificial Analysis Video Arena (I2V/T2V Elo) and live CLI pricing
(5s clips unless noted):

| Model / Workflow (`job_type`) | CLI Cost (5s) | Refs Supported | Benchmark Strength | Best Use Case |
| :--- | ---: | :--- | :--- | :--- |
| `seedance_2_0_mini` (`480p` / `720p`) | **`2.5 cr.`** (`4s` = `2 cr.`) / `5 cr.` | `start_image`, `end_image`, `image_references` | Fast lightweight Seedance motion | **Default `R4` economy draft** (6× cheaper than CS 4.0) to prove rhythm, camera move & edit cut |
| `wan3_0` (`480p` / `720p`) | **`5.0 cr.`** / `8.75 cr.` | `start_image`, `end_image`, `image_references` | **Top Elo leader (~1175)**: natural fabric/light physics & subject stability | **Best quality/cost `R4` realistic draft** (3× cheaper than CS 4.0) and calm narrative takes |
| `cinematic_studio_video_v2` (`std`, `sound=off`) | **`5.0 cr.`** (`sound=on` = `7.5 cr.`) | `start_image`, `end_image`, `image_references` | Older Cinema Studio framing | Cheap alternative draft when staying inside Cinema Studio style |
| `grok_video_v15_lite` (`480p`) | `5.0 cr.` | `start_image` only | Fast basic I2V | Simple single-frame motion tests without multi-ref continuity |
| `kling_o3_image_reference` (`std`) | `6.25 cr.` | `image_references` | Multi-ref motion & smooth fabric | Reference-driven motion drafts |
| `minimax_h3` / `minimax_h3_max` | `10–12.5 cr.` | `start_image` / refs | **Top-5 Elo (~1161)**: strong character likeness retention | Calm portrait/character shots where face stability matters |
| `veo3_1_lite` / `veo3_1` | `12 cr.` / `32 cr.` | I2V / T2V | **Benchmark leader for atmospheric light, DOF & cinema audio** | Moody single-subject atmospheric shots without heavy wardrobe ref stacks |
| `cinematic_studio_video_4_0` (`480p` / `720p` / `1080p`) | `15` / `35` / **`80 cr.`** | Up to 30 images / 50 refs (`omni_reference`) | Best multi-reference continuity + native diegetic foley | **Flagship `R5` `1080p` master** & complex multi-ref `R4A` pilots (mirrors, outfit swaps) |
| `seedance_2_5` (`480p`/`720p` draft → `1080p`) | `15 cr.` → **`80 cr.`** | Up to 30 images (`omni_reference`) + `--draft_job_id` | **Top-5 Elo (~1160)**: multi-shot narrative & VFX coherence | Flagship `R5` when escalating an approved `--draft true` take via `--draft_job_id` |

## Quick Round-by-Round Defaults

- **`R2` Lookbook & `R3` Draft Stills:** Web `Unlimited` (`0 cr.`) first →
  else CLI `gpt_image_2_6` (`0.25 cr.`) / `seedream_5_0_flash` (`0.5 cr.`) /
  `soul_cinematic` (`0.12 cr.`).
- **`R3` Locked Hero Stills:** Web `Unlimited` (`0 cr.`) if eligible → else
  `nano_banana_2_1` (`1.5 cr.`), `flux_3_image` (`2 cr.`), or `seedream_5_5`
  (`3.5 cr.`) only on approved compositions.
- **`R4A` / `R4B` Motion Drafts:** Web `Unlimited` (`0 cr.`) if eligible →
  else CLI `seedance_2_0_mini` (`480p`, `2.5 cr.`) for rhythm/cut proof or
  `wan3_0` (`480p`, `5 cr.`) for photorealistic draft takes; reserve
  `cinematic_studio_video_4_0` (`480p`, `15 cr.`) for complex multi-ref pilots.
- **`R5` Final Master (`1080p`):** Upgrade only Director-approved unlocked
  shots using `cinematic_studio_video_4_0` / `seedance_2_5` (multi-ref hero
  shots) or `wan3_0_prime` / `veo3_1` (atmospheric single-subject shots).
