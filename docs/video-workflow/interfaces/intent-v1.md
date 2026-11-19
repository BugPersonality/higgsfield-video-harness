# Video Intent V1

`campaigns/<slug>/intent.md` preserves requester meaning, visual/brand truth,
autonomy mode, budget envelope, and closed interview decisions across the
cold-start boundary into Creative Definition, Production Design, Planning,
Production, and Review. It is the synthesized decision record after
[Intake](../phases/intake.md)—not a chat transcript, creative treatment, prompt
pack, or task ledger.

## Schema

```markdown
# Intent: <campaign title>

status: draft | ready

## Purpose & viewer effect

<Who watches, where the video lives, and the concrete shift in attention, emotion, or understanding within the opening seconds and full runtime.>

## Subject & visual truth

<Hero product, character, or subject invariants, physical setting, material finishes, wordmark rules, spoken pronunciation cues, and cited brand/reference locators.>

## Format, audio & delivery

<Duration, shot cadence or flexibility, aspect ratio, target FPS, draft vs master resolution expectations, voiceover/music/diegetic audio posture, and expected exports.>

## Constraints & boundaries

- **Must not:** <non-negotiable visual, brand, audio, IP, or operational prohibitions>
- **Authority & budget envelope:**
  - Autonomy mode: autonomous-draft | checkpointed
  - Draft cap: <N> credits
  - Final cap: <M> credits
  - Max auto-retries/shot: <K>
- **Scope & non-goals:** <explicit in-scope deliverables and plausible adjacent work excluded from this campaign>
- **Suggested mechanisms (non-binding context):** <optional casual model, lens, or tool mentions from the requester; downstream phases may replace them when another choice satisfies the outcome better>

## Success signal

<Falsifiable technical, visual/continuity, and budget conditions proving the finished spot solves the requester's goal.>

## Settled decisions

### I1 — <short decision topic>

- **Binding:** hard | default
- **Decision:** <exact user choice; preserve user-pinned numbers, durations, hex codes, pronunciations, and wording verbatim>
- **Rejected:** <alternative(s) explicitly discussed and ruled out during grilling, with brief reason>
- **Why:** <requester's underlying rationale so fresh downstream phases preserve intent on unseen edge cases>

## Concrete viewer scenarios

- **<Scenario name>:** <Concrete muted-autoplay, sound-on playback, or pause-frame viewer check confirming what the audience sees and hears>

## Preferences & delegated choices

- **Priority / tie-breakers:** <ordered trade-off compass guiding autonomous downstream craft decisions>
- **Delegated decisions:** <what downstream agents own deciding, guided by what outcome, within what bounds>

## Assumptions & reopen triggers

- **A1 — <short assumption name>:** <reversible, outcome-preserving assumption surfaced at confirmation> — **Reopen if:** <objective condition or owner>

## Terminology

- **<Term>:** <canonical requester meaning and spoken pronunciation when relevant>. **Not:** <excluded interpretation>

## Open questions

- **Q1 — <non-blocking question>:** Owner: <non-requester owner> | Fallback: <`A<n>` or delegated default> | Reopen if: <objective condition>
```

## Required vs. Optional Sections

| Section (`##`) | Status | Rule |
| --- | --- | --- |
| `Purpose & viewer effect` | Required | Always present |
| `Subject & visual truth` | Required | Always present |
| `Format, audio & delivery` | Required | Always present |
| `Constraints & boundaries` | Required | Must include `Must not`, `Authority & budget envelope` (`Autonomy mode`, `Draft cap`, `Final cap`, `Max auto-retries/shot`), and `Scope & non-goals` |
| `Success signal` | Required | Always present |
| `Settled decisions` | Optional | Include whenever grilling closed material branches (`### I<n> — <title>`) |
| `Concrete viewer scenarios` | Optional | Recommended 1–3 scenarios for every multi-shot campaign |
| `Preferences & delegated choices` | Optional | Include priority tie-breakers and explicitly delegated craft bounds |
| `Assumptions & reopen triggers` | Optional | Required whenever reversible assumptions exist (`A<n>`) |
| `Terminology` | Optional | Include for brand names, product SKUs, pronunciations, or domain terms |
| `Open questions` | Optional | At `status: ready`, zero requester-owned questions allowed |
| `Remaining frontier` | Draft-only | Permitted **only** while `status: draft` for multi-round resumability; MUST be cleared and removed before Gate 1 and `status: ready` |

