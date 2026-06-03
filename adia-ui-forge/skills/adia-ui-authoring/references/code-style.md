# AdiaUI code style — best practices

Modern AdiaUI is small, declarative, and token-driven. Most of the "bugs" agents write are bugs _against the conventions_ — bare `<div>`s where `col-ui` belongs, raw `<input>` where `input-ui` belongs, hex colors where tokens belong. The conventions are not stylistic preferences; each one corresponds to a working feature (theme switching, density modes, form association, focus rings) that breaks silently when the convention is violated.

When in doubt: look up the catalog (use the `lookup_component` MCP tool, or the consumer-side composition skill in the adia-ui-factory plugin), pick the existing primitive, wire through tokens.

Absorbed from the legacy code-bestpractices skill (now a redirect; this file replaces the daily-driver content).

---

## `<*-ui>` custom elements

Every interactive surface, form control, layout container, and content block ships as a custom element with a `-ui` suffix.

**Don't author raw HTML primitives** for anything the catalog covers. Raw `<button>` skips focus rings, density modes, theming, and the trait factory; raw `<input>` skips form association and validation propagation; raw `<div>` skips the layout primitive's spacing scale.

```html
<!-- right -->
<button-ui text="Save" variant="primary"></button-ui>
<input-ui type="email" label="Email"></input-ui>

<!-- wrong -->
<button class="btn-primary">Save</button>
<input type="email" />
```

The catalog has 90+ `*-ui` elements. Before composing, confirm via `get_component_map` (the a2ui MCP) that the one you want exists — and what its real prop names are.

## Layout primitives

Use `<col-ui>`, `<row-ui>`, `<grid-ui>`, `<stack-ui>` for layout — never a bare `<div>`. The primitives carry the project's spacing scale (`gap`, padding tokens) and respond to density / theme providers; a plain `<div>` strands content outside that system.

Pick the primitive by the axis the content flows along:

- Vertical stack of fields → `<col-ui gap="N">`
- Horizontal action cluster or info row → `<row-ui gap="N" justify="end">`
- Responsive grid → `<grid-ui cols="1 | 2 | 3 | 4">`
- Loose wrapping items → `<stack-ui gap="N">`

```html
<!-- right -->
<col-ui gap="2">
  <input-ui label="Email" type="email"></input-ui>
  <input-ui label="Password" type="password"></input-ui>
</col-ui>

<!-- wrong — manual spacing fights the density provider -->
<div style="display: flex; flex-direction: column; gap: 8px;">
  <input-ui label="Email" type="email"></input-ui>
  <input-ui label="Password" type="password"></input-ui>
</div>
```

The validator (`check_anti_patterns` → `noBareDivs`) catches this on rendered HTML. If a `<section>` has multiple direct children, wrap them in one layout primitive — `cardContentModel` flags the alternative.

### `@bp` responsive prop annotations

Layout primitives accept `@bp` (breakpoint) annotations on numeric or keyword props. Mobile-first parsing: unannotated value = base; `@bp` applies at that breakpoint and wider.

```html
<grid-ui cols="2 4@md"><!-- 2 cols base, 4 at md+ --></grid-ui>
<col-ui gap="2 4@lg"><!-- 8px gap base, 16px at lg+ --></col-ui>
<text-ui size="sm md@lg"><!-- sm at base, md at lg+ --></text-ui>
```

Subscription is lazy: a primitive only listens to the breakpoint signal when at least one prop carries `@`. Wired primitives: `grid-ui`, `col-ui`, `row-ui`, `text-ui`, `block-ui`. Source: `packages/web-components/core/responsive.js`.

## `<card-ui>` content model

The card content model is mandatory for anything resembling a block. Header carries icon / heading / description / action slots; section wraps content in a layout primitive; footer holds action rows.

```html
<card-ui>
  <header>
    <span slot="icon"><icon-ui name="users"></icon-ui></span>
    <span slot="heading" variant="section">Members</span>
  </header>
  <section>
    <col-ui gap="2"><!-- one layout primitive per section --></col-ui>
  </section>
  <footer divider>
    <button-ui slot="action" text="View All" variant="outline"></button-ui>
  </footer>
</card-ui>
```

Headings live in `<header>`, never in `<section>`. Sections contain exactly one layout primitive. Multiple direct children in `<section>` fail `cardContentModel` validation.

