---
name: adia-ui-ssr
description: >
  Architect and wire an adia-ui app inside an SSR framework (Next / Nuxt / SvelteKit / Astro) —
  client-only registration in lifecycle hooks, framework routing (never <router-ui>), server-side
  data fetch + initial props, cookie/session state. Use when consuming the components under SSR; if
  the rendering mode isn't decided yet, start with adia-ui-factory. (Author components with adia-ui-compose.)
---

# adia-ui-ssr — components inside an SSR framework

For consuming adia-ui components inside Next.js / Nuxt / SvelteKit / Astro (or similar). Same components, same UI as SPA — but the **framework owns routing**, **registration must be deferred to the client**, and **state lives in cookies/session, not signals**. Get these three wrong and the app breaks in ways SPA habits won't predict.

Full depth: **`${CLAUDE_PLUGIN_ROOT}/references/ssr-integration.md`** (it labels every pattern documented-by-the-framework vs. inferred). Compose the screens with `adia-ui-compose`.

## Build order

1. **Client-boundary provider** — defer the side-effect import into a client hook: Next `'use client'` + `useEffect`; Nuxt `.client.vue` + `onMounted`; SvelteKit `onMount`; Astro `<script>` (CSS may import server-side). A top-level `import '@adia-ai/web-components'` on the server throws `HTMLElement is not defined`.
2. **Routing = the framework's** — never mount `<router-ui>`. Exactly one route owner; use `<Link>`/`<NuxtLink>`/`<a>` and the framework's route dirs. The shell body becomes the framework's route outlet.
3. **Server data → props** — fetch with the framework's mechanism (Server Components / `useAsyncData` / `load`), pass as initial props, refresh on the client.
4. **State → cookies/session** — the shell re-mounts per navigation, so cross-cutting state (sidebar, nav, optimistic UI) goes in cookies/`localStorage`/session, not component-lifetime signals.
5. **Property binding** — attributes are strings; set objects/arrays as properties (React `ref`, Vue `:prop`, Svelte `bind:`).
6. **Verify** — the browser gate (`adia-ui-verify`).

## Non-negotiables

- **Client-only registration** — never import the components at server module top-level.
- **One route owner** — the framework's router; `<router-ui>` is an SPA tool and must not co-exist with it.
- **State out of signals** — anything that must survive a navigation lives in cookies/session.
- **Properties, not attributes**, for non-string data.

## Honesty about coverage

The framework **documents** Next / Nuxt / SvelteKit / Astro patterns — follow them. For frameworks it only names in its routing table (Remix, Rails/Turbo, Django/HTMX, Phoenix), the **rules hold** (one route owner; client-only registration) but the wiring is that stack's standard pattern, not kit-shipped — say so, don't fabricate. A few things (Astro reactive binding, non-Vite icon loaders, the React-≤18 ref wrapper) are genuinely undocumented; reason from framework conventions and check `mcp__a2ui__search_chunks`.

## References

- `${CLAUDE_PLUGIN_ROOT}/references/ssr-integration.md` — registration, routing ownership, data, state, property binding, anti-patterns, gaps.
- `${CLAUDE_PLUGIN_ROOT}/references/component-model.md` and `authoring-components.md` — for the components themselves (via `adia-ui-compose`).
