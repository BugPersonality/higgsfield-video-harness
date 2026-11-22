---
name: performance-ads
description: "High-converting e-commerce and service ad packs (PROOF, QUEST, STOP frameworks, 1-product-to-10-creatives static+video batches, 9:16 mobile safe zones, and organic-to-paid iteration). Use when producing performance ad batches for Meta, TikTok, or Reels."
---

# Performance Ads & Creative Batches (`performance_ads`)

Canonical workflow for producing **multi-angle static + `9:16` video ad
batches** for e-commerce products and B2B/B2C services grounded in real buyer
language.

## 1. Research-First & Angle Multiplication (`R0` -> `R1A`)

1. **Buyer Research Before Visuals:** Extract real customer reviews, buying
   triggers, competitors, and top objections (separating verified facts from
   assumptions) before writing any ad copy or visual prompt.
2. **1 Product -> 5 Angles -> 10 Creatives (5 Video + 5 Static):** Assign each
   creative **one distinct job** (fit, styling, matching couple, craftsmanship,
   social proof) rather than repeating one generic pitch.
3. **Viral Hook Check (`STOP`):** Validate every hero hook against
   **S**urprise, **T**ension, **O**utcome, and **P**ass it on — tying any
   humor or contrast directly to a verifiable product benefit.

## 2. Proven Format Matrices

### E-Commerce (`PROOF`: Promise, Receipts, Offer, Objection, First step)
- **3 Static Formats (`9:16` `4k` `Nano Banana 2` / `GPT Image 2`):**
  1. *Callout Diagram:* Flat-lay / split card with numbered markers, `1px`
     leader lines, physical dimensions, and circular detail zoom-ins linking
     hardware to daily benefit.
  2. *Review Card:* Discount badge + hero shot + specific verified customer
     quote answering a real hesitation + star rating.
  3. *Offer Card:* Clean knolling flat-lay + clear price/guarantee + CTA.
- **3 Video Formats (`9:16` `1080p` `12–15s`, `Seedance 2.5`):**
  1. *UGC (`13s`):* Authentic iPhone main-camera look (deep focus, neutral
     phone contrast, zero cinema grain) across 3 daily-routine outfits/sets.
  2. *Unpacking (`14s`):* Real compartments/capacity + `@audio_1` phonetic
     brand pronunciation + clean negative space (`11–15s`) for post CTA.
  3. *Hyper Motion (`15s`, `30fps`):* Studio durability torture test (fire,
     snow, water on brushed podium -> wipe-down -> dry interior reveal) or
     architectural occlusion outfit swap (`>= 6` frames full-body cover).

### Services (`QUEST`: Qualify, Understand, Educate, Stimulate, Transition)
- **3 Formats (Static + `24–30s` Narrative Video):**
  1. *Quiz:* Self-qualifying niche question (never generic agency copy).
  2. *Case Story:* Real verified before->after metric breakdown (never run paid
     traffic on placeholder/fictional metrics).
  3. *Direct Offer:* Concrete physical visual metaphor + low-friction CTA.

## 3. Mobile Composition, Resizing & Testing Discipline

- **Leave Negative Space for Post Overlays:** Reserve explicit clean canvas
  zones (top quarter white on statics; right side `10.2–13s` or lower-center
  `11–15s` on video) and add animated UI/CTAs in post (`assemble.sh --overlay`
  or Remotion/AE) instead of forcing cluttered text inside base video gens.
- **Recompose, Never Blind-Crop (`16:9` / `1:1` / `9:16`):** Reflow layouts
  across Feed (`1:1`), Stories, and Reels (`9:16`) so product details and
  copy never collide with platform UI. For horizontal cinema footage inside
  `9:16`, use sharp centered `16:9` panel framed by blurred enlarged copy.
- **6-Point Mobile QA Audit (before delivery):** Inspect every creative at
  actual phone size for: (1) product accuracy, (2) logos/lettering integrity,
  (3) offer text accuracy, (4) mobile readability, (5) safe framing, and
  (6) shot-to-shot continuity (including exclusive accessory windows like
  `"sunglasses exist only 0–3s"`).
- **Organic-First & One-Variable Paid Testing:** Validate hooks organically on
  Reels first; in paid tests change **one variable at a time** (hook, opening
  shot, or offer) and feed winning data back into the next variation batch.

*Done when:* Every angle maps to real buyer objections, every creative passes
the 6-point phone-size QA audit with clean safe zones, and variations isolate
one tested variable at a time.
