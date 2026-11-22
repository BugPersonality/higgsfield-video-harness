---
name: youtube-clipping
description: "Faceless YouTube 3-5 min documentary/edutainment pipelines, YouTube A/B packaging, and batch vertical clipping/repurposing (Katana, Shorts safe zones, 1-clip gate before 10-clip batch). Use when producing long-form faceless YouTube videos or repurposing long footage into viral Shorts/Reels."
---

# Faceless YouTube & Video Clipping (`youtube_and_clipping`)

Canonical workflow for **serialized 3–5 minute faceless YouTube channels** and
**high-retention vertical clipping (`9:16`)** from films, podcasts, or
long-form episodes.

## 1. Faceless YouTube Production Pipeline (`3–5 min`, `16:9` `1080p`)

1. **Step 0 — Policy & RPM Gate (Zero Media Spend):** Verify evergreen
   high-RPM niche demand (education, tech, finance, science "What if…") and
   avoid YouTube demonetization traps (mass-produced templates, fake emotional
   bait, cloned real people, or fake YMYL experts). Explicitly separate verified
   facts from guesses before writing.
2. **Step 1 — Script & Visual Moodboard Gate:** Build `Hook (impact within 10s)
   -> Intro -> Body (mini-question + payoff per section; faster cuts in minute
   1, calmer pace during complex explanations) -> Recap -> Outro`. Lock one
   consistent moodboard/storyboard, narrator voice (`ElevenLabs`), and reusable
   environment/object references before generating bulk clips.
3. **Anti-Slop B-Roll Rule:** For automated B-roll shots without locked `R2`
   Character Bibles or 3D previz, **avoid gratuitous visible human anatomy**
   (`"No visible humans — stage objects, scale, diagrams, and environments
   positively"`) to prevent costly anatomy re-rolls.
4. **Composite Disclaimers & Labels in Post:** Keep text out of raw `Seedance`
   generations; add factual badges (`HYPOTHETICAL SCENARIO`), counters, and
   callouts in edit synced to narration (use `assemble.sh --overlay` or NLE).
5. **YouTube A/B Packaging Gate:** Deliver **3 distinct thumbnail + title
   pairs** (`16:9`) for YouTube's built-in A/B test:
   - Thumbnail rules: frozen peak-action moment or scale progression with
     warm/cold lighting split, **<= 4–5 words max** (often 1 bold word + visual
     focal arrow), curiosity gap where title *adds* to image rather than
     repeating thumbnail text, zero timestamps/corner badges/watermarks, and
     verified at phone size.
   - Remind creator to check **"Yes"** on YouTube Studio's **"AI use"**
     disclosure when synthetic realistic media is included.

## 2. Shorts Repurposing & Batch Clipping (`9:16`, `15–30s`)

- **Repurpose Existing Footage First:** Cut 3 standalone `9:16` Shorts directly
  from the finished long-form MP4 (`assemble.sh` `trim_in/trim_out` + reframe,
  never stretching `16:9`) before spending credits on net-new Shorts.
- **Shorts Safe-Zone Contract (`1080x1920`, `30s`):**
  - Horizontal text bounds: **`x 8–88%`**.
  - Contextual labels: **`y 12–60%`** (**keywords lead VO by ~3 frames**).
  - Captions: **`y 68–78%`**, `3–5` words, max `2` lines, high-contrast with
    dark outline, replace cleanly (never overlap).
  - Pacing: finish VO by **`28s`** of a `30s` clip and hold final frame
    **`0.5–2.0s`**.
- **3-Input Clipping Workflow (`Higgsfield Katana` / Edit Pipeline):**
  1. Attach **3 strictly separated inputs**: (a) source footage (film/podcast),
     (b) editing reference video (pacing/rhythm only — explicitly state
     `"Use footage from our source, not from the reference"`), and (c) separate
     music track (build toward the drop while keeping dialogue crystal clear).
  2. **1-Clip Stage Gate Before Batching:** Run **1 single clip first** with
     mandatory checkpoints (`analysis report -> edit plan -> preview`). Only
     after Director approval run a **Batch of 10** in the same session (each
     clip with a distinct hook/moment, exported separately in `9:16`).
  3. **Teaser & Localization Rules:** For film teasers, explicitly list which
     twists/endings are deliberately withheld. For localized versions, start
     from an *approved* edit, adjust caption timing, and flag any idiom needing
     native-speaker review.

*Tool availability fallback:* If Higgsfield Katana is not enabled in the user's
account, execute the exact same 3-input clipping & Shorts repurposing loop
locally with `scripts/assemble.sh` (`shots[].edit.trim_in/out`, `--overlay`
captions/labels, `--duck-music`) + `qa_media.py`.

*Done when:* Research and moodboard are approved before bulk clip generation,
captions/graphics obey `9:16` safe zones, 1-clip preview passes before any
batch run, and packaging includes 3 phone-verified A/B thumbnail/title options.
