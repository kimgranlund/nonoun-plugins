# Portable HCT palette skill engine

Version: hct-palettes@4. This source-generation wrapper follows the project's current HCT defaults while retaining explicit tone-only and distance Prime requests.

## Source and build

Canonical implementation lives at `resources/corpus/computation/hct-skill/` in the ultimate-tokens-color-science project. `generate.ts` exposes `normalizeRequest`, `capacity` and `generate`; `cli.ts` writes artifacts. `build.ts ESBUILD_API_PATH SKILL_DIRECTORY` creates a self-contained Node 22 CommonJS executable, preserving vendored license notices and recording every bundled source hash in `references/build-manifest.json`. esbuild 0.25.11 is build-only. The installed skill needs neither the originating repository nor external libraries at execution time. Rebuild deliberately to adopt later engine changes; a hash is provenance/integrity information, not a trust signature.

## Project policies retained

- Conversion: original tagged sources plus float64 XYZ-D65 reference, with Color.js 0.5.2's fixed HCT viewing conditions. No integer RGB intermediate.
- Project defaults: hct-tone@1, Base 60%, Prime 80%, tone 5–100, sampling 25, falloff 1.5, vibrancy 50, model-prime@4, hue balance enabled and Prime brightness bias 0 (unbiased center). Explicit max-chroma requests default hue balance off and retain tone-only Prime to preserve their boundary.
- Base positions: 50 through 950 inclusive in increments of 25 (37 samples), padded only for display. Tone is `100*(max-(max-min)*(stop-50)/900)`, with normalized settings endpoints. Stop 500 is T52.5 under defaults, not the source seed tone.
- The source-envelope recipe requests source CAM16 chroma multiplied by `(1-distance^falloff)*Base/100`, where distance is `abs(stop-500)/450`, then fits gamut at fixed HCT hue/tone.
- Primes: brightest, brighter, bright, prime, dim, dimmer, dimmest. The default fits HCT chroma at seven shared CIELAB tone targets derived from the Base envelope, then caps OKLCH chroma under a shared bright-end envelope by refitting HCT at fixed hue and tone. `primeSpacing:"tone"` retains the uncapped tone-only version; `"distance"` retains the earlier OKLab-distance scheduler. Actual distances and tone gaps remain reported; equal numeric chroma does not guarantee equal perceived colorfulness.
- System seeds: original opaque OKLCH L0.62/C0.16, hues 255/155/75/25 for Info/Success/Warning/Danger.
- Tinted Material: foundation OKLCH L0.6/C0.08, hue inherited from the first core source using the project's source-policy resolver; fallback authored hue235 for an achromatic parent. Neutral Material sets seed chroma to zero. These are additional source palettes, not semantic schemas.
- `preset:project` reuses exact core seeds from foundation-twelve.theme.v2.json (L0.62/C0.16, OKLCH hue235 + 30-degree steps), system seeds, Material dependency and authored Base 50% / Prime 85% factors. It matches source-palette generation for that file, not a potentially different startup session.

## New wrapper policies, not historical project behavior

Custom HCT intent defaults to H230/C48/T60. The requested intent is retained separately; conversion to a supported fitted tagged seed is explicit. Numeric C beyond gamut is reduced; seeds are not falsely reported as exact requested HCT colors.

Boundary solver: start an upper CAM16 chroma at64, double through1024 until the existing `fitHct` solver reports reduction; recover its fitted chroma. The original solver performs30 bisections and uses an RGB tolerance of1e-9. Exact tone0/100 uses neutral black/white. This is a bounded numerical fixed-hue gamut search, not an analytic or independently proven global maximum. Failure to bracket is an error, not a fallback cap.

`hct-gamut-boundary@1` replaces core Base chroma with each tone's fitted boundary times the Base factor. Balanced sets use the minimum boundary across core hues. It is intentionally different from the source-envelope recipe and does not get inserted into the application's registry.

`hct-balanced-envelope@1` retains the common seed envelope and caps it at each tone to the minimum core boundary. Before optional hue balance, corresponding Base outputs share feasible requested CAM16 chroma, within solver tolerance. Prime scheduling remains independent, with its own feasible center and brightness bias. Neither balancing nor angular hue spacing certifies equal perceived colorfulness or categorical distinguishability.

Generated `palettes.json` contains requests, recipe IDs, source graph, source intent, samples and diagnostics. CSS is a projection of its selected groups. `sources.json` is a schemaVersion2 source document; it cannot preserve wrapper generation settings when imported alone. Keep palettes.json/request alongside it to reproduce those settings. Do not feed wrapper-only recipe IDs into theme/session schema fields. No semantic theme or session is authored.

## Verification

Run the narrowly scoped `node resources/corpus/computation/hct-skill/verify.ts`. It verifies canonical project parity, all requested set counts, stop/Prime identities, both gamuts, max-boundary membership, tone order, balanced chroma and invalid requests. Skill packaging is additionally checked by running the bundled CLI in a new output directory and checking its artifacts. These are numerical/package checks, not accessibility or perceptual-equality certification.

## Appearance adjustment and brightness

`hueBalance` selects `hct-hue-balance@1` or off. It is enabled by default except for explicit max-chroma requests; those preserve their strict boundary unless the user opts in. The numerical implementation is bundled from `recipes/hct-hue-balance.ts` and runs once on the final Base envelope, including the wrapper's balanced/max paths. Prime includes it in both trajectory and final sample generation.

With HCT hue H, CAM16 chroma C, and CIELAB tone T:

```
s(x) = clamp(x,0,1)^2 * (3 - 2*clamp(x,0,1))
w = (0.02 + 0.98*exp(-0.5*(wrap180(H-100)/28)^2))
    * (1-s((T-20)/55)) * s((C-1)/7)
H' = wrap360(H-12*w); C' = C*(1-0.08*w); T' = T
```

Fit the result to the target gamut at fixed HCT hue/tone. This is art direction, not an independently validated improvement. Highlights at/above T75 and achromatic samples are unchanged. Final corrected output need not retain identical chroma across hues or lie on the original maximum boundary. Provenance is in each sample's `postprocess` record.

`primeBrightnessSteps` defaults to 0 (integer 0–2), centering Prime on the Base envelope midpoint; 1 and 2 are explicit requests for one or two shared tone intervals brighter. With a nonzero request in the default tone recipe, the Base envelope midpoint rises by that many shared tone intervals; the center clamps to leave three steps on each side. In retained distance mode, the center advances that many OKLab-distance steps along the fitted trajectory. Neither changes Base or source coordinates. The numerical implementation and cache key are bundled from `recipes/perceptual-prime.ts`. Missing fields in older saved project themes/sessions retain their historical choices; this wrapper's new request defaults are explicit in generated output. See [the HCT Prime tone contract](../recipes/HCT-PRIME-TONE.md).
