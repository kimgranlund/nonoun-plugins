<!-- role=verifier level=L1 model=opus effort=medium -->
## Verdict
pass

## Criteria
- `grep -qF 'BASH_DEFAULT_TIMEOUT_MS:-' plugins/sdlc-lite/scripts/fanout.py`: pass. Evidence: exit 0 on the built tree, where the match is at fanout.py:647. In a throwaway worktree at HEAD it exits 1, so the check can go red.
- `grep -qF 'BASH_MAX_TIMEOUT_MS:-' plugins/sdlc-lite/scripts/fanout.py`: pass. Evidence: exit 0 on the built tree, where the match is at fanout.py:648. At HEAD it exits 1.
- (guard) `python3 plugins/sdlc-lite/scripts/fanout.py selftest`: pass. Evidence: on the built tree it prints `fanout selftest: PASS` and exits 0. It is also green at HEAD.
  - Negative control: I copied the built fanout.py into the base worktree and changed the driver env at line 507 to `BASH_DEFAULT_TIMEOUT_MS="5"`. The selftest then went red: `fanout selftest: FAIL ... T-0001 merged in alpha, got ('alpha', 'driver failed rc=1')`, with the same failure for T-0002.
  - This shows the new stub lines really check what the driver is given. The variable that makes it go red is the value of `BASH_DEFAULT_TIMEOUT_MS` in the env passed at fanout.py:506-507.

## Out of scope changes
None.
- The diff for this step is 2 added lines in fanout.py, at 647-648, next to the `SDLC_HEADLESS` check (`git diff plugins/sdlc-lite/scripts/fanout.py`).
- `run.sh` and `run-selftest.sh` are also modified. The step-1 handoff (Bash timeouts in run.sh, recorded in the run-selftest.sh stub) and the step-2 handoff (run.sh report saving) call for those changes. Both steps have builder and verifier results in their dirs.
- `.sdlc/` changes are task bookkeeping.

## For the next attempt
None
