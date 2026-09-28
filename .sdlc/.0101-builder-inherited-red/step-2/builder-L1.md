<!-- role=builder level=L1 model=sonnet effort=low -->
## Status
done

## Changes
- plugins/sdlc-lite/scripts/run.sh: the builder `allowed` pattern is now `done|blocked|inherited red: .+`, and the header comment names the new value.
- plugins/sdlc-lite/scripts/run-selftest.sh: added `want_rc 0` for `inherited red: test_a` and `want_rc 3` for a bare `inherited red`.

## Checks
- Both `grep -q` acceptance criteria: pass.
- `bash plugins/sdlc-lite/scripts/run-selftest.sh`: "run selftest: PASS".
- `shellcheck --severity=warning` on run.sh and run-selftest.sh: exit 0.

## Notes
None
