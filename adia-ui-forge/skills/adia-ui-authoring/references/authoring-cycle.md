# Authoring cycle — modes 1 & 2 (NEW or MODIFY primitive)

The 5-step procedure run AFTER [primitive-audit.md](primitive-audit.md) clears (mode 1) or jumping straight to Step 2 (mode 2: modify existing).

Absorbed from the legacy author skill's Workflow section.

---

## Step 1 — Read the contract and the reference components

Before writing or editing, load these four files. They are the ground truth:

- `docs/specs/component-token-contract.md` — the authoritative invariants. Skim the whole thing if you haven't read it this session; focus on "Variants vs Modes" and "Sanctioned Mode Attributes" if you're adding a new layout-affecting attribute.
- `packages/web-components/core/element.js` — `AdiaElement` base class. The `static properties` schema, `connected()`/`disconnected()`/`render()` lifecycle, and attribute-mapping conventions are all defined here.
- `packages/web-components/core/form.js` — `AdiaFormElement`. Only needed if the new component participates in forms (inputs, selects, checkboxes, etc.).
- At least one good-citizen reference that matches the shape of what you're building. Pick from: `button-ui`, `card-ui`, `input-ui`, `textarea-ui`, `check-ui`. Read both the `.js` and the `.css`.

## Step 2 — Classify the work before you write

Before typing, answer:

1. **Is this cosmetic or structural?** If the change affects `display`, `flex-direction`, `grid-template`, `padding`, layout geometry — it's a mode, not a variant. Modes require an entry in the Sanctioned Mode Attributes table (`docs/specs/component-token-contract.md` `Modes` section). Do not introduce undocumented layout-changing variants.

2. **Does the new prop fit the Boolean-default-false rule?** If the default behavior is "on," negate the prop name before writing (`closable` is wrong if closable is the default; `permanent` is right).

3. **Does the component hold state that CSS needs to read?** If yes, every state-bearing Boolean declares `{ type: Boolean, default: false, reflect: true }`.

4. **Does the component add listeners, timers, or observers?** If yes, plan the `disconnected()` method at the same time as `connected()` — do not defer. The symmetric pair is one unit of work, never two.

## Step 3 — Apply the non-negotiable rules

These rules are the distilled lessons from a 5-iteration audit. Each one corresponds to a real bug that was fixed in the codebase. Full rationale and the bug histories are in [anti-patterns.md](anti-patterns.md).

### API / Attributes

1. **Boolean defaults are `false`.** If the expected default is "on," rename: `closable` → `permanent`, `animate` → `static`, `cursor` → `hideCursor`, `average` → `hideAverage`, `pause-on-hover` → `noPauseOnHover`.

2. **No magic-value sentinels in numeric props.** Indeterminate = `null`, not `-1`. Consumers branch on `value == null`, which is explicit.

3. **Use `attribute:` not `attr:`.** `attr:` is a silent typo — the mapper ignores it and the kebab-case HTML attribute never wires. This cost a real bug in `rating-ui`.

4. **State-bearing Booleans reflect.** `{ type: Boolean, default: false, reflect: true }`. Without `reflect`, CSS can't match `:scope[disabled]`, hover/active/selected states break silently.

5. **Reserved-name anti-patterns.** Avoid: `title` (collides with HTML tooltip attribute), `active` on parent components (use `value` for a selection or `step` for an index — per-item `active` on children is fine), `error` in variant names (use `danger`; reserve `error` for validation state), `disabled` on non-form-participating components (use `readonly`), `multiple` with exclusion semantics (use a negated positive like `single`).

6. **Element tag ends in `-ui`; JS class is `Adia<Component>`.** `<foo-ui>` ↔ `class AdiaFoo extends AdiaElement`. Three-way consistency: filename, class name, custom-element tag. The sanctioned `-n` carve-out is `cot-ui` (the chain-of-thought streaming component); `nav-ui` was deprecated in favor of the `-ui` replacements. New `-n` tags require a contract-doc update — see `docs/specs/component-token-contract.md`.

### CSS

1. **Two-block `@scope` structure** is mandatory:

   ```css
   @scope (component-ui) {
     :where(:scope) {
       /* ── Tokens ── */
       --component-bg: var(--a-bg);
       --component-fg: var(--a-fg);
       /* ...all component tokens here, zero-specificity */
     }

     :scope {
       /* ── Base styles — consume only component tokens ── */
       background: var(--component-bg);
       color: var(--component-fg);
     }

     /* ── Variants / states third — override TOKENS only ── */
     :scope[variant="outlined"] {
       --component-bg: transparent;
       --component-border: var(--a-border);
     }
   }
   ```

