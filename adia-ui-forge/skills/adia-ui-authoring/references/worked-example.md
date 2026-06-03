# Worked Examples

Two annotated examples: a light presentation component (`<badge-ui>`) and a form-associated component (`<counter-ui>`). Copy the structure; adapt the content.

## Example 1 — Light presentation component: `<badge-ui>`

A small inline container for status labels. Supports cosmetic variants (accent/success/danger) and an optional remove button that fires a `remove` event.

### File layout

```text
packages/web-components/components/badge/
  badge.js
  badge.css
```

### `badge.js`

```javascript
import { AdiaElement } from '../../core/element.js';

/**
 * <badge-ui> — Compact inline status label.
 *
 * Props:
 *   variant    — 'neutral' | 'accent' | 'success' | 'danger' (default 'neutral')
 *   removable  — show an inline × button that fires 'remove' on click
 *
 * Events:
 *   remove — user clicked the × button (bubbles)
 */
class AdiaBadge extends AdiaElement {
  static properties = {
    variant:   { type: String,  default: 'neutral', reflect: true },
    removable: { type: Boolean, default: false,     reflect: true },
  };

  static template = () => null;

  #removeBtn = null;

  #onRemove = (e) => {
    e.stopPropagation();
    this.dispatchEvent(new CustomEvent('remove', { bubbles: true }));
  };

  connected() {
    // Lazy-append the remove button on first render when the attribute is present.
    // If authors want to control the markup, they can pre-slot their own button
    // and we skip the injection.
    if (this.removable && !this.querySelector('[data-badge-remove]')) {
      this.#removeBtn = document.createElement('button');
      this.#removeBtn.type = 'button';
      this.#removeBtn.setAttribute('data-badge-remove', '');
      this.#removeBtn.setAttribute('aria-label', 'Remove');
      this.#removeBtn.textContent = '×';
      this.appendChild(this.#removeBtn);
      this.#removeBtn.addEventListener('click', this.#onRemove);
    }
  }

  disconnected() {
    this.#removeBtn?.removeEventListener('click', this.#onRemove);
    this.#removeBtn = null;
  }
}

customElements.define('badge-ui', AdiaBadge);
export { AdiaBadge };
```

**Annotations:**

- **Class name `AdiaBadge`, tag `badge-ui`** — three-way naming.
- **`variant` default `'neutral'`** — string enum, default is the absent- attribute state. No special behavior to "opt into."
- **`removable: default false`** — Boolean false (rule 1). Reflects so CSS can match `:scope[removable]`.
- **`#removeBtn` private field** — cached DOM ref, nulled on teardown.
- **`#onRemove` stable arrow** — reference equality works for `removeEventListener`.
- **Symmetric connected/disconnected** — single listener, single removal.
- **Idempotent `connected()`** — checks `querySelector('[data-badge-remove]')` before injecting, so an author who pre-slots their own button isn't overridden.

### `badge.css`

```css
@scope (badge-ui) {
  :where(:scope) {
    /* ── Tokens ── */
    --badge-bg:         var(--a-bg-muted);
    --badge-fg:         var(--a-fg);
    --badge-border:     1px solid var(--a-border-subtle);
    --badge-radius:     var(--a-radius-sm);
    --badge-padding:    var(--a-space-1) var(--a-space-2);
    --badge-gap:        var(--a-space-1);
    --badge-font-size:  var(--a-caption-size);
  }

  :scope {
    /* ── Base styles — consume component tokens only ── */
    display: inline-flex;
    align-items: center;
    gap: var(--badge-gap);
    padding: var(--badge-padding);
    background: var(--badge-bg);
    color: var(--badge-fg);
    border: var(--badge-border);
    border-radius: var(--badge-radius);
    font-size: var(--badge-font-size);
    line-height: 1;
    white-space: nowrap;
  }

  /* ── Variants — token-only overrides ── */
  :scope[variant="accent"] {
    --badge-bg: var(--a-accent-bg);
    --badge-fg: var(--a-accent-fg);
    --badge-border: 1px solid transparent;
  }
  :scope[variant="success"] {
    --badge-bg: var(--a-success-bg);
    --badge-fg: var(--a-success-fg);
    --badge-border: 1px solid transparent;
  }
  :scope[variant="danger"] {
    --badge-bg: var(--a-danger-bg);
    --badge-fg: var(--a-danger-fg);
    --badge-border: 1px solid transparent;
  }

  /* ── Removable state ── */
  :scope[removable] > [data-badge-remove] {
    all: unset;
    cursor: pointer;
    padding: 0 var(--a-space-1);
    margin-inline-start: var(--a-space-1);
    color: inherit;
    opacity: 0.7;
    border-radius: var(--a-radius-sm);
  }
  :scope[removable] > [data-badge-remove]:hover {
    opacity: 1;
    background: color-mix(in oklab, currentColor 15%, transparent);
  }
  :scope[removable] > [data-badge-remove]:focus-visible {
    outline: 2px solid var(--a-focus-ring);
    outline-offset: 1px;
  }
}
```

