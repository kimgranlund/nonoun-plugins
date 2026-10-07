---
id: T-0066
title: "/file files a follow-up that duplicates an existing ticket in different words"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
---

## Goal
/file flags a follow-up that restates an existing open ticket, before it is filed.

## Repro
1. Exact command or steps, from a clean checkout.

## Expected

## Actual
Paste the output or error verbatim.

## Context
Live T-0047 run, 2026-09-25: the filer's `calc.div raises an unhandled ZeroDivisionError when b == 0` was filed as T-0003 although T-0002 `div crashes on zero divisor` was open. close only skips exact normalized-title or slug duplicates, and /file step 3.2 compares follow-ups only against the task's own artifacts. Fix: step 3.2 also reads open ticket titles and marks likely duplicates for dropping, with the matching id.

## Constraints
The failing test lands before or with the fix, never after.
