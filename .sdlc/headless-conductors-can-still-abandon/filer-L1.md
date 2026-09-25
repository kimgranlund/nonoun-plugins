<!-- role=filer level=L1 model=opus effort=low -->
## Warnings
None

## PR title
T-0076: Block background Agent calls in headless sessions

## PR body
### Summary
A headless sdlc-lite session (`SDLC_ROLE` set, or `SDLC_HEADLESS=1`) could launch a subagent through the Agent tool and then end its turn, which abandoned the work. `hooks/block-background.sh` only matched Bash. Agent runs in the background by default, so leaving out `run_in_background` was enough to trigger it. The guard now covers Agent. In a headless session, an Agent call is denied (exit 2) unless `run_in_background` is explicitly `false`. Interactive sessions behave as before, and so does Bash.

### Changes
Step 1 (hook, registration, selftest):
- `plugins/sdlc-lite/hooks/block-background.sh`: adds a branch on `tool_name == Agent`. It denies unless `run_in_background` is exactly JSON `false`, and the deny message includes `run_in_background: false`. The Bash logic is unchanged. The header comment now names both Bash and Agent.
- `plugins/sdlc-lite/hooks/hooks.json`: adds a second PreToolUse entry with matcher `Agent` that runs only `block-background.sh`. `block-publish.sh` stays Bash-only.
- `plugins/sdlc-lite/scripts/hook-selftest.sh`: adds 8 cases. With a role or `SDLC_HEADLESS=1` set, an absent field or `true` exits 2 and `false` exits 0. Interactive sessions and `SDLC_HEADLESS=0` exit 0. A Bash fixture with `tool_name` and no field exits 0. The existing cases are unchanged.

Step 2 (docs):
- Repo `CLAUDE.md` and `.claude/agents/sdlc-lite-author.md` now describe the hook as `PreToolUse(Bash, Agent)` and state the Agent rule. The same update went into `agents/conductor.md`, `skills/chain/SKILL.md`, `skills/bench/SKILL.md`, `skills/fanout/SKILL.md`, the `scripts/bench.sh` comment, and the `scripts/fanout.py` driver docstring.

### Verification
- Step 1 passed verifier L1. Every hook exit-code criterion was run and matched. The three `jq` checks on hooks.json passed. `hook-selftest.sh` printed `hook selftest: PASS`. shellcheck at warning severity was clean. No `PreToolUse(Bash)` text remains in either script. In the mutation check, a throwaway copy that allows a missing field made the selftest print `FAIL: agent role + absent: exit 0, want 2`.
- Step 2 passed verifier L1. Each per-file `grep ... | grep -q Agent` check passes on the tree and fails against HEAD. No em dashes were added. `bash plugins/sdlc-lite/scripts/check.sh` exited 0; the verifier ran it itself because the builder did not capture the exit code.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Changelog entry
- Headless sessions (`SDLC_ROLE` or `SDLC_HEADLESS=1`) now also block Agent calls unless `run_in_background` is explicitly `false`, because Agent runs in the background by default. Interactive sessions and Bash behavior are unchanged. (T-0076)

## Follow-ups
- Run a live probe to confirm that the running Claude Code version reports the subagent tool as `Agent`, not `Task`, in PreToolUse `tool_name` and matchers, and that `run_in_background: false` is accepted. If either fails, the new block-background.sh Agent guard never fires or blocks every headless Agent call.
