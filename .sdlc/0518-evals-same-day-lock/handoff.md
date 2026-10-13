---
id: T-0518
title: "evals.py lock: a later-numbered eval on the same date may supersede the lock"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-12
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`evals.py lock` accepts a new eval whose date equals the locked eval's date when its number is higher, so two model decisions on one day do not need a date trick.

## Repro
1. Lock the table to an eval dated 2026-10-12 (`0006`).
2. Change a model row, add `0007` dated 2026-10-12, run `evals.py lock --eval .sdlc/evals/0007-...md`.

## Expected
The lock moves to 0007: it is the later record by number.

## Actual
`eval ... date 2026-10-12 is not later than the cited eval ... date 2026-10-12; a changed table needs a new eval` (`evals.py` `not_later`, lines 273 to 275, 375 and 486). Seen twice on 2026-10-12: the builder change had to reset the lock file by hand and re-lock an edited 0006.

## Context
Rule today: `date <= old_date` refuses. Change to: refuse when the new date is earlier than the old date, or equal and the new number is not greater. `evals.py check` (line 375, previous_eval) uses the same rule and changes the same way.

## Constraints
Red check: an `evals.py selftest` case (refused today): same date, higher number locks; same date, lower or equal number still refuses; an earlier date still refuses. Do not weaken the rule that a changed table needs a new eval.
