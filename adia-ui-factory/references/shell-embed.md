---
name: shell-embed
load-when: authoring an embedded adia-ui surface (a light-DOM element a host page sizes/centers), or anticipating the official adia-embed-shell
load-size: ~1.5k tokens
required-for: [adia-ui-shells — embed path]
---

# adia-embed-shell — embedded surface _(FORTHCOMING)_

> **Status: emerging.** There is **no `<adia-embed-shell>` web-module shipped yet.** This is the official promotion-in-progress of the **embedded-app pattern** (the patient-labs / population-health surfaces). Build to the pattern below today; when the shell ships, re-bake this reference (paired with the pinned a2ui MCP snapshot) and the API firms up. Treat exact shapes here as **[PATTERN]** (verified from the embedded app), not **[SHELL-API]** (doesn't exist yet).

An **embedded surface** is a self-contained light-DOM custom element that a _host page_ (an EHR, another SaaS) positions and sizes — adia-ui owns the surface, the host owns the frame.

## The pattern (today) **[PATTERN]**

- **A self-booting container.** One custom element (`<my-surface>`); `connected()` guarded by a `#booted` flag (it re-fires on DOM moves); it fetches its data and renders its own subtree. No framework wrapper, no shadow DOM.
- **The host sizes/centers it.** The placer page positions the element (absolute + `translate(-50%, -50%)`); the surface does **not** hardcode width/height (size-agnostic — the consumer owns extent).
- **Panel layout:** pinned header/footer + scrollable body via flex + `min-block-size: 0` on the scroll region.
- **Data via projection.** `DataClient.read({ type, params })` returns typed projections from pure mappers (`app/shared/corpus/mappers/`); the surface never calls a backend directly. **Every `mutate` carries `action_source`** (attribution is required; the client throws without it). Depth: `adia-ui-data`.
- **Routing (in-DOM tabs):** a content-less `<router-ui>` whose URL you manage yourself with `history.replaceState()` to preserve the host's query params — do **not** set `router.routes` (that fetches + replaces). (This is the one place an embedded surface uses `<router-ui>`; it's a self-contained SPA island, not an SSR page — see the hybrid note in `adia-ui-data`.)
- **Shared foundation.** Multiple embedded surfaces live under a `shared-foundation` project shape (`app/shared/` for DataClient/mappers/tokens) — see `project-shapes.md`.

## Authoring checklist (until the shell ships)

1. Scaffold a `shared-foundation` app; put the surface under `app/<surface>/src/`.
2. Author the surface as a self-booting light-DOM container (`#booted` guard, render in `connected()`).
3. Wire data through `DataClient`/mappers; attribute every mutation.
4. Keep it size-agnostic; let the host place it.
5. Verify in a host harness (renders, zero console errors, non-zero box) — `adia-ui-verify`.

## When it ships

The official `adia-embed-shell` is expected to package this chrome (the panel layout, the host-placement contract, the embed bridge) as a web-module like the others. At that point: register via the cluster barrel, replace the hand-rolled container chrome with the shell, and keep the DataClient/projection + attribution wiring. Until then, the pattern above **is** the contract.
