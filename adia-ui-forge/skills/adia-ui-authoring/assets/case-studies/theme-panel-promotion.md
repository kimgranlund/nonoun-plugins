# Case study — Mode 4: theme-panel promotion

**Scenario:** [module-promotion.md](../../references/module-promotion.md) — lift duplicated theme controls into a single reusable web-module element **Source:** the canonical 5-phase inline → module instance **Outcome:** `<theme-panel>` element + new `theme/` cluster + 23 unit tests + 2 consumers migrated + chunk corpus refreshed. Three observation rules (OD-001/002/003) extracted from the arc.

---

## §The shape

The theme controls (color-scheme toggle, theme picker, density slider, radius slider, preset buttons) appeared in TWO consumers with non-trivial drift:

- **`site/`** (docs shell) — full-fat: persistence to localStorage, prefers-color-scheme listener, computed-value read-back, preset buttons.
- **`playgrounds/admin-shell/`** — stripped: no persistence, no prefers-color-scheme listener, **no computed-value read-back**.

The stripped variant had a real behavior bug: clicking a theme reset the density + radius sliders to `1, 1` regardless of the theme's `[data-theme="ocean"] { --a-radius-k: 1.5 }` value. The sliders lied about the current state. The docs variant didn't have this bug because its controller read `getComputedStyle()` after the theme attribute write.

Markup was duplicated across the two consumers (~80 lines each), plus controller JS (~120 lines each). Drift was structural; the playground "feature" was actually a controller-omission bug.

---

## §The diagnosis

Per [module-promotion.md](../../references/module-promotion.md) § When to use, the duplication qualified for the lift:

1. A consumer-authored inline block appears in 2+ surfaces ✓
2. The block has a stable, semi-public API surface (4–10 props) ✓ (color-scheme, theme, parametric, presets, persist, scheme-toggle — 6 props)
3. The bug-surface from drift is real ✓ (playground sliders lie about computed values)

Cluster placement (OD-001):

| Option | Decision |
| --- | --- |
| **A. New cluster** | ✓ — theme/ cluster has ≥ 2 credible siblings foreseeable: theme-panel today, theme-toggle + theme-preview tomorrow |
| B. Existing cluster | rejected — none of `simple/` / `runtime/` / `shell/` fits the product axis |

Sibling-button absorption (OD-002): the docs shell had a separate `<button-ui id="theme-toggle">` flipping `color-scheme` NEXT TO the `<popover-ui>` containing the theme panel. **Two duplications could collapse to zero** if the module absorbed it as `[scheme-toggle]`.

---

## §The fix

### Phase 1 — Author the element (one commit)

`packages/web-modules/theme/theme-panel/` — 7 files:

- `theme-panel.yaml` — SoT (6 props: `value`, `theme`, `parametric`, `presets`, `persist`, `scheme-toggle`)
- `theme-panel.js` — UIElement subclass; ~340 LOC; light-DOM; imperative DOM stamping (text-ui + segmented-ui + slider-ui + field-ui + button-ui children)
- `theme-panel.css` — two-block `@scope` per component-token-contract.md
- `theme-panel.html` + `theme-panel.examples.html` — standalone demo
- `theme-panel.test.js` — 23 specs (target ≥ 15)
- `theme-panel.a2ui.json` — GENERATED

4 `package.json` touchpoints wired in one diff: `packages/web-modules/theme/index.js` (cluster barrel), `packages/web-modules/index.js` (root barrel), `packages/web-modules/package.json` `exports` + `files` + `sideEffects`.

### Phase 2 — Migrate `site/` (primary consumer)

Replaced ~80 lines of inline markup with:

```html
<popover-ui placement="bottom-end">
  <button-ui icon="palette" variant="ghost" size="sm" slot="trigger"></button-ui>
  <theme-panel slot="content" persist parametric presets scheme-toggle></theme-panel>
</popover-ui>
```

Deleted controller blocks from `site.js` (~120 LOC). Confirmed via `grep -nE 'id="theme-default"|id="param-density"|id="preset-compact"' site/index.html site/site.js` — zero hits.

**OD-002 applied**: retired the standalone `<button-ui id="theme-toggle">`; `[scheme-toggle]` attribute on the module renders an internal segmented-ui at the top of the panel.

**LS-key migration shim** added to `site.js` boot script — one-shot read-old / write-new / drop-old for 4 keys (`adia-theme` → `adia-theme-scheme`, etc.). Idempotent across reloads; TODO removal date 60 days out.

### Phase 3 — Migrate `playgrounds/admin-shell/`

Same markup substitution **omitting `[persist]`** (playground stays ephemeral). Deleted controller blocks. Updated playground's `spec/SPEC.md` ASCII diagram.

**OD-003 applied**: the playground's slider-lie bug auto-fixed — the module's internal controller calls `requestAnimationFrame(() => { ... getComputedStyle(target)... })` on theme-change, so sliders correctly read back computed values regardless of how the theme changed.

### Phase 4 — Migrate chunk corpus

`packages/a2ui/corpus/chunks/` re-harvested via `npm run harvest:chunks` (SOURCES included `site/pages`). The harvested HTML captured the new authoring shape.

A hand-edit fallback path was also exercised on a playground chunk; a later re-harvest superseded it cleanly when `playgrounds/` was added to SOURCES — concrete proof of the "re-harvest may improve on your hand-edit" gotcha.

### Phase 5 — Release

Standard lockstep cut. `packages/web-modules/CHANGELOG.md` documented `<theme-panel>` + the new `theme/` cluster. Root `CHANGELOG.md` got the cross-cutting entry. The journal captured the DevTools-long-async-stack pitfall.

---

## §The verification

- `theme-panel.test.js` — 23/23 (stamp + connect; attribute reflection on all 6 props; primary user action — scheme/theme/density/radius changes; programmatic `.apply({ scheme: 'dark' })`; persistence on/off; disconnect cleanup; OD-003 computed-value read-back on theme-change)
- `node scripts/build/components.mjs --verify` — clean (1 new module + a2ui.json sidecar)
- `npm run test:a2ui` — 22 pass / 0 fail / 1 skipped (chunk loads with new shape)
- `npm run smoke:chunks` — tolerated pre-existing failures; no new regressions
- Manual visual QA at `npm run dev` — both consumers rendered the popover + panel correctly; theme-change + density-slide + preset buttons all worked

---

## §The lesson

Three observation rules graduated from this arc, all encoded into [module-promotion.md](../../references/module-promotion.md):

1. **OD-001 cluster placement** — the A/B/C/D matrix. New cluster when ≥ 2 credible siblings foreseeable. Cost is 4 single-line edits.
2. **OD-002 absorb sibling-button-next-door** — duplications conceptually adjacent to the module should fold INTO it behind a boolean attribute, not stay alongside.
3. **OD-003 read computed values back into controls** — user mental model is "the slider shows the current value, regardless of how it got there." Use `requestAnimationFrame(() => getComputedStyle(...))` on theme-change.

Pitfall caught: hand-edit chunk corpus can be SUPERSEDED by a later re-harvest if a peer adds your consumer to SOURCES. Usually that's good — the re-harvest captures the live state. Diff before assuming your hand-edit still applies.

## §Cross-references

- [module-promotion.md](../../references/module-promotion.md) § The 5-phase arc + § OD-001 + § OD-002 + § OD-003
- `packages/web-modules/theme/theme-panel/` — canonical implementation
- ADR-0012 — three-tier package architecture (primitives vs modules vs themes)
