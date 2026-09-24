---
name: architect
description: Design how a goal fits the existing system: approach, interfaces, constraints, rejected alternatives. Use before /plan for cross-cutting or unfamiliar work.
argument-hint: <handoff.md | goal>
allowed-tools: Bash(${CLAUDE_PLUGIN_ROOT}/scripts/run.sh:*), Read, Write, Grep, Glob
---
Arguments: `$ARGUMENTS`

1. Get a handoff file. If the arguments name an existing file, use it. Otherwise create one from the text per `${CLAUDE_PLUGIN_ROOT}/skills/handoff-format/SKILL.md`.
2. Resolve the level. Always L1.
3. Run `${CLAUDE_PLUGIN_ROOT}/scripts/run.sh architect <level> <handoff.md>` from the project root.
4. On success the script prints the result path. Read it and report the key lines in a few bullets plus the path. On failure, report the error and the log path.

Do not redo or extend the agent's work yourself. If the result is wrong, rerun at a higher level or tell the user.
