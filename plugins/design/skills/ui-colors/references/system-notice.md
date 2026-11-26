# Color system engine: provenance and notices

`scripts/system/` is a self-contained copy of a contrast-targeted spectrum engine (MIT, see `scripts/system/LICENSE`):

- `index.js`, `config.js`, `contrast.js`, `roles.js`, `oklch.js`, `alpha.js`, `correct.js`, `anchors.js`: readable ES modules (settings, APCA step placement, roles, OKLCH generator, transparent steps, hue correction, anchors).
- `runtime.json`: an esbuild bundle of the HCT spectrum generator (engine sha256 `a5e029449341ac3305fce2df3fbbdf5f9aa74a7c7731a94b127a41766d95a4e4`, runtime sha256 `849a8e5603017aabdbcd35408e317c88a5609d7fa73810b16e47a607641d642f`). Its source is private and not included.
- `radix-colors.json`: data, not engine code: every `@radix-ui/colors` 3.0.0 scale (MIT, Copyright (c) 2021 Radix; the licence text travels in its `provenance.licenseText`), taken from the npm tarball (sha256 `f6cec1ff1fcc58a45eeefc25d0e6aa1f1659845dbd198963617a86e43d21f3d1`), read only by `system.mjs` for `compare: "radix"` (`references/system.md` › Reports › Radix comparison). Replace it from a newer package as its `provenance.rebuild` says, never by hand.

The bundle inlines third-party code whose notices travel inside it and must stay with it: colorjs (MIT, Lea Verou and Chris Lilley), ultimate-tokens (MIT), `@stdlib` math (Apache-2.0) and a Go-derived `atan2` (BSD). Do not strip or minify the embedded notices.

Do not edit the copied modules by hand; replace the whole directory from the engine's source to adopt changes, then run `node scripts/check.mjs` (it runs `scripts/system.mjs` on `{}` and a light-dark request, compares the raw HCT ramps with `fixtures/hct-default.json`, checks every contrast floor and output, and proves its checks bite).

## Local changes

None to the engine modules. Everything added in this version lives in `scripts/system.mjs` and `scripts/check.mjs`:
- solids and their labels: `system.mjs` no longer calls `index.js › anchoredSpectrum`, whose last step (`solveSolids`) darkens every family's step 9 until the fixed light label reaches 4.6:1 (WCAG 2). Its `prepare()` repeats `anchoredSpectrum` without that step (the same `applyAnchors`, `shapeKeys`, `deriveKeys`, `deriveNeutral` calls from `anchors.js`, and it returns their `pins`), then `solveSolidLabels()` solves each family's solid with APCA, white first except the bright-hue window (yellow, amber, lime: dark label at the cusp), with a visibility guard and the dark-label cusp, rebuilds steps 10–11 as an even APCA run from step 9 to step 12 (`respace`), and holds the control border at `apca.ui` (`references/system.md › Contrast model`). `solveSolids` itself is unchanged and unused by the CLI; when adopting a new engine, check `anchoredSpectrum` for steps `prepare()` should mirror;
- APCA only: every contrast decision in `system.mjs` and `check.mjs` (solids, hovers, control border, series floors, the contrast matrix, the CLI line, the showcase) uses `contrast.js › apcaLc` unchanged, the foreground as its text argument, at thresholds in `system.mjs › APCA_DEFAULTS` (the `apca` request key overrides them). WCAG 2 ratios survive only as the matrix's informational `ratio`;
- CSS notation: the engine can leave a lightness such as `7.45e-9` in a step's CSS (an anchored ramp's black step 12 in a contrast mode); `system.mjs` rewrites such a step in fixed notation so every consumer can parse it;
- anchor colors in any space: `anchors.js › parseAnchorColor` already read `oklch()`, `oklab()`, `color(srgb | display-p3 | xyz …)` and `rgb()` without clipping to sRGB, so no engine change was needed. `system.mjs` turns tagged colors into those strings, rejects unreadable or translucent ones (exit 2) and clips a color outside the mode's `target` gamut by OKLCH chroma before the engine sees it, so solids are solved on what will be shown;
- the contrast matrix, series CVD report, tonal map and tonal agreement are computed from the engine's output; none changes a color.
- the neutrals split (`neutrals`, `references/system.md › Neutrals`): `system.mjs` runs the engine once per distinct neutral spec (settings.grays for a Radix grey, mat/tint/neutralFrom for a tinted neutral, the lifted page tones for the surface) and takes that family; ground, ink and surface anchors reuse `anchors.js › applyAnchors` unchanged on a one-family stand-in (its own `ground`/`ink` end pins); the split roles are written over `index.js › roleVariables`' output (`SPLIT_ROLES`, `selectionVars` with surface and ink references). No engine module changed; with the key absent every path is the one-neutral system's, byte for byte (`check.mjs` holds a digest of the default output in `fixtures/default-digest.json`).

