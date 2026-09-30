<!-- role=verifier level=L2 model=sonnet effort=high -->
## Verdict
pass

## Criteria
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k findings`: pass. Evidence: exit 0, three `ok: findings: ...` lines (same-three rewrite, stale marking, clusters top 2), then `traces selftest: PASS`.
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k findings | grep -q '^ok: findings: '`: pass. Evidence: rc=0.
- `test -f plugins/sdlc-lite/scripts/traces/findings.py`: pass. Evidence: rc=0. The file exists and defines `make`, `finding_id`, `load`, `write` and `clusters`.
- (guard) scope: pass. Evidence: the handoff command returned rc=0. It is not a pre-build gate, because it checks scope rather than a suite. It can go red: an out-of-scope path such as `.sdlc/...` is excluded and anything else would show up in the grep. I did not run it red.
- Behavior beyond the selftest, read from `findings.py` and probed directly:
  - The id is 12 hex characters. It stays equal when the evidence order, summary and severity form (`'high'` vs `3`) differ.
  - `cause_hint` comes back as `{file, rule}`.
  - Writing the same finding at two different times keeps `first_seen` at the earlier time and moves `last_seen` to the later one.
  - A finding missing from a later run comes back with `stale` True.
  - `clusters` skips stale findings, and it returned `[]` when the only finding was stale.
- The selftest can go red. I ran a negative control on a full copy of `scripts/` under `$SDLC_TMP_WORKTREES`: changing `if d.get('stale'):` to `if False:` in `clusters` turned the clusters case FAIL. The biting variable is stale findings leaking into the clusters, and the ranking is off in the output. The unmodified copy passed, and the copy was removed afterwards. My first control attempt failed for an unrelated reason (`order.py` was missing from the copy), so I redid it with the whole `scripts/` directory.

## Out of scope changes
- `.gitignore` gains `__pycache__/`. The handoff's scope guard allows it, and it is a harmless one-line ignore for the new package. I read the diff.
- `selftest.py` and `__init__.py` also changed. Both sit under `scripts/traces/`, which the guard allows. The selftest edit is the `findings` case registration the Do asks for, and `__init__.py` only adds `findings` to the docstring module list.
- Nothing else is outside scope. `git diff --stat` shows only `.gitignore` and the `.sdlc` handoff among tracked files.

## For the next attempt
None
