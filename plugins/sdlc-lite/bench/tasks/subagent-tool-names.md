repo: /Users/kimba/Projects/nonoun/agent-ui
base: 0d49969de91af5f4158702a070c18c1da560b9a2
solution: 0e668ece21841919518efaf94e6119c699462c43
level: L1
tests_from: 0e668ece21841919518efaf94e6119c699462c43
test_paths:
  - packages/agent-ui/devtools/src/timeline/events.test.ts
setup: npm ci
check: npx vitest run packages/agent-ui/devtools/src/timeline/events.test.ts && npx tsc

## Goal
Claude Code now calls its subagent tool either `Task` or `Agent`. Give devtools one shared way to recognise a subagent tool name that accepts both spellings. Export `SUBAGENT_TOOL_NAMES` and `isSubagentToolName` from the timeline events module.

## Context
- Code lives in packages/agent-ui/devtools/src/timeline/.
- The timeline events module is events.ts; its tests are events.test.ts alongside it.
- Follow the existing export and typing style in events.ts.

## Constraints
- Existing tests your change legitimately breaks may be updated to the new behavior; never delete a test or weaken an assertion to get green. The grader overwrites its own test files after the run, so edits to those do not count.
- The check must pass: vitest on events.test.ts, then a clean `npx tsc` at the repo root.
