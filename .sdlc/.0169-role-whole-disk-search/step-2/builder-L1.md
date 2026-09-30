<!-- role=builder level=L1 model=sonnet effort=low -->
## Status
done

## Changes
None

## Checks
- `bash plugins/sdlc-lite/scripts/hook-selftest.sh`: exit 0, PASS
- `bash plugins/sdlc-lite/scripts/hook-live-probe.sh --selftest`: exit 0, PASS
- `python3 scripts/check-packaging.py`: exit 0, PASS
- `python3 plugins/sdlc-lite/scripts/check.py`: exit 0, ok (18 role levels, 8 agents)
- `bash plugins/sdlc-lite/scripts/check.sh`: exit 0. The tail shows the hook selftests passing, "skip: shellcheck not installed", and "ok: plugin validate".
- `git diff --check "$SDLC_BASE_SHA" -- . ":(exclude).sdlc"`: exit 0, no output (base 9d6ca64)

## Notes
My first attempt ran the commands through zsh word-splitting and failed with exit 127. I reran them through `bash -c` and all passed. The shellcheck step was skipped because the tool is not installed, so that part of `check.sh` is unverified.
