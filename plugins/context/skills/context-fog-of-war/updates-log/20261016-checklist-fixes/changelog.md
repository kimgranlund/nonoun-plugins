---
date: 2026-10-16
slug: checklist-fixes
requested_by: Kim Granlund
harness: Claude Code CLI (sdlc-lite 0.24.0 conductor session)
authors:
  - role: solo
    agent: sdlc-lite:solo-L2
    model: claude-opus-5-5
    did: edited SKILL.md (routing table Visualize cell for runtime-harness bundles, checklist steps 1, 4 and a new step 10) and wrote this entry
  - role: verifier
    agent: sdlc-lite:verifier-L2 (fog-skill-checklist-fixes-verifier-L2)
    model: claude-sonnet-5-5
    did: independent verification, verdict pass
  - role: conductor
    agent: sdlc-lite conductor (main session)
    model: claude-opus-5-5
    did: wrote the task handoff and dispatched the solo; edited no skill file
project: agent-ui (nonoun), task .sdlc/work/fog-skill-checklist-fixes/handoff.md
verification: independent verifier L2 pass (2026-10-16); skill tests 20 of 20
backup: /private/tmp/claude-501/scratch/cfow-backup-1792159498
---

# 2026-10-16: autonomous checklist fixes from the round 6 field test

Closes four Open items of updates-log/20261016-round-6-field-test/changelog.md.

## Added
- SKILL.md checklist step 10: turn each useful failure into a keyless replay pinned to its failing checks (references/learnings/test-loop.md lesson 24), named as the project's step when the project has a replay mechanism.

## Changed
- SKILL.md checklist step 1: a bundle run reuses a mapping manifest from a prior run's record (the project's fog records, or the mapping the previous report cites) before writing a new one.
- SKILL.md checklist step 4: when the mapping cannot carry pass and fail verdicts, cluster from the per-run reports outside the bundle and cite them as outside the bundle.
- SKILL.md routing table, runtime-harness bundle, Visualize cell: hydrate the ingest session.json (checklist step 6), then `fog.py validate`, then `library.py publish`.
- SKILL.md: the deliverable step renumbered from 10 to 11, with the step references in the checklist intro and stop rule updated.

## Fixed
- None.

## Open
- Learnings, validation-and-repair: the candidate lesson "a check that exists can still be too narrow; test each check against the live failure that motivated it" waits for a second project.
- The 2026-10-16 script fixes (`lookup_request`, `wrapped.py`) are still unproven on a real trace with tool calls.
