<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
None. All gates were already green, so nothing needed fixing.

## Checks
- `bash plugins/sdlc-lite/scripts/check.sh`: exit 0. Its last lines were run selftest PASS, hook selftest PASS, hook live probe selftest PASS, and `ok: plugin validate`.
- `python3 scripts/check-packaging.py`: exit 0.
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`: exit 0 ("Codex agent definitions verified").
- `git diff --check`: exit 0.
- Em dash guard on `git diff $SDLC_BASE_SHA` (bc21b53): passed. A grep of the untracked files also found no U+2014.
- Scope criterion (changed files limited to the allowed list, untracked files limited to `docs/validation/messages-wait-live-run*`): passed.

## Notes
check.sh printed "skip: shellcheck not installed", so the shellcheck step inside it did not run.
