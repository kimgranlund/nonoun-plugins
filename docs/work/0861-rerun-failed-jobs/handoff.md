---
id: T-0861
title: "check.sh reruns only failed or affected jobs after a fix"
type: feature        # feature | bug | chore | spike | idea
status: claimed     # proposed | ready | claimed | paused | blocked | done | dropped (build progress lives in /board)
size: L2             # L1 | L2 | L3 | L4 (L5 reserved)
priority: P2         # P1 | P2 | P3
depends: [T-0858, T-0860]          # T-NNNN, file:<path>, cap:<name>; e.g. [T-0002]
created: 2026-11-19
claimed_by: nonoun-author 2026-11-19
branch: lane/T-0861-t0861
worktree: ../sdlc-lite.worktrees/T-0861-t0861
router: .sdlc/AGENTS.md  # how to claim and close this ticket
---

## Goal
After a fix during a release or a land, one command reruns only the jobs that failed or that the fix touches, not the whole suite.

## Intent
- Do: record each full run's per-job result, and add `check.sh --rerun` that runs the failed jobs plus the jobs `check_select.py` picks for files changed since that run.
- Non-goals: changing what a first full run does.
- Done when: the criteria below hold.

## Context
- User feedback 2026-11-19 (see T-0858). Release 1.0.7 ran the full 10-minute suite twice because one job (`check.py`) failed the first time.
- T-0858 landed `check_select.py select <path>...` and `check.sh --changed`; T-0860 landed sharded jobs. `check_pool.py` runs the jobs.
- Design: a full or `--fast` run writes `.sdlc/runtime/check-last.json` (git-ignored; confirm `.sdlc/runtime/` is ignored): the commit sha, a hash of the tracked tree plus dirty files, and each job's name, exit code and seconds. `check.sh --rerun` reads it, selects failed jobs plus `check_select.py` jobs for paths changed since the recorded state, runs them, and prints `rerun: <k> of <N> jobs; <m> passed earlier at <sha>`. It refuses with a clear line when there is no record, or when the record is from another branch tip that is not an ancestor. When the selection is every job, it says so and runs the full suite. The record is updated so a second `--rerun` after a clean one says `nothing to rerun`.
- The release rule: a release is green when the latest record shows every job ok for the release tree, by a full run or a full run plus reruns. State that in `plugins/sdlc/AGENTS.md` and in `.claude/agents/nonoun-author.md` "Running waves" rule 11 (one sentence; that file is the maintainer session's instructions, edit nothing else there). Run scripts with `export SDLC_ALLOW_STALE_PLUGIN=1`. Read `plugins/sdlc/AGENTS.md` first.

## Do
1. Write the run record from `check_pool.py` or `check.sh`.
2. Add `--rerun` with its refusals, and selftest cases in `check_pool.py` or `check_select.py`.
3. Document it and add the CHANGELOG `[Unreleased]` line.

## Acceptance criteria
- Selftest cases cover: a record with one failed job reruns only it; a changed leaf script adds its job; no record refuses; a clean rerun then says `nothing to rerun`. The selftest exits 0.
- Live: in a throwaway worktree, run `check.sh --fast`, break one fast job's input, run `--fast` again (red), fix it, run `check.sh --rerun`: it runs fewer jobs than `--fast` and exits 0. Put the three summary lines in the report.
- `bash plugins/sdlc/scripts/check.sh --changed $SDLC_BASE_SHA` exits 0 and `git diff --check` is clean.

## Constraints
- A job that never ran green for the recorded tree is never reported as passed.
