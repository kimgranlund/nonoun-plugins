# Writing a source

A source says what one system brings to a bento. Keep the substance in the system's own brief, and put only the wiring here. That way the system can still make its showcase without this skill, and the two never disagree.

## A UI skill

1. Point `brief` at the skill's showcase brief (`{skills}/<skill>/references/showcase.md`).
2. Use a catalogue for its content when one exists (`aria-24`, `geometry-28`, `colour-24`). Add a new catalogue only for a new set of groups that other sources will reuse. Otherwise inline the groups.
3. Declare `owns` for what the skill is the authority on:
   - lengths for a geometry system;
   - colours for a palette;
   - paint for a material system.

   A source that owns lengths sets the chrome numbers from its own calculator and records how in `chrome.derived`.
4. Put the skill's generators in `tokens.commands` and their stylesheet output in `tokens.css`.
5. Add the axes the skill varies (mode, material, density). Mark an axis `invariant: false` only if it is meant to change lengths.
6. Copy into `acceptance` the brief's criteria that a browser check cannot prove, one line each.

The three shipped sources follow these steps:

| Source | Owns | Content | Tokens and axes |
|---|---|---|---|
| `ui-geometry` | lengths: canvas 1280 × 1600 and margin 36 for the brief's 1208 × 1528 usable area, gutter G = 12, pad d = 5q = 20, radius R = d + 2q = 28, gaps d/2 − I, d and I | Geometry 28 | — |
| `ui-colors` | colours: chrome mapped to `--colors-*`, page on `bg` and tiles on `bg-subtle` so step-1 faces separate | Colour 24 | `system.css`; the mode axis (id `theme`) swaps the `light`, `dark`, `dim` classes |
| `ui-materials` | paint (informational: no chrome field) | ARIA 24 | a material switch with each preset's four settings as its caption; an anatomy switch (off, layer, relief, face; `on` is a retired alias of relief) with a legend; overlay CSS. The system's own material tokens come with the specimens' stylesheet |

**Known disagreement with ui-materials.** Its brief (`ui-materials/references/showcase.md`) asks for coloured stripes under every overlay, and for the four settings (lighting, transmission, delineation, chroma) as separate switches. This bento puts overlays on the tile's grid paper instead (`authoring.md`, Overlays) and switches presets only. Each sheet's caption names its four settings. Until the two briefs agree, report a materials sheet made here as not meeting those two items.

**Modes on the axis.** The ui-colors source lists light, dark and dim: the modes ui-colors forces with one class. Its two contrast modes are not on the axis. ui-colors applies them under `prefers-contrast: more` and forces them with two classes (`.light.contrast-more`), which a `class` axis, swapping one class, cannot set. Whether to add them is an open decision, recorded in the source's `note`.

**Catalogues.** `aria-24` is the 24 ARIA patterns in eight groups. `geometry-28` is the same eight groups, group for group, plus the Type group (the type roles at true size) and the Space group (the gap ladder and the container padding ladder) that ui-geometry's brief adds: 28 specimens in ten groups. The `ui-geometry` source uses `geometry-28`, so a sheet whose content it gives, the combined geometry, colour and materials sheet among them, shows typography and the use of space. `ui-materials` and the framework template keep `aria-24`. A test holds the first eight groups of the two catalogues equal.

ui-geometry also rules the tile grid paper at minor 2q and major 8q = h. At other n, density or card depth, re-derive the geometry chrome with `derive.mjs --containers` and write a local source that overrides it.

## A layout

A layout source has no groups: `canvas`, `areas` and `mins`, measured from a sheet that passed. List it after the content. Two are shipped:

| Layout | Content | Canvas | Rows need |
|---|---|---|---|
| `layouts/aria-24-1280.json` | `aria-24` | 1280 × 1280 | about 1,161px |
| `layouts/geometry-28-1280.json` | `geometry-28` | 1280 × 1600 | 1,509px: the four ARIA 24 rows and a fifth for Type and Space |

The second keeps the first's eight minimums and adds two. Type (463 × 336) and Space (676 × 329) were measured with the in-page checker in headless Chromium, each group alone in a tile with the geometry chrome, in the system UI face. A full sheet with all 28 specimens drawn has not been measured as a whole. The room for the two groups comes from the canvas height, never from scaling or dropping a specimen. A layout's minimums hold for specimens of the same size. Different specimens, or another typeface for the Type group, need their own measurement.

For a colours-only sheet, ui-colors' own generator (`"showcase": true`) remains the reference implementation. Its sheet reads `system.json` directly. Use the bento source when colour is combined with other systems, or when you want the bento checks and switches.

## A framework (shadcn, MUI, Radix Themes, Base UI, Bootstrap …)

Start from `sources/templates/framework.json`.

- **Content.** Use `aria-24`. Each specimen is the framework's own component in its documented markup and classes, with each state the brief asks for. Where the framework has no such component, show a labelled empty state that names the closest component. Never build a stand-in.
- **Tokens.**
  - Copy the framework's built stylesheet into `tokens.css`: its colour variables and the component CSS from the docs build.
  - Read the chrome lengths from the framework's own tokens: card padding, card radius and grid gap. Name the token beside each number in `chrome.derived`.
- **Axes.** Use the framework's own light/dark switch as the mode axis (id `theme`), such as the `class` `dark` or `[data-theme]`. Add `density` or `size` as non-invariant axes if the framework has them.
- **Measuring.** To learn the framework's numbers from a running site, `ui-geometry/scripts/collect.js` collects the lengths and `fit.mjs` names the system. Use its fitted preset to explain the sheet, not to restyle it.

## A brand

Start from `sources/templates/brand.json`.

- **Content.** Group what the brand is made of: identity (logo, palette, type), voice (headline, microcopy, a before and after rewrite), and, where the brand has them, imagery, iconography and layout. Use real copy from the brand's site or guidelines, or copy written in its documented voice. Never invent metrics or testimonials.
- **Tokens.** The brand's own colours, faces and radii as CSS variables in `brand.css`. Load fonts from Google Fonts or inline them. Never imitate a typeface the brand doesn't own.
- **Combining.** A brand source with ui-geometry gives the brand's colours on the geometry system's lengths, with geometry owning lengths and the brand owning colours. With ui-colors anchored to the brand's colours, ui-colors owns colours instead.
- **Publishing.** A page that carries a real organisation's name or branding is the user's to share. Build it as a file and let them decide whether it gets a URL.

## Combining

```
node scripts/scaffold.mjs ui-geometry ui-colors ui-materials --work W --specimens W/specimens --style W/specimens.css --out W/showcase.html
```

ui-geometry's Geometry 28 content (ARIA 24, Type and Space) and lengths, ui-colors' colours and mode switch, and ui-materials' material switch and anatomy overlay. The checker then proves every box stays put across all modes and materials.
