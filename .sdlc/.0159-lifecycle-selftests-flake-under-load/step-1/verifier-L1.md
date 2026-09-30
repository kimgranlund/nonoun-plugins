<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- Load simulation (every child `python3` start delayed 11 s), three named race tests: pass. Evidence: I ran the handoff command on the built tree. All 3 tests reported ok, "Ran 3 tests in 273.407s, OK". I ran the same command in a detached worktree at `$SDLC_BASE_SHA` (7334f49). It was red there: 2 FAIL and 1 ERROR, "FAILED (failures=2, errors=1)". So the check bites.
- No fixed one- or two-digit timeout or poll deadline remains: pass. Evidence: I ran the negated grep against both files and it exited 0 with no matches. A read of the diff shows every `timeout=N` became `DEADLINE` or `fixture.DEADLINE`, and both `monotonic()+10` polls were replaced by `wait_for`.
- Timeout failure message shows the watched directory's listing and the child's returncode and stderr: pass. Evidence: `codex-selftest.py`, `wait_for`/`state()` (lines 52-71 of the diff). The message includes the reason, `directory ...: sorted listing`, `observed: describe()`, and the owner's returncode. The owner's stderr is added once the owner has exited. If the owner exits first, it fails at once instead of waiting for the deadline.
- (guard) `lifecycle-selftest.py`: pass. Evidence: rc=0, "Ran 6 tests in 6.545s, OK".
- (guard) `codex-selftest.py`: pass. Evidence: rc=0, "Ran 20 tests in 12.034s, OK".
- (guard) Negative control against the pre-c78e9b5 `run_lifecycle.py`: pass. Evidence: sha c78e9b5 was found. In the copied tree the selftest failed with "AssertionError: 0 != 1" and "FAILED (failures=2)". So the negated command is green and the selftest can go red.
- (guard) Only the two selftest files changed: pass. Evidence: the command exited 0. `git status` shows only `codex-selftest.py` and `lifecycle-selftest.py` modified, plus untracked files under `.sdlc`.
- (guard) No untracked files outside `.sdlc`: pass. Evidence: the command exited 0.
- (guard) `git diff --check`: pass. Evidence: exit 0, no output.
- Do items: stub sleeps, `role('timeout')`, and `SDLC_CODEX_TIMEOUT_SECONDS`: pass. Evidence: both timeout stubs now `time.sleep(600)`. `role('timeout')` still sets `SDLC_CODEX_TIMEOUT_SECONDS='1'`, at `codex-selftest.py:79`. The native and conductor exchange tests set `str(DEADLINE)` (lines 321 and 345). I did not re-verify the builder's claim about `codex_exec.py` killing the stub on timeout. However, `pgrep` for `sdlc native test|scout-L1` found no leftover processes after all runs, and the run reached its normal end.

## Out of scope changes
None. `git diff --stat` shows only the two selftest files. The untracked `.sdlc` files are task artifacts.

## For the next attempt
None
