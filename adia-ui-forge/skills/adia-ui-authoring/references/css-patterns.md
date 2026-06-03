# CSS Patterns — Two-Block `@scope`, Variants, Modes, Tokens

Deep dive on AdiaUI's CSS architecture. Read when authoring a new component stylesheet, adding a variant that feels layout-shaped, or editing the token block of an existing component.

## The two-block `@scope` structure

Every component CSS file has exactly this shape:

```css
@scope (component-ui) {
  :where(:scope) {
    /* ── Tokens (zero-specificity declarations) ── */
    --component-bg:     var(--a-bg);
    --component-fg:     var(--a-fg);
    --component-border: 1px solid var(--a-border-subtle);
    --component-radius: var(--a-radius);
    /* ... */
  }

  :scope {
    /* ── Base styles — consume component tokens only ── */
    box-sizing: border-box;
    display: inline-flex;
    align-items: center;
    padding: var(--a-space-2) var(--a-space-3);
    background: var(--component-bg);
    color: var(--component-fg);
    border: var(--component-border);
    border-radius: var(--component-radius);
  }

  /* ── Variants / states (token-only overrides) ── */
  :scope[variant="outlined"] {
    --component-bg: transparent;
    --component-border: 1px solid var(--a-border);
  }

  :scope[disabled] {
    --component-bg: var(--component-bg-disabled);
    --component-fg: var(--component-fg-disabled);
    pointer-events: none;
  }
}
```

**Why two blocks?**

- `:where(:scope)` has specificity `(0,0,0)`. Consumer overrides, theme providers, and nested surface rules all beat it cleanly.
- `:scope` has specificity `(0,1,0)` — enough to beat `:where()` inside the same file, but low enough to compose across components without `!important`.
- The separation enforces the rule visually: tokens in the first block, styles in the second. A reviewer can spot a violation at a glance.

**Common mistake:** collapsing both into one `:scope` block.

```css
/* WRONG — tokens and styles interleaved */
:scope {
  --component-bg: var(--a-bg);
  background: var(--component-bg);
  display: flex;
}
```

When a parent tries to override `--component-bg`, specificity beats them. The zero-specificity layer is the contract.

## Variants vs modes — the decision tree

The rule: **variants change tokens; modes change layout.**

```text
Does your [attribute=value] need to change any of:
  padding, display, position, width, height, margin,
  gap, flex, grid, overflow, border-radius, flex-direction?

                    ├── YES → it's a MODE
                    │         Add it to the Sanctioned Mode Attributes
                    │         table in docs/specs/component-token-contract.md
                    │         with a one-line justification.
                    │
                    └── NO  → it's a VARIANT
                              Body may contain only --component-*: var(...) lines.
```

**Approved mode attributes** (as of the most recent contract update):

- `progress-ui[variant="spinner"]` — size and flex centering change
- `code-ui[inline]` — inline vs block display
- `divider-ui[vertical]` — flex-direction, width ↔ height swap
- `tabs-ui[orientation="vertical"]` — flex-direction swap
- `input-ui / textarea-ui / select-ui / slider-ui[data-direction="row"]` — grid rewrite
- `toast-ui[position="..."]` — fixed positioning corner
- `nav-ui / pane-ui / cot-ui[collapsed]` — width/height collapse
- `list-ui[divider]` — gap:0 for visual seam
- `description-list-ui[layout="inline"]` — grid-template change
- `chart-ui[type="sparkline"|"segments"]` — strip vs full layout
- `chat-ui[data-role="user"|"assistant"]` — bubble alignment
- `timeline-ui[orientation="horizontal"]` — flex-direction swap
- `timeline-ui[mode="steps"]` — flex-direction + step-counter layout
- `button-ui[block]` — block-fill with `display: flex; width: 100%`
- `pagination-ui[variant="button"]` — square 1:1 page buttons

This list is the single source of truth. If your mode isn't here, add it. If adding would feel weird, that's a signal the "mode" is actually a **sibling component** — prefer `code-inline-ui` over `code-ui[inline]` unless the attribute genuinely toggles one surface between two states of the same thing.

