<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- `plugins/sdlc-lite/hooks/block-role-spawn.sh`: new executable PreToolUse hook for Agent calls. In a conductor session it exits 2 on any `sdlc-lite:*` spawn, and on a plugin-qualified name holding a `builder`, `verifier`, `reviewer`, `planner` or `checker` token (split on `-` and `_`). The stderr message names the subagent and `run.sh`.
- `plugins/sdlc-lite/adapters/claude/hooks.json`: registered the hook as the second command in the existing `"matcher": "Agent"` entry, after `block-background.sh`.
- `plugins/sdlc-lite/scripts/hook-selftest.sh`: added the `rs` variable, a header-comment sentence, and all 12 fixtures from the handoff (6 exit 2, 6 exit 0), run through the `run` helper.
- `plugins/sdlc-lite/scripts/check.sh`: added `block-role-spawn.sh` to the hook list in the header comment.

## Checks
- `test -x plugins/sdlc-lite/hooks/block-role-spawn.sh`: pass.
- Conductor spawning `sdlc-lite:builder`: exit 2 (`test $? -eq 2` gave 0): pass.
- Same case, stderr piped to `grep -q run.sh`: pass.
- Conductor spawning `Explore`: exit 0, pass.
- No agent_type spawning `sdlc-lite:builder`: exit 0, pass.
- `jq -e` looking for `block-role-spawn.sh` under the Agent matcher: pass (it printed the command).
- Negative control (stub hook that always exits 0, then `! bash hook-selftest.sh`): pass. The selftest failed as intended with "role-spawn conductor + sdlc-lite:builder: exit 0, want 2".
- `grep -q block-role-spawn plugins/sdlc-lite/scripts/check.sh`: pass.
- (guard) `bash plugins/sdlc-lite/scripts/hook-selftest.sh`: printed "hook selftest: PASS", exit 0.
- `git diff --check`: clean.
- `shellcheck`: not run, because it is not installed on this host.

## Notes
- The full suite `check.sh` was not run; the handoff did not name it.
- shellcheck was not run on the new hook or the selftest, since it is not installed here.
