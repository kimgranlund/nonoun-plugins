<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
None. Every gate was already green, so nothing needed fixing.

## Checks
- `bash plugins/sdlc-lite/scripts/check.sh`: exit 0. The fanout, run, hook, and live probe selftests all passed, and plugin validate is ok. Shellcheck was skipped because it is not installed.
- `python3 scripts/check-packaging.py`: exit 0, PASS.
- `python3 plugins/sdlc-lite/scripts/check.py plugins/sdlc-lite`: exit 0, "18 role levels, 8 agents checked".
- `python3 plugins/sdlc-lite/scripts/codex_roles.py generate --check`: exit 0, "Codex agent definitions verified".
- `git diff --check "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"`: exit 0, no output.

## Notes
The only uncommitted changes in the tree are the three files steps 1 and 2 changed, plus `.sdlc` artifacts. The generated Codex agents need no regeneration. Shellcheck is not installed, so `check.sh` did not run its shellcheck stage.
