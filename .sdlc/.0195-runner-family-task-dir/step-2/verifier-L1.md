<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- Criterion 1 (verifier at a task dir whose `step-1/` holds a luna builder): pass. Evidence: the command printed `('gpt-6.1-sol', 'low', False) ('gpt-6-luna', 'low', True)` and exited 0. The alternate applies, and with alternates emptied the verifier shares the builder's model.
- Criterion 2 (superseded dirs ignored, step order numeric): pass. Evidence: it printed `[('gpt-6.1-sol','low',False), ('gpt-6.1-sol','low',False)]` and exited 0. In dir `a`, `step-2.superseded-1` is ignored and `step-2` holds no builder, so `step-1` is read. In dir `z`, `step-10` beats `step-2`.
- (guard) Criterion 3 (the task dir's own `builder-L3.md` wins over step dirs): pass. Evidence: it printed `('gpt-6-luna', 'low', False)` and exited 0. The other-model builder at the task dir takes priority, so no alternate switch occurs.
- Criterion 4 (run.sh in Codex dry-run mode picks the alternate): pass. Evidence: the command exited 0 (c4=0), and the dry-run output contains `--model gpt-6.1-sol --effort low`.
- Criterion 5 (the new test goes red against the base code): pass. Evidence: I extracted base-SHA `plugins/sdlc-lite` with the new selftest copied in. The test failed there and `out` had a line starting `AssertionError` (exit 0).
- Criterion 6 (the new test passes on the built tree): pass. Evidence: `Ran 1 test in 0.170s OK`.
- (guard) Criterion 7 (full selftest): pass. Evidence: `Ran 23 tests in 21.182s OK`, rc=0. I did not run this gate at base, since it is green.
- Criterion 8 (doc contains `step-<n>.superseded-<k>`): pass. Evidence: grep exit 0. The diff shows the new sentence on line 46.
- Criterion 9 (scope): pass. Evidence: the diff names only `codex_roles.py`, `codex-selftest.py` and `docs/references/codex-role-execution.md`, all on the allowed list. There are no untracked files outside `.sdlc`. `git diff --check` is clean.
- Steelman pass: I considered failing the "steps that hold a builder" selection, because the Do names the largest `n` overall. Step 1's rules 2 and 3 are "highest that holds one", and sub-case 2 (`step-2` has only a handoff) expects `step-1`, so the code matches the Do. Dropped.
- Test coverage against the Do: the test method has all five sub-cases from the Do. The plan-reviewer sub-case expects `('gpt-6-astra','high',False)`, which the code returns.

## Out of scope changes
None.

## For the next attempt
None
