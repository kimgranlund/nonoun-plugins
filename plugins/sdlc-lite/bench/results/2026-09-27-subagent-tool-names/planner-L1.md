<!-- role=planner level=L1 model=sonnet effort=medium -->
Good, both guards are green now. This is a small, single-file, mechanical change with a fully given spec — L1 fits well. Now producing the plan.

## Goal
Add a shared `SUBAGENT_TOOL_NAMES` set and `isSubagentToolName` guard to the devtools timeline events module so callers can recognize either `Task` or `Agent` as the subagent tool name.

## Step 1: Export SUBAGENT_TOOL_NAMES and isSubagentToolName from events.ts
level: L1
### Do
In `packages/agent-ui/devtools/src/timeline/events.ts`, add, near the existing `DEVTOOLS_EVENT_KINDS` closed-vocabulary pattern (same `as const` + derived-type + type-guard style already used in this file):
- `export const SUBAGENT_TOOL_NAMES = ['Task', 'Agent'] as const` (or equivalent tuple naming both spellings), with a one-line doc comment stating both are accepted subagent tool names.
- `export type SubagentToolName = (typeof SUBAGENT_TOOL_NAMES)[number]` if a derived type is useful for consistency with `DevtoolsEventKind`, otherwise skip if unused.
- `export function isSubagentToolName(name: string): boolean` (or narrowing to `SubagentToolName`) that returns true iff `name` is `'Task'` or `'Agent'`, implemented via membership over `SUBAGENT_TOOL_NAMES` (never a hardcoded duplicate list) so the two stay in sync.

Do not touch `events.test.ts` — the grader supplies its own tests for this behavior.

### Acceptance criteria
- (guard) `cd /tmp/bench-subagent.5vv6 && npx vitest run packages/agent-ui/devtools/src/timeline/events.test.ts` exits 0 (currently green: 6 passed, must stay green).
- `grep -n "export const SUBAGENT_TOOL_NAMES" packages/agent-ui/devtools/src/timeline/events.ts` finds the export.
- `grep -n "export function isSubagentToolName\|export const isSubagentToolName" packages/agent-ui/devtools/src/timeline/events.ts` finds the export.
- A short inline probe confirms behavior: `node -e "$(cd /tmp/bench-subagent.5vv6 && npx tsx -e "import('./packages/agent-ui/devtools/src/timeline/events.ts').then(m => { if (!m.isSubagentToolName('Task') || !m.isSubagentToolName('Agent') || m.isSubagentToolName('Bash')) process.exit(1) })")"` — this is red now (function doesn't exist) and must go green after the Do. (Run via whatever module loader the repo's vitest config already uses, e.g. a one-off vitest test snippet or `npx tsx`, since this is plain TS with `.ts` extension imports.)
- (guard) `cd /tmp/bench-subagent.5vv6 && npx tsc` exits 0.

## Risks
None — single file, fully specified export shape, no cross-module edges to update, existing tests already green and the file's own conventions (as-const closed vocabulary + derived type) directly fit the ask.