2. **Variants override tokens only.** A variant body may only contain `--component-*: var(...)` lines. Never `padding`, `display`, `position`, `width`, `height`, `margin`, `gap`, `flex`, `grid`, `overflow`, `border-radius`. Layout changes are modes, see rule 3 in Step 2.

3. **Zero raw colors in component CSS.** No `#hex`, `rgb()`, `rgba()`, `oklch()` outside `packages/web-components/styles/colors/semantics.css` and `packages/web-components/styles/tokens.css`. Every color goes through a token.

4. **Raw px ≥ 3 is forbidden.** Use `var(--a-space-*)`. Stroke/border widths (1–2px) and documented component-intrinsic constants are carve-outs, and each carve-out needs a one-line code comment explaining why the literal.

5. **Component tokens follow `--<tag-stem>-<prop>`.** `--button-bg`, not `--btn-bg`. Files hosting multiple `@scope` blocks (e.g. `layout.css` with `col-ui`, `row-ui`, `stack-ui`) use each scope's own stem (`--col-gap`, `--row-gap`, `--stack-gap`).

6. **Consume L3, not L2.** In a variant/state body, alias from the role×state matrix, not the family base. Right: `--button-fg-hover: var(--a-accent-fg-hover)`. Wrong: `--button-fg: var(--a-accent)`.

7. **No BEM, no `::part()`, no `::slotted()`.** AdiaUI is light-DOM; the shadow-DOM escape hatches don't apply. Slots are styled through slotted attribute selectors (`:scope > [slot="foo"]`), not `::slotted()`.

### JS Lifecycle

1. **Every `addEventListener` in `connected()` has a matching `removeEventListener` in `disconnected()`.** Handler must be a stable `#field` arrow (`#onClick = (e) => { ... }`), never an inline arrow passed to `addEventListener`. Inline arrows can't be removed — `removeEventListener` needs reference equality.

2. **`AdiaFormElement` subclasses call `super.connected()` and `super.disconnected()`.** `ElementInternals` registration depends on it. Omitting `super` strands the form-association.

3. **Timers and observers are torn down.** `clearInterval`, `clearTimeout`, `ResizeObserver.disconnect()`, `MutationObserver.disconnect()`, `IntersectionObserver.disconnect()` all in `disconnected()`.

4. **Null cached DOM refs in `disconnected()`.** `this.#fooEl = null` after removing its listeners. Prevents stale-tree GC pinning when the component is re-attached.

5. **Never declare `disconnected()` twice in one class.** The second silently overrides the first — this exact bug lost `ResizeObserver` cleanup in `chart.js` for several commits. If you find yourself needing a "second disconnected," merge it into the existing one.

6. **Popover/tooltip overlays created in `connected()` are removed in `disconnected()`.** Anything appended to `document.body` or `<body>` via the Popover API needs explicit cleanup; they don't GC with the host.

7. **Inline arrows on dynamically created ephemeral DOM are tolerated only when the container is guaranteed fully-detached before re-render.** If a row is built fresh per render and the parent's `innerHTML` replacement detaches the old subtree, GC collects the listeners with their nodes. If the container persists, use stable handlers or event delegation on the parent.

### Field composition

1. **Do not add a `label` attribute to a new form-associated control.** `<field-ui label="…">` is the canonical labeled-field wrapper. It owns the real `<label for="…">` and binds to the slotted control's id for proper click-to-focus — a pattern the embedded per-control `label` attribute can't provide (no `[for]`, just a shadow slot). Existing controls (input-ui, select-ui, textarea-ui, switch-ui, check-ui, radio-ui, slider-ui, calendar-picker-ui, upload-ui, range-ui) still accept the legacy `label` attr but log a one-shot console.warn; **no new control should declare one**. Wrap instead:

   ```html
   <!-- right -->
   <field-ui label="Email">
     <input-ui type="email" value="…"></input-ui>
   </field-ui>

   <!-- wrong (deprecated) -->
   <input-ui label="Email" type="email" value="…"></input-ui>
   ```

   `field-ui` also carries `[slot="trailing"]` and `[slot="action"]` composition slots + an `inline` mode attribute (stacked vs. single-row). See the Field component at `packages/web-components/components/field/`.

### Nested-control composition

