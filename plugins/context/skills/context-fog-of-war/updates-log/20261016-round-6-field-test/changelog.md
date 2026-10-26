---
date: 2026-10-16
slug: round-6-field-test
requested_by: Kim Granlund
harness: Claude Code CLI (sdlc-lite 0.24.0 conductor session)
authors:
  - role: solo
    agent: sdlc-lite:solo-L2 (0294-solo-L2)
    model: claude-opus-5-5
    did: ran the skill unaided on agent-ui live round 6 (87 runs) and drafted these findings in that round's report
  - role: verifier
    agent: sdlc-lite:verifier-L2 (0294-verifier-L2)
    model: claude-sonnet-5-5
    did: independent verification of the round 6 report, including the skill-improvements table, verdict pass
  - role: conductor
    agent: sdlc-lite conductor (main session)
    model: claude-opus-5-5
    did: wrote this entry from the verified report
project: agent-ui (nonoun), live round 6, report .sdlc/evals/rounds/2026-10-15-r6-matrix/report.md, fog report d242f3e13e7408d0d5327c38
verification: field test verified by an independent verifier (L2 pass); this entry records findings only, no skill file changed
backup: none (no skill file changed)
---

# 2026-10-16: field test of the autonomous checklist on a runtime-harness bundle

## Verified in the field
- Routing table: picked the runtime-harness bundle diagnose entry.
- Prerequisites block: the detectors' coverage lines matched what the traces record.
- Learnings: each of the six clusters mapped to a lesson, and the runtime-harness tags fit.
- Autonomous run checklist: partly. All 10 steps ran in order with no conductor step list, but the ticket supplied the points listed under Open.

## Open
- Checklist step 1: say where a reused mapping manifest is found (a prior run record or the project's records), not only "create or reuse".
- Checklist step 4: when the mapping cannot carry pass and fail verdicts (per-run reports outside the vocabulary), say to cluster from those files and cite them as outside the bundle.
- Checklist: add "turn each useful failure into a keyless replay" (learnings lesson 24) before step 10, or say it is the project's step.
- Routing table, runtime-harness bundle, Visualize cell: name hydrate and `fog.py validate` before `library.py publish`.
- Learnings, validation-and-repair: a candidate lesson, "a check that exists can still be too narrow (here a case-sensitive id match); test each check against the live failure that motivated it". Confirm on a second project before adding it.
- The 2026-10-16 script fixes (`lookup_request`, `wrapped.py`) are still unproven on a real trace: web-chat bundles have no tool calls.
