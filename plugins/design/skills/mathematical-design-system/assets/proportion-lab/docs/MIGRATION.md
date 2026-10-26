# Proportion study · Differential Forms

This is a deliberate migration of the retained study, not a copy of the reference jig. The eight study topics, typography choice, menu actions, configuration import/export, guide inspection and density comparisons remain application concerns.

## Authority and build

`../differential-forms` supplies the current contracts, component parts, recipes and pure typed resolvers. `src/app.js` consumes those functions. `scripts/build.mjs` strips their TypeScript and embeds the same implementations in the standalone preview, so HTTP and file previews use identical geometry. It also emits browser modules. No old Base UI builder or percentage token package participates.

Edit `specimens/source.html`, `src/app.css` and `src/app.js`; run `npm test` and `npm run build`. Both `specimens/index.html` and `dist/index.html` are generated. `system.manifest.json` records the authored-source hash, implementation hash and upstream provenance. The reference system's independent specimen formulas are unchanged because this consumer does not change its contracts or resolvers. Historical scripts, old runtime files and `tests/` are retained compatibility artifacts; current checks live in `verification/`.

## Component mapping

| Study content | Current geometry and behavior |
| --- | --- |
| Buttons, Sharp/Pill pairs | Control; fixed 6u slots, density-independent exposed label edges |
| Chips and input adornments | Chip; 4u slots and half Control label edge |
| Composed inputs | Neutral input wrapper, chip adornments; own input edge policy, sibling actions |
| Menus/listboxes | Attached composite containing Control rows; requested inset controls gap and child radius |
| Tables/data lists/multiline | Collection and multiline resolvers, content growth and shared table columns |
| Ordinary cards | Card resolver, no composite subtraction; descendants keep their Control density |
| Layout comparisons | Explicit Control, Collection and Card family comparison; page/group layout is not a fourth geometry formula |
| Radius comparisons | Named curvature endpoints; container Softest is 4u, Control Softest is a pill |

Defaults are u4, border0, inset0u, Soft curves and label edge1.5u. Three density settings replace five legacy levels, tier/scale selectors and percentage curvature. Control density is never inherited from Collection or Card density. Transparent borders consume their owner's budget once. Fixed slots and text are preserved; tighter budgets grow containing composites. Zero-inset flattening applies only to attached composites.

## Explicit extensions and limits

The study's action menu uses the same attached Control-row geometry as a listbox, with menu semantics and commands rather than selection. Avatar/logo demonstrations use artwork inside the fixed Control slot; authored artwork remains independent of the owning slot's shape. Page layout, specimen captions, navigation and inspector dimensions are application layout, not geometry tokens. Typography selection affects specimens only; interface text remains system-ui.

Guides are diagnostic paint and must not consume layout space. Geometry validation and focus styling are separate; focus uses a 3px solid ink outline at zero offset. Text input focus belongs to its neutral wrapper while sibling actions remain individually focusable. Dark/light surfaces use the shared appearance roles.

Numerical tests establish resolver invariants, not accessibility certification. Browser checks cover rendered sizes and interaction; manual screenshots cover appearance. Full assistive-technology and contrast certification remain outside this migration. No deployment is part of the work.

## Verification record · 2026-10-22

- Shared Differential Forms contract suite: 14 tests passed.
- Consumer checks: default golden values, border/slot conservation, composite growth, label-edge rules, invalid domains, generated hash and compiled-module parity.
- Browser: 36 unit/border/control-density/composite-inset boundary combinations; no fixed slot shrinkage or JavaScript errors. Currency keyboard selection/focus return and separate input-wrapper/action focus indicators checked.
- Visually inspected light button arrangements, dark menus with maximum border/inset, and a 390px composed-input layout. No page-level horizontal overflow; density comparisons scroll internally with hidden scrollbars.
- Browser automation is reusable via `PLAYWRIGHT_MODULE=<module path> CHROME_PATH=<browser path> node verification/browser-check.mjs`; Playwright is optional and not vendored. Screenshots are written to `/tmp/df-*.png`.
- Full screen-reader, contrast and every browser engine testing is not claimed. External font/icon assets require network access.

## Editorial appearance restoration

The study retains its Vignelli-inspired warm paper (#f7f5ee), charcoal (#252525) and vermilion (#c9281c) identity, with paired dark surfaces. Explicit Display, Heading, Subhead, Title, Body and Caption roles govern editorial content; the typography disclosure previews the hierarchy. Interface text remains system-ui and captions IBM Plex Mono 400. Control text, slots, border budgets, focus geometry and family densities remain resolver-owned. This restores appearance without reintroducing the legacy typography formulas.

Rendered examples use component-level Title (18px) for card headings, Body for card prose and table/data-list cells, and Caption for specimen feedback. Display is reserved for page-level editorial content and the typography preview; cards do not use brand/content-level headings. Collection rows grow naturally for the text. Buttons, chips, inputs, menu/listbox rows and their label slots retain resolver typography and unchanged geometry.
