# Phase 0 — Intake

Use when a new video campaign lacks a confirmed
[Video Intent V1](../interfaces/intent-v1.md) (`campaigns/<slug>/intent.md`) at
`status: ready`, or when viewer meaning, brand truth, spoken pronunciation,
`Must not` taboos, autonomy mode, or credit caps are unresolved or changed.

The Root Orchestrator owns Intake directly with the requester. Every downstream
phase runs in a fresh session (`fork_turns: "none"`) with zero chat history, so
precision here governs the entire production.

## Steps

1. **Ground via `evidence-agent` and map the design tree.**
   - Inspect whether `campaigns/<slug>/intent.md`, a brand profile in
     `brands/`, local reference photos in `campaigns/<slug>/media/references/`,
     or prior `/idea-refine` / `/grilling` outputs already exist; carry settled
     decisions forward without re-asking them.
   - Dispatch a fresh read-only `evidence-agent` (`fork_turns: "none"`,
     `reasoning_effort: low`) to run free discovery checks before Round 1 so
     the root stays in the **Smart Zone**:
     - verify brand docs and reference files on disk;
     - check `higgsfield account status`, `higgsfield workspace list`, and
       available models/voices relevant to the request.
   - **XY check & downgrade check:** separate the requester's desired viewer
     effect from any casually mentioned model, lens, or edit mechanism. If
     grounding proves the request is one isolated image/clip or local edit,
     downgrade to [`Direct Work`](../../../AGENTS.md#direct-work) instead of
     opening a full campaign.
   - Classify every open branch using [Grilling](../shared/grilling.md)'s four
     buckets (**facts**, **technical choices**, **low-stakes reversible
     conventions**, **requester-owned decisions**), consulting
     [Video Blind-Spot Coverage](#video-blind-spot-coverage). Keep all model
     IDs, CLI flags, prompt syntax, and codecs strictly OFF the requester's
     frontier.

2. **Grill the frontier in paced rounds.**
   - Run [Grilling](../shared/grilling.md) in 3–5 question rounds until the
     requester-owned **frontier** is empty.
   - Never accept unbound creative adjectives (`"cinematic"`, `"premium"`,
     `"dynamic"`, `"high quality"`) without grounding them into concrete viewer
     scenarios or explicit delegated bounds.
   - Obtain explicit requester choices for hard
     [Budget Authority](../shared/budget-authority.md) fields: `Autonomy mode`
     (`autonomous-draft` default vs `checkpointed`), `Draft cap`, `Final cap`,
     and `Max auto-retries/shot`.
   - On multi-round interviews (3+ rounds), persist
     `campaigns/<slug>/intent.md` incrementally at `status: draft` with a
     temporary `## Remaining frontier` section so interruption or compaction
     never loses settled answers.

3. **Synthesize `intent.md` (`status: draft`) and run `make intent-check`.**
   - Write `campaigns/<slug>/intent.md` conforming to
     [Video Intent V1](../interfaces/intent-v1.md):
     - all 5 required H2 sections (`Purpose & viewer effect`, `Subject & visual
       truth`, `Format, audio & delivery`, `Constraints & boundaries`,
       `Success signal`);
     - addressable `### I<n> — <title>` decisions (`Binding: hard | default`,
       `Decision`, `Rejected`, `Why`);
     - 1–3 `Concrete viewer scenarios` (muted autoplay, sound-on playback,
       pause-frame audit);
     - `Assumptions & reopen triggers` (`A<n>`) and any non-blocking
       `Open questions` (zero requester-owned questions);
     - remove any temporary `## Remaining frontier` section.
   - Run the mechanical gate and fix every error or unbound-qualifier warning:
     ```sh
     make intent-check CAMPAIGN=<slug>
     ```
   - Perform a quick Author Cold-Start Self-Check: re-read only `intent.md`
     without chat context and verify a fresh Phase 1 session could direct the
     spot without guessing brand truth, pronunciation, or taste boundaries.

4. **Run Cold-Start Intent Review (before Gate 1).**
   - Dispatch one fresh read-only `reviewer-agent` (`fork_turns: "none"`,
     `reasoning_effort: high`) running
     [Cold-Start Intent Review](#cold-start-intent-review) under
     [Review](../shared/review.md).
   - Pass strictly `campaigns/<slug>/intent.md`, any cited `brands/` file, and
     the review adapter—omit chat transcripts and author justifications.
   - Repair confirmed local defects in place, ask one surgical follow-up round
     if a genuine requester fork surfaces, and re-run
     `make intent-check CAMPAIGN=<slug>`.

5. **Confirm shared understanding (Gate 1) and flip to `status: ready`.**
   - Present a compact one-screen Gate 1 brief in the requester's language with
     a link to `campaigns/<slug>/intent.md`:
     - viewer purpose and emotional effect;
     - 1–2 concrete viewer scenarios (including muted opening and pause-frame
       product/brand check);
     - settled decisions (`I1..In`: `Binding`, chosen, rejected, why);
     - `Must not` prohibitions, non-goals, and spoken pronunciation cues;
     - explicit **Budget Envelope** (`Autonomy mode`, `Draft cap`, `Final cap`,
       `Max auto-retries/shot`);
     - labeled assumptions (`A1..An` with `Reopen if`, highlighting the riskiest
       assumption) and observable success signal.
   - Wait for explicit requester confirmation before flipping `status: ready`,
     re-running `make intent-check CAMPAIGN=<slug>` to prove all `ready`
     invariants, and launching
     [Cross-Phase Continuation](../shared/transition.md#cross-phase-continuation)
     into [Creative Definition](creative-definition.md).

6. **Handle mid-pipeline reopens.**
   - When reopened by a downstream `Blocked Exit` (`B1..Bn`), Visual Critic
     `INTENT_GAP`, or requester feedback on Stills / Pilot / Draft Cut:
     - flip `campaigns/<slug>/intent.md` from `ready` back to `draft` first
       under [Artifacts](../shared/artifacts.md#in-place-reopen-discipline);
     - translate `B1..Bn` or feedback into plain viewer questions (holding back
       `Follow-up if <option>` lines until needed) and grill strictly on the
       delta;
     - reconcile settled changes into `intent.md` in place while keeping
       surviving `I<n>` and `A<n>` IDs stable (mark overturned decisions
       `Superseded by I<m>`), re-run `make intent-check CAMPAIGN=<slug>`,
       re-run Cold-Start Intent Review if a high-risk boundary changed, confirm
       material deltas with the requester, and flip back to `status: ready`;
     - return control under
       [Mid-Pipeline Reopen](../shared/transition.md#mid-pipeline-reopen) to
       the earliest invalidated phase while preserving all unaffected accepted
       shots and `receipts.jsonl`.

## Video Blind-Spot Coverage

Consult only the branches relevant to the campaign when mapping the design tree:

- **Viewer situation & muted opening (0–3 s):** where the video plays (web
  autoplay, YouTube, Reels/TikTok, paid ad) and what must register even muted.
- **Subject & brand truth:** product colorway/finish, logo/wordmark rules,
  character likeness or anonymity, physical setting, and reference photo
  availability.
- **Spoken pronunciation & audio posture:** exact phonetic spelling for brand,
  product, or person names; voiceover vs purely visual/diegetic; music mood
  taboos; on-screen text prohibition vs requirement.
- **Format & cadence:** target duration, aspect ratio, platform-required FPS or
  safe zones, and cutdown exclusions (`Non-goals`).
- **Hard taboos (`Must not`):** visual clichés, competitor/third-party IP,
  forbidden styles, audio dislikes, and forbidden shortcuts.
- **Authority & budget envelope:** `Autonomy mode`, `Draft cap`, `Final cap`,
  `Max auto-retries/shot`, and active Higgsfield billing workspace.
- **Trade-off compass:** ordered `Priority / tie-breakers` deciding which value
  wins (for example, material accuracy over dramatic camera flair) when
  downstream craft forks appear.

## Cold-Start Intent Review

Read-only review adapter for a fixed `campaigns/<slug>/intent.md`
(`status: draft`) before Gate 1. Return
[Review Result V1](../interfaces/review-result-v1.md) without rewriting
`intent.md` or inventing requester answers. Run Checks 1–4 strictly from
`intent.md` with zero chat history before inspecting cited brand/reference
files for Check 5:

1. **Two-reader divergence (cold):** flag any ambiguity where two fresh
   Creative Definition teams reading only `intent.md` would produce materially
   different subjects, settings, audio postures, or visual moods.
2. **Internal contradictions:** check for conflicts across `I<n>`, `Rejected`,
   `Concrete viewer scenarios`, `Must not`, `Scope & non-goals`,
   `Authority & budget envelope`, `A<n>`, and `Success signal`.
3. **Unbound qualifiers & hidden requester forks:** flag ungrounded adjectives
   (`"cinematic"`, `"premium"`, `"dynamic"`, `"high quality"`), unanswered
   requester-owned `Open questions`, missing `Autonomy mode` / credit caps, or
   one-way brand choices disguised as `A<n>` assumptions.
4. **Mechanism leak vs. mandate:** flag Higgsfield model IDs, CLI flags, prompt
   templates, or FFmpeg settings leaking into `Hard constraints` instead of
   `Suggested mechanisms (non-binding context)` unless explicitly mandated.
5. **Premise & brand anchor check:** open cited `brands/` files and verify
   `intent.md` does not silently contradict recorded brand invariants, hex
   codes, pronunciations, or taboos without an explicit `I<n>`.

Return `PASS` when all five checks clear, `CONCERNS` only for bounded external
risks already paired with `Reopen if`, or `FAIL` (`INTENT_GAP`) naming exact
anchors and `reopen_owner: Intake`.
