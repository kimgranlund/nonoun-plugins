---
name: plan-goal
description: "Redirect: run `/sdlc-lite:plan goal`; removed in the next minor."
argument-hint: "[what the goal should achieve]"
allowed-tools: Read
---

**Codex host:** Before following this workflow, read the Codex adapter at `${CLAUDE_PLUGIN_ROOT}/skills/sdlc-lite/SKILL.md` and apply its tool, argument, path, and process translations. Claude Code follows the workflow below directly.

Arguments: `$ARGUMENTS`

This skill is retired and runs nothing itself. Run `/sdlc-lite:plan goal $ARGUMENTS` instead. When that name is not callable, read `${CLAUDE_PLUGIN_ROOT}/skills/plan/SKILL.md` and follow it with the kind `goal` and the arguments above.
