# Drawing specimens

How to write the specimen fragments and their stylesheet so a sheet passes the check the first time. The lessons below come from building the full ARIA 24 sheet on ui-geometry, ui-colors and ui-materials. The Type and Space specimens of `geometry-28` follow the same rules.

## Files

- **Use a generator.** Put the fragments (24 for ARIA 24, 28 for Geometry 28) in one script, such as `gen.py`, that writes `<work>/specimens/<id>.html` and concatenates the stylesheet. Shared icons, part attributes and a dialog template then live in one place, and a change is one edit and one rerun. Inside Python f-strings, keep SVG paths in constants: an f-string expression cannot contain a backslash.
- **One stylesheet, assembled in order.**
  1. Any `@import` for Google Fonts. It must come first in its `<style>`.
  2. The material tokens.
  3. The specimen classes.

  `--style` inlines the whole file.
- **A local source for the sheet itself.** The canvas size and title go in a small source next to the work, for example `{ "id": "local", "canvas": { "height": 1600 } }`, listed last. Any later source may set the canvas, whoever owns lengths. Pass the areas with `--areas` and the measured sizes with `--mins`, because the areas come from the content source.

## Paint

How a part is painted belongs to ui-materials: its token contract, the light model, line and mono rendering, and the rule that an unlit mode has no direction (`ui-materials/SKILL.md`, `references/fills.md`). Write the material tokens from there. This sheet adds three constraints of its own:

- **No paint may change a box.** Draw lines as inset rings or shadows, never `border`, because the checker compares every box across modes and materials and fails on any move.
- **The tile is the ground, one step off the faces.** With ui-colors, put the tile on step 2 (`bg-subtle`) and the page on step 1 (`bg`), so a flat dialog or menu on a step-1 face separates from its tile by fill alone, with the grid off too. Which role paints a face is ui-materials' rule (`ui-materials/references/fills.md`).
- **Shade from an opaque colour when combining ui-colors with ui-materials.** ui-colors' `--colors-shadow` is already a 14% mix, so shadow alphas built on it come out about seven times too faint. Use `--colors-gray-12` in light modes and `#000` in dark.

## Overlays

- **The tile's grid paper is the backdrop.** Every tile is ruled as grid paper (`chrome.texture: "grid"`, the default), from its content edge: minor lines every `chrome.grid`, major lines every `gridMajor` cells. ui-geometry sets minor 2q and major 8q = h.
  - Overlays sit straight on the tile, so frosted and clear transmission have something to show.
  - No specimen draws its own backdrop, and triggers need no special background.
  - The ruling also shows the geometry: control heights, insets and gaps can be read against it.
- **Don't build per-specimen stages.** An earlier sheet put a coloured stripe under each overlay. It cost 12px a side, needed a ground plate under every trigger so Outline stayed legible, and still read as decoration. Set `texture: "none"` only when the system shown brings its own background.
- **Keep overlays in the page's stacking context.** An ancestor with `filter`, `opacity`, `mask` or `backdrop-filter` becomes the backdrop root, and the glass then blurs nothing. Wrap a specimen in plain layout boxes only.
- **Popup offset is d_c**, the same as the frame's padding. Draw it as a 3px spacer between the trigger and the list.

## Fitting

- **Measure, don't guess.**
  1. Pack with no minimums.
  2. Render, then run `uiBentoCheck()` after `await document.fonts.ready`. Text measured before the web font loads is the wrong width.
  3. Save `needs` and repack with `--mins`.
  4. Repeat until nothing overflows.

  A specimen tile is as wide as its widest line of specimens, plus 2 × pad.
- **Make a wide group shallower.** When a tile is too tall, first try to fit its specimens on one line by narrowing whatever has slack: three textboxes at 120px instead of 132, an accordion at 150. One line of specimens costs one caption and no gap.
- **Annotations cost no height on a caption.** Put the construction annotation on the specimen's caption with `[data-specimen="dialog"] .b-caption::after { content: " · …" }` rather than on a line of its own.
- **Uneven tracks are fine.** Tight minimums can make the exact packer return 0px tracks, for example `0/0/575/191/141/241`. Tiles still close on the canvas, because every group spans two or more tracks.
- **ARIA 24 at full size needs about 1,161px of height** (n 14, standard preset, tile depth 5q, dialogs at 80q). 1280 × 960 cannot hold it, so add the layout source `aria-24-1280` (canvas 1280 × 1280, the tested areas and minimums) or measure your own. Say in the report that the canvas was raised. Never scale.
- **Geometry 28 needs 1,509px.** The Type and Space groups take a fifth row, 336px tall, under the four ARIA 24 rows, so the layout source `geometry-28-1280` sets the canvas to 1280 × 1600. Make room for a new group by raising the canvas. Never take it from the specimens already there.
- **Type is drawn at true size.** Each role sits in a line box of its own line height, at its own size, with no `transform` and no shared scale factor. The checker fails a scaled role. The Type tile's width follows the typeface, so measure again when the face changes.

## Checking

- **Clipping is judged against the tile's content box.** Content that runs into a tile's padding is an error, even though `overflow: hidden` keeps it from scrolling. The checker measures every descendant. `scrollHeight` alone misses this.
- **A negative control proves it bites.** Squeeze one row in place (`canvas.style.gridTemplateRows = …`) and the check must fail. Then restore it.
- **Switch axes through the page's selects.** Set the select's value and dispatch `change`, so the root attribute, the select and the remembered state agree. Screenshot at least two modes and three materials, including Outline (mono) in dark, where the grid is strongest, and Glass or Frosted.
- **Expect one warning.** Boxes off whole pixels follow text widths (a button sized to its label). They are reported, not errors.
- **By eye, after the check passes:**
  - legibility of text over glass and over the grid;
  - triggers and frames in Outline, where faces are transparent and the grid shows through;
  - meaning without colour in mono;
  - the annotation matching the drawn lengths.

## Viewing and publishing

- The browser pane can't open `file://`. Serve the work folder with a temporary `python3 -m http.server` entry in `.claude/launch.json`, then restore the file.
- Build with `--standalone` to view locally. Rebuild without it for the Artifact, which wraps the page itself.
- The Artifact tool publishes only from the working directory or this session's scratchpad. Copy the page there first if it was built elsewhere.
