---
id: T-0364
title: "A plan review whose findings are one-line Notes fixes does not trigger a replan"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-08
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
A plan review whose findings are one-line Notes fixes does not force a replan.

## Intent
- Do: In scripts/steps.py (replan and the review verdict handling) and agents/planner.md / plan-reviewer.md: when every plan-reviewer finding is marked a Notes-level fix (a one-line addition the builder can take from the handoff), the verdict passes with the findings folded into the step Notes instead of a replan. Keep the one-replan cap for real defects.
- Non-goals: model or effort changes; anything outside this finding.
- Done when:
  - A selftest: a review with only Notes-level findings passes with Notes appended; one with a real defect still replans (observed failing first).
  - check.py, tickets.py check, the affected selftests and both generate --check pass.

## Context
ultimate-tokens ran 6 planner runs and 3 plan reviews on geometry-maison-ladder; each review found small gaps (a guard contradicting a Do line, a test file with no owning step); planner L3 spend in that repo $67.84 in the window. Source: docs/reports/2026-10-08-fleet-retro-06.md (fleet retro 2026-10-08, filed by the user's choice). outcome metric: planner_results_per_ticket (fleet_detect.py), before: 6

## Constraints
No em or en dashes. No push or publish.
