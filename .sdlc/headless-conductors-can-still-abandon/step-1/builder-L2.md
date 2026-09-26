<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- plugins/sdlc-lite/hooks/block-background.sh: new Agent branch. In a headless session it denies with exit 2 unless `run_in_background` is exactly `false`, and the message includes `run_in_background: false`. The Bash logic is unchanged, and the header comment now names both Bash and Agent.
- plugins/sdlc-lite/hooks/hooks.json: added a second PreToolUse entry with matcher `Agent`, running only block-background.sh.
- plugins/sdlc-lite/scripts/hook-selftest.sh: added the 8 Agent/Bash `tool_name` cases and updated the header comment. The existing cases are unchanged.

## Checks
- Acceptance criteria 1 to 15 (the hook exit codes, the three jq queries on hooks.json, the grep for Agent fixtures, the selftest printing PASS, no `PreToolUse(Bash)` text, shellcheck --severity=warning): all passed. Each command was run as written from the worktree root.
- No em dashes found in the two edited scripts (grep exit 1).
- Mutation check: I copied the hook and selftest to a temp dir and changed the Agent condition to `== "true"`, so a missing field is allowed. The selftest printed `hook selftest: FAIL: agent role + absent: exit 0, want 2`. The temp dir was deleted and the tree was not touched.

## Notes
None
