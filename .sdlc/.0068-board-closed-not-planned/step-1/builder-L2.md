<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/board.py`: in `task_rows`, a task with no plan whose ticket is `done` now gets a `🟢 closed 100` row. In `summary`, the same case returns `<name> closed`. Added selftest fixture 5c, with a `ready` control that still expects `not planned`.
- `CLAUDE.md`: added one clause to the `board.py` description saying a `done` ticket with no plan renders as a `closed` task row and `--summary` line.

## Checks
- `python3 plugins/sdlc-lite/scripts/board.py selftest`, run after adding the fixture and before the fix: exit 1. The four new `done` assertions failed and the `ready` control held.
- `python3 plugins/sdlc-lite/scripts/board.py selftest`, run after the fix: exit 0, printed `board selftest: PASS`. Case 1 (the byte-for-byte 4-column table for a task with no front matter) is unchanged and passes.
- `plugins/sdlc-lite/scripts/check.sh`: exit 0, ending `ok: shellcheck` and `ok: plugin validate`.
- The same `check.sh` in a `git worktree add <tmp> HEAD` copy: exit 0. I diffed the shellcheck, warning, and validate lines between the two runs and they match. The temp worktree has been removed.

## Notes
- Fixture 5c builds the task folder from the shared `front` template with `status: done` or `status: ready`. It contains only `step-1/builder-L1.md`: no planner file and no step handoff.
- Existing fixture 5 `done-with-plan` (a planner file that lists no steps) now also renders as `closed`. Its assertions only check that the task is visible, so they still pass.
