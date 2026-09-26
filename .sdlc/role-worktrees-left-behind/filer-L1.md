<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
None

## PR title
T-0095: Clean up role throwaway worktrees on every exit

## PR body
### Summary
Role runs (verifiers and builders) created throwaway git worktrees in `/tmp` to prove a check can go red, and never removed them. One machine had 12 detached worktrees left behind. `run.sh` now gives each role run its own worktree prefix and removes everything under it when the run exits, on success or failure.

### Changes
- `plugins/sdlc-lite/scripts/run.sh`:
  - On a real run (a dry run creates nothing), it sets `SDLC_TMP_WORKTREES=<toplevel>/.worktrees/tmp/<role>-<pid>` and passes it to the role next to `SDLC_ROLE`.
  - A new `on_exit` EXIT trap removes each worktree registered under that prefix (matched by physical path, so the macOS `/var` vs `/private/var` difference is handled). It then runs `rm -rf` on the prefix and `git worktree prune`, and removes `.worktrees/tmp` and `.worktrees` when empty.
  - The trap never changes the exit code. INT, TERM and HUP also trigger cleanup (exit 130, 143, 129).
  - Cleanup is scoped to this run's prefix only, so concurrent fanout lanes are not touched.
- `plugins/sdlc-lite/scripts/run-selftest.sh`: adds a stub `claude` that creates a worktree under `SDLC_TMP_WORKTREES`, with three cases: success (exit 0), failure (exit 1), and missing required section (exit 3). Each asserts that only the main worktree remains, `.worktrees/tmp` is gone, and the stub saw a non-empty prefix. A dry run is asserted to create no `.worktrees`.
- `plugins/sdlc-lite/agents/verifier.md`: rule 3 now creates the throwaway worktree only under `$SDLC_TMP_WORKTREES`. The verifier still removes its own worktree, and run.sh removes anything left.
- `plugins/sdlc-lite/agents/builder.md`: new rule 5 says throwaway worktrees go only under `$SDLC_TMP_WORKTREES`, never `/tmp` or a sibling dir.
- `CLAUDE.md` and `.claude/agents/sdlc-lite-author.md`: records updated to describe the new export and cleanup.
- The `merge-step` template and `skills/checks-that-bite` are unchanged.

### How each was verified
- Step 1 (run.sh and selftest), verifier L2: pass.
  - The handoff's failing-run and successful-run commands leave no worktree and no `.worktrees/tmp`.
  - `run-selftest.sh` prints PASS. Shellcheck at warning severity is clean. The dry-run guard passes.
  - The new selftest bites. Run against HEAD's `run.sh`, it printed `run selftest: FAIL: worktree ok run: leftover worktree ...` and exited 1.
  - Extra probes: TERM mid-run exits 143 and leaves no `.worktrees`. A sibling worktree outside the prefix survives. The prefix match cannot confuse `builder-12` with `builder-123`.
- Step 2 (prompts and docs), verifier L1: pass.
  - The greps for `SDLC_TMP_WORKTREES` in `verifier.md`, `builder.md`, `CLAUDE.md` and the author agent all pass. Each had 0 matches at HEAD.
  - The old `git worktree add <tmp dir> HEAD` phrase is gone from `verifier.md`.
  - `scripts/check.sh` exits 0: all selftests, shellcheck and plugin validate pass.

### Known limits
- A `kill -9` of run.sh skips every trap, so the prefix stays.
- A worktree a role creates outside the prefix is not cleaned, and a worktree created with `-b` leaves its branch behind.
- In a target repo where `.worktrees/` is not git-ignored, a live temp worktree shows as untracked during the run.

## Changelog entry
Fixed: role runs no longer leave throwaway git worktrees behind. `run.sh` exports `SDLC_TMP_WORKTREES=<toplevel>/.worktrees/tmp/<role>-<pid>` and removes every worktree under it on any exit, including failure and INT/TERM/HUP, then runs `git worktree prune`. The verifier and builder prompts now create throwaway worktrees only under that prefix.

## Follow-ups
- Role throwaway worktrees created outside `$SDLC_TMP_WORKTREES` (for example in `/tmp`) or with `-b` are never cleaned, and `-b` leaves its branch behind; add a guard or a check that detects them.
- A dry run of a role whose agent declares skills (planner, architect, verifier) leaves its `mktemp` skill file behind in `run.sh`; remove it on dry-run exit.
