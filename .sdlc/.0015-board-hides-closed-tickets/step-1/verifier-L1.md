<!-- role=verifier level=L1 model=opus effort=medium -->
## Verdict
pass

## Criteria
- `board.py selftest` exits 0, prints `board selftest: PASS`, and the new dropped/done assertions are present and pass: pass. Evidence: `cd plugins/sdlc-lite && python3 scripts/board.py selftest` printed `board selftest: PASS` and exited 0, with nothing on stderr. The new cases are in the diff at board.py selftest §5: `belongs_on_board` unit legs for dropped-no-steps, dropped-with-plan, done-no-steps, done-with-plan, done-with-step and proposed-no-steps. §5b adds a subprocess leg that runs `board.py --root <gate>` and asserts the same set in main() output.
- `check.sh` passes: pass. Evidence: `bash plugins/sdlc-lite/scripts/check.sh` exited 0 and printed `ok: 18 role levels, 8 agents checked`, `selftest: PASS`, `tickets selftest: PASS`, `board selftest: PASS`, `ok: shellcheck`, `ok: plugin validate`.
- Manual: a temp root with a dropped task and a done task, neither with steps, shows no row for either: pass. Evidence: the temp root held `dropd` (dropped, T-0001) and `donen` (done, T-0002), both with no step work. `board.py --root $T` rendered rows only for T-0003 `dones` and T-0004 `donep`. There was no dropd row and no donen row.
- Manual: a done task with a `step-1/handoff.md` or a `planner-L1.md` still appears: pass. Evidence: the same run showed `| T-0003 | dones | done | 1. x | ...`, which has a step-1/handoff.md, and `| T-0004 | donep | done | task | ⏳ not planned |`, which has a planner-L1.md.
- Reverting only the filter makes selftest fail, and restoring it makes selftest pass: pass. Evidence: in a temp copy of `scripts/`, I deleted board.py:386 (`tasks = [t for t in tasks if belongs_on_board(t)]`) with sed. `python3 board.py selftest` then printed `FAIL` with `main() output hides dropped-no-steps`, `... dropped-with-plan` and `... done-no-steps`, and exited 1. After restoring the file it printed `PASS` and exited 0. The subprocess leg is what bites here: the `belongs_on_board` unit legs stay green without the filter line.
- The repo backlog board hides T-0008, T-0010, T-0011, T-0012, T-0005 and T-0018, and still shows T-0014: pass. Evidence: I took the first two columns of every row from `board.py --root .sdlc`. The ID set is T-0001, 0002, 0003, 0004, 0006, 0007, 0009, 0013, 0014, 0015, 0016, 0017, 0019. A plain grep also finds T-0012, but only inside T-0013's step title text, not as a row. The done tickets still shown (T-0001 to T-0004, T-0006, T-0009) all have step dirs or planner files. T-0005 and T-0018 have none.
- The docs state the new rule in one line: pass. Evidence: the diff adds one line each to `plugins/sdlc-lite/skills/board/SKILL.md` (a new rule bullet), `skills/handoff-format/SKILL.md` (a sentence after the front matter paragraph) and root `CLAUDE.md` (the Feed line: "leaves off tasks whose ticket is `dropped` or `done` with no recorded step work").

## Out of scope changes
None. The modified files are CLAUDE.md, board.py, skills/board/SKILL.md and skills/handoff-format/SKILL.md, all called for by the step. The untracked files under `.sdlc/0015-board-hides-closed-tickets/` are task artifacts.

## For the next attempt
None
