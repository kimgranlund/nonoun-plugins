---
id: T-0189
title: "Lean chain: fewer, coarser planner builder verifier steps for size M work"
type: chore           # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-03
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Planner, builder, verifier granularity is excessive.

## Intent
- Do: A size-M ticket can run with one or two coarse steps, one batched verification, and an optional plan review, with the rules for when the full chain is still required. The /fix fast lane already covers size S.
- Non-goals: building before a reviewed design; weakening independent verification.
- Done when: a design doc exists in docs/, an independent review passed, and a build ticket set is filed.

## Context
Feedback from another repo using SDLC Lite (2026-10-03, pasted by the maintainer): "Planner, builder, verifier granularity is excessive."

## Constraints
Design first (docs), independent review, then build. Related: T-0191, T-0192.

## Closed

2026-10-04: Superseded by build tickets T-0194, T-0193, T-0208 from the lean SDLC design (docs/lean-sdlc/design.md v0.4), reviewed twice. No work was built under this ticket.
