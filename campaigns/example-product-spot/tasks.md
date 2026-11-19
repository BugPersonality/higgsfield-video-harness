# Tasks: Nord Atelier Soren Weekender — Morning Departure 15s Spot

status: ready
Intent: intent.md
Treatment: treatment.md
Script: script.md
Storyboard: storyboard.md
Shotlist: shotlist.json
Completion: Assemble a verified 15-second 480p draft cut (`media/exports/draft_cut.mp4`) within the 140-credit Draft cap for Gate 2 requester review, then render approved 1080p final clips, normalized `media/exports/master.mp4`, and separated `media/exports/stems/` within the 260-credit Final cap.
Global constraints: Route every paid Higgsfield generation and upload through `scripts/hf_guard.py`; enforce Draft cap <= 140 credits, Final cap <= 260 credits, Max auto-retries/shot <= 2; honor Risk-First Pilot by proving `s02` (`test_take_check`) before parallel Wave 4 (`T04a`, `T04b`); workers never self-approve visual QA (Root Orchestrator dispatches fresh read-only `reviewer-agent` for Visual Critic and Delivery Review); keep raw video clips free of music bleed (`NO MUSIC. NO BACKGROUND SCORE. Native diegetic sound only.`); commit only text specs, prompts, manifests, receipts, and JSON QA reports.

## Tasks

- [ ] T01: Upload Soren Weekender product reference photos via hf_guard.py upload and record upload IDs [reference]
  Depends on: none
  Packet: tasks/T01-upload-references.md

- [ ] T02: Generate reference-locked keyframe stills for s01, s02, and s03 for Visual Critic review [still]
  Depends on: T01, budget-envelope [effect:spend]
  Packet: tasks/T02-generate-stills.md

- [ ] T03: Run Risk-First Pilot 480p draft workflow clip for s02 and produce QA artifacts for test_take_check review [pilot]
  Depends on: T02 [acceptance], budget-envelope [effect:spend]
  Packet: tasks/T03-pilot-s02-draft.md

- [ ] T04a: Generate 480p draft workflow clip for s01 and produce contact sheet for Visual Critic review [video]
  Depends on: T02, T03 [acceptance], budget-envelope [effect:spend]
  Packet: tasks/T04a-draft-s01.md

- [ ] T04b: Generate 480p draft workflow clip for s03 and produce contact sheet for Visual Critic review [video]
  Depends on: T02, T03 [acceptance], budget-envelope [effect:spend]
  Packet: tasks/T04b-draft-s03.md

- [ ] T05: Generate 15s ambient cello-piano score, assemble 480p draft cut, and prepare Gate 2 review package [assembly]
  Depends on: T03, T04a [acceptance], T04b [acceptance], budget-envelope [effect:spend]
  Packet: tasks/T05-music-and-assemble-draft.md

- [ ] T06: Render approved 1080p final workflow clips for s01, s02, and s03 for Visual Critic verification [video]
  Depends on: T05 [acceptance], user-draft-gate [effect:approve-draft], budget-envelope [effect:spend]
  Packet: tasks/T06-final-1080p-renders.md

- [ ] T07: Assemble 1080p master and stems, validate render QA, and hand off for independent Delivery Review [assembly]
  Depends on: T05, T06 [acceptance]
  Packet: tasks/T07-assemble-master-and-delivery.md