## Font-family floor — text-bearing primitives must anchor to a token

A primitive that renders text must NOT rely on `font: inherit` / `font-family: inherit` alone. Those carry **no default** — the primitive inherits whatever the host page sets, so a consumer page with a broken or serif `font-family` (a dead token, a missing `--a-font-family`, a serif host document) makes the primitive's labels render in UA serif while token-anchored siblings (`text-ui`) stay correct. A confusing same-page split — the exact bug behind an embedded-app `<segmented-ui>` serif regression (25 primitives shared the flaw).

**Rule:** anchor `font-family` to a token, the way `text-ui` does:

```css
@scope (foo-ui) {
  :where(:scope) {
    --foo-font-family-default: var(--a-font-family-ui);  /* UI-control font */
  }
  :scope {
    font: inherit;                                        /* keep — resets style/variant/leading */
    font-family: var(--foo-font-family, var(--foo-font-family-default));
  }
}
```

- `font: inherit` may stay (it still resets `font-style` / `font-variant` / `line-height`); the `font-family` longhand AFTER it is the floor.
- Floor to `--a-font-family-ui` for chrome/controls (or `--a-body-family` for prose-like text, as `text-ui` does). The `var(--foo-font-family, …)` first arg is the per-component override hook.
- For composite controls (`select` / `combobox` / `tags-input` / `table`), floor the **host `:scope`** — internal fields/options/cells inherit it.
- **Exception:** a contextual editor (`inline-edit`) or an optional centered label (`spinner`) SHOULD inherit to match surrounding content — do NOT floor those (they're allowlisted in the audit).

**Enforced by** `npm run audit:font-family-floor:strict` (`scripts/dev/audit-font-family-floor.mjs`): flags any component CSS with `font: inherit` / `font-family: inherit` and no `font-family: var(…)` floor, plus dead `var(--a-font)` usage.

## Token consumption — L3 over L2

The token stack has four layers:

- **L1 (primitives):** raw scale values — `--a-blue-500`, `--a-gray-100`.
- **L2 (family semantics):** role tokens per family — `--a-accent`, `--a-danger`, `--a-success`, `--a-info`, `--a-warning`.
- **L3 (state × role matrix):** `--a-<family>-{bg,fg,border}-{rest,hover,active,selected,disabled,invalid}` — every family has a full matrix.
- **L4 (component tokens):** `--component-*`, defined in `:where(:scope)`.

**Rule:** L4 aliases L3, not L2.

```css
/* RIGHT — component token aliases from L3 */
:where(:scope) {
  --button-bg:         var(--a-accent-bg);
  --button-bg-hover:   var(--a-accent-bg-hover);
  --button-fg:         var(--a-accent-fg);
  --button-fg-hover:   var(--a-accent-fg-hover);
}

:scope[variant="danger"] {
  --button-bg:         var(--a-danger-bg);
  --button-bg-hover:   var(--a-danger-bg-hover);
}

/* WRONG — variant body consumes L2 directly */
:scope[variant="danger"]:not([disabled]):hover {
  --button-fg: var(--a-danger);      /* ← L2 */
  --button-border: var(--a-danger);  /* ← L2 */
}
```

**Why:** L3 exists so state wiring lives in ONE place. When you bypass L3, the state doesn't cascade through theme × scheme × contrast × density overrides correctly. A user enabling high-contrast mode won't see the hover state you skipped.

This was a real bug in `button.css` caught in a final audit pass.

## Raw values — what's allowed

- **Colors:** zero raw values in component CSS files.
  - No `#hex`, `rgb()`, `rgba()`, `oklch()`, `hsl()`, named colors (`red`, `white`). Every color goes through a token.
  - Exception: `styles/colors/semantics.css` and `styles/tokens.css` — those ARE the raw values.

- **px values:**
  - ≤ 2px: allowed for `stroke-width`, `border-width`, hairline details. Comment not required.
  - ≥ 3px: forbidden in component base styles. Use `var(--a-space-*)`.
  - Exception: component-intrinsic constants (e.g. a port-dot diameter, an icon size that must match a specific SVG coordinate). Each such literal needs a one-line comment justifying why.

Example carve-out:

```css
:where(:scope) {
  /* Component-intrinsic visual constant; no --a-space-* equivalent */
  --noodles-port-size: 10px;
}
```

## Component token naming

`--<tag-stem>-<prop>`. The stem is the custom-element tag with `-ui` removed.

- `button-ui` → `--button-bg`, `--button-fg`, `--button-radius`.
- `chat-input-ui` → `--chat-input-bg`, `--chat-input-gap`.
- `timeline-item-ui` → `--timeline-item-dot-size`.

**Files with multiple `@scope` blocks:** each scope uses its own stem.

```css
/* layout.css contains three components */

@scope (col-ui) {
  :where(:scope) { --col-gap: var(--a-gap-md); }
  :scope { gap: var(--col-gap); }
}

@scope (row-ui) {
  :where(:scope) { --row-gap: var(--a-gap-md); }
  :scope { gap: var(--row-gap); }
}

@scope (stack-ui) {
  :where(:scope) { --stack-gap: var(--a-gap-md); }
  :scope { gap: var(--stack-gap); }
}
```

A cursory check might flag `--col-*` as "wrong" because the file is named `layout.css`. It's not wrong — the **scope tag** determines the stem, not the filename.

## Slot styling without `::slotted()`

AdiaUI is light-DOM. Slotted children are just children. Style them with attribute selectors:

```css
/* RIGHT */
:scope > [slot="icon"] {
  margin-inline-end: var(--component-gap);
}

:scope > header > [slot="heading"] {
  font-weight: var(--a-font-weight-strong);
}

/* WRONG — ::slotted() is for shadow DOM */
::slotted([slot="icon"]) { ... }
```

## `@property` for animated custom properties

When a custom property needs to participate in CSS transitions or animations, declare it with `@property` so the browser can interpolate it:

```css
@property --_card-loading-angle {
  syntax: '<angle>';
  initial-value: 0deg;
  inherits: false;
}

@scope (card-ui) {
  /* ... */
  @keyframes card-loading-spin {
    to { --_card-loading-angle: 360deg; }
  }
}
```

The `--_` prefix marks it as internal to the component. `@property` is at the top of the file, outside the `@scope` block.

## Nested surface layering

When a component can contain itself (cards inside cards), step the background up one canvas level per nesting depth:

```css
:scope card-ui                        { --card-bg: var(--a-canvas-2); }
:scope card-ui card-ui                 { --card-bg: var(--a-canvas-3); }
:scope card-ui card-ui card-ui          { --card-bg: var(--a-canvas-4); }
```

The `:scope card-ui` specificity `(0,1,1)` beats the inner scope's `:where(:scope)` initializer `(0,0,0)`, so the nested card picks up the bumped canvas. No JavaScript required.

## `:has()` — constrain to direct children when gating on slots

When a component uses `:has([slot="X"])` to toggle a layout (e.g. activate a grid when a slotted child is present), the selector matches any descendant. That collides with composite children like `<avatar-ui>` which owns an internal `<icon-ui slot="icon">` — dropping an avatar into a header you intended to render without an icon column will falsely activate it.

**Rule:** gate layout on `:has(> [slot="X"])`, not `:has([slot="X"])`.

```css
/* WRONG — matches nested <icon-ui slot="icon"> inside an <avatar-ui> */
> header:has([slot="icon"]) { grid-template-columns: max-content 1fr; }

/* RIGHT — only activates for a direct-child [slot="icon"] */
> header:has(> [slot="icon"]) { grid-template-columns: max-content 1fr; }
```

This applies everywhere layout flips on slot presence:

```css
/* card-ui / drawer-ui header grid — all :has() clauses are direct-child */
> header:has(> [slot="icon"]):has(> :is([slot="action"], [slot="close"])) {
  grid-template-columns: max-content 1fr max-content;
}
> header:has(> [slot="icon"]):not(:has(> :is([slot="action"], [slot="close"]))) {
  grid-template-columns: max-content 1fr;
}
```

**Recognition:** if a container uses `:has(…)` to decide whether a layout column exists, and any sibling component may own an internal slotted descendant with the same name, the selector is wrong. Tighten to `:has(> …)`.

**Real fix:** card-ui and drawer-ui both had un-scoped `:has()` selectors; a `<avatar-ui slot="icon">` inside a header triggered the grid twice (once for the avatar, once for the icon-ui inside it), collapsing the content column to zero. Tightened in both files to `:has(> [slot="…"])`.

## Conditional-render parts defeat `:scope >` (the `display:contents` wrapper)

The template engine wraps every **conditional render branch** — a `${cond ? … : null}` (or `?` / `.map()`) expression — in a `<span style="display:contents">`. The span generates no box (invisible in layout) but is a real DOM node, so a conditionally-rendered part is a **grandchild** of `:scope`, not a direct child. A `:scope > [data-part="X"]` rule on that part silently matches nothing — no error, passes `components --verify`, and renders un-styled only in a live browser (happy-dom won't catch it).

**Rule:** use a **descendant** combinator for any conditionally-rendered part; keep `:scope >` only for parts that render unconditionally.

```css
/* WRONG — empty-state lives behind a `${isEmpty ? … : null}` branch,
   so it's wrapped in <span style="display:contents"> and never matched */
:scope > [data-part="empty"] { display: grid; place-items: center; }

/* RIGHT — descendant combinator survives the display:contents wrapper */
:scope [data-part="empty"] { display: grid; place-items: center; }

/* static parts (always rendered) stay direct children */
:scope > [data-part="header"] { … }
```

Recurring class (integrations-page empty-state, onboarding-checklist complete CTA — bug-51 / bug-53). Full failure entry + recognition heuristic: [anti-patterns.md](anti-patterns.md) AP-S6.

## Sticky header/footer inside a flex-column scroll container

When a card-like container (drawer-ui, pane-ui, full-height cards) needs a header + scrolling body + footer where header and footer pin to the top/ bottom during scroll, use `position: sticky` on the pinned children rather than splitting the container into separate scroll regions:

```css
> [slot="panel"] {
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  overflow-y: auto;              /* one scroll region */
  background: var(--component-bg);
}

[slot="panel"] > [slot="header"] {
  position: sticky;
  top: 0;
  background: var(--component-bg);  /* opaque so content scrolls under */
  z-index: 1;
  flex-shrink: 0;
}

[slot="panel"] > [slot="footer"] {
  position: sticky;
  bottom: 0;
  background: var(--component-bg);
  z-index: 1;
  flex-shrink: 0;
}

[slot="panel"] > [slot="body"]:last-of-type {
  flex: 1 0 auto;  /* last body takes slack so footer hugs bottom */
}
```

**Why this over a dedicated scroll wrapper:**

- No extra DOM element required.
- Multiple `[slot="body"]` siblings stack naturally — the author can put dividers between sections, include sub-headers, etc.
- Sticky works inside `display: flex` flex-columns in all modern browsers.

**Gotcha:** the sticky background must be opaque. If the header is transparent, content scrolls visibly underneath. Match the sticky element's `background` to the panel's `--*-bg` token.

## Anti-patterns specific to CSS

- **BEM class syntax** — `.component--variant__element`. Not allowed. Slot attribute selectors replace this pattern.
- **`::part()` / `::slotted()`** — shadow DOM syntax. AdiaUI is light DOM.
- **Global selectors inside `@scope`** — `body { ... }`, `html { ... }`, `* { ... }`. The scope is the component; don't reach outside.
- **`!important`** — ever. If you need it, the specificity layering is wrong. Fix the layering.
- **Setting tokens at `:root`** — tokens scoped to a component belong in `:where(:scope)`. Only cross-component semantic tokens live in `:root` / `styles/colors/semantics.css`.
