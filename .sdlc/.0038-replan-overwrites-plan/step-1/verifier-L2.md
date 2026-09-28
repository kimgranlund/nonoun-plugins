<!-- role=verifier level=L2 model=fable effort=medium -->
## Verdict
pass

## Criteria
- `bash plugins/sdlc-lite/scripts/run-selftest.sh` exits 0 and prints `run selftest: PASS`: pass. Evidence: ran in the worktree, output `run selftest: PASS`, `exit=0`.
- Red-then-green with only run.sh reverted: pass. Evidence: instead of stashing (forbidden for this role) I made a throwaway worktree at HEAD `cd15ee7` (run.sh unchanged), copied only `run-selftest.sh` in, ran it: `run selftest: FAIL: planner-L3.md does not hold 'run 1', it was overwritten: <!-- role=planner level=L3 model=fable effort=xhigh --> ## Goal run 3`, `exit=1`. Worktree removed afterwards (`git worktree list` shows only the two originals). The biting variable is the `if [[ -e "$dir/$name.md" ]]` numbering block at run.sh:48-53; the failing assertion is the `grep -qx "run 1"` content check, so the red discriminates an overwrite, not a missing file.
- `board.py selftest` prints PASS; reverting only `level_of` makes a new case fail: pass. Evidence: `python3 plugins/sdlc-lite/scripts/board.py selftest` → `board selftest: PASS`, `exit=0`. In a temp copy with `level_of` restored to `return p.stem.split('-')[-1]` (grep at line 64-66 confirms), the selftest printed `board selftest: FAIL, these did not hold: - level_of(builder-L3-2.md) is L3, got '2' - newer builder-L3-2.md (done) renders built · builder L3, got 'built · builder 2, awaiting verify'`, `exit=1`. The `plan_steps` newest-file case did not go red under this revert because it depends on the mtime glob, not `level_of`; it is still a real check of the numbered file being picked (`got == [(1, 'only', 'L2')]` pins the value).
- Dry run names: pass, with the criterion's L3 half read by the Do-section rule. Evidence: dir holds only `planner-L2.md/.log`; `SDLC_DRY_RUN=1 run.sh planner L3 …` printed a command whose prompt names `planner-L3.md`; `… planner L2 …` names `planner-L2-2.md`. The criterion text asks for `planner-L3-2.md` "because `planner-L3.md` is not present", which contradicts the Do section ("Keep `$role-$level.md` when that file does not exist yet") and the task goal. The L2 half is the behavior under test and it holds. No files were created by the dry runs (`ls` before and after identical).
- `check.sh` exits 0 with the run selftest PASS line and `ok: shellcheck`: pass. Evidence: output tail `… board selftest: PASS / run selftest: PASS / ok: shellcheck / ok: plugin validate`, `exit=0`. shellcheck at `--severity=warning` covers `scripts/*.sh`, so the new selftest is included.

Code inspection: run.sh:47-55 picks the lowest free k >= 2 and sets both `result` and `log` from `$name`; the `.running` marker still uses `$role-$level` (not in the diff, so unchanged). check.sh:12 adds the selftest line and the header at lines 2-4 mentions it. board.py:64-67 `level_of` matches `-(L\d)(?:-\d+)?$` with the old split as fallback.

## Out of scope changes
- `.sdlc/0038-replan-overwrites-plan/handoff.md`: a `## Paths (added by the conductor)` section appended. Attributed to the conductor in the text, not the builder; harmless but outside the step.
- Untracked run artifacts (`planner-L2.*`, `runs.jsonl`, `step-1/`, `step-2/`): normal chain output.
- Docs still say a rerun overwrites (CLAUDE.md, handoff-format, chain); the builder notes these are step-2's job, consistent with the plan.

## For the next attempt
None. One item for the planner: the L3 dry-run criterion in this handoff is self-contradictory (`planner-L3-2.md` when `planner-L3.md` is absent); rephrase to expect `planner-L3.md` when absent and `-2` once it exists.
