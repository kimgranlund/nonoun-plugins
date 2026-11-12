# Colour system: request contract

`scripts/system.mjs` turns one JSON request into a complete colour system.

**Per mode** (default: `light`, `dark`, `light-contrast`, `dark-contrast`, `dim`), each generated for its own scheme, never inverted from another:
- a 12-step ramp per family (twelve hues even in CAM16 hue quadrature, or the Radix 25, plus a tinted neutral), each step at its APCA Lc against that mode's page;
- transparent steps a1–a12 that reproduce each solid over the page;
- semantic roles, anchors and endpoints;
- solids that take a white label first (Radix-style), else a dark one, kept exactly wherever they already reach the APCA floor; a key run 9→12 spaced evenly in APCA Lc; a control border held above the APCA non-text floor (Contrast model);
- a data series and a sequential ramp (opt-in: a diverging ramp);
- reports, never fixes: an APCA contrast matrix, the series under simulated colour-vision deficiency, and the nearest tonal stop for every role step.

**Mode-independent:** a 050–950 tonal scale per family from the bundled HCT source-palette recipe, seeded with each family's light solid (opt-in: its seven Primes). Use the 12-step ramps and roles for UI; use the tonal scale for brand, illustration and design tools, where dark mode picks *different stops* rather than different values (`tonalMap` says which).

Outputs, in a new directory:

| File | Default | Content |
|---|---|---|
| `system.css` | on | Custom properties per mode. sRGB values, then `@media (color-gamut: p3)` re-declaring only the colours that differ in Display P3 |
| `system.base.css`, `system.<mode>.css` | `split: true` | The same stylesheet in pieces (Split CSS); `system.css` is still written |
| `system.json` | on | `brightHues` (the window used, or false); per mode: settings, roles as resolved, `apca` (the thresholds used), ramps (OKLCH, hex, tone, APCA), `solidLabels`, `solidLabelContrast`, `keyRun`, alpha, series, `contrast`, `seriesCvd`, `tonalMap`, the anchor report and every variable; plus `labelColors`, the tonal layer and `diagnostics` (with `tonalAgreement`) |
| `tokens.dtcg.json` | on | DTCG 2025.10: one group per mode, plus `palette` (tonal) |
| `preview.html` | on | Every mode with its contrast table and series CVD rows, the tonal scale |
| `showcase.html` | `showcase: true` | A static 1280 × 960 specimen sheet: 24 specimens in 8 groups, `system.css` inlined, every failure in `system.json` flagged ([showcase.md](showcase.md)) |
| `tailwind.css` | `tailwind: true` | Tailwind 4 `@theme inline` aliases for every role, step and tonal stop |
| `figma-variables.json` | `figma: true` | A `Color` collection with one column per mode and a single-mode `Palette` collection; roles are aliases (Figma) |

```sh
node /absolute/path/to/ui-colors/scripts/system.mjs --request request.json --out NEW_OUTPUT_DIRECTORY
```

The summary line names the modes, the weakest solid per mode (its APCA Lc against its label, the family and the floor), the number of contrast pairs under their APCA threshold per mode, and the series' smallest ΔE under colour-vision deficiency per mode, with a `WARNING` when any is under 10.

Exit codes: 0 written; 1 generation failed (message on stderr); 2 bad arguments, unknown key, invalid value, unreadable anchor colour, invalid mode or existing output directory.

## Request keys

Every key is optional; `{}` is the default system. Unknown keys reject.

