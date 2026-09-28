## Task goal
Define `step-<n>.superseded-<k>/` as the name for a step dir replaced by a replan. `board.py` and `bench-summary.sh` skip it when counting steps, but still count its cost, and `/chain` and `handoff-format` document and perform the rename.

## Step 1: board.py ignores superseded dirs, with selftest
level: L2
### Do
In `plugins/sdlc-lite/scripts/board.py`:
- Add a helper `live_step_dirs(task)`. It returns `task.glob('step-*')` entries that are dirs and match `re.fullmatch(r'step-\d+', d.name)`.
- Use the helper in `plan_steps` (~line 109). Sort by `int(d.name[5:])` and keep the existing filter on `handoff.md` existing. The later `int(d.name.split('-')[1])` at ~line 118 stays valid for live dirs.
- Use the helper in the `--summary` L5 check (~line 170), replacing `t.glob('step-*/builder-L5.*')` with a check over live dirs.
- Leave `cost()` (line 54) and `has_step_work` (line 190) on the `step-*` glob. Superseded dirs still count for cost and recorded work. Add a short comment on each saying so.
- Update the module docstring (line 13) to mention that superseded dirs are ignored.

Add a selftest case in the same file, following the existing `expect(...)` style near line 410:
- Build a task with `step-1/handoff.md`, `step-2/handoff.md`, and `step-2.superseded-1/handoff.md`. Give the superseded dir a `builder-L5.md` and a `runs.jsonl` line with `cost_usd`.
- Expect `plan_steps` to return exactly two steps.
- Expect the rendered board to have exactly two step rows.
- Expect `--summary` to show no `⚠ L5`.
- Expect `cost()` to include the superseded dir's cost.
- Expect `has_step_work` to be true for a task whose only handoff sits in a superseded dir.

### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/board.py selftest` passes and includes the new superseded cases.
- Negative control: temporarily revert the helper in `plan_steps`. The new selftest case must then fail; restore it afterwards.
- Manual: create a temp `.sdlc/x/` with `step-1`, `step-2`, and `step-2.superseded-1` (each with `handoff.md`) and run `board.py --root <tmp>`. The output has exactly two step rows and no second "2." row.
- The existing board and tickets selftests still pass.

## Paths
Edit only files in this worktree (/Users/kimba/Projects/nonoun/sdlc-lite-wt-tickets7/plugins/sdlc-lite). Do not commit.
