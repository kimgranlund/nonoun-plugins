---
id: T-0135
title: "Extend the clean-status lint in steps.py to catch a whole-tree..."
type: idea            # feature | bug | chore | spike | idea
status: ready     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-26
from: T-0125
---

## Goal
One or two sentences: the outcome, not the method.

## Context
Follow-up from T-0125 (criteria-no-porcelain-clean/filer-L1.md):

Extend the clean-status lint in steps.py to catch a whole-tree clean check not written as a `git status --porcelain` emptiness test (for example `git diff --quiet && ...` over the whole tree, or a script that hides it). The detector only matches span text.

## Constraints
What must not change. "None" if none.
