<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/board.py`: added selftest section 5f for dot-prefixed ticket folders. This is a selftest-only change (+28 lines).
- `plugins/sdlc-lite/scripts/steps.py`: added selftest case (i), which runs `split` on a `.0003-x` task dir. This is a selftest-only change (+10 lines).

Neither script's logic changed. Both selftests passed as written, so no fix was needed.

## Checks
- `python3 plugins/sdlc-lite/scripts/board.py selftest`: 🟢 printed `board selftest: PASS`. The new section 5f covers:
  - `.0003-closed-work` renders as `| T-0003 | .0003-closed-work |`.
  - `.0004-closed-bare` (done, no step work) is hidden.
  - `.0005-gone` (dropped) is hidden.
  - `_templates/feature.md` and `.board-state.json` produce no row.
  - Under the default id sort, the order is `0002-open`, `.0003-closed-work`, `0006-later`.
  - `--task .0003-closed-work` renders only that task.
- `python3 plugins/sdlc-lite/scripts/steps.py selftest`: 🟢 exit 0, prints `steps selftest: PASS`, including `ok: (i) split on .0003-x writes .0003-x/step-1/handoff.md`.
- Manual temp-root check with `board.py --root <root>`: 🟡 one criterion fails as literally worded.
  - The output contains `.0001-a` and `0003-c` as table rows.
  - It does not contain `.0002-b` or `_templates`.
  - It does contain `board-state`, but only in the legacy hint line below the table (`Note: legacy .../.board-state.json is no longer used ...; safe to delete.`). No table row mentions it.
- `git diff --stat plugins/sdlc-lite/scripts/board.py plugins/sdlc-lite/scripts/steps.py`: 🟢 `board.py | 28 +`, `steps.py | 10 +`, insertions only.

## Notes
The acceptance criterion "output does not contain `board-state`" conflicts with a documented feature. CLAUDE.md says board.py prints a one-line hint when a legacy `.sdlc/.board-state.json` exists, so any root holding that file will show `board-state` in the output. I did not change the hint, because that would be out of scope and would break documented behavior. The board selftest checks the intended property instead: no table row mentions `board-state`. The planner should reword this criterion to cover table rows only, or drop `.board-state.json` from that fixture.
