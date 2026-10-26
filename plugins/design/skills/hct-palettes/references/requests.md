# Request contract

Write a UTF-8 JSON object. Natural-language attributes are interpreted by the agent; the executable accepts JSON, not arbitrary natural-language text. Unknown keys and invalid combinations reject.

| Key | Values / default |
|---|---|
| `hue` | HCT degrees, default 230; negative/wrapped angles accepted within ±36000 |
| `hues` | Explicit distinct HCT angles; exclusive with `hue`; length determines count unless count supplied |
| `count` | 1, 2, 3, 4, 6, 8 or 12; default 1. Without explicit hues, angles are evenly distributed starting at `hue` |
| `chroma` | CAM16 chroma 0–200, default 48; or `"max"` |
| `tone` | Seed CIELAB L* 2–98, default 60; independent of Base stop-500 tone |
| `balance` | Boolean; defaults true for multi-core sets, false for single palettes |
| `output` | `"base"` (default), `"base-primes"`, `"primes"` |
| `system` | Boolean, default false; adds Info, Success, Warning, Danger |
| `material` | `"none"` (default), `"tinted"`, `"neutral"`; adds at most one palette |
| `target` | `"srgb"` (default) or `"display-p3"` |
| `base` | Base chroma percentage 0–100, default 60; max mode defaults 100 |
| `hueBalance` | Boolean, default true; max-chroma requests default false to preserve the boundary. Explicit true applies appearance adjustment after the Base envelope |
| `primeBrightnessSteps` | Integer 0–2, default 0 (unbiased center); 1 or 2 shifts Prime one or two shared tone intervals brighter |
| `primeSpacing` | `"balanced"` (default, aligned HCT tone plus shared chroma envelope), `"tone"` (retained tone-only recipe), or `"distance"` (retained equal OKLab-distance policy). Explicit max-chroma requests default to `"tone"` to preserve boundary behavior. |
| `prime` | Independent Prime percentage 0–100, default 80; max mode defaults 100 |
| `toneMin`, `toneMax` | Base tone endpoints, default 5 and 100; 0–100 with at least 10 difference |
| `step` | 25 (default, 37 stops) or 50 (19 stops) |
| `falloff` | Base envelope exponent 0.2–5, default 1.5; irrelevant for max Base curves |
| `source` | One opaque project tagged color `{colorSpace,components,alpha:1}`; exclusive with HCT hue/chroma/tone fields and multi-core sets; retained exactly |
| `preset` | Only `"project"`: exact twelve project seeds, default system=true, material=tinted, output=base-primes. Do not combine with hue/hues/count/chroma/tone/balance/source. Output/settings/extras may be overridden explicitly |

Supported tagged source spaces: srgb, display-p3, xyz-d65, xyz-d50, oklab, oklch. HCT is an input intent in this wrapper, not a supported tagged source-space identifier. The source must also satisfy the engine's opaque SDR generation domain.

The all-default custom HCT seed (H230/C48/T60) is a **new skill convenience**, not the project's historical authored source. `preset=project` is the route for exact project parity. Its angles are authored OKLCH and must not be relabeled HCT.

## Examples

One gamut-boundary range:
```json
{"hue":230,"chroma":"max","output":"base"}
```
Six balanced core families with both sample groups and additions (11 source palettes):
```json
{"hue":230,"count":6,"balance":true,"output":"base-primes","system":true,"material":"tinted"}
```
Exact project foundation (17 source palettes):
```json
{"preset":"project"}
```
Preserve a brand source:
```json
{"source":{"colorSpace":"oklch","components":[0.62,0.18,265],"alpha":1},"output":"base-primes"}
```

Translate `hue balance off` into `hueBalance:false`, `one step brighter` into `primeBrightnessSteps:1`, `prime brightness +2` into `primeBrightnessSteps:2`, `original prime center` into `primeBrightnessSteps:0`, `tone only` into `primeSpacing:"tone"`, and `legacy Prime distance` into `primeSpacing:"distance"`.

Translate `max chroma` into `chroma:"max"`, `base + primes` into `output:"base-primes"`, `primes only` into `output:"primes"`, and `8 colors` into `count:8`. Bare `material` means tinted; `neutral material` means zero-chroma neutral. Bare `system` means all four feedback palettes. Do not silently infer extras from a count, or parse `812` as a supported count. Ask if a phrase admits materially different interpretations.

## Balance and maximum

Custom numeric chroma first fits the seed at the requested tone. Multi-core balanced requests use a common feasible seed chroma. Their Base envelopes are further capped to the smallest available chroma across the core hues at each shared tone. Unbalanced numeric requests use the project HCT source-envelope recipe, followed by hue balance when enabled.

Max Base curves use the numerical gamut boundary at **each** requested tone, without the project envelope. For balanced max sets, the common feasible boundary wins; therefore not every hue individually reaches its own maximum. Explain that tradeoff if both words are requested. The Base percentage scales this boundary. Max mode does not alter optional system or Material recipes, although explicitly selected global Base/Prime factors still apply to them.

Hue balance applies after envelope construction, so equal chroma and fixed-hue maximum claims describe the uncorrected envelope only. Use `hueBalance:false` for those strict output constraints.

Primes always use the project's independent seven-sample scheduler. They are not numbered Base stops. Evenly spaced HCT hue angles are a deterministic starting layout, not proof of perceptually equal hue spacing. No perceptual scoring, semantic bindings or contrast assessment is performed.

The executable computes both groups internally to preserve the engine path, then omits the unrequested group from each delivered palette. Thus metadata may still describe Base diagnostics in a Primes-only document. Prime-specific measurements live in `primeSpacing`.
