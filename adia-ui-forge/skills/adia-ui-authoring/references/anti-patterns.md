# Anti-Pattern Catalogue

Every entry here is a real bug caught in the framework's 5-iteration coherence audit. They're named and cited so future authors recognize the _shape_ of the mistake before repeating it.

Organized by axis.

---

## API / Attributes

### AP-01 · `default: true` on a Boolean prop

```javascript
// WRONG
closable: { type: Boolean, default: true, reflect: true }
```

**What went wrong:** the component did something by default, and the prop named the default behavior. Users couldn't opt out by just setting the attribute — they had to pass `closable="false"` which doesn't even work for Boolean attributes (presence = true; absent = false is the HTML model).

**Fix:** flip the name. Default `true` behavior = name the prop for the opt-out.

| Before | After |
| --- | --- |
| `modal-ui[closable]` (default `true`) | `modal-ui[permanent]` (default `false`) |
| `skeleton-ui[animate]` | `skeleton-ui[static]` |
| `stream-ui[cursor]` | `stream-ui[hideCursor]` |
| `chart-ui[average]` | `chart-ui[hideAverage]` |
| `toggle-group-ui[multiple]` | `toggle-group-ui[single]` |
| `swiper-ui[pause-on-hover]` | `swiper-ui[noPauseOnHover]` |

**Recognition:** if you find yourself writing `default: true` in a `static properties` block, stop — the name is wrong.

### AP-02 · Magic-value sentinel instead of `null`

```javascript
// WRONG
value: { type: Number, default: -1, reflect: true } // -1 means "indeterminate"
```

**What went wrong:** `-1` is a magic number. Consumers branch on `this.value !== -1`, which breaks the day someone assigns `-1` to mean something else, or decides `-0.5` is also indeterminate.

**Fix:** `null` for indeterminate. Check `value == null`.

```javascript
value: { type: Number, default: null, reflect: true }
```

**Real fix:** `progress-ui.value` carried `-1` for months; fixed with a back-compat coercion (`if (v === -1) v = null`) to avoid breaking existing consumers.

### AP-03 · `attr:` silent typo

```javascript
// WRONG — silently ignored
allowHalf: { type: Boolean, default: false, reflect: true, attr: 'allow-half' }
```

**What went wrong:** the mapper looks for `attribute:`, not `attr:`. The typo is silently dropped. The kebab-case HTML attribute _happens_ to auto- convert to `allow-half` so the bug hides — until someone renames `allowHalf` and the attribute never wires.

**Fix:** `attribute:` always.

**Real fix:** `rating-ui` had this typo for several commits. Found by grep in axis-1 audit.

### AP-04 · `title` as a prop name

```html
<cot-ui title="Analyzing intent"></cot-ui>
```

**What went wrong:** HTML's global `title` attribute is the browser-native tooltip. A custom element with a `title` attribute gets a tooltip on hover by default, which is almost never intended.

