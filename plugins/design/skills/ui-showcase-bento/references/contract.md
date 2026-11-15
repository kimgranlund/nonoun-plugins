# Contract

## Spec

A source is JSON. Every key is optional except `id`. Every key and every closed value below is declared once in `SETS` in `scripts/lib.mjs`; `validateSource()` refuses anything else when a source loads, so a typo fails instead of doing nothing.

```jsonc
{
  "id": "ui-geometry",
  "title": "Geometry showcase",                  // page title; the last source with a title names the page
  "brief": "{skills}/ui-geometry/references/showcase.md",  // the source's own brief: required depictions live there
  "owns": ["lengths"],                           // lengths | colors | paint (paint has no chrome field: informational)
  "groups": { "catalogue": "geometry-28" },      // or an inline array, below
  "areas": ["a b c d", "e f g h"],               // CSS grid-template-areas, one string per row; "." is empty
  "mins": { "a": [400, 300] },                   // a layout source's measured minimums per group
  "canvas": { "width": 1280, "height": 960 },
  "chrome": {
    "margin": 36, "gutter": 12,                  // around and between tiles
    "pad": 20, "radius": 28,                     // inside a tile, its corner
    "titleGap": 4, "specimenGap": 20, "captionGap": 6, "header": 0,
    "title": 14, "caption": 12, "font": "system-ui, sans-serif",
    "texture": "grid", "grid": 8, "gridMajor": 4,   // grid paper on every tile, ruled from the content edge; "none" to turn it off
    "gridStrength": [14, 32], "gridStrengthDark": [8, 20],  // minor and major lines, % of the line colour, light and dark
    "darkThemes": ["dark", "dim"],                 // mode-axis values that take the dark strength
    "colors": { "bg": "var(--colors-bg)", "tile": "var(--colors-bg-subtle)", "fg": "…", "muted": "…", "line": "…", "slot": "…" },
    "derived": "how these numbers were obtained",   // documentation only
    "colorsNote": "why the colours map as they do"  // documentation only
  },
  "axes": [ { "name": "material", "label": "material", "attr": "data-material", "values": ["flat", "glass"],
              "invariant": true, "target": "root",
              "aliases": { "matte": "flat" },            // retired value → current value; a remembered retired value maps over
              "captions": { "glass": "Glass: lit · clear · fill · colour" } } ],   // shown in the bar for the current value
  "tokens": { "css": ["{work}/colors/system.css"], "commands": ["node … --out {work}/colors"] },
  "acceptance": ["one line per criterion the browser check cannot prove"],
  "note": "free text about the source or layout"   // documentation only
}
```

An inline group is `{ "id", "label", "layout"?: "column", "min"?: [w, h], "specimens": [{ "id", "label", "depiction", "grow"?: true, "briefRow"?: "…" }] }`. Ids are unique across the sheet. `briefRow` names the specimen's row in its brief's required-depictions table when the two names differ. A layout source's `mins` may name only groups of the content source.

Paths may use the following placeholders:

| Placeholder | Means |
|---|---|
| `{skills}` | the installed skills folder |
| `{bento}` | this skill |
| `{spec}` | the spec's own folder |
| `{work}` | `--work` |
| `~` | the home folder |

### Merging

Sources apply in order:

| Field | Rule |
|---|---|
| groups and areas | From the content source: `--content <id>`, else the first source with groups. |
| canvas | Field by field, with later sources winning, whoever owns lengths: a local source can resize the sheet. |
| chrome lengths | Field by field, with later sources winning. If any source `owns: ["lengths"]`, only that source's apply. `texture`, `gridStrength`, `gridStrengthDark` and `darkThemes` are sheet choices that any later source may set; `grid` and `gridMajor` stay with the owner. |
| chrome colours | Field by field, with later sources winning. If any source `owns: ["colors"]`, only that source's apply. |
| axes | Merge by name, with a later source's definition winning. The mode axis (public id `theme`, `data-theme`: light, dark) is added when no source defines one, and a `grid` axis (`data-bento-grid`: on, off) when the texture is grid paper. |
| tokens and acceptance | Accumulate. |
| layout sources (no `groups`) | The last one's `areas` replace the content's; their `mins` (`{ group: [w, h] }`) only grow each group's minimum. |

