# Grilling

Interview the requester **relentlessly** in structured rounds until you reach
**shared understanding** on what the video must communicate, preserve, and cost.
Map the campaign as a **design tree**: every settled choice opens or prunes the
branches hanging off it.

## Four-Bucket Classification

Classify every branch under [Decision Ownership](../../../AGENTS.md#decision-ownership)
before putting a single question in front of the requester:

1. **Facts (resolve yourself, never ask):** existing brand profiles in
   `brands/`, reference photos in `campaigns/<slug>/media/references/`, live
   Higgsfield CLI models/workflows/voices (`higgsfield model list`,
   `higgsfield voices list`), active billing workspace, credit balance, and
   verified credit costs (`higgsfield generate cost`). Dispatch a fresh
   `evidence-agent` for read-heavy discovery before Round 1 so the root session
   stays in the **Smart Zone** and premise conflicts surface immediately.
2. **Technical choices (owned by agents, kept strictly OFF the frontier):**
   Higgsfield model IDs (`gpt_image_2_6`, `seedance_2_5`,
   `cinematic_studio_video_4_0`), `--mode`, `omni_reference` wiring, still-to-I2V
   chaining, prompt phrasing mechanics, anti-IP wording, FFmpeg filter graphs,
   codec bitrates, and `-14 LUFS` loudness filters. Never ask the requester to
   pick models, flags, or codecs.
3. **Low-stakes reversible conventions (record as `A<n>` assumptions):**
   platform-neutral defaults that preserve viewer meaning and are cheap to
   adjust later (for example `24 fps` filmic cadence when unspecified, subtle
   intro/outro audio fade length, or stem folder layout). Record each as a
   labeled assumption (`A<n>`) with an objective `Reopen if:` trigger for Gate 1
   confirmation instead of grilling on trivia.
4. **Requester-owned decisions (place ON the frontier):** viewer emotional
   effect, target placement and aspect ratio, subject/product/character truth
   invariants, exact spoken brand/product pronunciation, voiceover vs purely
   visual storytelling, `Must not` taboos, genuine creative taste forks,
   `Autonomy mode` (`autonomous-draft` vs `checkpointed`), `Draft cap`,
   `Final cap`, `Max auto-retries/shot`, and priority tie-breakers.

## Paced Rounds And Anti-Yes-Bias

Work the **design tree** in **rounds**. The **frontier** is every
requester-owned decision whose prerequisites are settled. When the initial idea
is raw or vague, open with one open-ended question inviting the concrete viewer
situation and desired reaction in the requester's own words. Otherwise:

- **Prioritize and pace:** order questions by pruning power and spend blast
  radius first (viewer purpose, placement/aspect/duration, subject/brand truth,
  budget envelope and autonomy mode) before finer visual or audio preferences.
  Ask **3–5 highest-leverage questions per round**, grouped by theme. When
  additional independent branches remain, append a one-line preview naming the
  queued topics so the user sees progress without facing a wall of text.
- **Plain-text numbered rounds:** write rounds in plain chat text numbered for
  rapid replies (`1 yes, 2 B, 3 150/300`) so the user can qualify answers or
  steer naturally.
- **Prevent yes-bias:**
  - *Supported default (`Q1`)* — when brand rules or low-regret conventions
    strongly favor one choice, phrase the question so `"yes"` accepts the
    recommendation and explicitly name what is given up.
  - *Balanced or high-stakes fork (`Q2`)* — for money/credit caps, autonomy
    mode, voiceover vs silent/diegetic, taste forks, or irreversible brand
    choices, never nudge toward `"yes"`; present 2–3 concrete options (`A` / `B`)
    with clear viewer or budget consequences and ask for an explicit choice.

```text
❓ **Q1** - **<supported-default title>**: <concise context anchor and concrete viewer tradeoff>

➡️ <recommended choice, one-line rationale, and what is given up if accepted>

---

❓ **Q2** - **<balanced or high-stakes fork title>**: <concise context anchor>
- **A:** <option and concrete viewer or budget consequence>
- **B:** <option and concrete viewer or budget consequence>

➡️ Balanced choice — pick **A** or **B** (or specify another rule).
```

## Unbound Qualifier Killer

Video briefs frequently use subjective adjectives that cause two fresh creative
teams to produce opposite films. Never accept an unbound qualifier into
`intent.md` as if it were a specification; immediately ground it into concrete
viewer scenarios or an explicit bounded delegation:

| Unbound qualifier | Ground into concrete viewer reality |
| --- | --- |
| `"cinematic"` | Ask what the viewer actually feels and sees: natural directional daylight vs high-contrast moody tungsten, slow 4–5 s tripod holds vs kinetic handheld motion, 35mm organic grain vs ultra-clean commercial glass. |
| `"premium"` | Separate quiet matte-material restraint (negative space, diegetic texture, sparse acoustic score) from glossy luxury spectacle (high-spec reflections, rapid prestige montage, dramatic swell). |
| `"dynamic"` | Distinguish fast rhythmic edit cuts (1.5–2.5 s beats) from kinetic subject motion inside longer single-take shots, and check compatibility with `Draft cap`. |
| `"high quality"` | Translate into checkable pause-frame invariants: true-to-reference product finish, zero distorted hands or typography, locked FPS, clean foley without music bleed. |
| `"modern"` / `"viral"` | Anchor to a concrete first-2-seconds hook scenario (muted feed scroll-stop vs sound-on narration hook) and name what clichés fall under `Must not`. |

## Handling Partial Replies, Contradictions, And Exit

Wait for the requester's replies before advancing dependent branches:

- **Skipped question:** silence in a partial reply is **never** `"yes"`.
  Re-surface the skipped branch or explicitly ask whether to convert it into a
  labeled assumption (`A<n>`) or delegated decision.
- **Delegation vs. vagueness:** if the user explicitly delegates ("your call on
  camera movement as long as it feels calm and unhurried"), record the exact
  guiding bound under `Preferences & delegated choices` in
  [Video Intent V1](../interfaces/intent-v1.md) and echo it in one sentence.
- **Contradiction detection:** if a new answer conflicts with a previously
  settled branch, brand profile rule, or credit ceiling (for example, requesting
  eight distinct locations inside a 100-credit `Draft cap`), stop immediately
  and surface the exact conflict so the user resolves which constraint bends—
  never silently overwrite or keep both.
- **Natural wrap-up:** if the requester asks to wrap up and assume the rest,
  convert remaining low-stakes branches into labeled `A<n>` assumptions with
  `Reopen if` triggers while still obtaining explicit numbers for hard
  [Authority](../../../AGENTS.md#authority) fields (`Autonomy mode`,
  `Draft cap`, `Final cap`, `Max auto-retries/shot`).

Grilling finishes when the **frontier** is empty: every requester-owned branch
is settled, delegated with bounds, or recorded as an explicit assumption ready
for Gate 1 confirmation in [Intake](../phases/intake.md).
