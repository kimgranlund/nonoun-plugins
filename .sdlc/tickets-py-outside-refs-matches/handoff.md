---
id: T-0128
title: "tickets.py outside_refs matches folder paths by fixed-string..."
type: idea            # feature | bug | chore | spike | idea
status: ready     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-26
from: T-0116
---

## Goal
One or two sentences: the outcome, not the method.

## Context
Follow-up from T-0116 (tickets-py-archive-renames-done/filer-L1.md):

`tickets.py outside_refs` matches folder paths by fixed-string prefix, so `.sdlc/0001-a` also matches `.sdlc/0001-ab`. `close` and `archive` can report or rewrite a citation of a different folder that shares the prefix.

## Constraints
What must not change. "None" if none.
