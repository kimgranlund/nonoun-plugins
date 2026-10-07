---
id: T-0192
title: "Conductor rule: finish work the fastest way, batch reviews and verifications"
type: chore           # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-03
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The conductor should always consider how to complete work in the fastest, most efficient way possible, including batching reviews.

## Intent
- Do: A conductor rule and checks for batching plan reviews and verifications, merging adjacent steps, running independent tickets in parallel worktrees, and skipping roles whose risk does not justify them, with each skip recorded. The whole-branch verifier used for T-0175 to T-0181 is the model.
- Non-goals: building before a reviewed design; weakening independent verification.
- Done when: a design doc exists in docs/, an independent review passed, and a build ticket set is filed.

## Context
Feedback from another repo using SDLC Lite (2026-10-03, pasted by the maintainer): "The conductor should always consider how to complete work in the fastest, most efficient way possible, including batching reviews."

## Constraints
Smallest of the four and could land first. A skip never removes the verifier for L4/L5 steps or merge steps.

## Closed

2026-10-04: Superseded by build tickets T-0195 to T-0199, T-0203 from the lean SDLC design (docs/lean-sdlc/design.md v0.4), reviewed twice. No work was built under this ticket.
