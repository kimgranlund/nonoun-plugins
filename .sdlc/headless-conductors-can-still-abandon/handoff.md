---
id: T-0076
title: "Headless conductors can still abandon work through the Agent tool's..."
type: idea            # feature | bug | chore | spike | idea
status: ready     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
from: T-0072
---

## Goal
One or two sentences: the outcome, not the method.

## Context
Follow-up from T-0072 (headless-background-abandon/filer-L1.md):

Headless conductors can still abandon work through the Agent tool's `run_in_background`, which defaults to background. `block-background.sh` matches only Bash, so extend the guard to Agent in headless sessions.

## Constraints
What must not change. "None" if none.
