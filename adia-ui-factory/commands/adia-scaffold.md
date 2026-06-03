---
description: Scaffold a new adia-ui app — pick the rendering mode (SPA / SSR-framework), lay out the structure, wire the host.
argument-hint: [spa|ssr] [app name]
---

Scaffold a new adia-ui app. **$ARGUMENTS**

1. **Determine the rendering mode** from the first argument (`spa` | `ssr`). If absent, run the `adia-ui-factory` mode detection (Step 0) — or ask the user when it's greenfield.
2. **Lay the skeleton deterministically** with the bundled scaffolder:
   - SPA → `python3 "${CLAUDE_PLUGIN_ROOT}/bin/adia-scaffold" spa <name>`
   - SSR → `python3 "${CLAUDE_PLUGIN_ROOT}/bin/adia-scaffold" ssr <name> --framework <next|nuxt|sveltekit|astro>`
3. **Hand off to the mode skill** for the parts that need judgment: `adia-ui-spa` / `adia-ui-ssr` for the host/provider wiring the bones don't decide, then `adia-ui-compose` for the first real screen.

The bin owns the byte-stable layout; the skills own the methodology. Don't restate either here.
