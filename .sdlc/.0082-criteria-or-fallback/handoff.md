---
id: T-0082
title: "Planner: ban || fallbacks in criteria; lint them in steps.py split"
type: bug             # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: S              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
---

## Goal
A criterion with an `||` fallback between checks is refused before any build.

## Repro
1. Exact command or steps, from a clean checkout.

## Expected

## Actual
Paste the output or error verbatim.

## Context
From peer setup-sdlc-lite-generative-ui (gen-ui-system-svelte-lite T-0164 step 3, on 0.7.0): the criterion `grep A || grep B` could not fail, because B matched prose even at HEAD. The verifier failed the build twice, and the chain escalated the builder to L4, which then blocked with plan defect. Already in 0.7.0: planner.md rule 1 (run each criterion on the current tree, and it must fail now) and verifier.md's `plan defect:` route. Their run did not use the verifier route. Still missing: an explicit ban on `||` fallbacks in the planner rules, plus a `steps.py split` lint that refuses as plan defect a criterion command joining two checks with `||`. The merge-step guard's `test $# -eq 0 ||` form needs an allowance.

## Constraints
The failing test lands before or with the fix, never after.
