---
id: T-0222
title: "fanout solo lane closes: write the ## Skipped entries the T-0219 skips guard needs"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-04
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The bug is fixed and a test that failed before the fix passes after it.

## Repro
1. Exact command or steps, from a clean checkout.

## Expected

## Actual
Paste the output or error verbatim.

## Context
Where it was found (file:line, story id, session). Suspected cause, marked as a guess.

## Constraints
The failing test lands before or with the fix, never after.

## Closed

2026-10-04: Fixed: fanout.py writes the planner and filer ## Skipped entries when a solo lane starts, so the T-0219 skips guard accepts the close by reason; guard unchanged. Selftest case 16 runs the real lane decision and real close with a negative control; live rerun of 4 lanes closed all four (hidden check 24/24); skill lane count and overlap-limit docs fixed. Independent L3 verifier passed 7 of 7.
