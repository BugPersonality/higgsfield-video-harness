# Phase 1 — Creative Definition

Use once `campaigns/<slug>/intent.md` is confirmed at `status: ready` and the
campaign lacks reviewed `treatment.md` and `style-bible.md`. Runs in a fresh
phase session (`fork_turns: "none"`) with zero prior chat history.

Creative Definition translates requester meaning into a coherent directorial
treatment, beat-to-shot narrative arc, lighting/palette/camera grammar, and
audio architecture—without locking premature CLI flags that belong to Phase 2.

## Steps

1. **Read authoritative inputs cold.**
   - Read `campaigns/<slug>/intent.md` (`status: ready`), any cited
     `brands/<brand>/brand.md`, and inspect the list of local reference files
     under `campaigns/<slug>/media/references/` (using `view_image` on
     reference photos when product or character detail shapes framing).
   - Extract every `Binding: hard` decision (`I<n>`), `Must not` rule,
     `Priority / tie-breakers`, and the `Draft cap` / `Final cap` envelope that
     bounds shot count and complexity.

2. **Run the track matching the campaign.**

   - **Track A — Commercial & product spots** (governed by shared vocabulary in
     [`docs/ad-craft-glossary.md`](../../ad-craft-glossary.md)):
     1. *Optional `ad-references` (via fresh `evidence-agent`):* run when real
        aired or published **primary spots** and **transferable mechanisms** are
        needed to replace vague mood adjectives with observable screen/audio
        cause-and-effect rules.
     2. *`ad-concepts`:* develop orthogonal, **product-locked** premises running
        on distinct **dramatic engines** and stress-test every candidate with
        the adversarial **swap test** (substituting the closest direct
        competitor and an adjacent product to prove which physical beat breaks).
        *Design It Twice* `specialist-agent` lanes (`fork_turns: "none"`,
        `reasoning_effort: high`) may propose competing premises under
        contrasting creative pressures before convergence.
     3. *`ad-script` (`campaigns/<slug>/script.md`):* turn the chosen premise
        into a timed **three-column script** (`Time | Video | Audio`) with
        explicit **earned pauses** (`[PAUSE Ns]`), audited against the
        **read-aloud budget** (`<= 2.0 words/sec` in Russian and other
        longer-word languages, `<= 2.3 words/sec` in English, `<= 4.5
        syllables/sec` baseline) and passing the **mute test** (`Verdict: PASS`
        — core product claim proven in the `Video` column alone).
     4. *`ad-storyboard` (`campaigns/<slug>/storyboard.md`):* convert
        `script.md` into a top-level **Continuity Lock** (Product, Lighting &
        palette, Space/cast/active hand/180-degree axis) and numbered shots
        (`S01..SN`) specifying `Focal entry`, observable `Start frame` /
        `Action` / `End frame`, `Cut trigger` (**motivated cut** + 30-degree
        rule), `Audio sync`, and a **`Test-take check`** (exact failure mode +
        observable pass check) strictly on risky shots, closed with a
        cut-by-cut continuity audit.

   - **Track B — Non-commercial / pure aesthetic spots (*Design It Twice*):**
     - Spawn **2–3 fresh read-only `specialist-agent` lanes**
       (`fork_turns: "none"`, `reasoning_effort: high`) in parallel under
       genuinely competing creative pressures tailored to the brief—for example:
       - *Lane A — Tactile Slow Cinema:* minimal shot count, longer 4–5 s beats,
         single continuous space, strong material fidelity and generous retry
         margin;
       - *Lane B — Kinetic Editorial / Hook-First:* faster beat progression,
         stronger visual contrast, sharper opening scroll-stop energy;
       - *Lane C (optional) — Intimate Human / Context Story:* subject
         experienced through lived human gesture, environment storytelling, or
         spoken cadence.
     - Each specialist advocates strictly its assigned pressure against
       `intent.md` without seeing sibling lanes, returning
       [Candidate Proposal V1](../interfaces/treatment-v1.md#candidate-proposal-v1)
       and surfacing any infeasibility or missing requester choice in
       `blocker_or_gap`.

3. **Distill into `treatment.md` and `style-bible.md` (`status: draft`).**
   - Always converge both tracks into `campaigns/<slug>/treatment.md` and
     `campaigns/<slug>/style-bible.md` conforming to
     [Creative Treatment & Style Bible V1](../interfaces/treatment-v1.md):
     - document the chosen direction and a steelman summary of each rejected
       alternative (`ad-concepts` runners-up or competing *Design It Twice*
       lanes) weighed strictly against `intent.md` (`Binding: hard` rules,
       `Concrete viewer scenarios`, `Priority / tie-breakers`, cross-shot
       consistency risk, and credit headroom);
     - record every material creative choice as `D1..Dn` (`Decision`,
       `Rejected`, `Why`, `Reopen if`);
     - lock the Beat-to-Shot Map (`s01..sN`, durations summing to
       `target_duration_s`, scale/lens, visual action, diegetic anchor, score
       or VO contour);
     - lock `style-bible.md`: when `storyboard.md` exists, inherit its
       three-part **Continuity Lock** (Product, Lighting & palette, Space/cast/
       active hand/180-degree axis) verbatim alongside film texture, motivated
       camera grammar, raw-clip `NO MUSIC. NO BACKGROUND SCORE.` audio law,
       phonetic VO pronunciation table (when VO is enabled), anti-IP visual
       phrasing rules, and the numbered Cross-Shot Continuity Checklist for
       Visual Critic QA.

4. **Run fresh Treatment & Style Review.**
   - Dispatch one fresh read-only `reviewer-agent` (`fork_turns: "none"`,
     `reasoning_effort: high`) running
     [Treatment And Style Review](#treatment-and-style-review) under
     [Review](../shared/review.md).
   - Pass strictly `intent.md`, cited `brands/` profile, `treatment.md`,
     `style-bible.md`, and—when produced on the commercial track—`script.md`
     and `storyboard.md` (omit specialist chat transcripts and author
     persuasion).
   - On `FAIL`, verify each anchored finding, repair affected Phase 1 artifacts
     in place (at most 2 bounded repair rounds), and re-verify with a fresh
     reviewer.

5. **Emit `status: ready` or `Blocked Exit` (genuine taste fork only).**
   - **Blocked Exit rule:** emit `treatment.md` at `status: blocked` with
     `B1..Bn` under [Blocked Exit](../shared/transition.md#blocked-exit) ONLY
     when two genuinely competing creative directions tie against `intent.md`
     and represent an irreversible requester taste fork (or when a
     `Binding: hard` constraint is infeasible inside the brief). Never block on
     routine craft choices like lens focal length or lighting fill ratio.
   - Otherwise flip `treatment.md` and `style-bible.md` to `status: ready` and
     return [Transition Result V1](../shared/transition.md#transition-result-v1)
     naming [Production Design](production-design.md) as `next_owner`.

## Treatment And Style Review

Read-only review adapter for fixed `campaigns/<slug>/treatment.md` and
`campaigns/<slug>/style-bible.md` (`status: draft`). Return
[Review Result V1](../interfaces/review-result-v1.md):

1. **Intent & brand fidelity:** verify every `Binding: hard` `I<n>`, `Must not`
   rule, spoken pronunciation cue, and `Concrete viewer scenario` in `intent.md`
   is honored with zero resurrected `Rejected` options.
2. **Steelman & creative rationale:** check that competing *Design It Twice*
   lanes and `D1..Dn` rejections represent honest alternatives with clear
   `Why` and `Reopen if` anchors rather than strawmen.
3. **Visual & continuity executability:** confirm lighting direction, palette
   hex anchors, wardrobe/product invariants, lens progression, and the
   Cross-Shot Continuity Checklist are concrete enough for Phase 2 prompt
   authoring and Visual Critic (`view_image`) falsification. When `script.md`
   and `storyboard.md` exist, also verify the **swap test**, **read-aloud
   budget**, **mute test** (`Verdict: PASS`), verbatim **Continuity Lock**
   inheritance into `style-bible.md`, cut-by-cut duration math, and
   `Test-take check` flags on risky shots.
4. **Audio, pacing & anti-IP hygiene:** confirm beat durations sum cleanly to
   `target_duration_s`, raw clip diegetic rules prevent music bleed, VO word
   budgets fit shot durations without speedup, and trademark/IP risks are
   phrased neutrally.
5. **Budget realism check:** flag treatments whose shot count or complexity
   obviously cannot fit `intent.md`'s `Draft cap` / `Final cap` with retry
   headroom (`BUDGET_CAP` or `CONCERN`).

Return `PASS`, `CONCERNS` (only for bounded risks forwarded to Production
Design), or `FAIL` (`INTENT_GAP`, `VISUAL_DRIFT_DEFECT`, `CONTINUITY_DEFECT`,
or `BUDGET_CAP`).
