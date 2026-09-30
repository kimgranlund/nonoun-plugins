<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
None. The existing uncommitted files already match the Do, so nothing was edited:
- `plugins/sdlc-lite/scripts/traces/sources/__init__.py` (present, checked)
- `plugins/sdlc-lite/scripts/traces/sources/attempts.py` (present, checked)
- `plugins/sdlc-lite/scripts/traces/selftest.py` (its three `attempts:` cases are present and were checked)

## Checks
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k attempts`: exit 0. All 3 `attempts:` cases print `ok`, then `traces selftest: PASS`.
- `... selftest -k attempts | grep -q '^ok: attempts: '`: exit 0.
- `test -f plugins/sdlc-lite/scripts/traces/sources/attempts.py`: exit 0.
- (guard) scope `test -z ...`: exit 0.

## Notes
Checked against the Do:
- **Return value:** `read(dir)` returns `(records, problems)`.
- **Order:** records are sorted by file name.
- **Record fields:** each record is the parsed dict plus `path` and `marker`. `marker` is True only when `<role>-<level>.running` exists next to the file. Role and level come from the record's fields, or from the file name if those are missing.
- **Bad files:** files that are not a JSON object (a JSON array, or JSON that does not parse) are skipped and listed in `problems`.
- **Status case:** the fixture has completed, failed, interrupted, and running records. The test checks each record's status and exit code, with None for the running one.
- **Join case:** feeds the records to `table.join` with no run rows and checks that each still yields a row.
- **Marker case:** only the running record, which has a `.running` file next to it, reports `marker` True.
