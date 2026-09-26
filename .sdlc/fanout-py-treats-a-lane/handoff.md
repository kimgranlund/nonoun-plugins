---
id: T-0115
title: "fanout.py treats a lane that ends on an inherited red builder like..."
type: idea            # feature | bug | chore | spike | idea
status: ready     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
from: T-0101
---

## Goal
One or two sentences: the outcome, not the method.

## Context
Follow-up from T-0101 (builder-inherited-red/filer-L1.md):

`fanout.py` treats a lane that ends on an `inherited red` builder like any other non-merged outcome; decide whether lane reports should name the inherited tests so the cause is visible.

## Constraints
What must not change. "None" if none.