Omit empty optional sections rather than writing `N/A` boilerplate.

## Field Rules

- **Lifecycle & mechanical gate (`make intent-check`):** start at `status: draft`
  when persisting multi-round grilling progress, handling a reopen, or preparing
  Gate 1 confirmation. Run `make intent-check CAMPAIGN=<slug>`
  (`python3 scripts/check-intent.py campaigns/<slug>`) on `draft`, fix every
  error, obtain requester confirmation under [Intake](../phases/intake.md), flip
  to `status: ready`, and re-run `make intent-check CAMPAIGN=<slug>` to verify
  all `ready` invariants. Downstream phases and `scripts/hf_guard.py` refuse any
  `intent.md` not at `status: ready`.
- **Budget envelope authority:** `Authority & budget envelope` inside
  `Constraints & boundaries` is the single canonical authorization parsed by
  `scripts/check-intent.py` and `scripts/hf_guard.py` under
  [Budget Authority](../shared/budget-authority.md):
  - `Autonomy mode`: strictly `autonomous-draft` or `checkpointed`.
  - `Draft cap`: positive integer (`> 0`) followed by `credits`.
  - `Final cap`: non-negative integer (`>= 0`) followed by `credits`.
  - `Max auto-retries/shot`: non-negative integer (`>= 0`) retry ceiling per
    shot.
  `scripts/check-intent.py` also verifies backticked `brands/...` and
  `docs/...` paths on disk, warns on missing `media/references/...` paths (or
  fails with `--require-media`), and warns on unbound vague qualifiers
  (`cinematic`, `premium`, `dynamic`, `high quality`) in `Purpose & viewer
  effect` or `Subject & visual truth` when `Concrete viewer scenarios` is
  absent.
- **Addressable decisions (`I1`, `I2`, ...) & verbatim fidelity:** give every
  closed interview decision its own `### I<n> — <title>` heading with `Binding:
  hard | default`, `Decision`, `Rejected`, and `Why`. Downstream treatments,
  shotlists, and reviewers cite `intent.md#i<n>-...` directly. Mark
  `Binding: hard` for explicit requester mandates or brand invariants (never
  weakened without reopening Intake) and `Binding: default` for confirmed
  defaults downstream phases may adjust only when live schema limits or a hard
  constraint conflicts. Preserve hex codes, wordmark rules, exact spoken
  pronunciations, durations, and `Must not` rules verbatim.
- **De-mechanization:** keep casual model IDs, lens guesses, or editing hints
  from the user inside `Suggested mechanisms (non-binding context)` unless the
  requester explicitly mandated a specific tool or look as a hard constraint.
  Keep prompt engineering, CLI flags, and FFmpeg filter graphs out of
  `intent.md`; those belong to [Decision Ownership](../../../AGENTS.md#decision-ownership).
- **Assumptions (`A<n>`) & `Open questions`:** every material assumption carries
  `- **A<n> — <name>:** <assumption> — **Reopen if:** <trigger>` and is surfaced
  at Gate 1. At `status: ready`, `Open questions` may hold **zero**
  requester-owned questions: every entry must name a non-requester `Owner:`
  (for example `evidence-agent`, `production-design`, `assembly-worker`, or an
  external asset provider), a concrete `Fallback:`, and an objective
  `Reopen if:` trigger.
- **ID stability on reopen:** on any mid-pipeline feedback or reopen, flip
  `status` back to `draft` under [Artifacts](../shared/artifacts.md#in-place-reopen-discipline).
  Never renumber surviving `I<n>` or `A<n>` IDs: add new sequential IDs, mark
  overturned decisions `Superseded by I<m>` (or note the delta in place), remove
  resolved open questions, re-run `make intent-check CAMPAIGN=<slug>`, confirm
  material deltas, and flip back to `status: ready`.
