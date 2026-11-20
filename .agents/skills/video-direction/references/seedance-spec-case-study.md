# Optional Case Study: Ultra-Lean Multi-Shot Spec Pipeline (`Seedance 2.5`)

An **optional, proven alternative workflow** distilled from the public Higgsfield Talent Contest short **`WHO AM I?`** (`@h8888m`, `1:20` runtime, **`175 credits`** across `273` generations and `8` final video clips).

> **Use as an option, not a default.** Keep the standard short-prose I2V and native `1080p` mastering paths for clean commercial product macros, crisp beauty/skin close-ups, or simple 5s single-beat shots. Reach for this playbook (or cherry-pick individual modules below) when the Director wants a **stylized, vintage/35mm narrative short, expressive handheld choreography, or maximum runtime per credit**.

---

## 1. Benchmark Anatomy (`WHO AM I?` — `1:20` in `175 cr.`)

| Metric / Layer | Observed Reality | Why It Saved Credits Without Hurting Craft |
| --- | --- | --- |
| **Image vs. Video Split** | **`74.4%` stills** (~203 gens: `Soul Cinematic` 42.1%, `Seedream 5.0 Pro` 14.6%, `Nano Banana Pro` 8.1%, etc.) vs. **`25.6%` video** (~70 gens of `Seedance 2.5`) | Cast, wardrobe, props, and clean sets were solved in cheap or Web `Unlimited` (`0 cr.`) image models before touching video. |
| **Final Delivery Spec** | All 8 final clips generated on `Seedance 2.5` at **`720p` (`High` bitrate, `1344×576` anamorphic `2.33:1`)** | Skipped expensive `1080p`/`4K` video mastering; 35mm grain (`Kodak Vision3`), soft tungsten/backlit contrast, and widescreen framing made `720p High` read as authentic 1970s film. |
| **Clip Packing** | **8 clips of `12s–20s`** carrying **`5–7` cuts inside a single generation** (or 1 continuous 20s handheld take with 6 timed beats) | Avoided burning 25–30 separate 5s video generations; averaged ~8.75 takes per complex 15–20s sequence. |
| **Zero-Credit External Inputs** | ~76 uploaded assets (`04 SOUNDS` `.mp3` voices/SFX, `03 MOTION CONTROL` 3D mannequin clip, NLE timeline/subtitles/music) | Voice identity (`@Audio 1`), physical mechanics, music score, and subtitles cost `0 cr.` and stayed editable in post. |

---

## 2. Optional Pre-Production & Asset Isolation Pattern

If you adopt this prep pattern before `R4` video generation:

1. **Split Face, Body, Start Pose, and Voice into separate references:**
   - **Face plate (`@Image 1`):** straight-on, neutral "passport" portrait (`Nano Banana Pro` / `Soul Cinematic`)—strictly face identity, no busy background.
   - **Body / Wardrobe plate (`@Image 2`):** full-body or outfit turnaround (`Soul Cinematic`) so clothing never bleeds into face geometry.
   - **Start Pose / Location plate (`@Image 3`):** exact frame `0–1s` staging and gaze lock.
   - **Voice plate (`@Audio 1`):** pre-recorded or externally generated `.mp3` voice clip fed directly into `Seedance 2.5` to lock timbre and cadence across scenes.
2. **Surgically pre-clean empty sets:** edit out distracting clocks, furniture, or props in `Seedream 5.0 Pro` with blunt literal instructions (e.g., *"remove the clock, remove the chairs and table"*) before animating.
3. **Isolate hero props on neutral gray:** generate closed/open prop states separately on matte gray (`#808080`) so `Seedance 2.5` can bridge state A → state B cleanly.
4. **Use 3D mannequin Motion Control for hard mechanics:** when a shot needs precise object interaction (e.g., opening a door cleanly), supply a simple 3D mannequin motion clip instead of re-rolling text prompts.

---

## 3. Optional 6-Block Spec Prompt Template (`Seedance 2.5`)

Unlike short `30–60w` single-shot I2V prompts, long `12–20s` multi-ref or multi-shot `Seedance 2.5` sequences respond well to an explicit, modular specification:

