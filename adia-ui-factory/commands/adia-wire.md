---
description: Wire an adia-ui app's routing, state, and data-flow (mode-aware).
argument-hint: [spa|ssr] [what to wire]
---

Wire routing, state, and data-flow for an adia-ui app. **$ARGUMENTS**

Determine the mode first (first argument, or the `adia-ui-factory` classifiers), then hand off:

- **Host wiring (mode-specific):** SPA → `adia-ui-spa` (content-less `<router-ui>`); SSR → `adia-ui-ssr` (framework router, never `<router-ui>`).
- **Data-flow · hydration · fetch/CRUD · section wiring (any mode) → `adia-ui-data`** — DataClient/projection, signals, property-API, the attribution gate, and the hybrid SPA-in-SSR boundary.

The skills own the patterns; don't restate them here.
