<!-- role=verifier level=L2 model=opus effort=high -->
## Verdict
pass

## Criteria
- #1 a `fanout.py` or `plan_done.py` selftest case that fails before the fix and passes after (observed red): pass. Evidence: the new case is at plugins/sdlc-lite/scripts/fanout.py:3636-3658. It puts an uncommitted, gitignored `verifier-L3.md` and `runs.jsonl` in a host-style `worktree-agent-w1` worktree, then asserts that `land` merges and that `fanout/w:.sdlc/t1/verifier-L3.md` exists. A control (w2, no record) must still be refused with `no verifier result`. Red check: in a throwaway worktree at HEAD (.worktrees/tmp/0439-verifier-L2/red), I deleted only the `commit_lane_records(ctx, t)` call in `land_ticket`. `python3 plugins/sdlc-lite/scripts/fanout.py selftest` then gave rc=1 with one failure, `case 23 land worktree record: an uncommitted verifier result in the lane worktree is carried in, got rc=1 ... | agent-w1 | T-0001 | no verifier result (commit the verifier result on the branch, then land again) |`. Green check: the same command on the built tree gave rc=0, `fanout selftest: PASS`, with no FAIL lines. The fix is `commit_lane_records` at fanout.py:1825-1836, called at fanout.py:1847 before the verdict check. `lane_wt` comes from the porcelain worktree list at fanout.py:1789. The run-rules text matches it (skills/run-plan/references/run-rules.md:37).
- #2 `check.sh` exits 0: pass. Evidence: `bash plugins/sdlc-lite/scripts/check.sh` on the built tree gave rc=0 in 15:19. Its log contains `fanout selftest: PASS` and no failed check (`cost_estimate selftest: 25 ok, 0 failed`).

## Out of scope changes
None. The diff 7d5cc740..HEAD touches only plugins/sdlc-lite/scripts/fanout.py (the fix, its docstring line and the selftest case) and plugins/sdlc-lite/skills/run-plan/references/run-rules.md (line 37, the run rule the handoff names). The untracked files are the run's own dispatch and record files in the ticket folder.

## For the next attempt
None
