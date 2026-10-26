---
name: hct-palettes
description: Generate HCT source-color palettes, 050–950 Base ramps, independent Primes, and balanced 2/3/4/6/8/12-color sets with optional feedback and Material palettes. Use for source palette generation, not semantic-token mapping or UI styling.
---
# HCT palettes

Use the bundled offline generator; do not estimate swatches, translate hue angles between color spaces, or recreate the math in prose. It includes the originating project's float64 color core, HCT recipe, balanced tone-aligned Prime scheduler, HCT hue balance and Prime brightness bias. Node.js 22+ is the only runtime requirement; no repository, network or npm installation is needed.

## Understand the request

Recognize `$hct-palettes` and natural shorthand such as `/hct-palettes 230deg max chroma`. Slash text is a request pattern, not a promised host slash-command registration. Bare angles are **HCT/CAM16 hue**, not OKLCH hue. Interpret `2/3/4/6/8/12 colors` as the number of core palettes; optional system and Material palettes are additional.

Examples:
- `230deg max chroma` → one maximum-chroma Base range.
- `230deg base + primes` → one project-envelope Base range plus seven Primes.
- `230deg 6 colors balanced system material` → six core palettes, four feedback palettes and one tinted Material palette.
- `hues 20,140,260 balanced primes only` → three explicit hues, Prime output only.
- `project defaults` → the project's exact twelve OKLCH seeds, four system seeds and inherited-hue Material, with Base + Primes.
- `100deg base + primes hue balance off original prime center` → disable hue balance and use zero brightness bias.
- `230deg 4 colors balanced base=70 prime=90 target=display-p3` → explicit factor and gamut overrides.

Ask **one compact clarification** when the output composition is unspecified and the answer would help: “Base range only, Base + seven Primes, or Primes only—and include four system palettes or a neutral/tinted Material palette?” If a palette system is requested without a count, offer 2, 3, 4, 6, 8 or 12. Ask only about missing choices; do not re-ask explicit choices. A clear single-range request can run immediately. If the user says to use defaults, use one core palette, Base only, no extras; for `project defaults`, use 12 + 4 + 1 and Base + Primes. Multiple core palettes default to balanced.

A “single palette” is one hue family; “Base + Primes” selects two sample groups from that family. Do not confuse those dimensions. Material here is one neutral or lightly tinted source ramp, not a Material Design semantic theme.

## Generate

Default hue balance on, balanced HCT Prime tone alignment and Prime brightness +1. Use `primeSpacing:"tone"` for the retained uncapped HCT tone recipe or `primeSpacing:"distance"` for equal OKLab-distance spacing. For explicit maximum-chroma requests, default hue balance off and uncapped tone-only Prime so the boundary remains available. Honor explicit overrides, and disclose when correction changes a balanced or maximum envelope.

Read [the request contract](references/requests.md) to construct the input JSON. It defines defaults, options, max-chroma behavior and balance limits. Write a request file, then run:

```sh
node /absolute/path/to/hct-palettes/scripts/generate.cjs --request request.json --out NEW_OUTPUT_DIRECTORY
```

Resolve the skill directory from this SKILL.md's location; do not assume the project checkout exists. Use an available Node 22+ runtime. The output directory must be new. If Node is unavailable, report that blocker; do not fabricate generated results or silently install a runtime.

Deliver `preview.html`, `palettes.css`, `palettes.json`, and `sources.json`. Open the preview when a local browser is available. Check output counts, requested Base/Prime groups, tone-order diagnostics and any Prime center limiting before describing the result. Preserve float64 JSON/CSS values; hex may be an additional rounded sRGB presentation only. Do not reinterpret Display P3 values as sRGB hex.

Report the selected hue model, core/additional palette counts, gamut and balance policy. “Maximum” is the bounded numerical HCT gamut boundary at each Base tone, not maximum chroma at every Prime sample. “Balanced” aligns Base tones and feasible CAM16 chroma across core hues; it does not certify equal perceived colorfulness or accessibility. Surface these distinctions briefly when relevant.

Keep original tagged source input and requested HCT intent separate from fitted generation seeds. `sources.json` contains reusable project-format sources; `palettes.json` is a generated-output document, **not** an importable theme/session. Applying this skill does not authorize changes to an existing app, theme, semantic mappings or UI.

For engine provenance, policies and maintenance, read [engine contract](references/engine.md). The build manifest records source hashes; don't edit the bundled generator manually.
