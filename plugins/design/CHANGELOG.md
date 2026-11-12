# Changelog

The design plugin, newest first. Releases before this file are recorded in the repository [CHANGELOG.md](../../CHANGELOG.md).

## [Unreleased]

### Added

- `ui-geometry` (T-0841): derives every UI length from a root font size and one unit across four tiers (controls, collections, containers, layout) and fits an existing project to the nearest system. Imported from the MacBook working copy at `1d96fbc`, with a new `agents/openai.yaml`; tests run with `node --test`.

### Changed

- `component-variants` (T-0843): builds its review page from a trimmed kit it owns (`scripts/kit.mjs`, `assets/kit/`: colours, type and one IBM Plex Mono face copied from base-ui) with geometry generated at build time from `ui-geometry/scripts/derive.mjs` by `scripts/geometry.mjs`; it no longer needs base-ui or mathematical-design-system beside it. `ui-kit.lock.json` is removed from the skill and from build output, and `check-build.mjs` now removes `ui-geometry` and the vendored kit as its negative controls.
- `hct-palettes` (T-0841): replaced with the MacBook working copy, which adds a light/dark color system generator (`scripts/system.mjs`, `scripts/system/`), presets (`scripts/preset.mjs`, `scripts/presets.json`), its check (`scripts/check.mjs`), `references/system.md`, `references/system-notice.md`, `references/showcase.md` and `evals/`.
