---
id: T-0134
title: "Mirror the extended planner rules a guard seen red first..."
type: idea            # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-26
from: T-0123
---

## Goal
The Plan-defect route bullet in `.claude/agents/sdlc-lite-author.md` also states the extended planner rules that CLAUDE.md's plan-defect decision and `plugins/sdlc-lite/agents/planner.md` rules 11 and 12 carry: each `(guard)` is seen red first (un-negated, or on a fixture) so it can go red, and files other lanes change are checked by membership or structure, never by an exact line.

## Context
Follow-up from T-0123 (replan-light-criterion-swap/filer-L1.md):

Mirror the extended planner rules (a guard seen red first, membership or structure checks) into `.claude/agents/sdlc-lite-author.md`. The step 3 builder did not, and the file lists the plan-defect route the maintainer must keep in sync.

## Constraints
Only `.claude/agents/sdlc-lite-author.md` changes. Its existing wording stays; this adds to it. `plugins/sdlc-lite/scripts/check.sh` stays green.

## Plan review
swap applied: step 1: steps swap: step-1: old `git diff --stat HEAD | awk '{print $1}'` -> new criterion scoping changed and untracked files to outside .sdlc/ (verifier-L1.md)
