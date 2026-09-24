<!-- role=filer level=L1 model=opus effort=low -->
## Warnings
None

## PR title
T-0015: board hides dropped tickets and done tickets with no step work

## PR body
### Summary
Since T-0009, `/board` reads ticket front matter. Because of that it showed every dropped ticket and every closed ticket that was never planned. The board now shows only the live set.

### Changes
- `plugins/sdlc-lite/scripts/board.py`:
  - Adds two helpers, `has_step_work` and `belongs_on_board`.
  - `main()` filters the task list before rendering. A task is hidden when its ticket status is `dropped`, or when the status is `done` and the task has no recorded step work (no `planner-L*.md`, no `step-*/handoff.md`, no `*.running`).
  - Tasks with no front matter and tasks with any other status are unchanged.
- `board.py selftest`:
  - New unit cases on `belongs_on_board`: dropped with no steps, dropped with a plan, done with no steps, done with a plan, done with a step, and proposed with no steps.
  - A new subprocess leg runs `board.py --root <fixture>` and asserts the same set against the rendered output of `main()`.
- Docs: `skills/board/SKILL.md`, `skills/handoff-format/SKILL.md` and the root `CLAUDE.md` Feed line each state the new rule.

### Verification
The independent verifier (L1, Opus medium) passed on attempt 2. Attempt 1 failed because its selftest called `belongs_on_board()` directly, so deleting the filter line in `main()` left selftest green. Attempt 2 added the subprocess leg to close that gap.
- `python3 scripts/board.py selftest` exits 0 and prints `board selftest: PASS`.
- `scripts/check.sh` exits 0: role levels, agents, tickets selftest, board selftest, shellcheck and plugin validate all pass.
- Negative control: with the filter line in `main()` deleted, selftest fails on the three hide assertions. With the line restored, it passes.
- Manual temp root:
  - A dropped task and a done task, neither with step work, render no rows.
  - A done task with `step-1/handoff.md` and a done task with `planner-L1.md` both still render.
- Repo backlog (`board.py --root .sdlc`):
  - T-0005, T-0008, T-0010, T-0011, T-0012 and T-0018 no longer appear.
  - T-0014 (done, with steps) still appears.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- Fixed: `/board` no longer lists dropped tickets or done tickets that never had planned or built steps (T-0015).

## Follow-ups
- board.py hides tickets by the hardcoded statuses `dropped` and `done`, so if tickets.py adds a new ticket status, update the filter to handle it.
