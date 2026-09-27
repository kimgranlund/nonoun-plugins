<!-- role=builder level=L1 model=sonnet effort=low -->
All checks pass.

## Status
done

## Changes
- packages/agent-ui/devtools/src/timeline/events.ts: added `SUBAGENT_TOOL_NAMES`, `SubagentToolName`, `isSubagentToolName`
- packages/agent-ui/devtools/src/timeline/events.test.ts: imported new exports, added `describe('subagent tool names', ...)` block with 3 tests

## Checks
- 6 node --experimental-strip-types acceptance probes (isSubagentToolName Task/Agent/Bash, SUBAGENT_TOOL_NAMES membership, SubagentToolName type grep, barrel re-export): all exit 0
- grep for isSubagentToolName in test file: exit 0
- `npx vitest run packages/agent-ui/devtools/src/timeline/events.test.ts`: exit 0, 9 tests passed
- `npx tsc`: exit 0
- guard diff/untracked-files check: both halves exit 0 (only timeline dir changed, no stray files)

## Notes
None
