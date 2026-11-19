# Direction Brief V1

`campaigns/<slug>/brief.md` is the lightweight, meaning-only campaign charter
authored in [R0 — Direction Seed](../rounds/r0-brief.md), owned exclusively by
the Root Producer, and validated mechanically by `make brief-check CAMPAIGN=<slug>`
(`scripts/check-brief.py`).

A brief captures **what the film means, must preserve, must avoid, and may cost**—never
model IDs, CLI flags, prompt recipes, UUIDs, codecs, or FFmpeg commands. Fine
visual taste evolves inside [`taste-log.md`](taste-log-v1.md) as the Director
reacts to concrete Dailies across `R1`–`R5`.

## Required Structure

Every `campaigns/<slug>/brief.md` MUST contain:

1. **H1 title:** `# Brief: <title>`
2. **Lifecycle status line:** `status: draft | active | done`
3. **Five required H2 sections:**
   - `## Purpose & viewer effect`
   - `## Subject & visual truth`
   - `## Format, audio & delivery`
   - `## Constraints & boundaries`
   - `## Success signal`
4. **Three required subsections/blocks inside `## Constraints & boundaries`:**
   - `Must not` — visual taboos, forbidden tropes, prohibited claims, or brand
     red lines.
   - `Budget & round policy` — four exact machine-parsed policy fields:
     - `Campaign cap: <N> credits` — hard total credit ceiling across all rounds
       (`R2`–`R5`, retries, and surgical re-rolls).
     - `Lookbook variants: <1..4>` — contrasting options (`A / B / C`) generated
       per invented Lookbook entity in `R2` (typically `3`; integer `1..4`).
     - `Max auto-retries/asset: <K>` — maximum internal QC auto-retries per
       entity/shot inside a round before escalating or surfacing transparently.
     - `Auto-open dailies: true | false` — whether the Root Producer runs macOS
       `open <artifact>` when presenting each visual Dailies Packet.
   - `Scope & non-goals` — explicit boundaries keeping the campaign focused.

### Optional H2 Sections

Include only when useful to preserve settled context across rounds:

- `## Settled meaning` — crisp numbered decisions settled in `R0` grilling.
- `## Concrete viewer scenarios` — 1–3 concrete scroll-stop or viewing moments.
- `## Preferences & tie-breakers` — priority ordering when visual beauty,
  pacing, and cost compete (for example: *"product material truth beats
  dramatic camera motion"*).
- `## Assumptions` — reversible defaults formatted as `- **A<n> ...**` paired
  with an objective `Reopen if:` trigger.
- `## Open questions` — every item specifies `Owner:`, `Fallback:`, and
  `Reopen if:`. Director/requester-owned open questions are permitted **only**
  while `status: draft` and must be resolved before flipping to `status: active`
  (agent/craft-owned questions with an explicit fallback may remain).

## Canonical Template

```markdown
# Brief: <Campaign Title>

status: active

## Purpose & viewer effect

- **Viewer takeaway:** <What the viewer should feel, remember, and do after watching.>
- **Target audience & placement:** <Who is watching and where the spot runs.>

## Subject & visual truth

- **Brand profile:** `brands/<brand>/brand.md` *(optional)*
- **Brand taste seed:** `brands/<brand>/taste.md` *(optional)*
- **Hero subject & invariants:** <Physical product, character, material finish, color, and logo/wordmark truths that must never drift.>
- **Supplied reference photos:** <Exact filenames in `media/references/`, or `none — cast and design in R2 Lookbook`.>

## Format, audio & delivery

- **Aspect ratio & runtime:** <e.g., 16:9 widescreen, 15s (3 beats)>
- **Audio & voiceover:** <Spoken language, exact phonetic pronunciation for brand/product names, voice feel, diegetic sound, or visual-only with music.>
- **Deliverables:** `media/exports/master.mp4` + `media/exports/stems/`

## Constraints & boundaries

- **Must not:** <Taboos, forbidden clichés, glossy glare, distorted typography, competitor lookalikes.>
- **Budget & round policy:**
  - **Campaign cap:** 360 credits
  - **Lookbook variants:** 3
  - **Max auto-retries/asset:** 2
  - **Auto-open dailies:** true
- **Scope & non-goals:** <Explicit exclusions, e.g., no on-screen legal fine print, single language version.>

## Success signal

- <Concrete, observable viewer criteria proving the film works on mute and with sound.>

## Preferences & tie-breakers

- <Example: Physical material honesty and legible wordmark outrank dramatic camera sweeps.>

## Assumptions

- **A1:** 24 fps filmic cadence unless Director requests 30 fps. *Reopen if:* platform spec requires 30/60 fps.
```

## Status Lifecycle

| Status | Meaning | `hf_guard.py` behavior |
| --- | --- | --- |
| `draft` | Under R0 grounding and light alignment; may still contain `## Open questions`. | Refuses all paid calls. |
| `active` | Confirmed by the Director at Dailies 0; passes `make brief-check CAMPAIGN=<slug>`; `Campaign cap` and round policy are live. | Permits paid calls **only** when combined with an explicit per-round `--round-cap` approved at Dailies. |
| `done` | Final Master (`R5`) approved by the Director and final spend audited. | Refuses further paid calls unless reopened to `active` by the Director. |

## Mechanical Validation

Run `make brief-check CAMPAIGN=<slug>` (`scripts/check-brief.py`) after creating
or editing `brief.md`, and run `make campaign-check CAMPAIGN=<slug>`
(`scripts/check-campaign.py`) once `taste-log.md` and `shotlist.json` exist:

- Verifies `# Brief: <title>` and valid `status: draft | active | done`.
- Verifies all five required H2 sections exist with non-empty content and zero
  unresolved template placeholders (`<...>`) when `status: active` or `done`.
- Verifies `Must not`, `Scope & non-goals`, and all four `Budget & round policy`
  fields (`Campaign cap` > 0, `Lookbook variants` in `1..4`,
  `Max auto-retries/asset` >= 0, `Auto-open dailies` boolean).
- Rejects `status: active` or `done` if `## Open questions` still contains any
  Director/requester-owned open question, validates `A<n>` + `Reopen if:` on
  `## Assumptions`, and warns on ungrounded subjective qualifiers.
