<!-- role=filer level=L1 model=opus effort=low -->
## Warnings
None

## PR title
T-0068: Board shows a done ticket with no plan as closed, not "not planned"

## PR body
### Summary
After a ticket was closed, the board and status line showed its task as `not planned`. The task had step results but no planner file. A done ticket now shows as closed.

### Changes
- `plugins/sdlc-lite/scripts/board.py`
  - `task_rows`: a task with no plan whose ticket is `done` gets a `🟢 closed 100` row. Every other status, and tasks without front matter, still get `⏳ not planned`.
  - `summary`: in the same case it returns `<name> closed`.
  - New selftest fixture 5c: a task with `status: done` holding only `step-1/builder-L1.md`. It asserts a closed row, a green 100 row, no `not planned` row, and the `<name> closed` summary. A `status: ready` control still expects `not planned`.
- `CLAUDE.md`: the `board.py` description gains one clause saying a `done` ticket with no plan renders as a `closed` task row and `--summary` line.

### Verification
- The builder ran `board.py selftest` with the fixture added and before the fix: it exited 1 on the four new `done` assertions, and the `ready` control held. After the fix it printed `board selftest: PASS`.
- The verifier separately put the new board.py in a throwaway HEAD worktree and reverted only the two fix hunks. The same four assertions failed and the control did not.
- `check.sh` exited 0, ending `ok: shellcheck` and `ok: plugin validate`. Compared with a HEAD worktree copy, it showed no new findings.
- The verifier's verdict is pass. It noted two limits:
  - Selftest exit codes were not captured because `PIPESTATUS` is empty under zsh. Exit 0 rests on the PASS line and on `check.sh` returning 0, since `check.sh` runs this selftest.
  - It did not separately confirm that the unticketed-table guard asserts byte for byte. It found that the diff leaves that block untouched.
- Side effect: the existing fixture 5 `done-with-plan`, whose planner file lists no steps, now also renders as `closed`. Its assertions only check that the task is visible, so they still pass.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- Fixed: `/board` and the status line now show a done ticket with no planner file as `closed` instead of `not planned` (T-0068).

## Follow-ups
None
