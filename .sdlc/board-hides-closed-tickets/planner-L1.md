<!-- role=planner level=L1 model=sonnet effort=medium -->
## Goal
Make `board.py` hide dropped tickets and closed (done) tickets that never had planner/step work, so `/board` shows only the live set.

## Step 1: Filter dropped and steps-less closed tickets out of the board
level: L1
### Do
In `plugins/sdlc-lite/scripts/board.py`:
- Add a helper (near `ticket_of`) that decides whether a task belongs on the board: given a task dir, read its ticket status via `ticket_of(task)` (already handles missing/broken front matter → `None`). A task is **excluded** only when it has ticket front matter and either:
  - status is `'dropped'` (regardless of whether it has steps), or
  - status is `'done'` **and** it has no recorded step work — i.e. no `planner-L*.md` file, no `step-*/handoff.md`, and no `*.running` file in the task dir.
  Everything else (no front matter, any other status, or `done` with recorded step work) stays visible — this preserves the existing `plain-task`/`raises`/`bare`/`broken` selftest rows, which all report `status: ready` or have no front matter.
- Apply this filter to the `tasks` list built in `main()` (the `sorted((d for d in root.iterdir() ...))` line), before the optional `--task` narrowing and before `render()`/`summary()` are called. Leave `render()`, `summary()`, and `task_rows()` themselves unchanged — the filter is a pre-pass over which task dirs get considered at all.
- Extend `selftest()` with a new fixture root and cases proving the gate bites:
  - a `dropped`-status ticket task with no steps → hidden
  - a `dropped`-status ticket task with a `planner-L1.md` present → still hidden
  - a `done`-status ticket task with no steps → hidden
  - a `done`-status ticket task with a `planner-L1.md` (or `step-1/handoff.md`) present → shown
  - a `proposed`-status ticket task with no steps → still shown (unchanged behavior, guards against over-filtering)

### Acceptance criteria
- `cd plugins/sdlc-lite && python3 scripts/board.py selftest` exits 0 and prints `board selftest: PASS`, and the new dropped/done-filter assertions are present in the function and pass (no entries printed to stderr).
- `plugins/sdlc-lite/scripts/check.sh` passes.
- Manual: build a temp `--root` with one task whose `handoff.md` has `status: dropped` and no `step-*`/`planner-L*.md`, and one task whose `handoff.md` has `status: done` and no `step-*`/`planner-L*.md`; `python3 scripts/board.py --root <tmp>` output contains no row for either task's name.
- Manual: in the same temp root, a task with `status: done` that also has a `step-1/handoff.md` (or a `planner-L1.md`) present still appears as a row.

## Risks
The handoff leaves "closed" undefined against the ticket schema's actual status vocabulary (`proposed, ready, blocked, done, dropped`) — I mapped "closed" to `done`, matching `tickets.py`'s `close` command which sets status to `done`. If a future ticket status is added, this filter will need revisiting, but that's out of scope here.
