## Task goal
The bug is fixed and a test that failed before the fix passes after it.

## Step 2: fanout reaps each lane's dead-owner tmp prefixes after its driver
level: L2
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Step 1 lets the next run.sh in a lane reap a SIGKILLed run's prefix. But the last role run in a lane has no successor, so the lane can still end with a nested `.worktrees/tmp/<role>-<pid>`.

Changes:
1. In `plugins/sdlc-lite/scripts/fanout.py`, right after the driver `subprocess.run(...)` returns in the per-ticket function (around line 537), before `inherited_red` and before any `git add -A` or wip commit, run `bash <SCRIPTS>/reap-tmp-worktrees.sh <lane worktree>`. Ignore its exit code; it only removes prefixes whose owner pid is dead. Update the module docstring step 2 to say so.
2. Add a selftest case to fanout.py's `selftest`. The existing STUB, or a variant used by a new small lane, registers a detached worktree under `$PWD/.worktrees/tmp/builder-<dead pid>/w` from inside the stub script, which the hook cannot see. After the fanout run, `expect('lane tmp prefix reaped', ...)` checks that the lane worktree has no `.worktrees/tmp/builder-<dead pid>` and that `git worktree list` no longer lists it.
   - The builder must show the case red once by temporarily removing the reaper call, running the selftest, then restoring the call. The builder quotes the red output in its report.
3. In `docs/maintenance/sdlc-internals.md`, add one clause about the per-driver lane reap to the fanout paragraph.
### Acceptance criteria
- (guard) `python3 plugins/sdlc-lite/scripts/fanout.py selftest`
- `grep -qF reap-tmp-worktrees.sh plugins/sdlc-lite/scripts/fanout.py`
- `grep -qF "lane tmp prefix reaped" plugins/sdlc-lite/scripts/fanout.py`
- The builder report quotes a `fanout selftest: FAIL` output naming `lane tmp prefix reaped`, observed with the reaper call removed.
