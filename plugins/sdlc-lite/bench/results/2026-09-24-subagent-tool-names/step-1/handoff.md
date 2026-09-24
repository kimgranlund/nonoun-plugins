## Task goal
Claude Code now calls its subagent tool either `Task` or `Agent`. Give devtools one shared way to recognise a subagent tool name that accepts both spellings. Export `SUBAGENT_TOOL_NAMES` and `isSubagentToolName` from the timeline events module.

## Step 1: Add subagent tool-name constant and guard
level: L1
### Do
In `packages/agent-ui/devtools/src/timeline/events.ts`, add the following after the `DevtoolsEventKind` type (line 35). This copies the file's existing `DEVTOOLS_EVENT_KINDS` pattern: an `as const` array plus a derived literal-union type.

```ts
/** Tool names Claude Code uses for its subagent tool: `Task` (older) and `Agent` (current). */
export const SUBAGENT_TOOL_NAMES = ['Task', 'Agent'] as const
export type SubagentToolName = (typeof SUBAGENT_TOOL_NAMES)[number]

/** True when `name` is one of the accepted subagent tool spellings. */
export function isSubagentToolName(name: string): name is SubagentToolName {
  return (SUBAGENT_TOOL_NAMES as readonly string[]).includes(name)
}
```

Do not edit any test file. A grep of `devtools/src` found no existing uses of these names, so nothing else needs to change.

### Acceptance criteria
- `grep -n "export const SUBAGENT_TOOL_NAMES\|export function isSubagentToolName" packages/agent-ui/devtools/src/timeline/events.ts` shows both exports.
- `npx vitest run packages/agent-ui/devtools/src/timeline/events.test.ts` exits 0.
- `npx tsc` at the repo root exits 0 with no errors.
- `git diff --stat` lists only `events.ts`.

