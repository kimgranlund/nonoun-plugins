<!-- role=builder level=L1 model=sonnet effort=low -->
## Status
done

## Changes
plugins/sdlc-lite/agents/conductor.md: added sentence documenting block-publish.sh's SDLC_ROLE scope near the AskUserQuestion publish rule.
plugins/sdlc-lite/skills/file/SKILL.md: added the same fact at the publish/approval step.

## Checks
`git diff --stat` shows only the two intended files. Pass.
`grep -n $'\u2014' ...` (em dash check on both files): no match (exit 1). Pass.
`bash plugins/sdlc-lite/scripts/check.sh`: exit 0, "18 role levels, 8 agents checked", "selftest: PASS", "shellcheck ok", "plugin validate ok".

## Notes
None.
