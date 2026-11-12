# Changelog

The design plugin, newest first. Releases before this file are recorded in the repository [CHANGELOG.md](../../CHANGELOG.md).

## [Unreleased]

### Added

- `ui-geometry` (T-0841): derives every UI length from a root font size and one unit across four tiers (controls, collections, containers, layout) and fits an existing project to the nearest system. Imported from the MacBook working copy at `1d96fbc`, with a new `agents/openai.yaml`; tests run with `node --test`.

### Changed

- `hct-palettes` (T-0841): replaced with the MacBook working copy, which adds a light/dark color system generator (`scripts/system.mjs`, `scripts/system/`), presets (`scripts/preset.mjs`, `scripts/presets.json`), its check (`scripts/check.mjs`), `references/system.md`, `references/system-notice.md`, `references/showcase.md` and `evals/`.