`<card-ui>` and `<drawer-ui>` body content must wrap in `<section>` — direct `<col-ui>` / `<row-ui>` / `<stack-ui>` / `<div>` / `<text-ui>` / `<h*>` bypass the canonical body slot, lose `--card-inset` margin, and corrupt gen-UI corpus. Use `<section bleed>` to preserve existing padding when needed. Gated by `npm run audit:card-structure` + `audit:drawer-structure`.

## `<field-ui>` for form composition

Wrap form controls in `<field-ui>`. Don't pass `[label]` as an attribute on new form controls — it's the legacy form, kept for back-compat but not extended.

```html
<!-- right -->
<field-ui label="Email" hint="We'll never share it">
  <input-ui type="email" required></input-ui>
</field-ui>

<!-- wrong (deprecated, console.warn) -->
<input-ui label="Email" type="email" required></input-ui>
```

`<field-ui>` owns the real `<label for="…">` and binds to the slotted control's `id` for proper click-to-focus — a pattern the embedded attribute can't provide. It also carries `[slot="trailing"]` / `[slot="action"]` for composition (clear button, helper actions) and an `inline` mode for stacked vs single-row layout.

For a single `check-ui` (which is its own labeled affordance), just use `<check-ui name label>` directly — wrapping it in `<field-ui inline>` produces ghost rows.

## Generated UIs through `<a2ui-root>`

Static markup written by hand uses the components directly. UIs generated from intent (LLM, agent) render through `<a2ui-root>` consuming a stream of A2UI messages or a static `doc` array.

```html
<a2ui-root data-stream-src="/api/genui-stream"></a2ui-root>
```

The runtime handles `createSurface` / `updateComponents` / `wireComponents` messages and binds `FormController` / `DataStreamController` controllers automatically. Don't roll your own message handler — the wiring lives in `@adia-ai/a2ui-runtime`.

For multi-turn refinement, pass back `state_id` from prior responses so the engine can chain through `parent_state_id`. See the **adia-ui-a2ui** skill for the operator playbook.

## Two-block `@scope` CSS

Component CSS uses a mandatory two-block `@scope` structure. Tokens go in `:where(:scope)` (zero-specificity); base styles go in `:scope`; variants and states override TOKENS only.

```css
@scope (badge-ui) {
  :where(:scope) {
    --badge-bg:     var(--a-bg-muted);
    --badge-fg:     var(--a-fg);
    --badge-radius: var(--a-radius-sm);
  }

  :scope {
    background: var(--badge-bg);
    color:      var(--badge-fg);
    border-radius: var(--badge-radius);
  }

  :scope[variant="accent"] {
    --badge-bg: var(--a-accent-bg);   /* token override only */
    --badge-fg: var(--a-accent-fg);
  }
}
```

The `:where()` wrapper around the token block is what keeps token overrides from a parent provider winning over child component defaults. Drop it and theme switching breaks. A Safari `@scope` sweep found that hover / state-bearing selectors inside the `@scope` block can fail to match in some Safari versions; if that bites, lift the rule out of the block as a plain `tagname:hover` selector.

Detailed pattern in [css-patterns.md](css-patterns.md).

## Tokens, never raw colors

Every color comes through a token. Zero `#hex` / `rgb()` / `rgba()` / `oklch()` in component CSS — the only places raw colors live are `packages/web-components/styles/colors/semantics.css` and `packages/web-components/styles/tokens.css`.

Component CSS aliases from L3 (the role × state matrix), not L2 (the family base). The L3 matrix is where state wiring lives; bypassing it strands the component outside the theme system and breaks dark mode / high-contrast modes silently.

```css
/* right — L3 alias keeps the state cascade working */
:scope[variant="accent"]:hover {
  --button-bg: var(--a-accent-bg-hover);
  --button-fg: var(--a-accent-fg-hover);
}

/* wrong — L2 stops the cascade */
:scope[variant="accent"]:hover {
  --button-bg: var(--a-accent);   /* loses theme + contrast wiring */
}
```

For text on filled accent discs (radio dots, step numerals), use `--a-chrome-light`, not `--a-accent-fg` — `accent-fg` resolves near-black in the current OKLCH derivation and disappears on saturated accent backgrounds.

