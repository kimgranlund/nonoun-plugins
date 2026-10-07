---
id: T-0028
title: "tickets.py selftest crashes with FileNotFoundError when run from a..."
type: idea            # feature | bug | chore | spike | idea
status: dropped
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
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

## Triage
2026-09-24, user-approved: niche; selftest runs from any cwd while it lives in the plugin.
