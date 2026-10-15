---
id: T-0587
title: "solo_run.py run --worktree without --cwd records the session checkout's base"
type: bug             # feature | bug | chore | spike | idea
status: proposed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: []          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-15
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
`solo_run.py run --worktree NAME` without `--cwd` records `base_sha` as the worktree's HEAD, matching the `tree` it records.

## Context
Found by the T-0578 solo (2026-10-15). `--worktree` without `--cwd` records `base_sha` from the session checkout's HEAD but `tree` as the worktree. A reused worktree that is already ahead would then carry a mismatched base. T-0578's tree check in `dispatch.py build_base` accepts it because the tree matches.

## Intent
- Do: take `base_sha` from the tree the solo will run in.
- Non-goals: other solo_run behavior.
- Done when: the criteria pass.

## Constraints
None.

## Acceptance criteria
1. `python3 plugins/sdlc-lite/scripts/solo_run.py selftest` exits 0. Its new case reuses a worktree whose HEAD is ahead of the session checkout: the dispatch's `base_sha` equals the worktree HEAD. The case failed before the fix.
2. `git diff --check` exits 0.
