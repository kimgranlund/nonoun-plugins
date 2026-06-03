---
name: adia-ui-ssr
description: >
  Architect and author an adia-ui app inside an SSR framework (Next / Nuxt / SvelteKit / Astro) — guarded dynamic-import registration in lifecycle hooks, framework routing (never <router-ui>), server-side data fetch + initial props, cookie/session state. Use when consuming the components under SSR.
---

# adia-ui-ssr

> **Stub — scaffolded in phase (a); content authored in phase (b).**

This skill will own:

- the client-boundary discipline: dynamic import in useEffect/onMounted/onMount (never top-level on the server)
- framework routing ownership (never alongside <router-ui>)
- server data fetch → initial props → client refresh
- cookie/session state (shell re-mounts per page); per-framework property binding

Source (to vendor/synthesize): the `app-authoring-best-practices` methodology (SPA) and `adia-ui-kit/rendering-model` (SSR) from the framework, plus the a2ui MCP tool surface.
