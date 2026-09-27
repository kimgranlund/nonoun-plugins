<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- plugins/sdlc-lite/hooks/block-background.sh: when the session is headless, a Monitor call is denied with exit 2. The stderr message tells the model to use foreground Bash with the timeout at 600000 or more and to never end the turn while background work runs. The header comment is updated.
- plugins/sdlc-lite/hooks/hooks.json: new PreToolUse entry with `"matcher": "Monitor"` that runs only block-background.sh.
- plugins/sdlc-lite/scripts/hook-selftest.sh: four Monitor fixtures (SDLC_ROLE=verifier exits 2 and stderr mentions foreground; SDLC_HEADLESS=1 exits 2; neither set exits 0; SDLC_HEADLESS=0 exits 0). The header comment is updated.

## Checks
- Monitor JSON piped to the hook with SDLC_ROLE=verifier, then `test $? -eq 2`: exit 0 (pass)
- Monitor JSON piped to the hook with SDLC_HEADLESS=1, then `test $? -eq 2`: exit 0 (pass)
- (guard) Monitor JSON piped to the hook under `env -u SDLC_ROLE -u SDLC_HEADLESS`: exit 0 (pass)
- `jq -e` Monitor matcher count == 1 in hooks.json: printed `true`, exit 0 (pass)
- `grep -qF '"tool_name":"Monitor"' ... && bash plugins/sdlc-lite/scripts/hook-selftest.sh`: "hook selftest: PASS", exit 0 (pass)
- `shellcheck --severity=warning` on both files: exit 0 (pass)

## Notes
The tree already had uncommitted changes from earlier steps when this step started: `.sdlc/find-out-why-the-t/*`, fanout.py, run.sh, and run-selftest.sh. This step did not touch them.
