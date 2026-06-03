# SSR integration

Consuming adia-ui components **inside an SSR framework** (Next.js, Nuxt, SvelteKit, Astro, …). Same components, same UI, **wildly different architecture** from the SPA path — the framework owns routing, registration must be deferred to the client, and state can't live in component-lifetime signals.

> **Honesty about sources.** The framework's `rendering-model` doc explicitly covers Next/Nuxt/SvelteKit/Astro — those patterns are marked **[D]** (documented) below. Frameworks it names in its routing table but doesn't give wiring for (Remix, Rails/Turbo, Django/HTMX, Phoenix) are marked **[G]** — the *rule* (one route owner; client-only registration) holds, but the wiring is your framework's standard pattern, not something the kit ships. Don't present **[G]** patterns as kit-guaranteed.

## Why SSR is different

Components are **light-DOM** custom elements — no shadow DOM, no hydration protocol. The server emits the tag as plain HTML (styled instantly from global CSS); the browser registers the element on the client and it self-initializes (~50ms, acceptable). **[D]**

The consequence that drives everything: `import '@adia-ai/web-components'` **throws `HTMLElement is not defined` if it runs on the server.** **[D]** So registration — the side-effect import — must be client-only.

## Client-boundary registration

Defer the import into a client lifecycle hook. One provider/boundary per app, mounted high.

**React / Next.js** **[D]** — `'use client'` + `useEffect`:

```tsx
'use client';
import { useEffect } from 'react';
export function AdiaProvider({ children }) {
  useEffect(() => {
    import('@adia-ai/web-components')
      .then(() => import('@adia-ai/web-modules/shell'))
      .then(() => import('@adia-ai/web-components/css'));
  }, []);
  return <>{children}</>;
}
```

(React ≤18 also needs a ref wrapper to set non-string props — see "property binding". React 19+ sets them natively.)

**Vue / Nuxt** **[D]** — a `.client.vue` component (Nuxt's SSR boundary) + `onMounted`:

```vue
<script setup>
import { onMounted } from 'vue';
onMounted(async () => {
  await import('@adia-ai/web-components');
  await import('@adia-ai/web-modules/shell');
});
</script>
```

**SvelteKit** **[D]** — `onMount` (the hydration barrier):

```svelte
<script>
  import { onMount } from 'svelte';
  onMount(async () => { await import('@adia-ai/web-components'); });
</script>
```

**Astro** **[D]** — CSS in server frontmatter (safe — no browser APIs), JS in a `<script>` (browser-only):

```astro
---
import '@adia-ai/web-components/css';
---
<slot />
<script>import '@adia-ai/web-components';</script>
```

## Routing ownership — exactly one owner

**[D]** Emphatic rule: there is **one route owner per app**. In SSR that's the framework's router — **never also mount `<router-ui>`.** Two owners means clicks get intercepted twice and the URL desyncs from the rendered page, breaking SSR's "URL is the source of truth" contract.

Use the framework's outlet and link element instead. Documented replacements:

| Framework | Owner | Link / outlet |
| --- | --- | --- |
| Next.js (App/Pages) **[D]** | Next router | `<Link>` (`next/link`) · `app/**/page.tsx` · `usePathname()`/`useRouter()` |
| Nuxt 3 **[D]** | Vue Router | `<NuxtLink>` · `pages/**.vue` · `useRoute()`/`useRouter()` |
| SvelteKit **[D]** | SvelteKit | `<a href>` · `src/routes/**/+page.svelte` · `$page` |
| Astro **[D]** | Astro | `<a href>` (reload) or `<ViewTransitions/>` · `Astro.url`/`Astro.params` |
| Remix · Rails/Turbo · Django/HTMX · Phoenix **[G]** | that framework | its own link + route table — wiring is standard for that stack, not kit-shipped |

The shell's body becomes the framework's route outlet — e.g. Next:

```tsx
<admin-shell>
  <admin-sidebar slot="leading">…</admin-sidebar>
  <admin-content>
    {children}   {/* the route outlet — NOT <router-ui> */}
  </admin-content>
</admin-shell>
```

## Server data → props

Fetch on the server with your framework's mechanism (`getServerSideProps`/Server Components, Nuxt `useAsyncData`, SvelteKit `load`, Astro frontmatter) and pass the result down as initial props; refresh on the client via property binding (below). The kit doesn't add a data layer here — it assumes your framework's. **[D for the constraint; the fetch mechanism is your framework's.]**

## State — cookies/session, not component signals

**[D]** Because the shell re-mounts per navigation in SSR, cross-cutting state (sidebar open/collapsed, active nav, optimistic UI) must live in **cookies / `localStorage` / a server session** — *not* in client-only signals scoped to a component's lifetime, which reset on every page. Read/write with `cookies()` (Next), `useCookie()` (Nuxt), `event.cookies` (SvelteKit). The shell primitives read those stores fine.

## Property binding (attributes are strings)

A light-DOM custom element only gets *string* attributes from markup; objects/arrays/booleans must be set as **properties**. **[D]**

- **React:** `ref` + `useEffect` to set `el.value`; read events off `e.detail`. (`<slider-ui ref={r}/>`, then `r.current.value = v`.)
- **Vue:** `:value="v"` sets the property (not the attribute); `@change="v = $event.detail.value"`.
- **Svelte:** `bind:value={v}` — two-way.
- **Astro:** **[not documented]** — static stringified attributes only; for reactive props, drop to a framework island (`.tsx` with `client:load`).

## SSR anti-patterns

- Top-level `import '@adia-ai/web-components'` in a module the server evaluates → `HTMLElement is not defined`. Defer to the client hook.
- Mounting `<router-ui>` alongside the framework router (double owner).
- Cross-cutting state in component-lifetime signals (lost on navigation) — use cookies/session.
- Top-level `<script type="module">` doing `el.columns = …` wiring — DOM isn't there during SSR; move it into the client hook.
- Wrapping a shell's direct children in a routing `<div>` — breaks direct-child selectors like `admin-page > admin-page-header`; use the framework outlet at the documented slot.

## Genuinely undocumented (don't fabricate)

The kit does **not** document: Astro reactive property binding; client wiring for Remix/Rails/Turbo/Django/HTMX/Phoenix (routing-owner rule applies, wiring is yours); icon-loader registration outside Vite (`installIconLoadersForRegistered` uses Vite's `import.meta.glob`); a unified CSS-placement rule across frameworks; and the exact React-≤18 ref-wrapper. When asked for one of these, say it's not kit-documented and reason from the framework's own conventions — and consider `mcp__a2ui__search_chunks` for anything that landed in the corpus after this snapshot.
