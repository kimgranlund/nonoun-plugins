<!-- role=verifier level=L1 model=opus effort=medium -->
## Verdict
fail

## Criteria
- `python3 scripts/board.py selftest` exits 0, prints PASS, and the new dropped/done assertions are present and pass: pass. Evidence: `cd plugins/sdlc-lite && python3 scripts/board.py selftest` printed `board selftest: PASS` with `exit=0` and nothing on stderr. The six new `expect(...)` cases are in the diff under `# 5. Dropped/done filter` in `selftest()`. They cover dropped with no steps, dropped with a planner file, done with no steps, done with a planner file, done with a step handoff, and proposed with no steps.
- `plugins/sdlc-lite/scripts/check.sh` passes: pass. Evidence: it exited 0. The tail read `ok: 18 role levels, 8 agents checked`, `tickets selftest: PASS`, `board selftest: PASS`, `ok: shellcheck`, `ok: plugin validate`.
- Manual: in a temp root, a dropped task with no steps and a done task with no steps get no row: pass. Evidence: I ran `board.py --root $T` on a temp root holding dropped-task, done-task, donestep-task and doneplan-task. It printed rows only for donestep-task and doneplan-task. As a red control, HEAD's board.py (`git show HEAD:...`) on the same root printed rows for `dropped-task` and `done-task`.
- Manual: a done task that has `step-1/handoff.md` or `planner-L1.md` still appears: pass. Evidence: on the same run, `| T-0001 | donestep-task | done | 1. x | ⏳ queued · planned L1 | 0 |` and `| T-0001 | doneplan-task | done | task | ⏳ not planned | 0 |` both appear.
- Reverting only the filter (keeping the new selftest cases) makes selftest fail: fail. Evidence: I ran two negative controls on throwaway copies of `scripts/`.
  - (A) I deleted only the filter application in `main()` (`board.py:372`, `tasks = [t for t in tasks if belongs_on_board(t)]`). Selftest printed `board selftest: PASS`, `A exit=0`. With the filter removed, the board lists dropped tickets again and selftest stays green.
  - (B) I forced `belongs_on_board` to always return True. Selftest failed on 3 assertions, `B exit=1`.
  - So the tests cover the helper but not its wiring into `main()`. The builder only ran control B.
- `board.py --root .sdlc` drops T-0005, T-0008, T-0010, T-0011, T-0012 and T-0018 but keeps T-0014: pass. Evidence: I counted rows per ID with the new script versus HEAD. T-0005, T-0008, T-0010, T-0011, T-0012 and T-0018 each went from 1 row at HEAD to 0 rows. T-0014 has 2 rows in both.
- Docs state the new rule in one line: pass. Evidence: the diff adds one line to `plugins/sdlc-lite/skills/board/SKILL.md` Rules, adds a sentence to the front matter paragraph in `plugins/sdlc-lite/skills/handoff-format/SKILL.md`, and extends the board.py Feed line in root `CLAUDE.md` Layout with "leaves off tasks whose ticket is `dropped` or `done` with no recorded step work".

## Out of scope changes
None. The modified files are board.py, the two SKILL.md files and CLAUDE.md, all named by the step. The untracked files are this task's own `.sdlc` artifacts.

## For the next attempt
The new selftest cases call `belongs_on_board()` directly. Nothing in the tests goes through `main()`, where the filter is actually applied (`plugins/sdlc-lite/scripts/board.py:372`). Deleting that line leaves `board.py selftest` green.

Add at least one selftest leg that goes through `main()`'s task selection. For example, factor the task listing at `board.py:370-372` into a function that `main()` and `selftest()` both call, or run `board.py --root <gate fixture>` as a subprocess. Assert that `dropped-no-steps` and `done-no-steps` do not appear in the output and that `done-with-step` and `proposed-no-steps` do.

Then show the red: delete the line at 372 and confirm selftest fails.
