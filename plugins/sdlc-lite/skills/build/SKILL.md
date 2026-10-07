---
name: build
description: "Build one plan step: dispatch a builder sub-agent at a fixed model and effort per level (L1..L5). If no level is given, take it from the handoff or assess the step first. Args: [level] <step handoff.md>."
argument-hint: "[L1..L5] <handoff.md>"
allowed-tools: Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/dispatch.py:*), Agent, Read, Grep, Glob
---

**Codex host:** Before following this workflow, read the Codex adapter at `${CLAUDE_PLUGIN_ROOT}/skills/sdlc-lite/SKILL.md` and apply its tool, argument, path, and process translations. Claude Code follows the workflow below directly.

Arguments: `$ARGUMENTS`

When launching a role, pass `dispatch.py prepare --routing-reason "<why>"` (or set `SDLC_ROUTING_REASON`) with a short explanation of the chosen role and level (user selection, task scope, or escalation evidence). `dispatch.py prepare` (Codex: `run.sh`) reads it and records the resolved model and effort separately. Read run operations at `${CLAUDE_PLUGIN_ROOT}/skills/handoff-format/run-operations.md` for readiness and interrupted-attempt recovery.

1. Resolve the level per `${CLAUDE_PLUGIN_ROOT}/skills/level-rubric/SKILL.md`, section builder. Without an explicit level or a `level:` line, read the handoff and the files it names, then assess. State the level and a one-line reason.
2. Dispatch the builder at `<level>` on `<handoff.md>` from the project root, the three steps of `${CLAUDE_PLUGIN_ROOT}/agents/conductor.md` ("How you run roles"): `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/dispatch.py prepare builder <level> <handoff.md>` runs the gates and prints the dispatch JSON; an `Agent` call passes its `subagent_type`, `name`, `description`, `model`, `prompt`, and `run_in_background` unchanged; `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/dispatch.py record <dispatch_file> --agent-id <id> --tokens <n> --transcript <sub-agent transcript jsonl> --tool-uses <n> --duration-ms <ms>`, with the sub-agent's final message on stdin, validates and records the result. On Codex run `SDLC_BACKEND=codex ${CLAUDE_PLUGIN_ROOT}/scripts/run.sh builder <level> <handoff.md>` instead.
3. On success `record` exits 0 and prints the result path. Read it and report its Status plus one line per change. On failure (`record` exit 1 or 3), report the error and the result or `.limit` file path (Codex: the log path).

Do not fix or redo the builder's work yourself.
