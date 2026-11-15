# Lighting: `lit`

`lit` adds one light to the fills. Every fill keeps its base value, and the light only shades it, so a part's colour reads the
same lit and unlit. `none` leaves the fills alone and sets every shadow to `none`; the one cast it keeps is that of an opaque overlay whose
fill equals what it floats over (fills.md › Separating reliefs without edges).

## The light model

- **One light**, from above (ℓ = (0, −1)), leaning left by default, so every cast shifts right by a quarter of its drop. A
  light straight above is the one alternative: then nothing shifts. Highlights fall on top edges, shadows below.
- **Two colours**: shade (a near-black tinted toward the neutral) and lit (white). All shading is one of them at an alpha.
- **Paint roles** carry them. Every shade and lit colour a table uses is a paint role, `--colors-paint-<use>`: a literal
  colour that ui-colors generates from [paint.json](paint.json) through its `translucent` request key
  (`node scripts/request.mjs` prints the request). No table derives a colour in the browser.
- **Scheme multipliers** scale the alphas, because a dark scheme needs stronger shade and much weaker lit. They are applied
  when the colour system is generated ([paint.json](paint.json) › `bases`):

  | base | light scheme | dark scheme |
  |---|---|---|
  | shade | the near-black of the neutral, at the role's alpha | black, at 3 × the alpha, capped at 1 |
  | lit | white, at the role's alpha | white, at 0.25 × the alpha |

  A role may set its own dark alpha. A cover pane's highlights are not scaled (`fixed`). Casts are not scaled either:
  ui-geometry's alpha budget is already larger in the dark scheme.
- **One scheme constant** remains: `--glass-k`, the brightness a transmissive body applies to its backdrop (≈ 1.4 in the
  light scheme, at most 1 ÷ the base ground's largest sRGB channel; ≈ 0.6 in the dark one; transmission.md). `--shade`, `--shade-k` and `--lit-k` are retired: they stay declared
  for one version, and no table reads them.

  The values marked ≈, and the alphas in paint.json, are starting values tuned by eye for each palette. No check holds
  them: the render checks in SKILL.md judge the result.

## The paint passes, in order

1. **Base**: the fill (fills.md).
2. **Face shading**: a gradient toward the light, layered over the fill. It lightens the top, holds the base through the
   middle and falls off at the bottom:
   `linear-gradient(var(--colors-paint-face-top), transparent, transparent, var(--colors-paint-face-bottom)), var(--element)`.
   Solid faces take `--colors-paint-face-top-solid` and `--colors-paint-face-bottom-solid`. Round parts (a knob, a round
   thumb) use a radial highlight above centre and a 2–3% darker ring **instead of a border**. This applies to neutral and
   solid faces. The shading follows the part's outline, not its job: a thumb or cap that is not round (a slide switch's
   cap, a fader cap) takes the linear shading of a key, because a radial rim on a rectangle draws a disc inside it, a
   raised part on a raised part. Display faces stay flat. The shading never moves a face off its fill: its lightest point
   is the fill itself, so a white face reads white and takes its shade only toward the lower edge. Where states are painted as an image over the
   fill, keep the shading a layer of its own and order it under the state image:
   `background: <state image>, <shading>, <fill>`. A lit face whose shading is part of its colour hides its own states.
3. **Bevel** (also called the compound edge), raised parts only, never a stroke colour: a lit 1px inset on top, a faint
   shade 1px inset at the bottom, and a half-pixel shade ring.
   `inset 0 1px 0 var(--colors-paint-bevel-top), inset 0 -1px 0 var(--colors-paint-bevel-bottom), 0 0 0 .5px var(--colors-paint-bevel-ring)`.
   Solid faces take the weaker `--colors-paint-bevel-top-solid` on top. A raised part at the popup level that holds parts
   (a card, a panel) takes the lit top alone and its cast: no lower shade and no ring. The half-pixel ring is the first cue
   to drop wherever it reads as a border.
4. **Cast**, raised parts and overlays: stacked drops. Their lengths come from **ui-geometry's elevation** (L cast layers in
   a geometric series, y = blur/2, a fixed alpha budget per level, alpha falling as blur grows). This pass sets only their
   direction and colour: layer k takes `--colors-paint-cast-<k>`, the shade colour at ui-geometry's alpha for that layer and
   scheme. Levels are ui-geometry's: `raised` for controls (`--raised-shadow-1`), `popup` for resting cards,
   popovers and a device standing as a part (`--raised-shadow-2`, `--overlay-shadow`), `floating` for floating bars and
   `modal` for dialogs.
5. **Texture**, optional: grain (SVG noise), brushing (a fine repeating gradient), a grip field of dimples, each at 7%
   opacity or less.
6. **Context**: the ground answers a part: a cavity (an inset shadow) around a key sitting in a hole, or a seam (a dark
   hairline with a lit one inside) where two parts meet.

## Recessed parts

A recess reverses the light: the shadow is **inside** and falls from the top, and the lit line is the **outer lower lip**,
where the ground catches the light.

