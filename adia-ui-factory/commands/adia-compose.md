---
description: Compose a screen or author components for an adia-ui app (catalog-driven, via the a2ui MCP).
argument-hint: [what to build]
---

Compose UI for an adia-ui app. **$ARGUMENTS**

Invoke **`adia-ui-compose`** and run its loop: discover the catalog (`mcp__a2ui__get_component_map` / `lookup_component`) → compose from primitives → author a light-DOM component only if no primitive fits → theme with `--a-*` tokens → validate (`mcp__a2ui__check_anti_patterns`).

This is mode-independent — the same whether the app is SPA or SSR. The skill owns the discipline; don't restate it here.
