---
id: T-0286
title: "Supervisor reports orphaned dispatches"
type: feature        # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0279]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-06
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The supervisor status and the board show dispatches whose parent died, so an account switch or crash is visible without opening each ticket.

## Intent
- Do: Supervisor reports orphaned dispatches.
- Non-goals: anything outside this deliverable; a new idea is a new ticket.
- Done when:
  - `supervisor.py watch --once` writes an `orphans` list into `status.json` from `dispatch.py status --orphans` over the active ticket folders; a fixture with one orphan lists it and a fixture with a live parent lists none (negative control).
  - `board.py` renders an orphaned step as `🟡 orphaned · resume` and `supervisor.py selftest` and `board.py selftest` pass.
  - The supervisor still never claims, moves, or reads a message body (existing selftest cases pass unchanged).

## Context
Design section 6. Read-only: the supervisor reports, the conductor or the user resumes.

## Constraints
No new wake behavior. No em dashes. No push, tag, or publish.

## Closed

2026-10-06: delivered by the solo agent (tier S); the ticket's own checks and the fanout gates passed
