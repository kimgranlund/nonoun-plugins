<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- `python3 plugins/sdlc-lite/scripts/messages.py selftest`: pass. Evidence: the run printed "messages selftest: PASS" and exited 0. The two new cases are among the `ok:` lines: "refused: protocol value not the mailbox AGENTS.md" and "refused: follow_up_requested not true or false".
- `... selftest 2>&1 | grep -c 'ok: .*protocol' | grep -qv '^0$'`: pass. Evidence: the pipeline exited 0 (c2=0).
- `... selftest 2>&1 | grep -c 'ok: .*follow_up_requested' | grep -qv '^0$'`: pass. Evidence: the pipeline exited 0 (c3=0).
- (guard) the diff-scope check: pass. Evidence: the command exited 0 (guard=0). `git status` shows `plugins/sdlc-lite/scripts/messages.py` as the only changed file outside `.sdlc`.
- (guard) `bash plugins/sdlc-lite/scripts/check.sh`: pass. Evidence: exit 0 (rc=0). The output ended with "run selftest: PASS", "hook selftest: PASS" and "ok: plugin validate"; shellcheck was skipped because it is not installed. The red-at-base check was not needed because the gate is green on the built tree.
- Negative controls (the checks can go red): pass. Evidence: I ran these in a throwaway worktree at HEAD, copying the built `messages.py` in and breaking one production line at a time, then removed the worktree.
  - Replacing `if fields['protocol'] != PROTOCOL:` with `if False:` gave "FAIL: refused: protocol value not the mailbox AGENTS.md: 'read ...' exited 0, expected 1".
  - Replacing `if fields['follow_up_requested'] not in BOOLS:` with `if False:` gave "FAIL: refused: follow_up_requested not true or false: 'read ...' exited 0, expected 1".
  - So each new case goes red when its production check is removed.
- Do-clause content: pass. Evidence: the diff adds `case_bad_protocol` and `case_bad_follow_up`.
  - Both go through `st_bad_value`, which asserts that `read` is refused, the file stays in `new/`, and `read_time` is still empty.
  - `case_bad_follow_up` also asserts that `send --follow-up maybe` is refused and the count is unchanged.
  - The only change outside the cases is the optional `**values` override added to the `st_message` helper. No production check changed.
  - I did not mutate the `--follow-up` argument check. The `send` half is read from the diff only; it is not shown to go red.

## Out of scope changes
None. `st_message` gained a `**values` parameter, which the two new cases need.

## For the next attempt
None
