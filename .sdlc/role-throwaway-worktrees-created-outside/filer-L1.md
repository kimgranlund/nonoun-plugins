<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
None

## PR title
T-0107: Block stray `git worktree add` in role runs with a PreToolUse hook

## PR body
### Summary
A role's throwaway worktree created outside `$SDLC_TMP_WORKTREES`, or with a new branch (`-b`, `-B`, `--orphan`), was never cleaned up. The `-b` form also left its branch behind. This adds `hooks/block-stray-worktree.sh`, a PreToolUse(Bash) hook that blocks these calls before they run. It only acts when `SDLC_ROLE` is set, so interactive sessions are unaffected. `fanout.py`'s own worktrees are not Bash tool calls, so they are untouched. The T-0095 EXIT cleanup in `run.sh` stays as it was. Follow-up from T-0095.

### Changes
- New `plugins/sdlc-lite/hooks/block-stray-worktree.sh`. Inside a role run it denies (exit 2) any `git [global opts] worktree add` when:
  - `-b`, `-B`, or `--orphan` is present.
  - `SDLC_TMP_WORKTREES` is unset or empty.
  - The path is not strictly under the prefix, has a `..` segment, or cannot be resolved (`$`, a glob, or a leading `~`).
  - The path is relative and follows a `cd` or `pushd`.
  - There is neither `--detach`/`-d` nor a commit-ish.
- The deny message names the role and gives the allowed form: `git worktree add --detach "$SDLC_TMP_WORKTREES/<name>" <commit>`.
- The hook fails closed. On a heredoc, a shell or evaluator command word, an unterminated quote, or a python3 or parser failure, it scans the raw text and denies any `git ... worktree add`.
- `hooks/hooks.json`: the hook is the fourth command in the Bash matcher group.
- `scripts/hook-selftest.sh`: a new `block-stray-worktree` section with deny and allow fixtures, including checks that stderr names the role and the `--detach` form. `run()` now also unsets `SDLC_TMP_WORKTREES`, so the caller's value never leaks into a test.
- `scripts/check.sh`: the header comment names the new hook.
- Records updated in the same change:
  - `CLAUDE.md`: a Layout bullet and the hook-selftest list.
  - `.claude/agents/sdlc-lite-author.md`: the hook-selftest list and a learned-hazard bullet.
  - `agents/builder.md` rule 5 and `agents/verifier.md` rule 3: one sentence each about the denial.

### Verification
Both steps passed independent verification.
- Step 1 (hook, wiring, selftest), verifier L2 pass:
  - Denied: `/tmp/x` with and without `-b`, a `bash -c` wrapper, and a conductor with the prefix unset.
  - Allowed: `--detach "$SDLC_TMP_WORKTREES/x"`, and everything when `SDLC_ROLE` is unset.
  - `hooks.json` lists the hook, and `shellcheck --severity=warning` is clean.
  - `hook-selftest.sh` prints `hook selftest: PASS`.
  - Negative control: with `exit 0` inserted after the `SDLC_ROLE` line, the selftest printed `hook selftest: FAIL: block-stray-worktree denies /tmp/x: exit 0, want 2`, so the fixtures bite.
  - The verifier also confirmed a sibling path such as `builder-1x/x` is denied.
- Step 2 (records), verifier L1 pass:
  - The greps for the new hook and `--orphan` pass, and each was absent at HEAD.
  - No added em dashes.
  - The verifier captured the exit code of `scripts/check.sh` as 0, with every selftest, shellcheck, and plugin validate passing.

## Changelog entry
- Role runs can no longer leak throwaway worktrees or branches through the Bash tool: a new `block-stray-worktree` hook denies `git worktree add` with `-b`, `-B`, or `--orphan`, or with a path outside `$SDLC_TMP_WORKTREES`. Interactive sessions and `fanout.py` are unaffected.

## Follow-ups
- Worktrees created from inside a script or program a role runs (python, make) bypass the new block-stray-worktree hook, which only sees Bash tool text; add run-end detection or reporting for stray worktrees and branches.
- `git worktree add <path> <name>` where `<name>` exists only as a remote branch can make git create a local tracking branch, but block-stray-worktree treats `<name>` as a commit-ish and allows it; close this gap, or require `--detach`.
