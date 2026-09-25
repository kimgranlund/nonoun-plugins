---
id: T-0068
title: "Board shows a closed task with no planner file as 'not planned'"
type: bug             # feature | bug | chore | spike | idea
status: ready     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
---

## Goal
A closed ticket's task row reads as closed, not 'not planned'.

## Repro
1. Exact command or steps, from a clean checkout.

## Expected

## Actual
Paste the output or error verbatim.

## Context
Live T-0047 run: after `close`, the status line and board showed `add-tests not planned`, since the task had step results but no planner file. A done ticket should render as done.

## Constraints
The failing test lands before or with the fix, never after.
