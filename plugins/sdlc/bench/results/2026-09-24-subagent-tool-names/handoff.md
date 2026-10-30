## Goal
Claude Code now calls its subagent tool either `Task` or `Agent`. Give devtools one shared way to recognise a subagent tool name that accepts both spellings. Export `SUBAGENT_TOOL_NAMES` and `isSubagentToolName` from the timeline events module.

## Context
- Code lives in packages/agent-ui/devtools/src/timeline/.
- The timeline events module is events.ts; its tests are events.test.ts alongside it.
- Follow the existing export and typing style in events.ts.

## Constraints
- Do not edit test files.
- The check must pass: vitest on events.test.ts, then a clean `npx tsc` at the repo root.
