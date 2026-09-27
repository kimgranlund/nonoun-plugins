<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- plugins/sdlc-lite/scripts/run.sh: header comment on the Bash timeouts (T-0105); a `bash_timeout` helper keeps an inherited value only when it is a plain integer of at least 3600000 and otherwise uses 3600000; both values go on the `claude` launch line next to `SDLC_ROLE`.
- plugins/sdlc-lite/scripts/run-selftest.sh: the stub `claude` records `BASH_DEFAULT_TIMEOUT_MS` and `BASH_MAX_TIMEOUT_MS`; `want_to` asserts that unset gives 3600000, an inherited 120000 gives 3600000, and an inherited 7200000 stays 7200000; the header comment covers the new check.

## Checks
- `grep -q 'BASH_DEFAULT_TIMEOUT_MS' plugins/sdlc-lite/scripts/run.sh`: passes
- `grep -q 'BASH_MAX_TIMEOUT_MS' plugins/sdlc-lite/scripts/run.sh`: passes
- `grep -q '7200000' plugins/sdlc-lite/scripts/run-selftest.sh && grep -q 'BASH_DEFAULT_TIMEOUT_MS' plugins/sdlc-lite/scripts/run-selftest.sh && bash plugins/sdlc-lite/scripts/run-selftest.sh`: `run selftest: PASS`, exit 0
- `shellcheck --severity=warning plugins/sdlc-lite/scripts/run.sh plugins/sdlc-lite/scripts/run-selftest.sh`: exit 0, no findings

## Notes
The edits to both files were already in the tree when this run started, probably left by an earlier attempt at this step. I read them against the handoff, found they match the spec, and ran every criterion myself. Nothing is committed.
