<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/steps.py`: added `lean_warnings(plan, task_dir, steps)`. `cmd_lint` now prints its warnings on stderr after a clean lint. The lint docstring entry is extended, an argparse epilog holding the literal `steps lint: warning:` was added, and there are four new `(lean)` selftest cases.
- `docs/maintenance/sdlc-internals.md`: added one parenthetical to the `lint` sentence naming `steps lint: warning:`, the eligibility conditions and both triggers.

## Checks
- `python3 plugins/sdlc-lite/scripts/steps.py selftest`: rc 0, `steps selftest: PASS`. All four `ok: (lean) ...` labels are present (each label checked with `grep -qF`, all 0).
- Criterion 5 (one-step L1 plan in `planner-L2.md`, lint stderr holds `steps lint: warning:`): 0.
- Criterion 6 (guard: lint stdout is exactly `steps lint: ok`): 0.
- Criterion 7 (`steps.py -h | grep -qF "steps lint: warning:"`): failed (1) on the first try, then 0 after adding the epilog. Also 0 with `COLUMNS=40`.
- Criterion 8 (`grep -qF "steps lint: warning:" docs/maintenance/sdlc-internals.md`): 0.
- Criterion 9 (guard: scope limited to the two files, against `SDLC_BASE_SHA=99d29b8`): 0.
- `git diff --check`: clean.

## Notes
- `steps.py -h` builds its help with argparse, which uses only the first docstring line. Extending the docstring alone did not put the literal into `-h`. To satisfy the criterion I set `formatter_class=argparse.RawDescriptionHelpFormatter` on the top-level parser and added an epilog that lists the eligibility conditions and the warning literal. This only changes how the one-line description and the epilog wrap; subcommand help is unchanged.
- In the "no warning" selftest case, each of the six plans has three one-criterion steps. So every dir would warn if it were wrongly eligible, which makes the case able to fail. The replan dir holds both `planner-L1.md` and `planner-L2.md`.
- Existing check (j) still passes without changes.
