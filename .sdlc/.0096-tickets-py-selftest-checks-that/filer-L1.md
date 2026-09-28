<!-- role=filer level=L1 model=sonnet effort=medium -->
## Warnings
None

## PR title
T-0096: tickets.py selftest: prove close --dry-run digest ignores other-worktree open lines when follow-ups exist

## PR body
### Summary
The `close --dry-run` `expect <digest>` line is meant to cover only the ordered follow-ups. `tickets.py selftest` tested this only when there were no follow-ups (the fixed empty digest `e3b0c44298fc`). This PR adds a case with two follow-ups and an open ticket that exists only in another worktree, so the guarantee is tested with real follow-ups. It is a follow-up from T-0079.

### Changes
- `plugins/sdlc-lite/scripts/tickets.py`: one new selftest case, `worktree dry-run with follow-ups:`, added right after the existing `worktree dry-run:` case. It writes a filer file for `delta` with two follow-up bullets, runs `close delta --dry-run`, and asserts:
  - rc is 0.
  - The output lists `open T-0004 Gamma [gamma] (worktree wtdr)`.
  - The last line is `expect ` plus the digest of only the two follow-ups.
  - Neither the main tree nor the other worktree changed.
- The diff is 10 added lines and none removed, all inside `selftest()`. `cmd_close` and its output are untouched.

### Verification
The verifier passed every criterion (verifier L1, step 1):
- `grep -c "worktree dry-run with follow-ups"` prints 1. The case is new.
- `tickets.py selftest` exits 0 and prints `tickets selftest: PASS`.
- Mutant check: in a copy of the whole `plugins/sdlc-lite` dir, the dry-run return was changed to `[f'expect {follow_digest(items + opens + other_opens)}']`. `selftest` on the copy exits 1 and lists the new case among the misses. It also breaks the existing `worktree dry-run:` case and others.
- `git diff HEAD --stat` lists only `tickets.py`, and `-U0` shows a single hunk with no removed lines.
- `tickets.py check` exits 0 (`ok: 126 tickets, roadmap current`).
- `check.sh` exits 0 on the current tree and in a detached HEAD worktree, so there are no new failures.

Note: `.sdlc/0096-tickets-py-selftest-checks-that/handoff.md` shows as modified. The verifier flagged it as planner-side ticket text and judged it harmless.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- Test: `tickets.py selftest` now checks that the `close --dry-run` `expect <digest>` line covers only the ordered follow-ups, and ignores other-worktree `open ... (worktree <name>)` lines, when follow-ups are present (T-0096). A mutant that folds open lines into the digest now fails the selftest.

## Follow-ups
None
