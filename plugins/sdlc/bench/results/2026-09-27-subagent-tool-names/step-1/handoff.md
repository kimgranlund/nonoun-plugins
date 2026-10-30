## Task goal
Claude Code now calls its subagent tool either `Task` or `Agent`. Give devtools one shared way to recognise a subagent tool name that accepts both spellings. Export `SUBAGENT_TOOL_NAMES` and `isSubagentToolName` from the timeline events module.

## Step 1: Export SUBAGENT_TOOL_NAMES and isSubagentToolName from events.ts
level: L1
### Do
In `packages/agent-ui/devtools/src/timeline/events.ts`, directly after the `DEVTOOLS_EVENT_KINDS` / `DevtoolsEventKind` pair (lines 33 to 35), add, in that file's closed-vocabulary style (`as const` tuple, derived type, doc comment):

```ts
/** The subagent tool's name as Claude Code spells it: both `Task` (older) and `Agent` (current) are
 *  accepted. ONE shared recogniser for every devtools consumer, never a second list. */
export const SUBAGENT_TOOL_NAMES = ['Task', 'Agent'] as const
export type SubagentToolName = (typeof SUBAGENT_TOOL_NAMES)[number]

/** True iff `name` is one of `SUBAGENT_TOOL_NAMES` (exact, case-sensitive); narrows to `SubagentToolName`. */
export function isSubagentToolName(name: unknown): name is SubagentToolName {
  return (SUBAGENT_TOOL_NAMES as readonly unknown[]).includes(name)
}
```

Rules: membership goes through `SUBAGENT_TOOL_NAMES`, never a duplicated literal list. The parameter is `unknown` so a caller holding an untyped tool name from a parsed line can pass it without a cast, and the cast to `readonly unknown[]` is what lets `.includes` type-check against the tuple. No `enum`, no `Set` (the file's pattern is the readonly tuple, and consumers read it with `.includes`). Do not touch `packages/agent-ui/devtools/src/index.ts`: it already `export *`s `./timeline/events.ts`, so the barrel picks the new exports up.

In `packages/agent-ui/devtools/src/timeline/events.test.ts`, add a `describe('subagent tool names', ...)` block with three tests: `isSubagentToolName` is true for `'Task'` and `'Agent'`; false for `'Bash'`, `'task'`, `''`, and `undefined`; and `SUBAGENT_TOOL_NAMES` equals `['Task', 'Agent']`. Import the two new exports from `./events.ts` alongside the existing import. Do not delete or weaken any existing test.

Change nothing else. The behavior probes below load `events.ts` under `node --experimental-strip-types`, which works today because the module has zero DOM or I/O at module scope; keep it that way (no new value imports). Run the two gates and judge them by exit code, never by grepping output.

### Acceptance criteria
- `node --experimental-strip-types -e "import('./packages/agent-ui/devtools/src/timeline/events.ts').then(m => process.exit(m.isSubagentToolName('Task') ? 0 : 1))"` exits 0 (red now: `m.isSubagentToolName is not a function`).
- `node --experimental-strip-types -e "import('./packages/agent-ui/devtools/src/timeline/events.ts').then(m => process.exit(m.isSubagentToolName('Agent') ? 0 : 1))"` exits 0.
- `node --experimental-strip-types -e "import('./packages/agent-ui/devtools/src/timeline/events.ts').then(m => process.exit(m.isSubagentToolName('Bash') ? 1 : 0))"` exits 0 (the recogniser rejects a non-subagent tool name).
- `node --experimental-strip-types -e "import('./packages/agent-ui/devtools/src/timeline/events.ts').then(m => process.exit(m.SUBAGENT_TOOL_NAMES.includes('Task') && m.SUBAGENT_TOOL_NAMES.includes('Agent') ? 0 : 1))"` exits 0 (the exported list carries both spellings).
- `grep -qE '^export type SubagentToolName\b' packages/agent-ui/devtools/src/timeline/events.ts` exits 0.
- `node --experimental-strip-types -e "import('./packages/agent-ui/devtools/src/index.ts').then(m => process.exit(typeof m.isSubagentToolName === 'function' ? 0 : 1))"` exits 0 (the package barrel re-exports it; the barrel loads under Node today with 18 exports, so a red here means the export is missing, not a load failure).
- `grep -qE 'isSubagentToolName' packages/agent-ui/devtools/src/timeline/events.test.ts` exits 0 (the step's own tests exist).
- (guard) `npx vitest run packages/agent-ui/devtools/src/timeline/events.test.ts` exits 0 (green now, 6 tests; observed red with exit 1 in a worktree copy carrying a failing test).
- (guard) `npx tsc` exits 0 at the repo root (green now, about 90 s; observed red with exit 2 in a worktree copy carrying a type error in events.ts).
- (guard) `test -z "$(git diff --name-only "$SDLC_BASE_SHA" -- . ":(exclude).sdlc" ":(exclude).worktrees" ":(exclude)packages/agent-ui/devtools/src/timeline")" && test -z "$(git ls-files --others --exclude-standard -- . ":(exclude).sdlc" ":(exclude).worktrees")"` exits 0 (only the timeline dir changes and no new files appear; observed red on each half in a worktree copy with an edited README.md and a stray untracked file).
