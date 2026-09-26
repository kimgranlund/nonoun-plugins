---
id: T-0093
title: "Check the steps.py || lint allowance against the merge guards peers..."
type: idea            # feature | bug | chore | spike | idea
status: ready     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
from: T-0082
---

## Goal
One or two sentences: the outcome, not the method.

## Context
Follow-up from T-0082 (criteria-or-fallback/filer-L1.md):

Check the `steps.py` `||` lint allowance against the merge guards peers actually use. It only exempts the exact form `test $# -eq 0 ||`, which was inferred from the ticket because this repo has no such form, so a peer using a different empty-argument short circuit would get its valid plan refused as a plan defect.

## Constraints
What must not change. "None" if none.
