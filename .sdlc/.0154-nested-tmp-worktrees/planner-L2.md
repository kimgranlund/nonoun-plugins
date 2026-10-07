<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
Throwaway worktrees that a role run makes under `<toplevel>/.worktrees/tmp/<role>-<pid>` (including the ones nested inside fanout lane worktrees) must not outlive the run. run.sh has to clean up within run_lifecycle's 5 s TERM grace. A prefix whose owning run was SIGKILLed has to be reaped by the next run.sh and by fanout after each lane driver returns. A failing selftest lands with each fix.

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
3. In `docs/references/sdlc-internals.md`, add one clause about the per-driver lane reap to the fanout paragraph.
### Acceptance criteria
- (guard) `python3 plugins/sdlc-lite/scripts/fanout.py selftest`
- `grep -qF reap-tmp-worktrees.sh plugins/sdlc-lite/scripts/fanout.py`
- `grep -qF "lane tmp prefix reaped" plugins/sdlc-lite/scripts/fanout.py`
- The builder report quotes a `fanout selftest: FAIL` output naming `lane tmp prefix reaped`, observed with the reaper call removed.

## Step 3: gates green
level: L2
### Do
Run every gate below and fix any red that Steps 1 and 2 introduced. A gate that is already red at `$SDLC_BASE_SHA` is reported as Status `inherited red`.
### Acceptance criteria
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`
- (guard) `python3 scripts/check-packaging.py`
- (guard) `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`
- (guard) `python3 plugins/sdlc-lite/scripts/lifecycle-selftest.py`
- (guard) `git diff --check "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"`

## Risks
- The handoff has no repro, and the evidence lives in another repo I could not reach. The TERM-grace mechanism is inferred from the code (run_lifecycle.py's 5 s SIGKILL, and bash deferring its trap while a foreground child runs). A plain SIGKILL from elsewhere would leave the same residue. The dead-owner reaper covers both causes, but the exact trigger of the 2026-09-28 leftovers is unconfirmed.
- Pid reuse: a dead run's pid reused by an unrelated live process keeps that stale prefix until the pid dies. This is conservative, never destructive.
- Backgrounding the role command changes signal delivery. Non-interactive bash makes background children ignore SIGINT, so the INT path must forward TERM explicitly, as Step 1 says. The `term cleanup` and existing selftest cases guard this, but a live claude's shutdown time is not proven by these tests.
- The `term cleanup` case depends on timing (5 s grace). The builder should use generous waits so it is not flaky on a loaded host.