| Key | Default | Value |
|---|---|---|
| `settings` | `{}` | Generator settings for every mode (next section) |
| `brightHues` | `[70, 125]` | The bright-hue window, OKLCH degrees of the step-9 hue (inclusive; `from > to` wraps through 0°), or `false` for white first everywhere (Contrast model › Bright hues). Anything else exits 2 |
| `apca` | below | APCA thresholds (\|Lc\|, 0–108): `{ solid, text, hint, ui, series, contrast: { … } }`; any key left out keeps its default; contrast modes add 15 to each unless `apca.contrast` names its own (Contrast model). A non-number, a value outside 0–108, an unknown key or a non-object exits 2 |
| `neutrals` | none | Split the neutral into ground (page), surface (cards, controls, borders) and ink (text): `{ ground?, surface?, ink?, cross? }` (Neutrals). Without it the system has one neutral, byte for byte as before |
| `roles` | `{}` | `{ role: family }`; an exact name, a Radix name (`red`) or a hue (`h210`); anything else resolves to the nearest hue. With `familyNames: "index"`, also `hue-N` |
| `anchors` | `[]` | Brand colours pinned into ramps (Anchors) |
| `endpoints` | engine | `{ white, black }`: `"pure"` for #fff/#000, or a neutral step 1–12 |
| `modes` | `{}` | Per-mode overrides: `{ "<mode id>": { settings, roles, anchors, endpoints } }` (Modes) |
| `extraModes` | contrast + dim | `false` for light and dark only, or your own list of `{ id, scheme, contrast?, settings?, roles?, anchors?, endpoints? }` |
| `preset` | none | `"minimal"`: `extraModes: false`, `alpha: false`, `tonal: false`. Any of those keys written in the request still wins |
| `familyNames` | `hue` | `hue`: families named after their hue (`indigo`, `cyan`…). `index`: `hue-1…hue-12` (`hue-1…hue-25` with Radix hues) in hue order from the first hue, plus the neutral (`gray`), so modes may change `hue` or `hueSet` (Per-mode hue) |
| `selectors` | `class` | `class`: `.light`, `.dark`, `.dim`, `.light.contrast-more`, `.dark.contrast-more`. `attribute`: `[data-color-mode=light\|dark\|dim]`, plus `[data-contrast=more]` |
| `lightDark` | false | Light and dark as one block of `light-dark()` values that follow `color-scheme`; extra modes stay override blocks (Light-dark) |
| `split` | false | Also write `system.base.css` and one `system.<mode>.css` per mode (Split CSS) |
| `scope` | none | A selector; every variable is declared on it (and its forced variants) instead of `:root` |
| `p3Fallback` | true | With `target: display-p3`: sRGB first, P3 upgrade under `@media (color-gamut: p3)`. `false` emits P3 values only |
| `alpha` | true | `--colors-<family>-a1…a12` per mode |
| `series` | true | `--colors-data-1…6`, `--colors-data-seq-1…7` per mode |
| `diverging` | false | `--colors-data-div-1…11`: the primary's opposite hue → neutral → primary |
| `tonal` | true | `--palette-<family>-050…950`; `false` to omit, or `{ toneMin: 10, toneMax: 98, step: 50 (or 25), base, prime, falloff, hueBalance: false }` (`hueBalance: true` restores the source recipe's own hue balance, the output before this version) |
| `tonalRoles` | false | Per mode, `--palette-role-<role>` (the stop nearest the role's solid) and `--palette-role-<role>-1…12`, each a `var()` of the nearest tonal stop. Needs `tonal` |
| `primes` | false | `--palette-<family>-brightest…dimmest` (the seven Primes) |
| `tailwind`, `figma` | false | Write the adapters |
| `dtcg` | true | Write `tokens.dtcg.json` |
| `showcase` | false | Write `showcase.html` (Showcase). With `scope`, the scope must be classes and/or attributes (`.brand`, `[data-theme=brand]`), or the request exits 2 |

Booleans must be `true` or `false` (exit 2 otherwise).

## Modes

A mode is `{ id, scheme: "light" | "dark" }` and is generated in full for its scheme. Every mode shares one contract: the same families, step numbers, role names, alpha steps and series. The generator rejects a mode whose families differ (exit 2), so a token never resolves in one mode and not another.

- **Overrides per mode.** `modes.<id>.settings` and `modes.<id>.roles` merge over the top-level values; `anchors` and `endpoints` replace them. Example: a deeper dark page and a different primary in dark only — `{ "modes": { "dark": { "settings": { "darkTone": 0, "chroma": 90 }, "roles": { "primary": "blue" } } } }`. An anchor's own `dark` colour also works without a mode override.
- **Per-mode hue.** With the default `familyNames: "hue"`, family names follow the hues, so a mode (in `modes` or `extraModes`) that changes `hue`, `hueSet` or `quadStart` rejects (exit 2): set them at the top level. With `familyNames: "index"` a mode may change them: families are `hue-1…hue-N` in every mode, `hue-1` is the family at that mode's first hue, and roles resolve per mode (a role named by colour, `blue` or `h250`, goes to that mode's nearest hue; a role named `hue-3` is the third hue in every mode, whatever it is). The modes still need the same number of hues and the same neutrals (`quad` vs `radix`, `grays` rejects). Read `system.json › modes.<id>.roles` for what each role became.
- **Contrast modes** (`contrast: true`) raise the scheme's APCA targets by up to 18%: the most the page can still reach, which is less on dark (`system.json › modes.<id>.targetLift`). Their APCA thresholds are 15 Lc higher (solids and text 60, hints 45, non-text 30, series 45), or `apca.contrast`. Auto-applied under `@media (prefers-color-scheme: <its scheme>) and (prefers-contrast: more)`, and forced with the selectors above. `system.json › modes.<id>.contrastMode` is `true` for them.
- **Dim** is a dark mode with page tone 14, forced only (`.dim`, `[data-color-mode=dim]`).
- **Custom modes:** add `{ "id": "sepia", "scheme": "light", "settings": { "toneMax": 92, "tint": 100 } }` to `extraModes`. Custom modes are forced only, unless `contrast: true`. The id `base` is reserved with `split`.

Every mode block sets `color-scheme`, so form controls and scrollbars follow.

### Light-dark

With `lightDark: true`, light and dark become one `:root` block whose differing values are `light-dark(<light>, <dark>)` and whose `color-scheme` is `light dark`; the browser picks by the page's used colour scheme, and `.light` / `.dark` (or the attribute selectors) only set `color-scheme: light` / `dark`. The P3 upgrade re-declares every variable that changes in either scheme, still as `light-dark()` pairs.

Extra modes can't be one more argument of `light-dark()`, so they stay **override blocks**: each one declares every variable with plain values and sets its own `color-scheme` (`.dim` → `dark`, `.light.contrast-more` → `light`). A contrast mode's automatic block applies only under its own scheme's preference (`(prefers-color-scheme: light) and (prefers-contrast: more)` for a light one), so it never repaints a page that prefers the other scheme. `scripts/check.mjs` checks every block's `color-scheme` and the P3 pairs.

### Split CSS

With `split: true`, beside `system.css`:
- `system.base.css`: literal values every mode shares (declared once on the root), the `light-dark()` block and forced light/dark blocks when `lightDark` is on, and the tonal scale, each with its P3 upgrade;
- `system.<mode>.css` for every mode (without `lightDark`, `system.light.css` and `system.dark.css` too), each with its own P3 upgrade.

Load `system.base.css` first, then the modes you ship (`system.light.css` alone is a light-only theme). A variable that resolves through `var()` is never shared: it must be re-declared in each mode block to re-resolve there. For smaller CSS without splitting, use `preset: "minimal"` (about 40% of the default size).

## Settings

Ramp shape: by default this skill sets `base: 76` and `keyIntensity: 200`, so steps 1–8 (surfaces, fills, borders) stay muted and steps 9–12 (solids and text) are saturated. Pass `"base": 100, "keyIntensity": 100` for the engine's flat ramp, where every step carries similar chroma. Step 9 is placed at the same Lc on the page for every hue; with the defaults every generated light-mode step 9 already carries white text (Contrast model), so yellow, amber and lime solids are dark gold and olive rather than Radix's lemon (see the note under Solids).

Values out of range throw (exit 1).

| Key | Default | Range | Effect |
|---|---|---|---|
| `generator` | `hct` | `hct`, `oklch` | Ramp generator. `oklch` reads only `hue`, `falloff`, `toneMax`, `darkTone`, targets, `mat`, `tint`, `neutralFrom`, `target`, `oklchChroma` and the key settings |
| `oklchChroma` | 0.3 | 0–0.37 | OKLCH: requested peak chroma, capped by the weakest hue |
| `hueSet` | `quad` | `quad`, `radix` | 12 hues even in CAM16 hue quadrature, or the Radix 25 |
| `quadStart` | `hue` | `radix`, `hue` | Fit the 12 hues to Radix hues, or start from `hue` |
| `hue` | 225 | 0–359 | First hue (HCT degrees) |
| `chroma` | 120 | 4–120 | Requested HCT chroma |
| `base` | 76 (skill; engine 100) | 0–100 | Share of chroma the whole ramp keeps |
| `keyIntensity` | 200 (skill; engine 100) | 0–300 | Chroma of steps 9–12 on accents; contrast holds |
| `keyDepth` | 0 | −30–30 | Moves step 9 in Lc; positive is a darker solid in both schemes |
| `keyRamp` | 0 | 0–4 | Eases `keyIntensity` in over that many steps before 9 |
| `falloff` | 1 | 0.2–5 | Shape of chroma away from the peak |
| `keyC` | `radix` | `shared`, `radix` | Chroma distribution between hues |
| `hb` | 1 | 0, 1 | Hue balance (yellow and hue-shift correction) |
| `rc` | 0 | 0, 1 | Chroma origin: HCT zero or true grey |
| `darkTone` | 5 | 0–20 | Dark page tone; 0 is black |
| `toneMax` | 97.5 | 80–100 | Light page tone; 100 is white |
| `targetsLight`, `targetsDark` | below | 11 numbers, 0–108 | APCA Lc for steps 2–12 on each page |
| `mat` | `tinted` | `none`, `tinted` | Tint the neutral |
| `tint` | 75 | 0–100 | Neutral tint strength |
| `neutralFrom` | 0 | 0–11 | Which accent tints the neutral |
| `grays` | `[]` | `Gray`, `Mauve`, `Slate`, `Sage`, `Olive`, `Sand` | Extra grey families |
| `radixGrays` | all six | same | Greys included with `hueSet: radix` |
| `harmony` | `off` | `off`, `analogous`, `complementary`, `split`, `triadic` | Hue relationship |
| `primary`, `secondary` | 0, −1 | 0–24, −2–24 | Harmony's primary index and secondary accent |
| `cvd` | `none` | `none`, `protan`, `deutan`, `tritan` | Simulate colour-vision deficiency in the generated colours themselves (a preview of the whole system; the report below is separate) |
| `target` | `display-p3` | `srgb`, `display-p3` | Output gamut; `srgb` keeps every colour on every screen |
| `ptAuto`, `pt`, `ladder` | 0, 62, `even` | | Legacy tone placement; leave out of new themes |

Default Lc targets, steps 2–12: light `5.5 11.6 18.4 25.8 33.8 42.4 51.7 61.6 72.1 83.2 95`; dark `3 7.1 12.2 18.4 25.7 34.1 43.5 54 65.6 78.3 92` (`scripts/system/contrast.js › DEFAULT_TARGETS`; `system.json › modes.<id>.settings` has the targets each mode used).

Under HCT, family names follow the hues, so they change with `hue` (at 250 the indigo family is blue). Write CSS against roles, which survive a hue change; read names from `system.json › families`, or use `familyNames: "index"`.

## Steps and roles

Ramps: `--colors-<family>-1…12` (the neutral is `gray`; with `neutrals`, also `ground`, `surface` and `ink`, and `gray` aliases `ink`); transparent `--colors-<family>-a1…a12`; tonal `--palette-<family>-050…950` and, with `primes`, `--palette-<family>-brightest…dimmest`; with `tonalRoles`, `--palette-role-<role>` and `--palette-role-<role>-1…12`. Steps 1–2 backgrounds (1 is the page), 3–5 interactive fills, 6–8 borders, 9–10 solids, 11–12 text.

Roles (defaults before resolving): primary indigo, secondary amber, neutral, critical red, warning yellow, success green, info cyan, data1–6. `primary`, `secondary`, `neutral`, `critical`, `warning`, `success`, `info` each get `-subtle`, `-subtle-hover` (3, 4), `-border` (7), `-solid`, `-solid-hover` (9, 10 or the anchored step), `-on-solid` (text on that solid: its family's label in this mode), `-fg` (11) and `-1…-12`. Page roles: `bg`, `bg-subtle`, `bg-muted`, `bg-muted-hover`, `bg-muted-active`, `bg-control(-hover/-active)`, `bg-selected`/`fg-selected` (strength from `--ui-emphasis` 0–2), `bg-inverse`/`fg-inverse`, `bg-backdrop`, `border`, `border-strong`, `control-border`, `fg`, `fg-muted`, `fg-subtle`, `fg-on-solid` (the primary's label, kept for compatibility), `fg-strong`, `white`, `black`, `focus-ring`, `data-1…6`, `shadow`. Translucent roles use `color-mix(in oklch, …)`. `bg-backdrop` (behind dialogs and sheets) is pure black at 80% (`rgb(0 0 0 / 0.8)`) in every mode, independent of `endpoints.black`.

## Neutrals

One neutral family colours the page, its cards, controls, borders and text alike. `neutrals` splits it into three families, generated separately, so a page and the material on it can differ (warm paper under cool cards, a toned page under white cards) while text keeps its own neutral:

- **ground**: the page — `bg`, `bg-subtle`, and the scrims cast over it;
- **surface**: the material on the page — cards, panels, wells, control fills, borders;
- **ink**: text — `fg`, `fg-muted`, `fg-subtle`, inverse surfaces, the dark label.

Each of the three is one of:
- `{ "from": "Gray" | "Mauve" | "Slate" | "Sage" | "Olive" | "Sand" }`: a Radix grey as the engine generates it (`settings.grays`), placed against the mode's page like every family;
- a generated tinted neutral `{ "tint"?: 0–100, "neutralFrom"?: 0–11, "hue"?: 0–360 }`: the engine's own neutral with `mat: tinted`, that tint strength and that tint source (`neutralFrom` is the accent index; `hue` picks the accent nearest that HCT hue; give one of the two); keys left out take the run's `settings`;
- left out: the run's own neutral (the default `settings` neutral; a `neutral` anchor still shapes it).

The engine makes one tinted neutral per run, so each distinct spec is one more engine run at the mode's own settings (contrast-mode targets and page tones included), cached; a Radix grey is that run with the grey added to `grays`. Only the family is taken from it.

`"cross": true` swaps which source fills the ground and the surface in dark schemes: the dark page is the surface source's dark ramp, the dark cards the ground source's (the families keep their roles; `system.json › modes.<id>.neutralSources` names each family's source per mode). Light schemes are never crossed.

**Elevation.** The surface family is generated against a page lifted by `SURFACE_LIFT` (CIE L* tone, `system.mjs`): +2.5 in light schemes (97.5 → 100: white cards on a toned page), +4 in dark ones (5 → 9: cards lift toward the light). A page with less headroom (a light page above 98.5, a dark page above 18) moves the surface the other way by the same amount. So a card always separates from the page by lightness, even when the two sources are both near-grey: the engine's Radix greys share almost the same step 1, and two tints at L 0.98 differ by less than a just-noticeable difference.

`system.json`: `neutrals` (the request, `cross`, `rampKeys` — the ink ramp stays under `ramps.gray` —, the lift, the separation threshold and the role table below), and per mode `neutralSources` and `separation`.

### Variables and roles

Ramps `--colors-ground-1…12`, `--colors-surface-1…12` and `--colors-ink-1…12` in every mode (with `alpha`, `-a1…a12` too, solved over ground 1). `--colors-gray-*` and `--colors-gray-a*` stay, as aliases: `--colors-gray-5: var(--colors-ink-5)`, so CSS written against the one-neutral system keeps working and reads the ink. The `neutral` role (`--colors-neutral-*`, `neutral-solid`…) follows gray, i.e. the ink.

| Role | Family and step | One-neutral system |
|---|---|---|
| `bg`, `bg-subtle` | ground 1, 2 | gray 1, 2 |
| `bg-backdrop` | pure black `#000` @ 80% in every mode | `#000` @ 80% |
| `shadow` | ground 12 @ 14% (dark: ground 1 @ 60%) | gray 12 / gray 1 |
| `surface`, `surface-subtle`, `surface-muted` (new) | surface 1, 2, 3 | – |
| `bg-muted`, `-hover`, `-active` | surface 3, 4, 5 | gray 3, 4, 5 |
| `bg-control`, `-hover`, `-active` | surface 12 @ 12 / 19 / 25% (dark 20 / 29 / 39%) | gray 12 |
| `bg-overlay` (new) | surface 1 (dark: surface 2) | – |
| `border`, `border-strong`, `control-border` | surface 6, 7, 8 | gray 6, 7, 8 |
| `bg-selected` | surface 3 → surface 4 → primary 3 by `--ui-emphasis` (dark: surface 4 → primary solid) | gray 3 → gray 1 → primary 3 |
| `fg`, `fg-muted` | ink 12, 11 | gray 12, 11 |
| `fg-subtle` | ink 10 as generated | gray 10 as generated |
| `fg-strong` | black / white, or ink 12 with an `ink` (light) or `ground` (dark) anchor | the same on gray |
| `fg-selected` | ink 12 | gray 12 |
| `bg-inverse` / `fg-inverse` | ink 12 / ground 1 (inverse text is the page colour) | gray 12 / gray 1 |
| `white`, `black` (endpoints) | ink 3 of the light / dark ramp, or `endpoints` | gray 3 |
| labels of solids | light label ground 1 of light mode (the page); dark label ink 12 of light mode | gray 1 / gray 12 |
| `focus-ring`, `data-*`, scale roles | unchanged | |

Ink 1–2 exist (every family has twelve steps) but no role puts them under content. The light label stays the page (ground 1) rather than the card (surface 1): it is the colour the one-neutral system used, it keeps every solid's white-first decision on the page it sits on, and a white card would raise every light-label Lc only a little. The selection fill moves to surface 4 because the one-neutral choice (gray 1, a raised row on a bg-subtle panel) would vanish on a surface-1 card. The data series sit on `bg-subtle` (ground 2), the alpha steps over ground 1 and the diverging midpoint on ink 3.

### Anchors

`ground` and `ink` keep their meaning (a brand's paper and ink) and pin the split families: `ground` pins ground 1 in light and ink 12 in dark (its `dark` colour, else the same colour); `ink` pins ink 12 in light and ground 1 in dark. `surface` (neutrals only, exit 2 without) pins surface 1 in light and, with `dark`, surface 1 in dark exactly; without `dark` the dark card takes the anchor's hue and chroma at its own lightness (`anchorReport.dark.derived`). Same colour formats as other anchors; `step`, `darkStep` and `reach` are not allowed on `surface`. Each pin eases its neighbours the way the engine pins the neutral's ends; the split families are not re-tinted between ground and ink (the one-neutral `deriveNeutral`), since each has its own source. A `neutral` anchor with `neutrals.ink` set, `roles.neutral` with `neutrals`, and `from` with `generator: oklch` exit 2.

### Checks

- The contrast matrix checks `fg`, `fg-muted` (text) and `fg-subtle` (hint) on `bg`, `bg-subtle`, `surface`, `surface-subtle` and `surface-muted` (ground 1–2, surface 1–3), and `control-border` (`ui`) on `bg`, `bg-subtle`, `surface` and `surface-subtle`; the control border solve holds surface 8 at `apca.ui` on all four (49 pairs per mode instead of 40).
- **Separation**: surface 1 against ground 1 in every mode, `modes.<id>.separation: { dE, lc, threshold, pass, groundTone, surfaceTone }`. The gate is OKLab ΔE × 100 ≥ 2 (`SEPARATION_MIN`): one just-noticeable difference, the JND CSS Color 4 uses for gamut mapping (ΔEOK 0.02). ΔE rather than APCA, because a warm page and a cool card of one lightness are visibly different at almost no Lc; `lc` is reported beside it. Like every report it is never fixed: the CLI warns (`WARNING separation under 2`) and the showcase flags it. With the lift the defaults land at ΔE 2.17–2.18 in light and light-contrast, 3.86 in dark and dark-contrast, 3.45 in dim (both examples below); a surface anchor close to the page can miss it.

### Examples

```json
{ "neutrals": { "ground": { "from": "Sand" }, "surface": { "from": "Slate" }, "cross": true } }
{ "neutrals": { "ground": { "tint": 20, "neutralFrom": 6 }, "surface": { "tint": 60 } } }
{ "neutrals": { "ground": { "from": "Sand" } }, "anchors": [{ "role": "ground", "value": "#f6f2ea" }, { "role": "surface", "value": "#ffffff", "dark": "#22211f" }] }
{ "neutrals": {} }
```

The first is a warm Sand page under cool Slate cards in light, crossed in dark (Slate page, Sand cards); the second a light amber-tinted page under cyan-tinted cards with the default ink; the third pins a paper and a white card; the last keeps one neutral source for all three but still lifts the surface off the page.

## Contrast model (APCA)

Every contrast decision and flag uses APCA only: |Lc| from the vendored `scripts/system/contrast.js › apcaLc(textTone, bgTone)` (tones are CIE L*), with the foreground — label, text, border, focus ring, data mark — as the text argument and its background second. WCAG 2 ratios appear only as an informational `ratio` column in the contrast matrix; they drive no decision and no flag. That `apcaLc` works on tones (CIE luminance, no APCA-W3 screen gamma) and leaves out APCA-W3's 0.027 low-contrast offset: measured on this system's pairs it reads within about 1 Lc of APCA-W3 0.0.98G for dark text on light grounds and 2–5 Lc higher for light text on dark grounds, so its thresholds are a little more lenient there than the published APCA-W3.

Thresholds: APCA's most lenient level for each use. Constants in `scripts/system.mjs › APCA_DEFAULTS`, overridable with the `apca` request key:

| Key | Use | Default | Contrast modes | Why this level |
|---|---|---|---|---|
| `solid` | label text on a solid (button, chip text); the `label` intent in the matrix | 45 | 60 | APCA's floor for large or bold text |
| `text` | text pairs in the matrix (`fg`, `fg-muted`, role `-fg`); steps 11–12 against the page | 45 | 60 | the same large/bold-text floor |
| `hint` | placeholder, hint and subtle text (`fg-subtle`) | 30 | 45 | APCA's absolute minimum for any text |
| `ui` | non-text: control border, focus ring, dividers; the least a solid keeps against its page | 15 | 30 | APCA's floor for a perceivable non-text edge |
| `series` | data marks against the chart surface | 30 | 45 | the minimum for large solid non-text marks |

```json
{ "apca": { "solid": 60, "hint": 45, "contrast": { "solid": 75 } } }
```

Contrast modes take `normal + 15` (capped at 108) for every key `apca.contrast` leaves out. Every solve aims 0.5 Lc over its floor (`SOLVE_MARGIN`: chroma clamping and 8-bit rounding of what ships). `system.json › modes.<id>.apca` holds the thresholds each mode used.

- **Steps** sit at their APCA Lc target against the page, so a step reads the same in every hue.
- **Bright hues**: an accent whose step-9 OKLCH hue lies in the bright-hue window (`system.mjs › BRIGHT_HUES`, 70°–125° by default; request key `brightHues`) always takes the dark label with its step 9 at the hue's gamut cusp (below), in every mode, whether or not white would pass — as Radix does for yellow, amber and lime. `solidLabels.<family>.brightHue: true` marks it. In the window by default: amber (78°), yellow (95°), lime (117°); orange (59°) and grass (146°) are outside. With `hueSet: "radix"`: gold (72°), amber (81°), yellow (97°), lime (122°). Every other family follows the rules below.
- **Solids** (step 9, or an anchored role's step) each take one of two labels: the **light label** (light neutral step 1, the light page) or the **dark label** (light neutral step 12, the ink — the same colour in every mode, so in dark modes it is dark text on a bright solid). White first, as in Radix, per family and mode:
  1. the light label whenever the generated solid reaches `apca.solid` against it; it is **kept exactly**;
  2. otherwise the dark label if the generated solid reaches the floor against it; kept exactly;
  3. otherwise its lightness moves just far enough to reach one of them — darker for the light label, lighter for the dark one — with chroma clamped to the output gamut at each tested lightness (the Lc tested is the Lc shipped): toward white when both moves keep about the same chroma (within 5% of it, `CHROMA_EDGE`), else the move that keeps more chroma.
  - **Visibility guard**: a solid that keeps white but whose key run (below) would then put step 9 under `apca.ui` against its page no longer reads as a solid; that family takes the dark label instead and records `whiteRejected: { lc9OnPage, floor }`. With the defaults this happens in dark-contrast only (white there would need step 9 at page Lc ~16, under 30).
  - **Cusp**: a solid that takes the dark label (an accent, not anchored at 9) goes up to its hue's gamut cusp — the lightness of greatest in-gamut chroma at the generated hue in the mode's target gamut, capped at L 0.95 — with the full chroma there, when that is brighter than where the floor left it and still clears the dark-label floor. It keeps at least `apca.ui` against the page and leaves the key run 15 Lc of room before step 12 (`KEY_RUN_MIN`; in a dark scheme a bright cusp can sit past step 12), lowered toward the floor-solved lightness only as far as those need. The hue never rotates. `solidLabels.<family>.cusp: true` and `cuspAt: { cuspL, L, floorL }` record it. Light-label solids never move to the cusp.
  - Anchored solids follow the same rule and stay exact when they pass.
  - With the defaults: **light, dark, dim, light-contrast**: amber, yellow and lime take the dark label at their cusp (bright hues), every other family the light label; **dark-contrast**: every family takes the dark label (indigo, plum, crimson, tomato, orange, grass and gray by the visibility guard), and amber, yellow, lime, grass, jade and teal sit at their cusp. Light yellow 9 is `#ffd600` (L 0.89), amber `#ffba00`, lime `#d0e900`. In dark and dim, yellow and lime stop short of their cusp (yellow `#edc700`, L 0.835) because the cusp lies within 15 Lc of step 12 (the key-run room); dark-contrast yellow reaches it (`#ffde00`).
- **Key run 9–12**: after the label, steps 10 and 11 are rebuilt between step 9 and step 12, evenly in APCA Lc against the page (`Lc10 = Lc9 + (Lc12 − Lc9)/3`, `Lc11 = Lc9 + 2(Lc12 − Lc9)/3`), each step's lightness solved for its Lc; hue along the shorter arc, weighted by chroma (a near-grey step 12 barely pulls the hue), chroma eased in (t²) from 9 to 12 and clamped to the gamut. Lightness is monotonic 9→12 in the ramp's direction.
  - **Hover** (step 10, `-solid-hover`) clears `apca.solid` against step 9's label. When the run heads toward the label (dark text in a light scheme, light text in a dark one) and it would not, step 9 moves toward the page just far enough that it does (`hoverRoom: true`, `roomMoved` ΔL; a cusp solid keeps the gamut's full chroma as it moves); with the defaults every white-label dark and dim family does this (step 9 ends near page Lc 45 and 40), and light amber. When no step 9 gives an even run a passing hover (an anchored step 9, or a dark label in light-contrast, whose step 12 is black), step 10 moves toward step 9 to the floor instead and 11 re-spaces between 10 and 12 (a `hover-floor` deviation; with the defaults: light-contrast amber, yellow and lime).
  - Steps 11 and 12 are text: each clears `apca.text` against the page and against step 3, where a role's `-fg` sits on its `-subtle` fill (`text-floor` deviation otherwise; with the defaults: light-contrast amber, yellow and lime step 11). Step 12 stays as generated unless it is needed for order (`order`).
  - **Anchors** on 10–12 are fixed points: the run is spaced evenly on each side of them.
  - `system.json › modes.<id>.keyRun.<family>`: `{ lc: [9, 10, 11, 12] (page Lc), L, C, H, pinned, deviations: [{ step, reason }] }`. Every deviation is flagged on the showcase.
  - `system.json › modes.<id>.solidLabels.<family>`: `{ label: "light" | "dark", lc (label on the solid), floor, hoverLc, moved (ΔL of the label solve, 0 when kept), generated (step 9 before the solve), hoverRoom?, roomMoved?, cusp?, cuspAt?, whiteRejected?, anchored? }`; `solidLabelContrast` is each family's solid against its own label (APCA Lc); `labelColors` holds the two label colours.
- **Control border** (neutral step 8) is held at `apca.ui` against steps 1 and 2 in each scheme (it already clears it with the defaults).
- **Data series**: six colours chosen for the worst case. Among the accent hues (the primary is always `data-1`) and steps 8, 9, 11 and 12, each candidate is first nudged in lightness to `apca.series` against the chart surface (neutral step 2), then the set whose smallest pairwise OKLab ΔE across normal vision and protan, deutan and tritan simulation is largest wins (`seriesSearch.worstCaseDE`); series are ordered by hue from the primary. Lightness spread is what keeps colours apart under dichromacy, so the set mixes light and dark steps. With the defaults the worst case is about 10–12 in light, dark, dim and dark-contrast and ~9.1 in light-contrast (the CLI warns under 10). `lcOnSurface` is reported. The sequential ramp is seven steps (3, 4, 5, 7, 8, 9, 11) of the primary hue; the diverging ramp is eleven steps from the primary's opposite hue through the neutral to the primary.

`--colors-<role>-on-solid` is the label of that role's solid in each mode (a literal colour, one of `labelColors`), so text on every solid meets `apca.solid` in every mode; `--colors-fg-on-solid` is `var(--colors-primary-on-solid)`. Use the role's own label: `fg-on-solid` on a warning solid can be the wrong one. The contrast matrix confirms each pair per mode.

## Reports (never fixed)

The generator reports these per mode and never moves a colour to pass them.

**Contrast matrix** (`system.json › modes.<id>.contrast`): `{ method, thresholds, intents, pairs: [{ fg, bg, intent, lc, threshold, pass, ratio }], summary: { pairs, fail, failures } }` for 40 pairs (49 with `neutrals`, Neutrals › Checks):
- `fg`, `fg-muted`, `fg-subtle` on `bg`, `bg-subtle`, `bg-muted` (intent `text`; `fg-subtle` is `hint`);
- each scale role's `-fg` on its `-subtle` and on `bg` (`text`);
- each scale role's `-on-solid` on its `-solid` and `-solid-hover` (`label`, threshold `apca.solid`);
- `border-strong`, `control-border` and `focus-ring` on `bg` (`ui`).

`lc` is |Lc| from the vendored `apcaLc`, the foreground as text, on the sRGB values (channels clipped) as CIE L* tones; a translucent colour is composited over its background (and the background over the page). `threshold` is the mode's APCA threshold for the intent and `pass` is `lc ≥ threshold`. `ratio` (WCAG 2) is informational only. The CLI line and the preview's per-mode table show the misses; with the defaults no pair misses in any mode (under WCAG 2 AA the previous version missed three: `fg-subtle` on `bg-muted` and `border-strong` on `bg` in light, `border-strong` in light-contrast).

**Series under colour-vision deficiency** (`modes.<id>.seriesCvd`): `{ method, threshold: 10, normal, protan, deutan, tritan, ok, weakest }`, each `{ minDE, pair, hex }`: the smallest OKLab ΔE × 100 between any two of the six series, the pair (1-based) and the simulated colours. Simulation: Machado, Oliveira & Fernandes (2009) at severity 1.0 (full dichromacy), applied to linear sRGB and clipped to 0–1, on each series colour's sRGB fallback. Threshold 10 (about five just-noticeable differences; under it two series are easy to confuse at a glance); the CLI warns when any minimum is under it. The default series pass normally (about 12) and fall to about 4 under protanopia: use direct labels, patterns or fewer series where colour alone must carry meaning.

**Tonal map** (`modes.<id>.tonalMap`, with the tonal layer): per scale role `{ family, solid, steps: [{ step, stop, dE }] }`, the 050–950 stop nearest each of the role's 12 steps by OKLab ΔE × 100, and the stop nearest its solid. `tonalRoles: true` writes the same as CSS aliases.

**Tonal agreement** (`diagnostics.tonalAgreement`): how far the tonal layer (one HCT bundle) sits from the 12-step ramps (another) — per mode and family, the stop nearest each step's tone, compared in hue and chroma only (`chromaHueDE`: mean, p95, max) and in OKLCH hue degrees (`hueDeg`). Defaults: mean about 3, max about 10–15 (the 12-step ramps' chroma varies by step under the skill's ramp shape, a single tonal envelope doesn't). See `references/system-notice.md`.

APCA placement and these reports are not an accessibility audit of your UI: they cover the role pairs above, not your components, and they use APCA's most lenient levels (raise them with `apca` for body text).

## Anchors

```json
{ "role": "primary", "value": "#0a4dff", "dark": "#6f9bff", "step": 9, "reach": "key" }
```

| Field | Meaning |
|---|---|
| `role` | Any role, or `ground` (light page and dark text) and `ink` (light text and dark page) for a brand's paper and ink; with `neutrals`, also `surface` (light and dark card, Neutrals › Anchors) |
| `value` | The colour (formats below) |
| `step` | Optional; default the step whose Lc is nearest the colour's. Not for `ground`/`ink` |
| `dark` | Optional exact dark-scheme colour, same formats; without it dark takes hue and chroma, and its solid stays at step 9 |
| `darkStep` | Optional step for `dark` |
| `reach` | `key` (default): chroma changes on steps 9–12 only. `ramp` (default on neutrals): the whole ramp |
| `name` | Optional label |

Colour formats for `value` and `dark`:
- `#rrggbb`;
- a CSS string: `oklch(L C H)`, `oklab(L a b)`, `color(srgb r g b)`, `color(display-p3 r g b)` (also `color(srgb-linear …)`, `color(xyz-d65 …)`, `rgb()`); an alpha other than 1 rejects;
- a tagged colour: `{ "colorSpace": "oklch" | "oklab" | "srgb" | "display-p3", "components": [3 numbers], "alpha": 1 }`.

Anything unreadable exits 2. Wide-gamut values are kept: an anchor is clipped only to the mode's output gamut (`settings.target`), by reducing OKLCH chroma at its lightness and hue, before the ramps and solids are solved. So `color(display-p3 0 0.8 0.3)` with `target: display-p3` stays exact (the sRGB block of `system.css` shows its sRGB fallback, the P3 block the exact value); with `target: srgb` it becomes the nearest sRGB colour of that lightness and hue. Each `anchorReport` entry carries `source` (the request's value) and `gamut: { target, inTarget, inSrgb, requested?, clipDE? }` (`clipDE`: OKLab ΔE × 100 lost to clipping), for `dark` too.

Every step except the page takes the anchor's hue; the anchored step becomes exact, neighbours settle, and an anchor on steps 8–12 moves the role's solid there. Read `system.json › anchorReport`: `inOrder: false` means the colour breaks the contrast order; `inRange: false` means it lies beyond the ramp (use `endpoints`).

## Showcase

With `showcase: true`, `showcase.html` is one self-contained page (it inlines `system.css`) laid out per [showcase.md](showcase.md): Ramps, Neutral & surfaces, Roles, Transparency, Modes, Brand, Data, Scales & checks, three specimens each. The sheet is the forced light mode; every panel that shows another mode carries that mode's forced selector (`.dark`, `.light.contrast-more`, `[data-color-mode=dim]`…, with the scope's classes or attributes), so it takes that mode's variables, `light-dark()` values included. The Modes group shows light, dark and the first extra mode in run order. With `neutrals`, Neutral & surfaces shows the ground, surface and ink strips and a card (surface) on the page per shown mode with its separation, the mode cards sit on `surface`, and the ramp tiles keep the accents and gray (= ink). A feature the run turned off (alpha, series, tonal, anchors, diverging, extra modes, a P3 target) keeps its specimen as a labelled empty state. With more than 16 families (Radix hues) the ramp tiles show the families the roles use.

