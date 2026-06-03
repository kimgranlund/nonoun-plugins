# The adia-ui component model

How to *think* about the catalog. The **live** catalog is the a2ui MCP (`get_component_map`, `lookup_component`, `get_traits`) — query it for exact names, props, and counts; don't memorize them here (they drift per release). This file teaches the vocabulary so the MCP's answers make sense.

## Three tiers

| Tier | Package | What it is | Examples (shape, not a contract) |
| --- | --- | --- | --- |
| **Primitives** | `@adia-ai/web-components` | Atomic custom elements — controls, layout, display, overlays | `<button-ui>` `<input-ui>` `<select-ui>` `<table-ui>` `<card-ui>` `<modal-ui>` `<drawer-ui>` |
| **Layout primitives** | (same) | The box model — never hand-roll a bare `<div>` for layout | `<col-ui>` `<row-ui>` `<grid-ui>` `<stack-ui>` `<page-ui>` `<section-ui>` |
| **Traits** | (subpath) | Reusable *behaviors* attached to any element — not data, not components | `pressable` `focusable` `draggable` `ripple` `scale-press` `roving-tabindex` `focus-trap` |
| **Composites / shells** | `@adia-ai/web-modules` | Multi-component surfaces / page chrome | `<admin-shell>` `<admin-sidebar>` `<chat-shell>` `<editor-shell>` |

**Naming:** kebab-case with a `-ui` **suffix** (`<button-ui>`, not `<a-button>`). Shells/composites carry a domain prefix (`<admin-*>`, `<chat-*>`).

**Rule of first resort:** reach for a catalog primitive before authoring anything. Never use a raw `<button>`/`<input>`/`<div>` where a `*-ui` primitive exists — raw elements skip focus rings, theming, density, and form association. Author a project component (see [authoring-components.md](authoring-components.md)) only when no primitive composes to the need.

## Registration is a side effect of import

Importing a component module **registers its tag**. Two forms:

```js
import '@adia-ai/web-components';            // the barrel — registers every primitive (incl. router-ui)
import '@adia-ai/web-components/components/button/button.js';  // one component
```

Registration uses `defineIfFree('button-ui', UIButton)` internally — idempotent, so double-import is safe. The non-registering class import (`.../button/class`) exists for tests/subclassing. **In SSR this import must be client-only** — see [ssr-integration.md](ssr-integration.md).

## Signals, not a virtual DOM

Components extend `UIElement` (or `UIFormElement` for form-participating controls) and use fine-grained signals:

```js
import { UIElement, signal, computed, effect } from '@adia-ai/web-components/core/element.js';
```

- `signal(v)` — reactive value (`.value` get/set)
- `computed(() => …)` — memoized derived value
- `effect(() => …)` — runs on dependency change; auto-cleans on disconnect

Declared `static properties` are wrapped as signals automatically, so setting `el.disabled = true` re-renders. Don't run a parallel `CustomEvent`-only state path that competes with signals.

## Traits — behavior by declaration

```html
<button-ui traits="pressable scale-press ripple">Save</button-ui>
```

or programmatically: `static traits = [pressable, scalePress]`. A trait is a factory (`defineTrait({ name, setup({host}) { …; return cleanup } })`) that manages attributes/events and tears itself down on disconnect. Query the live set with the MCP's `get_traits`.

## Tokens — the only styling currency

Three levels, all `--a-*`:

| Level | Role | Examples |
| --- | --- | --- |
| **L1 primitive scales** | dimensionless base values | `--a-space-2` `--a-size-md` `--a-radius-sm` `--a-duration-fast` `--a-font-family-ui` |
| **L2 semantic families** | role vocabulary | `--a-primary` `--a-danger` `--a-accent-bg` |
| **L3 state × role** | what components consume | `--a-accent-bg-hover` `--a-danger-fg-active` `--a-ui-bg-disabled` |

- **Color scheme** uses `light-dark()` at the token layer — never swap tokens by hand. Toggle with `<toggle-scheme-ui scheme="auto" target=":root" persist>`.
- **Density** scales spacing via `--a-density` set at a provider boundary (`<div style="--a-density: 0.8">`).
- **Zero raw colors, zero raw px ≥ 3** in component CSS — always a token. This is mechanized by the `adia-lint` hook and by the MCP's `check_anti_patterns`.

## "Registers" — typographic treatments, opt-in

A *register* (e.g. `verse`, `prose`) is a typographic treatment applied two ways together: **link the register stylesheet** (`styles/verse.css`) **and** put the **attribute** on the surface (`<my-surface verse>`). One without the other is a no-op — a common smell. Body/UI text defaults to `--a-font-family-ui`; registers opt a subtree into a different family/rhythm.

## Where this is incomplete

The deep internals — the `html` template engine's escaping contract, `BaseController` delegation, the icon loader (`installIconLoadersForRegistered` + Vite `import.meta.glob`), `@bp` responsive notation, and the A2UI runtime/`<a2ui-root>` resolver — are framework-owned and version-specific. Treat the MCP (`lookup_component`, `search_chunks`) as the source of truth for them rather than encoding them here.