1. **Composite hosts own the focus ring; nested form controls suppress theirs.** When a composite wraps a form control as an internal implementation detail (textarea-ui inside chat-input-ui is the canonical example), the composite IS the primary surface from a user's perspective. Focus should wrap the whole composite, not just the inner control. Pattern:

   ```css
   @scope (my-composite-ui) {
     /* 1. Composite paints the ring via :focus-within —
        wraps both the control and any siblings inside the shell. */
     :scope:focus-within {
       box-shadow: var(--my-composite-focus-ring);
     }
     :scope[aria-invalid="true"]:focus-within,
     :scope[error]:focus-within {
       box-shadow: var(--my-composite-focus-ring-invalid);
     }

     /* 2. Suppress the inner control's own focus affordance.
        The @scope block's containment IS the signal — no data
        attribute or explicit opt-in needed; selectors targeting
        inner elements only apply when they're inside this host. */
     textarea-ui [slot="text"]:focus {
       box-shadow: none;
     }
   }
   ```

   Tokens follow the L3 pattern from rule 12:

   ```css
   --my-composite-focus-ring:         var(--a-focus-ring);
   --my-composite-focus-ring-invalid: var(--a-focus-ring-invalid);
   ```

   **When to use this (not field-ui):**
   - **field-ui** is a _wrapper composite_ — it adds chrome (label / hint / error / required) around a control, but the control is still the primary focus target. Control owns the ring.
   - **chat-input-ui** (and future equivalents) are _shell composites_ — the composite IS the control; the inner textarea is an implementation detail. Host owns the ring.

   A user's mental model is the discriminator: do they think of the composite as a single control, or as a labeled/wrapped version of an inner control? The former is a shell; the latter is a wrapper.

## Step 4 — Run the 30-second self-check

Before declaring the work done, run through this checklist. If anything fails, fix before committing.

### Attributes

- [ ] No Boolean prop has `default: true`.
- [ ] No numeric prop uses `-1` or other sentinels (indeterminate = `null`).
- [ ] Every `static properties` entry uses `attribute:` (not `attr:`).
- [ ] Every state-bearing Boolean has `reflect: true`.
- [ ] No reserved-name anti-patterns (`title`, parent-level `active`, `error` variant, `disabled` on non-form, exclusion-`multiple`).
- [ ] Element tag ends in `-ui`; class is `Adia<Component>`.

### CSS

- [ ] File opens with `@scope (component-ui) {` and has both `:where(:scope)` (tokens) and `:scope` (base styles) blocks.
- [ ] Variants in the file contain ONLY `--component-*: var(...)` lines.
- [ ] Zero `#hex` / `rgb()` / `rgba()` / `oklch()` in the file.
- [ ] Zero raw `px` values ≥ 3 (or each has a one-line justification comment).
- [ ] Component tokens prefixed with the scope's tag-stem.
- [ ] Variant/state bodies alias from L3 (`--a-<family>-<role>-<state>`), not L2 (`--a-<family>`).

### Lifecycle

- [ ] Every `addEventListener` in `connected()` has a paired `removeEventListener` in `disconnected()`.
- [ ] All handlers passed to `addEventListener` are stable `#field` arrows (or bound method refs), not inline arrows.
- [ ] If the class extends `AdiaFormElement`, both `connected()` and `disconnected()` call `super`.
- [ ] Every timer/observer created in `connected()` is disposed in `disconnected()`.
- [ ] Cached DOM refs (`this.#fooEl`) are nulled in `disconnected()`.
- [ ] Class declares `disconnected()` exactly once.

## Step 5 — Run the project's verification gates

Before committing, run the project's verify scripts. These catch the drift-shaped bugs the checklist can miss:

```bash
npm run verify:components   # component schema integrity (catalog)
npm run verify:palette      # CVD thresholds across theme × scheme
node -c path/to/new/file.js # JS syntax check
```

The full release-side gate roster lives in the **adia-ui-release** skill's gate catalog. Invoke `adia-ui-release` mode "Just verify" for the comprehensive sweep after any structural change.

If a gate fails, fix before declaring done.

## Cross-references

- [primitive-audit.md](primitive-audit.md) — mode 1 §0 gate (run BEFORE this)
- [api-contract.md](api-contract.md) — deep dive on prop naming, type choices, reflection policy
- [css-patterns.md](css-patterns.md) — exhaustive CSS architecture (@scope, variants, modes)
- [lifecycle-patterns.md](lifecycle-patterns.md) — timers, observers, popovers, listener patterns
- [anti-patterns.md](anti-patterns.md) — full failure-mode catalogue, file:line refs
- [worked-example.md](worked-example.md) — badge-ui + counter-ui walkthroughs
- [token-contract.md](token-contract.md) — mode 5 audit (post-implementation token check)
