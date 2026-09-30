<!-- role=builder level=L3 model=opus effort=high -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/traces.py`: new thin entry. It puts its own folder at the front of `sys.path` and calls `traces.cli.main(sys.argv[1:])`.
- `plugins/sdlc-lite/scripts/traces/__init__.py`: new package marker with a docstring.
- `plugins/sdlc-lite/scripts/traces/table.py`: new. Holds `ROW_FIELDS` in the specified order, `join(dir_rel, attempts, runs, results, ticket=None)`, and the helpers `dir_parts` and `name_parts`. `name_parts` uses `order.RESULT` rather than a new name regex.
- `plugins/sdlc-lite/scripts/traces/selftest.py`: new. Case registry (`case` decorator, `Skip` exception, `run(family=None)`) and the five `join:` cases.
- `plugins/sdlc-lite/scripts/traces/cli.py`: new. `main(argv)` with only `selftest [-k FAMILY]`. An unknown subcommand, or no subcommand, prints usage and exits 2.
- `.gitignore`: added the `__pycache__/` line.

## Checks
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k join`: exit 0, 5 `ok: join: ...` lines, then `traces selftest: PASS`.
- `... selftest -k join | grep -q '^ok: join: '`: exit 0.
- `... selftest -k nonesuch 2>&1 | grep -q 'no selftest case matches'`: exit 0.
- `... selftest -k nonesuch 2>/dev/null; test $? -eq 1`: exit 0.
- `test -f plugins/sdlc-lite/scripts/traces/__init__.py`: exit 0.
- The `python3 -c "... import traces.table as t; assert list(t.ROW_FIELDS) == [...]"` criterion: exit 0.
- `grep -qxF '__pycache__/' .gitignore`: exit 0.
- (guard) scope command exactly as written, with `$SDLC_BASE_SHA`=7334f490 (the same as HEAD): exit 0.
- `traces.py bogus` and `traces.py` with no arguments: both print usage and exit 2.
- `traces.py selftest` (all cases): PASS, exit 0.
- Negative control: I monkeypatched `table.name_parts` so it always returns k=1 and no role, then ran `selftest.run('join')`. It returned 1 with 3 cases missed: orphan, fields, and names. The join cases do catch a broken name parse.
- `git diff --check`, including the new files through intent-to-add, which I then reset: clean.

## Notes
- Choices the handoff left open:
  - A result record that matches no row creates no row.
  - Row order is attempt rows in input order, then orphan run rows in `runs.jsonl` index order.
  - When several run records join the same attempt, the last one in index order wins.
  - A run record whose `attempt_id` matches no attempt becomes an orphan legacy row, even if it has a `file`.
- The row fields `tool_calls`, `denials` and `rate_limits` are copied from the first record that has them, checked in the order run, attempt, result. For now they are None unless a later reader adds those keys.
- `sources` uses each record's `path` when present. When there is none, it falls back to `<dir_rel>/<name>.attempt.json`, `<dir_rel>/runs.jsonl` or `<dir_rel>/<name>.md`.
- `task_dir` is the parent of a `step-<n>` dir, or `dir_rel` itself for a task-level dir.
- `attempt_k` is None when the name does not match `<role>-L<n>(-<k>)`.
- `secs` accepts ISO stamps ending in `Z` or `+00:00`.
- I removed the `__pycache__` the runs created; it is ignored either way.
