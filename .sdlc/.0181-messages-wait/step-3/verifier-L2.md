<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- AC1 (selftest prints `probe selftest: PASS` and each of the 12 labeled `ok:` lines): pass. Evidence: I ran the criterion's command verbatim with `SDLC_BASE_SHA` set and it exited 0. A separate run printed 12 `ok:` lines in the required order, then `probe selftest: PASS`, on Python 3.9.6. The negative controls below show the check can go red.
- AC2 (`BASH_DEFAULT_TIMEOUT_MS` and `BASH_MAX_TIMEOUT_MS` appear in probe.py): pass. Evidence: the verbatim loop exited 0. Both names are in `DROPPED_ENV` at probe.py:66-67, and `clean_env` deletes them at probe.py:111.
- AC3 (file exists and contains no em dash): pass. Evidence: the verbatim command exited 0.
- AC4 (scope guard against `SDLC_BASE_SHA`): pass. Evidence: the verbatim command exited 0. Tracked changes outside `.sdlc` are only the five allowed files. The only untracked file outside `.sdlc` is `probe.py`.
- Negative controls (the selftest can go red): pass. I mutated copies of probe.py under `$SDLC_TMP_WORKTREES` with a `plugins` symlink. The original file was not touched. Each mutation made the selftest fail on its own case:
  - Dropping the `wait_before_send=no` reason failed `fail: the wait started after the send`.
  - Dropping the `poll_calls` reason failed `fail: a count call`.
  - Disabling the `wait_returned` check failed `fail: the wait returned another id`.
  - Changing `wait_calls != 1` to `< 1` failed `fail: two wait calls`.
  - Ignoring `rollout_polls` failed `fail: a Codex write_stdin poll`.
  - Not counting backgrounded Bash failed `fail: a backgrounded wait call`. That case's reason list had no `poll_calls=1`, so the `st_fail` assertion fired on the planted defect.
- Do-section behavior I could check offline: pass.
  - Judge: the one `judge` function is called by both `run_arm` (probe.py:763) and `st_run` (probe.py:874).
  - PATH check: `PATH=/usr/bin:/bin python3 probe.py codex` printed `result=unverified reason=host cannot run: codex is not on PATH` and exited 3.
  - Output order and `PLUGIN` depth match the Do (probe.py:44). The live host commands and the prompt text match the Do (probe.py:69-74, 539-547).
  - `git diff --check` is clean.
- Live arm: not run. The step says to make no model call. The `run_arm` host launch, delayed send and Codex isolation controls are therefore unobserved here. The criteria do not require them, and step 4 covers them.

## Out of scope changes
None. The changed tracked files (`messages.py`, `messenger.md`, the codex toml, `sdlc-internals.md`, `design.md`) are on AC4's allow-list and come from steps 1 and 2. The untracked `docs/validation/messages-wait-live-run/probe.py` is this step's target. A probe run of mine left a temp project in `$TMPDIR` outside the repo. No project files were changed.

## For the next attempt
None.
