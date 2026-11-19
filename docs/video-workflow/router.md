# Workflow Router

Select the execution path and active production round for a video request. If
[`AGENTS.md`](../../AGENTS.md#direct-work) selects `Direct Work`, stop routing
here.

**No end-to-end autonomous mode exists.** Visual taste, casting charisma,
lighting feel, and cutting rhythm emerge when a human Director sees and hears
concrete work. Every production round (`R0` → `R5`) runs full technical craft
internally and terminates in a compact
[**Dailies Packet**](interfaces/dailies-packet-v1.md) for Director feedback
and explicit credit approval (`--round-cap`) before the next paid round starts.

## Terms

| Term | Meaning |
| --- | --- |
| `Direct Work` | Single-owner local execution under [`AGENTS.md`](../../AGENTS.md#direct-work) for one isolated deliverable (schema/balance check, doc/script edit, local `qa_media.py`/`assemble.sh`, or one standalone test asset after live cost confirmation) with no campaign folder, `brief.md`, or `taste-log.md`. |
| `Campaign` | One persisted multi-shot video project under `campaigns/<slug>/` with its own `brief.md`, `taste-log.md`, creative specs, live `shotlist.json`, spend ledger (`receipts.jsonl`), and gitignored `media/`. |
| `Dailies Packet` | The mandatory 4-block Director checkpoint ending every round (`R0`–`R5`): (1) single visual/readable artifact to inspect, (2) 1-line internal QC filter summary, (3) 2–3 jargon-free comparative taste questions, and (4) exact live Cost Ticket for the next round (`--round-cap`). Defined in [Dailies Packet V1](interfaces/dailies-packet-v1.md). |
| `Taste Memory` | Cumulative, append-only creative direction recorded in `campaigns/<slug>/taste-log.md` (`TL-01`, `TL-02`, ...) and seeded from/graduated to `brands/<brand>/taste.md`. Binding on every prompt and internal Visual Critic check (`TASTE_REGRESSION` if violated). Defined in [Taste Log V1](interfaces/taste-log-v1.md). |
| `LOCKED Asset` | Any Lookbook entity, keyframe still, audio stem, or video shot approved by the Director and marked `status: "LOCKED"` in `shotlist.json`. Immutable both in policy and mechanically in `scripts/hf_guard.py` (`asset_locked` refusal) unless explicitly unlocked by the Director. |
| `Campaign Cap` | Hard ceiling on total campaign credit spend declared in `campaigns/<slug>/brief.md` (`Budget & round policy`), validated against `shotlist.json` by `make campaign-check` and enforced across all rounds by `scripts/hf_guard.py`. |
| `Round Cap` | Mandatory cumulative per-round credit ceiling (`--round-cap <N>`) approved by the Director on the preceding Dailies Cost Ticket and passed to `scripts/hf_guard.py {preflight,run} --round <R2\|R3\|R4\|R4A\|R4B\|R5> --round-cap <N>`. Prevents runaway spend even when `Campaign cap` has headroom left. |
| `Still Animatic` | Zero-video-credit playable movie (`media/exports/animatic.mp4`) built in `R3` via `make animatic` (`scripts/assemble.sh --animatic`) combining stills at shot durations with VO and rough music so the Director judges framing, voice cadence, and cut rhythm before spending a single video credit. |
| `Risk-First Pilot` | Sub-round `R4A` shooting only `test_take_check != null` shots (grip, physics, legible text, reflection, comic timing, multi-subject blocking) at low-cost preview settings first so motion risk is proven or steered before fanning out batch video credits in `R4B`. |
| `Smart Zone` | Lean working-context envelope where each actor holds one coherent outcome, bounded files, and primary artifacts (`brief.md`, `taste-log.md`, `shotlist.json`) without attention degradation from prior chat history or unrelated shots. |

## Direct Work vs Feedback-Loop Studio

Choose the smallest path that honors meaning, visual consistency, and spending
control:

- **`Direct Work`** — one isolated deliverable with zero cross-shot continuity
  requirements: inspecting live schemas/balances/workspaces, editing harness
  docs/scripts/skills, running local `qa_media.py` or `assemble.sh` on existing
  files, or generating one standalone image or 5s test clip after echoing live
  `higgsfield generate cost` and getting explicit user confirmation.
- **Feedback-Loop Studio (`R0` → `R5`)** — mandatory for every multi-shot
  video, commercial, launch film, UGC sequence, or branded spot. Runs as an
  iterative loop between the **Director (Human)** and **Production Crew
  (Agents)** through `R0`–`R5`, never bypassing Dailies approval or spending
  credits without an approved `--round-cap`.

Re-route upward immediately from `Direct Work` into `R0` if a single test
clip expands into coordinated shots or repeated paid iterations.

## The 6 Production Rounds (`R0` → `R5`)

Traverse rounds in order. Inside each paid round, agents own 100% of technical
craft (schemas, prompting, parallel generation via `hf_guard.py`, `qa_media.py`,
and internal `reviewer-agent` defect filtering), then stop cleanly with a
**Dailies Packet**.

| Round | Playbook | Crew work inside the round | Dailies Packet shown to Director | Typical credits |
| --- | --- | --- | --- | --- |
| **R0 — Direction Seed** | [R0 Brief](rounds/r0-brief.md) | `evidence-agent` grounds in balance, workspace, `brands/*/brand.md`, `brands/*/taste.md`, and local photos; 3–5 meaning-only questions → `brief.md` (`active`) + seeded `taste-log.md` | **Dailies 0:** Short Direction Brief card + seeded taste anchors + `Campaign cap` sign-off | `0 cr.` |
| **R1 — Story & Cost Ticket** | [R1 Story & Cost](rounds/r1-story-and-cost.md) | **1A:** Commercial track (`[ad-references]` → `ad-concepts`, 4–5 swap-tested pitches) or 2–3 contrasting treatments.<br>**1B:** `ad-script` + `ad-storyboard` (`continuity_lock`, `test_take_check`) + `style-bible.md` + `evidence-agent` live CLI schemas & `generate cost` → `shotlist.json` (`make campaign-check`) | **Dailies 1A:** Pick/blend 1 of 4–5 pitches (commercial) or 2–3 treatments.<br>**Dailies 1B:** Readable story + **exact round-by-round Cost Ticket** (approves `R2`/`R3` `--round-cap`) | `0 cr.` |
| **R2 — Casting & World Lookbook** | [R2 Lookbook](rounds/r2-lookbook.md) | Parallel workers generate **2–3 contrasting variants (`A / B / C`)** per invented object/character/location via `hf_guard.py --round R2`; fresh `reviewer-agent` filters AI trash; `make lookbook` stitches `qc/lookbook.png` | **Dailies 2:** Single `lookbook.png` (`A / B / C`) + next-round Cost Ticket; pick/blend → upload & `LOCK` winning UUIDs | `~20–45 cr.` *(0 if skipped)* |
| **R3 — Keyframe Stills & Animatic** | [R3 Stills & Animatic](rounds/r3-stills-and-animatic.md) | Parallel workers generate `s01..sN` stills locked to `LOCKED` UUIDs + `continuity_lock` + `taste-log.md`; generate VO (`qa_media.py voice`, zero `atempo`) + rough music; internal Visual Critic filter; build `qc/stills_strip.png` + **0-video-credit `animatic.mp4`** | **Dailies 3:** `stills_strip.png` + playable `animatic.mp4` + `R4A` Cost Ticket; `LOCK` winning stills, re-roll ONLY rejected stills | `~30–50 cr.` *(0 video cr.)* |
| **R4 — Motion Dailies** | [R4 Motion Dailies](rounds/r4-motion-dailies.md) | **4A:** Shoot `test_take_check != null` pilot shot(s) at `480p`/`720p`/`--draft` + `qa_media.py clip` + internal Visual Critic.<br>**4B:** Parallel remaining unlocked shots + `make assemble` → `draft_cut.mp4` (`-14 LUFS`, `<= -1.0 dBTP`) | **Dailies 4A:** Pilot clip + `R4B` Cost Ticket.<br>**Dailies 4B:** Full `draft_cut.mp4` + **per-shot `1080p` upgrade prices** for `R5` | `~45–90 cr.` |
| **R5 — Final Master (`1080p`)** | [R5 Mastering](rounds/r5-mastering.md) | Upgrade ONLY approved shots to `1080p` via `hf_guard.py --round R5`; re-verify every clip with `qa_media.py clip` + Visual Critic; `make assemble` → `master.mp4` + `stems/` + `make qa-render`; optional `brain_activity` Virality Predictor | **Final Dailies 5:** `master.mp4` + `stems/` + final spend receipt + optional graduation of `taste-log.md` → `brands/<brand>/taste.md` | Approved final quote |

### Skip & Fast-Path Rules

Skip a round or sub-round ONLY when its exact observable condition holds:

- **Skip `R2` (Lookbook) automatically** when every hero object, character,
  and environment is already supplied as real reference photos under
  `campaigns/<slug>/media/references/` (`lookbook: []` in `shotlist.json`).
  Upload and verify those real photos directly at the start of `R3`.
- **Skip `ad-references` inside `R1A`** when the Director already brings a
  concrete creative angle or supplied reference spots; still run `ad-concepts`
  for commercial spots to verify swap-tested contrast.
- **Skip `R4A` pilot isolation** when zero shots in `shotlist.json` carry
  `test_take_check != null` AND the Director explicitly approves shooting all
  draft clips together on the `R3` Cost Ticket.
- **Never skip Dailies or internal QC.** Even on a 1–2 shot campaign, every
  executed round ends in a Dailies Packet, and every generated media asset
  passes `qa_media.py` + fresh `reviewer-agent` filtering before Dailies.

## Round Entry & Re-Entry Triggers

| Observable state | Active round / action |
| --- | --- |
| New campaign lacks `brief.md` at `status: active`, or core viewer meaning, brand truth, spoken pronunciation, taboos, or `Campaign cap` changed | [R0 — Direction Seed](rounds/r0-brief.md) |
| `brief.md` is `active`, but no Director-picked concept (`R1A`) or validated `shotlist.json` + live Cost Ticket (`R1B`) exists | [R1 — Story & Cost Ticket](rounds/r1-story-and-cost.md) |
| `shotlist.json` has unlocked `lookbook[]` entries (`status != LOCKED`) and `R2` `--round-cap` is approved | [R2 — Casting & World Lookbook](rounds/r2-lookbook.md) |
| All `lookbook[]` entities are `LOCKED` (or `R2` skipped), unlocked stills/audio remain, and `R3` `--round-cap` is approved | [R3 — Keyframe Stills & Animatic](rounds/r3-stills-and-animatic.md) |
| All stills are `LOCKED` (or pure T2V approved), unlocked draft shots remain, and `R4` `--round-cap` is approved | [R4 — Motion Dailies](rounds/r4-motion-dailies.md) |
| `draft_cut.mp4` approved on Dailies 4B and `R5` `1080p` `--round-cap` is approved | [R5 — Final Master](rounds/r5-mastering.md) |
| Director requests a change on one specific entity or shot while keeping other assets `LOCKED` | Stay in current round; run [Feedback Loop](shared/feedback-loop.md) + [Surgical Re-Iteration](shared/transition.md#surgical-single-asset-re-iteration) |

## Conditional Shared Protocols & Interfaces

Load a protocol or interface contract immediately before its trigger:

| Trigger | Reference |
| --- | --- |
| Translating Director reactions into `taste-log.md`, updating `LOCKED`/`ITERATING`, quoting micro re-rolls | [Feedback Loop](shared/feedback-loop.md) |
| Running light meaning-only alignment in `R0`/`R1` or resolving a taste fork | [Grilling](shared/grilling.md) |
| Filtering technical defects, `continuity_lock`, `test_take_check`, and `TASTE_REGRESSION` before Dailies | [Review](shared/review.md) |
| Enforcing `Campaign cap`, per-round `--round-cap`, `asset_locked`, `hf_guard.py`, and `receipts.jsonl` | [Budget Authority](shared/budget-authority.md) |
| Managing campaign folder layout, Git vs `media/` boundary, and status transitions | [Artifacts](shared/artifacts.md) |
| Handling round handoffs, surgical single-asset re-rolls, timeouts, HTTP 429, or `ip_detected` recovery | [Transition](shared/transition.md) |
| Authoring or checking campaign contracts | [Brief V1](interfaces/brief-v1.md), [Taste Log V1](interfaces/taste-log-v1.md), [Dailies Packet V1](interfaces/dailies-packet-v1.md), [Shotlist V1](interfaces/shotlist-v1.md), [Review Result V1](interfaces/review-result-v1.md) |
| Applying shared commercial craft vocabulary (`primary spot`, `swap test`, `mute test`, `Continuity lock`, `test-take check`) | [Ad Craft Glossary](../ad-craft-glossary.md) |
| Delegating to Codex Multi-Agent V2 roles and `view_image` / macOS `open` | [Agent Harness](../agent-harness.md) & [Codex Adapter](../agent-harness/codex.md) |
