---
id: T-0858
title: "Make testing during incremental work isolated and parallel, not a slow sequential suite"
type: feature        # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-11-19
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
Testing during incremental work is fast and isolated, so a project does not stall on test ceremony.

## Intent
- Do: to be scoped with the user before work starts.
- Non-goals: none stated yet.
- Done when: to be scoped.

## Context
- User feedback, 2026-11-19, verbatim: "workflows for testing need to be improved and less sequential and slow. focus on isolated testing during incremental development work so that the project doesnt grind to a halt with excessive testing ceremony."
- Evidence from this repo: the full `check.sh` takes about 600 s for 58 jobs and a release ran it twice (release 1.0.7 report). Roles already run only the checks a criterion names; candidates for scoping are per-change test selection, parallel verifier checks, and when the full suite is required.

## Constraints
None stated.
