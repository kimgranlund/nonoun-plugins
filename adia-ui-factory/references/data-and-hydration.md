---
name: data-and-hydration
load-when: wiring an adia-ui app's data-flow, state ownership, content hydration, or section registration
load-size: ~2.5k tokens
required-for: [adia-ui-data — all modes]
---

# Data, state & hydration — patterns

Code shapes for the five data-flow patterns, the three hydration paths, and section wiring. The ownership rules (single-owner · projections-only · attribution) are the `adia-ui-data` rubric gates.

## The five patterns

**1 · Signals** — fine-grained reactivity (no virtual DOM).

```js
import { signal, computed, effect } from '@adia-ai/web-components/core/signals.js';
const view = signal('live');
effect(() => render(view.value));   // re-runs on change; auto-cleans on disconnect
```

**2 · Service / Controller / Command** — CRUD with undo. The Service is **async from day one** (so an in-memory impl can later swap for a remote one behind the same interface); the Controller orchestrates signals + service; Commands record patches for undo.

```js
class InMemoryTaskService { async create(d){…} async update(id,d){…} async delete(id){…} }
// swap for RemoteTaskService (same interface) → Controller + Commands unchanged
```

**3 · DataClient + mappers** — the UI reads typed **projections**, never a backend. The pure mapper is the fixtures⇄API swap seam.

```js
const labs = await client.read({ type: 'LabRecommendationSet', params });   // → projection
// mapper lives in app/shared/corpus/mappers/, pure: (sources) => Projection
await client.mutate({ type: 'order', payload }, { action_source: btn.dataset.action }); // attribution REQUIRED
```

**Attribution `[gate]`:** every `mutate` passes an `action_source`; the client throws without it.

**4 · Property-API binding** — populate catalog components by property, not children.

```js
table.columns = [{ key:'name', label:'Name', sortable:true }];
table.data    = rows;          // NOT: append <option>/<tr> children post-connect —
select.options = opts;         // the element auto-stamps its slots at connected()
```

**5 · Declarative `data-*`** — static flows; state is CSS.

```html
<main data-auth> … </main>
<style>[data-auth] form { display: block; }</style>
```

## The three hydration paths

**SPA — self-boot.** The surface is a self-booting container; it fetches and renders itself.

```js
connected() { if (this.#booted) return; this.#booted = true; this.#load(); }
```

**SSR — server → props → client.** The framework fetches on the server, seeds components as initial props, and the client refreshes via property binding (React `ref`+`useEffect`, Vue `:prop`, Svelte `bind:`). See `adia-ui-ssr`.

**Hybrid — SPA island in an SSR page.** The server renders the page and emits the island's seed as a prop/attribute; the island **registers + boots on the client** and owns its own state and in-island routing. The framework owns the page and top-level routing; the island is a self-contained SPA surface inside it.

```html
<!-- server-rendered page (SSR) -->
<analytics-panel data-seed-id="abc"></analytics-panel>
<script type="module">import('/islands/analytics-panel.js');</script>  <!-- client-only registration -->
```

Rule: exactly one route owner *per scope* — the framework routes the page; a content-less `<router-ui>` may route tabs **inside** the island. Never let the island's router fight the framework's.

## Section registration & connection

- **Register by side-effect import** — the barrel (`@adia-ai/web-components`) or the component module; an unimported section never upgrades.
- **Data down, events up** — props in (`.rec = …`), `CustomEvent`s out; no reaching into a parent's internals.
- **Read projected children** via `logicalChildren` / `logicalSlotted` (from `@adia-ai/web-components/core/logical-children`) — `this.children` misses `${items.map(…)}` output and the `display:contents` trap.

## Routing & state ownership

- **Content-less `<router-ui>`** for in-DOM/in-island tabs: routes *without* `content`; CSS shows the active view. A content-mode route fetches + `innerHTML`-replaces — wrong for stamped views.
- **Own the URL** when you need query params: `history.replaceState(...)` and reflect `data-route-path` yourself; don't set `router.routes` (it path-routes and clobbers query params).
- **Single owner** per piece of state — the route owns the active view, the component owns selection/toggles, the DataClient owns fetched data. A control mutates the route; an observer/CSS reflects it back — never a second source of truth.
