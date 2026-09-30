<!-- role=verifier level=L1 model=sonnet effort=medium -->
## Verdict
pass

## Criteria
- `test -x plugins/sdlc-lite/hooks/block-role-spawn.sh`: pass. Evidence: the test printed `exec`.
- Conductor spawning `sdlc-lite:builder` exits 2: pass. Evidence: I ran the criterion's input and got `rc=2`. The stderr was "conductor session: do not spawn 'sdlc-lite:builder' through the Agent tool; planner, builder, and verifier work runs through ${CLAUDE_PLUGIN_ROOT}/scripts/run.sh, never the Agent tool".
- The stderr contains `run.sh`: pass. Evidence: `2>&1 >/dev/null | grep -q run.sh` matched (`grepok`).
- Conductor spawning `Explore` exits 0: pass. Evidence: the run returned `rc=0`.
- No `agent_type` with `sdlc-lite:builder` exits 0: pass. Evidence: the run returned `rc=0`.
- `hooks.json` registers the hook: pass. Evidence: the `jq -e` command printed `"\"${CLAUDE_PLUGIN_ROOT}/hooks/block-role-spawn.sh\""`. The diff shows it as the second command in the existing Agent matcher, after block-background.sh.
- Negative control: pass. Evidence: with a stub hook that always exits 0, the selftest printed "FAIL: role-spawn conductor + sdlc-lite:builder: exit 0, want 2", and the `!` command exited 0.
  - I also swapped in a stub that always exits 2. The selftest failed that too, with "stderr lacks run.sh". The fixtures catch a hook that allows everything and one that denies everything.
- `grep -q block-role-spawn plugins/sdlc-lite/scripts/check.sh`: pass. Evidence: it printed `chk`. The diff adds the name to the header comment.
- (guard) `bash plugins/sdlc-lite/scripts/hook-selftest.sh`: pass. Evidence: it printed "hook selftest: PASS" with exit 0. I did not re-run it at the base SHA. The gate is green on the built tree and I saw its negative control fail, so an inherited-red check does not apply.

## Out of scope changes
None. `git status` shows changes only to these files:
- The new `block-role-spawn.sh`.
- `hooks.json`, `check.sh`, and `hook-selftest.sh`.
- `.sdlc/` artifacts.

I did not check the `.sdlc/0166-agent-spawn-hook/handoff.md` modification. It is task bookkeeping, not plugin behavior.

## For the next attempt
None