**Fix:** rename to `heading` (or something domain-specific that doesn't collide).

### AP-05 · `active` on a parent component

```html
<timeline-ui active="3">   <!-- parent taking an index -->
  <timeline-item-ui active>  <!-- child per-item state -->
```

**What went wrong:** `active` on the parent carries a non-boolean payload (an index or a selection). The name `active` implies a Boolean.

**Fix:** rename by intent:

- Parent holds a current index → `step` (e.g. `timeline-ui[step="3"]`)
- Parent holds a selection → `value` (e.g. `inspector-ui[value="item-42"]`)
- Child Boolean state stays as `active` — that's fine.

### AP-06 · `error` as a variant

```html
<tag-ui variant="error">Failed</tag-ui>
```

**What went wrong:** `error` is the validation-state family (`[error]` on inputs; `--a-error-*` tokens). A variant named `error` conflates visual variant with validation state.

**Fix:** use the semantic-family name for the variant: `danger` (matches `--a-danger-*` tokens). Reserve `error` for validation state.

### AP-07 · `disabled` on a non-form component

```html
<noodles-ui disabled>...</noodles-ui>  <!-- diagram, not form-participating -->
```

**What went wrong:** `disabled` has specific form semantics (removed from tab order, blocks submission). On a non-form component, the implicit meaning is "read-only interaction."

**Fix:** `readonly` — matches the actual intent.

### AP-08 · `multiple` with exclusion semantics

```html
<toggle-group-ui multiple>  <!-- default: multi-select -->
```

**What went wrong:** implies multi-select is the default (matches HTML's `<select multiple>`). But then the prop violates the Boolean-default-false rule (AP-01).

**Fix:** negate to `single` so absent-attribute = multi-select default = Boolean false.

```html
<toggle-group-ui>         <!-- default: multi-select -->
<toggle-group-ui single>  <!-- opt-in to single-select -->
```

---

## Tokens

### AP-T1 · Variant body consumes L2 directly

```css
/* WRONG — button.css */
:scope[variant="danger"]:not([disabled]):hover {
  --button-fg: var(--a-danger);      /* L2 */
  --button-border: var(--a-danger);  /* L2 */
}
```

**What went wrong:** the variant bypassed the L3 state matrix. When a user enables high-contrast mode, the contrast-mode overrides on `--a-danger-fg-hover` don't reach this component — it's reading the flat L2 token instead of the stateful L3 one.

**Fix:** alias from the L3 matrix:

```css
:scope[variant="danger"]:not([disabled]):hover {
  --button-fg: var(--a-danger-fg-hover);
  --button-border: var(--a-danger-border-hover);
}
```

Or, if the component already defines state-aware tokens in `:where(:scope)`, reuse those:

```css
:scope[variant="danger"]:not([disabled]):hover {
  --button-fg: var(--button-fg-hover);
  --button-border: var(--button-border-hover);
}
```

### AP-T2 · Raw hex / rgb / oklch in component CSS

```css
/* WRONG */
:scope {
  background: #f4f4f5;
  color: oklch(0.2 0.01 264);
}
```

**What went wrong:** theme/scheme/contrast switching can't reach a hardcoded color. The component breaks silently in dark mode.

**Fix:** consume tokens. Always.

### AP-T3 · Raw px ≥ 3 without justification

```css
/* WRONG — 12px is neither a stroke nor intrinsic */
:scope { padding: 12px; }
```

**Fix:** use the spacing scale.

```css
:scope { padding: var(--a-space-3); }
```

**Allowed carve-out** (with comment):

```css
:where(:scope) {
  /* Component-intrinsic visual constant; no --a-space-* equivalent */
  --noodles-port-size: 10px;
}
```

### AP-T4 · Component token name mismatches scope

```css
/* WRONG — button.css */
@scope (button-ui) {
  :where(:scope) {
    --btn-bg: var(--a-accent-bg);  /* ← stem mismatch */
  }
}
```

**Fix:** stem matches the scope's tag-stem exactly.

```css
@scope (button-ui) {
  :where(:scope) {
    --button-bg: var(--a-accent-bg);
  }
}
```

---

## CSS Patterns

### AP-S1 · Variant body sets layout properties

```css
/* WRONG — pagination.css (pre-fix) */
:scope[variant="button"] [slot="nav"] button {
  width: var(--pagination-button-size);
  height: var(--pagination-button-size);
  padding: 0;
  border-radius: var(--pagination-radius);
}
```

**What went wrong:** `variant="button"` changes the layout (square buttons with specific dimensions) — that's a mode, not a variant.

**Fix:** add `pagination-ui[variant="button"]` to the Sanctioned Mode Attributes table in `docs/specs/component-token-contract.md`. Document the layout change as intentional.

Alternative: refactor to make the attribute cosmetic — if possible.

### AP-S2 · Single-block `:scope` (tokens and styles interleaved)

```css
/* WRONG — missing the :where(:scope) token block */
@scope (button-ui) {
  :scope {
    --button-bg: var(--a-accent-bg);
    background: var(--button-bg);
    display: inline-flex;
  }
}
```

**What went wrong:** tokens inherit `:scope`'s `(0,1,0)` specificity. Parent overrides fail because they can't out-specify.

**Fix:** two blocks.

### AP-S3 · `::slotted()` in light-DOM component

```css
/* WRONG — shadow DOM syntax */
::slotted([slot="icon"]) { margin-inline-end: var(--gap); }
```

**Fix:** attribute selector on child.

```css
:scope > [slot="icon"] { margin-inline-end: var(--component-gap); }
```

### AP-S4 · `!important`

Ever. If you need it, specificity is wrong somewhere. Fix the layering.

### AP-S5 · Inline `grid-template-columns` for asymmetric splits

```html
<!-- WRONG — escape hatch that bypasses the grid-ui vocabulary -->
<grid-ui gap="4" style="grid-template-columns: 2fr 1fr">
  <card-ui>Chart</card-ui>
  <card-ui>Sidebar</card-ui>
</grid-ui>
```

**What went wrong:** the inline style works visually but opts out of the component's attribute API. It doesn't reflect to `[style]`-based selectors, doesn't compose with theme overrides, and reads as a local hack when agents scan the page for grid conventions. Every inline style is a precedent the next author cargo-cults.

**Fix:** use `grid-ui[columns="N"]` plus `[span="M"]` on the children. The component ships column variants 1-6, auto-fill, auto-fit, and a per-child `span="2|3|4|5|6|full"` attribute. Compose a 2:1 split as `columns="3"` + the wide child gets `span="2"`; compose a 3:2 split as `columns="5"` + `span="3"` + `span="2"`.

```html
<!-- RIGHT — 2:1 via columns=3 and a span=2 child -->
<grid-ui columns="3" gap="4">
  <card-ui span="2">Chart</card-ui>
  <card-ui>Sidebar</card-ui>
</grid-ui>

<!-- RIGHT — 3:2 via columns=5 and span=3 + span=2 -->
<grid-ui columns="5" gap="4">
  <card-ui span="3">Overview</card-ui>
  <card-ui span="2">Recent Sales</card-ui>
</grid-ui>
```

**Recognition:** `style="grid-template-columns: …"` anywhere in a page is a signal that either (a) the author doesn't know the `span` attribute exists, or (b) the ratio truly can't be expressed in columns 1-6. The second case is rare — most asymmetric splits approximate cleanly to `3:1`, `2:1`, `3:2`, or `4:1`. If the ratio genuinely can't be expressed, it probably should become a separate layout primitive with a named attribute rather than live as an inline style.

**Real fix:** admin-dashboard had `style="grid-template-columns: 7fr 5fr"` and `"2fr 1fr"`, analytics-dashboard had one `"2fr 1fr"`. Replaced with `columns="5" span="3"+"2"` and `columns="3" span="2"+default` respectively; the 7:5 ratio shifted to 3:2 (60:40 vs 58:42) — imperceptible visually, a win structurally.

### AP-S6 · `:scope >` child combinator on a conditionally-rendered part

```css
/* WRONG — [data-part="empty"] is rendered behind a `${isEmpty ? … : null}` branch */
:scope > [data-part="empty"] { display: grid; place-items: center; }
```

**What went wrong:** the template engine wraps every conditional render branch — `${cond ? … : null}` (also `?` / `.map()`) — in a `<span style="display:contents">`. That span is a real DOM child, so the conditionally-rendered element is a _grandchild_ of `:scope`, not a direct child. `display:contents` removes the span from layout but NOT from selector matching, so `:scope > [data-part="empty"]` matches nothing and the rule silently no-ops — no error, passes `components --verify`, looks fine in happy-dom. Only a live render shows the un-styled block.

**Fix:** use a **descendant** combinator for any conditionally-rendered part; keep `:scope >` only for parts that render unconditionally (those stay direct children).

```css
/* RIGHT — descendant combinator survives the display:contents wrapper */
:scope [data-part="empty"] { display: grid; place-items: center; }
:scope > [data-part="header"] { … }   /* static part — child combinator OK */
```

**Recognition:** a `[data-part]` rule that "doesn't apply" though the markup looks right, on a part rendered inside a `${cond ? … : null}` / `?` / `.map()` branch. Inspect the live DOM — a `<span style="display:contents">` wrapping the part confirms it. **Recurring class:** integrations-page empty-state, onboarding-checklist complete-CTA, and earlier sightings (bug-51, bug-53). Positive-guidance version: [css-patterns.md](css-patterns.md) §"Conditional-render parts defeat `:scope >`".

**Real fix:** integrations-page.css + onboarding-checklist.css had `:scope > [data-part]` on conditionally-rendered parts (empty-state / complete CTA); the layout grid and the separating margin silently dropped. Converted those rules to descendant combinators.

### AP-S7 · `align-self: stretch` to vertically center a fixed-height flex child

```css
/* WRONG — stretch can't size a child that carries a definite height */
[slot="field"] > [slot="trailing"] { align-self: stretch; }   /* a 20px <kbd-ui> pins to the TOP */
```

**What went wrong:** a flex item with `align-self: stretch` **and** a definite cross-axis size (`height` / `block-size`) does not stretch — the explicit size wins and the item positions at **flex-start** (top), not center. A `<kbd-ui>` (`height: 1.25rem`) in a 30px chrome sat ~4px high. `stretch` only sizes auto-height items; for a fixed-height child it silently degrades to top-alignment. A sibling `<button-ui>` looked fine only because it had no blocking height and genuinely filled the chrome (center vs. stretch identical for it).

**Fix:** to vertically center a row of mixed-height affordances, use `align-self: center` and let each child keep its own token height.

```css
/* RIGHT — center keeps each child's intrinsic height on the vertical center */
[slot="field"] > [slot="trailing"] { align-self: center; }
```

**Recognition:** a fixed-height inline affordance (kbd / icon / badge) hugging the top of a taller flex container while a full-height sibling looks correct — suspect `align-self: stretch` on a mixed-height row.

**Real fix:** input-ui's leading/trailing affordance slots used `align-self: stretch`; the ⌘K `<kbd-ui>` hint sat 4px high. `center` fixed it and let `<button-ui>` children honor their own `--button-height` token (bug-60).

---

## JS Lifecycle

### AP-L1 · Inline arrow passed to `addEventListener`

```javascript
// WRONG — cot.js (pre-fix)
this.#summaryEl.addEventListener('click', () => {
  this.collapsed = !this.collapsed;
});
```

**What went wrong:** `removeEventListener(type, anInlineArrow)` can't match — new function instance each time. The listener stays bound. If the component is re-attached, a SECOND listener binds too. Accumulates.

**Fix:** stable `#field` arrow.

```javascript
#onSummaryClick = () => {
  this.collapsed = !this.collapsed;
};

connected() {
  this.#summaryEl.addEventListener('click', this.#onSummaryClick);
}

disconnected() {
  this.#summaryEl?.removeEventListener('click', this.#onSummaryClick);
  this.#summaryEl = null;
}
```

### AP-L2 · Duplicate `disconnected()` method

```javascript
// WRONG — chart.js (pre-fix)
class AdiaChart extends AdiaElement {
  connected() { /* ... */ this.#ro = new ResizeObserver(...); }

  disconnected() {
    this.#ro?.disconnect();  // ← this one gets SHADOWED
  }

  // ... 100 lines later ...

  disconnected() {
    // second declaration silently wins; ResizeObserver never disconnected
    this.#tooltipEl?.remove();
  }
}
```

**What went wrong:** JavaScript silently takes the last method definition. The first `disconnected()` (with the observer cleanup) is discarded. No error, no warning.

**Fix:** merge into one method. Always.

```javascript
disconnected() {
  this.#ro?.disconnect();
  this.#ro = null;
  this.#tooltipEl?.remove();
  this.#tooltipEl = null;
}
```

### AP-L3 · Missing `super.connected()` / `super.disconnected()`

```javascript
// WRONG — AdiaFormElement subclass missing super call
class AdiaInput extends AdiaFormElement {
  connected() {
    // super.connected() NOT called
    this.#inputEl = this.querySelector('input');
  }
}
```

**What went wrong:** `ElementInternals` registration skipped. The component doesn't participate in forms — no value submission, no validation, no form-reset handling. Silent.

**Fix:** `super.connected()` first line of the method. `super.disconnected()` first line of its method too.

### AP-L4 · Listener added to global `document` without cleanup

```javascript
// WRONG
connected() {
  document.addEventListener('click', this.#onDocumentClick);
  // disconnected() doesn't removeEventListener
}
```

**What went wrong:** the listener survives the component. Every time the component mounts, another listener is added. Over an SPA's lifetime, dozens accumulate. Each fires on every document click.

**Fix:** mirror the addListener with a removeListener in `disconnected()`.

### AP-L5 · Timer not cleared

```javascript
// WRONG
connected() {
  this.#timer = setInterval(() => this.tick(), 1000);
}
// disconnected() doesn't clearInterval
```

**What went wrong:** timer keeps firing on a removed component. Can cause null-dereferences (DOM refs are nulled), phantom renders, or memory leaks.

**Fix:** `clearInterval(this.#timer)` in `disconnected()`.

### AP-L6 · Observer recreated without disconnecting old one

```javascript
// WRONG
connected() {
  this.#ro = new ResizeObserver(...);
  this.#ro.observe(this);
}

// Later — new options, recreated
updateConfig(opts) {
  this.#ro = new ResizeObserver(...); // ← old one leaks
  this.#ro.observe(this);
}
```

**Fix:** disconnect first, then recreate.

```javascript
updateConfig(opts) {
  this.#ro?.disconnect();
  this.#ro = new ResizeObserver(...);
  this.#ro.observe(this);
}
```

### AP-L7 · Empty template wipes authored light-DOM children

```javascript
// WRONG — drawer.js (pre-fix)
class AdiaDrawer extends AdiaElement {
  static template = () => html``;   // ← looks harmless. It isn't.

  connected() {
    this.addEventListener('press', this.#onPress);
    // ... intent: migrate authored [slot="header|body|footer"] into the panel
  }
}
```

**What went wrong:** `AdiaElement`'s base `connectedCallback` runs an effect that calls `stamp(template(this), this)`. `stamp` calls `mount`, which calls `container.replaceChildren(fragment)`. Even an "empty" `html\`\``produces a non-null result, so`replaceChildren`runs and clears every authored child (header/section/footer) out of the host element. The component's own`render()` then tries to migrate children that no longer exist.

Symptom: drawers render with a close button in an empty panel; all authored content is gone. Hard to debug because the children WERE in the DOM at `connected()` time — they get wiped milliseconds later when the effect runs.

**Fix:** drop the override entirely. The base class already defines `static template = () => null;`, and `stamp()` is skipped when the result is null:

```javascript
// RIGHT — no template override
class AdiaDrawer extends AdiaElement {
  // base AdiaElement.template returns null → stamp() is skipped →
  // authored light-DOM children survive through render().

  connected() { /* ... */ }
  render()    { /* migrate children into the panel */ }
}
```

**Recognition:** light-DOM components that compose authored children (card-ui, drawer-ui, list-item-ui, menu-ui, anything with slots) must NOT declare any template — not even an empty one. If the component needs to stamp structural parts (dialog, panel, scrim), use `static parts = {...}` and `this.ensure('name')` instead; parts append once and don't wipe siblings.

### AP-L8 · `setAttribute('value', …)` on `input-ui` after first render

```javascript
// WRONG — expected to update the visible text
input.setAttribute('value', 'Liam Johnson');
// …user still sees an empty field
```

**What went wrong:** `input-ui.connected()` copies `this.value` to `#textEl.textContent` exactly once. `render()` does NOT re-sync when the `value` attribute changes externally — this is intentional, to prevent external re-renders from clobbering in-progress user input. But it means declarative value updates after mount have no visible effect.

**Fix:** set the attribute AND mirror the text slot when you need to update the displayed value from outside:

```javascript
input.setAttribute('value', 'Liam Johnson');
const textSlot = input.querySelector('[slot="text"]');
if (textSlot) textSlot.textContent = 'Liam Johnson';
```

**Real fix:** drawer-populating setup code (admin-dashboard transaction drawer, report drawer) hit this when filling input-ui fields from a clicked row. Worked around with an explicit text-slot mirror; a proper fix would be for `input-ui.render()` to re-sync `#textEl.textContent` when the `value` property changes while the field isn't focused.

**Recognition:** if you're setting an `input-ui` / `textarea-ui` `value` from JavaScript and the field looks empty, you've hit this. `<stat-ui>` and `<select-ui>` do sync on attribute change — the gap is only in the contenteditable-backed text field.

### AP-L9 · Radio cards without a `role="radiogroup"` parent

```html
<!-- WRONG — radios never cross-deselect -->
<list-ui>
  <list-item-ui>
    <card-ui>
      <header>
        <radio-ui slot="icon" name="plan" value="pro" checked></radio-ui>
        <span slot="heading">Pro</span>
      </header>
    </card-ui>
  </list-item-ui>
  <!-- …more radio-ui name="plan"… -->
</list-ui>
```

**What went wrong:** `radio-ui.#select` does a sibling lookup via `this.closest('fieldset, [role="radiogroup"]') || this.parentElement`. When each radio sits inside its own `<span slot="icon">`, the "parent" contains only that one radio — no siblings to deselect. Clicking one doesn't uncheck the others, and the initial `checked` state may or may not render visually depending on mount order.

**Fix:** wrap the whole group in an element `role="radiogroup"`:

```html
<div role="radiogroup" aria-label="Plan" data-plan-picker
     onclick="const r = event.target.closest('card-ui')?.querySelector('radio-ui'); r && r.click()">
  <list-ui divider>
    <list-item-ui>
      <card-ui>
        <header>
          <radio-ui slot="icon" name="plan" value="pro" checked></radio-ui>
          <span slot="heading">Pro · $49/mo</span>
          <span slot="description">…</span>
        </header>
      </card-ui>
    </list-item-ui>
    <!-- additional options -->
  </list-ui>
</div>
```

The inline delegate on the group lets users click anywhere on a card to toggle its radio; the radio's own click handler no-ops on a card-click when it's already checked.

**Recognition:** any time `radio-ui`s with the same `name` are separated by container elements (cards, list-items, grid cells), they need a `role="radiogroup"` ancestor or they won't behave as a group.

### AP-L10 · Popover / tooltip not removed from `document.body`

```javascript
// WRONG
showTooltip() {
  this.#tip = document.createElement('div');
  document.body.appendChild(this.#tip);
  // disconnected() doesn't remove #tip
}
```

**What went wrong:** tip stays in `<body>` after the component is destroyed. Visible zombie element.

**Fix:**

```javascript
disconnected() {
  this.#tip?.remove();
  this.#tip = null;
}
```

---

## Meta-pattern: the "just this once" trap

All of these bugs started as "just this once" exceptions — a component author thought "I'll fix it later," or "this component is special," or "the linter isn't catching it so it's fine." Each "just this once" became a template for the next author.

The audit found 100 findings in iteration 1. Fifteen were novel; eighty-five were different authors cargo-culting the same five shapes.

**Convention is an exponential.** Breaking it once multiplies; enforcing it once multiplies in the other direction. Treat every authoring decision as setting a precedent, because it is.
