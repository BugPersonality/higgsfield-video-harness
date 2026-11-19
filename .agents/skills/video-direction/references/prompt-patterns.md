# Prompt Patterns & Rewrites

## 1. Translating `taste-log.md` Into Positive Visual Cues

Convert every `taste-log.md` bullet into observable lighting, texture, or
camera language—phrase `Never` rules as their positive physical opposite:

| `taste-log.md` bullet | Positive prompt translation |
| --- | --- |
| `Approved / LOCKED`: `lb_traveler_hand` | Keep exact `approved_upload_id` and wool-coat sleeve / leather patina descriptors. |
| `More of`: cool misty daylight, stillness | *"Diffuse cool 5200K morning mist from camera-left, generous negative space."* |
| `Change / Steer`: pull shot 2 wider | *"Medium-wide 35mm framing showing full stone bench and unobstructed right-hand clasp grip."* |
| `Never`: glossy leather, neon bounce | *"Dry matte vegetable-tanned grain, muted warm-neutral stone palette, natural overcast fill."* |

## 2. True `R2` Lookbook Contrast (`A / B / C`)

Vary genuinely distinct visual axes while holding product geometry constant:
- **Variant A:** cool diffuse morning mist, generous negative space, understated matte finish.
- **Variant B:** low directional golden sunbeams, higher micro-contrast, closer intimate crop.
- **Variant C:** architectural symmetry, overcast slate tones, tactile deep-grain emphasis.

## 3. I2V Motion Prompt Structure (`R4` / `R5`)

Do not re-describe static elements locked in `--start_image`; write only
camera, physics, and diegetic sound:

```text
0-2s: Slow steady dolly push forward as morning mist drifts past the right window; the traveler's right thumb presses the brushed brass clasp with subtle mechanical resistance.
2-5s: The clasp clicks open smoothly and the top leather flap settles naturally as the camera holds still on the open seam.
NO MUSIC. NO BACKGROUND SCORE. Native diegetic sound only.
```

## 4. Anti-IP & Phonetic VO Rewrites

- **Anti-IP:** Replace *"Blade Runner cyberpunk city"* → *"wet basalt street at night under mist-diffused amber sodium streetlights"*; *"Wes Anderson pastel café"* → *"symmetrical one-point interior, muted ochre walls, crisp flat daylight"*.
- **Phonetic VO:** Keep canonical spelling in `script.md` and captions; write phonetic pronunciation in TTS prompts per `brand.md` (`"Aethel"` → `"AY-thel"`, `"Kestrel"` → `"KES-trel"`), honoring `<= 2.0 wps` (Russian) / `<= 2.3 wps` (English) after `[PAUSE Ns]`.
