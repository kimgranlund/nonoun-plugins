<!-- role=planner level=L1 model=sonnet effort=medium -->
## Goal
board.py classifies every `tickets.ENUMS['status']` value as shown or hidden in named sets, and its selftest fails when the two drift apart.

## Step 1: Named visibility sets, drift guard, and negative control
level: L2

### Do
In `plugins/sdlc-lite/scripts/board.py`:
- Add module-level frozensets above `belongs_on_board`:
  - `ALWAYS_HIDDEN = frozenset({'dropped'})`
  - `HIDDEN_WITHOUT_STEP_WORK = frozenset({'done'})`
  - `ALWAYS_SHOWN = frozenset({'proposed', 'ready', 'blocked'})`
  - Add a short comment saying that a new status in `tickets.ENUMS['status']` must be classified here, and that the selftest enforces it.
- Rewrite `belongs_on_board` to use the sets:
  - Return False if `status in ALWAYS_HIDDEN`.
  - Return False if `status in HIDDEN_WITHOUT_STEP_WORK and not has_step_work(task)`.
  - Otherwise return True, so unknown statuses stay visible.
  - Keep the `front is None` early return, and update the docstring only if needed.
- Add a helper `unclassified_statuses(known)`. It returns the set difference between `known` and the union of the three sets. It also reports any pair of the three sets that overlap, or any classified status missing from `known`. Return a list of problem strings (empty means OK).
- In `selftest()`, after the gate section 5b and before `if misses:`, add these checks:
  - **Consistency:** `unclassified_statuses(set(tickets.ENUMS['status']))` returns an empty list.
  - **Negative control:** `unclassified_statuses(set(tickets.ENUMS['status']) | {'zz-new-status'})` is non-empty and mentions `zz-new-status`.
  - **Overlap check:** a synthetic overlap, for example `dropped` also passed as a second set, is detected. Only do this if the helper takes the sets as parameters with the module sets as defaults.
- Do not touch `tickets.py` or the existing dropped/done tests.
- Check `CLAUDE.md` (the `board.py` line in the Layout section) and `skills/board/SKILL.md`. Edit them only if they describe the filter in a way this changes. The visible behavior is unchanged, so they probably need no edit.

### Acceptance criteria
- `python3 plugins/sdlc-lite/scripts/board.py selftest` prints `board selftest: PASS` and exits 0.
- `grep -n "'dropped'\|'done'" plugins/sdlc-lite/scripts/board.py` shows no literal status checks inside `belongs_on_board`. The literals appear only in the named sets and the selftest fixtures.
- Negative control: temporarily add `'zz'` to the `status` list in `tickets.ENUMS` (in a scratch copy or by patching in memory, without committing). `board.py selftest` then exits 1 and names `zz`. Alternatively, run `python3 -c "import sys; sys.path.insert(0,'plugins/sdlc-lite/scripts'); import board, tickets; print(board.unclassified_statuses(set(tickets.ENUMS['status'])|{'zz'}))"` and confirm it is non-empty and names `zz`.
- The existing selftest expectations (dropped/done, sort, the 4-column table) are unchanged in the diff. `git diff` shows no edits to `tickets.py`.
- `plugins/sdlc-lite/scripts/check.sh` passes. Run it from `plugins/sdlc-lite`, since `CLAUDE.md` gives `scripts/check.sh` as the command.

## Risks
- The `ENUMS['status']` key name or shape may differ from what the handoff assumes. The builder should confirm at `tickets.py` line 37.
- `check.sh` runs shellcheck and `claude plugin validate`, and the latter may need the CLI. A failure there that has nothing to do with `board.py` should be reported, not fixed.