```css
--recessed-shadow: inset 0 1px 2px var(--colors-paint-recess-1), inset 0 2px 6px var(--colors-paint-recess-2),
                   inset 0 0 0 .5px var(--colors-paint-recess-ring), 0 1px 0 var(--colors-paint-recess-lip);
--pressed-shadow:  inset 0 1px 2px var(--colors-paint-pressed-1), inset 0 0 0 .5px var(--colors-paint-recess-ring),
                   0 1px 0 var(--colors-paint-recess-lip);                                    /* shallower */
--display-shadow:  inset 0 2px 4px var(--colors-paint-display-1), inset 0 0 0 1px var(--colors-paint-display-ring),
                   0 1px 0 var(--colors-paint-display-lip);                                   /* deeper */
--display-cover:   linear-gradient(170deg, var(--colors-paint-display-sheen) 0 38%, transparent 38%);   /* the pane's reflection */
```

## Etched

An etched part is level with its ground, so its lit paint is the recess's pattern at a smaller depth: shade at the top,
light at the bottom, every cue **inside** the box, and no cast, outer lip or top highlight.

```css
--etched-shadow: inset 0 1px 1px var(--colors-paint-etch-top), inset 0 -1px 0 var(--colors-paint-etch-ledge),
                 inset 0 -2px 0 var(--colors-paint-etch-edge);
```

- The ledge is a lit line just inside the bottom edge: the floor of the inlay meeting its lower wall.
- The edge is a shade hairline directly above the ledge, in the light scheme only (its dark alpha is 0), because a white
  line on a near-white fill is too faint alone.
- Known risk: the edge puts shade near the bottom, which can read as a raised part's lower bevel. If it does, set the
  edge's alpha to 0 and keep the top shade. Never strengthen the ledge by moving the fill a step deeper: that step is the
  disabled and editable face.
- These three alphas are starting values from an exploration (2026-11-13) and are not yet confirmed in a build.

## Lamps and holes

- **Emissive (on)** glows: `0 0 6px var(--colors-paint-lamp-glow)`, its own colour at 60%, plus a lit inset on top and a
  shade inset below (the bevel's top and bottom roles), so it reads as a lens.
- **Hole (off)**: light from above shades its upper wall and catches its lower inner wall, so the lit line is *inside* the
  hole (a half-pixel inset at the bottom), never a ring around it:
  `inset 0 1px 1.5px var(--colors-paint-hole-wall), inset 0 -.5px 0 var(--colors-paint-hole-lip)`.
- An **indicator on a moving part** (a knob's pointer) is recessed into that part.

## States

Each state moves a fixed set of levers and leaves the rest alone.

| State | Face | Face shading | Bevel | Cast | Inward shadow | Ring |
|---|---|---|---|---|---|---|
| rest | the relief's face | lit top, shade low | lit top, shade bottom | at its level (a control: `raised`) | none | none |
| hover | one step nearer the ink (a ghost: no fill, its ink one step stronger) | unchanged | unchanged | unchanged: hover is not a change of height | none | none |
| pressed (held) | `--pressed-face` (a solid part: `--solid-pressed-face`) | none | none | none: it falls to the pressed recess | the pressed shadow, from the top, with the lit lower lip. The box doesn't move (no translate) | none |
| focus | unchanged | unchanged | unchanged | unchanged | none | the focus ring outside the box, identical in every material |
| selected / latched | the solid or selected face | the solid shading | the solid bevel (`--colors-paint-bevel-top-solid`) | unchanged: a control keeps its cast, a row has none | none, ever | none |
| open (a trigger whose popup is open) | the pressed face as a tint over its own face | unchanged | unchanged | unchanged | none: open is not pressed | none |
| disabled | the neutral face of its relief, marks faded | unchanged | unchanged | kept: the object is still there | none | none |
| review / read-only | `--etched-face` | none | none | none | the etched shadow | none |

A state that is not a change of relief or layer never changes the cast: a hover lift reads as motion and moves nothing a
reader can act on (rejected 2026-11-13). Timings are in construction.md › States.

## Pitfalls

- A lit alpha tuned in the light scheme shows up as grey smears in the dark one. Give every lit role a dark alpha: paint.json
  scales it by 0.25 unless the role sets its own.
- Gradients across many small parts band. Keep the face deltas at 0.03 L or less.
- `border` for the half-pixel ring changes the box. Use the shadow ring.
- A white or near-white solid face shaded all over turns grey. Limit the shade to the lower edge and keep the top at the fill.
- A selected part drawn with the pressed recess reads as stuck down. Selected keeps the raised paint; only a held press recesses.
- Never shade marks. The light falls on the face around a scale, not on the ink.
- A shade ring all round a card reads as a border (2026-11-13).
- A hosted control that clears only its fill keeps its recess shadow: a box in a box in every lit material (2026-11-13).
- An overlay whose inner card keeps its raised face draws a box in a box: a second rounded shape ending at the content
  (2026-11-13).
