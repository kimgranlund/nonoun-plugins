<!-- role=builder level=L1 model=sonnet effort=low -->
## Status
done

## Changes
None

## Checks
- `bash plugins/sdlc-lite/scripts/check.sh`: all selftests PASS. shellcheck was skipped because it is not installed. The `rc=` line printed empty because of a shell quirk, so I did not capture the exit code. The output ends at "ok: plugin validate" with no failure lines.
- `python3 scripts/check-packaging.py`: PASS, rc=0.
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`: "Codex agent definitions verified", rc=0.
- `git diff --check`: clean, rc=0.

## Notes
None
