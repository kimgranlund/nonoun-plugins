---
id: T-0020
title: "board.py hides tickets by the hardcoded statuses dropped and done..."
type: idea            # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-24
from: T-0015
---

## Goal
One or two sentences: the outcome, not the method.

## Context
Follow-up from T-0015 (board-hides-closed-tickets/filer-L1.md):

board.py hides tickets by the hardcoded statuses `dropped` and `done`, so if tickets.py adds a new ticket status, update the filter to handle it.

## Constraints
What must not change. "None" if none.
