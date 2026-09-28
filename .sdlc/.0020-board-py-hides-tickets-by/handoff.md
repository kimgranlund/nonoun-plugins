---
id: T-0020
title: "board.py hides tickets by the hardcoded statuses dropped and done..."
type: idea            # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-24
from: T-0015
---

## Goal
A new ticket status added to tickets.py can never silently get the wrong board visibility: board.py's selftest fails until someone decides whether the new status is shown or hidden.

## Context
Follow-up from T-0015 (board-hides-closed-tickets/filer-L1.md):

board.py hides tickets by the hardcoded statuses `dropped` and `done`, so if tickets.py adds a new ticket status, update the filter to handle it.

## Intent
Literal ask: board.py hides tickets by the hardcoded statuses `dropped` and `done`, so if tickets.py adds a new ticket status, update the filter to handle it.
Deltas:
- Conditional ask, no new status exists today: defaulted: deliver a guard that forces the update when one is added, not a behavior change now.
- Wrong unit (a reminder is not enforcement): defaulted: board.py declares every tickets.ENUMS['status'] value as shown or hidden in one place, and its selftest fails when that set differs from tickets.ENUMS['status'].
- Unknown status at runtime (a hand-edited or future value): defaulted: stays visible, as today.
Do: in plugins/sdlc-lite/scripts/board.py, replace the literal 'dropped'/'done' checks in belongs_on_board with named module-level sets (hidden always: dropped; hidden when no step work: done; shown: proposed, ready, blocked) and add a board.py selftest case asserting their union equals set(tickets.ENUMS['status']) with no overlap, plus a negative control proving the check fails when tickets.ENUMS['status'] gains a value. Update CLAUDE.md or skills/board docs only if they describe the filter in a way this changes.
Non-goals: changing which statuses are hidden; changing tickets.py.
Done when: board.py selftest and scripts/check.sh pass; the new case fails when a status is added to tickets.ENUMS['status'] without classifying it; existing dropped/done filter tests still pass unchanged.

## Constraints
Current visibility for all five statuses must not change. Unknown statuses stay visible.