The step-use specimen carries the construction annotation: each primary step's `apcaOnPage` next to its target, the `primary-on-solid` / `primary-solid` APCA Lc against the solid floor, the key run 9–12 (page Lc), which families take the dark label in light and dark, the bright-hue window and its families, and every key-run deviation (grouped per mode); in both ramp tiles step 9 carries an "A" in its family's label for that mode. Roles show each solid's and hover's Lc against its label and each status role's `-fg` Lc on `bg`; the contrast excerpt shows Lc, threshold and pass. Machine-readable marks, which `scripts/check.mjs` reads: `data-group`, `data-specimen`, `data-mode-panel`, `data-annot` (`lc` with `data-step`, `data-lc`, `data-target`; `solid-lc` with `data-step`, `data-value`, `data-floor`; `keyrun` with `data-lc`; `labels`), `data-label` on each step-9 tile and `data-flag`: `lc-miss` (`data-mode`, `data-count`), `series-weak` (`data-mode`, `data-kind`, `data-value`), `keyrun` (`data-mode`, `data-family`, `data-step`, `data-reason`), `anchor-order`, `anchor-range`, `anchor-clip` (`data-role`, `data-modes`).

## Figma

`figma-variables.json`: `{ $description, collections: [{ name: "Color", modes: [mode ids], variables }, { name: "Palette", modes: ["default"], variables }] }`. Each variable is `{ id, name, type: "COLOR", valuesByMode, resolvedValuesByMode }`:
- `id` is stable across runs: `Color:<name>` or `Palette:<name>` (names: `indigo/9`, `primary-solid`, `gray/a3`, `cyan/050`, `tonal-role/primary/9`);
- `valuesByMode[mode]` is RGBA `{ r, g, b, a }` (sRGB 0–1), or `{ "type": "VARIABLE_ALIAS", "id": "<variable id>" }` when the role points at a ramp step (directly or through other roles) — `primary-solid` → `Color:indigo/9`, a `tonalRoles` alias → `Palette:indigo/450`. Translucent roles (`color-mix(… X%, transparent)`) stay resolved, with alpha X/100. Variables that don't resolve to one colour (`bg-selected`, mixed from `--ui-emphasis`) are left out;
- `resolvedValuesByMode[mode]` is always the plain RGBA, for importers without alias support.

