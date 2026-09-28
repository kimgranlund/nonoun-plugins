<!-- role=builder level=L1 model=sonnet effort=low -->
## Status
done

## Changes
- `CLAUDE.md`: added the `.nvmrc` behavior sentence to the `scripts/run.sh` Layout bullet.

## Checks
- `grep -F "run.sh" CLAUDE.md | grep -qF ".nvmrc"`: passed.
- `head -8 plugins/sdlc-lite/scripts/run-selftest.sh | grep -qiF nvmrc`: passed. It already passed before my edit.
- `bash plugins/sdlc-lite/scripts/check.sh`: exit 0, run twice (before and after the edit).

## Notes
- The header comment of `run-selftest.sh` already names the nvmrc cases, so I left it unchanged.
- The Commands bullet doesn't describe the run selftest's scope, so I left it unchanged too.
