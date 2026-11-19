# Taste & Direction Log V1

`campaigns/<slug>/taste-log.md` is the campaign's **cumulative Taste Memory**.
Every Director reaction across `R0`–`R5` is distilled into structured, binding
rules so the Production Crew never drifts back toward rejected aesthetics or
forgets why an option won.

Only the Root Producer writes to `taste-log.md`. Every creative specialist
(`specialist-agent`), prompt author, and internal pre-Dailies QC pass
(`reviewer-agent`) MUST read `taste-log.md` before acting. Violating an active
rule in `taste-log.md` (or its cited `brands/<brand>/taste.md`) is classified
as a blocking [`TASTE_REGRESSION`](review-result-v1.md#closed-video-defect-taxonomy).

## Required Structure

1. **H1 title:** `# Taste Log: <title>`
2. **Optional brand seed header:** `Brand taste seed: brands/<brand>/taste.md`
   (when the campaign belongs to a brand with graduated taste memory; summarize
   inherited brand taste in an optional `## Inherited Brand Taste` section).
3. **Append-only chronological entries** using the exact H3 heading format:
   `### TL-<NN> (R<k> — <stage>)`
   - `<NN>` is a stable zero-padded sequential integer (`01`, `02`, `03`, ...).
   - `R<k>` names the round (`R0`, `R1A`, `R1B`, `R2`, `R3`, `R4A`, `R4B`, `R5`).
   - `<stage>` names the concise Dailies beat (for example `Seed`,
     `Concept Pick`, `Lookbook`, `Stills & Animatic`, `Pilot`, `Draft Cut`,
     `Master`).
4. **Four structured fields inside every `TL-<NN>` entry:**
   - **Approved / LOCKED:** exact assets, concepts, or visual anchors approved
     in this round (or `none`).
   - **More of:** positive aesthetic, pacing, lighting, casting, or sound traits
     the Director responded to and wants amplified downstream.
   - **Change / Steer:** specific directional corrections for unlocked/iterating
     assets (translated from natural language into observable visual/audio
     reality, free of CLI jargon).
   - **Never:** ruled-out aesthetics, lighting styles, pacing traps, or tropes
     that must not reappear in any downstream prompt or take.

## Canonical Example

```markdown
# Taste Log: Nord Atelier Autumn Spot

Brand taste seed: brands/example-brand/taste.md

## Inherited Brand Taste

- Quiet matte-material restraint over glossy studio luxury.
- Cool Nordic daylight (~4600K–6200K) with real tactile grain; never neon rim light.

### TL-01 (R0 — Seed)

- **Approved / LOCKED:** Direction brief (`brief.md` active); real product photos (`ref_bag_front`, `ref_clasp_macro`, `ref_bag_profile`).
- **More of:** Tactile stillness, natural morning light on stone and leather, unhurried confidence.
- **Change / Steer:** Keep the traveler anonymous—hands, coat sleeve, silhouette only.
- **Never:** Glossy studio sweeps, flashy luxury transitions, spoken hard-sell taglines.

### TL-02 (R1A — Concept Pick)

- **Approved / LOCKED:** Pitch B ("Weight of Real Brass" — silent morning concourse sequence).
- **More of:** Sound of the brass clasp carrying the emotional turn; generous negative space.
- **Change / Steer:** Slow the middle bench lift slightly so the leather weight reads physically.
- **Never:** Fast montage cuts under 2.5 seconds; upbeat pop score.

### TL-03 (R3 — Stills & Animatic)

- **Approved / LOCKED:** `s01.still` (`LOCKED`), `s03.still` (`LOCKED`), rough solo cello score (`LOCKED`).
- **More of:** Soft limestone shadow roll-off from `s01`; warm saddle leather tone against charcoal wool.
- **Change / Steer:** Re-roll `s02.still` (`ITERATING` v2) — pull camera 20% wider so the whole bench and right-hand grip read clearly without cropping the bag edge.
- **Never:** Tight cropped hands where the brass clasp disappears out of frame.
```

## Append-Only & Superseding Rules

- **Never delete or silently rewrite prior `TL-<NN>` entries.** Chronological
  history explains *why* current anchors exist and prevents oscillating between
  rejected styles.
- **Explicit superseding:** if the Director later reverses an earlier steer
  (for example, deciding in `R4B` to add a warm sunset grade after earlier
  preferring cool morning light), append a new `TL-<NN>` entry stating
  `Supersedes TL-02 on lighting temperature: ...` so downstream actors follow
  the newest binding rule without ambiguity.
- **Plain observable craft language:** capture what the viewer sees and hears
  (light direction, texture, lens closeness, rhythm, vocal warmth), never raw
  prompt tags or CLI parameters.

## Graduation To Brand Taste Memory

At **Final Dailies 5** ([R5 Mastering](../rounds/r5-mastering.md)), the Root
Producer proposes graduating durable, cross-campaign learnings from
`campaigns/<slug>/taste-log.md` into `brands/<brand>/taste.md`:

- **Graduate (only with explicit Director confirmation):**
  - Durable visual signatures (lighting palette, material honesty, framing
    restraint, camera energy) that define the brand across spots.
  - Persistent casting, wardrobe, or voiceover texture preferences.
  - Hard brand-wide `Never` rules discovered through real visual reactions.
- **Leave campaign-local in `campaigns/<slug>/taste-log.md`:**
  - One-off story plot beats, seasonal locations, temporary props, or
    shot-specific fixes (`"pull s02 20% wider"`).
- **Attribution:** record the source campaign slug and date when appending
  graduated bullets to `brands/<brand>/taste.md` so future `R0` groundings know
  where each taste anchor originated.
