---
id: T-0274
title: "run.sh lane gate"
type: chore           # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-05
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
run.sh refuses a planner, builder, or plan-reviewer run on a ticket whose `steps.py lane` is solo (exit 5, prints the solo_run.py command) unless SDLC_LANE_OVERRIDE gives a reason, so solo is the easy path and full-chain use is recorded.

## Intent
- Do: gate in scripts/run.sh after the Goal precheck; read-only `steps.py lane --check`; override line in skips.md and a lane_override field in runs.jsonl; one conductor line; sdlc-internals entry; run-selftest case.
- Non-goals: gating scout, researcher, architect, archaeologist, verifier, filer; version files; release reports.
- Done when: planner on a size S ticket exits 5 without the override and proceeds with it; a full-lane ticket is not gated; check.sh is green.

## Context
Pre-run hook point: the 0.20.9 Goal precheck in plugins/sdlc-lite/scripts/run.sh. Fanout forced lanes and a chain that already recorded a non-solo lane are not gated.

## Constraints
No push, tag, publish, version bump. No em dashes.
