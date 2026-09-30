<!-- role=verifier level=L1 model=opus effort=medium -->
## Verdict
pass

## Criteria
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`: pass. Evidence: I ran it on the built tree and it exited 0 (`rc=0`). The output includes "run selftest: PASS", "hook selftest: PASS" and "ok: plugin validate". `grep -cE "FAIL\b|Traceback"` on the log returned 0. shellcheck printed "skip: shellcheck not installed", which comes from the harness, not the step. To confirm the gate can go red, I made a throwaway worktree at HEAD (`$SDLC_TMP_WORKTREES/base`) and applied the step diff there. I then took out only the new `{` after `set -euo pipefail` and the closing `exit 0\n}` from run.sh. `bash plugins/sdlc-lite/scripts/run-selftest.sh` then exited 1 with "run selftest: FAIL: self-edit: run.sh exited 1, want 0 (run_lifecycle: runner exited 0 but wrote no result ...)". So check.sh, through run-selftest, covers the step's new behavior.
- (guard) `python3 scripts/check-packaging.py`: pass. Evidence: exit 0, with the output "PASS: catalog parity, identity, skill routes, hook isolation and context links".
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`: pass. Evidence: exit 0, with the output "Codex agent definitions verified".
- (guard) `git diff --check`: pass. Evidence: exit 0 on the built tree with no output. To confirm it can go red, I added a trailing-whitespace line to docs/maintenance/sdlc-internals.md in the throwaway worktree and it exited 2. After I undid that change it exited 0. I removed the worktree afterwards with `git worktree remove --force` (rm=0).

## Out of scope changes
None. The builder's own report says it changed nothing in this step ("## Changes None"). The working-tree diff is 5 files: run.sh, run_lifecycle.py, run-selftest.sh, lifecycle-selftest.py and docs/maintenance/sdlc-internals.md. These are the steps 1 and 2 changes to the runner and its tests, plus the internals doc entry. I read the run.sh diff: a self-edit comment, the `{ ... }` wrapper ending in `exit 0`, and an update to the exit-code comment. All of it is in the task's scope.

## For the next attempt
None