For the Variables REST API, create the variables with these ids as temporary ids and send `valuesByMode` as each mode's value.

## Checks

```sh
node /absolute/path/to/ui-colors/scripts/check.mjs [--keep]
```

Runs `system.mjs` on `{}`, on a light-dark request (`brightHues: false`, `lightDark`, `split`, `figma`, `tonalRoles`, `showcase`, dim and both contrast modes), on `{ "showcase": true }`, on a scoped attribute-selector sRGB showcase request with an out-of-order and a clipped anchor, on an APCA-override request with anchors at step 9 (both schemes) and 11, and on three neutrals requests (Sand ground and Slate surface crossed, with the showcase; generated tinted ground, surface and ink with `lightDark`, `split`, `figma` and dim; ground, ink and surface anchors whose card is too close to the page), in a temporary directory, then checks, with its own colour maths (APCA through the vendored `apcaLc`):
- **fixture**: `scripts/system/fixtures/hct-default.json` holds the raw engine ramps (before the solid and border solves) at the targets it was made with, which predate today's defaults (light `7.3 … 85.7`, dark `3.4 … 77.1`). The check measures those targets from the fixture's neutral, regenerates the raw engine ramps at them and compares all 12 steps of all 13 families, light and dark: ΔE OKLab × 100 ≤ 0.1. (The post-solve default output differs from the fixture by design; it is covered by the next two checks.)
- **placement**: in the default output, every family's steps 2–7 within 1.5 Lc of their target and accents' step 12 within 2.5 (steps 8–11 are moved by the border solve and the key run);
- **floors** (APCA), recomputed from the ramps at thresholds the check derives from the request on its own (defaults, `apca` overrides, contrast +15 or `apca.contrast`): every family's solid and its hover against its own label (the light mode's gray 1 or gray 12, as `solidLabels` names it) and the reported Lc, each role's `-on-solid` equal to that label; control border ≥ `ui`; series ≥ `series`; `modes.<id>.apca` equal to the derived thresholds;
- **apca key**: an override run (`solid 60`, `hint 60`, `contrast.solid 75`) is checked at those thresholds, and eight bad values (string, negative, over 108, unknown key, non-object `contrast`, out-of-range `contrast` value, array, unknown `contrast` key) each exit 2;
- **bright hues**: the window read from the request on its own (default 70°–125°, `false` none); a family whose generated step-9 hue is inside takes the dark label and carries `brightHue`, one outside never does; the default run has bright-hue families, the light-dark run (`brightHues: false`) none; six bad `brightHues` values exit 2;
- **white first**: each mode's ramps regenerated before the solid solve (engine at the mode's settings, keys shaped), independently of `system.mjs`: the recorded `generated` step matches; a generated step 9 that reaches the floor against white takes the light label, unless its white run (APCA reads tones only, so the lightest hover tone white allows and the step 9 it implies, `(3·Lc10 − Lc12)/2`, are exact) would put step 9 under `ui` on the page — then dark with `whiteRejected`; a solid that passes its label is unmoved by the label solve; every later change of step 9 has a recorded reason (`hoverRoom`, minimal: the hover lands at the floor ± 0.3; or `cusp`) (runs without anchors);
- **cusp**: each dark-label accent's step 9 at its hue's cusp (the check's own scan), lowered only as far as `ui` on the page or the 15 Lc key-run room needs, at the gamut's maximum chroma there, hue unrotated; no cusp mark on a light-label or anchored solid;
- **key run**: page Lc of steps 9–12 recomputed and equal to `keyRun.lc`; every step between fixed points (9, 12, anchored 10–12 from the anchor report, each recorded deviation) within ±0.5 Lc of even spacing — the solver bisects lightness to ~1e-9 with the same tone maths, so the only slack is JSON's 6-decimal rounding (measured 0.000 Lc); 0.5 is a third of a just-visible 1.5 Lc step; lightness monotonic; steps 11–12 ≥ `text` on the page and on step 3; every deviation real (not evenly spaced) and at its own floor;
- **files** exist; **CSS** (system.css, the preview's stylesheet, the split files together) has balanced braces, `;`-terminated declarations and no `var()` without a declaration;
- **light-dark**: root `color-scheme: light dark`, forced light/dark and every extra mode's blocks with their own scheme, a P3 `light-dark()` pair for every variable that leaves sRGB in either scheme;
- **split** files declare everything `system.css` does, and each mode file re-declares every `var()` role;
- **Figma**: every alias names a variable in the file whose resolved colour equals the alias's own;
- **contrast** pairs recomputed from the ramps (Lc ±0.1, informational ratio ±0.02), each threshold the intent's, `pass` consistent; **series CVD** unsimulated minimum recomputed; **tonal** agreement and map present;
- **showcase**: written only when requested; 24 specimens in the 8 groups, three each; the annotation's Lc, targets, the solid's Lc and floor, and the key run 9–12 equal `system.json` (and, for the key run, the ramps) in attributes and visible text; exactly the failures `system.json` reports are flagged (APCA misses per mode with their count, series minima under the threshold, key-run deviations, anchors out of order, out of range or clipped); each mode panel carries its forced selector, scope included; every colour is a variable `system.css` declares, a value from `system.json` or a light step's sRGB fallback, and the sheet's own CSS names no colour. Layout (fit, overlap, blank swatches, legibility) needs a browser at 1280 × 960 and is not checked here.
- **neutrals**: the default run's `system.css` and `system.json` hash to `scripts/system/fixtures/default-digest.json` (byte-identical default; after a deliberate change to the default output, refresh it with `check.mjs --update-digest`) and carry no split variable or field; every split role points at its family and step (the table above, restated in the check), `gray-N` is `var(--colors-ink-N)` and ink N is the gray ramp's colour; each family's steps 1–7 equal the neutral the engine makes for its spec at the mode's settings (the surface at the lifted page; ground and surface specs swapped in dark when `cross`), skipping anchored ends; the cross run names Slate for the dark page and Sand for the dark cards; separation recomputed (ΔE ± 0.05, Lc ± 0.1, threshold 2, `pass`), every mode separated in the unanchored runs and the anchored run has a miss to flag; anchors pin ground 1 / ink 12 / surface 1 and their dark ends; floors with the split labels, control border on ground 1–2 and surface 1–2, series on ground 2; key run, contrast (with the split pairs), CSS, light-dark, split files and Figma on the split runs; the preview shows the three families; the showcase's Neutral & surfaces group has the three strips and a surface card on the page per shown mode with its ΔE, and separation misses are flagged; 15 bad `neutrals` values or combinations exit 2.

Then 74 negative controls mutate a copy (move a fixture step or a placed step; lighten a solid, bring a contrast-mode solid under Lc 60, push a hover under the floor, claim the light label for a dark-label solid, give a role the other label, raise the request's `apca.solid`, drop the control border, slip a valid `apca` or `brightHues` value into the bad list; put a bright-hue family on the light label, mark a family outside the window bright, read `brightHues: false` as the default; give a white-passing solid the dark label, reject white without cause, put a white-rejected solid back on white, move a passing solid, report a failing solid as kept, widen a hover room; pull a cusp solid back, rotate its hue, drop its cusp mark; push step 10 or 11 off even spacing, collapse step 12, drop a recorded deviation, misreport `keyRun.lc`; put a series under the surface floor; delete a file, drop a brace or a declaration, flip a `color-scheme`, drop a P3 pair or a split declaration, misroute a Figma alias, misreport an Lc, pass a pair under its threshold, give a pair the wrong threshold, misreport a ΔE, drop a tonalMap role; in the showcase: delete it, drop or add a specimen, misreport an Lc, a target, the solid's Lc or floor or the key run, drop an APCA-miss, key-run or anchor flag, report a weak series the sheet doesn't flag, flag an anchor `system.json` reports in order, strip a panel's forced class or attribute, inject a colour or a sheet colour literal; neutrals: change the default output by one byte, add a split variable to the default run, read `border` from the ground, leave `fg` on gray, break the gray alias, swap the dark ground and surface back, drop the surface lift, read `cross` as off, misreport a separation, set the card to the page colour, unpin a ground anchor or a surface anchor's dark colour, drop a separation flag, drop the ink strip, draw a dark card on the wrong role, slip a valid `neutrals` value into the bad list); each must make its check fail. Exit 0 when every check passes and every control bites; 1 otherwise.

## Example requests

```json
{}
{ "settings": { "hue": 250, "target": "srgb" } }
{ "settings": { "hueSet": "radix", "cvd": "deutan" } }
{ "settings": { "generator": "oklch", "oklchChroma": 0.2 } }
{ "roles": { "primary": "h265" }, "anchors": [{ "role": "primary", "value": "#0a4dff" }], "endpoints": { "white": "pure", "black": "pure" } }
{ "anchors": [{ "role": "ground", "value": "#f6f2ea" }, { "role": "ink", "value": "#1c1a17" }], "scope": ".brand" }
{ "anchors": [{ "role": "success", "value": "color(display-p3 0 0.8 0.3)" }, { "role": "primary", "value": { "colorSpace": "oklch", "components": [0.55, 0.25, 265], "alpha": 1 } }] }
{ "modes": { "dark": { "settings": { "darkTone": 0, "chroma": 90 }, "roles": { "primary": "blue" } } } }
{ "familyNames": "index", "modes": { "dark": { "settings": { "hue": 40 } } }, "roles": { "primary": "hue-3" } }
{ "extraModes": false, "lightDark": true, "settings": { "target": "srgb" } }
{ "lightDark": true, "extraModes": [{ "id": "dim", "scheme": "dark", "settings": { "darkTone": 14 } }] }
{ "selectors": "attribute", "extraModes": [{ "id": "sepia", "scheme": "light", "settings": { "toneMax": 92 } }] }
{ "preset": "minimal", "split": true }
{ "showcase": true, "selectors": "attribute", "scope": ".brand", "anchors": [{ "role": "primary", "value": "#0a4dff" }] }
{ "primes": true, "diverging": true, "tailwind": true, "figma": true, "tonalRoles": true, "tonal": { "base": 90 } }
{ "apca": { "solid": 60, "text": 60, "contrast": { "solid": 75, "text": 75 } } }
{ "brightHues": false }
{ "brightHues": [60, 130] }
```

## Runtime notes

A default run (five modes plus the tonal layer) takes 1–3 s and needs no network or packages; `generator: oklch` never starts the engine. The engine is a vendored bundle (`scripts/system/runtime.json`) that starts with `new Function`, so generate at build time rather than in a page with a strict Content-Security-Policy. Its third-party notices travel inside it; see `references/system-notice.md`. `scripts/system/fixtures/` holds the HCT and OKLCH ramps for checking a port (`check.mjs` reads the HCT one).
