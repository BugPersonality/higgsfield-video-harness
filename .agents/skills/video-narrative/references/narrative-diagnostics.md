# Narrative Diagnostics (Symptom -> Fix)

Use this lookup during `R1B` script/storyboard audits, `R3` Still Animatic
Blind Viewer Reads, and `R4B` Draft Cut reviews whenever a technically clean
take fails to land in meaning (`NARRATIVE_DEFECT`).

## Symptom-to-Fix Table

| Symptom / Cold-Read Failure | Observable Signal | Root Cause | Exact Fix & `reopen_owner` |
| --- | --- | --- | --- |
| **Primary Misread triggered** | Cold reviewer misidentifies product category or brand role (e.g., reads an AI software assistant as smart-mirror hardware, or mistakes a curation tool for a giant marketplace) | Visual metaphor overpowers product proof, or opening chaos looks like assortment bragging instead of friction | `Root Producer` — strengthen the explicit misread-foreclosing beat in `Narrative Lock` and `storyboard.md` (add physical problem setup, state-preserving surgical edit, or minimal diegetic cue); re-test on `R3` animatic before `R4` motion |
| **Slideshow / `AND THEN` drift** | Shots look gorgeous individually, yet feel disconnected like a random mood reel | Beats chain via `AND THEN` rather than `BUT` / `THEREFORE`; missing clear `Turn` | `Root Producer` — rewrite `Causal Spine` in `script.md` so every transition carries a physical contrast (`BUT`) or consequence (`THEREFORE`); reorder or cut unmotivated shots |
| **Zero-delta filler shot** | Viewer attention dips mid-spot; deleting shot `S0X` leaves story and turn intact (e.g., aimless walking, rolling a suitcase across a room, redundant second swap, gratuitous macro) | Shot has no distinct `Narrative job` or repeats the previous/next beat's information delta | `Root Producer` — cut the shot completely (Deletion Test) and reallocate its seconds to tighten rhythm or breathe on the true climax/button |
| **`0.1s` semiotic ambiguity** | Technically crisp hero object or gesture fails instant recognition on mute/mobile (e.g., turned-off designer mushroom dome reads as abstract sculpture rather than a lamp) | Stylized silhouette sacrifices canonical instant readability | `Worker(<asset_id>)` — replace with canonical, unmistakable silhouette and active state cue (e.g., articulated conical desk lamp switched ON with warm light pool) in `R2`/`R3` still before animating |
| **Synthetic referent grouping** | Props or actions in a hero tableau feel artificially assembled by an ad writer rather than belonging to one believable human life (e.g., mismatched travel kit pairing) | Weak or fabricated `Human Truth` in `Narrative Lock` | `Root Producer` — replace scenario with one universally recognizable human need where every item organically justifies its presence; re-stage `R3` still |
| **Over-explaining / broken `2 + 2`** | VO captions visible action, numeric counters or price boxes clutter frames, or a crutch closing tagline explains the payoff right before the logo | Distrust of picture; handing the viewer `"4"` instead of `"2 + 2"` with an earned pause | `Root Producer` — strip captioning VO lines, numeric clutter, and crutch endcards; replace with `[PAUSE 1.5–2.2s]` or diegetic `SFX:` and verify mute readability |
| **Narrative voice break** | Sudden drop in brand status or tonal whiplash (parody opener, weak throwaway closer, stiff corporate B2B pitch inside an intimate or minimalist piece) | Copy or acting violates `POV & Narrative Voice` in `Narrative Lock` | `Root Producer` — rewrite offending line/card to match locked tonal distance or cut straight from visual peak to minimalist brand button |
| **Narrative over-dramatization** | Clean `15s` tactile or design spot gets bogged down in melodramatic VO monologue or contrived character drama | Misapplying `60s+` character-drama tropes to a short sensory/object spot | `Root Producer` — switch to **Sensory / Object-Led** mode ([Narrative Structures](narrative-structures.md#1-four-protagonist-modes-narrative-works-without-actors)); carry `State Shift` strictly through optics, material physics, foley, and scale progression |

## Blind Viewer Read Protocol (`R3` & `R4B` Pre-Dailies QC)

Run inside fresh `reviewer-agent` (`fork_turns: "none"`, zero builder
rationales):

1. **Step 1 — Cold Read (before consulting builder notes):** Inspect
   `stills_strip.png` + `animatic.mp4` (`R3`) or `draft_cut.mp4` + contact
   sheets (`R4B`) as a first-time viewer with sound off first, then sound on.
   Record in two plain lines:
   - *Cold read:* what physically happens, what category/product this appears to
     be, and what shifts from start to end.
   - *Friction / confusion:* any object, gesture, cut, or text beat that caused
     hesitation (`> 0.5s` to decode) or felt redundant.
2. **Step 2 — Lock Audit (against `brief.md` + `Narrative Lock`):** Compare the
   cold read against the 6 `Narrative Lock` invariants and each shot's
   `Narrative job`:
   - Flag **`FAIL` / `NARRATIVE_DEFECT`** when `Primary Misread Risk` actually
     triggers, a proof-bearing object fails `0.1s` instant recognition, a
     required causal turn disappears on mute, or an entire shot fails the
     Deletion Test with zero narrative delta.
   - Flag **`CONCERNS` / `NARRATIVE_DEFECT`** when pacing/pause room for
     `2 + 2` feels slightly rushed or one line borders on over-explaining.
   - Return **`PASS`** when meaning lands cleanly on first watch—even if the
     reviewer personally might prefer a different aesthetic direction (**taste
     belongs solely to the Director**).
