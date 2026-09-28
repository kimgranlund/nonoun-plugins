<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- `test -x plugins/sdlc-lite/hooks/block-stray-worktree.sh`: pass. Evidence: rc=0.
- `git worktree add /tmp/x HEAD` with builder and prefix `/r/.worktrees/tmp/builder-1` exits 2: pass. Evidence: rc=2; stderr: "Blocked for sdlc role 'builder': the path /tmp/x is not under $SDLC_TMP_WORKTREES (/r/.worktrees/tmp/builder-1)...".
- `-b tmpbr "$SDLC_TMP_WORKTREES/x" HEAD` exits 2: pass. Evidence: rc=2; stderr: "-b creates a branch, which the run never deletes".
- `--detach "$SDLC_TMP_WORKTREES/x" HEAD` exits 0: pass. Evidence: rc=0, no output.
- `git worktree add /tmp/x HEAD` with `SDLC_ROLE` and `SDLC_TMP_WORKTREES` unset exits 0: pass. Evidence: rc=0. With only `SDLC_ROLE` unset, even `-b t /tmp/x HEAD` gave rc=0.
- `bash -c "git worktree add /tmp/x HEAD"` exits 2: pass. Evidence: rc=2 through the raw-scan branch ("cannot parse safely").
- Conductor with `SDLC_TMP_WORKTREES` unset and `--detach /r/x HEAD` exits 2: pass. Evidence: rc=2; stderr: "Blocked for sdlc role 'conductor': SDLC_TMP_WORKTREES is unset...".
- hooks.json lists the new hook under the Bash matcher: pass. Evidence: the `jq -e ... any(test("block-stray-worktree"))` command printed `true`, rc=0. The diff shows it as the 4th command in the Bash group.
- `grep -q block-stray-worktree hook-selftest.sh`: pass. Evidence: rc=0.
- `grep -q block-stray-worktree check.sh`: pass. Evidence: rc=0; the diff shows the header comment updated.
- `shellcheck --severity=warning` on the new hook: pass. Evidence: rc=0.
- (guard) `bash plugins/sdlc-lite/scripts/hook-selftest.sh`: pass. Evidence: `hook selftest: PASS`, rc=0. This is a new-behavior guard, and the base HEAD has no stray-worktree section to compare, so no pre-build run was needed.
- Negative control: pass. Evidence:
  - I made a throwaway worktree at `$SDLC_TMP_WORKTREES/base` and copied in the new hook and the selftest.
  - The unmodified copy printed `hook selftest: PASS`.
  - After inserting `exit 0` right after the `SDLC_ROLE` line (line 24), it printed `hook selftest: FAIL: block-stray-worktree denies /tmp/x: exit 0, want 2`, rc=1.
  - The biting variable is the hook's role gate and everything after it. The selftest's deny cases are the conjunct that catches an early exit.
  - I removed the worktree; `git worktree list | grep -c "/base"` gave 0.
- Extra edge checks (not criteria):
  - `--detach /r/.worktrees/tmp/builder-1/x HEAD` exits 0.
  - `--detach /tmp/x` (no commit-ish, wrong path) exits 2.
  - `.../builder-1x/x` is denied, so a prefix-sibling path is not accepted.

## Out of scope changes
None. `git status` shows the four in-scope plugin files: hooks.json, check.sh, hook-selftest.sh and the new hook. The other changes are `.sdlc/0107-role-throwaway-worktrees-created-outside/` artifacts: the handoff.md Goal, Constraints and Clarify text, plus planner and runs files. That folder is the ticket's own workspace, written before this build. `run.sh` and `fanout.py` are untouched, and step 2's records were not touched.

The `run()` helper in `hook-selftest.sh` now also unsets `SDLC_TMP_WORKTREES`. This matches the header note that the selftest never inherits the caller's env, and it is needed for the new section to be deterministic.

The steelman pass found nothing to file. The live hook blocked two of my own verification commands that put `bash` (a shell command word) and `git worktree add` in one command. That is the raw-scan behavior the handoff specifies, not a defect. Splitting the commands avoided it.

## For the next attempt
None
