# Changelog

The design plugin, newest first. Releases before this file are recorded in the repository [CHANGELOG.md](../../CHANGELOG.md).

## [Unreleased]

### Added

- `ui-geometry`: a length is a line a·n + b in the scope's font size, and a preset constant may be one (`{ "a": 2, "b": -8 }`) as well as a multiple of the unit q. An exact preset (`exact: true`, unit 1px) rounds nothing; `affine` is the one shipped (S = 2n − 8, I = n − 9, h = 4n − 26, r = n − 6), with 30 rows held to a measured kit's own lines by a test. `scripts/derive.mjs` gains `--lines` (each length's line), `--whole` (where each length is whole px with nothing snapped, exit 1 if any is not) and `--emit css|json` (custom properties with exact em fallbacks), and presets gain `cardRadius: 'level'`, `spacing.fieldGap`, `spacing.popover`, `spacing.dialog`, `grid`, `marks.sizes` (check box, switch and range at three sizes), `widths.header` (a shell's header, with the docking width), `reasons`, `source` and `fractional`. `scripts/fit.mjs --lines` recovers each length's line from lengths measured at two or more n and says whether one unit holds them. `references/equations.md` › 21 has the model, and the generated `references/lines.md` every row as a line for the standard, ladder and affine presets.

### Changed

- `ui-geometry`: `SKILL.md` states the line as the primitive and the unit as one way to give it. **The default preset is `affine`**, no longer `ladder`: `scripts/derive.mjs` with no `--preset` answers in the exact system, where q is 1px, so its q column and `--card <d>` are px. A unit preset named by `--preset` prints what it printed before. `ui-frameworks` `scripts/tokens.mjs` and `component-variants` `scripts/geometry.mjs` now name `--preset ladder`, so their output is unchanged. The message for a refused `cardRadius` names three values.

## [0.6.0] - 2026-11-22

### Changed

- `explore-variants`, formerly `ui-explore-variants`: renamed and synced from the MacBook copy at `8ab4c62`. The skill explores any open question with several answers, not only a UI layout: `SKILL.md` holds the method, and `references/` holds one recipe per subject (`ui.md` with the UI rules that were in `SKILL.md`, `architecture.md`, `strategy.md`, `creative.md`, `review.md`), each naming the specimen, the fixture and the stress. A variant that cannot be operated carries a fourth fact, Depends on, and its claims are marked measured, sourced, estimated or assumed. The feedback JSON's `skill` is `explore-variants`; a JSON from a page built before the rename is still read. The module's storage keys and fallback aspects changed with it.

### Fixed

- `explore-variants`: "Send feedback" is appended to the page's container, so it no longer hides with an earlier round's wrapper. `scripts/check.mjs` gains two checks, each with its control.

## [0.5.1] - 2026-11-20

### Changed

- `AGENTS.md` (T-0863): the Checks section names the Playwright scratch project and the commands for the two browser checks, `ui-explore-variants` `scripts/check.mjs` and the inspector panel's `examples/test.mjs`. Both ran green here (33/33 and 134/134).

### Fixed

- `ui-frameworks` (T-0862): `scripts/tokens.mjs` (and `scripts/panda.mjs`, which builds on it) find `ui-colors`, `ui-geometry` and `ui-materials` inside the plugin's own `skills/` folder, so they run without copies in `~/.claude/skills`. One helper, `scripts/siblings.mjs`, tries `SKILLS_DIR`, then the folder beside the skill, then `~/.claude/skills`, and names every place tried when none has the file. A deliberate difference from the MacBook source. Generated output is unchanged.

## [0.5.0] - 2026-11-19

### Changed

- `ui-geometry` (T-0856): synced from the MacBook copy at `ec93828`. The ladder preset is the default (30px controls at n = 14), `standard` keeps h = 32 (alias `standard-32`), and the dialog inset is a row, `containers.frame.dialog-inset`; the inspector panel's `geometry-runtime/derive.js` and `provenance.json` are rebuilt with `npm run build`.
- `ui-frameworks` (T-0856): synced from the MacBook copy at `97eee29`, the installed build of its source. Adds components (avatar, calendar, date field, file field, pagination, popover, progress, select, separator, skeleton, stepper, tag, toast and others) with React recipes; the build carries no `checks/`, so `checks/focus-on-top` leaves this copy. The 17 `ui-frameworks` rows in `docs/reports/broken-links-allowlist.md` are gone: those `docs/` links no longer break.
- `ui-explore-variants` (T-0856): synced from the MacBook copy at `406b2db` plus its uncommitted `assets/feedback.js` edit. The page uses plain language; internal names move under Technical details.
- `ui-materials` (T-0856): synced from the MacBook copy at `59d4f4b`. SKILL.md is shorter, and `scripts/check.mjs` checks that delineation writes a face's mark tokens.
- `ui-content` (T-0856): synced from the MacBook copy at `f0bf8a6`. Adds its own check, `scripts/check.mjs`, each rule with a planted fault it must catch.
- `ui-geometry` (T-0855): synced from the MacBook copy at `2b1500a`. The floor for a text line on the line grid is 1.15 again (`references/equations.md`, `scripts/derive.mjs` and its tests); the inspector panel's `geometry-runtime/derive.js` and `provenance.json` are rebuilt with `npm run build`.
- `ui-frameworks` (T-0855): synced from the MacBook copy at `2cf5ee1`. Adds `checks/focus-on-top`, a keyboard check of the focus ring over a joined neighbour, named in `docs/checks.md` and the CSS contract.
- `ui-explore-variants` (T-0855): synced from the MacBook copy at `6e5d784`. Pages can name their own verdicts (`data-verdicts`) and pick one variant per moment (`data-pick="one"`); adds its own check, `scripts/check.mjs` with `scripts/check.page.html`, which tests the feedback module in Chromium and WebKit.
- `ui-interaction-dev` (T-0855): synced from the MacBook copy at `ba2f4c4`. The rule spec cites the W3C WAI forms tutorial on placeholder text.

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
