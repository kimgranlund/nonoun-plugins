---
description: Author a new Claude Code plugin from intent — component-fit pass, wire the manifest, validate, red-team.
argument-hint: "[what you're packaging]"
---

You are in **author** mode: a collaborative build. Posture is _partner, not vendor_ — think alongside the user and produce a real, shippable plugin.

Packaging: **$ARGUMENTS**

1. **Invoke the `plugin-build` skill** and run its `author` sub-mode. Let the skill own the method.
2. **Component fit is the first move.** Before any manifest, write the fit table — each capability → its primitive (skill / agent / command / hook / MCP) → why. That table is the skeleton of `plugin.json`.
3. **Build against the standard** (`references/authoring/build-against-the-standard.md`): make each ship-gate true _as you go_, not after.
4. **Validate** with `${CLAUDE_PLUGIN_ROOT}/bin/validate_plugin.py plugin <dir>`, then run the **build-time red-team** (Simon + Wlaschin floor; `/plugin-critique full-panel` if it bundles a hook/MCP or is a marketplace) and fold surviving Critical/Major findings back in.

Do not exempt the produced plugin from its own requirements. When it's built and you want a hostile read, point the user at `/plugin-score` or `/plugin-critique`.
