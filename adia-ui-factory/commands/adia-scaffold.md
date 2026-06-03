---
description: Scaffold a new adia-ui app — pick the rendering mode (SPA / SSR-framework), lay out the structure, wire the host.
argument-hint: [spa|ssr] [app name]
---

Scaffold a new adia-ui app. **$ARGUMENTS**

1. **Pick mode + shape** via the `adia-ui-factory` classifiers (or the first argument) — or ask when it's greenfield. The shapes + four-axis layout are owned by **`adia-ui-project`** (load it for the decision).
2. **Lay the skeleton deterministically** with the bundled scaffolder:
   - SPA → `python3 "${CLAUDE_PLUGIN_ROOT}/bin/adia-scaffold" spa <name>`
   - SSR → `python3 "${CLAUDE_PLUGIN_ROOT}/bin/adia-scaffold" ssr <name> --framework <next|nuxt|sveltekit|astro>`
   - add surfaces with the `page` (`--duo` for declarative) / `component` sub-commands.
3. **Hand off:** `adia-ui-project` for the shape/layout decisions the bin doesn't make, `adia-ui-spa` / `adia-ui-ssr` for host wiring, then `adia-ui-compose` for the first real screen.

The bin owns the byte-stable layout; the skills own the methodology. Don't restate either here.
