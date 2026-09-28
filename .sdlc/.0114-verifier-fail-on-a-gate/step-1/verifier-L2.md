<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- c1, `steps.py next` for a done builder plus an `inherited red: test_a` verifier prints `inherited`: pass. Evidence: ran the criterion verbatim under `bash -c` and got rc=0. In a throwaway worktree at HEAD the same fixture printed `reverify L1`, so the check goes red without the change. `steps.py:644` is the new branch, placed after the no-verdict branch and before the pass/fail counting.
- c2 (guard), a `fail` verdict still gives `rebuild L2`: pass. Evidence: rc=0. The new `next rebuild` selftest case also covers it.
- c3 (guard), a bare `inherited red` gives `reverify L1`: pass. Evidence: rc=0. `verdict_or_none` requires the colon (`steps.py` diff, `startswith('inherited red:')`).
- c4, `board.step_row` gives 🔴 and a string starting `inherited red`: pass. Evidence: rc=0. At HEAD the same fixture gave `('🟡', 'no verdict · builder L2 · verifier L1, rerun verify')`, so the check bites.
- c5 (guard), the board still renders `fail` as 🔴 `fail…`: pass. Evidence: rc=0.
- c6, `steps.py` holds the fixture string `Verdict\ninherited red: `: pass. Evidence: grep rc=0. The string is inside the new selftest fixture.
- c7, `board.py` holds the same fixture string: pass. Evidence: grep rc=0.
- c8, `run-selftest.sh` has the `want_rc 0 verifier L1 … inherited red: ` line: pass. Evidence: grep rc=0. I copied the changed `run-selftest.sh` onto HEAD's `run.sh` and it failed with `verifier result '## Verdict\ninherited red: test_a': exit 3, want 0`, so the line bites.
- c9, `run-selftest.sh` has the `want_rc 3 verifier L1 … inherited red'` line: pass. Evidence: grep rc=0 (`run-selftest.sh` diff).
- c10 (guard), `steps.py selftest`: pass. Evidence: rc=0. It includes the five new cases: inherited gives `inherited`; bare gives `reverify L1`; fail, rebuild, inherited gives `inherited`, not `bump`; inherited, rebuild, fail gives `rebuild L2`; and a plain fail gives `rebuild L2`.
- c11 (guard), `board.py selftest`: pass. Evidence: rc=0. It includes the new `('🔴', 'inherited red · builder L2 · verifier L1, ask the user')` case.
- c12 (guard), `run-selftest.sh`: pass. Evidence: rc=0 on the changed tree.
- Do items not covered by the numbered criteria: pass. Evidence:
  - The `steps.py` module docstring has the new `next` rule.
  - The `board.py` docstring is updated.
  - The `run.sh` allowed value is `pass|fail|inherited red: .+`, and the header comment is updated.
  - The no-verdict loop in `board.py` treats `inherited red:` as a verdict.
  - `steps.py` counting uses `verdict_or_none(w) == 'fail'`, so an inherited verdict never counts as a fail.
  - `scripts/check.sh` runs green (rc=0, including shellcheck and plugin validate).

## Out of scope changes
None. The step's four scripts changed as called for. The other changes are `.sdlc/0114-verifier-fail-on-a-gate/` handoff and artifact files, which predate this step and are ticket bookkeeping. `git worktree list` shows no leftover throwaway worktree.

## For the next attempt
None. Only the scripts changed; the chain and conductor docs and the `check.py` inherited-red route guard still name only the builder Status. The step did not call for those, so they belong to a later step (step-2 exists).
