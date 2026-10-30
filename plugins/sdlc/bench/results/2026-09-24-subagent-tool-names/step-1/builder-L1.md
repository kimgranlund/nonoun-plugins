<!-- role=builder level=L1 model=sonnet effort=low -->
## Status
done

## Changes
- `packages/agent-ui/devtools/src/timeline/events.ts`: added `SUBAGENT_TOOL_NAMES`, the `SubagentToolName` type and `isSubagentToolName` after `DevtoolsEventKind`, exactly as the handoff specified.

## Checks
- `grep -n "export const SUBAGENT_TOOL_NAMES\|export function isSubagentToolName" …/events.ts` showed both exports, at lines 38 and 42.
- `npx vitest run packages/agent-ui/devtools/src/timeline/events.test.ts` exited 0.
- `npx tsc` at the repo root exited 0.
- `git diff --stat` lists only `events.ts` (9 insertions).

## Notes
None
