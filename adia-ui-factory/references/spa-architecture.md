# SPA architecture

The client-rendered path (vanilla / Vite static host). The framework is SPA-native: the components register at load, the page is one document, and routing/state live in the browser. If you're inside Next/Nuxt/SvelteKit/Astro instead, you're on the **SSR** path — see [ssr-integration.md](ssr-integration.md); the two diverge sharply on routing, registration, and state.

## The host document

One static `index.html` whose job is to load CSS in cascade order and register components once:

```html
<!doctype html>
<html lang="en" data-theme="auto">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <link rel="stylesheet" href="/packages/web-components/styles/host.css" />   <!-- foundation: tokens + resets + page frame -->
  <link rel="stylesheet" href="/packages/web-components/styles/index.css" />  <!-- barrel: every component's CSS -->
  <link rel="stylesheet" href="/packages/web-components/styles/verse.css" />  <!-- opt-in register (only if a surface uses [verse]) -->
  <link rel="stylesheet" href="./index.css" />                               <!-- page framing: sizes + centers the surface -->
  <link rel="stylesheet" href="./components/my-surface/my-surface.css" />    <!-- the surface's own chrome -->
  <script type="module" src="/packages/web-components/index.js"></script>    <!-- registers EVERY primitive (incl. router-ui) -->
  <script type="module" src="./components/my-surface/my-surface.js"></script>
</head>
<body>
  <my-surface verse></my-surface>
</body>
</html>
```

**Cascade order is load-bearing** (later wins): foundation → barrel → register → page → component. Invariants:

- Link **both** `host.css` and `styles/index.css`. Post-0.7.6 the barrel was split — `host.css` is foundation-only, so linking it alone renders primitives unstyled.
- **One** registration script (`/packages/web-components/index.js`). Don't piecemeal-import primitives across the page.
- Never hand-roll `:where(html,body){}` — the foundation owns the page frame; re-rolling it drifts from the system (the classic serif-leak bug).
- A register has two halves: link `verse.css` **and** put `verse` on the surface. One without the other is a no-op.

## Four-axis project structure

```text
my-app/
├── spec/     design axis — BRIEF · ARCHITECTURE · SPEC · screen specs
├── plan/     execution axis — ROADMAP · MILESTONES · PLAN
├── skills/   procedural-knowledge axis — the app's own expert skill (optional)
└── app/
    ├── shared/   cross-surface source — DataClient, loaders, mappers, images
    └── <surface>/src/
        ├── index.html              the host shell (above)
        ├── index.css               page framing
        └── components/<tag>/<tag>.{js,css}
```

Keep design (`spec/`), plan (`plan/`), and source (`app/`) on separate axes — the spec is the contract, the plan is the sequence, the app is the build.

## The page-trio (and when it collapses)

A standalone page is a triplet:

| File | Owns |
| --- | --- |
| `<page>.html` | static shell — meta, CSS/script links, a mount point |
| `<page>.contents.html` | the markup, **fetched** and injected at runtime |
| `<page>.contents.js` | `setup(root)` — wires behavior after the markup lands |

```js
const root = document.getElementById('demo-root');
root.innerHTML = await (await fetch('./page.contents.html')).text();
(await import('./page.contents.js')).default?.(root);   // setup(root)
```

In a real app the trio usually **collapses into the surface's own custom-element lifecycle** — the container fetches its data and renders its own subtree in `connected()`, so there's no separate `.contents.*` pair. Use the trio for playground/demo pages; use a self-booting container for app surfaces.

## Routing — content-less `<router-ui>`

`router-ui` (registered by the barrel) drives in-DOM tabs. Give it routes **without** `content` so it leaves your stamped children intact and only reflects `data-route-path` on itself; CSS shows the active view:

```js
router.routes = [{ path: '/live' }, { path: '/briefing' }];   // content-LESS
router.navigate('/live');
```

```css
my-surface .view { display: none; }
my-surface router-ui[data-route-path="/live"] .live { display: flex; }
```

A **content-mode** route (one carrying `content`) makes the router fetch and `innerHTML`-replace — which wipes stamped views, scroll, and focus. That's the wrong tool for in-DOM tabs. Never `innerHTML` a view on switch; show/hide.

## Data-flow — `DataClient` → projection

The UI never talks to a backend. It reads typed **projections** from a `DataClient`; a pure mapper is the swap seam between fixtures and a real API:

```text
DataClient.read({ type: 'LabRecommendationSet', params })   ← the only surface the UI sees
   → runMapper(query, loader)                                ← pure (sources) => Projection; the v1-fixture ⇄ v2-API seam
      → CorpusLoader.load*()                                 ← fetches the source data
```

- Components consume **projections only** — no backend calls, no re-deriving projections in the view, no per-view reshaping (the projection type *is* the contract).
- **Attribution is structural:** every `mutate` requires an `action_source`; the client throws without it.

  ```js
  await client.mutate({ type: 'order', payload }, { action_source: btn.dataset.action });
  ```

## State — single owner

One owner per piece of state, no shadow copies:

- the **route** owns which view is active,
- the **component** owns selection sets / UI toggles,
- the **DataClient** owns fetched data.

A control mutates the route; an observer or CSS reflects the route **into** the DOM — never the reverse. Mirror with a `MutationObserver` on `data-route-path`, not a second source of truth.

## Exit gate

A surface isn't done when it compiles — it's done when it passes the **browser gate** (zero console errors on load, non-zero bounding boxes, and you've *read* the screenshot) plus the a11y and git checks. That gate is the `adia-ui-verify` skill. Re-baseline git at the start of every turn, stage explicit allowlists (never `git add -A` on a shared clone), and confirm the branch before committing.
