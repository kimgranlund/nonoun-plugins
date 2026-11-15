# Color system showcase

Use this brief when asked for a showcase, specimen sheet or overview of what a generated color system contains, or to review one at a glance. `scripts/system.mjs` builds it when the request has `"showcase": true`; this brief defines its content, layout constraints and acceptance criteria. It is not needed for ordinary generation.

The color system supplies every color. The sheet supplies only neutral page chrome (layout, system type, borders drawn with the run's own border roles). This brief does not prescribe a palette, typeface, icon family or theme.

## Output

One static specimen sheet, `showcase.html`, on a **1280 × 960px canvas**, from a single `system.mjs` run: the default `{}` plus `"showcase": true`, or the user's request with it added. It contains **24 specimens in eight groups**.

- Every color comes from that run: a CSS variable of its `system.css` (inlined in the page, so the file is self-contained) or a value read from its `system.json` (simulated CVD colors, anchor values, a step's sRGB fallback). Never a hand-picked color.
- The sheet adds no styling of its own beyond neutral chrome and system type; its own stylesheet names no color.
- The sheet itself is the forced light mode; every specimen that depicts another mode sits on a panel carrying that mode's forced selector.

User-supplied requests change what the sheet shows, never its structure: recompute content, keep the 24 specimens.

## Parameters

| Parameter | Default | Source |
|---|---|---|
| Canvas | 1280 × 960px, 12px margin | fixed |
| Request | `{ "showcase": true }` | the user's request plus `showcase: true` |
| Modes shown | light, dark and one extra mode | the first extra mode in run order (contrast or dim, whichever exists); none with `extraModes: false` |
| Primary ramp | `modes.light.roles.primary` | `system.json` |
| Type | system UI font, 8–13px | chrome |
| Selector mounting | classes or attributes of `forced(mode)`, scope included | the run's `selectors` and `scope` |

`scope` must be classes and/or attributes (`.brand`, `[data-theme=brand]`) so a panel can carry it; any other scope exits 2 with `showcase: true`.

## Grouping

| Group | Specimens |
|---|---|
| Ramps | 12-step light ramps (all accent families + neutral) · 12-step dark ramps · step-use legend (bg / fill / border / solid / text bands) |
| Neutral & surfaces | neutral ramp with its tint source · page/surface ladder (bg → bg-subtle → bg-muted) · control fills (rest / hover / active). With `neutrals`: the three families (ground, surface, ink) · a card on the page per shown mode · control fills on the surface |
| Roles | primary and secondary solids on their own label, light and dark, with APCA Lc · status roles (critical, warning, success, info) as solid on its own label + subtle + border + fg, fg Lc on bg · focus ring on a solid and on a surface |
| Transparency | alpha a1–a12 over the page · the same alpha over a contrasting surface (shows the tint) · backdrop over content |
| Modes | the same mini UI card in light · dark · one extra mode |
| Brand | anchor report (requested vs pinned step, Lc vs target, ΔE, order) or a "no anchors" state · ground and ink if anchored, else the page and ink endpoints · P3 vs sRGB fallback pairs for the widest-gamut steps (Display P3 target), else an sRGB-only note |
| Data | six series bars with labels · the same bars under simulated deuteranopia and protanopia with their minimum ΔE · sequential and (if enabled) diverging ramps, else sequential only, noted |
| Scales & checks | 050–950 tonal scale for primary and neutral (+ Primes as dots if present) · contrast matrix excerpt (worst five pairs per shown mode by APCA margin: Lc, threshold, pass) · tonal ↔ role map (each primary step → nearest stop) |

Label every group and each of its three specimens. State and mode comparisons are variants within one specimen, never extra specimens. A feature the run turned off (alpha, series, tonal, anchors, diverging, extra mode, P3) keeps its specimen and shows a labelled empty state saying which key turns it on.

## Composition

- Fit the sheet within the canvas without scrolling, clipping or overlap.
- Unequal bento tiles sized to content: Ramps and Modes are the largest (top row), Scales & checks runs tall, Data runs wide. No fixed proportions beyond fitting.
- Never scale specimens down to fit; cut words from captions instead. With many families (Radix hues) ramp rows grow thinner, columns stay.
- Comparisons keep identical content and dimensions: the three mode cards, the normal / deutan / protan bar charts, the light and dark halves of the surface ladder, control fills and ground/ink.
- Every swatch strip names its family and step (row label + step header, or a label under the swatch).
- Numbers (Lc, targets, ratios, ΔE, stops) are read from `system.json`; none is recomputed or rounded differently on the sheet.
- Every warning or failure in `system.json` is visible: contrast pairs under their APCA threshold (count per mode, the failing pairs in the shown modes' excerpts), any series minimum ΔE under the threshold (per mode and simulation), key-run deviations from even spacing (per mode, family, step and reason), anchors out of order, out of range or clipped to the gamut (per anchor, with the modes), and with `neutrals` every mode whose surface fails to separate from the ground (`data-flag="separation"`, `data-mode`).
- With `neutrals` the light and dark ramp tiles show the accents and gray (the ink); ground and surface have their strips under Neutral & surfaces, so the tiles keep the default's row count.
- No application navigation, invented metrics or decorative filler; the mini UI card is the only composed scene.

## Required depictions

| Specimen | Depiction |
|---|---|
| Light ramps | Every family's steps 1–12 on a light panel, rows labelled by family, columns by step; step 9 carries an "A" in the label its family takes in that mode (`solidLabels`) |
| Dark ramps | The same on a dark panel |
| Step use | The primary ramp under the five bands, with the construction annotation, the families that take the dark label (light and dark mode), the bright-hue families, and key-run deviations |
| Neutral ramp | gray 1–12 labelled, and its tint source: the accent and tint %, a ground/ink anchor, or "untinted". With `neutrals`: "Neutral families", ground, surface and ink 1–12 as three labelled strips (light), with each family's source, the surface lift and whether dark is crossed |
| Surface ladder | bg holding bg-subtle holding bg-muted, light and dark. With `neutrals`: "Card on page", per shown mode (light, dark, extra) a `surface` card with `border` and a `bg-muted` well on `bg`, the mode and its separation ΔE (✓ or ✗; a mode under the threshold is flagged `separation`) |
| Control fills | bg-control, -hover, -active inside control-border, light and dark (on `surface` with `neutrals`) |
| Solids | per mode (light, dark): primary and secondary solid and solid-hover with their own `<role>-on-solid` text; each role's family, label (light or dark) and APCA Lc on solid / hover |
| Status roles | each status role's solid chip with its `<role>-on-solid` text, a subtle chip with its border and fg text, and fg-on-bg APCA Lc |
| Focus ring | focus-ring outline (2px, offset 2px) around a solid and around a surface |
| Alpha over the page | a1–a12 of the primary family and gray on the page |
| Over a contrasting surface | the same rows on bg-inverse |
| Backdrop | bg-backdrop over page content with a dialog above it |
| Mode cards | one identical card (title, status chip, body, field, list with a selected row, alert, six-series chart, primary and neutral buttons, hint text) per shown mode, on `bg-subtle` (on `surface` with `neutrals`) |
| Anchor report | per anchor: requested value and swatch, pinned family and step (dark step if different), Lc vs target, ΔE, flags |
| Ground and ink / page and ink | light and dark panels showing ink on page with both hex values |
| P3 vs sRGB | up to six steps whose sRGB fallback differs most from their P3 value, as split swatches with ΔE |
| Series | data-1…6 bars, numbered, with each series' family and step |
| Series under CVD | the same bars with `seriesCvd.light.deutan.hex` and `.protan.hex`, their min ΔE and pair; all modes' sub-threshold minima flagged |
| Sequential & diverging | data-seq-1…7 and data-div-1…11 labelled by step |
| Tonal 050–950 | primary and gray stops labelled, Primes as dots when present |
| Contrast excerpt | per shown mode the five weakest pairs by Lc over their APCA threshold (more when more pairs miss, up to eight), with a sample, Lc, threshold and pass; the APCA-miss count of every mode |
| Tonal ↔ role map | primary steps 1–12 above their nearest stop, with ΔE and the solid's stop |

## Construction annotation

On the step-use specimen, label each primary step's APCA Lc against the page next to its target (step 1 is the page), the primary solid's APCA Lc against its own label (light or dark) with the solid floor (`apca.solid`, 45 by default), the key run 9–12 as page Lc (evenly spaced thirds), which families take the dark label in light and dark mode, the bright-hue window and the families in it (dark label at the cusp), and every key-run deviation as a flag, grouped per mode. Steps moved off target by a solve are marked `*`, an anchored step `◆`. It proves: *steps sit at their contrast targets; solids are solved to their label; 9→12 is one even run.* Do not add a twenty-fifth specimen for it.

## Static rendering

- HTML, no script, no interactivity: every state shows immediately.
- No operable controls: buttons, fields and list rows are drawn spans, out of the tab order, with no interactive roles.
- Groups are labelled sections, specimens are figures with captions that describe what they show; color is never the only carrier (steps are numbered, failures carry ✗ and text, the selected row carries ▸).
- A visual demonstration of the color system, not evidence of a UI's accessibility conformance.

## Specimen content

- Short, plausible labels; identical text in every mode card.
- Units and names as in `system.json`: `Lc`, `:1`, `ΔE`, role and variable names.
- Numeric labels agree with what is drawn (the solid outline sits on the solid step; bar numbers match series order).

## Acceptance criteria

1. 24 specimens in the eight groups, three each, every one labelled.
2. The sheet fits 1280 × 960 with no scrolling, clipping or overlapping specimens.
3. Every color resolves from the run's variables or `system.json`; no swatch is blank; the sheet's CSS names no color.
4. Each mode panel takes its mode's variables (forced classes or attributes, scope included).
5. The construction annotation's Lc, targets, solid Lc and floor, and key run equal `system.json`.
6. Every flagged failure in `system.json` is shown, and nothing else is flagged.
7. Light and dark text is legible on its own panel.
8. Inspected at the target size; if it could not be viewed, say so rather than claiming the layout was verified.

`scripts/check.mjs` checks 1, 3 (color sources), 4, 5 and 6 on six runs (two with `neutrals`, which also check the Neutral & surfaces content) with negative controls; 2, 3 (blank swatches) and 7 need a browser at 1280 × 960.