Audit procedure + chrome palette in [token-contract.md](token-contract.md).

## Variants change tokens, modes change layout

A **variant** is cosmetic — color, border, shadow depth. A **mode** restructures the box — direction, grid template, display type.

Variant bodies may only contain `--component-*: var(...)` lines. They must NEVER touch `padding`, `display`, `position`, `width`, `height`, `gap`, `flex`, `grid`, `overflow`, `border-radius`. Layout-changing attributes are modes, and modes require an entry in the Sanctioned Mode Attributes table at `docs/specs/component-token-contract.md` `Modes` section.

```css
/* right — variant overrides tokens only */
:scope[variant="outlined"] {
  --button-bg:     transparent;
  --button-border: var(--a-border);
}

/* wrong — variant changes layout; this should be a mode */
:scope[variant="outlined"] {
  padding: var(--a-space-3) var(--a-space-4);
  display: flex;
}
```

## Boolean attributes default to `false`

Every Boolean prop on a component must default to `false`. If the expected default behavior is "on," the prop name is wrong — flip it.

| Right (default off, opt in)       | Wrong (default on, opt out)    |
| --------------------------------- | ------------------------------ |
| `<drawer-ui permanent>`           | `<drawer-ui closable>`         |
| `<chart-ui static>`               | `<chart-ui animate>`           |
| `<cursor-ui hide-cursor>`         | `<cursor-ui cursor>`           |
| `<carousel-ui no-pause-on-hover>` | `<carousel-ui pause-on-hover>` |

Default behavior is the absent attribute. Attributes exist to opt OUT or carry a value — never to opt INTO the expected default.

State-bearing Booleans must `reflect: true` so CSS can match `:scope[disabled]`, `:scope[selected]`, etc. Without reflection, hover / active / selected styles break silently.

Native DOM accessors (`textContent`, `innerHTML`) get clobbered if declared in `static properties` — `installProps` overrides the native setter and `el.textContent = ''` becomes a signal write, not a child-wipe. Don't declare those names in `static properties`.

## Symmetric lifecycle

Every `addEventListener` in `connected()` must be paired with a `removeEventListener` in `disconnected()`. Every timer cleared, every observer disconnected, every popover removed. Handlers must be stable `#field` arrows so `removeEventListener` finds them via reference equality.

```js
class AdiaBadge extends AdiaElement {
  #onRemove = (e) => { /* ... */ };  // stable handler

  connected() {
    this.#removeBtn?.addEventListener('click', this.#onRemove);
  }

  disconnected() {
    this.#removeBtn?.removeEventListener('click', this.#onRemove);
    this.#removeBtn = null;  // null cached refs to release GC pin
  }
}
```

Inline arrows passed to `addEventListener` look fine and leak quietly — `removeEventListener` no-ops because the new arrow has different identity. Three components in one audit cycle bit on this exact bug.

If the class extends `AdiaFormElement`, `connected()` and `disconnected()` MUST call `super.*` — `ElementInternals` registration depends on it. And declare `disconnected()` exactly once per class; the second silently overrides the first.

Full lifecycle patterns in [lifecycle-patterns.md](lifecycle-patterns.md).

## Reactivity through signals + effects

New runtime data flows use the project's `signal()` / `effect()` primitives — never parallel `CustomEvent`-only paths. The convention keeps reactivity coherent: a single read-write surface, observable by any number of consumers, integrated with the framework's effect graph.

```js
import { signal, effect } from '@adia-ai/web-components/core/reactivity';

const count = signal(0);

effect(() => {
  console.log('count is', count.value);
});

count.value = 1;  // effect re-runs
```

`CustomEvent` is fine for one-shot lifecycle notifications (a button click, a form submit). It's wrong for ongoing state that other components want to read — that wants a signal.

Custom setter `untracked()` discipline: reactive-property reads inside `set options/data/columns/...` setters that read `this.value` (via installProps getter) subscribe the caller's effect. Next `el.value = X` re-triggers it → drain loop. Wrap setter body in `untracked()`.

## `data-stream-*` for data ingestion

Universal data ingestion across the library is the `data-stream-*` attribute trait (`packages/web-components/core/data-stream.js`). Signal-backed, refcounted shared transports, supports HTTP / SSE / WS, formats JSON / CSV / TSV / JSONL / text. Use it instead of bespoke `fetch` / `EventSource` per component.

