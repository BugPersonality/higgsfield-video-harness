# R0 — Direction Seed

**Credit spend:** `0 credits`
**Owner:** Root Producer (with read-only `evidence-agent` grounding)
**Outputs:** `campaigns/<slug>/brief.md` (`status: active`), seeded `campaigns/<slug>/taste-log.md` (`TL-01`)

R0 settles only the **meaning, brand/product truth, taboos, and `Campaign cap`**
needed to craft strong story options in `R1`—without interrogating the Director
on aesthetic micro-details that are far easier to judge visually in `R1A`–`R4`.

## Entry Criteria

- The request is a multi-shot video, commercial, or branded spot routed here by
  the [Workflow Router](../router.md) (not isolated `Direct Work`).
- Scaffold the workspace if it does not yet exist:
  ```sh
  make campaign-init SLUG=<slug> [BRAND=<brand>]
  ```
- If the Director starts from a vague raw hunch, offer `idea-refine` (only when
  explicitly invoked or confirmed) to sharpen the viewer bet before drafting
  `brief.md`.

## Step 1 — Read-Only Grounding (`evidence-agent`)

Before asking the Director a single question, dispatch a fresh read-only
`evidence-agent` (`fork_turns: "none"`, `reasoning_effort: low`) to resolve
observable facts:

1. Check active Higgsfield billing workspace and credit balance
   (`higgsfield workspace list`, `higgsfield account status`).
2. Discover matching brand profiles (`brands/<brand>/brand.md`) and graduated
   brand taste files (`brands/<brand>/taste.md`).
3. Inventory all supplied source photos already placed under
   `campaigns/<slug>/media/references/` (filenames, resolutions, subjects).
4. Note whether every hero object, character, and location is already covered by
   real photos (which will allow skipping `R2` Lookbook later) or whether
   invented entities will need `R2` Lookbook casting.

Never ask the Director for facts `evidence-agent` can read directly.

## Step 2 — Light Meaning Alignment

Apply [Grilling](../shared/grilling.md) strictly on the Director's frontier:
**3–5 plain-language questions** covering only unresolved high-leverage meaning
decisions:

- **Viewer effect:** what the viewer should feel, remember, or do after watching
  (both muted and with sound).
- **Subject & brand truth:** non-negotiable physical/material/logo truths, plus
  exact spoken pronunciation if voiceover is used.
- **Format & audio:** target placement, aspect ratio, runtime, and voiceover vs
  purely visual/diegetic storytelling.
- **Taboos (`Must not`) & `Campaign cap`:** visual clichés to ban, total
  `Campaign cap` (contextualized against live account balance), `Lookbook
  variants` (`1..4`, default `3`), `Max auto-retries/asset` (default `2`), and
  `Auto-open dailies` (`true` on macOS by default).

Keep 100% of technical mechanics (models, flags, prompts, codecs, FFmpeg) off
the Director's plate, and convert low-stakes defaults into labeled
`Assumptions`.

## Step 3 — Draft `brief.md` & Seed `taste-log.md`

1. Author `campaigns/<slug>/brief.md` following
   [Direction Brief V1](../interfaces/brief-v1.md) at `status: draft` (zero
   placeholders in settled sections; zero technical mechanics).
2. Seed `campaigns/<slug>/taste-log.md` following
   [Taste Log V1](../interfaces/taste-log-v1.md):
   - Cite `Brand taste seed: brands/<brand>/taste.md` and summarize inherited
     brand rules when present.
   - Append `### TL-01 (R0 — Seed)` capturing initial `Approved / LOCKED`
     (supplied real reference photos, if any), `More of`, `Change / Steer`, and
     `Never` rules surfaced during R0.

## Step 4 — Dailies 0 (Confirmation)

Present a compact [Dailies Packet V1](../interfaces/dailies-packet-v1.md):

1. **What to inspect:** concise Direction Brief card summarizing viewer effect,
   non-negotiable subject truth, format/audio, `Must not`, seeded taste anchors,
   and `Budget & round policy` (`campaigns/<slug>/brief.md`).
2. **Filtered internally:** confirm workspace/balance check and local reference
   photo inventory (`0 credits spent`).
3. **Comparative taste questions:** 1–2 quick confirmation checks if any
   assumption or `Must not` boundary needs tightening.
4. **Cost ticket:** `0 credits spent`; `R1` (Story & Cost Ticket) is **`0 credits`**;
   confirm `Campaign cap: <N> credits` and go-ahead to enter `R1`.

## Exit Criteria & Next Round

Once the Director confirms Dailies 0:

1. Reconcile any final tweaks into `brief.md`, close or remove any
   Director-owned items in `## Open questions`, and flip `status: active`.
2. Verify mechanically:
   ```sh
   make brief-check CAMPAIGN=<slug>
   ```
3. Append any R0 sign-off nuances to `taste-log.md` (`TL-01`) and advance to
   [R1 — Story & Cost Ticket](r1-story-and-cost.md).
