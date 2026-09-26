---
id: T-0118
title: "The reference scan matches only the literal toplevel-relative path..."
type: idea            # feature | bug | chore | spike | idea
status: ready     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
from: T-0113
---

## Goal
One or two sentences: the outcome, not the method.

## Context
Follow-up from T-0113 (close-rename-breaks-refs/filer-L1.md):

The reference scan matches only the literal toplevel-relative path `<rel>/<slug>`, so relative (`../NNNN-x/`) or absolute-path references to the ticket folder are missed and still break on rename.

## Constraints
What must not change. "None" if none.
