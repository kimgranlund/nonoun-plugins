<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/scripts/traces/sources/results.py`: new file. `read(dir)` returns `(records, problems)`: one record per `<role>-L<n>(-<k>).md` result file in `dir`.
- `plugins/sdlc-lite/scripts/traces/selftest.py`: added two `results` cases.

## Checks
- `python3 plugins/sdlc-lite/scripts/traces.py selftest -k results`: PASS, 2 ok lines.
- `... selftest -k results | grep -q '^ok: results: '`: exit 0.
- grep criterion (uses the three helpers, no `## Status` or `## Verdict` text in results.py): exit 0.
- (guard) scope: exit 0.
- `python3 plugins/sdlc-lite/scripts/traces.py selftest` (all families): PASS.

## Notes
- Result files are picked by `order.RESULT`, so a stray file like `notes.md` is skipped.
- `steps` and `order` are imported from the scripts dir, which `traces.py` puts on sys.path.
- Changes spans use `steps.SPAN_RE`, trimmed with `.strip()`.
- `status` is None for non-builders and `verdict` is None for non-verifiers.
- The selftest builds heading strings with a helper (`'#' * 2`) only in selftest.py. results.py never contains those heading strings.
- In the next_action case, the builder "done" fixture with no verifier gives `verify`. The handoff did not name an expected action for that case.
