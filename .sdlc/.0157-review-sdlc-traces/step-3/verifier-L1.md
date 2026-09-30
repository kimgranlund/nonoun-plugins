<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k runs`: pass. Evidence: I ran it and got two `ok: runs:` lines, then `traces selftest: PASS`, exit 0.
- `... selftest -k runs | grep -q '^ok: runs: '`: pass. Evidence: exit 0. The check can go red: in a throwaway worktree at `$SDLC_BASE_SHA`, where `traces.py` does not exist, the same command exited 1.
- `test -f plugins/sdlc-lite/scripts/traces/sources/runs.py`: pass. Evidence: exit 0.
- `grep -q 'order.records' plugins/sdlc-lite/scripts/traces/sources/runs.py`: pass. Evidence: exit 0. The call `for i, rec in order.records(dir)` is in `read`.
- (guard) scope: pass. Evidence: the scope command exited 0 with `SDLC_BASE_SHA=7334f49...`.
- Behavior in the Do, which I read in `runs.py` and in the selftest cases at `selftest.py:289-327`. The run above exercised these and they passed:
  - One fixture has a legacy row, a `{not json` line and a full row. It reads as two records, `skipped == 1`, and indexes 0 and 2.
  - The legacy row defaults to `None` for the scalar fields and `[]` for the stray lists.
  - The full row equals the expected dict exactly, and the extra key is dropped.
  - A missing `runs.jsonl` and a missing dir both give `([], 0)`.

## Out of scope changes
None. Every changed or new file under the repo root (`traces.py`, `traces/`, `.gitignore`) is on the scope guard's allowlist. The `.gitignore` change was already in the tree before this step, as the builder noted. The scope guard passed, which shows that.

## For the next attempt
None
