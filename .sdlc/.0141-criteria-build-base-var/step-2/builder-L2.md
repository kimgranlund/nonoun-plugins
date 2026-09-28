<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/steps.py`: new `rev_commit`, `base_sha` and `span_env` helpers. `run_guard` now takes a `base` argument and runs each span with `SDLC_BASE_SHA` set to it. The caller's value is always dropped, and the variable stays unset outside git. `run_guards` (used by `split --only`) passes HEAD at the toplevel. `swap` passes the first line of `<step dir>/base-sha` when that line names a commit, else HEAD. I updated the module docstring and the `--only` and `--timeout` help text, and added three selftest cases:
  - `split --only` passes a `$SDLC_BASE_SHA = HEAD` guard even when the caller's env sets a bogus value.
  - A `swap` new span sees the stored `base-sha` value after HEAD has moved past it.
  - `lint` passes `git diff --name-only "$SDLC_BASE_SHA"`.

## Checks
- Criterion 1 (a throwaway repo with a plan whose guard is `test "$SDLC_BASE_SHA" = "$(git rev-parse HEAD)"`, then `split --only 1` and `test -f step-1/handoff.md`): exit 0.
- `grep -q SDLC_BASE_SHA plugins/sdlc-lite/scripts/steps.py`: exit 0.
- (guard) `python3 plugins/sdlc-lite/scripts/steps.py selftest`: `steps selftest: PASS`.
- Negative control: I ran the selftest from a copy of steps.py under `.worktrees/tmp/` (removed afterwards) whose `run_guard` strips `SDLC_BASE_SHA` from the env. It FAILs exactly the new `split --only` and `swap` base-sha cases, so both tests catch a missing variable.

## Notes
The uncommitted changes to `run.sh` and `run-selftest.sh` in the tree were there before this step (step 1), and I did not touch them. Nothing was committed.
