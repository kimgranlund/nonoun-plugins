---
id: T-0274
title: "run.sh lane gate"
type: chore           # feature | bug | chore | spike | idea
status: done     # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
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

## Acceptance criteria
Re-verify of the failed criteria only (first verdict: .sdlc/0274-lane-gate/verifier-L3-first.md.txt; other criteria passed and are not re-run). The fix commit is HEAD on branch lane-gate; diff it against its parent.
5. fanout.py sets SDLC_LANE_OVERRIDE for a `--driver` run and a forced `--lane full` run, and leaves it unset for `--lane auto` on a size L ticket; observe it in a driver log with a stub driver in a throwaway repo (the first run's method).
7. plugins/sdlc-lite/skills/fix/SKILL.md step 3 no longer dead-ends: following it (append the `- lane: fix` line to skips.md, then `run.sh builder L1 .sdlc/<slug>/step-1/handoff.md` on a size S ticket with id and no planner result, dry run) exits 0, and the same dry run without the line exits 5.
8. A dry run with SDLC_LANE_OVERRIDE set does not write skips.md.

## Closed

2026-10-05: delivered solo; run.sh lane gate, selftest red then green, independent L3 verifier (two rounds)
