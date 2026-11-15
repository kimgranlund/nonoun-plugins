# Changelog

The design plugin, newest first. Releases before this file are recorded in the repository [CHANGELOG.md](../../CHANGELOG.md).

## [Unreleased]

## [0.4.0] - 2026-11-15

### Added

- `ui-materials` (T-0853): paints UI parts in any material and builds components that render in all of them. Imported from the MacBook copy at `ec1743a`; checks run with `node scripts/check.mjs`.
- `ui-content` (T-0853): prints values and labels so they read and line up. Imported from the MacBook copy at `1aafd92`; ships no tests.
- `ui-interaction-dev` (T-0853): builds UI interactions that work for every input from a rule spec. Imported from the MacBook copy at `de8f3a9`; tests run with `node --test`.
- `ui-frameworks` (T-0853): creates a UI kit of light-DOM custom elements (or React) with plain CSS recipes. Imported from the MacBook copy (no git); checks run with `node scripts/manifests.mjs --check` and `node scripts/lint-recipes.mjs`.
- `ui-explore-variants` (T-0853): explores a UI problem as distinct live variants on one page with per-variant feedback. Imported from the MacBook copy at `c7d3ac9`; ships no tests.
- `ui-showcase-bento` (T-0853): generates bento showcases packed to fit, with an in-page checker. Imported from the MacBook copy at `f3fbd78`; tests run with `node --test`.

### Changed

- `ui-geometry` (T-0852): synced from the MacBook copy at `62d0cda`. Adds measured archetypes, dimensions and terms (`references/{archetypes,dimensions,terms}.json`) with their scripts and tests (`archetypes`, `dimensions`, `docs`, `observe`, `terms`, `knowledge.test.mjs`). The built-in preset `massimo` is now `standard` with the same values, so the inspector panel (`PRESETS.standard`, rebuilt `geometry-runtime/derive.js`) and `wireframe-review` (`generate-geometry.mjs` dial, regenerated `geometry.json` and its provenance hash) follow the new name.
- `ui-colors` (T-0852): synced from the MacBook copy at `e9ff385`. Adds `references/terms.json` and a pressed solid role, `-solid-active`, in every mode.
- `ui-colors` (T-0848): renamed from `hct-palettes`, the first of the ui-* skills. Invoke it as `$ui-colors`; the generator id `hct-palettes@4` in output manifests is unchanged.

## [0.3.0] - 2026-11-12

### Added

- `ui-geometry` (T-0841): derives every UI length from a root font size and one unit across four tiers (controls, collections, containers, layout) and fits an existing project to the nearest system. Imported from the MacBook working copy at `1d96fbc`, with a new `agents/openai.yaml`; tests run with `node --test`.

### Changed

- `component-variants` (T-0843): builds its review page from a trimmed kit it owns (`scripts/kit.mjs`, `assets/kit/`: colours, type and one IBM Plex Mono face copied from base-ui) with geometry generated at build time from `ui-geometry/scripts/derive.mjs` by `scripts/geometry.mjs`; it no longer needs base-ui or mathematical-design-system beside it. `ui-kit.lock.json` is removed from the skill and from build output, and `check-build.mjs` now removes `ui-geometry` and the vendored kit as its negative controls.
- `ui-kit-inspector` (T-0842): the `inspector-panel` example takes its geometry from `ui-geometry/scripts/derive.mjs` instead of the Differential Forms resolvers. `npm run build` writes a browser copy to `geometry-runtime/derive.js`, `panelGeometry()` takes `n` in place of `unit`, and `npm test` asserts ui-geometry identities. Control heights change to 28/32/36px with a 20px slot at n = 14.
- `hct-palettes` (T-0841): replaced with the MacBook working copy, which adds a light/dark color system generator (`scripts/system.mjs`, `scripts/system/`), presets (`scripts/preset.mjs`, `scripts/presets.json`), its check (`scripts/check.mjs`), `references/system.md`, `references/system-notice.md`, `references/showcase.md` and `evals/`.
- `wireframe-review` (T-0844): owns a trimmed UI kit and no longer needs `base-ui` or `mathematical-design-system` beside it. The mirrored kit files are its own source, `scripts/kit.mjs` vendors the base-ui modules its scripts call (fonts, runtime, catalog, browser resolver), and `ui-kit.lock.json`, `ui-compatibility.json`, `sync-ui-kit.mjs` and 48 forwarding checks are removed. Six checks the docs name moved in as real scripts. `scripts/generate-geometry.mjs` regenerates the Maison geometry from `ui-geometry` `derive.mjs --json` (product md/md: S 20, I 6, h 32). The review shell's intent disclosure now carries its contract classes, and artifact verification compares the embedded foundation with the full bundle, so `generate.mjs` builds the example manifest again.

### Removed

- `base-ui` and `mathematical-design-system` (T-0845): removed from the plugin. `component-variants`, `wireframe-review` and the `ui-kit-inspector` example own their kits and take geometry from `ui-geometry`.
