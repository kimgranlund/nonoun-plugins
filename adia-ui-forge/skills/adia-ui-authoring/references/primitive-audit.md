# Primitive Audit — Mode 1 §0 gate

**This is mandatory before _every_ new component or interactive surface in `packages/web-components/components/`.** Skipping it produces work that re-derives existing wiring, hits first-paint timing races (e.g. `input-ui[prefix]` falls back to literal text before the icon registry loads — `search-ui` was built precisely to hide that), creates asymmetry across the library, and burns user trust.

The audit takes 30 seconds. Do it.

Absorbed from the legacy `primitive-audit` skill (now removed; this file replaces it).

---

## Step 0 — list the affordances

Take your spec / screenshot / user request and list each interactive affordance independently. For a "table header bar" like a table-toolbar, that's:

1. Title with optional count badge
2. Filter button → popover with per-column inputs
3. Sort button → popover with per-column rows
4. Columns visibility button → popover with checkbox list
5. Search field

Each line is a separate audit target.

## Step 1 — inventory the library

```bash
ls packages/web-components/components/
```

Skim the names. Most affordances have a dedicated component already.

## Step 2 — for each affordance, grep yamls

```bash
# Example: looking for an existing search-input primitive
grep -lE "search|magnifying" packages/web-components/components/*/*.yaml

# Example: looking for an existing label+control wrapper
grep -lE "label.*control|inline label" packages/web-components/components/*/*.yaml

# Example: looking for an action-menu / popover primitive
grep -lE "menu|popover|dropdown" packages/web-components/components/*/*.yaml
```

Read every match's yaml top section (description + props + slots + events). Five minutes of reading saves an hour of re-implementation.

## Step 3 — known-primitive map

Treat this as the default lookup table. **If your affordance maps to a row here, use that primitive — do not roll your own.**

| Affordance | Primitive (NOT your own from scratch) |
| --- | --- |
| Search field with magnifying-glass + clear + debounce | `search-ui` |
| Label + form control pair | `field-ui` (use `inline` for single-row layout) |
| Action menu anchored to a trigger button | `menu-ui` + `menu-item-ui` (+ `menu-divider-ui`) |
| Content popover (free-form) anchored to a trigger | `popover-ui` |
| Tooltip on hover / focus | `tooltip-ui` |
| Toolbar with overflow → spillover popover | `toolbar-ui` + `toolbar-group-ui` |
| Legend bound to a chart-ui by id | `chart-legend-ui[for]` |
| Pagination bar | `pagination-ui` |
| Empty state (icon + heading + body + action) | `empty-state-ui` |
| Loading skeleton blocks | `skeleton-ui` |
| Inline code / shortcut hint | `kbd-ui` (NOT raw `<code>` / `<kbd>`) |
| Inline metric (label + value + change + trend) | `stat-ui` |
| Block of code with syntax highlighting | `code-ui` |
| Table data-cell formatting (badge, link, progress, date, etc.) | `cell-types.js` registry — register a new type, don't render in column.render |
| Filter / sort / columns / search bar above a table | `table-toolbar-ui[for]` |
| Tabs + panels | `tabs-ui` + `tab-ui` |
| Modal / drawer / toast | `modal-ui` / `drawer-ui` / `toast-ui` |
| Switch / checkbox / radio / segmented / toggle group | `switch-ui` / `check-ui` / `radio-ui` / `segmented-ui` / `toggle-group-ui` |
| Avatar / avatar group | `avatar-ui` / `avatar-group-ui` |
| Color / calendar / OTP picker | `color-picker-ui` / `calendar-picker-ui` / `otp-input-ui` |
| Stepper / timeline / progress / progress-row | `stepper-ui` / `timeline-ui` / `progress-ui` / `progress-row-ui` |
| Card with header / section / footer | `card-ui` (+ slot children) — don't roll a "panel" |
| Description-list (key/value) | `description-list-ui` |
| Tree / list / action-list | `tree-ui` / `list-ui` / `action-list-ui` |

If your affordance isn't in this table, run Step 2 again with better grep keywords. Only after those return nothing should you consider authoring something new.

## Step 4 — when authoring IS warranted

If an affordance genuinely has no primitive (e.g. you're building the _first_ version of a new pattern), follow `chart-legend-ui` as the canonical "companion-bound-by-`[for]`" template:

- `[for]` id-ref to the peer element
- Resolve via `getRootNode().getElementById()`, fall back to first sibling of the right tag
- Listen to peer events for state sync
- Dispatch state changes back via `peer.<setter>` or `peer.<method>()`
- NEVER duplicate state in the companion — peer remains source of truth

## Step 5 — tone & token audit (mode 5 of this skill)

After the primitive audit passes, run mode 5 (the token audit at [token-contract.md](token-contract.md)) to confirm:

- Two-block `@scope` pattern (tokens on `:where(:scope)`, styles on `:scope`)
- Zero raw colors (`grep -E '#[0-9a-fA-F]|rgb\(|hsl\(|oklch\(' <component>.css`)
- Match the canonical surface tokens of similar primitives — for any popover that visually competes with `select-ui [slot="listbox"]`, copy its surface tokens exactly: `--a-canvas-bright`, `--a-ui-border`, `--a-radius`, `--a-bg-hover`, `--a-fg-hover`, `--a-fg-subtle`. Don't pick `--a-canvas` for floating menus — it's the L2 mid-tone surface, identical luminance in both schemes.

## Past failure (do not repeat)

A `table-toolbar-ui` initial implementation rolled its own from scratch:

- Hand-stamped `<input-ui prefix="magnifying-glass">` for search → "magnifying-glass" rendered as **literal text** because the icon registry hadn't resolved at first paint. `search-ui` already wraps input-ui with the right prefix + suffix + debounced `search` event.
- Hand-stamped `<label>` + `<span>` + `<input-ui>` for filter rows → `field-ui inline` is the canonical label+control pair, mints `id` + `[for]` automatically.
- Wrote `<text-ui display>` (invalid bare attr — `display` is an enum value of `variant`, requires `<text-ui variant="display">`).
- Wrote popover surface as `--a-canvas` (washed-out mid-gray) instead of reading `select-ui`'s listbox tokens (`--a-canvas-bright`).

Caught only after user feedback. The audit takes 30 seconds. Do it.

## Quick reflex check before any `document.createElement('input-ui')` etc

Ask: "is there a higher-level primitive that wraps this?" 80% of the time yes. Examples:

| You're about to write | Probably want |
| --- | --- |
| `createElement('input-ui')` + `setAttribute('type', 'search')` | `createElement('search-ui')` |
| `createElement('input-ui')` + manual label `<span>` | `createElement('field-ui')` with `[label]` attr |
| `createElement('div')` + `setAttribute('popover', 'manual')` + `anchorPopover()` | `createElement('menu-ui')` (action) or `createElement('popover-ui')` (content) |
| `createElement('button')` + raw `<icon-ui>` + raw label | `createElement('button-ui')` with `[icon]` + `[text]` |
| `createElement('div')` + multiple `<text-ui>` for empty state | `createElement('empty-state-ui')` |

## Cross-references

- [authoring-cycle.md](authoring-cycle.md) — the full 5-step authoring procedure (run AFTER this audit clears)
- [anti-patterns.md](anti-patterns.md) — failure-mode catalogue (look up the rule a found primitive enforces)
