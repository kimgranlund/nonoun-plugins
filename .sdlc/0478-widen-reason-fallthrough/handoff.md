---
id: T-0478
title: "steps.py widen --reason records an unrecognized scope form (T-0470 finding 10)"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-12
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`steps.py widen --reason` records an explicit list under `## Scope widened` when the scope span has an unrecognized allow-list form, instead of refusing.

## Repro
`steps.py widen` on a step whose scope criterion is ``git diff --name-only $SDLC_BASE_SHA | grep -v -E '^(a|b)'`` with `--reason "conductor decision"`.

## Expected
`widen_recorded` with the reason.

## Actual
`plan defect: steps widen refused: the scope criterion has an unrecognized allow-list form` (`steps.py:3482-3484`).

## Context
Origin: T-0470 investigation, `docs/reports/2026-10-12-maison-wave-7b-mechanics.md`. Report item 10. The `--reason` route runs only when the step has no scope span (`steps.py:3462-3464`); recorded under `## Scope widened` (`steps.py:3536`). Red check: a `steps.py selftest` widen case.

## Constraints
The failing test lands before or with the fix, with an observed-red control. No prompt wording change.
