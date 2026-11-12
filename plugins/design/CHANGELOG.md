# Changelog

The design plugin, newest first. Releases before this file are recorded in the repository [CHANGELOG.md](../../CHANGELOG.md).

## [Unreleased]

### Added

- `ui-geometry` (T-0841): derives every UI length from a root font size and one unit across four tiers (controls, collections, containers, layout) and fits an existing project to the nearest system. Imported from the MacBook working copy at `1d96fbc`, with a new `agents/openai.yaml`; tests run with `node --test`.

### Changed

- `hct-palettes` (T-0841): replaced with the MacBook working copy, which adds a light/dark color system generator (`scripts/system.mjs`, `scripts/system/`), presets (`scripts/preset.mjs`, `scripts/presets.json`), its check (`scripts/check.mjs`), `references/system.md`, `references/system-notice.md`, `references/showcase.md` and `evals/`.
- `wireframe-review` (T-0844): owns a trimmed UI kit and no longer needs `base-ui` or `mathematical-design-system` beside it. The mirrored kit files are its own source, `scripts/kit.mjs` vendors the base-ui modules its scripts call (fonts, runtime, catalog, browser resolver), and `ui-kit.lock.json`, `ui-compatibility.json`, `sync-ui-kit.mjs` and 48 forwarding checks are removed. Six checks the docs name moved in as real scripts. `scripts/generate-geometry.mjs` regenerates the Maison geometry from `ui-geometry` `derive.mjs --json` (product md/md: S 20, I 6, h 32). The review shell's intent disclosure now carries its contract classes, and artifact verification compares the embedded foundation with the full bundle, so `generate.mjs` builds the example manifest again.
