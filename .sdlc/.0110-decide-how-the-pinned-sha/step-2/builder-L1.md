<!-- role=builder level=L1 model=sonnet effort=low -->
check.sh passes fully (exit 0). All acceptance criteria pass.

## Status
done

## Changes
- plugins/sdlc-lite/agents/planner.md: rule 6 now names the ancestry exemption
- CLAUDE.md: scripts/steps.py bullet parenthetical extended with the exemption
- .claude/agents/sdlc-lite-author.md: plan-defect route line notes the exemption

## Checks
- `grep '^6\. ' plugins/sdlc-lite/agents/planner.md | grep -q 'merge-base --is-ancestor'` → pass
- `grep -F 'scripts/steps.py' CLAUDE.md | grep -q 'is-ancestor'` → pass
- `grep -F 'pins a commit sha' .claude/agents/sdlc-lite-author.md | grep -q 'is-ancestor'` → pass
- `bash plugins/sdlc-lite/scripts/check.sh` → exit 0, all ok

## Notes
None
