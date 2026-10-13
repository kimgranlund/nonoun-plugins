---
id: T-0536
title: "Catch a criterion that needs a later step, and a narrow amend route for a builder-reported plan defect (maison T-0546)"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L3             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0533]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-13
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Catch a criterion that needs a later step, and a narrow amend route for a builder-reported plan defect.

## Intent
- Do: find where a criterion that can only pass after a later step can be caught cheaply: a planner self-check, a plan-reviewer instruction to run each step's criteria against the tree state that step will see, or a `steps.py lint` rule for criteria naming files or tests a later step owns. Choose from evidence, state the rejected options.
- Do: a narrow route to amend one criterion of one unbuilt step after a builder reports a plan defect, mirroring `steps.py swap` for the verifier case: bounded to one criterion, recorded, and counted against the one-replan cap.
- Non-goals: removing the full replan route.
- Done when: `steps.py selftest` covers the amend route (positive, and a refusal when the step is already built) and the chosen order check has a positive case and an observed negative control.
- Full chain reason: changes next-action decisions in `steps.py`, a behavioral invariant.

## Context
maison T-0546 observations 35, 36: `/Users/kimgranlund/Projects/maison/ui-kit-maison/.sdlc/tickets/0546-sdlc-lite-work-record-improvements/observations.md` (section "Added after the author's reply"). Read only; never edit maison.

## Constraints
A new or changed check needs a positive case and an observed negative control.
