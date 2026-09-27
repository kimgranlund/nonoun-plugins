---
id: T-0137
title: "The steps.py || lint accepts test -f a || exit 1 | cat, which is..."
type: idea            # feature | bug | chore | spike | idea
status: ready     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-26
from: T-0093
---

## Goal
One or two sentences: the outcome, not the method.

## Context
Follow-up from T-0093 (check-the-steps-py-lint/filer-L1.md):

The steps.py `||` lint accepts `test -f a || exit 1 | cat`, which is really `a || (exit 1 | cat)` and returns cat's status 0, so the criterion passes when the left side fails. Drop the lone `|` from `ends_command`, and the planner spec in Do item 1 that lists it.

## Constraints
What must not change. "None" if none.
