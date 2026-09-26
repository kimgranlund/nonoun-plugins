<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- A failing role run leaves no worktree behind: pass. Evidence: ran the handoff's command in a fresh repo. run.sh printed "builder exited non-zero", and the trailing worktree-count and `.worktrees/tmp` checks passed (`C1=0`). The check can go red: the bite run below shows a leftover worktree failing the same kind of assertion against HEAD's `run.sh`.
- A successful role run leaves no worktree behind: pass. Evidence: ran the handoff's command; it printed the result path and exited 0 (`C2=0`).
- `grep -q SDLC_TMP_WORKTREES plugins/sdlc-lite/scripts/run.sh`: pass. Evidence: `C3=0`.
- `grep -q SDLC_TMP_WORKTREES plugins/sdlc-lite/scripts/run-selftest.sh`: pass. Evidence: `C4=0`.
- (guard) `bash plugins/sdlc-lite/scripts/run-selftest.sh`: pass. Evidence: printed `run selftest: PASS`, `C5=0`. This ran with an inherited `SDLC_TMP_WORKTREES` set by the outer role run, so the new run.sh overrides it correctly.
- (guard) Dry run creates no `.worktrees`: pass. Evidence: the handoff's command exited 0 (`C6=0`).
- (guard) `shellcheck --severity=warning` on both scripts: pass. Evidence: no output, `C7=0`.
- The new selftest bites: pass. Evidence: made a throwaway worktree of HEAD, copied the new `run-selftest.sh` into it, and ran it against HEAD's `run.sh`. It printed `run selftest: FAIL: worktree ok run: leftover worktree: .../.worktrees/tmp/verifier-81444/w ...` and exited 1 (`BITE_rc=1`). The failure names a leftover worktree, as the criterion requires. Removed the throwaway worktree; `git worktree list` shows only the main checkout and tickets-18.
- Extra checks on the Do items:
  - TERM cleanup: a stub added a worktree and slept. TERM sent mid-run gave exit 143 and left no `.worktrees`.
  - Prefix scoping: an unrelated sibling worktree in the same repo survived that TERM run. Read `run.sh`: the prefix match uses `"$wt_real"/*`, so `builder-12` cannot match `builder-123`.
  - Exit code unchanged: `on_exit` captures `$?` first and ends with `exit "$rc"`, and cases (b) and (c) return 1 and 3 in the selftest.
  - Dry-run ordering: `wt_tmp` is set after the `SDLC_DRY_RUN` exit, and `SDLC_TMP_WORKTREES` is passed alongside `SDLC_ROLE` (`run.sh` diff).
  - Header comment: documents the env var, the cleanup-on-failure rule and the signal exit codes. The selftest header lists the new cases.
- Builder claim that `--force --force` is used: accepted after reading the diff. It is a superset of the handoff's `--force` and does not conflict with it.

## Out of scope changes
None. `git status` shows only `run.sh` and `run-selftest.sh` modified, plus untracked `.sdlc/` artifacts for this task.

## For the next attempt
None
