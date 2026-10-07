---
name: research
description: "Research an outside-world question (docs, APIs, libraries) with cited findings."
argument-hint: "[L1..L3] <handoff.md | question>"
allowed-tools: Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/dispatch.py:*), Agent, Read, Write, Grep, Glob
---

**Codex host:** Before following this workflow, read [the Codex adapter](../sdlc-lite/SKILL.md) and apply its tool, argument, path, and process translations. Claude Code follows the workflow below directly.

Arguments: `$ARGUMENTS`

When launching a role, set `SDLC_ROUTING_REASON` to a short explanation of the chosen role and level (user selection, task scope, or escalation evidence). `dispatch.py prepare` (Codex: `run.sh`) reads it and records the resolved model and effort separately. Read [run operations](../handoff-format/run-operations.md) for readiness and interrupted-attempt recovery.

1. Get a handoff file. If the arguments name an existing file, use it. Otherwise create one from the text per `${CLAUDE_PLUGIN_ROOT}/skills/handoff-format/SKILL.md`.
2. Resolve the level. Follow `${CLAUDE_PLUGIN_ROOT}/skills/level-rubric/SKILL.md`, section researcher.
3. Dispatch the researcher at `<level>` on `<handoff.md>` from the project root, the three steps of `${CLAUDE_PLUGIN_ROOT}/agents/conductor.md` ("How you run roles"): `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/dispatch.py prepare researcher <level> <handoff.md>` runs the gates and prints the dispatch JSON; an `Agent` call passes its `subagent_type`, `name`, `description`, `model`, `prompt`, and `run_in_background` unchanged; `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/dispatch.py record <dispatch_file> --agent-id <id> --tokens <n> --tool-uses <n> --duration-ms <ms>`, with the sub-agent's final message on stdin, validates and records the result. On Codex run `SDLC_BACKEND=codex ${CLAUDE_PLUGIN_ROOT}/scripts/run.sh researcher <level> <handoff.md>` instead.
4. On success `record` exits 0 and prints the result path. Read it and report the key lines in a few bullets plus the path. On failure (`record` exit 1 or 3), report the error and the result or `.limit` file path (Codex: the log path).

Do not redo or extend the agent's work yourself. If the result is wrong, rerun at a higher level or tell the user.
