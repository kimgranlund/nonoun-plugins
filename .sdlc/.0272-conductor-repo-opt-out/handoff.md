---
id: T-0272
title: "Conductor honors a repo opt-out of delegation"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-05
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The conductor honors an explicit repo opt-out line instead of pipeline-first routing.

## Context
dom-charts has a repo AGENTS.md line, "No extra agents or delegation required", which conflicts with the conductor's pipeline-first routing. Proposal: the conductor recognizes a stated opt-out in the repo entry file, works solo in-session, and says so once. Decide the exact wording to match, and whether `steps.py lane` prints it.

## Constraints
No push, tag, version bump, or publish. No em dashes.

## Closed

2026-10-06: delivered by the solo agent (tier S); the ticket's own checks and the fanout gates passed
