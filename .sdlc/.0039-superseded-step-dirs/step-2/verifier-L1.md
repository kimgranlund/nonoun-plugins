<!-- role=verifier level=L1 model=opus effort=medium -->
## Verdict
pass

## Criteria
- Temp bench fixture (`step-1/` with a passing `verifier-L1.md` and a builder `runs.jsonl` line costing 1.00, plus `step-1.superseded-1/` with a builder line costing 2.00): pass. Evidence: I built it under `mktemp -d` at `results/2026-01-01-t/`, exactly as specified.
- `SDLC_BENCH_DIR=<tmp> bench-summary.sh` shows steps=1, passed=1, attempts=1, cost=3.00: pass. Evidence:
  - Working tree output: `2026-01-01-t none 1 1 1 3` (exit 0).
  - The check fails on the old code. In a throwaway HEAD worktree the same fixture gives `none 2 1 2 3`, so the superseded dir was counted as a step and an attempt. That makes the new basename test at `bench-summary.sh:16` the part of the check that catches the bug.
  - Cost prints as `3` rather than `3.00`. The value matches, and the format comes from the unchanged jq `round / 100` at line 26, which also prints `3` at HEAD. Cost stays 3 in both versions, so the superseded dir's cost is still counted, as the step requires.
  - I also tested the replacement for the old `ls -t` pick of the newest verifier. When the newest file is a failing `verifier-L1-2.md`, passed=0. When that failing file is older, passed=1. HEAD behaves the same in both cases.
- `shellcheck plugins/sdlc-lite/scripts/bench-summary.sh` is clean: pass. Evidence:
  - Working tree: no output, exit 0.
  - HEAD copy: exit 1 with `SC2012 (info)` at the old `ls -t` line, so this check does go red.
  - `scripts/check.sh` also passes end to end (shellcheck, the selftests and plugin validate all ok, exit 0).

## Out of scope changes
None from this step. `git diff` also shows `plugins/sdlc-lite/scripts/board.py` and `.sdlc/0039-superseded-step-dirs/handoff.md` as changed. The board.py change belongs to step 1 of the same task (`step-1/` holds its builder and verifier artifacts), and the handoff edit is the task's own record. The only change this step made is `bench-summary.sh`: the skip, the comment, and the replacement for the `ls -t` pick asked for under Previous attempt. The cost line is unchanged.

## For the next attempt
None
