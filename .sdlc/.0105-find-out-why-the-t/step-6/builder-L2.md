<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- CLAUDE.md: the block-background line is now `PreToolUse(Bash, Agent, Monitor)` and says Monitor is denied headless, with the Monitor fixtures named. The run.sh Layout line covers the `BASH_DEFAULT_TIMEOUT_MS`/`BASH_MAX_TIMEOUT_MS` 3600000 floor, the `stream-json` log, and the result pick (required heading, else not `task-notification`, else last). The Commands check.sh line names the new hook and run selftest coverage.
- .claude/agents/sdlc-lite-author.md: the headless-foreground hazard now names Monitor and says run.sh and fanout also raise the timeouts.
- plugins/sdlc-lite/agents/conductor.md: says bench.sh, run.sh, and fanout raise the timeouts, and that every Monitor call is denied.
- plugins/sdlc-lite/skills/handoff-format/SKILL.md: says the `.log` is a stream-json transcript.
- plugins/sdlc-lite/scripts/check.sh: header comment updated to cover the Monitor fixtures and the run selftest.
- plugins/sdlc-lite/skills/chain/SKILL.md: the block-background list now includes Monitor. fix/SKILL.md does not list what block-background denies, so it was not changed.

## Checks
- All 6 grep criteria: ok.
- `bash plugins/sdlc-lite/scripts/check.sh`: exit 0. The steps, order, fanout, run, hook, and live-probe selftests all passed, and so did shellcheck and plugin validate.

## Notes
None
