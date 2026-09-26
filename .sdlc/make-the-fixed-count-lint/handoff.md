---
id: T-0109
title: "Make the fixed-count lint skip a bare = assignment such as n=26..."
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

Make the fixed-count lint skip a bare `=` assignment such as `n=26`, which is currently flagged when the span also has a count tool and a glob, `ls` or `find`.

## Constraints
What must not change. "None" if none.
