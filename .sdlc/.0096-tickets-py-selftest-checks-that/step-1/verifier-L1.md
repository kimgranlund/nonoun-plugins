<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- grep for "worktree dry-run with follow-ups" prints at least 1: pass. Evidence: `grep -c "worktree dry-run with follow-ups" plugins/sdlc-lite/scripts/tickets.py` printed 1. The diff shows the case is new, so it would have been 0 before.
- `tickets.py selftest` exits 0 and prints `tickets selftest: PASS`: pass. Evidence: I ran it and it printed `tickets selftest: PASS` with rc=0.
- Mutant check: pass. Evidence: I copied `plugins/sdlc-lite` to a temp dir and changed line 835 to `[f'expect {follow_digest(items + opens + other_opens)}']`. `selftest` on the copy exited 1 and printed `tickets selftest: FAIL, these did not bite:`. That list includes `worktree dry-run with follow-ups: gamma listed as (worktree wtdr), digest covers only the follow-ups, nothing written`. The mutant also broke the existing `worktree dry-run:` case and several others, so the new case is not the only one that bites. It is still red on the mutant, and green unmutated.
- Diff touches only `tickets.py` in `scripts`, and removes no lines outside `selftest()`: pass. Evidence: `git diff HEAD --stat` shows `plugins/sdlc-lite/scripts/tickets.py | 10 ++++++++++`. `git diff HEAD -U0` shows one hunk `@@ -2074,0 +2075,10 @@ def selftest()` with no removed lines.
- (guard) `tickets.py check` exits 0: pass. Evidence: it printed `ok: 126 tickets, roadmap current` with rc=0.
- `check.sh` shows no new failures versus a HEAD worktree: pass. Evidence: `check.sh` in a detached HEAD worktree exited 0 (base rc=0), and the current tree exited 0 (cur rc=0). The tail of the current run shows `ok: shellcheck` and `ok: plugin validate`. I removed my worktree afterwards.

## Out of scope changes
`.sdlc/0096-tickets-py-selftest-checks-that/handoff.md` is modified. The diff shows it replaces the goal and constraints template text, which is planner output. The step's scope is the scripts folder, so this is harmless. The other new files are under `.sdlc/` (planner and step artifacts) and are not project code.

## For the next attempt
None
