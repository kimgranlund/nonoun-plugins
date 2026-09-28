---
name: build
description: "Build one plan step: run a builder headless at a fixed model and effort per level (L1..L5). If no level is given, take it from the handoff or assess the step first. Args: [level] <step handoff.md>."
argument-hint: "[L1..L5] <handoff.md>"
allowed-tools: Bash(${CLAUDE_PLUGIN_ROOT}/scripts/run.sh:*), Read, Grep, Glob
---

**Codex host:** Before following this workflow, read [the Codex adapter](../sdlc-lite/SKILL.md) and apply its tool, argument, path, and process translations. Claude Code follows the workflow below directly.

Arguments: `$ARGUMENTS`

1. Resolve the level per `${CLAUDE_PLUGIN_ROOT}/skills/level-rubric/SKILL.md`, section builder. Without an explicit level or a `level:` line, read the handoff and the files it names, then assess. State the level and a one-line reason.
2. Run `${CLAUDE_PLUGIN_ROOT}/scripts/run.sh builder <level> <handoff.md>` from the project root.
3. On success the script prints the result path. Read it and report its Status plus one line per change. On failure, report the error and the log path.

Do not fix or redo the builder's work yourself.
