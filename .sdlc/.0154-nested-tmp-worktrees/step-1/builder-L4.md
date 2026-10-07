<!-- role=builder level=L4 model=opus effort=xhigh -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/reap-tmp-worktrees.sh` (new, mode 755): reaps `<toplevel>/.worktrees/tmp/<role>-<pid>` dirs whose pid is dead, per the handoff. The header states the contract.
- `plugins/sdlc-lite/scripts/run.sh`:
  - New `reap_tmp` call before the stray snapshot, and again in `cleanup_worktrees` after the run's own prefix is removed. Both are real runs only.
  - The role now runs in the background and run.sh waits on it (`role_pid`).
  - New `stop_role` runs first in `on_exit`: TERM, up to 2 s of polling, KILL, wait. Cleanup comes after it.
  - Header gains "Prompt TERM" and "Reaper" paragraphs.
  - Exit codes 130/143/129, the non-zero-exit message plus `exit 1`, and the `{ ... }` group are unchanged.
- `plugins/sdlc-lite/scripts/run-selftest.sh`: new `stale prefix` and `term cleanup` cases after the `want_wt` cases, both described in the header. They drive run.sh only.
- `docs/references/sdlc-internals.md`: the run.sh paragraph now covers the prompt TERM cleanup and `reap-tmp-worktrees.sh` (dead-owner prefixes, called at start and exit).

## Checks
- `bash plugins/sdlc-lite/scripts/run-selftest.sh` (guard): `run selftest: PASS`, rc 0. Ran twice, the second time after the last reaper edit.
- `test -x plugins/sdlc-lite/scripts/reap-tmp-worktrees.sh`: rc 0.
- `grep -qF reap-tmp-worktrees.sh plugins/sdlc-lite/scripts/run.sh`: rc 0.
- `grep -qF 'fail "stale prefix:' plugins/sdlc-lite/scripts/run-selftest.sh`: rc 0.
- `grep -qF 'fail "term cleanup:' plugins/sdlc-lite/scripts/run-selftest.sh`: rc 0.
- Base-failure criterion (the exact command in the handoff): rc 0. The output was `run selftest: FAIL: stale prefix: dead-owner prefix builder-14856 is still on disk`.
- Extra control: base plugin with the stale-prefix block removed from the copied selftest gave `FAIL: term cleanup: a worktree under .worktrees/tmp is still registered: .../wrepo/.worktrees/tmp/builder-18438/w`. The term case fails at base on its own.
- Extra control: the fixed run.sh with the `stop_role` call removed gave `FAIL: term cleanup: the stub claude (pid 24822) is still alive`. The liveness assertion catches a missing role stop.
- `grep -qF reap-tmp-worktrees.sh docs/references/sdlc-internals.md`: rc 0.
- `bash -n plugins/sdlc-lite/scripts/reap-tmp-worktrees.sh`: rc 0.
- `python3 plugins/sdlc-lite/scripts/lifecycle-selftest.py`: `Ran 6 tests ... OK`, rc 0.
- `python3 plugins/sdlc-lite/scripts/check.py`: rc 0.
- `git diff --check`: rc 0.
- Direct reaper probe using plain dirs under `$SDLC_TMP_WORKTREES`, removed afterwards:
  - With no `ps` on PATH, all dirs were kept.
  - With `ps`, the dead-owner dir was removed; the live-owner and non-matching dirs were kept.
  - A missing toplevel and no args both exited 0.
- shellcheck: not installed, not run.

## Notes
- One addition beyond the handoff: the reaper exits 0 without reaping when `ps` is not on PATH. Without it, every owner would read as dead and a concurrent live run's prefix would be removed.
- The reaper skips symlinked entries under `.worktrees/tmp`, so a link cannot send worktree removal outside the prefix.
- The term-cleanup stub runs `trap '' TERM` and then `exec sleep 30`. The exec keeps the stub's pid, and sleep inherits the ignored TERM. This forces the more-than-5-s path at base, and no orphaned sleep is left.
- The term-cleanup case also asserts exit code 143, which holds at base and with the fix.
- With the fix, the term case takes about 2 s. At base it takes about 5 s, until run_lifecycle's SIGKILL.
- A background command in non-interactive bash starts with SIGINT and SIGQUIT ignored. run_lifecycle only ever sends TERM to the group, and run.sh's own INT trap still stops the role with TERM, so no path relies on the role getting INT.
- The worktree-level probe of the reaper (nested `git worktree add`) was blocked by `block-stray-worktree.sh` before anything ran. The selftest's `stale prefix` case covers that path through run.sh.
