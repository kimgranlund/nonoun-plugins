---
name: ui-showcase-bento
description: Generate bento showcases - a fixed canvas of labelled groups and specimens, packed to fit with nothing scaled down, built from one or more sources (a UI skill such as ui-geometry, ui-colors or ui-materials, a framework such as shadcn or MUI, or a brand), with mode, material and anatomy switches and an in-page checker for overflow, clipping, scaling, labels, left edges and boxes that must not move between switches. Use for "make a showcase", "specimen sheet", "bento of our components", "show the system on one page", or a showcase combining geometry, colour and materials. NOT for deriving lengths (ui-geometry), colours (ui-colors) or paint (ui-materials), or a colours-only sheet (ui-colors makes its own); NOT for a jig that tunes a system's constants (ui-kit-inspector), comparing implementation alternatives of one component (component-variants), wireframes (wireframe-review) or documenting a brand system as audited sheets (brand-system-sheets); NOT for implementing a component library.
---

# UI showcase bento

A bento is one fixed canvas (1280 × 960 unless a source sets another) of labelled **groups**, each holding labelled **specimens**, on tiles ruled as grid paper that the page's bar can switch off. This skill owns the showcase canvas: the source contract, the packing, the page and its texture, the switches and the checks. It chooses no colour, length, typeface or paint; those come from **sources**. Each UI skill keeps its own showcase brief and can still be shown alone. Terms are defined once in `references/terms.json`.

Contents: [Route](#route) · [Sources](#sources) · [Procedure](#procedure) · [Rules](#rules) · [Commands](#commands)

## Route

| Question | Read | Load when |
|---|---|---|
| Make a sheet from existing sources | [Procedure](#procedure) below | Always, for a new sheet |
| Which spec keys, values and merge rules exist; what the page and checker guarantee | `references/contract.md` | Writing or reading a source, a layout or a page by hand |
| Show a new skill, framework or brand | `references/sources.md` | No shipped source covers it |
| Draw specimens, fit the canvas, check by eye, publish | `references/authoring.md` | Writing specimen fragments, or the sheet fails its check |
| What a word means here (`theme`, mode, tile, part, owner …) | `references/terms.json` | A term is ambiguous or shared with a sibling skill |
| How a part is painted (relief, face, lines, shadows) | ui-materials | Writing the material tokens; never here |

## Sources

| Source | Owns | Content | Adds |
|---|---|---|---|
| `ui-geometry` | lengths: canvas 1280 × 1600, margin, gutter, tile depth and radius, gaps, grid ruling | Geometry 28: ARIA 24 plus a Type group and a Space group | the geometry acceptance |
| `ui-colors` | colours: chrome mapped to its role variables | Colour 24 | its `system.css` and the mode switch (light, dark, dim) |
| `ui-materials` | paint (informational) | ARIA 24 | the material switch (flat, physical, frosted, glass, outline) with each preset's settings as caption, and the anatomy switch (off, layer, relief, face) |
| `sources/templates/framework.json` | the framework's tokens | ARIA 24 | its stylesheet; the specimens are its own components |
| `sources/templates/brand.json` | the brand's tokens | identity and voice | its stylesheet |

Sources layer in the order given. Merge rules: `references/contract.md` › Merging.

## Procedure

Run scripts by full path from `scripts/`. `--work <dir>` is where generated tokens and the page live.

1. **Choose sources.** A named skill → `sources/<id>.json`; a framework or brand → copy a template and fill it in (`references/sources.md`). Read each source's `brief`: it holds the required depictions and wins over anything here. Add a layout source when one exists for the content source: `geometry-28-1280` for the `ui-geometry` content at full size, `aria-24-1280` for a source that shows ARIA 24 alone. Add a local source last for the title or canvas.
2. **Produce the tokens.** Run each source's `tokens.commands`. With ui-materials among the sources, run its request command first: it writes the colours request, with the paint roles lit materials need, that ui-colors' generator then reads. The scaffold refuses a missing stylesheet and names the command.
3. **Pack.** `node scripts/pack.mjs <sources…>` prints areas, tracks and tile sizes; `NOFIT` (exit 1) names the shortfall in px and means no arrangement of these tracks fits. Then rearrange the areas, shorten labels or change a parameter. Never scale.
4. **Draw the specimens** with a generator script that writes `<work>/specimens/<specimen-id>.html` and one stylesheet (`references/authoring.md`). Mark deliberate exceptions with `data-inset` and empty states with `data-empty`. Nothing operable.
5. **Scaffold.** `node scripts/scaffold.mjs <sources…> --work <dir> --specimens <dir>/specimens --style <dir>/specimens.css --out <dir>/showcase.html`, with `--standalone` to view the file locally over http. Re-running it loses nothing, because specimens live in their own files.
6. **Check in a browser** at the canvas size: `await document.fonts.ready`, then `uiBentoCheck({ final: true })`. It checks every axis combination up to 256 (`references/contract.md` › Checks).
7. **Close the loop.** On overflow, save `needs` as JSON and repack with `--mins`. Before growing the canvas, put a too-tall tile's specimens on one line. Squeeze one row in place once: the check must fail.
8. **Look, then report.** Screenshot at least two modes and three materials, Outline in dark among them. Report the sources and what each owned, the tracks and canvas (and whether it was raised), the check's summary and warnings, and each acceptance item the check cannot prove, marked checked by eye or not checked.

## Rules

| Rule | Why | Check |
|---|---|---|
| Never scale a specimen; give it room, shorten labels or change a parameter | A scaled specimen misstates every length | `uiBentoCheck` scaled error; fixture `scaled` |
| Every box stays inside its tile's content box | Content in the padding breaks the tile's depth | `uiBentoCheck` clipped and overflow errors; fixtures `overflow`, `padding` |
| Every group and specimen has a label; a feature that is off keeps its specimen and names the key that turns it on | A reader identifies every entry by name | `uiBentoCheck` label and empty-state errors; fixture `label` |
| No box moves along an invariant axis | Switching mode or material must repaint only | `uiBentoCheck` invariance error; fixture `moves` |
| Comparisons are identical: state and mode variants sit in one specimen with the same content and dimensions | A difference must come from the state alone | Judgement, by eye |
| Captions and first-line content start on the specimen's edge | One left edge per specimen | `uiBentoCheck` edge warning |
| Whatever a source reports as failing, the sheet shows, and nothing else is flagged | The sheet is evidence, not decoration | Judgement, against the source's report |
| No app chrome, invented metrics or placeholder text; labels come from the brief | Filler hides what the system does | Judgement, by eye |

## Commands

- `node --test scripts/`: packer, merge, scaffold, closed sets, terms closure, brief and catalogue agreement, and the checker fixtures in headless Chromium (skipped when none is found).
- `node scripts/check-fixtures.mjs`: the checker fixtures alone, one line per case.
- `node scripts/terms.mjs`: `references/terms.json` against every name the skill emits.

Files: `scripts/lib.mjs` (load, validate, merge, pack), `scripts/pack.mjs` and `scripts/scaffold.mjs` (command lines), `scripts/check.js` (the in-page checker), `catalogues/` (shared group sets), `layouts/` (tested layout sources), `sources/` (the three skill sources, templates, the anatomy overlay), `evals/triggers.json` (trigger cases for the description; rerun them when the description or scope changes).
