<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- `board.py selftest` exits 0 and prints `board selftest: PASS`, red on the unfixed code: pass. Evidence: on the fixed tree it printed `board selftest: PASS`. In a throwaway HEAD worktree I put in the new board.py and reverted only the two fix hunks. It then failed on the four new assertions: `done ticket with no plan renders 'closed', got ['not planned']`, `... has no not planned row`, `closed row is green at 100`, `done ticket summary reads shipped closed, got 'shipped not planned'`. The `ready` control did not fail, as intended. The exit code was not captured for either selftest run: `PIPESTATUS` is empty under zsh. Exit 0 rests on the PASS line and on the `check.sh` rc=0, which runs this selftest.
- New fixture reads correctly: pass. Evidence: the diff adds section 5c to `selftest()` (board.py, about line 514). It loops over `('done','closed')` and `('ready','not planned')`, using `front.replace('status: ready', f'status: {status}')`. The only files created are `step-1/builder-L1.md`, with no planner file and no `step-*/handoff.md`. It asserts the `closed` row, a green 100 row, no `not planned` row, and the summary `shipped closed` for done. The `ready` control expects `not planned` in both the row and the summary.
- (guard) The 4-column table for tasks without front matter is unchanged: pass. Evidence: the selftest PASS covers the existing unticketed expectations, and the diff touches none of them. I did not separately confirm that this selftest block asserts the table byte for byte.
- (guard) `check.sh` exits 0 with no new findings versus base: pass. Evidence: `check.sh` on the working tree exited 0 (`rc=0`). I compared the last 15 lines of `check.sh` output from the HEAD worktree and the working tree. The only diff was the `rc=` label, and both rc values were empty from the same `PIPESTATUS` problem. The new output ends `ok: shellcheck`, `ok: plugin validate`.

## Out of scope changes
None. The changes are `board.py`, the one-clause `CLAUDE.md` update the step asked for, and untracked `.sdlc` artifacts.

## For the next attempt
None
