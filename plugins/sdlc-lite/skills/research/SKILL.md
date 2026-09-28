---
name: research
description: "Research an outside-world question (docs, APIs, libraries) with cited findings."
argument-hint: "[L1..L3] <handoff.md | question>"
allowed-tools: Bash(${CLAUDE_PLUGIN_ROOT}/scripts/run.sh:*), Read, Write, Grep, Glob
---

**Codex host:** Before following this workflow, read [the Codex adapter](../sdlc-lite/SKILL.md) and apply its tool, argument, path, and process translations. Claude Code follows the workflow below directly.

Arguments: `$ARGUMENTS`

When launching a role, set `SDLC_ROUTING_REASON` to a short explanation of the chosen role and level (user selection, task scope, or escalation evidence). The runner records the resolved model and effort separately. Read [run operations](../handoff-format/run-operations.md) for readiness and interrupted-attempt recovery.

1. Get a handoff file. If the arguments name an existing file, use it. Otherwise create one from the text per `${CLAUDE_PLUGIN_ROOT}/skills/handoff-format/SKILL.md`.
2. Resolve the level. Follow `${CLAUDE_PLUGIN_ROOT}/skills/level-rubric/SKILL.md`, section researcher.
3. Run `${CLAUDE_PLUGIN_ROOT}/scripts/run.sh researcher <level> <handoff.md>` from the project root.
4. On success the script prints the result path. Read it and report the key lines in a few bullets plus the path. On failure, report the error and the log path.

Do not redo or extend the agent's work yourself. If the result is wrong, rerun at a higher level or tell the user.
