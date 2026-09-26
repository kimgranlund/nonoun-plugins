---
id: T-0132
title: "Planner batches its criterion probes into one Bash call per step"
type: chore           # feature | bug | chore | spike | idea
status: ready     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-26
---

## Goal
Planner runs keep rule 1's criterion probing but use fewer requests and less context.

## Intent
- Do:
- Non-goals:
- Done when:

## Context
Cost investigation, 2026-09-26: planner L2 went from $0.54 to $0.79 a run in this repo (8.2 to 11.5 turns) and from $0.69 to $1.12 in the user's transcripts, after 0.7.0 added planner rule 1 (probe each criterion). Fix: agents/planner.md rule 1 says to run all of a step's probes in one Bash call, printing each criterion's label, exit code, and at most the first 5 lines of output. Keep read-only probing and the red-now/green-guard semantics.

Done when:
- The rule is updated.
- check.py still passes.
- One live planner L2 run on a small existing ticket handoff (dry run copy, not committed) shows fewer turns than the 11.5 average. Record its turns and cost in the filer notes.

Do not change any model or effort.

## Constraints
What must not change. "None" if none.
