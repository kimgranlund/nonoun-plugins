<!-- role=verifier level=L2 model=opus effort=high -->
## Verdict
pass

## Criteria
- #1 `fleet_collect.py selftest` exits 0 and prints both T-0445 ok lines: pass. Evidence: on the built tree `python3 plugins/sdlc-lite/scripts/fleet_collect.py selftest` exited 0 and printed `ok: interrupted: an attempt whose result file holds a verdict is not counted` and `ok: negative control: an interrupted attempt whose result holds no verdict is still counted`. Red control: in a throwaway worktree at base 7bec36a8, I copied in the built scripts and removed the 2-line guard in `collect_runs` (fleet_collect.py:478-479). The selftest then exited 1 with `FAIL: interrupted: an attempt whose result file holds a verdict is not counted` and `FAIL: negative control: ...`. Second control: I patched `results.attempt_reported` to return true whenever `<stem>.md` exists, verdict or not. Only `FAIL: negative control: an interrupted attempt whose result holds no verdict is still counted` went red, so the negative control catches over-skipping on a result file that has no verdict.
- #2 `dispatch.py selftest` exits 0 and prints both lines: pass. Evidence: on the built tree it exited 0 and printed `ok: recover leaves a dead-parent attempt whose result holds a verdict alone (T-0445)` and `ok: recover marks it interrupted with run_lifecycle.py text`. Red control: removing the guard at dispatch.py:478-479 in the base copy gave exit 1 with `FAIL: recover leaves a dead-parent attempt ... (T-0445)` and `FAIL: recover marks it interrupted with run_lifecycle.py text`. When `attempt_reported` was forced to always return true, the negative control and 4 other recover cases failed, so it catches over-skipping.
- #3 `results.py selftest` exits 0: pass. Evidence: exited 0 and printed `results selftest: PASS`. The new `attempt_reported` (results.py:172-178) only adds code; `key_value` is unchanged.
- #4 `fleet_collect.py collect . --since 2026-10-11` reports `runs.interrupted.lost_min_total` 0: pass. Evidence: on the built tree `runs.interrupted` = `{"count": 0, "attempts": [], "lost_min_median": null, "lost_min_total": 0}`. The same command at base 7bec36a8 gave `1364.7`, which matches the ticket's before value. The base copy with the fix stripped also gave `1364.7`. The two phantom files `.sdlc/.0431-*/verifier-L3.attempt.json` and `.sdlc/.0432-*/verifier-L3.attempt.json` still hold `"status": "interrupted"` next to their `verifier-L3.md`. The collector fix alone zeroes them, so no repair commit was needed (the Non-goals allow this).
- #5 `bash plugins/sdlc-lite/scripts/check.sh` exits 0: pass. Evidence: exit 0. The output ends with `run selftest: PASS`, `hook selftest: PASS`, `hook live probe selftest: PASS`, `ok: shellcheck`, `ok: plugin validate`, and has 0 `^FAIL` lines. `git diff --check` is clean.

## Out of scope changes
None.
- `docs/kpi/002-restart-recovery-minutes.md`: the Excluded line now names the case where a result file already holds a verdict. The Constraints allow a K-002 edit if the definition text is now wrong. I read the diff: the old text would misdescribe what the collector counts after this fix, so the edit is in scope.
- `.sdlc/0445-*/handoff.md`: the solo builder added `## Acceptance criteria`, as solo.md:48 requires when a handoff has none. Each criterion traces to the Do and Done-when.
- `results.py` gains an exported `attempt_reported`. `git grep attempt_reported -- plugins` finds no consumers beyond fleet_collect.py and dispatch.py. Both selftests and check.sh are green.
- Process note, not a criterion: criteria #1 and #2 pin exact strings. Per solo.md:48 that calls for a `verifier: L3` line in the handoff, which is absent, so this check ran at L2.

## For the next attempt
None