```text
---- SCENE TITLE / BEAT ----

REFERENCE DECLARATIONS
@Image 1 — FACE IDENTITY (strictly face only; ignore clothing/background)
@Image 2 — BODY / WARDROBE (or PROP state B)
@Image 3 — LOCATION / INITIAL POSE & GAZE LOCK (exact match at 0-1s)
@Image 4 — HERO PROP (optional)
@Audio 1 — VOICE IDENTITY (match timbre and natural delivery)

PARAMS {
  duration=20s;
  shot_count=1;              // or 5..7 for rhythmic multi-shot sequences (cuts=hard_3s)
  camera=physical_handheld;  // micro-breathing, reactive crash zooms, no tripod gloss
  fps=24;
  shutter=180;
  film=Kodak_Vision3_250D;
}

PALETTE & INVARIANTS
- Hex palette lock: #4A2819 walnut wood, #C5986B warm tungsten, #234B3A green lamp,
  #E8E1D3 cream paper, #191919 black leather.
- Spatial & prop invariants: table_count=1; book_count=1; wall clock frozen at 11:55.

TIMELINE & AUDIO (diegetic only)
0-1s: Exact initial pose and eyeline from @Image 3. Quiet room tone.
1-4s: Fast handheld crash zoom onto documents on desk. Crisp paper rustle.
4-6s: Reactive crash zoom left to vintage phone. Mechanical ring.
6-10s: Subject picks up receiver, speaks (@Audio 1): "..."
10-12s: Hangs up, crash zoom out to medium frame.
12-18s: Looks up, delivers line (@Audio 1): "..."
18-20s: Sets pen down on paper. Subtle breathing, no freeze.

LOCK MANIFEST
music=0; no_music=1; strict_no_music=1;
freeze_frame=0; hero_shot=0; subtitles=0;
cast_count=1; extra_people=0;

中文强制锁定
[Optional for Seedance / Kling / Wan when English constraints drift:
repeat the 4–6 hardest invariants in concise Simplified Chinese —
exact cast count, zero extra people, strict no music/subtitles,
locked face/prop/clock geometry.]
```

---

## 4. What Each Technique Produces (Expectations & Trade-offs)

Pick individual levers below based on the brief—you do not need all of them together:

| Technique | Expected Result | Trade-off / When to Skip |
| --- | --- | --- |
| **HEX Palette Lock (5–7 hex codes)** | Strong color-grade coherence across different clips and locations before NLE grading. | Skip if the Director wants natural, uncontrolled documentary color shifts. |
| **`hero_shot=0`, `freeze_frame=0`, `physical_handheld` + `crash zoom`** | Breaks the stiff "glossy AI commercial" look; produces asymmetric, lived-in cinema energy. | Skip for luxury watch/cosmetic packshots requiring locked-off symmetry and smooth dolly elegance. |
| **Long `12–20s` Multi-Shot (`shot_count=5..7`)** | Cuts video credit burn dramatically while keeping shared grain, lighting, and costume continuity across cuts. | Harder to surgically re-roll just 1 bad cut inside the 20s block; use separate 5s clips when every beat must be independently lockable. |
| **`720p High` (`1344×576`) Final Delivery** | 3–5× cheaper than native `1080p` mastering; looks convincing with 35mm grain, soft halation, and widescreen crop. | Not suitable for sharp modern `1080p`/`4K` tech/beauty commercials where fine skin pores or micro-typography must hold up at `1:1`. |
| **High-Contrast / Simplified Character Silhouette** | Eliminates micro-face drift and redirects model capacity into expressive body choreography, timing, and physics (smoke, fabric). | Applies only when the concept supports stylized/masked/silhouette protagonists rather than photorealistic human close-ups. |
| **`LOCK MANIFEST` + Optional `中文强制锁定`** | Noticeably stricter compliance on `Seedance 2.5` for suppressing background music, extra background people, and prop duplication. | Overkill for simple 5s single-subject I2V shots; unnecessary on non-Chinese engines (`veo3_1`, `runway`, `luma`, `sora`). |
