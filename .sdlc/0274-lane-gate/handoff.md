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

## Acceptance criteria
Diff to verify: `git diff main..HEAD` (commit 4fc9e5b on branch lane-gate). Scope: plugins/sdlc-lite/scripts/{run.sh,steps.py,fanout.py,run-selftest.sh}, plugins/sdlc-lite/agents/conductor.md (+ generated codex toml), docs/maintenance/sdlc-internals.md, .sdlc/0274-lane-gate.
1. `bash plugins/sdlc-lite/scripts/run-selftest.sh` prints PASS.
2. Revert only run.sh gate (`git stash`-free: copy run.sh from main to a temp plugin copy, or inspect) and observe run-selftest.sh fails with "lane gate: planner on a size S ticket exited 0, want 5"; i.e. the new case bites.
3. In a throwaway git repo, planner/builder/plan-reviewer on a size S or M ticket (front matter with `id: T-NNNN`) exit 5 without SDLC_LANE_OVERRIDE, stderr holds `solo_run.py run --task-dir <dir> --tier <S|M>`, and no attempt record, runs.jsonl, or skips.md is written; with SDLC_LANE_OVERRIDE set the run proceeds, skips.md gets exactly one `lane override: <reason>` line (not duplicated on a second run) and the runs.jsonl line has `lane_override`.
4. Not gated: verifier, filer, scout, researcher, architect, archaeologist; a size L ticket; a handoff with no id; a skips.md whose last `lane:` line is not solo; SDLC_LIFECYCLE_CHILD runs.
5. fanout.py sets SDLC_LANE_OVERRIDE for forced `--lane full` or `--driver` full-kind tickets and otherwise leaves it unset; `steps.py lane --check` prints the lane and writes nothing, while plain `steps.py lane` still records.
6. No em dashes in the added lines; no version files or docs/reports/release-* touched.
