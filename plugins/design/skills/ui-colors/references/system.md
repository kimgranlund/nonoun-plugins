# Color system: request contract

`scripts/system.mjs` turns one JSON request into a complete color system.

**Per mode** (default: `light`, `dark`, `light-contrast`, `dark-contrast`, `dim`), each generated for its own scheme, never inverted from another:
- a 12-step ramp per family (twelve hues even in CAM16 hue quadrature, or the Radix 25, plus a tinted neutral), each step at its APCA Lc against that mode's page;
- transparent steps a1–a12 that reproduce each solid over the page;
- semantic roles, anchors and endpoints;
- solids that take a white label first (Radix-style), else a dark one, kept exactly wherever they already reach the APCA floor; a key run 9→12 spaced evenly in APCA Lc; a control border held above the APCA non-text floor (Contrast model);
- a data series and a sequential ramp (opt-in: a diverging ramp);
- reports, never fixes: an APCA contrast matrix, the series under simulated color-vision deficiency, and the nearest tonal stop for every role step.

**Mode-independent:** a 050–950 tonal scale per family from the bundled HCT source-palette recipe, seeded with each family's light solid (opt-in: its seven Primes). Use the 12-step ramps and roles for UI; use the tonal scale for brand, illustration and design tools, where dark mode picks *different stops* rather than different values (`tonalMap` says which).

Outputs, in a new directory:

| File | Default | Content |
|---|---|---|
| `system.css` | on | Custom properties per mode. sRGB values, then `@media (color-gamut: p3)` re-declaring only the colors that differ in Display P3 |
| `system.base.css`, `system.<mode>.css` | `split: true` | The same stylesheet in pieces (Split CSS); `system.css` is still written |
| `system.json` | on | `brightHues` (the window used, or false); per mode: settings, roles as resolved, `apca` (the thresholds used), ramps (OKLCH, hex, tone, APCA), `solidLabels`, `solidLabelContrast`, `keyRun`, alpha, series, `contrast`, `seriesCvd`, `tonalMap`, the anchor report and every variable; plus `labelColors`, the tonal scale and `diagnostics` (with `tonalAgreement`) |
| `tokens.dtcg.json` | on | DTCG 2025.10: one group per mode, plus `palette` (tonal) |
| `preview.html` | on | Every mode with its contrast table and series CVD rows, the tonal scale |
| `showcase.html` | `showcase: true` | A static 1280 × 960 specimen sheet: 24 specimens in 8 groups, `system.css` inlined, every failure in `system.json` flagged ([showcase.md](showcase.md)) |
| `tailwind.css` | `tailwind: true` | Tailwind 4 `@theme inline` aliases for every role, step and tonal stop |
| `figma-variables.json` | `figma: true` | A `Color` collection with one column per mode and a single-mode `Palette` collection; roles are aliases (Figma) |

```sh
node /absolute/path/to/ui-colors/scripts/system.mjs --request request.json --out NEW_OUTPUT_DIRECTORY
```

The summary line names the modes, the weakest solid per mode (its APCA Lc against its label, the family and the floor), the number of contrast pairs under their APCA threshold per mode, and the series' smallest ΔE under color-vision deficiency per mode, with a `WARNING` when any is under 10. Then one `WARNING anchor …` line per anchor problem read from `anchorReport` (the modes it holds in, in brackets): a step out of contrast order (`inOrder: false`), an accent placed off step 9 by `step: "auto"`, an accent whose solid in a mode is not the anchor colour (with ΔE; usually a missing `dark`), a derived dark card (`dark.derived`) and gamut clipping (`clipDE`).

Exit codes: 0 written; 1 generation failed (message on stderr); 2 bad arguments, unknown key, invalid value, unreadable anchor color, invalid mode or existing output directory.

## Request keys

Every key is optional; `{}` is the default system. Unknown keys reject.

