---
id: T-0191
title: "One plan record per ticket; later roles do not repeat research or planning"
type: chore           # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-03
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Excessive planning docs when using progressive context. No need to write docs for the whole trace. Keep things simple, economical, and make sure the next step does not repeat research and planning already done.

## Intent
- Do: One plan record per ticket that later roles read and append to, each role reading only the prior result and the files it cites, so no role repeats scouting or planning. Measure files and tokens written per ticket before and after.
- Non-goals: building before a reviewed design; weakening independent verification.
- Done when: a design doc exists in docs/, an independent review passed, and a build ticket set is filed.

## Context
Feedback from another repo using SDLC Lite (2026-10-03, pasted by the maintainer): "Excessive planning docs when using progressive context. No need to write docs for the whole trace. Keep things simple, economical, and make sure the next step does not repeat research and planning already done."

## Constraints
Design first. Touches handoff-format, the planner and filer contracts, steps.py, and check.py.

## Closed

2026-10-04: Superseded by build tickets T-0200 to T-0202 from the lean SDLC design (docs/lean-sdlc/design.md v0.4), reviewed twice. No work was built under this ticket.
