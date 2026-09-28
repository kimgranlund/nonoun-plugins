## Task goal
A confirmed root cause for why hooks/block-background.sh (T-0072) did not stop the builder L2 run in T-0103's reported incident, and whether the Agent guard shipped in T-0076 (or anything else) now closes that route.

## Step 4: block-background.sh denies Monitor in headless sessions
level: L2
### Do
In `plugins/sdlc-lite/hooks/block-background.sh`:
- When `tool_name` is `Monitor` and the session is headless (`SDLC_ROLE` set or `SDLC_HEADLESS=1`), deny with exit 2.
- The stderr message says to run gates and tests with foreground Bash (timeout 600000 or more) instead, and never end the turn while background work runs.
- Update the header comment.

In `plugins/sdlc-lite/hooks/hooks.json`, add a `PreToolUse` entry with `"matcher": "Monitor"` running only `block-background.sh`.

In `plugins/sdlc-lite/scripts/hook-selftest.sh`, add Monitor fixtures:
- `SDLC_ROLE=verifier`: exit 2, and stderr mentions foreground.
- `SDLC_HEADLESS=1`: exit 2.
- Neither set: exit 0.
- `SDLC_HEADLESS=0`: exit 0.

Update the selftest's header comment.
### Acceptance criteria
- `printf '%s' '{"tool_name":"Monitor","tool_input":{"command":"x"}}' | SDLC_ROLE=verifier plugins/sdlc-lite/hooks/block-background.sh 2>/dev/null; test $? -eq 2`
- `printf '%s' '{"tool_name":"Monitor","tool_input":{"command":"x"}}' | SDLC_HEADLESS=1 plugins/sdlc-lite/hooks/block-background.sh 2>/dev/null; test $? -eq 2`
- (guard) `printf '%s' '{"tool_name":"Monitor","tool_input":{"command":"x"}}' | env -u SDLC_ROLE -u SDLC_HEADLESS plugins/sdlc-lite/hooks/block-background.sh`
- `jq -e '[.hooks.PreToolUse[] | select(.matcher == "Monitor") | .hooks[].command | select(test("block-background"))] | length == 1' plugins/sdlc-lite/hooks/hooks.json`
- `grep -qF '"tool_name":"Monitor"' plugins/sdlc-lite/scripts/hook-selftest.sh && bash plugins/sdlc-lite/scripts/hook-selftest.sh`
- `shellcheck --severity=warning plugins/sdlc-lite/hooks/block-background.sh plugins/sdlc-lite/scripts/hook-selftest.sh`
