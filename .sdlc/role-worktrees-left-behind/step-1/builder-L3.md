<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/run.sh`: on a real run (dry run creates nothing), it now sets `wt_tmp=<toplevel>/.worktrees/tmp/<role>-$$` and passes it to the role as `SDLC_TMP_WORKTREES` next to `SDLC_ROLE`. A new `on_exit` EXIT trap does the old `.running` and skill-file removal, then `cleanup_worktrees`:
  - removes each worktree registered under the prefix with `git worktree remove --force --force`, matching paths by physical path through a `phys` helper that also resolves missing paths
  - then runs `rm -rf` on the prefix and `git worktree prune`
  - then runs `rmdir` on `.worktrees/tmp` and `.worktrees`
  - runs under `set +e` and ends with `exit "$rc"`, so it never changes the exit code

  INT, TERM and HUP now trap to exit 130, 143 and 129, and the EXIT trap still runs. The header comment documents the env var, the prefix-only scope and cleanup on failure.
- `plugins/sdlc-lite/scripts/run-selftest.sh`: adds a second stub `claude` that records `SDLC_TMP_WORKTREES`, adds a worktree under it, then succeeds, fails or returns a result with no required section (`STUB_MODE` is `ok`, `fail` or `nosect`). It runs cases (a) exit 0, (b) exit 1 and (c) exit 3. Each case asserts:
  - `git worktree list` shows only the main tree
  - `.worktrees/tmp` does not exist
  - the stub saw a non-empty `SDLC_TMP_WORKTREES` under `<toplevel>/.worktrees/tmp/`

  A dry run is also asserted to create no `.worktrees`. The header comment lists the new cases.

## Checks
- Criterion 1 (a failing run leaves no worktree): exit 0 (run.sh printed "builder exited non-zero" as expected).
- Criterion 2 (a successful run leaves no worktree): exit 0.
- `grep -q SDLC_TMP_WORKTREES plugins/sdlc-lite/scripts/run.sh`: exit 0.
- `grep -q SDLC_TMP_WORKTREES plugins/sdlc-lite/scripts/run-selftest.sh`: exit 0.
- (guard) `bash plugins/sdlc-lite/scripts/run-selftest.sh`: `run selftest: PASS`, exit 0.
- (guard) The dry-run criterion (`SDLC_DRY_RUN=1` creates no `.worktrees`): exit 0.
- (guard) `shellcheck --severity=warning plugins/sdlc-lite/scripts/run.sh plugins/sdlc-lite/scripts/run-selftest.sh`: exit 0, no output.
- Bite test: I copied the new `run-selftest.sh` into a throwaway worktree of HEAD (under a mktemp dir) and ran it there. It printed `run selftest: FAIL: worktree ok run: leftover worktree: .../wrepo/.worktrees/tmp/unset/w ...` with exit 1. I removed the throwaway worktree afterwards.
- Extra probe, not a criterion: a stub adds a worktree and sleeps, and run.sh gets TERM mid-run. It exits 143 with only the main tree left and no `.worktrees`.
- Extra regression check: `bash plugins/sdlc-lite/scripts/check.sh` exits 0 (all selftests PASS, shellcheck ok, plugin validate ok).

## Notes
- The live run.sh process that launched this builder (PID 81396) was executing this worktree's `plugins/sdlc-lite/scripts/run.sh`. Bash reads a script as it runs, so editing it in place could have broken that run. I edited a temp copy, checked it with `bash -n`, and swapped it in with `mv`, so the running process kept the old file. If another run.sh edit happens while a run from this tree is live, it should use the same copy-and-rename approach.
- Cleanup uses `git worktree remove --force --force`, a superset of the `--force` the handoff names, so a locked worktree under the prefix is removed too.
- Existing leak, left alone because it is out of scope: a dry run of a role whose agent declares skills (planner, architect, verifier) leaves its `mktemp` skill file behind. This predates the step and is unrelated to worktrees.
