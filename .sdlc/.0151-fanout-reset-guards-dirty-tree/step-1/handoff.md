## Task goal
The bug is fixed and a test that failed before the fix passes after it.

## Step 1: Refuse a dirty integration tree before the merge, with a selftest
level: L2
### Do
In `plugins/sdlc-lite/scripts/fanout.py`, `run_ticket`, inside `with lock:` and before `before = git_out(integ, 'rev-parse', 'HEAD')` / the `git merge --no-ff`:
- Add a check for uncommitted tracked changes in the integration worktree: `git status --porcelain --untracked-files=no` is non-empty. Do not use the `porcelain()` helper here, because untracked files survive `reset --hard` and the close step also uses that helper.
- When dirty, do not merge, reset, or run gates. Return the outcome `integration dirty: <first path>` with commit `lane_sha[:7]`. The lane commit already exists, so the ticket stops and `run_lane` WIP-handles it as for any other non-merged outcome.
- The point of the guard is that both `git reset --hard <pre-merge HEAD>` calls (the merge-failure path and the red-gate path) run only on a tree that held no human edits when the merge began.

Update the docstring near line 67 and the `sdlc-internals.md` fanout paragraph to state that a dirty integration tree is refused with `integration dirty`. Add one sentence to `skills/fanout/SKILL.md` line 14.

Add a selftest case in `cmd_selftest`, written before the fix. It uses a fixture repo with a tracked file, and a stub driver that appends a line to that file in `<lanes-dir>/integration`, the integration worktree, which is `../integration` relative to the lane worktree. The case runs a gate that goes red on a dirty-tree ticket, and it must show:
- the report row is `integration dirty`
- the edit survives in the integration worktree (`git diff` there still shows it)
- the integration branch has no merge commit for the ticket

Observe the case fail with the guard removed (a negative control), then pass with it. The runtime failure is proven by the selftest itself.
### Acceptance criteria
- `grep -qF 'integration dirty' plugins/sdlc-lite/scripts/fanout.py`
- `grep -qF 'integration dirty' docs/maintenance/sdlc-internals.md`
- `grep -qF 'integration dirty' plugins/sdlc-lite/skills/fanout/SKILL.md`
- `python3 plugins/sdlc-lite/scripts/fanout.py selftest` exits 0 and its source carries the new dirty-integration case (the `integration dirty` string appears in a selftest `expect` line).
- (guard) `python3 plugins/sdlc-lite/scripts/check.py` shows no new findings versus base: run the same command in a `git worktree add --detach <tmp> HEAD` copy and compare.
- (guard) `bash -c 'test -z "$(git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc" | grep -vE "^(plugins/sdlc-lite/scripts/fanout.py|plugins/sdlc-lite/skills/fanout/SKILL.md|docs/maintenance/sdlc-internals.md)$")"'`
