<!-- role=planner level=L2 model=opus effort=medium -->
## Goal
Extend `hooks/block-background.sh` so that in headless sessions it also covers the Agent tool. Such a session is denied any Agent call unless `run_in_background` is explicitly false. Bash semantics, `block-publish.sh`, and interactive sessions stay unchanged, and every doc names Agent too.

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

## Step 2: Name Agent in every doc that describes block-background.sh
level: L1
### Do
Update each description of the guard so it says the hook covers both Bash and Agent in headless sessions. For Agent, it denies the call unless `run_in_background` is explicitly `false`, because Agent runs in the background by default and a missing field counts as background. Keep all other wording, and keep every word `scripts/check.py` requires (`interactive`, `run_in_background`, `notification`, `sleep`, `SDLC_HEADLESS`) in chain, bench, fanout, and conductor. No em dashes. Files to change:
- Repo-root `CLAUDE.md`, the `hooks/block-background.sh` Layout bullet. Change `PreToolUse(Bash) hook` to `PreToolUse(Bash, Agent) hook` or similar, and add the Agent rule. Leave the `block-publish.sh` bullet as it is.
- `plugins/sdlc-lite/agents/conductor.md`
- `plugins/sdlc-lite/skills/chain/SKILL.md`
- `plugins/sdlc-lite/skills/bench/SKILL.md`
- `plugins/sdlc-lite/skills/fanout/SKILL.md`
- `.claude/agents/sdlc-lite-author.md`, which mirrors CLAUDE.md.
- The comments in `plugins/sdlc-lite/scripts/bench.sh` (line 7) and `plugins/sdlc-lite/scripts/fanout.py` (the driver env docstring near line 36), where they say the hook denies `run_in_background`, so they mention Agent too.
### Acceptance criteria
- `grep 'hooks/block-background.sh' CLAUDE.md | grep -q Agent`
- `! grep 'hooks/block-background.sh' CLAUDE.md | grep -q 'PreToolUse(Bash)'`
- `grep 'block-background' plugins/sdlc-lite/agents/conductor.md | grep -q Agent`
- `grep 'block-background' plugins/sdlc-lite/skills/chain/SKILL.md | grep -q Agent`
- `grep 'block-background' plugins/sdlc-lite/skills/bench/SKILL.md | grep -q Agent`
- `grep 'block-background' plugins/sdlc-lite/skills/fanout/SKILL.md | grep -q Agent`
- `grep 'block-background' .claude/agents/sdlc-lite-author.md | grep -q Agent`
- `grep 'block-background' plugins/sdlc-lite/scripts/bench.sh | grep -q Agent`
- `grep 'block-background' plugins/sdlc-lite/scripts/fanout.py | grep -q Agent`
- (guard) `! git diff HEAD -- CLAUDE.md .claude/agents/sdlc-lite-author.md plugins/sdlc-lite/agents/conductor.md plugins/sdlc-lite/skills plugins/sdlc-lite/scripts/bench.sh plugins/sdlc-lite/scripts/fanout.py plugins/sdlc-lite/hooks plugins/sdlc-lite/scripts/hook-selftest.sh | grep '^+' | grep -q '—'`
- (guard) `bash plugins/sdlc-lite/scripts/check.sh` exits 0. It is green on the current tree.

## Risks
- Recent Claude Code versions name the subagent tool `Agent`; older ones named it `Task`. If the running version reports `Task` in the PreToolUse `tool_name` or matcher, the new guard never fires. This plan follows the handoff and covers `Agent` only. A live probe, like the one in ticket `confirm-with-a-live-claude` for Bash, would settle it.
- Denying an Agent call whose `run_in_background` field is missing assumes a headless model can re-issue the call with `run_in_background: false`. If a Claude Code version rejects that field, every headless Agent call would be blocked.
