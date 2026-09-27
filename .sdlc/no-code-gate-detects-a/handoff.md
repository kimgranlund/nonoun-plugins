---
id: T-0140
title: "No code gate detects a full-suite guard placed on a non-final step..."
type: idea            # feature | bug | chore | spike | idea
status: ready     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-26
from: T-0124
---

## Goal
One or two sentences: the outcome, not the method.

## Context
Follow-up from T-0124 (inherited-red-gate-steps/filer-L1.md):

No code gate detects a full-suite guard placed on a non-final step; the planner-L2 handoff notes rule 14 lives only in the prompt and check.py only proves the phrase's presence, not that planners follow it — worth deciding whether a heuristic check (e.g. flag a non-final step whose guard command matches the project's declared whole-gate command) is worth building.

## Constraints
What must not change. "None" if none.
