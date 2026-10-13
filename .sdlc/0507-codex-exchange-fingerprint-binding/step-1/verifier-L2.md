<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- #1 (red) three new tests exit 0 and say 3 tests ran: pass. Evidence: `python3 plugins/sdlc-lite/scripts/codex-selftest.py CodexTests.test_native_exchange_enforces_the_dispatched_profile_binding CodexTests.test_native_exchange_binding_survives_profile_change_after_dispatch CodexTests.test_native_exchange_failed_response_needs_no_profile_line` printed `Ran 3 tests in 2.576s`, `OK`. red-checkpoint.jsonl records this span red (exit 1) pre-edit; no process-deviations.md exists.
- #2 (red) grep for profile_fingerprint in the three files: pass. Evidence: the && chain exited 0. The pre-edit control is recorded red in red-checkpoint.jsonl.
- #3 new assertions fail on the base exchange: pass. Evidence: `git worktree add` is denied by block-stray-worktree.sh ("SDLC_TMP_WORKTREES is unset"), the same denial the builder hit. Substitute: `git archive 07a5c289 plugins/sdlc-lite` extracted under the tmp prefix, `cmp` of its `codex_exchange.py` with `git show 07a5c289:...` (`basesame`), then the new `codex-selftest.py` copied in. Each of the three new tests then fails on a real assertion, not an import or attribute error. The first: `AssertionError: 0 != 2 : a report with a missing profile line must be refused:`. The second: `AssertionError: 0 != 2 : the live fingerprint is not the dispatched binding:`. The third: `AssertionError: None != 'native agent reported failure: could not finish: the fixture tool is missing'`. Each ran 1 test, `FAILED (failures=1)`. The export was removed afterwards. This is the same tree content the criterion asks for, reached by archive instead of the denied worktree form.
- #4 builder result quotes the pre-change failing output: pass. Evidence: builder-L3.md Notes quotes `FFF`, the three FAIL tracebacks, and `FAILED (failures=3)`. The messages match what I reproduced in #3.
- #5 (guard) five CodexTests: pass. Evidence: exit 0, `Ran 5 tests in 20.572s`, `OK`.
- #6 (guard) four test_solo_native_*: pass. Evidence: `Ran 4 tests in 9.641s`, `OK`.
- #7 (guard) three lifecycle tests: pass. Evidence: exit 0, `Ran 6 tests in 20.952s`, `OK`. It ran six although three were named, and all are green.
- #8 (guard) `solo_run.py selftest`: pass. Evidence: `solo_run selftest: PASS`.
- #9 (guard) scope: pass. Evidence: the negated pipeline exited 0 with SDLC_BASE_SHA=07a5c289. The only non-.sdlc changes are codex_exchange.py, codex-selftest.py, run.sh, solo_run.py (`git diff --stat`). `git diff --check` exited 0.

Behavior read in the diff, backed by the runs above. `_wait_for_agent` binds `codex_roles.fingerprint(agent)` after the alternate suffix. It checks the report with `check_loaded(..., payload['profile_fingerprint'])`. A `--failed` response skips the check and stores the first-line reason in `error`. `respond()` runs the check last. `run.sh` and `solo_run.py` add the keys only when `profile_fingerprint` is present. The tests drive a real waiter subprocess and the CLI, including the direct-response-file case and the fake-fingerprint-at-dispatch case.

The dependent `dispatch.py selftest` has a runs.jsonl key-parity case. It uses Claude fixtures and the new keys are optional, so it is unaffected: `dispatch selftest: PASS`.

Steelman: I drafted a fail on criterion 3 because the literal worktree command was not run. The builder's rebuttal holds: the hook denies it for roles with no SDLC_TMP_WORKTREES, and the archive of the base commit is byte-identical for `codex_exchange.py`. I dropped the finding.

## Out of scope changes
None.

## For the next attempt
None.

## Notes
- plugins/sdlc-lite/scripts/codex_exchange.py:56: `context ='\n'.join(...)` lost the space after `=`. Cosmetic.
- Criterion 3's `git worktree add` form is denied inside role sessions by block-stray-worktree.sh because the hook sees no SDLC_TMP_WORKTREES. A planner could phrase it as a `git archive` recipe.
