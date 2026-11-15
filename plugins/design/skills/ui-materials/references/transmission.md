# Transmission: `frosted` and `clear`

Transmission is what an overlay body, or a pane over a display, does with what's behind it.

| Value | Overlay body (overlay · ground · neutral) | Cover pane (recessed · display, only when lit) |
|---|---|---|
| `opaque` | hides the backdrop | none |
| `frosted` | translucent face over a light blur (8px): the backdrop keeps its colour and soft shapes | its lit lower inner edge, and reflections over the display |
| `clear` | translucent face over a 3px blur: the backdrop keeps its shapes. The lens is added where it runs. | as frosted, with the clear rim below |

It never touches ground parts, raised parts, solid faces or emissive faces. A button never turns translucent. A tooltip with
a solid face stays solid. Transmission writes only the tokens in [terms.json](terms.json) › `transmissionReach`.

## Glass bodies

A glass face is the raised face's colour at an alpha, as paint roles that ui-colors generates ([paint.json](paint.json):
62% over 46% frosted, 66% over 54% clear). Nothing mixes a colour in the browser. These are starting values: one consuming
system needed 0.90 over 0.84 frosted and 0.92 over 0.86 clear in the light scheme, and 0.80 over 0.72 clear in the dark one.

```css
/* frosted */
--overlay-face: linear-gradient(180deg, var(--colors-paint-glass-frosted-top), var(--colors-paint-glass-frosted-bottom));
--overlay-backdrop: blur(8px) saturate(1.2) brightness(var(--glass-k));
/* clear */
--overlay-face: linear-gradient(180deg, var(--colors-paint-glass-clear-top), var(--colors-paint-glass-clear-bottom));
--overlay-backdrop: blur(3px) saturate(1.6) brightness(var(--glass-k));

.menu { background: var(--overlay-face); box-shadow: var(--overlay-shadow);
        backdrop-filter: var(--overlay-backdrop); -webkit-backdrop-filter: var(--overlay-backdrop); }
```

- **Clear needs more tint than frosted**, because a sharp backdrop competes with text more than a blurred one does.
- **`--glass-k`** brightens the backdrop in the light scheme (≈ 1.4, where text is dark) and darkens it in the dark scheme (≈ 0.6; lower crushes to black whatever the blur left).
  `brightness()` multiplies every sRGB channel, so it has a ceiling in the light scheme: 1 ÷ the largest channel of the
  palest colour the glass sits over (the base ground, as a rule). Above that the pale backdrop clips to white and fine lines
  in it disappear: a ground of `#f8f6f4` caps it at 255 ÷ 248 ≈ 1.03. Choose the smaller of 1.4 and the ceiling, and hold
  legibility over dark or busy content with the tint and the blur, which work at any brightness. If holding the ceiling
  means thickening the frosted face until it fails the reads-as-glass gate (next bullet), a system may go above it, up to
  1.4, and beyond 1.4 only with its legibility pass as the check, and accept that the palest backdrops clip under glass.
- **Frosted still reads as glass.** Over the showcase's finest backdrop, the frosted body must show the pattern softened,
  not a flat fill. Keep the blur under the pitch of the finest backdrop feature the glass should show, and brightness close
  to the values above. Then solve the text again (below): this gate and legibility pull in opposite directions, and
  legibility wins. One system, measured against its legibility pass: an 8px blur kept its 60%/46% faces passing, and a
  thinner 40%/26% face failed 50 of 808 text runs.
- **The rim, when lit.** `frosted`:
  `inset 0 1px 0 var(--colors-paint-rim-frosted-top), inset 0 0 0 .5px var(--colors-paint-rim-frosted-ring), inset 0 -1px 0 var(--colors-paint-rim-frosted-bottom), 0 0 0 .5px var(--colors-paint-rim-frosted-outer)`
  plus the popup-level cast. Clear:
  `inset 0 0 0 1px var(--colors-paint-rim-clear-ring), inset 0 1px 0 var(--colors-paint-rim-clear-top), inset 0 0 20px var(--colors-paint-rim-clear-glow), 0 0 0 .5px var(--colors-paint-rim-clear-outer)`
  plus the cast.
- **Unlit transmission** (for example Flat + frosted) keeps the face and the backdrop filter, with no rim and no cast. The
  body separates by its tint and the blur. Add a scrim (ui-colors `bg-backdrop`) for modals.
- **With `line`**, the body keeps a translucent face and its backdrop filter, and takes the strong line instead of the rim.
  The face is then the base ground's colour at the same alphas: the `-line` glass roles
  (`--colors-paint-glass-frosted-top-line`, `--colors-paint-glass-frosted-bottom-line`, `--colors-paint-glass-clear-top-line`,
  `--colors-paint-glass-clear-bottom-line`).

