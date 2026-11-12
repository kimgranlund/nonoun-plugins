# Owned UI kit

This skill owns the UI kit it builds with. `scripts/kit.mjs` is the kit API (`readSource`, `describeKit`, `getAssetBundle`, `compileControls`, `createIndex`, `updateIconCSS`, `collectCatalog` and the sheet renderers), and `scripts/ui-kit.mjs` `loadUI()` returns it with the skill directory as its root. No sibling skill, lock file or mirror check is consulted, and no network installation is used.

## What the kit holds

- Foundation CSS: `assets/foundation/` (colors, typography, semantic palettes, Maison geometry and layout) and `assets/wireframe.css`. `scripts/token-index.mjs` lists the six token groups; `references/style/token-index.json` records them.
- Bundled fonts: `assets/fonts/` (woff2 faces, their OFL licenses and `manifest.json` with each file's hash). `scripts/lib/font-css.mjs` embeds them and fails on a hash mismatch.
- Icons: `assets/icons/` with `assets/phosphor-license.txt`; `scripts/lib/icon-css.mjs` writes their data URIs.
- Runtime and markup: `assets/ui-runtime.js`, `assets/control-markup.mjs`, `scripts/compile-controls.mjs`, `scripts/class-names.mjs`, `scripts/token-inspection.mjs`.
- Recipes and contracts: `assets/recipes/`, `references/style/`, `references/runtime-api.json`, `references/semantic-palettes.json`.
- Catalog extraction and sheet renderers: `scripts/catalog.mjs`, `scripts/lib/specimen-extraction.mjs`, `scripts/lib/sheets/`.
- Browser resolution: `scripts/resolve-browser.mjs` (bounded; no install).

`describeKit()` returns `{packageId:'wireframe-review/kit', runtimeApiVersion:1, contentSHA256}`, where the hash covers the token sources, the font manifest, the runtime and the control markup. Every compiled artifact embeds it as `UI_KIT`, and `verify-artifact.mjs` checks that binding and the embedded foundation bytes.

## Maintaining it

Edit kit files here; there is no upstream copy to synchronize. After a change:

- Geometry: `node scripts/generate-geometry.mjs` regenerates `assets/foundation/maison/geometry.{css,json}` from `ui-geometry/scripts/derive.mjs --json`, and `--check` verifies them. See [geometry and spacing](geometry-spacing.md).
- Token sources: `node scripts/generate-token-index.mjs`, then `--check`.
- Icons: `node scripts/generate-icons.mjs`, then `--check`.
- Fonts: update `assets/fonts/manifest.json` hashes with the files.

The review build embeds the kit runtime and `assets/review-runtime-adapter.js`. `assets/prototype-runtime.js` is their concatenation for older harnesses; keep it in step when either changes. registerPrototype, approval helpers, unit/variant keys, read-only host policy and feedback belong to the review tool; generic state/render/bind, cleanup and heading focus belong to the kit runtime. Existing controllers keep their API.

`component-context.mjs` reads this skill's component contracts; `--runtime` returns the review adapter contract and `--root` reads another corpus for frozen evaluation fixtures. It does not change the kit used for building.

## Checks

The component-family browser matrices that used to forward to another skill are not shipped here. Use the checks in [conditional build checks](workflows/build-checks.md), the generation gates in `generate.mjs`, and rendered review of the actual artifact. The retired migration is recorded in [compatibility retirement](migration/compatibility-retirement.md).
