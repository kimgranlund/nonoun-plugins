## Task goal
Which result is newest (builder, verifier, planner) is decided from recorded run order, so a fresh clone or a committed .sdlc/ trail reads the same verdicts as the machine that ran them.

## Step 2: board.py reads verdicts through order.py
level: L2
### Do
- In `plugins/sdlc-lite/scripts/board.py`:
  - `by_level(d, role, 'md')` returns `order.ordered(d, role)`.
  - For `.running` files, sort by `(level number, name)`, with no mtime.
  - At line 93, the verifier-after-build test becomes `order.counts_after(verifies[-1], last_build)`.
  - `plan_steps` gets the newest plan through the same `by_level`.
  - Update the docstring line "the newest file by mtime wins" to state the runs.jsonl rule.
  - Leave the task-recency uses alone (`summary`'s task pick, and `sort_tasks`, including their selftests). They are display order, not verdicts.
- Add a board selftest case with equal mtimes on every file. Step dir with runs.jsonl records in this order:
  1. builder L1
  2. verifier L1 with `## Verdict` fail
  3. builder L2
  4. verifier L2 with `## Verdict` pass

  Expected row: 🟢 pass · builder L2 · verifier L2. Second fixture: the last record is a builder run after the passing verifier. Expected row: awaiting verify. Also include one fixture whose mtimes are inverse to the record order.
### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/board.py selftest` exits 0.
- `grep -n "st_mtime" plugins/sdlc-lite/scripts/board.py` shows only the lines in `summary` (task pick), `sort_tasks`, and their selftest. None are in `by_level`, `step_row`, or `plan_steps`.
- Copy `bench/results/2026-09-24-button-geometry-model` into `<tmp>/results/`, `touch` every file to one time, and run `board.py --root <tmp>/results`. It shows step 2 as 🟢 pass · builder L3 · verifier L2.
- Negative control: reverting line 93 to the mtime comparison makes the new selftest case fail.
