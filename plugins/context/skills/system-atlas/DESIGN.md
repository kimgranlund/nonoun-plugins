# DESIGN: the visual contract of an atlas page

Thirteen rulings. All binding. `assets/page-template.html` already satisfies them, so the cheapest
way to stay inside the contract is to copy the template and change nothing structural.
`scripts/atlas_check.py` enforces the mechanical half of this file.

| # | Ruling |
|---|---|
| D1 | Full-width pages, large diagram canvas. No max-width on sections. The canvas inner element has `min-width:1100px` inside its own `overflow-x:auto`. |
| D2 | Type is `system-ui` sans and `ui-monospace` mono only. No web fonts, ever. |
| D3 | Neutral charcoal surfaces. |
| D4 | Every color is OKLCH. The accent hue is 235, held once in `--hue: 235`. The accent, the diagram tier and the tinted neutrals all read `var(--hue)`, so one edit re-hues the page. |
| D5 | Every color in the stylesheet is a token. No literals, `transparent` included, which is `--none`. |
| D6 | Every color token is `light-dark(<light>, <dark>)`. No per-theme token redefinition blocks. |
| D7 | Light and dark switch only through `color-scheme`. `:root{color-scheme:light dark}`; the host's `data-theme` and the in-page Auto/Light/Dark toggle set `color-scheme:light` or `dark`, never token values. The toggle's choice is kept in localStorage inside try/catch. |
| D8 | Radius tokens: `--r-control: clamp(0.75rem, 1.25rem, 1.75rem)` for controls, `--r-container: clamp(0.75rem, 1.4vw, 2.75rem)` for surfaces. Every `border-radius` reads one of the two. No joined button strips, since a middle button would need square corners. |
| D9 | Corners use `corner-shape: superellipse(1.8)` through `--corner` wherever a radius is set. The CSS function is `superellipse()`, no hyphen. Round corners are the fallback where the property is unsupported. |
| D10 | Two token tiers. Page: `--ground --sheet --ink --muted --rule --accent --accent-soft`, plus state `--green --amber --red`. Diagram: the `--dg-*` set. Decisions are the only accent-colored shape; notes are the only warm hue. |
| D11 | Mermaid is themed by overriding its SVG classes onto the `--dg-*` tier with `!important`, scoped `:is(pre.mermaid,.vstage) svg`. Mermaid's own theme variables cannot take `oklch()` or `light-dark()`, which is why the class map exists. See `references/mermaid-class-map.md`. |
| D12 | Fonts are tokens: `--font-sans`, `--font-mono`, `--dg-font`. Mermaid gets its font by CSS only, `font-family: var(--dg-font) !important` on the SVG's text and label elements. Never put an `%%{init}%%` directive in a diagram. Because the font arrives after layout, `--dg-font` must stay metrically close to mermaid's default (system-ui is), and font size is not changed at all. |
| D13 | Tables carry outputs 1, 4 and 5. `.tablewrap{overflow-x:auto}` wraps every `<table>`; cells are token-only, separated by a `1px solid var(--rule)` bottom border, never by a fill; `<th>` is `var(--font-mono)`, uppercase, `var(--muted)`. No border-radius on a table, so no corner-shape is owed. The three header rows are fixed in `assets/table-section.html`. |

## Viewer rulings

| # | Ruling |
|---|---|
| V1 | Clicking an embedded diagram, or its "Open viewer" button, opens a full-viewport `<dialog>`. |
| V2 | Pan by drag; zoom by wheel or pinch at the cursor; double-click zooms in. Buttons are minus, plus, Fit all, Fit width, 100%, Close, with a live zoom readout. Keys are `+ - 0 1 w`, the arrows to pan, Esc to close. |
| V3 | The viewer MOVES the live SVG into the dialog and restores it on close. Never clone: mermaid scopes its styles by the SVG's id, so a clone renders black boxes and clipped labels. |
| V4 | Fit measures the rendered size after placement, never the viewBox alone, which overflows the right edge. |

`assets/viewer.js` implements all four. The template inlines the same code, because an artifact
cannot load a local script. Keep the two copies identical.

## The token block, verbatim

