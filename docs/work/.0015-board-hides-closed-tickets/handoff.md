---
id: T-0015
title: "board lists dropped and unplanned done tickets"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-24
---

## Goal
/board shows the live set only: tasks with steps in flight or done in the current work, not dropped tickets or closed tickets that never had steps.
## Repro
1. Exact command or steps, from a clean checkout.

## Expected

## Actual
Paste the output or error verbatim.

## Context
Since T-0009 the board reads ticket front matter; with 14 tickets it renders every dropped and not-planned ticket as a row (see `board.py --root .sdlc`). Status in front matter (dropped, done) is enough to filter on.

## Constraints
The failing test lands before or with the fix, never after.