## Cover panes (displays only, when lit)

A cover pane sits over a **display** (a screen, a readout), never over a neutral recess. A field, well, track or tray is cut
into its ground; giving it a pane's lit top edge, ring and sheen made every well read as a raised glass panel, foreground
on foreground, so a neutral recess keeps the shadow lighting wrote in every transmission. (Corrected 2026-11-13, from a
consuming project's review: fields, segmented trays and spinbuttons all read as panels under `frosted`.)

Glass over a display changes what the face is made of, never its relief. Highlights are plain white at a fixed alpha, *not*
scaled for the dark scheme (`fixed` in [paint.json](paint.json)), because a pane catches the room's light in either scheme.
Transmission appends the pane's lower inner edge to the display's shadow; the pane's reflections stay in `--display-cover`.
A lit top, ring or sheen on the pane reads as a raised panel.

```css
--display-shadow:  /* the lit recess shadow */, inset 0 -1px 0 var(--colors-paint-cover-bottom);
--display-cover:   linear-gradient(165deg, var(--colors-paint-cover-reflection-1) 0 30%, var(--colors-paint-cover-reflection-2) 30% 46%, transparent 46%);
```

Without lighting there is no cover pane: a pane is seen only through its reflections.

## The lens: refraction added to `clear`

- **The map.** A pixel p shows the backdrop at c + (p − c)·(1 − k·b(p)), with b = |x|⁴ + |y|⁴ over the layer
  (x, y ∈ [−1, 1]) and k = 0.6: the centre barely moves and a band along the rim pulls in and magnifies. The fourth power
  makes that band about a third of the way in from each edge; a higher power confines the bend to a thin line the rim
  highlight covers. Encode it as a small PNG: red = x offset, green = y offset (128 = none), blue = the rim weight
  w = smoothstep(0.55, 0.9, b), 0 in the centre and 255 in the outer few pixels, where the bend is strongest. A wider sharp
  band puts the text inset from the edge over sharp, high-contrast backdrop and fails the legibility check below. Displace R, G and B by ×1, ×1.05 and ×1.1 and
  recombine them with `screen`, so the rim fringes.
- **Set the bend in pixels; express it in the layer's box.** Use `primitiveUnits="objectBoundingBox"` with the filter region
  and the `feImage` at `x="0" y="0" width="1" height="1"`: the whole box of the element the filter is on. A pixel then
  moves by `scale` × d × the box's size along that axis, where d is the map's offset: k/2 = 0.3 at the middle of each edge,
  up to 0.6 in the corners. Choose the shift at the middle of the rim in pixels (12–16px, so the bend reads through the tint
  and the rim highlight) and set `scale` = shift ÷ (0.3 × the box's width): for 14px, about 0.13 on a 360px card and 0.22
  on a 208px menu. The vertical shift follows the height, so a wide, short layer (a toast) bends little at its top and
  bottom. Two forms fail in WebKit (checked in WebKit 27 against Chromium 156): `userSpaceOnUse` filters on an HTML element
  draw nothing, and a filter region that covers only part of the element misplaces the displacement.
- **A shared backdrop lens is in pixels.** Where one filter serves every layer through `backdrop-filter` (Chromium is the
  only engine that applies an SVG filter there), use `primitiveUnits="userSpaceOnUse"` and scale = shift ÷ 0.3 in pixels,
  so every pane bends by the same shift. The box form above is for `filter` on an element the layer's size, the route
  WebKit can draw.
- **The filtered element is the layer's box.** Where the lens is an ordinary `filter` over a copy of the backdrop, put the
  filter on an element exactly the layer's size with `overflow: hidden` (not `overflow: clip`, which WebKit then measures
  by the copy's overflow), and position the copy inside it. Give that element no border radius; clip the radius on a
  wrapper around it, so nothing the filter draws leaves the layer.
- **Blur the centre, not the rim.** With the lens, clear's 3px blur moves inside the filter and applies only where the rim
  weight is 0: blur the displaced backdrop, keep it `out` of the rim weight, keep the sharp displaced backdrop `in` it, and
  merge the two. Text sits in the centre, so it keeps the blur it needs, and the band keeps the bent lines that show the
  lens. `stdDeviation` is in box units too: 3px ÷ the width and 3px ÷ the height.
- **The map must be readable by the filter.** Chromium won't let `feImage` use a cross-origin image, and sandboxed frames
  make every fetched file cross-origin. Embed it as a data URL, or draw it at runtime into a canvas and use `toDataURL()`.
- **Detection is necessary, not sufficient.** Only Chromium applies an SVG filter in `backdrop-filter`; Safari parses it and
  draws nothing, so `@supports` can't tell. Read the engine (`navigator.userAgentData?.brands` includes Chromium, or the UA
  has `Chrome/` and not `CriOS`), check `prefers-reduced-transparency`, and set `data-lens="on"`. A frame can still pass that
  check and draw nothing, so confirm the lens by rendering. Where it must show (a diagram, an explainer), draw the pane
  yourself: a canvas that paints the backdrop with the lens computed per pixel works in every engine.
- **One glass with a lens option.** A system may ship one glass material on `frosted` and offer the lens on it, instead of
  the two presets. Where the lens runs, its blur moves inside the filter (Blur the centre, not the rim); where it does
  not, the body stays frosted. The lensed body keeps frosted's face, tint and alphas, so the two read as one material;
  solve the text over both. With the two presets, `clear` never falls back to `frosted`.
- **A lens that must show is a canvas pane.** An SVG filter on an HTML element is the weakest link: across engines it
  has drawn nothing, drawn outside the layer, or applied the blur without the bend, and a local engine passing is not
  evidence the viewer will. Where the backdrop is known (a showcase, a diagram, an explainer), draw it in script, then
  paint the pane per pixel with the map above: the bend, the R/G/B split, and the blur on the centre only. Draw the
  backdrop from the same data the page's own markup uses, so the two can't drift. Keep `backdrop-filter` with the SVG
  map for real product UI, where the backdrop is unknown and Chromium is the only engine that applies it.
- **Show it in a showcase.** Print "LENS ON" or "LENS OFF" near the glass, so a reviewer knows which one they are looking at.

## Traps

- **The backdrop root.** An ancestor with `filter`, `opacity < 1`, `mask`, `mix-blend-mode` or `backdrop-filter` starts a new
  backdrop root, so a glass body inside it blurs only that ancestor. Keep overlays in the top layer (`popover`, `<dialog>`) or a
  portal at the body, and never nest glass in glass. A filter on a *sibling* (such as greyscale media) is fine.
- **Transmission needs a backdrop.** Over a plain ground, glass looks like a grey card. Showcases put scrolling, colourful,
  high-contrast content under every overlay, with large shapes (frost turns them into a glow) and fine lines (clear glass
  keeps them, and the lens bends them).
- **Legibility.** Check text against the *worst* backdrop (black and white stripes, a saturated image) at the lowest face
  opacity. If it fails, raise the tint or the blur. Don't thin the text. Over clear glass, also measure backdrop text
  through the body: it should fall under about an eighth of the body text's contrast (Lc 8 against Lc 58 in one consuming
  system).
