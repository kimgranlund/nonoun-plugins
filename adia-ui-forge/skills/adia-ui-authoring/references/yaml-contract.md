# YAML component contract — `<name>.yaml` schema

Authoritative source-of-truth fields for `packages/web-components/components/<name>/<name>.yaml` and `packages/web-modules/<cluster>/<name>/<name>.yaml`. The build pipeline (`scripts/build/components.mjs`) reads these yamls + emits sidecar JSON (`<name>.a2ui.json`) that feeds the docs site, the A2UI runtime registries, and consumer harnesses.

This is the authoritative schema reference for the authoring lane. The full validator + JSON Schema lives at `scripts/schemas/component.yaml.schema.json` (referenced by every yaml's `$schema:` key). This file covers the human-facing contract: what each field means, when to use which value, and the canonical shape of a complete yaml.

---

## Canonical fields (top-level)

```yaml
# Edit this file; run `npm run build:components` to regenerate a2ui.json.
$schema: ../../../../scripts/schemas/component.yaml.schema.json
name: UIMyComponent          # Class name (PascalCase, UI-prefixed)
tag: my-component-ui         # Custom element tag (kebab-case, -ui-suffixed)
component: MyComponent       # Short component name (no UI- prefix)
category: form               # Category — form / display / layout / chrome / a2ui / shell
version: 1                   # Schema version (always 1 for now)
status: stable               # Stability tier — see §status field below
description: >-
  Short one-paragraph description of what the component does and when
  to use it. Used by the docs site, sidecar, and a2ui registry. Be
  concrete about behavior + appearance, not generic ("a button").
props:
  …                          # Prop schemas — see §props field below
events:
  …                          # Event schemas — fired by the component
slots:
  …                          # Named slot semantics
css-vars:
  …                          # CSS custom properties the component reads
```

---

## `status:` field — stability tier

**Required** for all new components. Existing components default to `stable` if unset, but new yamls MUST set this explicitly.

| Value | When to use |
| --- | --- |
| `stable` | Public API contract; safe for consumers to depend on. The vast majority of shipped components. No docs-site badge. |
| `beta` | Functional but API may change in MINOR releases. Docs site shows a `warning`-variant `<tag-ui>` badge labeled "beta". |
| `experimental` | Early prototype; expect breaking changes. Docs site shows a `ghost`-variant badge labeled "experimental". |
| `deprecated` | Has a replacement; check the component's `related:` section. Docs site shows a `danger`-variant badge labeled "deprecated". |
| `early-access` | Customer-preview tier; release notes gate. Docs site shows an `info`-variant badge labeled "early access". |

**Guidance**:

- Set `beta` or `experimental` at FIRST AUTHORING for any component that's not in the stable API contract yet. Don't default to `stable` and bump later — the badge is consumer-facing, and stable→beta is a downgrade signal.
- Only set `stable` after the component has shipped at least one MINOR cycle and gathered consumer feedback. The bar for `stable` is "no API changes anticipated in the next 3 MINOR releases."
- `deprecated` requires a `related:` entry pointing at the replacement. Without one, consumers can't recover.

**Sidecar emission**: `x-adiaui.status` field in `<name>.a2ui.json`. The docs site (`site/site.js`) reads this and injects the badge automatically — no HTML change needed in `<name>.examples.html`.

**Verification**: `grep -L '^status:' packages/web-components/components/*/*.yaml` should return empty (every yaml has a status). Run before opening any authoring PR that adds new yamls.

---

## `props:` field — prop schemas

Each prop is a top-level key inside `props:`. The full prop schema:

```yaml
props:
  label:
    description: >-
      Visible label for the field. Wires aria-labelledby on the
      editable surface so screen readers announce it.
    type: string              # string | number | boolean | enum
    default: ""               # default value (omit for boolean true)
    required: true            # ← see §required field below
    reflect: true             # mirror attribute ↔ property
    enum: [primary, ghost]    # for type: enum
    values:                   # alternative enum syntax (legacy)
      - primary
      - ghost
```

### `required: true` field

**When to use**: only for props where omitting them makes the component meaningless or inaccessible.

| Use `required: true` | Don't use `required: true` |
| --- | --- |
| `field-ui.label` — no visible/accessible label without it | `button-ui.variant` — has a sensible default |
| `icon-ui.name` — nothing renders without it | `select-ui.placeholder` — useful but optional |
| `nav-item-ui.text` — empty nav item | `card-ui.size` — affects styling, not function |
| `chart-ui.type` — can't render a chart of "nothing" | `stat-ui.change-indicator` — optional enhancement |
| `tabs-ui.value` — needs an initial selected tab | `tag-ui.variant` — has a default |

**Heuristic**: ask "if I author `<my-component-ui></my-component-ui>` with nothing else, is the component **broken** or just **default-styled**?" If broken → mark required. If default-styled → don't.

**Representative props marked required**:

- `field-ui.label`
- `icon-ui.name`
- `nav-item-ui.text`
- `chart-ui.type`
- `stat-ui.label`, `stat-ui.value`
- `check-ui.label`
- `badge-ui.text`
- `rating-ui.value`
- `tabs-ui.value`

**Sidecar emission**: `required: true` propagates to the JSON Schema `required` array in `<name>.a2ui.json`. The A2UI validator + MCP tools consume this array — correct marking improves validation quality on generated UI trees.

**Anti-pattern**: marking ALL props required because they all "have a useful value." That defeats the validation signal. `required` is a strict-failure constraint, not a "recommended" hint.

---

## Reserved `data-*` attribute names (admin-shell scope)

`admin-shell.helpers.css` (in `packages/web-modules/shell/admin-shell/css/`) reserves 5 layout-utility `data-*` attribute names with `admin-shell [data-X]` ancestor scoping:

| Attribute | Effect | Use within `<admin-shell>` |
| --- | --- | --- |
| `[data-col]` | `display: flex; flex-direction: column; gap: var(--page-grid-gap)` | column layout helper |
| `[data-row]` | `display: flex; align-items: center; gap: var(--page-grid-gap)` | row layout helper |
| `[data-grid]` | `display: grid; grid-template-columns: 1fr 1fr` (or `1fr 1fr 1fr` for `data-grid="3"`) | 2- or 3-col grid helper |
| `[data-actions]` | `display: flex; align-items: center; gap: var(--page-actions-gap)` | action button cluster |
| `[data-spacer]` | `flex: 1` | flex spacer for pushing content to edges |

**Authoring contract**:

1. **DO NOT use these attribute names for any other purpose** (table column markers, sort-state, etc.) inside `<admin-shell>` descendants. The CSS rules will apply unintended layout. Use namespaced names instead (`data-page-col`, `data-sort-col`, `data-my-actions`).
2. **`admin-shell` ancestor is required**. An earlier dist CSS shipped bare global selectors that applied to ANY element with these attributes on ANY page loading `admin-shell.min.css` — including `<table>` headers (silent layout breakage in Safari/WebKit). Source + dist now both prefix `admin-shell` ancestor. This is a hard constraint: the parent-tag selector is the only reliable CDN-safe scoping mechanism (LightningCSS strips `@scope` blocks).
3. **Outside `<admin-shell>`, these names have NO EFFECT**. If you need `[data-col]` semantics on a non-admin-shell page, you must author your own CSS (the helpers do not apply globally).

**Documented for consumers** in the adia-ui-factory plugin's consumer composition skill (§CSSPolicy → "Reserved layout-helper attribute names (admin-shell scoping)").

---

## Build pipeline

```bash
npm run build:components       # regenerates all <name>.a2ui.json sidecars from yamls
npm run verify:components      # verifies no drift (CI gate)
node scripts/build/components.mjs --verify   # same as above, direct invocation
```

The build:

1. Reads every `<name>.yaml` under `packages/web-components/components/` and `packages/web-modules/<cluster>/`
2. Validates against `scripts/schemas/component.yaml.schema.json`
3. Emits `<name>.a2ui.json` (the sidecar) co-located with the yaml + js + css
4. Emits the `traits/_catalog.json` aggregate
5. `--verify` mode: re-runs steps 1-4 in-memory and fails if any sidecar drifts from disk content (CI hard-fail)

**Never hand-edit `<name>.a2ui.json`** — it's regenerated from the yaml. The yaml is the SoT.

---

## Component creation playbook (full lifecycle)

This is the canonical end-to-end procedure for creating a new component yaml + js + css + examples.html + sidecar. Run in order:

1. **Author `<name>.yaml`** with all required fields:
   - `name:`, `tag:`, `component:`, `category:`, `version: 1`
   - `status:` — pick from the table above
   - `description:` — concrete one-paragraph
   - `props:` with per-prop `type:`, `default:`, optional `required: true`, optional `enum:` / `values:`
   - `events:`, `slots:`, `css-vars:` as applicable
2. **Author `<name>.js`** following the `AdiaElement` / `AdiaFormElement` patterns (see [code-style.md](code-style.md))
3. **Author `<name>.css`** following the light-DOM cascade rules (see [css-patterns.md](css-patterns.md))
4. **Build the sidecar**:

   ```bash
   npm run build:components
   ```

   This generates `<name>.a2ui.json`.

5. **Author `<name>.examples.html`** with at minimum:
   - A `<h1>` matching the component name
   - One `<section data-section data-property="usage">` with the canonical worked example
   - Per-prop demo sections matching `data-property="<prop-name>"` (one per prop)
6. **Run the anatomy sweep**:

   ```bash
   node scripts/docs/anatomy-sweep.mjs
   ```

   This auto-generates the **canonical anatomy sections** (`slots`, `data-attrs`, `keyboard`, `css-vars`, `a2ui`, `related`) from the sidecar. The sweep is idempotent — skip-on-already-present, safe to re-run. Hand-author `accessibility` and any prop-demo sections; the sweep covers the schema-derivable sections only.

   Canonical `data-property` vocabulary for `<section data-section data-property="X">`:
   - `usage` — canonical worked example
   - `props` — prop reference table
   - `slots` — named-slot semantics
   - `events` — fired events
   - `data-attrs` — `data-*` attributes the component reads
   - `css-vars` — CSS custom properties
   - `keyboard` — keyboard interaction model
   - `accessibility` — ARIA, screen-reader notes
   - `a2ui` — A2UI runtime integration notes
   - `related` — sibling/replacement components
   - `<prop-name>` — visual demo for a specific prop

   The sweep also **normalizes legacy section data-properties**: `Properties` → `props`, `Events` → `events`, `CSS Tokens` → `css-vars`, `Usage` → `usage`. Run with `--dry` first to preview changes:

   ```bash
   node scripts/docs/anatomy-sweep.mjs --dry
   ```

7. **Run the full verify gate**:

   ```bash
   node scripts/build/components.mjs --verify   # sidecar drift
   npm run verify:traits                         # 100% coverage
   ```

After the playbook, the component is consumable by the docs site, the A2UI runtime, and any harness reading the sidecar.

---

## Cross-references

- `docs/specs/component-token-contract.md` — token/variant/mode contract
- `docs/specs/component-implementation-patterns.md` — implementation patterns
- [code-style.md](code-style.md) — JS code style rules
- [css-patterns.md](css-patterns.md) — light-DOM CSS cascade rules
- [api-contract.md](api-contract.md) — props/events/slots conventions
- [authoring-cycle.md](authoring-cycle.md) — the 5-step authoring procedure
- `scripts/schemas/component.yaml.schema.json` — JSON Schema (authoritative)
