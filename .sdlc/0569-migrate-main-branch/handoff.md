---
id: T-0569
title: "migrate script takes main from the first worktree's branch"
type: bug             # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L1             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0563]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-10-15
claimed_by: claude 2026-10-15
branch: lane/T-0569-t0569
worktree: ../sdlc-lite.worktrees/T-0569-t0569
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
The worktree migration judges "landed" against the repo's default branch, not the branch of the first worktree.

## Repro
1. A repo whose primary checkout is on a non-default branch (maison: `candidate-8`), with lanes under `.worktrees/`.
2. Run `migrate-0.23.sh` (or `migrate-worktrees.sh` after T-0563).

## Expected
Lanes are tested against the default branch: `tickets.py` `default_branch()` gives origin/HEAD's target, else `main`, else `master`.

## Actual
`migrate-0.23.sh:50` sets `main` from the first `git worktree list` entry's branch, so maison's landed checks ran against `candidate-8` (maison conductor report, 2026-10-15).

## Context
After T-0563, `migrate-0.23.sh` is a wrapper and the logic lives in `migrate-worktrees.sh`; fix it there. Reuse `default_branch()` from `tickets.py` (around line 1545), or the same origin/HEAD, main, master order in shell.

## Constraints
The skip-unlanded rule is unchanged. Only the base it compares to changes.

## Acceptance criteria
1. `bash plugins/sdlc-lite/scripts/migrate-worktrees.sh --selftest` exits 0. Its new case puts the primary checkout on `candidate` with a lane landed on `main` but not on `candidate`; the lane moves rather than being skipped. The case failed before the fix.
2. `git diff --check` exits 0.
