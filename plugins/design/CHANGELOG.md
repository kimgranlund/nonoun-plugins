# Changelog

The design plugin, newest first. Releases before this file are recorded in the repository [CHANGELOG.md](../../CHANGELOG.md).

## [Unreleased]

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
