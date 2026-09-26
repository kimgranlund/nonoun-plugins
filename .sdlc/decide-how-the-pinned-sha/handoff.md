---
id: T-0110
title: "Decide how the pinned-sha lint should handle a deliberate commit..."
type: idea            # feature | bug | chore | spike | idea
status: ready     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
from: T-0100
---

## Goal
One or two sentences: the outcome, not the method.

## Context
Follow-up from T-0100 (planner-parallel-safe-criteria/filer-L1.md):

Decide how the pinned-sha lint should handle a deliberate commit reference such as `git merge-base --is-ancestor <real sha> HEAD`, which is now refused with no escape hatch.

## Constraints
What must not change. "None" if none.