- **The containing block.** A backdrop filter also makes the body the containing block of its fixed and absolute
  descendants. Hidden native inputs move with it, so a box diff across materials counts them apart; a popup opened from
  inside a glass body opens in the top layer. Don't move the filter to a pseudo-element of a scrolling body: its blur
  scrolls away.
- A cover pane prepended before the recess shadow reads raised (2026-11-13).
- **Cost.** Each backdrop filter re-samples every frame it moves. Keep three or fewer transmissive overlays on screen at once,
  don't animate their size, and avoid full-screen blurs on mobile.
- **Scrolling content stays opaque.** Lists, fields and cards that scroll are base-layer parts. Only the bars and sheets
  they scroll under are overlays.

## Fallbacks

```css
@media (prefers-reduced-transparency: reduce) { :root { /* use the opaque transmission table */ } }
@media (forced-colors: active) { .menu { backdrop-filter: none; background: Canvas; outline: 1px solid CanvasText; } }
@supports not (backdrop-filter: blur(1px)) { :root { /* opaque face, keep the rim and cast */ } }
```

- **Say when the lens falls back.** Wherever the lens is offered (a material switch, a showcase, a jig), disable it with
  a note when detection says the engine can't draw it, or label the frosted fallback where it renders. A silent fallback
  looks broken.

## Solve the text again when a face moves

Text over a glass body is solved against the worst backdrop for one face colour and one pair of alphas. Change either (a
lighter dark overlay face, a new tint) and solve it again: a dark face one neutral step lighter dropped muted text over a
white backdrop from its target to Lc 41.6, and raising the frosted alphas from 0.62 and 0.46 to 0.74 and 0.66 restored it
(measured in one consuming system's render, 993 texts, 2026-11-13).
