## Task goal
Inside a role run, `hooks/block-stray-worktree.sh` denies every `git worktree add` form that can create a local branch, including the DWIM forms where git creates one implicitly (a `<name>` that exists only as a remote-tracking branch, and, per git docs, an omitted commit-ish, which auto-creates a branch named after the path basename), while the explicit detached form under `$SDLC_TMP_WORKTREES` still passes.

## Step 3: Gates green
level: L1
### Do
Run the repo check script `plugins/sdlc-lite/scripts/check.sh`. It covers:
- the merge-step copies being identical and lint-clean
- the conflict-marker probe
- the hook selftest
- shellcheck
- plugin validate

Fix any red that steps 1 and 2 introduced. The expected validate warning about CLAUDE.md is fine. Never commit.
### Acceptance criteria
- (guard) `plugins/sdlc-lite/scripts/check.sh`
