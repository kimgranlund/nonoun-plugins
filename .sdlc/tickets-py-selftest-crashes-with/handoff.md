---
id: T-0028
title: "tickets.py selftest crashes with FileNotFoundError when run from a..."
type: idea            # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-24
from: T-0022
---

## Goal
One or two sentences: the outcome, not the method.

## Context
Follow-up from T-0022 (tickets-py-roadmap-skips-the/filer-L1.md):

tickets.py selftest crashes with FileNotFoundError when run from a copy outside the plugin dir, so negative controls from a temp copy cannot show clean per-case failures

## Constraints
What must not change. "None" if none.
