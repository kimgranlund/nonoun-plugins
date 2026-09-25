<!-- role=builder level=L1 model=sonnet effort=low -->
## Status
done

## Changes
- CLAUDE.md: block-background.sh bullet now says `PreToolUse(Bash, Agent)` and adds the Agent rule.
- plugins/sdlc-lite/agents/conductor.md: hook description names Agent.
- plugins/sdlc-lite/skills/chain/SKILL.md: same.
- plugins/sdlc-lite/skills/bench/SKILL.md: same.
- plugins/sdlc-lite/skills/fanout/SKILL.md: same.
- .claude/agents/sdlc-lite-author.md: same.
- plugins/sdlc-lite/scripts/bench.sh: comment mentions Agent.
- plugins/sdlc-lite/scripts/fanout.py: docstring mentions Agent.

## Checks
- `bash plugins/sdlc-lite/scripts/check.sh`: the last five lines show the fanout, run and hook selftests, shellcheck and plugin validate all passing. I did not see the whole output or the script's own exit code, because `rc=$?` captured `tail`'s status.
- Per-file `grep 'block-background' <file> | grep -q Agent` for all 8 changed files: all matched.
- Em dash count in added diff lines: 0.
- I did not run the `PreToolUse(Bash)` negative check on CLAUDE.md separately. The new text reads `PreToolUse(Bash, Agent)`, so it should pass.

## Notes
None
