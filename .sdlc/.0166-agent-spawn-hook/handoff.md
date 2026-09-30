---
id: T-0166
title: "Warn when the conductor spawns another plugin's role agent"
type: feature        # feature | bug | chore | spike | idea
status: done        # proposed | ready | blocked | done | dropped (build progress lives in /board)
size: M              # S | M | L | XL
priority: P2         # P1 | P2 | P3
depends: []          # ticket ids, e.g. [T-0002]
created: 2026-09-29
---

## Goal
When the SDLC Lite conductor is in force, an Agent-tool spawn of another plugin's builder, verifier, or planner agent is flagged before it runs, with a message pointing at `run.sh`.

## Intent
- Do: a Claude Code `PreToolUse` hook on the Agent tool that warns or denies when the session runs as `sdlc-lite:conductor` and the spawn names a builder, verifier, reviewer, or planner agent from another plugin, or an SDLC Lite role agent.
- Non-goals: blocking read-only helpers such as Explore; any Codex enforcement.
- Done when: a live Claude Code session as the conductor shows the hook firing on such a spawn and not on an allowed one, and the hook selftest has a negative control.

## Context
Source: the second report in T-0165, from the gen-ui-kit conductor session on 2026-09-29.

Checked 2026-09-29 with Claude Code 2.1.284 in a throwaway project: a `PreToolUse` hook on the Agent tool received an `agent_type` field set to the session agent's name when the session ran with `--agent probecond`, and no `agent_type` field when it ran with no agent. The input also carried `tool_input.subagent_type`. Not yet checked: the exact `agent_type` value for a plugin agent such as the conductor, and the field in an interactive session that declares the agent in `.claude/settings.json`. Read `docs/maintenance/claude-hooks.md` before designing it. Existing hooks key off `SDLC_ROLE`, which an interactive session does not set.

T-0165 adds the text rule. This ticket is the enforcement behind it.

## Constraints
Claude hook enforcement does not imply Codex enforcement; say so where the rule is documented. A warning must not block a session that is not the conductor.

## Plan review
- split refusal on planner-L2.md, step 3: acceptance criterion commands do not parse. Backticks inside inline-code criteria split the span: `grep -qF "## \`hooks/block-role-spawn.sh\`" ...` and the `awk "/^## \`hooks\/block-role-spawn.sh\`/..."` criterion. Write those criteria without backticks inside the command (for example grep -qF "block-role-spawn.sh" with a heading pattern that avoids backticks, or grep -qE with `.` in place of the backtick). plan defect: replan this step (/chain 3)
