---
id: T-0475
title: "steps.py lint warns on a history-shaped criterion (T-0470 finding 1)"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-12
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`steps.py lint` warns `history-shaped criterion` on a criterion span that counts or greps commit subjects, so the plan reviewer sees it before a builder does.

## Repro
Lint a step handoff holding ``git log --oneline $SDLC_BASE_SHA..HEAD | grep -c 'feat: x' | grep -qx 3``.

## Expected
A `history-shaped criterion` warning.

## Actual
Exit 0, no finding.

## Context
Origin: T-0470 investigation, `docs/reports/2026-10-12-maison-wave-7b-mechanics.md`. Report item 1 (spans: `git log`, `git rev-list --count`, `grep -c` on `--oneline` output). Red check: a `steps.py selftest` lint case. Advisory only; the state-form criterion wording in the planner prompt is T-0461 scope.

## Constraints
The failing test lands before or with the fix, with an observed-red control. No prompt wording change.
