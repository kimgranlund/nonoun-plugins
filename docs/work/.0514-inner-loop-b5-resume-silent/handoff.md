---
id: T-0514
title: "dispatch.py resume accepts a running attempt whose transcript is silent (T-0501 B5)"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-12
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`dispatch.py resume` accepts a `running` attempt whose transcript is silent and prints the ladder: ask by name, ask by id, then `prune --add` and a new attempt at the same level with the resume addendum.

## Repro
1. A running attempt with a stored agent id and a transcript dated 2 hours back (the T-0476 case).
2. `dispatch.py resume <dispatch.json>`.

## Expected
The ladder prints; the conductor picks the rung.

## Actual
`resume` refuses any attempt that is not `orphaned` or `interrupted` (`dispatch.py:610-611`), and a silent one is `running`.

## Context
Design: `docs/planning/inner-loop-profile.md`. Opt-in by `profile: inner-loop` in `.sdlc/config`; a repo that does not declare it sees no change. No relaunch at a lower level: model and effort are user decisions, and the stall cause was host load. Uses `SILENT_SECONDS` (`dispatch.py:556`, `:580-586`).

## Constraints
Red check: a `dispatch.py selftest` case (refused today). No change for a live, recently written attempt.

## Closed

2026-10-12: delivered by the solo agent (level L1); the ticket's own checks and the fanout gates passed; gate: full
