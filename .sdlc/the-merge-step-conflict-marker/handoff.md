---
id: T-0089
title: "The merge-step conflict-marker guard misses a kept conflict-marker..."
type: idea            # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
from: T-0069
---

## Goal
One or two sentences: the outcome, not the method.

## Context
Follow-up from T-0069 (conflict-guard-lane-false-positive/filer-L1.md):

The merge-step conflict-marker guard misses a kept conflict-marker line that is textually identical to a parent line and aligns with it in the combined diff (shown as `+ `, not `++`). Add a probe case and decide whether to close the gap.

## Constraints
What must not change. "None" if none.
