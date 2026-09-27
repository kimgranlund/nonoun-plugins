## Goal
Claude Code now calls its subagent tool either `Task` or `Agent`. Give devtools one shared way to recognise a subagent tool name that accepts both spellings. Export `SUBAGENT_TOOL_NAMES` and `isSubagentToolName` from the timeline events module.

## Context
- Code lives in packages/agent-ui/devtools/src/timeline/.
- The timeline events module is events.ts; its tests are events.test.ts alongside it.
- Follow the existing export and typing style in events.ts.

## Constraints
- Existing tests your change legitimately breaks may be updated to the new behavior; never delete a test or weaken an assertion to get green. The grader overwrites its own test files after the run, so edits to those do not count.
- The check must pass: vitest on events.test.ts, then a clean `npx tsc` at the repo root.

## Plan review
    steps: .sdlc/bench-subagent-tool-names/planner-L1.md step 1: acceptance criterion joins two checks with ||: node -e "$(cd /tmp/bench-subagent.5vv6 && npx tsx -e "import('./packages/agent-ui/devtools/src/timeline/events.ts').then(m => { if (!m.isSubagentToolName('Task') || !m.isSubagentToolName('Agent') || m.isSubagentToolName('Bash')) process.exit(1) })")"
      the fallback can pass on either side, so the criterion cannot fail: split it into separate criteria
    plan defect: replan this step (/chain 3)