**Annotations:**

- **Two blocks:** `:where(:scope)` for tokens, `:scope` for base. Variants and state third.
- **Variants override tokens only.** No `display`, `padding`, etc. in the variant bodies — they just reassign the component's token values.
- **Zero raw colors.** Every color is a token.
- **Zero raw px** — spacing via `--a-space-*`, radius via `--a-radius-*`. The only numeric literal is `1px` for the border (allowed carve-out).
- **Stem `--badge-*`** matches the scope tag `badge-ui`.
- **`color-mix()` on `currentColor`** is the idiomatic hover tint — stays theme-aware without introducing a new token.

---

## Example 2 — Form-associated component: `<counter-ui>`

A numeric input that shows value + increment/decrement buttons. Form- participating — submits a string value with the host form.

### `counter.js`

```javascript
import { AdiaFormElement } from '../../core/form.js';

/**
 * <counter-ui> — Integer counter with +/− controls. Form-associated.
 *
 * Props:
 *   value — number, default 0 (syncs to form value as string)
 *   min   — number, default null (no lower bound)
 *   max   — number, default null (no upper bound)
 *   step  — number, default 1
 */
class AdiaCounter extends AdiaFormElement {
  static properties = {
    ...AdiaFormElement.properties,
    value: { type: Number,  default: 0,    reflect: true },
    min:   { type: Number,  default: null, reflect: true },
    max:   { type: Number,  default: null, reflect: true },
    step:  { type: Number,  default: 1,    reflect: true },
  };

  static template = () => null;

  #decBtn = null;
  #incBtn = null;
  #valueEl = null;

  #onDecrement = () => this.#commit(this.value - this.step);
  #onIncrement = () => this.#commit(this.value + this.step);

  #commit(next) {
    if (this.min != null) next = Math.max(this.min, next);
    if (this.max != null) next = Math.min(this.max, next);
    if (next === this.value) return;
    this.value = next;
    this.syncValue(String(next)); // inherited from AdiaFormElement
    this.dispatchEvent(new Event('change', { bubbles: true }));
    this.render();
  }

  connected() {
    super.connected(); // registers ElementInternals — do not omit

    if (!this.querySelector('[data-counter-dec]')) {
      this.innerHTML = `
        <button type="button" data-counter-dec aria-label="Decrement">−</button>
        <span data-counter-value>${this.value}</span>
        <button type="button" data-counter-inc aria-label="Increment">+</button>
      `;
    }

    this.#decBtn   = this.querySelector('[data-counter-dec]');
    this.#incBtn   = this.querySelector('[data-counter-inc]');
    this.#valueEl  = this.querySelector('[data-counter-value]');

    this.#decBtn?.addEventListener('click', this.#onDecrement);
    this.#incBtn?.addEventListener('click', this.#onIncrement);
  }

  disconnected() {
    super.disconnected(); // unregisters form participation
    this.#decBtn?.removeEventListener('click', this.#onDecrement);
    this.#incBtn?.removeEventListener('click', this.#onIncrement);
    this.#decBtn = null;
    this.#incBtn = null;
    this.#valueEl = null;
  }

  render() {
    if (this.#valueEl) this.#valueEl.textContent = String(this.value);
  }
}

customElements.define('counter-ui', AdiaCounter);
export { AdiaCounter };
```