```html
<table-ui data-stream-src="/api/members"></table-ui>
<chart-ui data-stream-src="/api/metrics" data-stream-format="csv"></chart-ui>
<a2ui-root data-stream-src="/api/genui"></a2ui-root>
```

The trait dedupes connections — two components pointing at the same URL share one transport — and propagates updates through the signal graph automatically.

## Modern browser baseline

The project targets Chromium 125+, Safari 18.0+, Firefox 129+ (raised from 17.4 to 18.0 in ADR-0007 to clear the OKLCH-with-transparent red-shift bug and `:scope:state` `@scope` selector failures).

Don't propose polyfilling native APIs already at the baseline. The runtime expects native `:has()`, `@scope`, `@property`, OKLCH, `light-dark()`, `popover`, `dialog.showModal()`, `ResizeObserver`, `color-mix()`. Authoring against an older implicit floor is the source of most "but it works in Chrome" surprises.

When transparency-mixing colors, use `oklab` not `oklch` for the interpolation space — Safari < 18 had an OKLCH-with-transparent red-shift bug, and `oklab` is perceptually equivalent here:

```css
--code-active-line-bg: color-mix(in oklab, var(--a-accent-muted) 40%, transparent);
```

## Legacy avoidance

The library was renamed from `@agent-ui-kit/*` to `@adia-ai/*`; tokens went from `--n-*` to `--a-*`; the base class went from `NanoElement` to `AdiaElement`. Don't use the legacy forms in new code. Don't reference `nano-ui` in notes, commit messages, CHANGELOG entries, or any AdiaUI artifact.

```js
// right
import { AdiaElement } from '@adia-ai/web-components';
:where(:scope) { --button-bg: var(--a-accent-bg); }

// wrong
import { NanoElement } from '@agent-ui-kit/web-components';
:where(:scope) { --button-bg: var(--n-accent-bg); }
```

Other deprecated forms swept in an early cut:

- `<button-ui variant="danger">` → `color="danger"`
- `<timeline-item-ui completed>` / `<stepper-item-ui completed>` → `status="completed"`
- `<table-toolbar-ui filterable>` (default-true Boolean) → `<table-toolbar-ui no-filter>` (default-false opt-out)
- `<chat-input-ui busy>` → `loading`
- `<toast-ui variant="error">` → `variant="danger"`
- `'chat-submit'` event → `'submit'`
- `<field-ui error="…">` → message moves to the slotted control

For a wholesale migration, use the dedicated migration skill — it reads the MIGRATION GUIDE and runs the mechanical sweeps.

## Validate, always

Before declaring AdiaUI work done, walk the rule list above against the file you touched, then run the gate.

For consumer markup (HTML pages, exemplars, training data), the checks are manual + visual:

- Walk the rule list above (`*-ui` over raw HTML, layout primitives over `<div>`, card content model, no inline `style=`, no raw colors, L3 tokens, etc.).
- Run the project's lint if applicable: `npx eslint <path>`.
- Smoke the rendered output via `npm run dev` and load the touched page.

For component source under `packages/web-components/components/**`, the gate is heavier — see [authoring-cycle.md](authoring-cycle.md) Step 5 + the full release-side gate roster in the **adia-ui-release** skill's gate catalog.

## Cross-references

- [authoring-cycle.md](authoring-cycle.md) — the full 5-step authoring procedure
- [api-contract.md](api-contract.md) — prop naming, type choices, reflection policy
- [css-patterns.md](css-patterns.md) — full @scope + variant/mode CSS architecture
- [lifecycle-patterns.md](lifecycle-patterns.md) — timers, observers, popovers, listeners
- [token-contract.md](token-contract.md) — token audit procedure
- [llm-bridge.md](llm-bridge.md) — mode 6 (extend @adia-ai/llm)
- [module-promotion.md](module-promotion.md) — mode 4 (promote inline → module)
- [anti-patterns.md](anti-patterns.md) — failure-mode catalogue with file:line refs
- **adia-ui-a2ui** (sibling skill) — generator / corpus / MCP pipeline
- **adia-ui-dogfood** (sibling skill) — cross-surface visual / static QA
- the **adia-ui-factory** plugin — composition playbook for consumers building apps on the framework
