<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- Criterion 1 (`next` on `inherited red: test_a` prints `inherited` first): pass. Evidence: I ran the exact `&&` chain from the repo root. It printed `CRIT1 OK`, and the output began with `inherited`. In a throwaway worktree at HEAD the same input gave `rebuild L2`, so the check goes red before the change.
- Criterion 2 (`grep -q "next inherited: " steps.py`): pass. Evidence: the grep exited 0, and the selftest output shows four `ok: next inherited: ...` lines.
- Criterion 3 (`grep -q 'inherited red:' steps.py`): pass. Evidence: the grep exited 0. The diff shows the string in the docstring, in `build_status_or_none`, and in the selftest cases.
- (guard) `steps.py selftest`: pass. Evidence: it printed `steps selftest: PASS`. The four cases are:
  - (a) the newest builder is inherited, giving `inherited`.
  - (b) an inherited builder then a done builder gives `verify L1`.
  - (c) done, a verifier FAIL, then inherited gives `inherited`.
  - (d) a bare `inherited red` with no colon gives `rebuild L2`.
- Do items, checked against `git diff`:
  - `build_status_or_none` returns `inherited`.
  - The new branch sits after the statusless branch and before the `blocked` check, and its return text matches the handoff.
  - The docstring line is added.
  - The builder list now keeps only `done` and `blocked` results. This is a small addition beyond the handoff's wording, and it serves the "never a counted fail" rule.

## Out of scope changes
None from the builder. The diff touches only `plugins/sdlc-lite/scripts/steps.py` (26 lines), plus the `.sdlc/0101-builder-inherited-red/` planning artifacts. The modified `.sdlc/0101-builder-inherited-red/handoff.md` is task-level plan state, not project code, so I dismiss it as harmless.

## For the next attempt
None
