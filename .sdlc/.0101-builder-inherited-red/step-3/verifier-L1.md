<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- Criterion 1, the `step_row` python check on an `inherited red` builder: pass. Evidence: from the repo root the command printed `🔴 inherited red · builder L2, ask the user` and exited 0. In a throwaway worktree at HEAD (before the change) the same command printed `🟡 built · builder L2, awaiting verify` and exited 1, so the check can go red. The biting conjunct is the `🔴` glyph and the `inherited red` prefix, and both are absent at HEAD.
- Criterion 2, `grep -q 'inherited red' plugins/sdlc-lite/scripts/board.py`: pass. Evidence: grep exit 0. The diff adds the string in the docstring, `step_row` and the selftest.
- Criterion 3, `(guard)` `python3 plugins/sdlc-lite/scripts/board.py selftest`: pass. Evidence: it printed `board selftest: PASS` and exited 0.
- Do: check placed right after the `blocked` check on the newest builder, with the exact return tuple: pass. Evidence: the `git diff` hunk at `step_row` adds `return '🔴', f'inherited red · builder {level_of(last_build)}, ask the user{tries}', LADDER['building']`.
- Do: docstring Status paragraph mentions the rendering: pass. Evidence: the diff adds two lines after the rerun/order.py sentence, ending "--summary counts it in 🔴<n>". The docstring says `--summary` counts it and I did not run `--summary`. The code change is only in `step_row`, and the step says `--summary` needs no other change.
- Do: selftest case in section 7 using `step_fixture`, with an expect label containing `inherited red`: pass. Evidence: the diff adds the case. The label is "an inherited red builder renders as 🔴 inherited red, got ...". The selftest passes.

## Out of scope changes
None from this step. `git status` also shows `handoff.md`, `run.sh`, `run-selftest.sh` and `steps.py` modified, plus untracked step dirs and planner files. The builder says these predate the step, and the step's `board.py` diff touches none of them. Whether steps 1 and 2 changed them was not checked, and this step's diff does not depend on them.

## For the next attempt
None
