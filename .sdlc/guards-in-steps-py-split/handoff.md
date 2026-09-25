---
id: T-0083
title: "Guards in steps.py split --only N really execute, so a guard..."
type: idea            # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
from: T-0062
---

## Goal
One or two sentences: the outcome, not the method.

## Context
Follow-up from T-0062 (criteria-that-contradict-each-other/filer-L1.md):

Guards in `steps.py split --only N` really execute, so a `(guard)` criterion with side effects now changes the tree before the build; only the planner prompt forbids that, and no code check does.

## Constraints
What must not change. "None" if none.
