---
id: T-0190
title: "Organize every .sdlc/ content type into topic sub-folders"
type: chore           # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-03
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The .sdlc/ folder should always organize all contents in topic-specific sub-folders.

## Intent
- Do: Every content type under .sdlc/ (tickets, messages, runs and role artifacts, notes, evals, proposals) lives in its own sub-folder with an entry file, and .sdlc/ itself holds only entry files and config. T-0175 made tickets/ opt-in; this makes the layout the default and migrates consumers.
- Non-goals: building before a reviewed design; weakening independent verification.
- Done when: a design doc exists in docs/, an independent review passed, and a build ticket set is filed.

## Context
Feedback from another repo using SDLC Lite (2026-10-03, pasted by the maintainer): "The .sdlc/ folder should always organize all contents in topic-specific sub-folders."

## Constraints
Design first. Must keep ID-stable references, the citing-file scan, fanout and traces working, and give consumers a migration command.

## Closed

2026-10-04: Superseded by build tickets T-0204 to T-0207 from the lean SDLC design (docs/lean-sdlc/design.md v0.4), reviewed twice. No work was built under this ticket.
