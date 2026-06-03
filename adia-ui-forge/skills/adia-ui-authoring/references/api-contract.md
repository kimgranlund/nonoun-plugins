# API Contract — Props, Attributes, Reflection

Deep dive on declaring component APIs in AdiaUI. Read this when adding a new prop whose shape doesn't match any obvious pattern in the good-citizen references.

## The `static properties` block

Every `AdiaElement` subclass declares its public API as a `static properties` object. Keys are camelCase JS names; values describe type, default, reflection, and attribute mapping.

```javascript
static properties = {
  disabled:  { type: Boolean, default: false,  reflect: true },
  placeholder: { type: String,  default: '',     reflect: true },
  value:     { type: String,  default: '' },
  maxLength: { type: Number,  default: null,   reflect: true, attribute: 'max-length' },
};
```

**Field rules:**

- `type` — one of `String`, `Number`, `Boolean`, `Object`, `Array`. The runtime uses this to coerce attribute strings into typed values.
- `default` — the value the prop takes when no attribute is present AND no JS value has been assigned. For `Boolean` props, default is ALWAYS `false` (see rule 1). For numeric props, default is `0`, a real value, or `null` for indeterminate — NEVER a sentinel like `-1`.
- `reflect` — when `true`, JS property changes write back to the HTML attribute so CSS can match it. Required for every state-bearing Boolean. Usually safe to omit for large value props (long strings, big objects).
- `attribute` — explicit kebab-case mapping when the JS name doesn't auto-convert cleanly. `camelCase` → `camel-case` automatic; override via `attribute: 'max-length'` when you want non-default behavior.

## The `attr:` silent-typo trap

A real bug caught in iteration 4:

```javascript
// BROKEN — silent
allowHalf: { type: Boolean, default: false, reflect: true, attr: 'allow-half' },

// FIXED
allowHalf: { type: Boolean, default: false, reflect: true, attribute: 'allow-half' },
```

`attr:` is not a recognized key. The mapper ignores it. The default auto-conversion (`allowHalf` → `allow-half`) happens to produce the same result, so the bug hides — until someone changes the prop name and notices the attribute never wired.

Use `attribute:` verbatim. If you think you're writing `attr:`, stop and correct it before saving.

## Boolean prop naming — the flip rule

AdiaUI conventions require `default: false` on all Booleans. The naming follows:

| Intended default behavior | Wrong name (default:true) | Right name (default:false) |
| --- | --- | --- |
| Modal can be dismissed | `closable` | `permanent` |
| Skeleton animates | `animate` | `static` |
| Stream shows blinking cursor | `cursor` | `hideCursor` |
| Chart shows average line | `average` | `hideAverage` |
| Toggle group allows multi-select | `multiple` | `single` |
| Swiper pauses on hover | `pause-on-hover` | `noPauseOnHover` |

**Naming patterns:**

- `permanent` / `static` / `readonly` — describes the non-default state positively.
- `no*` / `hide*` / `disable*` — prefixes for "opt-out of a default."

**Don't write:**

- `enabled` (invert to `disabled`), `visible` (invert to `hidden`) — these clash with standard HTML attribute vocabulary.
- Double-negatives like `unhide` or `dontSkip`.

## Numeric props — `null` over sentinels

Indeterminate, unknown, or "not yet set" numeric state uses `null`, not `-1` or `Infinity`:

```javascript
// BROKEN — `-1` is a magic sentinel
value: { type: Number, default: -1, reflect: true }
// Consumer: if (this.value !== -1) { ... }

// FIXED
value: { type: Number, default: null, reflect: true }
// Consumer: if (this.value != null) { ... }
```

The `progress-ui` component carried `-1` for "indeterminate" for a long time. Branching on a specific number is fragile — someone assigns `-1` meaningfully later and the indeterminate check breaks silently. `null` is unambiguous.

**Back-compat coercion is allowed:**

```javascript
set value(v) {
  if (v === -1) v = null; // legacy input coercion, remove in a future cycle
  this._value = v;
}
```

## Reserved-name anti-patterns

These prop names collide with HTML semantics, framework-wide conventions, or create ambiguity in audit. Pick alternatives:

### `title`

HTML's global `title` attribute is the browser tooltip. Using `title` on a custom element makes any custom-element heading a tooltip by default, which is almost never intended. Use `heading`.

