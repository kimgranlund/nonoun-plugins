---
id: T-0132
title: "Planner batches its criterion probes into one Bash call per step"
type: chore           # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-26
---

## Goal
Planner runs keep rule 1's criterion probing but use fewer requests and less context.

## Intent
- Do: change rule 1 in plugins/sdlc-lite/agents/planner.md so the planner runs all of one step's criterion probes in a single Bash call that prints, per criterion, its label, exit code, and at most the first 5 lines of output. Keep read-only probing and the red-now / green-guard semantics (rules 1 and 11 otherwise unchanged).
- Non-goals: any model or effort change; changes to run.sh level tables; changes to other agents.
- Done when: the rule is updated; plugins/sdlc-lite/scripts/check.sh passes; one live planner L2 run on a dry-run copy of a small existing ticket handoff (not committed) records fewer than 11.5 turns, with its turns and cost noted for the filer.

## Context
Cost investigation, 2026-09-26: planner L2 went from $0.54 to $0.79 a run in this repo (8.2 to 11.5 turns) and from $0.69 to $1.12 in the user's transcripts, after 0.7.0 added planner rule 1 (probe each criterion). Fix: agents/planner.md rule 1 says to run all of a step's probes in one Bash call, printing each criterion's label, exit code, and at most the first 5 lines of output. Keep read-only probing and the red-now/green-guard semantics.

Done when:
- The rule is updated.
- check.py still passes.
- One live planner L2 run on a small existing ticket handoff (dry run copy, not committed) shows fewer turns than the 11.5 average. Record its turns and cost in the filer notes.

Do not change any model or effort.

## Constraints
No model or effort changes. Rule 1's read-only probing and red-now/green-guard semantics stay. The live measurement copy lives outside .sdlc tickets (for example under /tmp) or is removed afterward, and is never committed.

## Plan review
- steps.py split refused planner-L2.md: step 1 criteria `grep -qF 'tagged` and `grep -qF '11. A` do not parse (a backtick inside a code span ends the span). plan defect: replan this step (/chain 3). Avoid backticks inside criterion commands.
