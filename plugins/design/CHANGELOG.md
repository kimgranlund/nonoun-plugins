# Changelog

The design plugin, newest first. Releases before this file are recorded in the repository [CHANGELOG.md](../../CHANGELOG.md).

## [Unreleased]

### Added

- `ui-geometry` (T-0841): derives every UI length from a root font size and one unit across four tiers (controls, collections, containers, layout) and fits an existing project to the nearest system. Imported from the MacBook working copy at `1d96fbc`, with a new `agents/openai.yaml`; tests run with `node --test`.

### Changed

- `ui-kit-inspector` (T-0842): the `inspector-panel` example takes its geometry from `ui-geometry/scripts/derive.mjs` instead of the Differential Forms resolvers. `npm run build` writes a browser copy to `geometry-runtime/derive.js`, `panelGeometry()` takes `n` in place of `unit`, and `npm test` asserts ui-geometry identities. Control heights change to 28/32/36px with a 20px slot at n = 14.
- `hct-palettes` (T-0841): replaced with the MacBook working copy, which adds a light/dark color system generator (`scripts/system.mjs`, `scripts/system/`), presets (`scripts/preset.mjs`, `scripts/presets.json`), its check (`scripts/check.mjs`), `references/system.md`, `references/system-notice.md`, `references/showcase.md` and `evals/`.
