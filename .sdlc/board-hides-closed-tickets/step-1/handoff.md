## Task goal
/board shows the live set only: no dropped tickets, and no done tickets that never had steps. (Ticket T-0015, `.sdlc/board-hides-closed-tickets/handoff.md`; its Goal and Constraints sections are binding: the failing test lands before or with the fix, never after.) Repo root: the git work tree containing this `.sdlc/`. Proposed, ready, and blocked tickets stay visible even without steps.

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
- Reverting only the filter (keeping the new selftest cases) makes `python3 plugins/sdlc-lite/scripts/board.py selftest` fail; with the filter it passes.
- `python3 plugins/sdlc-lite/scripts/board.py --root .sdlc` (this repo's backlog) no longer lists T-0008, T-0010, T-0011, T-0012 (dropped) or T-0005, T-0018 (done, no steps); done tickets with steps (e.g. T-0014) still appear.
- Any doc that says which tasks the board lists (`plugins/sdlc-lite/skills/board/SKILL.md`, `skills/handoff-format/SKILL.md`, root `CLAUDE.md` Layout line for board.py) states the new rule in one line, in the same change.

## Previous attempt
Verifier L1 failed attempt 1 (builder L1). Keep the existing changes; fix only this.

The new selftest cases call `belongs_on_board()` directly. Nothing in the tests goes through `main()`, where the filter is actually applied (`plugins/sdlc-lite/scripts/board.py:372`). Deleting that line leaves `board.py selftest` green.

Add at least one selftest leg that goes through `main()`'s task selection. For example, factor the task listing at `board.py:370-372` into a function that `main()` and `selftest()` both call, or run `board.py --root <gate fixture>` as a subprocess. Assert that `dropped-no-steps` and `done-no-steps` do not appear in the output and that `done-with-step` and `proposed-no-steps` do.

Then show the red: delete the line at 372 and confirm selftest fails.
