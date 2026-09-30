<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/traces/sources/runs.py`: new file. `read(dir)` returns `(records, skipped)`. Records come from `order.records(dir)` in file order. Each one keeps the 14 listed fields: the two stray lists default to `[]` and every other field defaults to `None`. Each also carries `index` and `path`, where `path` is `os.path.join(dir, 'runs.jsonl')`. `skipped` is the file's line count minus the number of good records. A missing `runs.jsonl` gives `([], 0)`.
- `plugins/sdlc-lite/scripts/traces/selftest.py`: adds a `runs` family with two cases.
  - The first writes a legacy row (no `attempt_id`, no `file`), a `{not json` line, and a row with both fields. It checks that this reads as two records and one skipped line, with the defaults and exact fields right and extra keys dropped.
  - The second checks that a missing `runs.jsonl` and a missing dir both read as no records.

## Checks
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k runs`: 2 ok, PASS, exit 0.
- `... selftest -k runs | grep -q '^ok: runs: '`: exit 0.
- `test -f plugins/sdlc-lite/scripts/traces/sources/runs.py`: exit 0.
- `grep -q 'order.records' .../runs.py`: exit 0.
- `python3 plugins/sdlc-lite/scripts/traces.py selftest` (all families): exit 0.
- Scope guard, with `SDLC_BASE_SHA=7334f49...`: exit 0.

## Notes
- `read` returns a `(records, skipped)` tuple, the same shape as `attempts.read`'s `(records, problems)`.
- Blank lines also count toward `skipped`, because `order.records` drops them too.
- The existing `.gitignore` change was already in the tree before this step; I did not touch it.