### `active` on a parent component

Children can have per-item `active` (a Boolean describing that item's state). Parents use `value` (for a selection) or `step` (for an index into a series).

- `<timeline-item-ui active>` — OK, per-item Boolean state.
- `<timeline-ui step="3">` — correct: parent holds the index.
- `<timeline-ui active="3">` — wrong: `active` shouldn't carry a non-boolean payload.

### `error` as a variant

Reserve `error` for validation state (`[error]` on form inputs matches ARIA patterns). For visual emphasis meaning "destructive/negative," use `danger`, matching the semantic family (`--a-danger-*` tokens).

```html
<!-- wrong -->
<tag-ui variant="error">Failed</tag-ui>

<!-- right -->
<tag-ui variant="danger">Failed</tag-ui>

<!-- separate use -->
<input-ui error>Please enter a valid email</input-ui>
```

### `disabled` on a non-form component

`disabled` has form-participating semantics — it removes the element from the tab order, blocks submission, etc. On a non-form component (a diagram, a toolbar, a noodle editor), use `readonly`:

- `<input-ui disabled>` — correct: input is form-participating.
- `<noodles-ui readonly>` — correct: diagram is read-only, not form-disabled.

### `multiple` with exclusion semantics

`<select multiple>` in HTML means "allow multiple selections." A prop named `multiple` means "multi-select is the default." If you want single-select as the default behavior:

```html
<!-- wrong: implies multiple was default, which violates Boolean-false rule -->
<toggle-group-ui multiple>...</toggle-group-ui>

<!-- right: single-select is the opt-out, matches Boolean-false -->
<toggle-group-ui single>...</toggle-group-ui>
```

## Three-way name consistency

The component has three names that must agree:

- **File path:** `packages/web-components/components/foo/foo.js`
- **Class name:** `class AdiaFoo extends AdiaElement`
- **Custom element tag:** `customElements.define('foo-ui', AdiaFoo)`

A fourth consistency requirement: the CSS file at `packages/web-components/components/foo/foo.css` uses `@scope (foo-ui)`.

## Extending `AdiaFormElement`

Form-participating components extend `AdiaFormElement` (which extends `AdiaElement`) and get `ElementInternals` wiring, form-reset handling, and `.form` / `.labels` / `.validity` accessors for free.

```javascript
import { AdiaFormElement } from '../../core/form.js';

class AdiaInput extends AdiaFormElement {
  static properties = {
    ...AdiaFormElement.properties, // inherit name, value, disabled, required, etc.
    placeholder: { type: String, default: '', reflect: true },
  };

  connected() {
    super.connected(); // MUST call — registers ElementInternals
    // ...
  }

  disconnected() {
    super.disconnected(); // MUST call
    // ...
  }

  // Override `value` getter/setter if the form-submitted value differs
  // from the stored one
  get value() { return this._value ?? ''; }
  set value(v) { this._value = v; this.syncValue(String(v)); }
}
```

Key details:

- **Always `super.connected()` and `super.disconnected()`** — without them, form-association doesn't register.
- **`this.syncValue(str)`** — call this whenever the value changes to update the form-submitted string. Accepts a string.
- **Inheriting properties** — spread `AdiaFormElement.properties` into your own `static properties` so you don't re-declare `name`, `disabled`, `required`.

## Event conventions

- Bubble custom events: `new CustomEvent('foo', { bubbles: true, detail: {...} })`.
- Reuse standard events where possible: `input`, `change`, `submit`, `focus`.
- Custom event names are kebab-case: `cot-toggle`, `noodle-connected`.
- When dispatching state changes, fire `input` during interaction and `change` on commit. Matches native form semantics.

## When to add the `render()` method

`render()` runs when reflected attributes change. Use it to update internal DOM that depends on props:

```javascript
render() {
  if (this.#textareaEl) {
    this.#textareaEl.disabled = this.disabled;
    this.#textareaEl.placeholder = this.placeholder;
  }
}
```

Rule of thumb: if CSS can do the work via an attribute selector (`:scope[disabled] { ... }`), prefer CSS. Reserve `render()` for propagating state into child inputs, recalculating positions, or reflecting data changes that attribute selectors can't express.
