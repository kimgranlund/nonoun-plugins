---
name: ui-colors
description: Generate HCT color - source palettes (Base 050–950, Primes, balanced sets) or a full light/dark color system for a design system, with APCA-placed 12-step ramps, alpha steps, roles, brand anchors, contrast-solved solids, chart data series that hold in every mode, a per-mode report of which pairs fail and a specimen sheet. Not for paint, glass or materials (ui-materials), lengths, radii or shadow geometry (ui-geometry) or a multi-source showcase (ui-showcase-bento).
---
# UI colors

Two offline generators that share the HCT/CAM16 model: source palettes for a swatch library, and a ready-to-use color system for a UI. Use it to generate color, not to edit existing tokens or answer one conversion or contrast question.

Contents: [Route](#route) · [Invariants](#invariants) · [Commands](#commands) · [Vocabulary](#vocabulary) · [Gamut](#gamut) · [Color system](#color-system-scriptssystemmjs) · [Source palettes](#source-palettes-scriptsgeneratecjs)

## Route

| The user wants | Do | Read | Load when |
|---|---|---|---|
| A color system a UI can use directly: light, dark, contrast and dim modes of 12-step ramps placed by APCA contrast, alpha steps, roles, brand anchors (paper, ink, brand colors), contrast-solved solids, data series, a mode-independent tonal scale; CSS (sRGB + P3), JSON, DTCG, optional Tailwind and Figma | `scripts/system.mjs` ([below](#color-system-scriptssystemmjs)) | [system.md](references/system.md) | Writing or reading a request, or explaining an output field |
| Source palettes to study, hand off or import: one hue family or a balanced set, Base stops 050–950, seven Primes, system and Material palettes | `scripts/generate.cjs` ([below](#source-palettes-scriptsgeneratecjs)) | [requests.md](references/requests.md) | Building the request JSON |
| A system from named brand colours, each kept exact | `system.mjs`, anchors + `brandExact` | [Brand colours](references/system.md#brand-colours) | The user lists brand colours |
| A fixed brand set of seed colors as source swatch ramps (no modes or roles) | `scripts/preset.mjs` ([palette presets](#palette-presets-scriptspresetmjs)) | `scripts/presets.json` | Adding or choosing a preset |
| A one-page specimen sheet of a color system | `system.mjs` with `showcase: true` | [showcase.md](references/showcase.md) | Making or reviewing the sheet |
| What a color word means here (ground, surface, step, mode, theme…) | Answer from the vocabulary | [terms.json](references/terms.json) | A term is ambiguous or a sibling skill uses it differently |
| Why the two generators disagree slightly | — | [system-notice.md](references/system-notice.md) | Comparing a source palette with the system's tonal scale |
| Engine provenance, policies, maintenance | — | [engine.md](references/engine.md) | Changing or auditing the bundled generator |

Words that mean the system generator: *theme*, *light and dark*, *modes*, *roles*, *tokens*, *CSS variables*, *anchor my brand color*, *Radix-style 12 steps*, *alpha / transparent steps*, *data or chart colors*, *DTCG*, *Figma variables*, *which pairs of a new palette pass APCA*. Words that mean source palettes: *Base*, *Primes*, *050–950*, *max chroma*, *balanced N colors*, *Material palette*, *a tonal ramp from one color* (no modes, roles or tokens). Not this skill: mapping or editing tokens an app already has, one color conversion, one contrast question about given colors, fonts, chart code; paint and materials (ui-materials), lengths and shadow geometry (ui-geometry), a combined showcase (ui-showcase-bento). If it is unclear, ask one question: "a source palette set (Base/Primes) or a ready-to-use light/dark color system with roles?" Routing cases: `evals/triggers.json`.

## Invariants

- **Display P3 by default** in every generator; sRGB only when the user asks ([Gamut](#gamut)). Checked by `check.mjs` (default targets).
- **Generated, not derived.** Every variable is a color or an alias, never `color-mix()`, `calc()` or relative color syntax. Checked by `check.mjs` (generated).
- **Light and dark are generated separately**, never inverted; every mode shares one contract. The CLI rejects a mode that breaks it (exit 2).
- **Contrast is reported, never fixed.** APCA only, at its most lenient level per use; a miss is reported as found. Checked by `check.mjs` (floors, contrast matrix).
- **Vocabulary is data.** Terms, roles and the names the system emits stay in step with [terms.json](references/terms.json). Checked by `check.mjs` (terms).
- **No project or brand names of any host project** appear in this skill. Checked by `check.mjs` (names).
- Applying the skill does not authorize editing an existing app, theme or stylesheet. Judgement: no check holds it.

## Commands

Run `node /absolute/path/to/ui-colors/scripts/check.mjs` after changing `scripts/system.mjs`, `scripts/system/`, this file, a reference or `terms.json`. Done means it exits 0. It regenerates the default and a light-dark system in a temporary directory, checks the fixture, contrast floors, CSS and adapters, the neutrals split, a byte-identical default (a recorded digest), the showcase, the vocabulary, request-key closure, the links and the invariants above, and runs negative controls that must fail ([system.md › Checks](references/system.md#checks)).

## Vocabulary

[terms.json](references/terms.json) is the vocabulary as data: each concept (source palette, base stop, Material palette, family, accent, neutral, ground, surface, ink, step, alpha step, tonal scale, tonal stop, role, primary, secondary, status, scheme, mode, theme, brand, anchor, endpoint and others) with its definition, intent, what it is not (including the sibling skills' meanings of shared words), accepted aliases, phrases to avoid and the names it owns, plus a catalogue of every role the system emits. Use its terms in reports and when reading a user's request.

## Gamut

Display P3 is the default for every generator: the color system targets `display-p3` (sRGB values first, a P3 upgrade under `@media (color-gamut: p3)`), `preset.mjs` defaults to `display-p3`, and every `generate.cjs` request this skill writes sets `"target": "display-p3"` (the executable's own default is sRGB, so always write the key). Use sRGB only when the user asks ("sRGB only", "for email", "for print", an sRGB-only tool) — then set `target: "srgb"` (`settings.target` for the system). Mention the gamut once in the report; don't ask about it.

## Color system (`scripts/system.mjs`)

Write a request JSON per [the system contract](references/system.md) (`{}` is the default system), then run:

```sh
node /absolute/path/to/ui-colors/scripts/system.mjs --request request.json --out NEW_OUTPUT_DIRECTORY
```

Defaults, without asking: modes `light`, `dark`, `light-contrast`, `dark-contrast` (auto under `prefers-contrast: more` in their own scheme) and `dim`; 12-step ramps, alpha steps, roles, series and sequential ramp per mode; the mode-independent tonal scale (050–950); sRGB values with a Display P3 upgrade; class selectors; CSS, JSON, DTCG and a preview; per mode an APCA contrast matrix (thresholds overridable with `apca`), the series under simulated color-vision deficiency and the nearest tonal stop per role step. Opt-ins: `primes`, `diverging`, `tailwind`, `figma` (roles as variable aliases), `lightDark`, `split` (per-mode CSS files), the request preset `preset: "minimal"` (light and dark only, no alpha, no tonal), `tonalRoles`, `familyNames: "index"`, `selectors: "attribute"`, `scope`, `emphasis` (selection strength 0–2), `showcase` (a 1280 × 960 specimen sheet, [showcase.md](references/showcase.md)), `neutrals` (the neutral split into ground, surface and ink families, [system.md › Neutrals](references/system.md#neutrals)), `translucent` (requested translucent roles, [system.md](references/system.md#requested-translucent-roles)).

Light and dark are generated separately, never inverted. Every mode shares one contract (families, steps, role names), so a different palette per mode goes through `modes.<id>` overrides (settings, roles, anchors, endpoints), and an anchor's `dark` color pins dark exactly. Hue and hue set stay top-level (they rename families) unless `familyNames: "index"` names families `hue-1…hue-N`, which lets a mode change them; the CLI rejects a mode that breaks the contract (exit 2).

Map natural language onto the contract (ask only about choices that change the output materially):

- a hue → `settings.hue`; "Radix hues" → `settings.hueSet: "radix"`; "a different hue in dark mode" → `familyNames: "index"` plus `modes.dark.settings.hue`
- "sRGB only" → `settings.target: "srgb"`; "fast / no HCT" → `settings.generator: "oklch"`
- "white page" → `settings.toneMax: 100`; "pure black dark mode" → `modes.dark.settings.darkTone: 0`; "pure white and black" → `endpoints`
- "brand blue #0a4dff" → an anchor on `primary` (`dark` for its dark twin); a P3 or OKLCH brand color → the anchor's `value` as `color(display-p3 …)`, `oklch(…)` or `{ colorSpace, components, alpha: 1 }`; "our paper and ink" → `ground` and `ink` anchors
- "dark only for hero sections" → `autoDark: false` + a forced extra mode; a role by OKLCH hue → `oklch:84`
- "warm page, cool cards", "paper and cards", "ground/surface", "cards that lift off the page" → `neutrals` (`{ "ground": { "from": "Sand" }, "surface": { "from": "Slate" } }`, a Radix gray or a tinted `{ tint, neutralFrom }` each); "swap them in dark" → `cross: true`; an exact card color → a `surface` anchor
- "simulate deuteranopia" → `settings.cvd: "deutan"`; "just light and dark" → `extraModes: false`; "a sepia mode" → a custom entry in `extraModes`
- "data-color-mode attributes" → `selectors: "attribute"`; "light-dark()" → `lightDark: true`; "Tailwind" / "Figma variables" → `tailwind` / `figma`; "smaller CSS" → `preset: "minimal"` or `split: true`
- "tonal stops for my roles" → `tonalRoles: true`; "quieter / louder selection" → `emphasis` 0 / 2; "a showcase / specimen sheet / one-page overview" → `showcase: true`

Deliver `preview.html`, `system.css`, `system.json`, `tokens.dtcg.json` (plus the adapters and split files requested); open the preview when a browser is available. Offer `showcase: true` when the system will be reviewed or shared, or the user wants everything on one page: `showcase.html` is 24 specimens in 8 groups at 1280 × 960, colored only by the run's variables, with every failure in `system.json` flagged. View it at that size before describing it, or say it wasn't viewed.

Before you report, read:

1. The CLI's summary line, per mode: weakest solid's APCA Lc, contrast pairs under their APCA threshold, the series' smallest CVD ΔE, and any `WARNING`.
2. In `system.json`, each mode's `apca` thresholds and anchor report (`inOrder`, `inRange`, `gamut.clipDE`).
3. `solidLabels` (each family's light or dark label — white first —, `moved`, `hoverRoom`, `cusp`, `whiteRejected`) and `solidLabelContrast` (APCA Lc against that label, ≥ `apca.solid`: 45, 60 in contrast modes). Text on a role's solid uses `--colors-<role>-on-solid`. Yellow, amber and lime (the `brightHues` window) always take dark text on a cusp-bright solid.
4. `keyRun` (9–12 evenly spaced in Lc, and any `deviations`), `contrast.summary.failures`, `hover.summary.failures`, `seriesCvd`, the series' `lcOnSurface` and contrast modes' `targetLift`.
5. With `neutrals`: each mode's `neutralSources` and `separation` (surface 1 vs ground 1, OKLab ΔE ≥ 2).

Then report modes, generator, hue set, gamut, roles as resolved (an anchor can move a role), any anchor that broke contrast order or was clipped, and the contrast and CVD misses as found. They are reported, never fixed, so don't claim a pair passes because the steps are APCA-placed; raise `apca` for body text.

## Source palettes (`scripts/generate.cjs`)

Use the bundled offline generator; do not estimate swatches, translate hue angles between color spaces, or recreate the math in prose. It includes the originating project's float64 color core, HCT recipe, balanced tone-aligned Prime scheduler, HCT hue balance and Prime brightness bias. Node.js 22+ is the only runtime requirement; no repository, network or npm installation is needed.

### Palette presets (`scripts/preset.mjs`)

A fixed brand set that isn't an evenly spaced hue spectrum runs through `preset.mjs`, as a palette preset: one source palette per seed color, each seed kept exact, merged into one output in the generator's shape (`palettes.css` with `--color-<id>-base-050…950` and the Primes, `palettes.json`, `sources.json`, `preview.html`).

```sh
node /absolute/path/to/ui-colors/scripts/preset.mjs --list
node /absolute/path/to/ui-colors/scripts/preset.mjs --preset field-operator [--request extra.json] --out NEW_OUTPUT_DIRECTORY
```

`field-operator` is eight colors after Teenage Engineering's field and operator palettes (field blue, orange, brown, grey; op red, blue, green, yellow); its defaults are full Base and Prime chroma with hue balance off, so the ramps keep the brand colors' punch. `extra.json` may override the generator keys that apply per palette (output, target, base, prime, toneMin, toneMax, step, falloff, hueBalance, primeBrightnessSteps, primeSpacing). Palette presets live in `scripts/presets.json`; add one by adding an entry. A palette preset is not the system's request preset (`preset: "minimal"`). The twelve-hue spectrum stays `generate.cjs`'s own `preset: "project"`. A source ramp peaks its chroma at mid-tone, so a light brand color (a yellow) appears exactly as its seed but not as a ramp stop; for a usable ramp that contains it exactly, anchor it in the color system instead.

### Understand the request

Recognize `$ui-colors` and natural shorthand such as `/ui-colors 230deg max chroma`. Slash text is a request pattern, not a promised host slash-command registration. Bare angles are **HCT/CAM16 hue**, not OKLCH hue. Interpret `2/3/4/6/8/12 colors` as the number of core palettes; optional system and Material palettes are additional.

Examples:
- `230deg max chroma` → one maximum-chroma Base range.
- `230deg base + primes` → one project-envelope Base range plus seven Primes.
- `230deg 6 colors balanced system material` → six core palettes, four feedback palettes and one tinted Material palette.
- `hues 20,140,260 balanced primes only` → three explicit hues, Prime output only.
- `project defaults` → the project's exact twelve OKLCH seeds, four system seeds and inherited-hue Material palette, with Base + Primes.
- `100deg base + primes hue balance off original prime center` → disable hue balance and use zero brightness bias.
- `230deg 4 colors balanced base=70 prime=90 target=display-p3` → explicit factor and gamut overrides.

Ask **one compact clarification** when the output composition is unspecified and the answer would help: “Base range only, Base + seven Primes, or Primes only—and include four system palettes or a neutral/tinted Material palette?” If a palette system is requested without a count, offer 2, 3, 4, 6, 8 or 12. Ask only about missing choices; do not re-ask explicit choices. A clear single-range request can run immediately. If the user says to use defaults, use one core palette, Base only, no extras; for `project defaults`, use 12 + 4 + 1 and Base + Primes. Multiple core palettes default to balanced.

A “single palette” is one hue family; “Base + Primes” selects two sample groups from that family. Do not confuse those dimensions. The Material palette here is one neutral or lightly tinted source ramp: not a Material Design semantic theme, and not a material in the ui-materials sense (Flat, Physical, Glass), which is how a part is painted.

### Generate

Default hue balance on, balanced HCT Prime tone alignment and Prime brightness +1. Use `primeSpacing:"tone"` for the retained uncapped HCT tone recipe or `primeSpacing:"distance"` for equal OKLab-distance spacing. For explicit maximum-chroma requests, default hue balance off and uncapped tone-only Prime so the boundary remains available. Honor explicit overrides, and disclose when correction changes a balanced or maximum envelope.

Read [the request contract](references/requests.md) to construct the input JSON. It defines defaults, options, max-chroma behavior and balance limits. Write a request file, then run:

```sh
node /absolute/path/to/ui-colors/scripts/generate.cjs --request request.json --out NEW_OUTPUT_DIRECTORY
```

Resolve the skill directory from this SKILL.md's location; do not assume the project checkout exists. The output directory must be new. If Node is unavailable, report that blocker; do not fabricate generated results or silently install a runtime.

Deliver `preview.html`, `palettes.css`, `palettes.json`, and `sources.json`. Open the preview when a local browser is available. Check output counts, requested Base/Prime groups, tone-order diagnostics and any Prime center limiting before describing the result. Preserve float64 JSON/CSS values; hex may be an additional rounded sRGB presentation only. Do not reinterpret Display P3 values as sRGB hex.

Report the selected hue model, core/additional palette counts, gamut and balance policy. “Maximum” is the bounded numerical HCT gamut boundary at each Base tone, not maximum chroma at every Prime sample. “Balanced” aligns Base tones and feasible CAM16 chroma across core hues; it does not certify equal perceived colorfulness or accessibility. Surface these distinctions briefly when relevant.

Keep original tagged source input and requested HCT intent separate from fitted generation seeds. `sources.json` contains reusable project-format sources; `palettes.json` is a generated-output document, **not** an importable theme/session. Applying this skill does not authorize changes to an existing app, theme, semantic mappings or UI.

For engine provenance, policies and maintenance, read [engine contract](references/engine.md). The build manifest records source hashes; don't edit the bundled generator manually.
