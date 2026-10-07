## Task goal
The bug is fixed and a test that failed before the fix passes after it.

## Step 1: run.sh cleans up promptly on TERM and reaps dead-owner prefixes
level: L4
### Read first
- `plugins/sdlc-lite/AGENTS.md`
### Do
Root cause, from reading the code:
- run_lifecycle.py (lines 98-126) answers SIGINT/TERM/HUP with `killpg(SIGTERM)` and sends SIGKILL to the group 5 s later.
- run.sh runs the role in the foreground (`env ... "${cmd[@]}"`, run.sh line 377). Bash defers its `trap 'exit 143' TERM` until that child exits.
- If the role process (claude) takes more than 5 s to exit, run.sh is SIGKILLed before `on_exit`/`cleanup_worktrees` runs. `<lane>/.worktrees/tmp/builder-<pid>` is then left behind.
- Any other SIGKILL of run.sh has the same effect.

Changes:
1. Add `plugins/sdlc-lite/scripts/reap-tmp-worktrees.sh <toplevel> [<own prefix>]`, executable.
   - For each directory directly under `<toplevel>/.worktrees/tmp/` whose name matches `^[a-z]+-[0-9]+$`, skip it when the pid suffix names a live process (`ps -p <pid>`, so EPERM counts as alive) or when it is the given own prefix.
   - For a dead owner, run `git -C <toplevel> worktree remove --force --force` on each registered worktree under it, matching paths by physical path (same idea as run.sh's `phys`), then `rm -rf` the dir.
   - Finally run `git worktree prune`, then `rmdir` `.worktrees/tmp` and `.worktrees` only when empty.
   - It never fails (exit 0), never touches anything outside `.worktrees/tmp`, and never deletes a branch.
   - Header comment states this contract.
2. In `plugins/sdlc-lite/scripts/run.sh`:
   - Real runs only, never a dry run. Call the reaper for `$toplevel`, excluding `$wt_tmp`, before the stray snapshot. Call it again from `cleanup_worktrees` after this run's own prefix is removed.
   - Launch the role command in the background, record its pid as `role_pid`, and `wait "$role_pid"`. Keep the `</dev/null >"$log" 2>&1` redirections and the existing "exited non-zero; see $log" / exit 1 behavior on a non-zero wait status.
   - In `on_exit`, when `role_pid` is still alive: send it TERM, wait up to about 2 s, then KILL it. Only then run `cleanup_worktrees`, so a dying role cannot recreate files, and so the whole handler finishes well inside run_lifecycle's 5 s grace.
   - Keep exit codes 130/143/129 and the whole-body `{ ... }` self-edit guarantee.
   - Update the header "Throwaway worktrees" paragraph to describe the reaper and the TERM behavior.
3. In `plugins/sdlc-lite/scripts/run-selftest.sh`, add two cases that drive run.sh only (never call the reaper script directly), and describe them in the header comment:
   - `stale prefix`: before a real stub run, register a detached worktree under `.worktrees/tmp/builder-<dead pid>/w` (dead pid from a subshell that has exited) and one under `.worktrees/tmp/builder-$$/w` (live). After the run, the dead one is gone from disk and from `git worktree list`, and the live one is still present. Clean it up afterwards. Failures read `fail "stale prefix: <reason>"`.
   - `term cleanup`: a stub claude adds a worktree under `$SDLC_TMP_WORKTREES`, traps and ignores TERM, writes a ready marker, and sleeps about 30 s. Launch run.sh in the background, wait for the marker, send TERM to the run.sh pid (the run_lifecycle process), and wait for it to exit. Then assert that no worktree under `.worktrees/tmp` is registered, that `.worktrees/tmp` is gone, and that the stub process is no longer alive. Failures read `fail "term cleanup: <reason>"`.
4. In `docs/references/sdlc-internals.md`, in the run.sh paragraph where `SDLC_TMP_WORKTREES` cleanup is described, add the reaper (`reap-tmp-worktrees.sh`, dead-owner prefixes, start and exit) and the prompt TERM cleanup.
### Acceptance criteria
- (guard) `bash plugins/sdlc-lite/scripts/run-selftest.sh`
- `test -x plugins/sdlc-lite/scripts/reap-tmp-worktrees.sh`
- `grep -qF reap-tmp-worktrees.sh plugins/sdlc-lite/scripts/run.sh`
- `grep -qF 'fail "stale prefix:' plugins/sdlc-lite/scripts/run-selftest.sh`
- `grep -qF 'fail "term cleanup:' plugins/sdlc-lite/scripts/run-selftest.sh`
- The new selftest fails on the base run.sh: `d=$(mktemp -d) && git archive "$SDLC_BASE_SHA" plugins/sdlc-lite | tar -x -C "$d" && cp plugins/sdlc-lite/scripts/run-selftest.sh "$d/plugins/sdlc-lite/scripts/run-selftest.sh" && out=$(bash "$d/plugins/sdlc-lite/scripts/run-selftest.sh" 2>&1); printf "%s\n" "$out" | grep -qE "FAIL: (stale prefix|term cleanup):"`
- `grep -qF reap-tmp-worktrees.sh docs/references/sdlc-internals.md`
- `bash -n plugins/sdlc-lite/scripts/reap-tmp-worktrees.sh`
