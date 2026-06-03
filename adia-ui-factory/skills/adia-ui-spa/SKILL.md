---
name: adia-ui-spa
description: >
  Architect and wire an adia-ui app in SPA mode — static host document, the four-axis structure,
  content-less <router-ui> routing, the client DataClient/projection data-flow, single-owner state.
  Use when the app is a client-rendered SPA (Vite / vanilla); if the rendering mode isn't decided
  yet, start with adia-ui-factory. (Author the components themselves with adia-ui-compose.)
version: 0.2.0
---

# adia-ui-spa — the client-rendered path

For apps where the browser owns everything: one static host document, components registered at load, routing and state in the client. The framework is SPA-native, so this is the path of least resistance. (Inside Next/Nuxt/SvelteKit/Astro instead? Use `adia-ui-ssr` — the wiring is opposite.)

Full depth: **`${CLAUDE_PLUGIN_ROOT}/references/spa-architecture.md`**. Compose the screens themselves with `adia-ui-compose`.

## Build order

1. **Host document** — one static index.html: cascade-ordered CSS links (`host.css` → `styles/index.css` → opt-in register → page → component) and **one** registration script (`/packages/web-components/index.js`).
2. **Four-axis layout** — `spec/` (design) · `plan/` (execution) · `app/` (source) · `skills/` (optional expert skill).
3. **Surface container** — a self-booting custom element that fetches data and renders its subtree in `connected()`. (Standalone pages can use the page-trio; app surfaces fold it into the container.)
4. **Routing** — content-less `<router-ui>`: routes *without* `content`, CSS shows the active view.
5. **Data-flow** — `DataClient.read(projection)` → pure `runMapper` → loader; the UI sees projections only.
6. **State** — single owner per piece; control mutates the route, observer/CSS reflects it back.
7. **Verify** — the browser gate (`adia-ui-verify`).

## Non-negotiables

- **Link both `host.css` and `styles/index.css`** (post-0.7.6 barrel split) — `host.css` alone renders primitives unstyled.
- **One registration script** — don't piecemeal-import primitives; never hand-roll `:where(html,body){}`.
- **Content-less router for in-DOM tabs** — a content-mode route fetches + `innerHTML`-replaces, wiping stamped views/scroll/focus. Show/hide; never re-`innerHTML` on switch.
- **Projections only** — components never call a backend or re-derive projections; mappers are pure `(sources) => Projection`.
- **Attribution is structural** — every `client.mutate(...)` passes an `action_source` or the client throws.
- **Single-owner state** — no shadow copies; the route is the source of truth for the active view.
- **Guards** — `defineIfFree` for define, a `#booted` flag for boot (the callback re-fires on DOM moves).

## Verify target

Done when the surface **renders in the browser** (`adia-ui-verify`) with zero console errors and non-zero bounding boxes, the host links + registration are correct (primitives styled, elements upgraded), and a state change round-trips. "Compiles" / "tests pass" is not the gate.

## §SelfAudit (before declaring done)

Both `host.css` + `styles/index.css` linked; one registration script; routing content-less; state single-owner; every mutation carries `action_source`; define + boot guards present. **Not done** if primitives render unstyled (missing barrel), a view re-`innerHTML`s on switch, or state has a shadow copy.

## Data, state & hybrid

This skill wires the SPA **host**; the **data-flow, hydration, and section-wiring patterns are shared** → `adia-ui-data` (DataClient/projection, signals, property-API, the attribution `[gate]`). A SPA surface can also run as an **island inside an SSR page** — `adia-ui-data` owns that hybrid boundary.

## References

- `${CLAUDE_PLUGIN_ROOT}/references/spa-architecture.md` — host doc, four-axis, page-trio, router, data-flow, state, git.
- `${CLAUDE_PLUGIN_ROOT}/references/component-model.md` and `authoring-components.md` — for the components themselves (via `adia-ui-compose`).
