## Task goal
A closed ticket's task row reads as closed, not 'not planned'.

## Step 1: Render a done ticket as closed, with a selftest
level: L2
### Do
In `plugins/sdlc-lite/scripts/board.py`, make two changes.
1. In `task_rows`, in the `elif not steps:` branch, emit a `🟢`, `closed`, 100 row instead of `⏳ not planned` when `ticket_of(task)` reports status `done`. Keep `⏳ not planned` for every other status and for tasks without front matter.
2. In `summary`, when `step_rows` is empty and no `*.running` file exists, return `<name> closed` when the ticket is `done`. Otherwise return `<name> not planned` as now.

Add a fixture to `selftest()` and land it with the fix.
- The fixture is a task folder whose handoff has the `done` front matter (the `front` template with `status: done`).
- It holds `step-1/builder-L1.md` and no `planner-L*.md` and no `step-*/handoff.md`.
- Assert `task_rows` gives a `closed` row and no `not planned` row.
- Assert `summary(root)` returns `<name> closed`.
- Assert that the same fixture with `status: ready` still gives `not planned`, so the check bites.

Do not change the existing selftest expectations for unticketed or `ready` tasks. Update the `board.py` description in `CLAUDE.md` with one clause saying a `done` ticket with no plan renders as `closed`.
### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/board.py selftest` exits 0 and prints `board selftest: PASS`. It is red now only on the new fixture assertions, which are absent, so add them first and confirm they fail on the unfixed code.
- Read the new fixture in `selftest()` and check that it uses `status: done` with only `step-1/builder-L1.md`. It asserts a `closed` row and the `<name> closed` summary, and it has a `ready` control that still expects `not planned`.
- (guard) `python3 plugins/sdlc-lite/scripts/board.py selftest` still shows the byte-for-byte 4-column table for tasks without front matter.
- (guard) `plugins/sdlc-lite/scripts/check.sh` exits 0 with no new findings versus the base commit. Its shellcheck and validate output is the same as the same command run in a `git worktree add <tmp> HEAD` copy.
