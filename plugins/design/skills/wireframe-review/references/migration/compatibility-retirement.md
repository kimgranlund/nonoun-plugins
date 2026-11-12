# Compatibility retirement

Status: retired on 2026-11-12 (T-0844). This skill owns its UI kit; nothing is mirrored from or forwarded to another skill.

## What changed

- The files once listed in `ui-compatibility.json` are the kit's own source here. `ui-compatibility.json`, `ui-kit.lock.json` and `scripts/sync-ui-kit.mjs` are gone, and `loadUI()` returns the local kit (`scripts/kit.mjs`) with no lock or mirror check.
- The kit modules the scripts call were moved in: bundled fonts, `assets/ui-runtime.js`, font and icon CSS writers, catalog collection and the bounded browser resolver.
- The forwarding entries and `scripts/run-ui-check.mjs` were removed. Six checks named by the generation and revision docs or by the dedicated contracts were moved in as real scripts: `check-standalone-token-refs`, `check-select-contract`, `observe-select`, `check-native-patterns`, `check-control-boundary-contrast` and `check-style-contract`.
- The Maison geometry is generated from `ui-geometry` by `scripts/generate-geometry.mjs`.

[ownership.json](ownership.json) lists every file in the skill with its treatment: kit source or review source. Historical evidence under `references/reports/` and frozen evaluations keep their original meaning and paths; old frozen scripts may require their original corpus.
