---
description: Fix or improve an existing plugin — a mis-fit component, a kitchen-sink boundary, an illegal dependency, bloated context.
argument-hint: "[path to plugin] [what's wrong]"
---

You are in **edit** mode: a targeted fix to an existing plugin, against the same standard it will be scored by.

Target / concern: **$ARGUMENTS**

1. **Invoke the `plugin-build` skill** and run its `edit` sub-mode. Read the existing plugin's files first — `plugin.json`, the component tree, `hooks/hooks.json`, `.mcp.json`.
2. **Name the dimension** the fix lives in (P1–P9) and read its rubric + foundation before changing anything.
3. **Make the fix**, keeping invocation names stable (P8) and the manifest valid (`${CLAUDE_PLUGIN_ROOT}/bin/validate_plugin.py`).
4. **Re-run the owning critic(s)** for that dimension as a targeted red-team before declaring done.

Common edits: a must-run step that should be a hook (P2), a kitchen-sink boundary to split (P3), a `../` cross-plugin path to legalize (P4), bloated always-on context (P6), a routing collision (P7). If the fix is really "score this first," start with `/plugin-score`.
