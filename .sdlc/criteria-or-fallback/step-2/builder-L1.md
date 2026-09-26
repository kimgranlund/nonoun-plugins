<!-- role=builder level=L1 model=sonnet effort=low -->
Both guards pass. Work is complete.

## Status
done

## Changes
plugins/sdlc-lite/agents/planner.md: added new rule 5 (ban `||` fallback joins) under Criteria that can pass, renumbered old rules 5-6 to 6-7
CLAUDE.md: added "or join two checks with `||` (an unquoted `||`, except after `test $# -eq 0`)" to the `scripts/steps.py` Layout bullet
.claude/agents/sdlc-lite-author.md: added the same `||` phrase to the plan-defect route bullet (line 18)

## Checks
`grep -qE '[|]{2}' plugins/sdlc-lite/agents/planner.md` — passed
`grep -q 'join two checks with' CLAUDE.md` — passed
`grep -q 'join two checks with' .claude/agents/sdlc-lite-author.md` — passed
`plugins/sdlc-lite/scripts/check.sh` — exit 0, all checks including `||` fallback lint tests pass
`python3 plugins/sdlc-lite/scripts/steps.py selftest` — PASS

## Notes
None
