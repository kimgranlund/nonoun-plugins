---
name: plan-doc
description: "Redirect: run `/sdlc-lite:plan doc`; removed in the next minor."
argument-hint: "[what the plan should achieve]"
allowed-tools: Read
---

**Codex host:** Before following this workflow, read the Codex adapter at `${CLAUDE_PLUGIN_ROOT}/skills/sdlc-lite/SKILL.md` and apply its tool, argument, path, and process translations. Claude Code follows the workflow below directly.

Arguments: `$ARGUMENTS`

This skill is retired and runs nothing itself. Run `/sdlc-lite:plan doc $ARGUMENTS` instead. When that name is not callable, read `${CLAUDE_PLUGIN_ROOT}/skills/plan/SKILL.md` and follow it with the kind `doc` and the arguments above.
