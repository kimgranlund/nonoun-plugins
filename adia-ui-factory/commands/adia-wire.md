---
description: Wire an adia-ui app's routing, state, and data-flow (mode-aware).
argument-hint: [spa|ssr] [what to wire]
---

Wire routing, state, and data-flow for an adia-ui app. **$ARGUMENTS**

The wiring is **opposite** across modes — determine the mode first (first argument, or `adia-ui-factory` Step 0), then hand off:

- **SPA → `adia-ui-spa`** — content-less `<router-ui>`, `DataClient`/projection data-flow, single-owner state.
- **SSR → `adia-ui-ssr`** — the framework router (never `<router-ui>`), server fetch → props, cookie/session state, property binding.

The skill owns the patterns; don't restate them here.
