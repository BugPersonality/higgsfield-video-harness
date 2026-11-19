# T01 — Upload Soren Weekender Product Reference Photos

## Outcome

Verify the three local daylight reference photographs for the Soren Weekender 40L exist and are unobstructed, upload each through `scripts/hf_guard.py upload` (recording 0-credit upload receipts in `receipts.jsonl`), and report their remote `upload_id` values in `qc/T01-references.json` for the Root Orchestrator to persist into `shotlist.json`.

## Depends on

- none

## Sources

- ../intent.md
- ../shotlist.json
- ../../../brands/example-brand/brand.md

## Provides

- Verified remote `upload_id` mappings for `ref_bag_front`, `ref_clasp_macro`, and `ref_bag_profile` recorded in `qc/T01-references.json` and logged at `0.0` credits in `receipts.jsonl`.

## Boundary

Do not generate stills, spend generation credits, or alter creative prompts. Stop and reopen if any local reference file is missing or violates matte leather / brushed brass invariants.

## Mutable owners

- `qc/T01-references.json`

## Exclusive locks

- `receipts.jsonl`

## Final validation

- Confirm all three reference images exist locally under `media/references/` with non-zero file size and valid image dimensions via `ffprobe`.
- Run `python3 scripts/hf_guard.py upload --campaign campaigns/example-product-spot --file campaigns/example-product-spot/media/references/bag_hero_front.jpg --ref-id ref_bag_front` (and matching `hf_guard.py upload` calls with `--ref-id ref_clasp_macro` and `--ref-id ref_bag_profile` for `clasp_macro.jpg` and `bag_worn_profile.jpg`).
- Confirm `qc/T01-references.json` records non-empty remote `upload_id` strings for `ref_bag_front`, `ref_clasp_macro`, and `ref_bag_profile`.
- Confirm zero generation credits were consumed (`python3 scripts/hf_guard.py status --campaign campaigns/example-product-spot --json`).

## Reopen if

Any reference photo is missing, shows glossy flash glare or wrong leather colorway, or fails Higgsfield upload authentication.