```css
:root{
  color-scheme:light dark;
  --hue:235;
  --ground:light-dark(oklch(96% 0.003 var(--hue)),oklch(21% 0.004 var(--hue)));
  --sheet:light-dark(oklch(99.5% 0.001 var(--hue)),oklch(25.5% 0.005 var(--hue)));
  --ink:light-dark(oklch(23% 0.005 var(--hue)),oklch(93% 0.004 var(--hue)));
  --muted:light-dark(oklch(48% 0.008 var(--hue)),oklch(71% 0.008 var(--hue)));
  --rule:light-dark(oklch(86% 0.004 var(--hue)),oklch(36% 0.006 var(--hue)));
  --accent:light-dark(oklch(50% 0.13 var(--hue)),oklch(78% 0.11 var(--hue)));
  --accent-soft:light-dark(oklch(92% 0.035 var(--hue)),oklch(33% 0.045 var(--hue)));
  --green:light-dark(oklch(52% 0.13 155),oklch(78% 0.14 155));
  --amber:light-dark(oklch(58% 0.13 75),oklch(80% 0.13 80));
  --red:light-dark(oklch(52% 0.17 28),oklch(74% 0.14 28));
  /* diagram tier: every mermaid paint reads one of these */
  --dg-node-fill:light-dark(oklch(97% 0.012 var(--hue)),oklch(31% 0.02 var(--hue)));
  --dg-node-stroke:light-dark(oklch(62% 0.06 var(--hue)),oklch(58% 0.06 var(--hue)));
  --dg-node-text:light-dark(oklch(23% 0.005 var(--hue)),oklch(94% 0.004 var(--hue)));
  --dg-decision-fill:light-dark(oklch(93% 0.04 var(--hue)),oklch(36% 0.055 var(--hue)));
  --dg-decision-stroke:light-dark(oklch(50% 0.13 var(--hue)),oklch(78% 0.11 var(--hue)));
  --dg-group-fill:light-dark(oklch(94.5% 0.004 var(--hue)),oklch(22.5% 0.005 var(--hue)));
  --dg-group-stroke:light-dark(oklch(80% 0.006 var(--hue)),oklch(40% 0.008 var(--hue)));
  --dg-group-label:light-dark(oklch(42% 0.01 var(--hue)),oklch(76% 0.01 var(--hue)));
  --dg-edge:light-dark(oklch(45% 0.01 var(--hue)),oklch(72% 0.01 var(--hue)));
  --dg-edge-label-fill:light-dark(oklch(99.5% 0.001 var(--hue)),oklch(25.5% 0.005 var(--hue)));
  --dg-edge-label-text:light-dark(oklch(35% 0.01 var(--hue)),oklch(84% 0.008 var(--hue)));
  --dg-note-fill:light-dark(oklch(95% 0.035 85),oklch(34% 0.035 85));
  --dg-note-stroke:light-dark(oklch(70% 0.09 85),oklch(62% 0.08 85));
  --dg-note-text:light-dark(oklch(28% 0.02 85),oklch(93% 0.02 85));
  --font-sans:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
  --font-mono:ui-monospace,"SF Mono",Menlo,Consolas,monospace;
  --dg-font:var(--font-sans);
  --r-control:clamp(0.75rem,1.25rem,1.75rem);
  --r-container:clamp(0.75rem,1.4vw,2.75rem);
  --corner:superellipse(1.8);
  --none:light-dark(oklch(100% 0 0 / 0),oklch(0% 0 0 / 0));
}
```

## Theme switching, the whole pattern

```css
:root[data-theme="light"]{color-scheme:light}
:root[data-theme="dark"]{color-scheme:dark}
:root[data-scheme="light"]{color-scheme:light}
:root[data-scheme="dark"]{color-scheme:dark}
```

`data-theme` is what the artifact host sets. `data-scheme` is what the in-page toggle sets, and
the toggle writes the choice to `localStorage` inside try/catch so a private window cannot throw
the page down. No token is redefined in either case: `light-dark()` reads the computed
`color-scheme` and nothing else has to change.

## Never

- Never a literal color anywhere in the stylesheet, `transparent` included. Use `var(--none)`.
- Never a per-theme token block. One definition per token, `light-dark()` inside it.
- Never a `@media (prefers-color-scheme: ...)` rule. `color-scheme` already does that job, and a
  media query would fight the toggle.
- Never a web font: no `<link>` to a font, no `@import`, no `@font-face`.
- Never an `%%{init}%%` directive in any diagram. The artifact host's native mermaid renderer
  then fails to detect the diagram and prints the source as text. This was observed on all nine
  diagrams of one page at once.
- Never a `border-radius` that is not `var(--r-control)` or `var(--r-container)`.
- Never a joined button strip. Gap the buttons; a shared border makes a middle button square.
- Never clone the SVG for the viewer. Mermaid scopes its styles by the SVG's id, so a clone
  renders black boxes and clipped labels. Move the live node and put it back on close.
- Never tell machinery kinds apart by color. Color carries state and accent only; kinds are
  shape plus a mono prefix.

## Standalone rendering

The assembler embeds the pinned Mermaid UMD bundle from `assets/vendor/manifest.json`;
its version, SHA-256, upstream archive and license are retained alongside it. No network
request or host-provided renderer is required. The template initializes Mermaid explicitly
and exposes `data-atlas-render="complete"` only when every source block contains SVG.
Rendering failures show an error instead of silently presenting raw source as a diagram.
The checker rejects absent or modified renderer bytes. Browser verification remains required.
