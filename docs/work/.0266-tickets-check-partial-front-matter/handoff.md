---
id: T-0266
title: "tickets.py check breaks on partial front matter"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-05
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`tickets.py check` reports partial front matter as a finding instead of breaking.

## Context
`tickets.py check` breaks on a ticket whose front matter is partial, for example `status: done` with no `id`. Expected a single clear finding naming the file. Add a regression case to the tickets selftest.

## Constraints
No push, tag, version bump, or publish. No em dashes.

## Closed

2026-10-06: delivered by the solo agent (tier S); the ticket's own checks and the fanout gates passed
