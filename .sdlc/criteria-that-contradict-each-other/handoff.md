---
id: T-0062
title: "Criteria that contradict each other, and criteria that are not red..."
type: idea            # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
from: T-0060
---

## Goal
One or two sentences: the outcome, not the method.

## Context
Follow-up from T-0060 (unpassable-plan-criteria/filer-L1.md):

Criteria that contradict each other, and criteria that are not red now, are caught only by the planner prompt. The static lint would not have caught T-0029's stray quote, which sat inside a double-quoted pattern and still parsed. Consider a code check that runs `(guard)` criteria against the current tree before the split.

## Constraints
What must not change. "None" if none.
