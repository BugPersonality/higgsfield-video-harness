# Grilling

Streamlined, meaning-only alignment used in [R0 — Direction Seed](../rounds/r0-brief.md),
[R1 — Story & Cost Ticket](../rounds/r1-story-and-cost.md), and standalone
`grilling` skill invocations.

Unlike an upfront waterfall interrogation, the Feedback-Loop Studio does **not**
try to extract every visual nuance in chat before anything exists. Keep grilling
light and focused on **meaning, truth, taboos, and `Campaign cap`**—because
visual taste, casting feel, and cutting rhythm emerge much faster when the
Director reacts to real `A / B / C` Dailies in `R1A`–`R4`.

## Four-Bucket Classification

Classify every open question under
[Decision Ownership](../../../AGENTS.md#decision-ownership) before asking the
Director anything:

1. **Facts (resolve yourself via `evidence-agent`, never ask):** existing brand
   profiles (`brands/<brand>/brand.md`), graduated brand taste
   (`brands/<brand>/taste.md`), local reference photos in
   `campaigns/<slug>/media/references/`, active Higgsfield billing workspace
   (`higgsfield workspace list`), credit balance (`higgsfield account status`),
   and live CLI schemas / `generate cost`.
2. **Technical choices (owned by Crew, kept strictly OFF the frontier):**
   Higgsfield model or workflow IDs (`gpt_image_2_6`, `seedance_2_5`,
   `cinematic_studio_video_4_0`), `--mode omni_reference`, UUID wiring,
   still-to-video chaining, prompt syntax, anti-IP phrasing, FFmpeg filters,
   codecs, and `-14 LUFS` loudness normalization. Never ask the Director to pick
   models, flags, or codecs.
3. **Low-stakes reversible conventions (record as `Assumptions` in `brief.md`):**
   sensible defaults that preserve viewer meaning and are cheap to change later
   (for example `24 fps` filmic cadence when unspecified, subtle intro/outro
   audio fades, `Lookbook variants: 3`, `Max auto-retries/asset: 2`,
   `Auto-open dailies: true` on macOS). Record each with an objective
   `Reopen if:` trigger instead of grilling on trivia.
4. **Director-owned decisions (place ON the frontier):**
   - viewer takeaway and emotional effect;
   - target placement, aspect ratio, and approximate runtime;
   - non-negotiable subject, product, or brand truths (and whether real photos
     are supplied);
   - exact spoken pronunciation of brand/product names when voiceover is used;
   - hard `Must not` taboos;
   - genuine comparative creative forks (e.g., `R1A` pitch direction or
     voiceover vs silent/diegetic storytelling);
   - `Campaign cap` (hard total credit ceiling contextualized against live
     account balance).

## Light Rounds & Comparative Choices

- **3–5 highest-leverage questions max per round.** Order by pruning power
  first (meaning, subject truth, format/audio, taboos, `Campaign cap`). If the
  idea starts raw, open with one plain question inviting the concrete viewer
  moment in the Director's own words.
- **Plain numbered text for rapid replies** (`1 yes, 2 B, 3 cap 360`) so the
  Director can answer or steer in seconds.
- **Prevent yes-bias with comparative `A / B` forks:**
  - *Supported default (`Q1`)* — when brand files or low-regret conventions
    strongly favor one option, state the recommendation and explicitly name
    what is traded away if accepted.
  - *Balanced or high-stakes fork (`Q2`)* — for `Campaign cap`, voiceover vs
    visual-only, or major creative tone forks, never nudge toward `"yes"`;
    present 2–3 concrete viewer-facing options (`A / B`) and ask for an
    explicit pick.

```text
❓ **Q1** - **<supported-default title>**: <concise context and concrete viewer tradeoff>

➡️ <recommended choice, one-line rationale, and what is given up if accepted>

---

❓ **Q2** - **<balanced or high-stakes fork title>**: <concise context>
- **A:** <option and concrete viewer or budget consequence>
- **B:** <option and concrete viewer or budget consequence>

➡️ Pick **A** or **B** (or blend/specify another rule).
```

## Unbound Qualifier Killer

Subjective adjectives mean opposite things to different viewers. Never write an
unbound adjective into `brief.md` as if it were a concrete direction—either
ground it with one quick `A / B` question in `R0` or defer visual calibration
explicitly to contrasting `A / B / C` variants in `R2` Lookbook:

| Unbound qualifier | Ground into concrete viewer reality |
| --- | --- |
| `"cinematic"` | Natural directional daylight vs moody tungsten shadows; unhurried tripod holds vs kinetic handheld motion; organic film grain vs crisp modern glass. |
| `"premium"` | Quiet matte-material restraint (negative space, tactile texture, sparse score) vs glossy luxury spectacle (high-spec reflections, dramatic montage). |
| `"dynamic"` | Fast rhythmic cut pace (`1.5–2.5 s` beats) vs continuous physical subject motion inside longer takes. |
| `"high quality"` | Checkable pause-frame truths: true-to-reference product finish, natural hands, legible wordmark, clean foley without music muddiness. |
| `"modern"` / `"viral"` | Concrete first-2-seconds scroll-stop hook (muted visual curiosity vs sound-on narration hook) and explicit clichés banned in `Must not`. |

## Partial Replies, Contradictions & Crisp Exit

- **Skipped question:** silence is never `"yes"`. Either re-surface the one
  skipped blocker or ask explicitly whether to convert it into a labeled
  assumption in `brief.md`.
- **Delegation:** if the Director says *"your call on music mood as long as it
  stays calm"*, record that exact guiding bound in `brief.md` (`Preferences &
  tie-breakers`) or `taste-log.md` (`TL-01`) and echo it in one line.
- **Contradiction detection:** if a requested scope conflicts with `Campaign
  cap` or `brand.md` (for example, 10 bespoke shots inside a 120-credit cap),
  surface the conflict immediately with concrete options (`A`: trim to 3–4
  shots, `B`: raise `Campaign cap`) instead of guessing.
- **Exit fast into tangible artifacts:** as soon as meaning, subject truth,
  taboos, and `Campaign cap` are settled, stop grilling, confirm **Dailies 0**
  (`brief.md` → `status: active`, `make brief-check`), and move straight into
  concrete story options in [R1](../rounds/r1-story-and-cost.md).
