<!-- role=verifier level=L1 model=opus effort=medium -->
## Verdict
pass

## Criteria
- (guard) `bash plugins/sdlc-lite/scripts/hook-live-probe.sh --selftest`: pass. Evidence: on the built tree it printed `hook live probe selftest: PASS` with exit 0 (`probe=0`). I checked that it can fail: in a throwaway worktree at HEAD under `$SDLC_TMP_WORKTREES` I copied in the built probe and it passed (`intact=0`). I then changed the Agent deny in `block-background.sh` to `if false; then`, and it went red: `hook live probe selftest: FAIL: (f) agent missing plus false: exit 1, want 0 (verdict: FAIL: agent deny: hook exit code 0, not 2)`, exit 1. The part that fails is the check that the Agent deny exits 2.
- (guard) `bash plugins/sdlc-lite/scripts/hook-selftest.sh`: pass. Evidence: on the built tree it printed `hook selftest: PASS` with exit 0. With the same broken Agent deny in the throwaway worktree it exited 1 (`hookselftest_broken=1`).
- (guard) `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`: pass. Evidence: on the built tree it printed `ok: 18 role levels, 8 agents checked` with exit 0. In the throwaway worktree I changed the builder L5 row in CLAUDE.md to Opus, and it went red: `FAIL CLAUDE.md: builder:L5 = Opus xhigh, run.sh = Fable xhigh`, `FAIL: 18 role levels, 8 agents checked`.
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`: pass. Evidence: a full foreground run on the built tree exited 0 (`check_sh=0`). The tail shows the steps, order, fanout, run, hook, and hook live probe selftests all `PASS`, plus `ok: shellcheck` and `ok: plugin validate`. check.sh can fail: every sub-check sets `fail=1` on red, and the script ends with `exit $fail` (plugins/sdlc-lite/scripts/check.sh:9-21 and its last line). Its parts check.py, hook-selftest.sh, and hook-live-probe.sh --selftest each went red in the negative controls above.

## Out of scope changes
None. Step 3 changed no files. The builder says so, and `git status` / `git diff --stat` show only four modified tracked files: hook-live-probe.sh, CLAUDE.md, sdlc-lite-author.md, and the task handoff.md, plus untracked .sdlc task artifacts. All of these belong to steps 1 and 2 of this task (the `--agent` probe and its docs). I read the CLAUDE.md and sdlc-lite-author.md diffs: they document only `--agent` mode, and the two copies agree. `bash -n` on the probe script is clean. Draft finding: "the builder made no change, so there's nothing to verify." Steelman: the step's Do only asks for fixes if a gate is red, and all four gates are green in my own runs. Dropped.

## For the next attempt
None
