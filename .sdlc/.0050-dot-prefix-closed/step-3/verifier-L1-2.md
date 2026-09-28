<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- `board.py selftest` prints `board selftest: PASS`: pass. Evidence: I ran `python3 plugins/sdlc-lite/scripts/board.py selftest` and it printed `board selftest: PASS`. The new selftest block sits at board.py:587 onward and covers all six required cases. As a negative control I copied the scripts to a temp dir and added a dot-name filter to the candidate list. The selftest then failed on the dot-folder ID render, the id sort and `--task` checks, so it can go red.
- `steps.py selftest` exits 0: pass. Evidence: I ran `python3 plugins/sdlc-lite/scripts/steps.py selftest` and it exited 0 (`steps=0`). Case (i) is a new `split` on `.0003-x`, and it asserts that `step-1/handoff.md` exists with the expected content.
- Temp-root board run: pass. Evidence: I built `.0001-a` (done, with `planner-L1.md`), `.0002-b` (done, no step work), `0003-c` (ready), `_templates/feature.md` and `.board-state.json`. `board.py --root <root>` printed table rows for `T-0001 | .0001-a` and `T-0003 | 0003-c` only. There is no `.0002-b`, `_templates` or `board-state` row. The only `board-state` mention is the expected legacy-hint Note line below the table.
- `git diff --stat` shows selftest-only changes, or a stated minimal fix: pass. Evidence: `git diff` on board.py shows +28 lines, all inside `selftest()` (5f block). steps.py shows +10 lines, all inside `selftest()` (case i). No production code changed in either script.

## Out of scope changes
- `plugins/sdlc-lite/scripts/tickets.py` has 248 changed lines. It is most likely other steps' work; the handoff for this step does not call for it.
- `.sdlc/0050-dot-prefix-closed/handoff.md` is modified, and the other step dirs and planner files are untracked. This is normal task bookkeeping.

## For the next attempt
None
