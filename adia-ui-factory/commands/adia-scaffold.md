---
description: Scaffold a new adia-ui app — pick the rendering mode (SPA / SSR-framework), lay out the structure, wire the host.
argument-hint: [spa|ssr] [app name]
---

Scaffold a new adia-ui app. **$ARGUMENTS**

1. **Determine the rendering mode** from the first argument (`spa` | `ssr`). If absent, run the `adia-ui-factory` mode detection (Step 0) — or ask the user when it's greenfield.
2. **Hand off to the mode skill** to lay out the structure and wire the host:
   - SPA → **`adia-ui-spa`** (static host document + four-axis layout + one registration script).
   - SSR → **`adia-ui-ssr`** (client-boundary provider + framework route outlet).
3. Compose the first screen with **`adia-ui-compose`**.

`bin/adia-scaffold` will mechanize the deterministic file layout in a later phase; until then follow the skill's build order. Don't restate the methodology here — the skill owns it.
