<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout54/b/plugins/sdlc-lite/scripts/codex_exchange.py`: `_wait_for_agent` binds `profile_fingerprint` to the request and checks the report against that stored value. `respond()` runs the same check last. The final request and the result event carry `profile_fingerprint` and `profile_check`.
- `/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout54/b/plugins/sdlc-lite/scripts/run.sh`: the `runs.jsonl` jq expression adds both keys only when the result event has `profile_fingerprint`.
- `/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout54/b/plugins/sdlc-lite/scripts/solo_run.py`: `build_record` copies both keys from `result` only when present.
- `/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout54/b/plugins/sdlc-lite/scripts/codex-selftest.py`: three new tests with `native_waiter` and `native_respond` helpers. Existing normal responses now carry the request's profile line, and the two extended tests assert the request and the `runs.jsonl` line hold `codex_roles.fingerprint(<agent>)`.

## Checks
- `python3 /Users/kimgranlund/Projects/nonoun/sdlc-lite/plugins/sdlc-lite/scripts/redck.py record <handoff>`, before the first edit: exit 0, "recorded 2 pre-edit control(s) red".
- Criterion 1 command with only `codex-selftest.py` edited (exchange still at base): exit 1, `Ran 3 tests`, `FAILED (failures=3)`. Output is quoted in Notes.
- Criterion 1 after the change: exit 0, `Ran 3 tests in 2.116s`, `OK`.
- Criterion 2 (`grep -q profile_fingerprint` on the three files): exit 0.
- Criterion 3 was not run as written. `git worktree add --detach "$SDLC_TMP_WORKTREES/0507-base-check" "$SDLC_BASE_SHA"` was denied twice by `block-stray-worktree.sh`, once with the variable and once with the literal path: "Blocked for sdlc role 'conductor': SDLC_TMP_WORKTREES is unset, so this session has no throwaway worktree prefix".
- Criterion 3 substitute: `git archive 07a5c289eae8ce19db8ed716c2400c10841d9ac2 plugins/sdlc-lite | tar -x -C <tmp prefix>/0507-base-export`, then `cmp` of the exported `codex_exchange.py` against `git show <base>:plugins/sdlc-lite/scripts/codex_exchange.py` (equal), then `cp` of the new selftest into the export. Running `CodexTests.test_native_exchange_enforces_the_dispatched_profile_binding` there exited nonzero: `AssertionError: 0 != 2 : a report with a missing profile line must be refused:` at line 641, `Ran 1 test`, `FAILED (failures=1)`. It was a failed assertion on the missing case, with no import or attribute error.
- Guard 1 (five named `CodexTests`): exit 0, `Ran 5 tests in 18.996s`, `OK`.
- Guard 2 (four `test_solo_native_*`): exit 0, `Ran 4 tests in 5.954s`, `OK`.
- Guard 3 (`lifecycle-selftest.py` with three named tests): exit 0, printed `Ran 6 tests in 21.717s`, `OK`. It ran six tests although three were named.
- Guard 4 (`python3 plugins/sdlc-lite/scripts/solo_run.py selftest`): exit 0, `solo_run selftest: PASS`.
- Scope guard, with `SDLC_BASE_SHA` exported in the command: holds. Only the four target files differ outside `.sdlc`.
- `git diff --check`: exit 0.
- Cleanup: the export and the tmp prefix directory are removed, and `git worktree list` shows no 0507 entry.

## Notes
- Criterion 3 is met in intent on an equivalent base tree, not by the literal worktree command. The verifier will likely hit the same hook denial; the archive recipe in Checks reproduces the result.
- Hook observation for the planner: in this session a builder sub-agent cannot follow the brief's own `git worktree add --detach <prefix>/<name>` instruction. The hook resolved the role as `conductor` with no `SDLC_TMP_WORKTREES`, and exporting the variable inside the command does not reach the hook.
- Criterion 4, the output of the three new tests from the run made before `codex_exchange.py` changed:
```
FFF
======================================================================
FAIL: test_native_exchange_enforces_the_dispatched_profile_binding (__main__.CodexTests)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout54/b/plugins/sdlc-lite/scripts/codex-selftest.py", line 641, in test_native_exchange_enforces_the_dispatched_profile_binding
    self.assertEqual(done.returncode,2,f'a report with a {label} profile line must be refused: {done.stderr}')
AssertionError: 0 != 2 : a report with a missing profile line must be refused: 

======================================================================
FAIL: test_native_exchange_binding_survives_profile_change_after_dispatch (__main__.CodexTests)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout54/b/plugins/sdlc-lite/scripts/codex-selftest.py", line 679, in test_native_exchange_binding_survives_profile_change_after_dispatch
    self.assertEqual(done.returncode,2,'the live fingerprint is not the dispatched binding: '+done.stderr)
AssertionError: 0 != 2 : the live fingerprint is not the dispatched binding: 

======================================================================
FAIL: test_native_exchange_failed_response_needs_no_profile_line (__main__.CodexTests)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/kimgranlund/Projects/nonoun/sdlc-lite/.worktrees/fanout54/b/plugins/sdlc-lite/scripts/codex-selftest.py", line 703, in test_native_exchange_failed_response_needs_no_profile_line
    self.assertEqual(final.get('error'),'native agent reported failure: '+reason)
AssertionError: None != 'native agent reported failure: could not finish: the fixture tool is missing'

----------------------------------------------------------------------
Ran 3 tests in 1.548s

FAILED (failures=3)
```
- The handoff says a request with no binding raises `ValueError` "with the helper message", but `check_loaded` has no message for that case. `respond()` raises its own: `native request carries no profile fingerprint binding; start a new run`.
- An agent with no generated profile raises `ValueError('native agent <agent> has no generated profile to bind; run codex_roles.py generate and install')` before any request file is written.
- A direct response with `is_error` false and a blank report keeps its earlier behavior: status `failed`, `profile_check` `not-checked`, no `error` text.
- `dispatch.py` is outside this step's file set and was not touched, and its selftest was not run. If its parity cases compare `runs.jsonl` keys against `run.sh`, the land gate may need the same two optional keys there.
- Nothing is committed. The work is in the tree as uncommitted changes to the four files.
