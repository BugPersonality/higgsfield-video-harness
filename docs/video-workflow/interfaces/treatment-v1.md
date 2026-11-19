# Creative Treatment & Style Bible V1

Phase 1 ([Creative Definition](../phases/creative-definition.md)) translates a
confirmed `campaigns/<slug>/intent.md` (`status: ready`) into two persistent
creative contracts: `campaigns/<slug>/treatment.md` (narrative arc, pacing, and
creative decisions) and `campaigns/<slug>/style-bible.md` (reusable visual,
lighting, motion, audio, and continuity grammar).

## Treatment Schema (`treatment.md`)

```markdown
# Treatment: <campaign title>

status: draft | ready | blocked
Intent: [intent.md](intent.md)
Brand: [<brand name>](../../brands/<brand>/brand.md)   <!-- omit if none -->
Style Bible: [style-bible.md](style-bible.md)
Blocked stop: <missing taste decision and owner; omit unless status: blocked>

## Design It Twice — Competing Creative Lanes

### Lane A — <pressure name> (Selected)
<Concise beat arc, shot cadence, visual and audio thesis, and why it wins against intent.md.>

### Lane B — <pressure name> (Steelman Rejected)
<Strongest honest case for the competing direction and the concrete intent/budget/continuity reason it was rejected.>

## Creative Decisions

### D1 — <decision topic>
- **Decision:** <selected creative rule>
- **Rejected:** <steelman alternative rejected>
- **Why:** <traceable rationale anchored to intent.md I<n>, brand truth, or credit envelope>
- **Reopen if:** <objective trigger that invalidates this choice>

## Beat-to-Shot Map

| Shot | Duration | Scale & Lens | Visual Action | Diegetic Audio Anchor | Score / VO Contour |
| --- | --- | --- | --- | --- | --- |
| `s01` | 5 s | ... | ... | ... | ... |

## Audio & Music Architecture

<Voiceover posture (enabled/disabled, tone, pacing words-per-second target), diegetic foley law, music contour, and ducking hierarchy.>

## Blocked Decisions

<!-- Include ONLY when status: blocked on a genuine requester taste fork -->
### B1 — <taste fork topic>
- **Option A:** <viewer-visible creative choice and trade-off>
- **Option B:** <contrasting creative choice and trade-off>
- **Why blocked:** <why intent.md I<n> and Priority / tie-breakers do not settle this fork>
- **Follow-up if A:** <conditional branch kept back until requester chooses A>
- **Follow-up if B:** <conditional branch kept back until requester chooses B>

## Carried Concerns

<!-- Optional: non-blocking risks forwarded to Production Design / QA -->
- <risk> — **Owner:** <phase/role> | **Closing action:** <check or fallback>
```

## Style Bible Schema (`style-bible.md`)

```markdown
# Style Bible: <campaign title>

status: draft | ready
Intent: [intent.md](intent.md)
Treatment: [treatment.md](treatment.md)
Brand: [<brand name>](../../brands/<brand>/brand.md)   <!-- omit if none -->

## Lighting & Color Temperature
<Key direction, Kelvin balance, ambient fill, atmosphere, and forbidden lighting clichés.>

## Palette & Material Fidelity
<Exact hex anchors, surface finishes, wardrobe palette, and material invariants.>

## Film Texture, Optics & Frame Rate
<Stock/grain aesthetic, focal-length progression across shots, shutter feel, and locked FPS.>

## Camera Grammar
<Single motivated movement per shot and explicit forbidden camera moves.>

## Audio Design & Level Law
<Raw clip diegetic rule (for example, `NO MUSIC. NO BACKGROUND SCORE.`), underscore brief, VO phonetic pronunciation table (when VO is enabled), and mix/loudness targets: master normalized with `loudnorm=I=-14:TP=-1.5:LRA=11`, verified by `qa_media.py render` at `-14 LUFS (±1.0 LU)` and true peak `<= -1.0 dBTP` (targeting `-1.5 dBTP` for headroom).>

## Negative Constraints & Anti-IP Phrasing
<Abstracted non-trademark visual descriptions replacing celebrity names, competitor marks, or IP-triggering brand terms.>

## Cross-Shot Continuity Checklist
<Numbered visual invariants verified by Visual Critic (`view_image`) across every still and contact sheet.>
```

## Candidate Proposal V1

During *Design It Twice*, each read-only `specialist-agent` lane advocates
strictly its assigned creative pressure without seeing or comparing sibling
lanes, returning one structured proposal:

```text
lane_pressure: <assigned creative pressure, e.g. Tactile Slow Cinema vs Rapid Editorial Montage>
concept_summary: <2-3 sentence narrative and emotional thesis>
beat_arc: <ordered shot-by-shot beats with approximate durations summing to target_duration_s>
visual_grammar: <lighting direction, palette anchors, framing/lens progression, camera movement>
audio_architecture: <diegetic foley plan, music contour, and VO cadence if enabled>
tradeoffs_accepted: <what viewer effect or craft dimension this lane intentionally trades away>
budget_posture: <estimated shot count and complexity impact relative to Draft cap / Final cap>
blocker_or_gap: <missing requester decision or infeasibility against intent.md, or none>
```

## Field Rules

- **Steelman rejection discipline:** every `D<n>` decision and every rejected
  *Design It Twice* lane must state the strongest honest case for the rejected
  alternative before stating why it lost against `intent.md` (`I<n>`, `Must not`,
  tie-breakers, or budget envelope). Do not invent strawman alternatives.
- **No premature CLI schema lock-in:** Creative Definition owns artistic and
  structural decisions (lighting, lenses, cadence, audio hierarchy, continuity
  rules). Exact live Higgsfield model IDs, CLI flags, and verified credit quotes
  belong to [Production Design](../phases/production-design.md) (`shotlist.json`).
- **Status discipline:** start both artifacts at `draft`; flip to `ready` only
  after fresh Treatment & Style Review (`reviewer-agent`) clears under
  [Creative Definition](../phases/creative-definition.md#treatment-and-style-review).
  Set `treatment.md` to `status: blocked` with `B1..Bn` strictly when an
  irreversible requester taste fork cannot be resolved from `intent.md`.
- **ID stability:** keep `D1..Dn` and shot IDs (`s01..sN`) stable across
  reopens so downstream `shotlist.json`, prompts, and receipts stay traceable.