## Two HCT bundles

The skill carries two HCT/CAM16 implementations built from private sources: `scripts/system/runtime.json` (the 12-step spectrum engine) and `scripts/generate.cjs` (the source-palette generator behind the tonal 050–950 layer). They share the HCT model but not code, and unifying them would need their sources, which aren't here. `system.mjs` seeds each tonal family with the family's solved light step 9 (after the APCA solid solve: a dark-label family's seed is its cusp solid), in the same output gamut as the ramps.

**How far apart they are.** `system.json › diagnostics.tonalAgreement`: for every mode, family and step, the tonal stop nearest the step's tone, compared on hue and chroma only (ΔE OKLab × 100 without the lightness term, since stops sit up to ~2.5 tone apart). Default request (ramp shape base 76, keyIntensity 200; per-family solid labels):

| Mode | ΔE hue+chroma mean / p95 / max | Hue ° mean / p95 / max |
|---|---|---|
| light | 2.92 / 8.5 / 18.43 | 2.37 / 5.67 / 7.77 |
| dark | 3.31 / 10.31 / 14.9 | 2.55 / 6.07 / 8.36 |
| light-contrast | 2.55 / 7.4 / 12.54 | 1.84 / 4.17 / 4.88 |
| dark-contrast | 3.52 / 13.32 / 33.15 | 2.61 / 6.46 / 9.59 |
| dim | 3.5 / 9.91 / 16.02 | 2.47 / 6.41 / 8.95 |

Per family (light), mean / max: cyan 2.90 / 7.43, indigo 3.40 / 9.73, plum 3.37 / 9.45, crimson 3.30 / 8.42, tomato 3.50 / 7.49, orange 2.15 / 5.13, amber 2.64 / 10.58, yellow 3.03 / 16.09, lime 3.79 / 18.43, grass 3.19 / 8.30, jade 2.69 / 7.12, teal 2.79 / 6.60, gray 1.25 / 1.89. These are after the APCA solve (white first, bright hues at their cusp, key run 9–12 rebuilt): the larger maxima are the cusp solids — yellow, amber and lime in every mode, and grass at its Display P3 cusp (chroma 0.37) in dark-contrast, the 33 — whose chroma is far beyond the tonal envelope's.

**Where it comes from.**
- *Chroma*, most of it: the tonal recipe keeps 60% of the seed's chroma under a falloff envelope (`tonal.base`, default 60), while the ramps' chroma follows their own shape (muted steps 1–8, punchy 9–12 under the skill's base 76 / keyIntensity 200). No single envelope follows both: `tonal: { base: 100 }` gives light 2.28 / 8.11 / 11.93 and dark 4.03 / 11.10 / 12.64 (with the engine's flat ramp it used to bring the mean under 1.5). The default stays 60: it is the source-palette recipe's own envelope, not a disagreement between the HCT cores.
- *Hue*: both cores hold HCT hue, but the 12-step engine already hue-balances its ramps (`hb`), and the tonal recipe used to hue-balance the seed a second time. That second pass moved dark yellow and orange stops up to 11.3° (dark mode, hue max) away from the ramps. The tonal scale now defaults to `hueBalance: false` (dark hue max 11.31° → 7.13°, light hue mean 2.39° → 2.27°); `tonal: { hueBalance: true }` restores the previous output. The remaining few degrees are the ramps' own per-step hue drift, which a single fixed-hue tonal family doesn't follow.
- *Seed*: seeding from the engine's raw (unsolved) step 9 or from its HCT hue/chroma/tone instead of the solved solid made no measurable difference (mean within 0.1).

Read the tonal scale as a related brand scale, not a second copy of the ramps; `tonalMap` names the nearest stop for every role step.
