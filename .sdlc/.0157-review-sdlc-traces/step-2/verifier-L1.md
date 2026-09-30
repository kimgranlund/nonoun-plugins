<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k attempts`: pass. Evidence: I ran it with `SDLC_BASE_SHA` set. Three `ok: attempts:` lines, `traces selftest: PASS`, rc=0.
- `... selftest -k attempts | grep -q '^ok: attempts: '`: pass. Evidence: rc=0. The check can go red. I mutated a copy of the script tree in a temp dir so the marker check always returned False. The selftest then printed `traces selftest: FAIL` on the marker case, and the other two cases still passed.
- `test -f plugins/sdlc-lite/scripts/traces/sources/attempts.py`: pass. Evidence: rc=0. `ls` shows `__init__.py` and `attempts.py` in `sources/`.
- (guard) scope: pass. Evidence: I ran the exact command with `SDLC_BASE_SHA` read from `step-2/base-sha`. rc=0.
- Do requirements checked by reading `attempts.py` and the three selftest cases:
  - `read(dir)` returns `(records, problems)`, sorted by file name, with `path` and `marker` added to each parsed dict.
  - The marker is True only when `<role>-<level>.running` exists. The fixture has that file for `verifier-L1` only.
  - The two non-object files (`[1, 2]` and `{not json`) are skipped and named in `problems`. The status case asserts this.
  - The four statuses come with exit codes 0, 1, 130 and None. The status case asserts them.
  - A record with no runs.jsonl row still yields a row through `table.join` with an empty run list. The join case asserts this.

## Out of scope changes
None. `git status` shows the code changes only in `traces.py`, `traces/`, and `.gitignore`, all allowed by the guard. The `.sdlc/` changes are artifacts.

## For the next attempt
None
