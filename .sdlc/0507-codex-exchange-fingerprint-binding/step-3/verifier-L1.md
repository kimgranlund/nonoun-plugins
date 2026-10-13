<!-- role=verifier level=L1 model=opus effort=medium -->
## Verdict
pass

## Criteria
- #1 `grep -qF "context = '" plugins/sdlc-lite/scripts/codex_exchange.py && ! grep -qF "context ='" plugins/sdlc-lite/scripts/codex_exchange.py`: pass. Evidence: ran the command in the tree, exit 0. `grep -nF "context = '"` prints one hit, `/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout54/b/plugins/sdlc-lite/scripts/codex_exchange.py:56` (`    context = '\n'.join(f'{key}=...`); `grep -nF "context ='"` prints nothing. The path exists, so the negated grep is not vacuous. Red control: a temp copy of the file with line 56 reverted to `context ='\n'.join(` (the only differing line per `diff`) makes the same command exit 1; the biting conjunct there is the first grep, and the second also matches. `python3 -m py_compile` on the file exits 0. The builder's claim was checked by these runs, not taken from its report.
- #2 (guard) `python3 plugins/sdlc-lite/scripts/codex-selftest.py CodexTests.test_native_exchange_enforces_the_dispatched_profile_binding CodexTests.test_native_exchange_binding_survives_profile_change_after_dispatch CodexTests.test_native_exchange_failed_response_needs_no_profile_line CodexTests.test_native_exchange_preserves_runner_artifacts`: pass. Evidence: ran it in the tree with `-v`, all four named tests `ok`, `Ran 4 tests in 3.744s`, `OK`, exit 0. Green, so no pre-build run at the base sha was needed (rule 4 applies only before failing a gate).

## Out of scope changes
None. The working tree carries the uncommitted changes of steps 1 and 2 as well, so the diff against 07a5c289 is wider than this step. Check that isolates step 3: `find plugins docs scripts -newer .sdlc/0507-codex-exchange-fingerprint-binding/step-3/handoff.md -type f` lists only `plugins/sdlc-lite/scripts/codex_exchange.py`, and on line 56 of the diff against the base sha that line is unchanged context, which matches "restore the space, change nothing else". `git diff --check` on the file exits 0. No shared contract changed (whitespace only), so no dependents to trace.

## For the next attempt
None
