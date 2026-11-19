# Dailies Packet V1

Every production round (`R0`–`R5`, including `R1A`, `R1B`, `R4A`, `R4B`) ends
with one compact **Dailies Packet** presented by the Root Producer to the human
Director. **There is no autonomous bypass:** the Production Crew never starts a
paid round without the Director's feedback and explicit `--round-cap` approval
on the preceding Dailies Packet.

## The 4 Mandatory Blocks

Every Dailies Packet contains exactly four scannable blocks in this order:

1. **What to inspect**
   - Present **one** consolidated visual or readable artifact for the round
     (never dump raw folders of intermediate files or prompt logs):
     - `R0`: Short Direction Brief card (`campaigns/<slug>/brief.md`) + seeded
       brand taste summary.
     - `R1A`: 4–5 contrasting plain-language pitches (`A / B / C / D [/ E]`) on
       the commercial track, or 2–3 contrasting treatments on the non-commercial
       track.
     - `R1B`: Readable story beat-by-beat (`script.md` / `storyboard.md`) +
       round-by-round price overview.
     - `R2`: Single labeled Lookbook comparison grid (`campaigns/<slug>/qc/lookbook.png`).
     - `R3`: Storyboard stills strip (`campaigns/<slug>/qc/stills_strip.png`) +
       playable 0-video-credit Still Animatic (`campaigns/<slug>/media/exports/animatic.mp4`).
     - `R4A`: Risk-First Pilot clip (`campaigns/<slug>/media/shots/sNN-*.mp4`).
     - `R4B`: Full edited Draft Cut (`campaigns/<slug>/media/exports/draft_cut.mp4`).
     - `R5`: Final Master (`campaigns/<slug>/media/exports/master.mp4`) +
       separated `media/exports/stems/` + complete spend audit.
   - **Auto-preview on macOS:** when `Auto-open dailies: true` in `brief.md` and
     running interactively on macOS (`Darwin`), execute `open <artifact>` right
     before posting the packet and note *"Opened locally for review."* See
     [Codex Adapter](../../agent-harness/codex.md#macos-open-dailies-previewing).
2. **Filtered internally**
   - **One line** summarizing defective takes or `TASTE_REGRESSION`s caught and
     replaced internally by `qa_media.py` and `reviewer-agent` before Dailies
     (for example: *"Filtered 1 extra-finger variant on Entity B and 1 frozen-end
     pilot take internally; only clean options shown."*).
   - If zero retries occurred, state *"All generated options passed internal QC
     on the first pass."*
   - If a borderline `CONCERN` survived after hitting `Max auto-retries/asset`,
     surface it honestly here in one plain sentence—never hide a real defect.
3. **Comparative taste questions**
   - **2–3 plain-language questions** inviting comparative picks (`A / B / C`),
     blends (*"A's lighting with C's camera distance"*), or visceral reactions
     (*"Does shot 2 feel heavy enough, or too rushed?"*).
   - **Zero technical jargon:** never mention model IDs (`gpt_image_2_6`,
     `cinematic_studio_video_4_0`), CLI flags, `--mode omni_reference`, UUIDs,
     prompt syntax, codecs, `loudnorm`, or FFmpeg filter strings.
4. **Cost ticket**
   - Exact numbers from `scripts/hf_guard.py status` and live
     `higgsfield generate cost`:
     - **Spent so far:** `<X>` credits
     - **Remaining `Campaign cap`:** `<Y>` of `<Cap>` credits
     - **Next round (`R<next>`) exact live quote:** `<Q>` credits (itemized by
       plain entity/shot names, plus recommended `--round-cap` including retry
       headroom if applicable; on `R4B`, show **per-shot `1080p` upgrade prices**)
     - **Explicit approval ask:** clear go/no-go question authorizing
       `--round-cap <N>` for the next single round (or confirming a small
       micro-cost for surgical re-rolls inside the current round).

## Canonical Packet Template

```markdown
### Dailies 2 — Casting & World Lookbook

**1. What to inspect**
- Lookbook grid (`A / B / C`): `campaigns/<slug>/qc/lookbook.png` *(opened locally)*

**2. Filtered internally**
- Filtered 1 warped-handle variant on the leather bag internally; all three options shown are clean.

**3. Comparative taste questions**
1. Which bag silhouette and leather texture feels most unmistakably like the brand—**A** (matte, softer slouch), **B** (structured architectural corners), or **C** (heavier aged grain)—or a blend of two?
2. For the railway concourse morning light, do you prefer **A** (cooler limestone mist) or **B** (warmer low sun shafts)?
3. Is there anything across A/B/C we should rule out permanently ("Never") before drawing the storyboard frames?

**4. Cost ticket — Next round: R3 (Keyframe Stills, Rough Music & Still Animatic)**
- **Spent so far:** 30 credits
- **Remaining Campaign cap:** 330 of 360 credits
- **R3 live quote:** 40 credits (3 keyframe stills @ 10 cr. + 15s music bed @ 10 cr.; Still Animatic = 0 cr.)
- **Proposed R3 `--round-cap`:** 50 credits *(includes 10 cr. internal defect-retry headroom)*

Reply with your picks/steers and confirm **Go for R3 (up to 50 cr.)**, or tell me which option(s) to re-roll first (10 cr. per re-rolled option).
```

## Anti-Jargon Guardrails

Before emitting any Dailies Packet, verify:

- Every question asks about **viewer experience** (emotion, casting presence,
  light, framing, texture, voice warmth, pacing)—never implementation mechanics.
- Only **one** primary visual/playable artifact is pushed into the Director's
  focus per round (`R3` pairs the strip + animatic as one cohesive storyboard
  review).
- The Cost Ticket authorizes **at most the next single round** (`--round-cap`),
  never an open-ended multi-round blank check.
- Reactions are immediately logged via
  [Feedback Loop](../shared/feedback-loop.md) into `taste-log.md` and
  `shotlist.json` before any further spend.
