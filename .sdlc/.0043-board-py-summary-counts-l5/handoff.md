---
id: T-0043
title: "board.py summary counts L5 runs with the glob step-/builder-L5..."
type: idea            # feature | bug | chore | spike | idea
status: dropped
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-24
from: T-0038
---

## Goal
One or two sentences: the outcome, not the method.

## Context
Follow-up from T-0038 (replan-overwrites-plan/filer-L1.md):

`board.py summary` counts L5 runs with the glob `step-*/builder-L5.*`, which assumes the first L5 run is always named `builder-L5.md`; it should also match numbered `builder-L5-<k>.md` reruns.

## Constraints
What must not change. "None" if none.

## Triage
2026-09-24, user-approved: covered by T-0049 (newest result from run order, not mtime).
