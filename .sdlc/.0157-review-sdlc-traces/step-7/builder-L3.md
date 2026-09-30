<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/traces/sources/git.py` (new): `read(repo, integration=None, limit=2000)` returns `worktrees`, `branches`, `tracked_runtime`, `resets`, `commits` and `problems`. It gets them from read-only `git -C` subprocesses. The subprocess env drops inherited `GIT_DIR`-style selectors and sets `GIT_OPTIONAL_LOCKS=0`.
- `plugins/sdlc-lite/scripts/traces/selftest.py`: adds two `git:` cases (a throwaway-repo read, and a dir that is not a work tree) plus their fixture helpers.

## Checks
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k git`: exit 0, both cases `ok`, `traces selftest: PASS`.
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k git | grep -q '^ok: git: '`: exit 0.
- `test -f plugins/sdlc-lite/scripts/traces/sources/git.py`: exit 0.
- (guard) scope `test -z "$(...)"` against `$SDLC_BASE_SHA`: exit 0.
- `python3 plugins/sdlc-lite/scripts/traces.py selftest` (all families): exit 0.
- Negative controls, monkeypatched in a Python run:
  - With `git.nested` forced to False, the `git` family fails (exit 1) on the worktree map.
  - With `read` wrapped to write a file into the repo, the family fails (exit 1) with `read changed the repo ('', 9) -> ('?? new.txt\n', 9)`.
- `git worktree list | grep -c private/var` in this repo: 0, so no throwaway worktree registered here.

## Notes
- **Record shapes:**
  - `commits` and `resets` are `(sha, subject)` tuples.
  - `worktrees` entries are `{path, branch, nested}`, with `branch` None when detached.
  - `problems` is a list of strings.
- **Commit matching is strict:** `close <id>` must be the whole subject. `close T-0152 after the merge step`, which appears in this repo's history, is not matched. Ticket ids match `T-\d+`.
- **Fixture layout:**
  - The throwaway repo ignores `.worktrees/` and holds two detached worktrees: the nested `.worktrees/x/.worktrees/tmp/builder-1` and a non-nested `.worktrees/lane`.
  - The lane has its own `reset: moving to HEAD~2`, which shows that `integration=` switches which reflog the resets come from.
  - Before/after equality of `git status --porcelain` and the reflog line count is checked for both the repo and the lane.
  - Both worktrees are removed in `finally`.
- **Empty repo:** an empty repo (no commits) gives a `problems` entry for the failing `log` and `reflog` commands rather than raising.
