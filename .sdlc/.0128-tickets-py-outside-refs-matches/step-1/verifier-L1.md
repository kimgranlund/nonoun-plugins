<!-- role=verifier level=L1 model=sonnet effort=medium -->
No leftover git state changes from my verification. All files changed are within scope (tickets.py, CLAUDE.md, plus artifact/planner files which are the task's own bookkeeping, not code).

## Verdict
pass

## Criteria
- `outside_refs`/`rewrite_files` prefix-sibling case (`0001-a`/`0001-ab`) exits 0: pass. Evidence: ran the exact criterion command on the built tree, printed `['both.md']`, exit 0. Confirmed the check bites by rerunning it in a throwaway worktree at pre-build HEAD (`git worktree add --detach "$SDLC_TMP_WORKTREES/base" HEAD`), which printed `['both.md', 'only.md']` and exited 1, matching the criterion's stated red-at-HEAD behavior exactly.
- (guard) end-of-line/punctuation/`/` boundary case exits 0: pass. Evidence: ran the exact command, printed `['e.md', 'p.md', 'q.md', 's.md']`, exit 0.
- `grep -qF "0001-ab" plugins/sdlc-lite/scripts/tickets.py` passes: pass. Evidence: `grep -qF "0001-ab" plugins/sdlc-lite/scripts/tickets.py && echo "grep pass"` printed `grep pass`.
- (guard) `python3 -B plugins/sdlc-lite/scripts/tickets.py selftest` exits 0: pass. Evidence: ran it, output `tickets selftest: PASS`, exit 0.
- (guard) `plugins/sdlc-lite/scripts/check.sh` exits 0: pass. Evidence: ran it in full, exit 0, tail of output shows shellcheck ok, plugin validate ok, all selftests PASS (steps, order, fanout, run, hook, hook live probe).
- Diff shows updated literal-rule wording in docstrings and CLAUDE.md: pass. Evidence: `git diff HEAD -- CLAUDE.md plugins/sdlc-lite/scripts/tickets.py` shows the module docstring, `outside_refs`, `rewrite_files`, and close docstrings, plus the `CLAUDE.md` `scripts/tickets.py` bullet, all updated to state the literal ends at `/`, end of token, or punctuation, never running into a longer folder name.

## Out of scope changes
`.sdlc/0128-tickets-py-outside-refs-matches/handoff.md` shows as modified (Goal/Constraints filled from template placeholders) but this predates step 1: it is the planner's own handoff authoring, not a step-1 edit, and the builder correctly noted it as pre-existing. `.sdlc/0128-tickets-py-outside-refs-matches/planner-L2.md` and `runs.jsonl` are untracked artifacts from the planning/build pipeline itself, not code changes. `.claude/agents/sdlc-lite-author.md` was left unchanged per the Do's own conditional ("update only if it describes the scan") — checked its content, it does not mention the literal-matching rule, so leaving it is correct, not an omission.

## For the next attempt
None.
