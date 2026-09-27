<!-- role=builder level=L1 model=sonnet effort=low -->
All checks pass.

## Status
done

## Changes
plugins/sdlc-lite/scripts/fanout.py: added two lines to the selftest STUB driver checking BASH_DEFAULT_TIMEOUT_MS and BASH_MAX_TIMEOUT_MS are 3600000

## Checks
- `grep -qF 'BASH_DEFAULT_TIMEOUT_MS:-' plugins/sdlc-lite/scripts/fanout.py`: PASS
- `grep -qF 'BASH_MAX_TIMEOUT_MS:-' plugins/sdlc-lite/scripts/fanout.py`: PASS
- (guard) `python3 plugins/sdlc-lite/scripts/fanout.py selftest`: PASS ("fanout selftest: PASS")

## Notes
None
