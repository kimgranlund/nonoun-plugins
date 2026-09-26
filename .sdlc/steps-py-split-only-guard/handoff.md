---
id: T-0094
title: "steps.py split --only guard check cannot see changes guards make to..."
type: idea            # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
from: T-0083
---

## Goal
One or two sentences: the outcome, not the method.

## Context
Follow-up from T-0083 (guards-in-steps-py-split/filer-L1.md):

steps.py split --only guard check cannot see changes guards make to gitignored files (logs, caches), so a side-effecting guard that writes only ignored paths still passes silently.

## Constraints
What must not change. "None" if none.

## Closed

2026-09-26: User decision 2026-09-26: keep ignoring gitignored paths in the split --only guard check (guards write caches and logs routinely; refusing would raise false plan defects). Documented limitation, per T-0083's design.
