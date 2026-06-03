# Authoring a project component

When no catalog primitive composes to the need, author a light-DOM custom element. The discipline below is what separates a component that themes, scales, and survives HMR from one that fights the system. It mirrors the framework's own audit gates — the `adia-lint` hook and the MCP's `check_anti_patterns` mechanize the catchable parts.

## The skeleton

A component is three files in one folder (`components/<tag>/`):

```
components/my-thing/
├── my-thing.js      # the class + side-effect registration
├── my-thing.css     # the @scope block (token-only)
└── my-thing.class.js  # (optional) the class alone, for tests/subclassing
```

```js
// my-thing.js
import { defineIfFree } from '@adia-ai/web-components/core/register.js';
import { UIElement } from '@adia-ai/web-components/core/element.js';

class UIMyThing extends UIElement {
  static properties = { /* declared props become signals */ };
  connected()    { /* set up; pair every addEventListener with a teardown */ }
  disconnected() { /* remove every listener added in connected() */ }
}
defineIfFree('my-thing', UIMyThing);   // idempotent — safe on HMR / double import
export { UIMyThing };
```

## The two-block `@scope` CSS (mandatory shape)

Every component stylesheet is scoped to its tag and split into a zero-specificity token block and a base block:

```css
@scope (my-thing) {
  :where(:scope) {                 /* specificity (0,0,0) — themes + consumers override cleanly */
    --my-thing-bg:     var(--a-ui-bg);
    --my-thing-fg:     var(--a-ui-text);
    --my-thing-radius: var(--a-radius);
    --my-thing-px:     var(--a-ui-px);
  }
  :scope {                         /* specificity (0,1,0) — base styles, consume component tokens only */
    display: flex;
    padding-inline: var(--my-thing-px);
    background: var(--my-thing-bg);
    color: var(--my-thing-fg);
    border-radius: var(--my-thing-radius);
  }
  :scope[variant="outline"] {      /* variants = token overrides only, never layout */
    --my-thing-bg: transparent;
  }
}
```

**Why two blocks:** `:where(:scope)` is zero-specificity, so a parent theme provider or a consumer override beats your defaults without `!important`. Collapsing into a single `:scope` block breaks theme switching. The base block consumes the component's *own* tokens (`--my-thing-*`), which alias the system tokens (`--a-*`) — so re-theming flows through one indirection layer.

## Invariants

- **Token-only.** No raw `#hex` / `rgb()` / `oklch()` and no raw px ≥ 3 in component CSS — always `var(--a-*)` (border-hairlines 1–2px are the only carve-out, with a comment).
- **Size-agnostic chrome.** Never set `width`/`height`/`inline-size` on the tag's `:scope`. The component owns *intrinsic* sizing (`min-height`, `padding`, `gap`); the **consumer** (a layout primitive or explicit style) owns extent. Width-on-tag fights the placer and the resizable frame.
- **Light DOM only.** Never `attachShadow`. No `::slotted()` (a shadow-DOM API) — style slotted content via `:scope > [slot="x"]`. To *read* projected children, use `logicalChildren` / `logicalSlotted` from `@adia-ai/web-components/core/logical-children` — plain `this.children` misses children rendered through `${items.map(…)}` and the `display:contents` trap.
- **Guard define and boot.** `defineIfFree` guards re-definition; also guard the boot (`#booted` flag in `connected()`) — the callback fires again whenever the element moves in the DOM, which otherwise double-renders.
- **Symmetric lifecycle.** Every `addEventListener` in `connected()` has a matching `removeEventListener` in `disconnected()`. Use a stable handler reference (private field `#onClick = (e) => …`), not an inline arrow — `removeEventListener` needs reference equality.
- **Data down, events up.** Sub-components receive state via properties (`.rec = …`) and emit `CustomEvent`s; they never reach into a parent's internals.
- **Font-family floor.** A text-bearing component floors its family to a token: `font-family: var(--my-thing-family, var(--a-font-family-ui))` — otherwise it inherits a broken host font (the dead-`--a-font` trap resolves to UA serif).

## Anti-patterns (the lint seeds)

The mechanizable smells the framework audits — these seed the phase-(c) hook and overlap the MCP's `check_anti_patterns`. Grep hints in parens.

| Smell | Fix |
|---|---|
| Shadow DOM (`attachShadow`) | light DOM only |
| Raw color in component CSS (`#`, `rgb(`, `oklch(`) | `var(--a-*)` token |
| Raw px ≥ 3 without carve-out comment | `var(--a-space-*)` |
| `::slotted(` | `:scope > [slot="x"]` |
| `width`/`height`/`inline-size` on the tag `:scope` | consumer owns extent |
| Dead font token (`--a-font` ≠ `--a-font-family*`) | floor to `--a-font-family-ui` |
| Single `:scope` block (no `:where(:scope)` token block) | two-block `@scope` |
| Boolean prop `default: true` | flip the name (`closable`→`permanent`) so absent = false |
| `attr:` in a property def | `attribute:` |
| `title`/`error`/`active`/`disabled` as a prop name | `heading` / `danger` / `value`|`step` / `readonly` |
| Bare `<div>` for layout; raw `<button>`/`<input>` | `<col-ui>`/`<row-ui>`/`<grid-ui>`; the `*-ui` control |
| Card/drawer body not wrapped in `<section>` | `<card-ui><section>…</section></card-ui>` |
| Hardcoded `open` on `<modal-ui>`/`<drawer-ui>` | drive via `.open = true` |
| `new URL('…', import.meta.url)` literal for a corpus path | hold the path in a variable first |

Run the framework's own gates when you have the repo (`npm run check:anti-patterns`, `audit:*`), and `mcp__a2ui__check_anti_patterns` / `validate_schema` on generated markup.
