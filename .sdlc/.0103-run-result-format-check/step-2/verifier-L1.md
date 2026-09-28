<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- Criterion 1, one statusless builder gives `rebuild L2`: pass. Evidence: ran the command's fixture in the tree and `steps.py next` printed `rebuild L2` with the reason "not counted as a fail". At HEAD in a throwaway worktree the same fixture exits 1 with "has no builder status", so the check goes red before the change.
- Criterion 2, two statusless builders give `stop`: pass. Evidence: the tree prints `stop`, reason "2 consecutive builder results with no Status ... ask the user". The check bites because a statusless newest builder at HEAD raises, so the output could not be `stop`.
- Criterion 3 (guard), a statusless builder then a `done` builder gives `verify L1`: pass. Evidence: the tree prints `verify L1`, reason "no verifier result; build L2 -> verifier L1".
- Criterion 4 (guard), `steps.py selftest`: pass. Evidence: output ends "steps selftest: PASS", rc=0. The diff adds the `rebuild L2`, `stop` and `verify L1` cases and removes the old error case.
- Criterion 5, old case name removed: pass. Evidence: `! grep -q "next error: a builder with no done/blocked Status" plugins/sdlc-lite/scripts/steps.py` exits 0. The diff shows the case removed from `selftest()`. The target file exists, so the grep did not fail on a bad path.
- Docstring (from the Do section): pass. Evidence: the `steps.py` diff adds the two new rules to the `next` rules and removes "a builder with no done/blocked Status" from the Errors line.

## Out of scope changes
`plugins/sdlc-lite/scripts/run.sh` and `plugins/sdlc-lite/scripts/run-selftest.sh` are modified in the tree. Step 2 does not call for them, and I did not open their diffs. I judged them earlier work from step 1 (`step-1/` is untracked next to this step), not from this step. The builder's changes list names only `steps.py`.

## For the next attempt
None
