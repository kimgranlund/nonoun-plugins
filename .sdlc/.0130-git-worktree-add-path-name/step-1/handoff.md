## Task goal
Inside a role run, `hooks/block-stray-worktree.sh` denies every `git worktree add` form that can create a local branch, including the DWIM forms where git creates one implicitly (a `<name>` that exists only as a remote-tracking branch, and, per git docs, an omitted commit-ish, which auto-creates a branch named after the path basename), while the explicit detached form under `$SDLC_TMP_WORKTREES` still passes.

## Step 1: Require --detach on every worktree add in the hook
level: L2
### Do
Pick a purely textual rule: every `git worktree add` inside a role run must carry `--detach` or `-d`. The reason: with `--detach`, git's `worktree add` skips all branch DWIM (no remote-tracking guess, no basename branch, no checkout of an existing branch). That property holds no matter which refs exist, so the hook never has to query the repo, which it cannot do reliably before git runs. The rule "allow only a commit-ish git cannot DWIM" was rejected because whether `<name>` is a remote-only branch depends on repo state.

In `plugins/sdlc-lite/hooks/block-stray-worktree.sh`, inside the Python `check_add`:
- Replace the final check `if not detach and len(pos) < 2` with `if not detach`.
- Give it a reason that says git can create or check out a branch without `--detach`, for example: "without --detach git can create a branch (a name that exists only on a remote becomes a new tracking branch, no commit makes one named after the path) or check out an existing branch".
- Keep the existing option parsing. `--no-detach` must not count as detach, and today it already does not. `-d` inside a combined short flag such as `-fd` still counts.
- Keep the prefix check, the `-b`/`-B`/`--orphan` checks, the unset-prefix check, the fail-closed raw scan, and the `SDLC_ROLE` unset exit unchanged.
- Update the header comment so it describes the new rule and the reason.

In `plugins/sdlc-lite/scripts/hook-selftest.sh`, in the block-stray-worktree section:
- Add to the denied loop: `git worktree add "$tw/x" feature-x` (remote-only-name DWIM), `git worktree add "$tw/x" HEAD`, `git worktree add --no-detach "$tw/x" HEAD`, `git worktree add "$tw/x" -- feature-x`, and `git worktree add "${SDLC_TMP_WORKTREES}/base" HEAD`.
- Move that last fixture from the allowed loop to the denied loop.
- Add to the allowed loop: `git worktree add -d "$tw/x" HEAD`, `git worktree add --detach "$tw/x" origin/feature-x`, and `git worktree add --detach "${SDLC_TMP_WORKTREES}/base" HEAD`.
- Keep the no-role fixture.

Do not touch other files in this step.
### Acceptance criteria
- `printf '%s' '{"tool_input":{"command":"git worktree add \"$SDLC_TMP_WORKTREES/x\" feature-x"},"cwd":"/r"}' | SDLC_ROLE=builder SDLC_TMP_WORKTREES=/r/.worktrees/tmp/builder-1 plugins/sdlc-lite/hooks/block-stray-worktree.sh 2>/dev/null; test $? -eq 2`
- `printf '%s' '{"tool_input":{"command":"git worktree add --no-detach \"$SDLC_TMP_WORKTREES/x\" HEAD"},"cwd":"/r"}' | SDLC_ROLE=builder SDLC_TMP_WORKTREES=/r/.worktrees/tmp/builder-1 plugins/sdlc-lite/hooks/block-stray-worktree.sh 2>/dev/null; test $? -eq 2`
- `printf '%s' '{"tool_input":{"command":"git worktree add \"$SDLC_TMP_WORKTREES/x\" -- feature-x"},"cwd":"/r"}' | SDLC_ROLE=builder SDLC_TMP_WORKTREES=/r/.worktrees/tmp/builder-1 plugins/sdlc-lite/hooks/block-stray-worktree.sh 2>/dev/null; test $? -eq 2`
- `printf '%s' '{"tool_input":{"command":"git worktree add \"$SDLC_TMP_WORKTREES/x\" feature-x"},"cwd":"/r"}' | SDLC_ROLE=builder SDLC_TMP_WORKTREES=/r/.worktrees/tmp/builder-1 plugins/sdlc-lite/hooks/block-stray-worktree.sh 2>&1 >/dev/null | grep -q -- '--detach'`
- `grep -q 'feature-x' plugins/sdlc-lite/scripts/hook-selftest.sh`
- `grep -qF -- '--no-detach' plugins/sdlc-lite/scripts/hook-selftest.sh`
- (guard) `printf '%s' '{"tool_input":{"command":"git worktree add --detach \"$SDLC_TMP_WORKTREES/x\" origin/feature-x"},"cwd":"/r"}' | SDLC_ROLE=builder SDLC_TMP_WORKTREES=/r/.worktrees/tmp/builder-1 plugins/sdlc-lite/hooks/block-stray-worktree.sh`
- (guard) `printf '%s' '{"tool_input":{"command":"git worktree add -d \"$SDLC_TMP_WORKTREES/x\" HEAD"},"cwd":"/r"}' | SDLC_ROLE=builder SDLC_TMP_WORKTREES=/r/.worktrees/tmp/builder-1 plugins/sdlc-lite/hooks/block-stray-worktree.sh`
- (guard) `printf '%s' '{"tool_input":{"command":"git worktree add \"$SDLC_TMP_WORKTREES/x\" feature-x"},"cwd":"/r"}' | SDLC_TMP_WORKTREES=/r/.worktrees/tmp/builder-1 plugins/sdlc-lite/hooks/block-stray-worktree.sh`
- (guard) `plugins/sdlc-lite/scripts/hook-selftest.sh`
