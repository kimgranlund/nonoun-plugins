---
id: T-0296
title: "steps lane refuses size M over 20 criteria"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-06
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`steps.py lane` refuses size M, and prints a split suggestion, when the ticket has more than 20 acceptance criteria.

## Context
Maison T-0137 was sized M for a 134-row epic; its verifier failed at the cost of one solo run. File: plugins/sdlc-lite/scripts/steps.py `lane` (before planning, the size alone decides). Count checkbox lines (`- [ ]`, `- [x]`) under `## Acceptance criteria` of the task handoff. Over 20 with size S or M: print lane `full` with a `reason:` line `ticket lists N criteria (limit 20 for size S or M); split it into tickets of at most 20`. Twenty or fewer is unchanged.

## Acceptance criteria
- [ ] `python3 plugins/sdlc-lite/scripts/steps.py selftest` exits 0 with new cases: size M with 21 criteria prints `full` with the split reason; size M with 20 prints `solo`.
- [ ] Negative control shown once: without the check the 21 case prints `solo`.
- [ ] docs/maintenance/sdlc-internals.md `steps.py lane` text and docs/lean-sdlc/design.md lane section name the 20-criteria limit.

## Closed

2026-10-06: delivered by the solo agent (tier S); the ticket's own checks and the fanout gates passed
