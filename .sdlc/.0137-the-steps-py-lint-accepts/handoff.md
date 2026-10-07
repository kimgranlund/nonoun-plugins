---
id: T-0137
title: "The steps.py || lint accepts test -f a || exit 1 | cat, which is..."
type: idea            # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-26
from: T-0093
---

## Goal
The `steps.py` `||` lint refuses a nonzero-exit right operand that is piped (`test -f a || exit 1 | cat`, `... || { ...; exit 1; } | cat`), because the pipeline returns the last command's status and lets the criterion pass when the left side fails.

## Context
Follow-up from T-0093 (check-the-steps-py-lint/filer-L1.md):

The steps.py `||` lint accepts `test -f a || exit 1 | cat`, which is really `a || (exit 1 | cat)` and returns cat's status 0, so the criterion passes when the left side fails. Drop the lone `|` from `ends_command`, and the planner spec in Do item 1 that lists it.

## Constraints
Every form the lint accepts or refuses today, other than a pipe after the nonzero exit, keeps its result. T-0093's own handoff is a closed record and stays as written.
