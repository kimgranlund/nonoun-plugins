---
id: T-0062
title: "Criteria that contradict each other, and criteria that are not red..."
type: idea            # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-25
from: T-0060
---

## Goal
`steps.py split --only N` runs that step's `(guard)` criteria against the current tree before writing its handoff, and refuses with a `plan defect` line when a guard is red now, so a plan whose guard cannot pass is caught before the build instead of by the verifier.

Done when: `split --only N` executes each runnable `(guard)` command span of step N (skipping spans that reference `HEAD^1` or contain a `<placeholder>`, each under a timeout), refuses and writes nothing on a red or timed-out guard with `plan defect` as the last stderr line naming the criterion, the full `split` (no `--only`) and `lint` still execute nothing, `steps.py selftest` proves each case (red guard refuses, green guard passes, HEAD^1 and placeholder guards skipped, timeout refuses, full split does not execute), and the docs that describe `split` (the `steps.py` usage text, CLAUDE.md, `.claude/agents/sdlc-lite-author.md`, `/chain` 4.2 and the plan-defect decision) say so. `scripts/check.sh` passes.

## Context
Follow-up from T-0060 (unpassable-plan-criteria/filer-L1.md):

Criteria that contradict each other, and criteria that are not red now, are caught only by the planner prompt. The static lint would not have caught T-0029's stray quote, which sat inside a double-quoted pattern and still parsed. Consider a code check that runs `(guard)` criteria against the current tree before the split.

## Decision (user, 2026-09-25)
Run `(guard)` criteria only in `steps.py split --only N` (the per-step split in /chain 4.2, right before that step's build). Skip guards that reference `HEAD^1` or hold a `<placeholder>`, run each with a timeout, and keep the full split execution-free. Contradicting criteria stay with the planner prompt.

## Constraints
- Full `split` and `lint` stay execution-free (user decision).
- Contradicting criteria stay with the planner prompt; no code check for them.
- Existing `plan defect:` tag format and `/chain` handling are unchanged; a guard refusal reuses them.

## Clarify gaps (unattended)
- Timeout length and the guard's working directory (project root vs. task dir) are not decided; pick a documented default (planner decides).
- How a `(guard)` criterion is marked in plan text: follow what `agents/planner.md` and `steps.py` already use.
