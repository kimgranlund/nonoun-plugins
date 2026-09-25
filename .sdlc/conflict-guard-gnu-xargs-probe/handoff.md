---
id: T-0070
title: "Run the merge-step conflict-marker guard probe under GNU xargs (Linux)"
type: idea            # feature | bug | chore | spike | idea
status: ready     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
from: T-0064
---

## Goal
One or two sentences: the outcome, not the method.

## Context
Follow-up from T-0064 (merge-step-conflict-marker-guard/filer-L1.md), filed by hand because `tickets.py close` marked it a duplicate of T-0064 itself (see T-0071):

Merge-step conflict-marker guard's xargs empty-input branch was checked only on macOS (BSD xargs); run the check.py probe under GNU xargs (Linux) to confirm the `test $# -eq 0` path.

## Constraints
What must not change. "None" if none.