**Annotations:**

- **`AdiaFormElement` superclass** — inherits `name`, `disabled`, `required` etc. via the spread.
- **`super.connected()` / `super.disconnected()`** — both present. Without them, form association silently fails.
- **`min`/`max` default `null`** — no magic sentinels. `null` = "no constraint."
- **`#commit()` is the one-place-value-changes** — clamps, short-circuits on no-op, fires `change`, calls `syncValue`, triggers `render()`.
- **`syncValue(String(next))`** — inherited from `AdiaFormElement`, updates the form-submitted string representation.
- **Two stable handlers** — `#onDecrement`, `#onIncrement`. Both paired in `disconnected()`.
- **`render()` updates internal DOM** only when a reflected prop (`value`) changes and CSS selectors can't express the update (text content). CSS handles the disabled state via `:scope[disabled]`.

### `counter.css`

```css
@scope (counter-ui) {
  :where(:scope) {
    --counter-bg:         var(--a-bg);
    --counter-fg:         var(--a-fg);
    --counter-border:     1px solid var(--a-border);
    --counter-radius:     var(--a-radius);
    --counter-gap:        var(--a-space-2);
    --counter-padding:    var(--a-space-1) var(--a-space-2);
    --counter-btn-size:   var(--a-size-sm);
  }

  :scope {
    display: inline-flex;
    align-items: center;
    gap: var(--counter-gap);
    padding: var(--counter-padding);
    background: var(--counter-bg);
    color: var(--counter-fg);
    border: var(--counter-border);
    border-radius: var(--counter-radius);
  }

  :scope > [data-counter-dec],
  :scope > [data-counter-inc] {
    all: unset;
    width: var(--counter-btn-size);
    height: var(--counter-btn-size);
    display: inline-flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    border-radius: var(--a-radius-sm);
  }

  :scope > [data-counter-dec]:hover,
  :scope > [data-counter-inc]:hover {
    background: var(--a-bg-muted);
  }

  :scope > [data-counter-value] {
    min-width: 3ch;
    text-align: center;
    font-variant-numeric: tabular-nums;
  }

  /* Disabled state — inherited from AdiaFormElement */
  :scope[disabled] {
    --counter-fg: var(--a-fg-muted);
    --counter-border: 1px solid var(--a-border-subtle);
    pointer-events: none;
    opacity: 0.6;
  }
}
```

**Annotations:**

- **No variants** in this example — the component is functional, not cosmetic. All state communicated via tokens and the `[disabled]` selector.
- **`:scope > [data-*]`** for slotted-like children without `::slotted()`.
- **`pointer-events: none` + `opacity` in the disabled body** — this is allowed because `pointer-events` is an interaction property, not a layout property. Same for `cursor`.
- **`min-width: 3ch`** is a non-layout metric (character-based), not a px literal; no carve-out needed.

---

## Checklist — did this component pass?

Run the 30-second self-check from the main SKILL.md against each example:

**Attributes:**

- ✓ No Boolean `default: true`.
- ✓ No numeric sentinels (`min: null`, `max: null`).
- ✓ `attribute:` correct (or omitted where auto-conversion works).
- ✓ State-bearing Booleans reflect (`removable`, inherited `disabled`).
- ✓ No reserved-name anti-patterns.
- ✓ `-ui` tag + `Adia<Component>` class.

**CSS:**

- ✓ `@scope (component-ui)` with two blocks.
- ✓ Variants are token-only.
- ✓ Zero raw colors.
- ✓ Spacing/radius via tokens; `1px` border allowed.
- ✓ Stem matches scope tag.
- ✓ Variants consume L2 family tokens (the component-local values in `:where(:scope)` ARE the L3 aliases; overriding them in the variant body is the pattern). No direct L2 in state-change bodies.

**Lifecycle:**

- ✓ Every `addEventListener` paired.
- ✓ Stable `#field` arrows.
- ✓ `super.connected()` / `super.disconnected()` in the `AdiaFormElement` subclass.
- ✓ DOM refs nulled.
- ✓ `disconnected()` declared once.

Pass. Ship.
