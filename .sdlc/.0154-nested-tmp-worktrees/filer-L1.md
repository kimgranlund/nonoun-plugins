<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
None

## PR title
T-0154: Reap nested tmp worktrees left behind by role runs

## PR body
### Summary
Throwaway worktrees that a role run makes under `<toplevel>/.worktrees/tmp/<role>-<pid>` could outlive the run. This includes the ones nested inside fanout lane worktrees, such as `.worktrees/i1/.worktrees/tmp/builder-78490`.

The planner found this cause from reading the code:
- `run_lifecycle.py` answers TERM with a group SIGTERM, then SIGKILL 5 s later.
- `run.sh` ran the role in the foreground, so bash deferred its TERM trap until the role exited.
- A role that took more than 5 s to exit got `run.sh` killed before `cleanup_worktrees` ran.
- Any other SIGKILL of `run.sh` leaves the same residue.

The evidence for the 2026-09-28 overnight run is in another repo and was not reachable. The exact trigger of those leftovers is inferred, not confirmed. The dead-owner reaper covers both causes.

### Changes
- **New `plugins/sdlc-lite/scripts/reap-tmp-worktrees.sh <toplevel> [<own prefix>]`:**
  - Removes `.worktrees/tmp/<role>-<pid>` dirs whose owner pid is dead. It skips live owners, the own prefix and symlinks.
  - It never fails, never touches anything outside `.worktrees/tmp`, and never deletes a branch.
  - If `ps` is not on PATH it reaps nothing, so a live run's prefix is never taken for dead.
- **`run.sh`:**
  - The role now runs in the background and `run.sh` waits on it.
  - `on_exit` first stops the role (TERM, up to 2 s, then KILL) and then cleans up, so it finishes inside the 5 s grace.
  - The reaper runs before the stray snapshot and again in `cleanup_worktrees`, on real runs only.
  - Exit codes 130/143/129, the non-zero-exit message and the `{ ... }` group are unchanged.
- **`run-selftest.sh`:** two new cases that drive `run.sh` only.
  - `stale prefix` checks that a dead-owner prefix is removed and a live one kept.
  - `term cleanup` uses a stub role that ignores TERM. It checks that no worktree is registered, `.worktrees/tmp` is gone, and the stub is dead.
- **`fanout.py`:** runs the reaper on the lane worktree right after each driver returns, before `inherited_red` and before any `git add -A` or wip commit. A new selftest case, `lane tmp prefix reaped`, covers it.
- **`docs/maintenance/sdlc-internals.md`:** describes the reaper, the prompt TERM cleanup and the per-driver lane reap.

### Verification
- **Step 1 (verifier L3, pass):**
  - `run-selftest.sh` passes on the built tree.
  - The new selftest run against the base plugin fails with `FAIL: stale prefix: dead-owner prefix builder-81703 is still on disk`.
  - With the stale-prefix block removed, the base fails with `FAIL: term cleanup: a worktree under .worktrees/tmp is still registered`.
  - With the `stop_role` call deleted from the fixed `run.sh`, it fails with `FAIL: term cleanup: the stub claude ... is still alive`.
  - The verifier probed the reaper directly on a scratch repo. Live, non-matching and own-prefix dirs were kept, a dead owner was removed, a missing toplevel and no args exited 0, and no `ps` meant no reaping.
  - `-x`, `grep` and `bash -n` checks also passed.
- **Step 2 (verifier L1, pass):**
  - `fanout.py selftest` prints PASS.
  - With the reaper call disabled it fails, naming `lane tmp prefix reaped`. The builder captured that output and the verifier reproduced it.
- **Step 3 (verifier L1, pass):**
  - Every gate passed: `check.sh`, `check-packaging.py`, `codex_roles.py generate --check`, `lifecycle-selftest.py`, and `git diff --check`.
  - The builder changed nothing in this step because every gate was already green.
- shellcheck is not installed, so the shellcheck part of `check.sh` was skipped.

## Changelog entry
Fixed: role runs no longer leave throwaway worktrees behind under `.worktrees/tmp`, including ones nested in fanout lane worktrees. `run.sh` now stops its role and cleans up within the TERM grace period. A new `reap-tmp-worktrees.sh` removes prefixes whose owner died. It runs at the start and end of each run and after each fanout lane driver.

## Follow-ups
- note: The reaper keeps a stale prefix whose dead pid was reused by an unrelated live process until that process exits. This is conservative and never destructive.
- note: The root cause of the 2026-09-28 leftovers is inferred from the code. The lane logs in the other repo were not reachable, and a live claude's shutdown time under TERM is not shown by the selftests.
- note: `check.sh` skipped shellcheck because it is not installed on the build host, so the new shell scripts were not linted.
