# Layout jig

A layout jig tunes how pages hold their content: breakpoints, containers and density, tested under content stress. Read [change-set.md](change-set.md) for the export and [patterns.md](patterns.md) for the interactions.

## What it tunes

| Family | Examples of a constant |
|---|---|
| Breakpoints | The widths at which the layout changes |
| Containers | Page width, reading measure, column count, sidebar width |
| Spacing between regions | Page margin, the gap between columns, the gap between sections |
| Density | How far one density step moves container spacing |

It does not tune the inside of a control (a component jig) or the scales those spacings come from (a system jig). When a layout value is derived from a system constant, it is a derived value here: show its formula and offer an override.

## Discover first

1. Find where breakpoints are written: media queries, container queries, a breakpoints map in a config or theme file, a script. List each with its `home`.
2. Find the container values: a max width on the page wrapper, a measure on text blocks, grid templates, sidebar widths.
3. Find the density setting when the host has one: the attribute, class or property that selects it, and the amounts each step changes.
4. Find the real page shells and layout components. These are the canvas.
5. Find the rules: a minimum and maximum line length, a smallest supported width, a no-sideways-scroll rule.
6. For each breakpoint, say whether the jig can move it live on the canvas. A breakpoint the jig cannot move live is drawn as a marker on the width control, is still a constant, and still exports as a change. Say in the panel which ones are markers only.

A layout value written straight into a page with no token behind it gets a control with `home: null` and a `hint` that says where the literal is written, in a group labelled as proposals.

## Context, constants and overrides

- Context: the canvas width, the density the canvas shows, the content setting (short, long, empty, many items), the direction, and which page is shown. These export under `context`.
- Constants: breakpoints, container widths, measures, region gaps and density step amounts. Each control carries `data-jig-constant="<path>"`.
- Overrides: a wish for one region at one width ("at 360 wide, the card margin 4 px less"). Export it under `overrides`, with the width in `at`.

The density a person views at is context. The amount a density step moves is a constant. Keep the two apart in the panel.

## Canvas

- Draw a real page shell from the host, inside a frame whose width the jig controls. A width slider with the breakpoints marked on it is the main control.
- Size the frame, not the browser window, so the panel stays usable while the canvas is narrow. Where the host's layout responds to the viewport and not to a container, load the page in an inner frame of its own so its queries see the canvas width.
- Show the current width in pixels, and the name of the active breakpoint range.
- Offer an overlay that outlines containers and hatches margins and gaps, so a person sees what a spacing value owns.
- Mark the canvas root with `data-jig-canvas`.

## Checks to offer

- Contract: the host's own layout rules, when it states any.
- Proposed, in a separate group:
  - no sideways scroll at the smallest supported width;
  - the reading measure stays inside the line length the host or the team names;
  - breakpoints rise in order, and no two are closer than a stated minimum;
  - a container is never wider than its parent;
  - content is not clipped at the long content setting.
- Run the checks at every breakpoint range, not only at the width shown. A failure names the width.

## Edges to stress

- One pixel below and one pixel above each breakpoint.
- The smallest supported width, and a very wide one.
- Long words and long labels with no place to break. Empty regions. Many items.
- Each density setting at the narrowest width.
- Right to left.
- Page zoom or a larger base text size, when the host supports it.

## Done when

- Every control maps to a layout value found in the source, or sits in the proposals group with `home: null`.
- Dragging the width control reflows the real page shell, and the panel names the active range.
- Each breakpoint is either live or marked as a marker only.
- Content stress is one control away, and the proposed checks run across every range.
- The panel root carries `data-jig="layout"`, and `node scripts/check-jig.mjs <page>` exits 0 with no `skip` line. At least one constant is a number field, so the `edit` check runs.
- The exported change set passes `node scripts/validate-changeset.mjs <file.json>`, and its `context` records the width and the content setting.
