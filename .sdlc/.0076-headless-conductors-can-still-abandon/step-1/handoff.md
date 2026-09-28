## Task goal
A headless sdlc-lite session (SDLC_ROLE set, or SDLC_HEADLESS=1) cannot launch a background subagent through the Agent tool and then end its turn, abandoning the work; interactive sessions are unaffected.

## Step 1: Guard the Agent tool in block-background.sh, hooks.json, and the hook selftest
level: L2
### Do
- `plugins/sdlc-lite/hooks/block-background.sh`: keep the early `exit 0` for interactive sessions (no `SDLC_ROLE` and `SDLC_HEADLESS` not `1`). Read `.tool_name` with jq.
  - When it is `Agent`, deny with exit 2 unless `.tool_input.run_in_background` is exactly JSON `false`. A missing field counts as a denial because Agent runs in the background by default. The stderr message must contain the literal text `run_in_background: false` and tell the model to pass that, wait for the subagent's result in the same turn, and never end the turn while it runs, because ending the turn ends the session and abandons the work.
  - Any other or missing `tool_name` keeps today's Bash logic byte for byte: deny only on `run_in_background == true`, with the existing message that contains `foreground` and `600000`. The existing selftest fixtures have no `tool_name` and must keep passing.
  - Change the header comment from `PreToolUse(Bash) hook` to name both Bash and Agent.
  - No em dashes.
- `plugins/sdlc-lite/hooks/hooks.json`: add a second `PreToolUse` entry with matcher `Agent` whose only hook is `block-background.sh` (same command string). Leave the Bash entry, with both hooks, as it is. Do not register `block-publish.sh` for Agent.
- `plugins/sdlc-lite/scripts/hook-selftest.sh`: add Agent fixtures that include `"tool_name":"Agent"`, with these cases:
  - `SDLC_ROLE=conductor` with the field absent: exit 2, and stderr contains `run_in_background: false`.
  - `SDLC_HEADLESS=1` with the field absent: exit 2.
  - Role with `true`: exit 2.
  - Role with `false`: exit 0.
  - Interactive (neither set) with the field absent: exit 0.
  - Interactive with `true`: exit 0.
  - `SDLC_HEADLESS=0` with the field absent: exit 0.
  - A `"tool_name":"Bash"` fixture with the field absent under a role: exit 0.

  Keep every existing case unchanged. Change the header comment so it no longer says `PreToolUse(Bash) hooks` only.
### Acceptance criteria
- `printf '%s' '{"tool_name":"Agent","tool_input":{"prompt":"x"}}' | env -u SDLC_HEADLESS SDLC_ROLE=conductor plugins/sdlc-lite/hooks/block-background.sh 2>/dev/null; test $? -eq 2`
- `printf '%s' '{"tool_name":"Agent","tool_input":{"prompt":"x"}}' | env -u SDLC_ROLE SDLC_HEADLESS=1 plugins/sdlc-lite/hooks/block-background.sh 2>/dev/null; test $? -eq 2`
- `out=$(printf '%s' '{"tool_name":"Agent","tool_input":{"prompt":"x","run_in_background":true}}' | env -u SDLC_HEADLESS SDLC_ROLE=conductor plugins/sdlc-lite/hooks/block-background.sh 2>&1); test $? -eq 2 && grep -q 'run_in_background: false' <<<"$out"`
- (guard) `printf '%s' '{"tool_name":"Agent","tool_input":{"prompt":"x","run_in_background":false}}' | env -u SDLC_HEADLESS SDLC_ROLE=conductor plugins/sdlc-lite/hooks/block-background.sh`
- (guard) `printf '%s' '{"tool_name":"Agent","tool_input":{"prompt":"x"}}' | env -u SDLC_ROLE -u SDLC_HEADLESS plugins/sdlc-lite/hooks/block-background.sh`
- (guard) `printf '%s' '{"tool_name":"Agent","tool_input":{"prompt":"x","run_in_background":true}}' | env -u SDLC_ROLE -u SDLC_HEADLESS plugins/sdlc-lite/hooks/block-background.sh`
- (guard) `printf '%s' '{"tool_name":"Bash","tool_input":{"command":"sleep 1"}}' | env -u SDLC_HEADLESS SDLC_ROLE=builder plugins/sdlc-lite/hooks/block-background.sh`
- (guard) `out=$(printf '%s' '{"tool_name":"Bash","tool_input":{"command":"sleep 1","run_in_background":true}}' | env -u SDLC_HEADLESS SDLC_ROLE=builder plugins/sdlc-lite/hooks/block-background.sh 2>&1); test $? -eq 2 && grep -q 600000 <<<"$out"`
- `jq -e '[.hooks.PreToolUse[] | select(.matcher | split("|") | index("Agent")) | .hooks[].command | select(test("block-background"))] | length == 1' plugins/sdlc-lite/hooks/hooks.json`
- (guard) `jq -e '[.hooks.PreToolUse[] | select(.matcher | split("|") | index("Agent")) | .hooks[].command | select(test("block-publish"))] | length == 0' plugins/sdlc-lite/hooks/hooks.json`
- (guard) `jq -e '[.hooks.PreToolUse[] | select(.matcher | split("|") | index("Bash")) | .hooks[].command] | map(select(test("block-publish|block-background"))) | length == 2' plugins/sdlc-lite/hooks/hooks.json`
- `grep -q '"tool_name":"Agent"' plugins/sdlc-lite/scripts/hook-selftest.sh`
- (guard) `bash plugins/sdlc-lite/scripts/hook-selftest.sh | grep -qx 'hook selftest: PASS'`
- `! grep -n 'PreToolUse(Bash)' plugins/sdlc-lite/hooks/block-background.sh plugins/sdlc-lite/scripts/hook-selftest.sh`
- (guard) `shellcheck --severity=warning plugins/sdlc-lite/hooks/block-background.sh plugins/sdlc-lite/scripts/hook-selftest.sh`
- Mutation check the verifier observes: in a throwaway copy of the hook, make the Agent branch treat a missing field as allowed. Run `hook-selftest.sh` against it by editing its `hooks=` path in the copy. The run must print `FAIL`. Never edit the tree.
