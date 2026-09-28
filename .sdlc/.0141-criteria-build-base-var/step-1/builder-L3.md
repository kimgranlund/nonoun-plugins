<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/run.sh`: only builder and verifier runs, and only real ones (after the `SDLC_DRY_RUN` exit), now work out the build base and store it in `<step dir>/base-sha`. The rules:
  - Keep the stored sha when it is a commit and an ancestor of HEAD.
  - When there is a resync merge after it, use the newest first-parent merge instead.
  - When the stored value is missing, junk, or not an ancestor, use HEAD.
  - Rewrite the file only when the base is new or changed.
  - Pass the base to the role as `SDLC_BASE_SHA`, set next to `SDLC_ROLE` through `env`. Every other role has `SDLC_BASE_SHA` unset, even when the caller exported it, and writes no file.
  - The header comment explains all of this, plus the caveat: on a merge step the builder's own merge commit moves the base on the verifier run, so merge-step criteria use `HEAD^1`.
- `plugins/sdlc-lite/scripts/run-selftest.sh`: the header comment is extended, and a new section uses a stub `claude` that records `${SDLC_BASE_SHA:-unset}`. It covers the six cases in the handoff:
  - a builder dry run writes no `base-sha`;
  - a planner run sees `unset` and writes no file, even with the caller exporting `SDLC_BASE_SHA=leak`;
  - the first builder run gets HEAD and writes it;
  - after a plain commit, a verifier run still gets the old base;
  - after a `--no-ff` resync merge, the next run gets the merge commit and the file is rewritten to it;
  - a `base-sha` holding junk, or a commit that is not an ancestor, is replaced by HEAD.

## Checks
All commands were run from the git toplevel unless noted.
- Criterion 1 (first builder run: stub and `base-sha` both equal HEAD): rc=0
- Criterion 2 (plain commit keeps the base; resync merge moves the base and rewrites the file): rc=0
- Criterion 3, guard (planner sees `unset`, no `base-sha`): rc=0
- Criterion 4, `grep -q SDLC_BASE_SHA plugins/sdlc-lite/scripts/run-selftest.sh`: rc=0
- Criterion 5, guard, `bash plugins/sdlc-lite/scripts/run-selftest.sh`: `run selftest: PASS`, rc=0
- Criterion 6, guard, `shellcheck --severity=warning plugins/sdlc-lite/scripts/run.sh plugins/sdlc-lite/scripts/run-selftest.sh`: rc=0
- Negative control: I ran the new run-selftest.sh against the base `run.sh` in a throwaway worktree at HEAD. It fails with `base planner: SDLC_BASE_SHA is 'leak', want unset`. Criterion 1 against the base `run.sh` gives rc=1. The worktree was removed afterwards.
- `scripts/check.sh` (from `plugins/sdlc-lite`), not a criterion:
  - Runs with output to a pipe or a file: rc=0.
  - Three runs with stdout to /dev/null: rc=1, and the trace showed `hook-selftest.sh` setting `fail=1`.
  - Later runs: `check.sh >/dev/null 2>&1` gave rc=0, `hook-selftest.sh` alone gave rc=0 in 6 runs, and the base tree's check.sh gave rc=0.

## Notes
- The `check.sh` failure was intermittent, in `hook-selftest.sh`, which neither reads nor calls `run.sh` or `run-selftest.sh`. Load average was 36 to 46 at the time. I read it as contention, not something this step caused, but I did not find the root cause.
- The claude call now starts through `env` (`env ${base_env[@]+...} SDLC_ROLE=... "${cmd[@]}"`), so for builder and verifier `SDLC_BASE_SHA` sits right next to `SDLC_ROLE`. Every role gets a shell `unset SDLC_BASE_SHA` first.
- A stored abbreviated sha counts as changed and is rewritten as the full sha.