| Key | Default | Value |
|---|---|---|
| `settings` | `{}` | Generator settings for every mode (next section) |
| `brightHues` | `[70, 125]` | The bright-hue window, OKLCH degrees of the step-9 hue (inclusive; `from > to` wraps through 0°), or `false` for white first everywhere (Contrast model › Bright hues). Anything else exits 2 |
| `apca` | below | APCA thresholds (\|Lc\|, 0–108): `{ solid, text, hint, ui, series, contrast: { … } }`; any key left out keeps its default; contrast modes add 15 to each unless `apca.contrast` names its own (Contrast model). A non-number, a value outside 0–108, an unknown key or a non-object exits 2 |
| `neutrals` | none | Split the neutral into ground (page), surface (cards, controls, borders) and ink (text): `{ ground?, surface?, ink?, cross? }` (Neutrals). Without it the system has one neutral, byte for byte as before |
| `roles` | `{}` | `{ role: family }`, `role` one of `primary`, `secondary`, `neutral`, `critical`, `warning`, `success`, `info`, `data1`–`data6` (any other name exits 2; it was silently dropped before): an exact family name, a Radix name (`red`), an **HCT** hue `h0`–`h360` (`h85`, `h085`, `h84.5`) or an **OKLCH** hue `oklch:0`–`oklch:360` (matched against each family's step-9 OKLCH hue; brand guides and CSS usually give OKLCH). The name or hue goes to the nearest family. Anything else exits 2. With `familyNames: "index"`, also `hue-N` |
| `anchors` | `[]` | Brand colors pinned into ramps (Anchors). `role` must be a role of the system (or `ground`, `ink`, `surface`); any other name exits 2 |
| `familyAnchors` | `{}` | `{ "<family>": { value, dark?, step?, darkStep?, reach?, name? } }`: pins a family by name, with no role (Anchors › Family anchors). An unknown family, a family a role anchor already pins, or an unknown key exits 2 |
| `endpoints` | engine | `{ white, black }`: `"pure"` for #fff/#000, or a neutral step 1–12. Each endpoint the request names also takes its side of the inverse pair: `bg-inverse` is black in light and white in dark, `fg-inverse` the other |
| `modes` | `{}` | Per-mode overrides: `{ "<mode id>": { settings, roles, anchors, endpoints } }` (Modes) |
| `extraModes` | contrast + dim | `false` for light and dark only, or your own list of `{ id, scheme, contrast?, settings?, roles?, anchors?, endpoints? }` |
| `preset` | none | A request preset (not a palette preset, which is `scripts/preset.mjs`). `"minimal"`: `extraModes: false`, `alpha: false`, `tonal: false`. Any of those keys written in the request still wins |
| `familyNames` | `hue` | `hue`: families named after their hue (`indigo`, `cyan`…). A map `{ "amber": "gold", "orange": "sand" }` renames those accent families (and their variables, tonal stops and roles) and keeps hue names for the rest; roles may then name `gold`. A key that is not an accent family, a name taken by another family, a duplicate, or `neutral`/`gray`/`ground`/`surface`/`ink` exits 2. `index`: `hue-1…hue-12` (`hue-1…hue-25` with Radix hues) in hue order from the first hue, plus the neutral (`gray`), so modes may change `hue` or `hueSet` (Per-mode hue) |
| `selectors` | `class` | `class`: `.light`, `.dark`, `.dim`, `.light.contrast-more`, `.dark.contrast-more`. `attribute`: `[data-color-mode=light\|dark\|dim]`, plus `[data-contrast=more]` |
| `lightDark` | false | Light and dark as one block of `light-dark()` values that follow `color-scheme`; extra modes stay override blocks (Light-dark) |
| `split` | false | Also write `system.base.css` and one `system.<mode>.css` per mode (Split CSS) |
| `scope` | none | A selector; every variable is declared on it (and its forced variants) instead of `:root` |
| `p3Fallback` | true | With `target: display-p3`: sRGB first, P3 upgrade under `@media (color-gamut: p3)`. `false` emits P3 values only |
| `alpha` | true | `--colors-<family>-a1…a12` per mode |
| `series` | true | `--colors-data-1…6`, `--colors-data-seq-1…7` per mode; `false` removes both, the `data-1…6` roles included |
| `autoDark` | true | `false`: no `@media (prefers-color-scheme: dark)` block (nor the dark contrast mode's automatic block), so the OS setting never repaints the page; dark stays a forced class or attribute (`.dark`, or an extra mode such as `{ "id": "on-ink", "scheme": "dark" }` for dark sections). Exits 2 with `lightDark` |
| `brandExact` | false | `true`: every `primary`, `secondary`, `critical`, `warning`, `success` and `info` anchor without `dark` uses its own value as `dark`, so each brand colour is the solid (step 9) in every scheme. Check the `WARNING anchor … out of contrast order` lines it may cause |
| `diverging` | false | `--colors-data-div-1…11`: the primary's opposite hue → neutral → primary |
| `tonal` | true | `--palette-<family>-050…950`; `false` to omit, or `{ toneMin: 10, toneMax: 98, step: 50 (or 25), base, prime, falloff, hueBalance: false }` (`hueBalance: true` restores the source recipe's own hue balance, the output before this version) |
| `tonalRoles` | false | Per mode, `--palette-role-<role>` (the stop nearest the role's solid) and `--palette-role-<role>-1…12`, each a `var()` of the nearest tonal stop. Needs `tonal` |
| `primes` | false | `--palette-<family>-brightest…dimmest` (the seven Primes) |
| `tailwind`, `figma` | false | Write the adapters |
| `dtcg` | true | Write `tokens.dtcg.json` |
| `showcase` | false | Write `showcase.html` (Showcase). With `scope`, the scope must be classes and/or attributes (`.brand`, `[data-theme=brand]`), or the request exits 2 |
| `emphasis` | 1 | Strength of the selection fills, 0–2: 0 quiet (neutral 3), 1 balanced (neutral 1, or surface 4 with `neutrals`), 2 loud (primary 3); dark runs neutral 4 → `bg-inverse` → the primary solid, with `fg-selected` following its fill, so the primary enters only above 1 in both schemes. Resolved at generation: a whole number is an alias to its step, a value between is the generated OKLCH mix |
| `translucent` | none | Requested translucent roles: `{ name: { of, alpha, darkOf?, darkAlpha? } }`, each emitted as `--colors-<name>` in every mode (Requested translucent roles). A bad name, alpha or base exits 2 |

Booleans must be `true` or `false` (exit 2 otherwise).

## Modes

A mode is `{ id, scheme: "light" | "dark" }` and is generated in full for its scheme. Every mode shares one contract: the same families, step numbers, role names, alpha steps and series. The generator rejects a mode whose families differ (exit 2), so a token never resolves in one mode and not another.

- **Overrides per mode.** `modes.<id>.settings` and `modes.<id>.roles` merge over the top-level values; `anchors` and `endpoints` replace them. Example: a deeper dark page and a different primary in dark only — `{ "modes": { "dark": { "settings": { "darkTone": 0, "chroma": 90 }, "roles": { "primary": "blue" } } } }`. An anchor's own `dark` color also works without a mode override.
- **Per-mode hue.** With the default `familyNames: "hue"`, family names follow the hues, so a mode (in `modes` or `extraModes`) that changes `hue`, `hueSet` or `quadStart` rejects (exit 2): set them at the top level. With `familyNames: "index"` a mode may change them: families are `hue-1…hue-N` in every mode, `hue-1` is the family at that mode's first hue, and roles resolve per mode (a role named by color, `blue` or `h250`, goes to that mode's nearest hue; a role named `hue-3` is the third hue in every mode, whatever it is). The modes still need the same number of hues and the same neutrals (`quad` vs `radix`, `grays` rejects). Read `system.json › modes.<id>.roles` for what each role became.
- **Contrast modes** (`contrast: true`) raise the scheme's APCA targets by up to 18%: the most the page can still reach, which is less on dark (`system.json › modes.<id>.targetLift`). Their APCA thresholds are 15 Lc higher (solids and text 60, hints 45, non-text 30, series 45), or `apca.contrast`. Auto-applied under `@media (prefers-color-scheme: <its scheme>) and (prefers-contrast: more)`, and forced with the selectors above. `system.json › modes.<id>.contrastMode` is `true` for them.
- **Dim** is a dark mode with page tone 14, forced only (`.dim`, `[data-color-mode=dim]`).
- **Custom modes:** add `{ "id": "sepia", "scheme": "light", "settings": { "toneMax": 92, "tint": 100 } }` to `extraModes`. Custom modes are forced only, unless `contrast: true`. The id `base` is reserved with `split`.

Every mode block sets `color-scheme`, so form controls and scrollbars follow.

**Dark as a section, not a mode.** Custom properties inherit, so a forced class on any element repaints only that element and its contents. For a brand whose dark colour is for some sections (a hero, a footer) rather than a dark mode, set `"autoDark": false` and add a forced-only mode named after the class, for example `"extraModes": [{ "id": "on-ink", "scheme": "dark" }]`. Then `<section class="on-ink">` gets the dark scheme and the page ignores the OS preference.

### Light-dark

With `lightDark: true`, light and dark become one `:root` block whose differing values are `light-dark(<light>, <dark>)` and whose `color-scheme` is `light dark`; the browser picks by the page's used color scheme, and `.light` / `.dark` (or the attribute selectors) only set `color-scheme: light` / `dark`. The P3 upgrade re-declares every variable that changes in either scheme, still as `light-dark()` pairs.

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
| `keyDepth` | 0 | −30–30 | Moves step 9 in Lc; positive is a darker solid in both schemes. In practice it acts at the label choice: once the darker solid lets the light label pass, the family switches to white first and its solid is solved there, so neighbouring values often give the same output (a dark-mode `keyDepth` of 4 and of 30 can be identical). Compare `solidLabels` after changing it |
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
| `cvd` | `none` | `none`, `protan`, `deutan`, `tritan` | Simulate color-vision deficiency in the generated colors themselves (a preview of the whole system; the report below is separate) |
| `target` | `display-p3` | `srgb`, `display-p3` | Output gamut; `srgb` keeps every color on every screen |
| `ptAuto`, `pt`, `ladder` | 0, 62, `even` | | Legacy tone placement; leave out of new themes |

Default Lc targets, steps 2–12: light `5.5 11.6 18.4 25.8 33.8 42.4 51.7 61.6 72.1 83.2 95`; dark `3 7.1 12.2 18.4 25.7 34.1 43.5 54 65.6 78.3 92` (`scripts/system/contrast.js › DEFAULT_TARGETS`; `system.json › modes.<id>.settings` has the targets each mode used).

Under HCT, family names follow the hues, so they change with `hue` (at 250 the indigo family is blue). Write CSS against roles, which survive a hue change; read names from `system.json › families`, or use `familyNames: "index"`.

## Steps and roles

Ramps: `--colors-<family>-1…12` (the neutral is `gray`; with `neutrals`, also `ground`, `surface` and `ink`, and `gray` aliases `ink`); transparent `--colors-<family>-a1…a12`; tonal `--palette-<family>-050…950` and, with `primes`, `--palette-<family>-brightest…dimmest`; with `tonalRoles`, `--palette-role-<role>` and `--palette-role-<role>-1…12`. Steps 1–2 backgrounds (1 is the page), 3–5 interactive fills, 6–8 borders, 9–10 solids, 11–12 text.

Roles (defaults before resolving): primary indigo, secondary amber, neutral, critical red, warning yellow, success green, info cyan, data1–6. `primary`, `secondary`, `neutral`, `critical`, `warning`, `success`, `info` each get `-subtle`, `-subtle-hover` (3, 4), `-border` (7), `-solid`, `-solid-hover` (9, 10 or the anchored step), `-solid-active` (the solid held down: step 11, or one step back from the solid where its label would fail on 11), `-on-solid` (text on that solid: its family's label in this mode), `-on-solid-muted` (quiet text on that solid: a step of the role's own family), `-fg` (11) and `-1…-12`. Page roles: `bg`, `bg-subtle`, `bg-muted`, `bg-muted-hover`, `bg-muted-active`, `bg-control(-hover/-active)`, `bg-selected`/`fg-selected` (a part chosen alone; strength from `emphasis` 0–2), `bg-selected-multiple` (the tint of a row chosen among several), `bg-inverse`/`fg-inverse`, `bg-disabled`/`fg-disabled` (the muted fill and neutral step 8; no contrast level applies), `bg-backdrop`, `border`, `border-strong`, `control-border`, `fg`, `fg-muted`, `fg-subtle`, `fg-on-solid` (the primary's label, kept for compatibility), `fg-strong`, `white`, `black`, `focus-ring`, `data-1…6`, `shadow`. **Generated, not derived.** Every variable is a color (`oklch(L C H)`, or `oklch(L C H / a)` when translucent) or an alias that names another variable (`var(--…)`); the output never contains `color-mix()`, `calc()` or relative color syntax, so the browser never derives a color (`check.mjs` › generated). Translucent roles (`bg-control*`, `shadow`, `bg-backdrop`) are their source step's color at a fixed alpha, written out per mode. The backdrop, `bg-backdrop` (behind dialogs and sheets), is pure black at 80% (`oklch(0 0 0 / 0.8)`) in every mode, independent of `endpoints.black`. The selection fills are resolved from the request's `emphasis` (0 quiet, 1 balanced, 2 loud; default 1): a whole number lands on a step and is an alias to it, a value between is the OKLCH mix of the two steps, written as a color. A theme that wants another emphasis regenerates; there is no live `--ui-emphasis`.

## Neutrals

One neutral family colors the page, its cards, controls, borders and text alike. `neutrals` splits it into three families, generated separately, so a page and the material on it can differ (warm paper under cool cards, a toned page under white cards) while text keeps its own neutral:

- **ground**: the page — `bg`, `bg-subtle`, and the shadow cast onto it;
- **surface**: the material on the page — cards, panels, wells, control fills, borders;
- **ink**: text — `fg`, `fg-muted`, `fg-subtle`, inverse surfaces, the dark label.

Each of the three is one of:
- `{ "from": "Gray" | "Mauve" | "Slate" | "Sage" | "Olive" | "Sand" }`: a Radix grey as the engine generates it (`settings.grays`), placed against the mode's page like every family;
- a generated tinted neutral `{ "tint"?: 0–100, "neutralFrom"?: 0–11, "hue"?: 0–360 }`: the engine's own neutral with `mat: tinted`, that tint strength and that tint source (`neutralFrom` is the accent index; `hue` picks the accent nearest that HCT hue; give one of the two); keys left out take the run's `settings`;
- left out: the run's own neutral (the default `settings` neutral; a `neutral` anchor still shapes it).

The engine makes one tinted neutral per run, so each distinct spec is one more engine run at the mode's own settings (contrast-mode targets and page tones included), cached; a Radix grey is that run with the grey added to `grays`. Only the family is taken from it.

`"cross": true` swaps which source fills the ground and the surface in dark schemes: the dark page is the surface source's dark ramp, the dark cards the ground source's (the families keep their roles; `system.json › modes.<id>.neutralSources` names each family's source per mode). Light schemes are never crossed.

**Surface lift.** The surface family is generated against a page lifted by `SURFACE_LIFT` (CIE L* tone, `system.mjs`): +2.5 in light schemes (97.5 → 100: white cards on a toned page), +4 in dark ones (5 → 9: cards lift toward the light). A page with less headroom (a light page above 98.5, a dark page above 18) moves the surface the other way by the same amount. So a card always separates from the page by lightness, even when the two sources are both near-grey: the engine's Radix greys share almost the same step 1, and two tints at L 0.98 differ by less than a just-noticeable difference.

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
| `bg-overlay` (new) | surface 1 (dark: surface 3, two steps above the card, so the fill alone clears the raised gate) | – |
| `bg-overlay-muted` (new) | surface 3 (dark: surface 4): a field or well inside an overlay, one step above it | – |
| `border`, `border-strong`, `control-border` | surface 6, 7, 8 | gray 6, 7, 8 |
| `bg-selected` | surface 3 → surface 4 → primary 3 by `emphasis` (dark: surface 4 → `bg-inverse` → primary solid) | gray 3 → gray 1 → primary 3 (dark: gray 4 → `bg-inverse` → primary solid) |
| `bg-selected-multiple` | surface 5, 6 or 7: the lowest that reaches `apca.ui` on surface 1 | gray 5, 6 or 7, on gray 1 |
| `fg`, `fg-muted` | ink 12, 11 | gray 12, 11 |
| `fg-subtle` | ink 10 as generated | gray 10 as generated |
| `fg-strong` | black / white, or ink 12 with an `ink` (light) or `ground` (dark) anchor | the same on gray |
| `fg-selected` | ink 12 | gray 12 |
| `bg-inverse` / `fg-inverse` | ink 12 / ground 1 (inverse text is the page color); with `endpoints`, the far and near endpoint of the scheme | gray 12 / gray 1; the same with `endpoints` |
| `bg-disabled` / `fg-disabled` | surface 3 (`bg-muted`) / ink 8 | gray 3 / gray 8 |
| `white`, `black` (endpoints) | past ink 1 of the light / dark ramp, or `endpoints` | past gray 1 |
| labels of solids | light label ground 1 of light mode (the page); dark label ink 12 of light mode | gray 1 / gray 12 |
| `focus-ring`, `data-*`, scale roles | unchanged | |

Ink 1–2 exist (every family has twelve steps) but no role puts them under content. The light label stays the page (ground 1) rather than the card (surface 1): it is the color the one-neutral system used, it keeps every solid's white-first decision on the page it sits on, and a white card would raise every light-label Lc only a little. The selection fill moves to surface 4 because the one-neutral choice (gray 1, a raised row on a bg-subtle panel) would vanish on a surface-1 card. The data series sit on `bg-subtle` (ground 2), the alpha steps over ground 1 and the diverging midpoint on ink 3.

### Anchors

`ground` and `ink` keep their meaning (a brand's paper and ink) and pin the split families: `ground` pins ground 1 in light and ink 12 in dark (its `dark` color, else the same color); `ink` pins ink 12 in light and ground 1 in dark. `surface` (neutrals only, exit 2 without) pins surface 1 in light and, with `dark`, surface 1 in dark exactly; without `dark` the dark card takes the anchor's hue and chroma at its own lightness (`anchorReport.dark.derived`). Same color formats as other anchors; `step`, `darkStep` and `reach` are not allowed on `surface`. Each pin eases its neighbours the way the engine pins the neutral's ends; the split families are not re-tinted between ground and ink (the one-neutral `deriveNeutral`), since each has its own source. A `neutral` anchor with `neutrals.ink` set, `roles.neutral` with `neutrals`, and `from` with `generator: oklch` exit 2.

### Checks

- The contrast matrix checks `fg`, `fg-muted` (text) and `fg-subtle` (hint) on `bg`, `bg-subtle`, `surface`, `surface-subtle` and `surface-muted` (ground 1–2, surface 1–3), and `control-border` (`ui`) on `bg`, `bg-subtle`, `surface` and `surface-subtle`; the control border solve holds surface 8 at `apca.ui` on all four (59 pairs per mode instead of 50).
- **Separation**: surface 1 against ground 1 in every mode, `modes.<id>.separation: { dE, lc, threshold, pass, groundTone, surfaceTone }`. `separation.layers` adds every adjacent pair of the stack, `[{ upper, lower, level, dE, threshold, pass }]`: `surface` on `bg`, `bg-overlay` on `bg` and on `surface`, `bg-muted` on `surface`, `bg-overlay-muted` on `bg-overlay`. A resting pair is held to the same floor; a raised pair (the overlay) to `raisedThreshold`, ΔE 6 (`RAISED_SEPARATION_MIN`, a judgement: 3.9 read as one layer and about 6 or more read clearly), in a dark scheme only, because in a light scheme its shadow separates it (`threshold` and `pass` are then `null`). The CLI line lists the layers under their gate; `pass` and the showcase flag stay the card on the page. The gate is OKLab ΔE × 100 ≥ 2 (`SEPARATION_MIN`): one just-noticeable difference, the JND CSS Color 4 uses for gamut mapping (ΔEOK 0.02). ΔE rather than APCA, because a warm page and a cool card of one lightness are visibly different at almost no Lc; `lc` is reported beside it. Like every report it is never fixed: the CLI warns (`WARNING separation under 2`) and the showcase flags it. With the lift the defaults land at ΔE 2.17–2.18 in light and light-contrast, 3.86 in dark and dark-contrast, 3.45 in dim (both examples below); a surface anchor close to the page can miss it.

### Examples

```json
{ "neutrals": { "ground": { "from": "Sand" }, "surface": { "from": "Slate" }, "cross": true } }
{ "neutrals": { "ground": { "tint": 20, "neutralFrom": 6 }, "surface": { "tint": 60 } } }
{ "neutrals": { "ground": { "from": "Sand" } }, "anchors": [{ "role": "ground", "value": "#f6f2ea" }, { "role": "surface", "value": "#ffffff", "dark": "#22211f" }] }
{ "neutrals": {} }
```

The first is a warm Sand page under cool Slate cards in light, crossed in dark (Slate page, Sand cards); the second a light amber-tinted page under cyan-tinted cards with the default ink; the third pins a paper and a white card; the last keeps one neutral source for all three but still lifts the surface off the page.

## Requested translucent roles

A consumer that needs a color at a fixed alpha asks for it in the request, so the system generates the value and nothing derives it in the browser. Each entry of `translucent` is a requested translucent role: it becomes `--colors-<name>` in every mode, a literal `oklch(L C H / a)` like the built-in translucent roles.

```json
{ "translucent": { "veil-strong": { "of": "neutral-12", "alpha": 0.12, "darkOf": "#000000", "darkAlpha": 0.36 } } }
```

- `of`: a variable of the system without its `--colors-` prefix (a role such as `bg`, or a family step such as `gray-12`), or an opaque color (`#rrggbb`, `oklch(…)`, `color(display-p3 …)`). A list takes the first entry the mode has: `["surface", "bg"]` reads `surface` with `neutrals` and `bg` without.
- `alpha`: 0–1. `darkOf` and `darkAlpha` apply in modes of the dark scheme, and default to `of` and `alpha`.
- The request owns the names and the alphas; the system defines none. Without the key nothing is emitted, and the default system stays byte-identical.
- Exits 2: a name that is not lowercase letters, digits and hyphens, or that is already a variable of the system; an alpha outside 0–1; a base that is unreadable, is itself translucent, or that no listed variable provides; an unknown field.

`system.json › modes.<id>.translucent` lists each role's resolved base and alpha. `tokens.dtcg.json` carries a `translucent` group per mode, and the Tailwind and Figma adapters take these variables as they take every other. They enter no contrast pair. ui-materials uses the key for its lit paint: its `scripts/request.mjs` prints the request fragment.

**A solve is only as current as its base.** Every run re-solves the system's own alpha steps and requested translucent roles, but a value solved outside it (an alpha copied into a stylesheet, a glass or frosted tint measured over a face) is tied to the steps it was measured on. Changing one of them (a ground, surface or ink anchor, `neutrals`, a mode's settings, or which step a layer reads) invalidates it: regenerate, then re-measure the text over every translucent layer against its worst backdrop, white and black. In a measured case a dark face moved one step lighter, and muted text through its frosted tint fell from over 45 to Lc 41.8 over a white backdrop until the tint's alpha was raised.

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
- **Bright hues**: an accent whose step-9 OKLCH hue lies in the bright-hue window (`system.mjs › BRIGHT_HUES`, 70°–125° by default; request key `brightHues`) always takes the dark label with its step 9 at the hue's gamut cusp (below), in every mode, unless the family is anchored or its step 9 has OKLCH chroma under 0.08 (`BRIGHT_MIN_C`: a khaki or sand of a yellow hue is a tinted neutral, not a bright hue), whether or not white would pass — as Radix does for yellow, amber and lime. The window is judged once per run, on the light mode's generated light step 9, and that verdict holds in every mode and scheme, so a family whose dark or per-mode step 9 drifts a few degrees (a darker dark solid moves lime past 125°) keeps its treatment. `solidLabels.<family>.brightHue: true` marks it. In the window by default: amber (78°), yellow (95°), lime (117°); orange (59°) and grass (146°) are outside. With `hueSet: "radix"`: gold (72°), amber (81°), yellow (97°), lime (122°). Every other family follows the rules below.
- **Solids** (step 9, or an anchored role's step) each take one of two labels: the **light label** (light neutral step 1, the light page) or the **dark label** (light neutral step 12, the ink — the same color in every mode, so in dark modes it is dark text on a bright solid). White first, as in Radix, per family and mode:
  1. the light label whenever the generated solid reaches `apca.solid` against it; it is **kept exactly**;
  2. otherwise the dark label if the generated solid reaches the floor against it; kept exactly;
  3. otherwise its lightness moves just far enough to reach one of them — darker for the light label, lighter for the dark one — with chroma clamped to the output gamut at each tested lightness (the Lc tested is the Lc shipped): toward white when both moves keep about the same chroma (within 5% of it, `CHROMA_EDGE`), else the move that keeps more chroma.
  - **Visibility guard**: a solid that keeps white but whose key run (below) would then put step 9 under `apca.ui` against its page no longer reads as a solid; that family takes the dark label instead and records `whiteRejected: { lc9OnPage, floor }`. With the defaults this happens in dark-contrast only (white there would need step 9 at page Lc ~16, under 30).
  - **Cusp**: a solid that takes the dark label (an accent, not anchored at 9) goes up to its hue's gamut cusp — the lightness of greatest in-gamut chroma at the generated hue in the mode's target gamut, capped at L 0.95 — with the full chroma there, when that is brighter than where the floor left it and still clears the dark-label floor. It keeps at least `apca.ui` against the page and leaves the key run 15 Lc of room before step 12 (`KEY_RUN_MIN`; in a dark scheme a bright cusp can sit past step 12), lowered toward the floor-solved lightness only as far as those need. The hue never rotates. `solidLabels.<family>.cusp: true` and `cuspAt: { cuspL, L, floorL }` record it. Light-label solids never move to the cusp.
  - Anchored solids follow the same rule and stay exact when they pass.
  - With the defaults: **light, dark, dim, light-contrast**: amber, yellow and lime take the dark label at their cusp (bright hues), every other family the light label; **dark-contrast**: every family takes the dark label (indigo, plum, crimson, tomato, orange, grass and gray by the visibility guard), and amber, yellow, lime, grass, jade and teal sit at their cusp. Light yellow 9 is `#ffd600` (L 0.89), amber `#ffba00`, lime `#d0e900`. In dark and dim, yellow and lime stop short of their cusp (yellow `#edc700`, L 0.835) because the cusp lies within 15 Lc of step 12 (the key-run room); dark-contrast yellow reaches it (`#ffde00`).
- **Key run 9–12**: after the label, steps 10 and 11 are rebuilt between step 9 and step 12, evenly in APCA Lc against the page (`Lc10 = Lc9 + (Lc12 − Lc9)/3`, `Lc11 = Lc9 + 2(Lc12 − Lc9)/3`), each step's lightness solved for its Lc; hue along the shorter arc, weighted by chroma (a near-grey step 12 barely pulls the hue), chroma eased in (t²) from 9 to 12 and clamped to the gamut. Lightness is monotonic 9→12 in the ramp's direction.
  - **Hover** (step 10, `-solid-hover`) clears `apca.solid` against step 9's label. When the run heads toward the label (dark text in a light scheme, light text in a dark one) and it would not, step 9 moves toward the page just far enough that it does (`hoverRoom: true`, `roomMoved` ΔL; a cusp solid keeps the gamut's full chroma as it moves); with the defaults every white-label dark and dim family does this (step 9 ends near page Lc 45 and 40), and light amber. When no step 9 gives an even run a passing hover (an anchored step 9, or a dark label in light-contrast, whose step 12 is black), step 10 moves toward step 9 to the floor instead and 11 re-spaces between 10 and 12 (a `hover-floor` deviation; with the defaults: light-contrast amber, yellow and lime).
  - **Active** (`-solid-active`, a solid held down) is one step further from rest than the hover, with the label kept. It is step 11 where the solid's label clears `apca.solid` on it. Where the run heads toward the label, step 11 is too near the label (with the defaults: every light-label family in dark and dim, and amber, yellow and lime in light and light-contrast), so active steps back the other way instead, to page Lc `Lc9 − (Lc10 − Lc9)`, no nearer the page than `apca.ui` (`clamped: true` where that limit binds; with the defaults, the bright hues in light and light-contrast). `solidLabels.<family>.active` records `side`, `lc`, `lcOnPage` and `clamped` (and `step` on 11, or the back step's `oklch`). Where the limit binds on a solid already at `apca.ui` (with the defaults: light lime, light-contrast yellow and lime), the back step is the solid's own colour; `hover.active` shows how far it sits from the hover. Where the solid itself sits nearer the page than `apca.ui` (its hover already a `hover-floor-unreachable` deviation), the limit puts the back step nearer the label than the solid, and the matrix reports the miss. An anchored solid applies the same rule from its own step; an anchored step 11 has no step past its hover, so its active there is the colour one hover gap beyond it (at most black or white), written as a colour.
  - Steps 11 and 12 are text: each clears `apca.text` against the page and against step 3, where a role's `-fg` sits on its `-subtle` fill (`text-floor` deviation otherwise; with the defaults: light-contrast amber, yellow and lime step 11). Step 12 stays as generated unless it is needed for order (`order`).
  - **Anchors** on 10–12 are fixed points: the run is spaced evenly on each side of them.
  - `system.json › modes.<id>.keyRun.<family>`: `{ lc: [9, 10, 11, 12] (page Lc), L, C, H, pinned, deviations: [{ step, reason }] }`. Every deviation is flagged on the showcase.
  - `system.json › modes.<id>.solidLabels.<family>`: `{ label: "light" | "dark", lc (label on the solid), floor, hoverLc, moved (ΔL of the label solve, 0 when kept), generated (step 9 before the solve), hoverRoom?, roomMoved?, cusp?, cuspAt?, whiteRejected?, active, anchored? }`; `solidLabelContrast` is each family's solid against its own label (APCA Lc); `labelColors` holds the two label colors.
- **Control border** (neutral step 8) is held at `apca.ui` against steps 1 and 2 in each scheme (it already clears it with the defaults).
- **Data series**: six colors chosen for the worst case. Among the accent hues (the primary is always `data-1`) and steps 8, 9, 11 and 12, each candidate is first nudged in lightness to `apca.series` against the chart surface (neutral step 2), then the set whose smallest pairwise OKLab ΔE across normal vision and protan, deutan and tritan simulation is largest wins (`seriesSearch.worstCaseDE`); series are ordered by hue from the primary. Lightness spread is what keeps colors apart under dichromacy, so the set mixes light and dark steps. With the defaults the worst case is about 10–12 in light, dark, dim and dark-contrast and ~9.1 in light-contrast (the CLI warns under 10). `lcOnSurface` is reported. The sequential ramp is seven steps (3, 4, 5, 7, 8, 9, 11) of the primary hue; the diverging ramp is eleven steps from the primary's opposite hue through the neutral to the primary.

`--colors-<role>-on-solid` is the label of that role's solid in each mode (a literal color, one of `labelColors`), so text on every solid meets `apca.solid` in every mode; `--colors-fg-on-solid` is `var(--colors-primary-on-solid)`. Use the role's own label: `fg-on-solid` on a warning solid can be the wrong one. The contrast matrix confirms each pair per mode.

## Reports (never fixed)

The generator reports these per mode and never moves a color to pass them.

**Contrast matrix** (`system.json › modes.<id>.contrast`): `{ method, thresholds, intents, pairs: [{ fg, bg, intent, lc, threshold, pass, ratio }], summary: { pairs, fail, failures } }` for 57 pairs (66 with `neutrals`, Neutrals › Checks):
- `fg`, `fg-muted`, `fg-subtle` on `bg`, `bg-subtle`, `bg-muted` (intent `text`; `fg-subtle` is `hint`);
- each scale role's `-fg` on its `-subtle` and on `bg` (`text`);
- each scale role's `-on-solid` on its `-solid`, `-solid-hover` and `-solid-active` (`label`, threshold `apca.solid`);
- each scale role's `-on-solid-muted` on its `-solid` (`hint`);
- `bg-selected-multiple` on `bg` (on `surface` with `neutrals`; `ui`) and `fg` on `bg-selected-multiple` (`text`);
- `fg-inverse` on `bg-inverse` (`text`);
- `border-strong`, `control-border` and `focus-ring` on `bg` (`ui`).

`contrast.unleveled` lists the pairs no level applies to, `[{ fg, bg, lc, level: "none", why }]`: `fg-disabled` on `bg-disabled` and on `bg`. They have no threshold, no `pass` and no flag.

`lc` is |Lc| from the vendored `apcaLc`, the foreground as text, on the sRGB values (channels clipped) as CIE L* tones; a translucent color is composited over its background (and the background over the page). `threshold` is the mode's APCA threshold for the intent and `pass` is `lc ≥ threshold`. A system with a Display P3 upgrade shows a P3 screen other colours than the fallback, so each pair also carries `lcP3` and `passP3`, measured on the P3 values (each clipped to P3, luminance by P3's weights), and `summary` carries `failP3` and `failuresP3`; the CLI line lists both counts. A saturated colour outside sRGB is clipped lighter or darker for the fallback, so the two can differ by a few Lc (up to 3.4 measured). Every solve (a solid against its label, the hover room, the visibility guard, the quiet on-solid ink) therefore holds the worse of the two renderings, and the reported `solidLabels` and `solidLabelContrast` figures are that worse value. With the defaults no pair misses on either. `ratio` (WCAG 2) is informational only. The CLI line and the preview's per-mode table show the misses; with the defaults no pair misses in any mode on the sRGB fallback (under WCAG 2 AA the previous version missed three: `fg-subtle` on `bg-muted` and `border-strong` on `bg` in light, `border-strong` in light-contrast).

**Series under color-vision deficiency** (`modes.<id>.seriesCvd`): `{ method, threshold: 10, normal, protan, deutan, tritan, ok, weakest }`, each `{ minDE, pair, hex }`: the smallest OKLab ΔE × 100 between any two of the six series, the pair (1-based) and the simulated colors. Simulation: Machado, Oliveira & Fernandes (2009) at severity 1.0 (full dichromacy), applied to linear sRGB and clipped to 0–1, on each series color's sRGB fallback. Threshold 10 (about five just-noticeable differences; under it two series are easy to confuse at a glance); the CLI warns when any minimum is under it. The default series pass normally (about 12) and fall to about 4 under protanopia: use direct labels, patterns or fewer series where color alone must carry meaning.

**Hover steps** (`modes.<id>.hover`): `{ method, threshold: 4, pairs: [{ rest, hover, over?, dE, pass }], steps, summary: { pairs, fail, failures } }`. Each pair is OKLab ΔE × 100 between a rest fill and its hover: `bg-muted` and `bg-control` (each composited over its ground, `over`: `bg`, and `surface` with `neutrals`), and each scale role's `-subtle` and `-solid`. `steps` gives the neutral's ΔE from each step to the next, steps 1 to 6 (with `neutrals`, the surface's too). Under 4, a hover can be told apart from its rest fill side by side but is not seen under the pointer; a component should then take the next step that clears it (one step from the lightest neutral measures about 3 with the defaults; two measure about 6). With the defaults, light `bg-muted` and several light `-subtle` hovers measure 3.8 to 4.0, and the dark and dim warning hover about 3. Four is a judgement read from three measured pairs (2.3 too faint, 4.1 and 4.6 kept), not a reader test. A hover is also not seen when it matches the fill around the part (a key hovered onto the step of its housing); that pair depends on the component, so measure it there. The CLI line counts the pairs under 4 per mode. `active: [{ hover, active, dE }]` gives each scale role's `-solid-hover` against its `-solid-active`, reported and held to no threshold.

**Tonal map** (`modes.<id>.tonalMap`, with the tonal scale): per scale role `{ family, solid, steps: [{ step, stop, dE }] }`, the 050–950 stop nearest each of the role's 12 steps by OKLab ΔE × 100, and the stop nearest its solid. `tonalRoles: true` writes the same as CSS aliases.

**Tonal agreement** (`diagnostics.tonalAgreement`): how far the tonal scale (one HCT bundle) sits from the 12-step ramps (another) — per mode and family, the stop nearest each step's tone, compared in hue and chroma only (`chromaHueDE`: mean, p95, max) and in OKLCH hue degrees (`hueDeg`). Defaults: mean about 3, max about 10–15 (the 12-step ramps' chroma varies by step under the skill's ramp shape, a single tonal envelope doesn't). See `references/system-notice.md`.

APCA placement and these reports are not an accessibility audit of your UI: they cover the role pairs above, not your components, and they use APCA's most lenient levels (raise them with `apca` for body text).

## Applying the roles

How a component system should use the roles for states the system has no role for. Each rule was measured in a shipped component system; measure your own pairs at the levels above, since the matrix covers role pairs, not components.

- **Selection by mode, never the primary by default.** A part chosen alone (the current page, a single-select option, a tab, a segment) takes the inverse pair, `bg-inverse` with `fg-inverse`: the fill furthest from every ground in both schemes. A neutral fill one or two steps off its surface barely shows in dark. A row chosen among several (a multi-select list, a table with a selection column) takes only a quiet neutral tint, with its own text kept, and the checked box in its leading slot carries the state; a block of inverse rows reads as a wall. `bg-selected-multiple` is that tint: the lowest of neutral steps 5 to 7 that clears `apca.ui` against a resting row, reported in the matrix with the row's text on it at `apca.text`; check the box's mark against the tint at `apca.series` (one measured light tint missed it by 0.8 Lc). A selected state is never a recessed surface. `bg-selected` is the fill of a part chosen alone: at the default `emphasis` 1 it is the lightest neutral in light and `bg-inverse` in dark, and it mixes toward the primary only above 1. Where a light single selection must be the inverse too, use `bg-inverse` with `fg-inverse` directly.
- **Disabled is never a tone.** A disabled part takes `bg-disabled` (the neutral muted fill; on another ground, that ground's own control fill) and `fg-disabled` (neutral step 8, below `fg-subtle`), whatever its tone or variant was: a disabled primary goes neutral, and so does the disabled text a toned solid or tint hands to what sits on it. No contrast level applies to disabled pairs: `contrast.unleveled` reports their Lc with level `none`.
- **Ink follows its host.** Text on a fill takes the ink solved or chosen for that fill, never the page's ink: a solid's `-on-solid`, a tint's `-fg`, `fg-inverse` on the inverse. A quieter ink on a painted fill is a step of the fill's own family, measured to `apca.hint`: on a solid it is `<role>-on-solid-muted`, the quietest step on the label's side of the solid that reaches `apca.hint` against it (`system.json › modes.<id>.solidMuted.<role>`: `{ family, step, lc, floor, reached }`; where no step reaches, the strongest is taken and the matrix reports the miss); on a tint its step 9, on the inverse a middle neutral step. Bold text keeps the color of the text around it rather than jumping to `fg-strong`, which on a solid ignores the label. Disabled text is the one exception (above).
- **White means the endpoint.** A fill or text named white or black takes an endpoint, `white` or `black` (`fg-strong` is the scheme's far end), the same in every scheme, never a ramp step that happens to be lightest or darkest in one scheme: step 12 is a light grey in dark and a mid slate in light, and step 1 is the page. By default the endpoints are the two ends of the system: white is halfway in lightness from the light page (step 1) to pure white, black is 0.6 of the dark page's lightness, and each keeps the neutral's hue, so both sit past every step without the hardness of pure (white L 0.989 and black L 0.106 on the default palette). They are never inside the ramps: where a step is already lighter or darker (a contrast mode's pure ink, a white page), the endpoint takes that lightness. Request `endpoints: { "white": "pure", "black": "pure" }` for #fff and #000, or a step number for a ramp step. `bg-inverse` is neutral step 12 and `fg-inverse` step 1 by default; a request that names an endpoint moves that side of the pair onto it (`bg-inverse` black in light and white in dark), so with `endpoints: { "white": "pure", "black": "pure" }` the inverse is true black and white in both schemes, and a dark `bg-selected` at `emphasis` 1 follows it.
- **A held solid stays solid.** A solid part held down takes `<role>-solid-active` with its `-on-solid` label, never the neutral `bg-muted-active`, which turns it grey under a light label, and not the hover, which a held part would then look the same as.
- **A dark stack climbs one neutral ramp.** A shadow barely shows on a dark ground, so in dark the fill alone must tell each layer from the one under it. Put the levels on consecutive steps of one neutral family (page 1, panel 2, card 3, popup or dialog two steps above what it floats over; a field or neutral control one step above what it sits on, its hover and press further up), rather than crossing two neutral sources of nearly the same lightness. Measure OKLab ΔE × 100 between each layer and the one beneath: the `separation` gate (2, one just-noticeable difference) is a floor for a card on the page, and a popup over a panel at 3.9 read as too weak where about 6 or more read clearly. With `neutrals`, `bg-overlay` is two steps above the card in dark (one step measured 4.4 in dark and 2.3 in dim on the default split, under the gate; two measure 10.2 and 7.2), `bg-overlay-muted` is the field inside it, and `separation.layers` reports each pair against those two gates.

## Anchors

```json
{ "role": "primary", "value": "#0a4dff", "dark": "#6f9bff", "step": 9, "reach": "key" }
```

| Field | Meaning |
|---|---|
| `role` | Any role, or `ground` (light page and dark text) and `ink` (light text and dark page) for a brand's paper and ink; with `neutrals`, also `surface` (light and dark card, Neutrals › Anchors) |
| `value` | The color (formats below) |
| `step` | Optional, 2–12 or `"auto"`. Default: 9 (the solid) on `primary`, `secondary`, `critical`, `warning`, `success` and `info`; on other roles, the step whose Lc is nearest the color's, which `"auto"` also asks for. Not for `ground`/`ink`/`surface` (exit 2) |
| `dark` | Optional exact dark-scheme color, same formats; without it dark takes hue and chroma, its solid stays at step 9 and is generated (the CLI warns with its ΔE). `brandExact: true` fills it with `value` on the brand and status roles |
| `darkStep` | Optional step for `dark`, 2–12 or `"auto"`, with the same default as `step` |
| `reach` | `key` (default): chroma changes on steps 9–12 only. `ramp` (default on neutrals): the whole ramp |
| `name` | Optional label |

Color formats for `value` and `dark`:
- `#rrggbb`;
- a CSS string: `oklch(L C H)`, `oklab(L a b)`, `color(srgb r g b)`, `color(display-p3 r g b)` (also `color(srgb-linear …)`, `color(xyz-d65 …)`, `rgb()`); an alpha other than 1 rejects;
- a tagged color: `{ "colorSpace": "oklch" | "oklab" | "srgb" | "display-p3", "components": [3 numbers], "alpha": 1 }`.

Anything unreadable exits 2. Wide-gamut values are kept: an anchor is clipped only to the mode's output gamut (`settings.target`), by reducing OKLCH chroma at its lightness and hue, before the ramps and solids are solved. So `color(display-p3 0 0.8 0.3)` with `target: display-p3` stays exact (the sRGB block of `system.css` shows its sRGB fallback, the P3 block the exact value); with `target: srgb` it becomes the nearest sRGB color of that lightness and hue. Each `anchorReport` entry carries `source` (the request's value) and `gamut: { target, inTarget, inSrgb, requested?, clipDE? }` (`clipDE`: OKLab ΔE × 100 lost to clipping), for `dark` too.

Every step except the page takes the anchor's hue; the anchored step becomes exact, neighbours settle, and an anchor on steps 8–12 moves the role's solid there. Read `system.json › anchorReport`: An anchored family never takes the bright-hue cusp, in any scheme: its solid stays the brand's own colour (or, without `dark`, the generated step of its hue and chroma). `stepFrom` records how the step was chosen (`solid`, `nearest-lc` or `given`). `inOrder: false` means the color breaks the contrast order (text then needs a higher step of the family, for example 11 for a light gold); `inRange: false` means it lies beyond the ramp (use `endpoints`).

### Family anchors

`familyAnchors` pins a family by name, for colours that belong to a family rather than a role: matching a reference palette step by step (each Radix accent's step 9), or a brand that names its own hues. Same fields and semantics as an anchor, without `role`; `step` defaults to 9 and, when `dark` is given (or `brandExact` fills it), `darkStep` to 9.

```json
{ "settings": { "hueSet": "radix" }, "brandExact": true,
  "familyAnchors": { "orange": { "value": "#f76b15" }, "blue": { "value": "#0090ff" } } }
```

The roles keep their families and no semantic variable moves. Each entry has an `anchorReport` row with `role: "family:<name>"` and the same warnings as a role anchor. A family that a role anchor already pins exits 2 (anchor one of them); with `familyNames`, use the family's output name.

### Plain-word requests

| The user says | Map to |
|---|---|
| "match Radix", "pin each family's step 9", "keep this family's colour exact" | `familyAnchors` (with `brandExact` for the same solid in both schemes); a role's colour is an `anchors` entry |
| "step 1 is too close to white / black" | Step 1 is the page: lower `toneMax`, raise `darkTone` |
| "step 1 has no colour", "step 1 is faint" | `tint` (up to 100), `rc: 1`, a higher `falloff`; on a specimen, paint the sheet on the white / black endpoint so step 1 reads as a tile |
| "orange looks rusty", "greens look dark next to Radix" | Every solid sits at one APCA contrast, so naturally light hues are darkened (hue is kept). Offer `familyAnchors` at Radix's step 9 |
| "dark solids look different from light" | `modes.dark.settings.keyDepth` (it switches at the label choice; compare `solidLabels`), or `familyAnchors` with `brandExact` |
| "text looks brown" | Steps 11–12 sit at high Lc targets (light 83.2 and 95). Offer the request below; the defaults stay |

The "text looks brown" request lowers the light targets for steps 11 and 12 to 75 and 90 and keeps the other nine:

```json
{ "settings": { "targetsLight": [5.5, 11.6, 18.4, 25.8, 33.8, 42.4, 51.7, 61.6, 72.1, 75, 90] } }
```

Measured with `scripts/system.mjs` on that request (the default hue set, `modes.light.ramps.orange`):

| Light orange | Default (`{}`) | With the request |
|---|---|---|
| Step 11 | `#7e3b00`, Lc 83.6 | `#8b4100`, Lc 80.3 |
| Step 12 | `#502200`, Lc 94.8 | `#662d00`, Lc 89.8 |

Step 12 lands on its target. Step 11 stops near Lc 80, not 75: steps 10 and 11 are spaced evenly in Lc between the solid (step 9) and step 12, so their own targets are not read and step 11 follows step 12. Both are still brown-leaning oranges, only lighter. To bring step 11 to Lc 75, set the last target to 82 (orange 11 `#9f4c00`, 12 `#834000`). Light and dark pass `apca.text` (45). In light-contrast, the shorter key run leaves two label-on-hover pairs (`secondary-on-solid` and `warning-on-solid`, Lc 35.8 against 60), so check `system.json › modes.light-contrast.contrast.summary` before shipping it with `contrast: true`. Dark text steps are light on a dark page and are left at the defaults.

### Brand colours

A system made from a brand's named colours: one anchor per colour, by what the colour is used for. Set `"brandExact": true` so every accent is its own solid in both schemes, and read the `WARNING anchor` lines before you report.

| Brand colour used as | Anchor | Note |
|---|---|---|
| Light page / paper | `ground` (`value`) | Ground 1 in light |
| Dark page / dark section background | `ink` with `dark` | The `ink` anchor's `dark` is ground 1 in dark; its `value` is the light body text |
| Body text | `ink` (`value`) | Ink 12 in light |
| Cards, panels, dividers | `surface` (needs `neutrals`) | Surface 1; add `dark` for an exact dark card, else it is derived |
| Accent, mark, call to action | `primary`, then `secondary` | Step 9 in both schemes with `brandExact`; a light accent under `apca.text` is not text: use step 11 |
| Label or caption colour | `secondary` | No label slot yet: `fg-muted` stays ink 11 |
| Any of the accents, under the brand's own name | `familyNames: { "amber": "gold" }` | Read `modes.<id>.roles` for the families the roles took |
| Error, warning, success, info picked to match | `critical`, `warning`, `success`, `info` | Step 9; give `dark` per scheme for a dark solid that clears its label |

For dark used only on some sections, add `"autoDark": false` and a forced-only extra mode (Modes). Write roles by OKLCH hue as `oklch:NN`: `hNN` is HCT and lands elsewhere (a gold at OKLCH 84° is HCT about 80°).

## Family files

`scripts/families.mjs` lays a system out one family per file, for a design-system repository that imports only the families it uses. It reads a `system.mjs` output folder and writes a new one:

```sh
node scripts/families.mjs --from SYSTEM_OUTPUT_DIR --out NEW_DIR [--light light] [--dark dark]
```

| File | Holds |
|---|---|
| `globals.css` | `color-scheme` only: `:root` follows the OS, `.light` / `.dark` and `[data-color-mode]` force a scheme on any subtree |
| `colors-p3/<family>.css` | Steps 1–12, alpha steps `a1`–`a12` and the tonal stops of one family, in the target gamut (with `target: display-p3`) |
| `colors-p3/semantic.css` | Every other variable: the roles, endpoints, series, shadows |
| `colors-p3/<name>.json`, `.dtcg.json` | Each value as CSS, OKLCH, P3 components, alpha and an sRGB hex fallback; DTCG paths `colors.<family>.<light\|dark>.<step>`, semantic tokens as aliases |
| `colors-p3/index.css` | Imports globals, every family, then semantic |
| `colors/…` | The same files with every value mapped into sRGB (the `system.css` sRGB block) |
| `manifest.json` | Every file with its size and SHA-256, the families and their solid labels per scheme, anchors, roles with both values, step groups, contrast summary |
| `README.md`, `USAGE.md` | Files and naming; how to use the steps, the solid labels, alpha steps and roles, generated from the same data |

Two modes go in, one light-scheme and one dark-scheme (`--light`, `--dark`; default `light` and `dark`): each variable that differs is written as `--x-light`, `--x-dark` and `--x: light-dark(var(--x-light), var(--x-dark))`, one that is equal in both is written once. Contrast and extra modes are not laid out (light-dark() has two schemes). `light-dark()` needs Chrome 123, Safari 17.5, Firefox 120. Checked by `check.mjs` (every variable resolves in both schemes, step 9 exact to the system, manifest hashes current).

## Showcase

With `showcase: true`, `showcase.html` is one self-contained page (it inlines `system.css`) laid out per [showcase.md](showcase.md): Ramps, Neutral & surfaces, Roles, Transparency, Modes, Brand, Data, Scales & checks, three specimens each. The sheet is the forced light mode; every panel that shows another mode carries that mode's forced selector (`.dark`, `.light.contrast-more`, `[data-color-mode=dim]`…, with the scope's classes or attributes), so it takes that mode's variables, `light-dark()` values included. The Modes group shows light, dark and the first extra mode in run order. With `neutrals`, Neutral & surfaces shows the ground, surface and ink strips and a card (surface) on the page per shown mode with its separation, the mode cards sit on `surface`, and the ramp tiles keep the accents and gray (= ink). A feature the run turned off (alpha, series, tonal, anchors, diverging, extra modes, a P3 target) keeps its specimen as a labelled empty state. With more than 16 families (Radix hues) the ramp tiles show the families the roles use.

The step-use specimen carries the construction annotation: each primary step's `apcaOnPage` next to its target, the `primary-on-solid` / `primary-solid` APCA Lc against the solid floor, the key run 9–12 (page Lc), which families take the dark label in light and dark, the bright-hue window and its families, and every key-run deviation (grouped per mode); in both ramp tiles step 9 carries an "A" in its family's label for that mode. Roles show each solid's and hover's Lc against its label and each status role's `-fg` Lc on `bg`; the contrast excerpt shows Lc, threshold and pass. Machine-readable marks, which `scripts/check.mjs` reads: `data-group`, `data-specimen`, `data-mode-panel`, `data-annot` (`lc` with `data-step`, `data-lc`, `data-target`; `solid-lc` with `data-step`, `data-value`, `data-floor`; `keyrun` with `data-lc`; `labels`), `data-label` on each step-9 tile and `data-flag`: `lc-miss` (`data-mode`, `data-count`), `series-weak` (`data-mode`, `data-kind`, `data-value`), `keyrun` (`data-mode`, `data-family`, `data-step`, `data-reason`), `anchor-order`, `anchor-range`, `anchor-clip` (`data-role`, `data-modes`).

## Figma

`figma-variables.json`: `{ $description, collections: [{ name: "Color", modes: [mode ids], variables }, { name: "Palette", modes: ["default"], variables }] }`. Each variable is `{ id, name, type: "COLOR", valuesByMode, resolvedValuesByMode }`:
- `id` is stable across runs: `Color:<name>` or `Palette:<name>` (names: `indigo/9`, `primary-solid`, `gray/a3`, `cyan/050`, `tonal-role/primary/9`);
- `valuesByMode[mode]` is RGBA `{ r, g, b, a }` (sRGB 0–1), or `{ "type": "VARIABLE_ALIAS", "id": "<variable id>" }` when the role points at a ramp step (directly or through other roles) — `primary-solid` → `Color:indigo/9`, a `tonalRoles` alias → `Palette:indigo/450`. Translucent roles (`color-mix(… X%, transparent)`) stay resolved, with alpha X/100. Variables that don't resolve to one color (`bg-selected`, mixed from `--ui-emphasis`) are left out;
- `resolvedValuesByMode[mode]` is always the plain RGBA, for importers without alias support.

For the Variables REST API, create the variables with these ids as temporary ids and send `valuesByMode` as each mode's value.

## Checks

```sh
node /absolute/path/to/ui-colors/scripts/check.mjs [--keep]
```

Runs `system.mjs` on `{}`, on a light-dark request (`brightHues: false`, `lightDark`, `split`, `figma`, `tonalRoles`, `showcase`, dim and both contrast modes), on `{ "showcase": true }`, on a scoped attribute-selector sRGB showcase request with an out-of-order and a clipped anchor, on an APCA-override request with anchors at step 9 (both schemes) and 11, and on three neutrals requests (Sand ground and Slate surface crossed, with the showcase; generated tinted ground, surface and ink with `lightDark`, `split`, `figma` and dim; ground, ink and surface anchors whose card is too close to the page), and on a brand-colours request (generic page, card, text, dark-section, accent and low-chroma label anchors with `brandExact`, `autoDark: false`, `series: false`, a forced `on-dark` mode and a `familyNames` map) plus the same without `brandExact` or a dark colour, in a temporary directory, then checks, with its own color maths (APCA through the vendored `apcaLc`):
- **fixture**: `scripts/system/fixtures/hct-default.json` holds the raw engine ramps (before the solid and border solves) at the targets it was made with, which predate today's defaults (light `7.3 … 85.7`, dark `3.4 … 77.1`). The check measures those targets from the fixture's neutral, regenerates the raw engine ramps at them and compares all 12 steps of all 13 families, light and dark: ΔE OKLab × 100 ≤ 0.1. (The post-solve default output differs from the fixture by design; it is covered by the next two checks.)
- **placement**: in the default output, every family's steps 2–7 within 1.5 Lc of their target and accents' step 12 within 2.5 (steps 8–11 are moved by the border solve and the key run);
- **floors** (APCA), recomputed from the ramps at thresholds the check derives from the request on its own (defaults, `apca` overrides, contrast +15 or `apca.contrast`): every family's solid and its hover against its own label (the light mode's gray 1 or gray 12, as `solidLabels` names it) and the reported Lc, each role's `-on-solid` equal to that label; control border ≥ `ui`; series ≥ `series`; `modes.<id>.apca` equal to the derived thresholds;
- **apca key**: an override run (`solid 60`, `hint 60`, `contrast.solid 75`) is checked at those thresholds, and eight bad values (string, negative, over 108, unknown key, non-object `contrast`, out-of-range `contrast` value, array, unknown `contrast` key) each exit 2;
- **bright hues**: the window read from the request on its own (default 70°–125°, `false` none); a family whose generated step-9 hue is inside takes the dark label and carries `brightHue`, one outside never does; the default run has bright-hue families, the light-dark run (`brightHues: false`) none; six bad `brightHues` values exit 2;
- **white first**: each mode's ramps regenerated before the solid solve (engine at the mode's settings, keys shaped), independently of `system.mjs`: the recorded `generated` step matches; a generated step 9 that reaches the floor against white takes the light label, unless its white run (APCA reads tones only, so the lightest hover tone white allows and the step 9 it implies, `(3·Lc10 − Lc12)/2`, are exact) would put step 9 under `ui` on the page — then dark with `whiteRejected`; a solid that passes its label is unmoved by the label solve; every later change of step 9 has a recorded reason (`hoverRoom`, minimal: the hover lands at the floor ± 0.3; or `cusp`) (runs without anchors);
- **cusp**: each dark-label accent's step 9 at its hue's cusp (the check's own scan), lowered only as far as `ui` on the page or the 15 Lc key-run room needs, at the gamut's maximum chroma there, hue unrotated; no cusp mark on a light-label or anchored solid;
- **brand colours**: with `brandExact`, every accent anchor is its family's step 9 in every mode (ΔE ≤ 0.5); no `prefers-color-scheme` block with `autoDark: false`; no `--colors-data-N` with `series: false`; the `familyNames` map's name emitted and the hue name gone; without `brandExact`, no anchored family at its cusp or marked bright in any mode; bad role names and hues, a `step` on `ink`, a non-step `step`, a bad `autoDark` and bad `familyNames` maps exit 2;
- **key run**: page Lc of steps 9–12 recomputed and equal to `keyRun.lc`; every step between fixed points (9, 12, anchored 10–12 from the anchor report, each recorded deviation) within ±0.5 Lc of even spacing — the solver bisects lightness to ~1e-9 with the same tone maths, so the only slack is JSON's 6-decimal rounding (measured 0.000 Lc); 0.5 is a third of a just-visible 1.5 Lc step; lightness monotonic; steps 11–12 ≥ `text` on the page and on step 3; every deviation real (not evenly spaced) and at its own floor;
- **files** exist; **CSS** (system.css, the preview's stylesheet, the split files together) has balanced braces, `;`-terminated declarations and no `var()` without a declaration;
- **light-dark**: root `color-scheme: light dark`, forced light/dark and every extra mode's blocks with their own scheme, a P3 `light-dark()` pair for every variable that leaves sRGB in either scheme;
- **split** files declare everything `system.css` does, and each mode file re-declares every `var()` role;
- **Figma**: every alias names a variable in the file whose resolved color equals the alias's own;
- **contrast** pairs recomputed from the ramps (Lc ±0.1, informational ratio ±0.02), each threshold the intent's, `pass` consistent; **pressed solid**: `side` on step 11 exactly where the label clears `apca.solid` there, else a back step at `max(Lc9 − (Lc10 − Lc9), apca.ui)` on the page with `clamped` consistent, the label at `apca.solid` on it, `lc` and `lcOnPage` recomputed, each role's variable that alias or colour; **hover** pairs and the neutral's steps 1–6 recomputed from the variables and ramps (ΔE ±0.05, a translucent fill composited over its ground), threshold 4, `pass` and `summary` consistent, every pair present; **series CVD** unsimulated minimum recomputed; **tonal** agreement and map present;
- **showcase**: written only when requested; 24 specimens in the 8 groups, three each; the annotation's Lc, targets, the solid's Lc and floor, and the key run 9–12 equal `system.json` (and, for the key run, the ramps) in attributes and visible text; exactly the failures `system.json` reports are flagged (APCA misses per mode with their count, series minima under the threshold, key-run deviations, anchors out of order, out of range or clipped); each mode panel carries its forced selector, scope included; every color is a variable `system.css` declares, a value from `system.json` or a light step's sRGB fallback, and the sheet's own CSS names no color. Layout (fit, overlap, blank swatches, legibility) needs a browser at 1280 × 960 and is not checked here.
- **neutrals**: the default run's `system.css` and `system.json` hash to `scripts/system/fixtures/default-digest.json` (byte-identical default; after a deliberate change to the default output, refresh it with `check.mjs --update-digest`) and carry no split variable or field; every split role points at its family and step (the table above, restated in the check), `gray-N` is `var(--colors-ink-N)` and ink N is the gray ramp's color; each family's steps 1–7 equal the neutral the engine makes for its spec at the mode's settings (the surface at the lifted page; ground and surface specs swapped in dark when `cross`), skipping anchored ends; the cross run names Slate for the dark page and Sand for the dark cards; separation recomputed (ΔE ± 0.05, Lc ± 0.1, threshold 2, `pass`), every mode separated in the unanchored runs and the anchored run has a miss to flag; anchors pin ground 1 / ink 12 / surface 1 and their dark ends; floors with the split labels, control border on ground 1–2 and surface 1–2, series on ground 2; key run, contrast (with the split pairs), CSS, light-dark, split files and Figma on the split runs; the preview shows the three families; the showcase's Neutral & surfaces group has the three strips and a surface card on the page per shown mode with its ΔE, and separation misses are flagged; 15 bad `neutrals` values or combinations exit 2.
- **family anchors**: a run pinning orange and teal by name with `brandExact`: each exact at step 9 in every mode, the roles where they were, no internal `family:` name in roles or CSS; unknown role names, unknown families, a family a role anchor pins and bad keys exit 2;
- **family files**: `families.mjs` on that run: every variable in `colors-p3/` and `colors/` resolves to a colour in both schemes through `light-dark()` and `var()`, each family's step 9 equals the system's, and every `manifest.json` hash is current;

Then 74 negative controls mutate a copy (move a fixture step or a placed step; lighten a solid, bring a contrast-mode solid under Lc 60, push a hover under the floor, claim the light label for a dark-label solid, give a role the other label, raise the request's `apca.solid`, drop the control border, slip a valid `apca` or `brightHues` value into the bad list; put a bright-hue family on the light label, mark a family outside the window bright, read `brightHues: false` as the default; give a white-passing solid the dark label, reject white without cause, put a white-rejected solid back on white, move a passing solid, report a failing solid as kept, widen a hover room; pull a cusp solid back, rotate its hue, drop its cusp mark; push step 10 or 11 off even spacing, collapse step 12, drop a recorded deviation, misreport `keyRun.lc`; put a series under the surface floor; delete a file, drop a brace or a declaration, flip a `color-scheme`, drop a P3 pair or a split declaration, misroute a Figma alias, misreport an Lc, pass a pair under its threshold, give a pair the wrong threshold, misreport a ΔE, alias a pressed solid to step 11 where its label fails there or to the hover, put a back step under `apca.ui`, misreport a hover ΔE, pass a hover under 4, drop a hover pair, drop a tonalMap role; in the showcase: delete it, drop or add a specimen, misreport an Lc, a target, the solid's Lc or floor or the key run, drop an APCA-miss, key-run or anchor flag, report a weak series the sheet doesn't flag, flag an anchor `system.json` reports in order, strip a panel's forced class or attribute, inject a color or a sheet color literal; neutrals: change the default output by one byte, add a split variable to the default run, read `border` from the ground, leave `fg` on gray, break the gray alias, swap the dark ground and surface back, drop the surface lift, read `cross` as off, misreport a separation, set the card to the page color, unpin a ground anchor or a surface anchor's dark color, drop a separation flag, drop the ink strip, draw a dark card on the wrong role, slip a valid `neutrals` value into the bad list); each must make its check fail. Exit 0 when every check passes and every control bites; 1 otherwise.

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

A default run (five modes plus the tonal scale) takes 1–3 s and needs no network or packages; `generator: oklch` never starts the engine. The engine is a vendored bundle (`scripts/system/runtime.json`) that starts with `new Function`, so generate at build time rather than in a page with a strict Content-Security-Policy. Its third-party notices travel inside it; see `references/system-notice.md`. `scripts/system/fixtures/` holds the HCT and OKLCH ramps for checking a port (`check.mjs` reads the HCT one).
