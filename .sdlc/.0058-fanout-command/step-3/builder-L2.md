<!-- role=builder level=L2 model=opus effort=low -->
## Status
done

## Changes
- plugins/sdlc-lite/skills/fanout/SKILL.md: new `/fanout` launcher skill with five steps: dry run, confirm, run, report, then an optional ff-only merge of main.
- plugins/sdlc-lite/agents/conductor.md: added the route line for parallel lanes to `/sdlc-lite:fanout`.
- plugins/sdlc-lite/scripts/check.py: added `skills/fanout/SKILL.md` to the long-run doc tuple and to docstring item 4.
- CLAUDE.md: added `/fanout` to the Workflow skills line, and a "Fan out lanes" entry under Commands.
- .claude/agents/sdlc-lite-author.md: added an invariant to keep fanout.py, the /fanout skill, board.py --lanes, the /board skill, and CLAUDE.md in sync. The long-run hazard now names four docs (chain, bench, fanout, conductor).

## Checks
- Criterion 1 (the skill file exists and has an argument-hint): pass
- Criterion 2 (check.py references the skill): pass
- Criterion 3 (in a temp copy with `run_in_background` removed from the skill, check.py reports the missing words): pass
- Criterion 4 (fanout appears in conductor.md, CLAUDE.md, and sdlc-lite-author.md): pass
- `bash plugins/sdlc-lite/scripts/check.sh`: exit 0; every selftest passed, plus shellcheck and plugin validate.

## Notes
The skill's `description` value is in quotes because it contains colons. The tree already had uncommitted changes from earlier steps (board.py, check.sh, the board skill, the task handoff). I did not touch them.