### Axes

`attr` is an attribute to set, or `"class"`, which swaps one class out of `values` on the target.
- `target` is `root` (`<html>`, the default) or `canvas`.
- `invariant: true` (the default) means a box may not move or resize when only this axis changes. Mode, material, anatomy and grid are invariant. Density and size are not.
- `aliases` map retired values to current ones; `captions` name the current value in the bar.

## Packing

`pack()` reads the areas, or makes them: about √(n·W/H) columns, filled in order. It then sizes the tracks:

1. Each track starts at 0. Each group's `min` grows the tracks it spans, narrowest first (water-filling), until the spans meet every minimum. If that overshoots the canvas, the exact greedy for interval covering runs instead (spans by right end, each deficit on its rightmost track), so a `NOFIT` means no arrangement of these tracks fits.
2. If the minimums exceed the canvas less its margins and gutters, it fails with `NOFIT` and the shortfall in px. It never scales.
3. The space left is water-filled, so the tracks stay as equal as the minimums allow.
4. Tracks are whole px and close exactly on the canvas: Σ tracks + (k − 1)·gutter + 2·margin = canvas.

`uiBentoCheck().needs` reports `{ group: [w, h] }` for every overflowing tile. Pass it back with `--mins`. A group's minimums only ever grow.

## Page contract

`scaffold.mjs` writes the page below. A hand-built page that keeps these attributes can use `check.js` as it is.

| Element | Attribute |
|---|---|
| the canvas, fixed at `canvas` size | `[data-bento]` |
| a tile | `[data-group="id"]` with a heading `[data-label]` |
| a specimen | `[data-specimen="id"]` with a caption `[data-label]` and a `[data-slot]` |
| an unfilled slot | `[data-placeholder]` |
| a part whose box is compared across axes | `[data-part]`, or ui-materials' `[data-layer]`, `[data-relief]`, `[data-face]` |
| content deliberately off the left edge | `[data-inset]` |
| a labelled empty state | `[data-empty]` |
| the spec subset the checker reads | `<script type="application/json" id="bento-spec">` |

The page also follows the Artifact contract: a `<title>`, colour tokens in light and dark, an explicit body background, a 16px side gutter, and the canvas inside a horizontal scroller at phone width. The switches sit above the canvas, outside its budget. The page remembers them in `localStorage`, inside try/catch. Without `--standalone` the page has no doctype, because the Artifact tool wraps it.

## Checks

`uiBentoCheck(opts)` returns `{ ok, errors, warnings, needs, summary }`. Every layout check runs on the page as it stands and again under every axis combination, up to `maxCombos` (256, with a warning above it). A combination reports only what it adds. `scripts/check-fixtures.mjs` proves each error below on a broken fixture and the pass on a clean one.

| Check | Level |
|---|---|
| Canvas size equals the spec | error |
| A tile overflows, any visible box leaves the tile's content box (padding included), tiles overlap, the canvas scrolls | error |
| Any element drawn with `transform` scale, `scale` or `zoom` ≠ 1 | error |
| A group or specimen without label text; a spec id missing, doubled or outside its group; an id not in the spec | error |
| A box moves between two combinations that differ only along invariant axes | error |
| An empty state with no text | error |
| Unfilled slots | warning (an error with `{ final: true }`) |
| First-line content off the caption's left edge without `[data-inset]` | warning |
| Text cut by an ellipsis | warning |
| Painted boxes off whole pixels | warning |

The browser check does not prove the following. They are the sources' acceptance items, checked by eye and reported as such:
- depictions;
- numeric agreement;
- colour sources;
- legibility;
- semantics.
