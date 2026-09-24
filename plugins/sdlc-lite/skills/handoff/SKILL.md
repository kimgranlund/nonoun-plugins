---
name: handoff
description: Start an sdlc task: create .sdlc/<task>/handoff.md from the current discussion so clean-context agents get everything they need.
argument-hint: <goal>
allowed-tools: Read, Write, Glob
---
Arguments: `$ARGUMENTS`

Create the task handoff per `${CLAUDE_PLUGIN_ROOT}/skills/handoff-format/SKILL.md`. Goal comes from the arguments. Context and Constraints come from what this conversation has established; the agents see nothing else, so include decisions, paths, and rejections. Leave out anything not established. Show the path and ask the user to correct anything missing before a run.
