# Component construction

How to build a component so it renders correctly in every material without per-material code. The geometry for every part
(tier, height, insets, radius, nesting inset, elevation level) comes from **ui-geometry**. This file assigns layer, relief and face.

## The rule of construction

> A component knows its parts and each part's layer, relief and face. It never knows the material.

Its CSS uses only material tokens (`--raised-face`, `--recessed-shadow`, `--overlay-backdrop`, …). The setting tables fill them.
A new material is a new preset, or at most a new value of one setting, and no component changes.

## Anatomy

layer · relief · face, with "—" for a mark. Casts use ui-geometry's elevation levels: controls `raised`, resting cards and
popovers `popup`, floating bars `floating`, dialogs `modal`.

| Component | Parts |
|---|---|
| Button | body: base · raised · neutral; primary: base · raised · solid; label: — |
| Ghost control | no face at rest; label and icon: marks. Hover: the ink one step stronger; pressed: one step quieter; no fill, no relief in any material. Selected, latched and open take their fill |
| Hosted control (an inline select, field or ghost in a row, toolbar or field) | no part: the host is its shape; label: a mark. It clears every face token (fill, shadow, pressed shadow, shading), not only its fill, so no material draws a recess, bevel or ring inside the host |
| Toggle / latching key | body: raised · neutral → latched: raised · solid (recessed only while held); status lamp: recessed · emissive (off: hole) |
| Checkbox | box: recessed · neutral → checked: recessed · solid; check: — (ink on solid) |
| Radio | well: recessed · neutral; bead: raised · solid |
| Switch | track: recessed · neutral (off) / recessed · solid (on); thumb: raised · neutral |
| Slider / fader | slot: recessed · neutral; filled range: recessed · solid; thumb: raised · neutral; scale: — beside the slot |
| Knob | body: raised · neutral (round face, darker ring); pointer: recessed into the body; scale: — around it |
| Text field | field: recessed · neutral (operable: `--field-shadow`) while it is editable; etched · neutral in review or when read-only by permission (with a lock mark); label, help: — at the text edge |
| Select / combobox | trigger: raised when it is pressed to open, recessed (a field) when it is typed into, etched in review; list: overlay · ground · neutral; rows: —; active row: a tint; selected row: `--selected-face`, no relief, when chosen alone; `--tint-face` and a checked box when chosen among several (the active row's tint differs from it: ui-interaction-dev `focus.cursor`) |
| Segmented control / tabs | tray: recessed · neutral, the same paint as a switch's off track (below its ground, never a panel on it); items: —; selected item: raised · neutral on the brightest face (white in both schemes) with dark text, never recessed and never the primary solid |
| Card | resting: raised · neutral at the popup level, the ground for its contents; dragged or opened over content: overlay |
| Panel / toolbar | body: ground (or raised at the popup level when it stands as a device); controls: raised / recessed. A bar of keys that must read as one tool takes the display fill (dark in every scheme), not the neutral solid, which inverts to a light bar in the dark scheme |
| Menu, popover | body: overlay · ground · neutral; items: — |
| Tooltip | ink tooltip: overlay · ground · **solid** (never transmissive); light tooltip: overlay · ground · neutral |
| Dialog, sheet | body: overlay · ground · neutral at the modal level, the ground for its own fields and buttons; scrim: an overlay fill (ui-colors `bg-backdrop`); a layout frame inside the body (a card that only lays out) is no part: no fill and no face. A card placed in the body as content is a card of its own |
| Sticky band (an overlay's or panel's header and closing row) | part of its host's ground: its host's face, clipped one hairline inside the host's edge so the host's ring runs past; a rule on its inner side under forced colours. Over glass, the same glass face as its host |
| Toast | overlay · ground · neutral; inline banner: base · recessed or ground |
| Tab bar, floating bar | overlay · ground · neutral at the floating level (content scrolls under it) |
| List / table | container: recessed (a well) or ground; rows: —; active row: a tint; selected row: `--selected-face`, no relief, when chosen alone; `--tint-face` and a checked box when chosen among several (the active row's tint differs from it: ui-interaction-dev `focus.cursor`) |
| Stat cell, read-only value, key cap in running text | etched · neutral; value: — |
| Meter, display | face: recessed · display; values: data marks |
| Chart | plot: recessed · neutral or display; grid and axes: — ink; series: — data |
| Node-link diagram | node: base · raised · neutral; edge: — a printed line; group: recessed · neutral (a well holding raised nodes); port: recessed · neutral hole, emissive when live; live path: — its edges in the emissive colour, with no glow |
| LED, status dot | recessed · emissive (on) / recessed · neutral hole (off) |

**An action over content is a fade.** A trailing action laid over a part's content (options, remove) has no relief: a
ghost glyph on a gradient from transparent to the face below it, wide enough to clear the glyph and its gap. The content
ends under the fade. Hover and press change the glyph's ink only, and the target and focus ring are kept. A raised key
in that place covers the content with a second, unrelated shape.

**A mark may carry live state.** A mark that shows what is live (a diagram's live path) may take the emissive colour,
`--emissive`, as its ink. It stays a mark: no relief, no glow and no shadow, and chroma maps it as it maps an emissive face.

**Rank is carried by the face.** Where delineation is `fill`, a control's rank shows in its face: primary a solid face,
secondary a neutral face (a quiet step of the neutral ramp, chosen by ui-colors), tertiary a ghost control. A line box
is not a rank: a secondary drawn as a ring beside a filled primary reads as a different kind of part, not a lower rank.
Where delineation is `line`, every rank is a line box and weight carries rank.

## States

| State | Move | Timing |
|---|---|---|
| hover | tint the face (no attribute change) | in at once, out over the settle duration |
| pressed | raised → recessed, keeping its face, only while it is held | in at once, out over the settle duration |
| selected / latched | a solid face, never recessed: a control stays raised, a row takes no relief. Wells that fill (a checked box, an on track, a filled range) stay recessed, because they hold | |
| live / active | the indicator's face → emissive | |
| open | the list or popover appears on the overlay layer; its trigger stays raised and takes the pressed face as a tint, with no inward shadow | |
| dragging | base → overlay | |
| review / read-only | a field or trigger → etched · neutral; controls that only act on the value (steppers, clear) leave the row, and the box keeps its size | |
| disabled | marks and emissive faded; a solid or tinted face → the neutral face of its relief (no primary, tint or status colour); layer, relief and casts kept; never etched | |
| focus | an outer ring, identical in every material | |
| invalid | a status mark or emissive indicator; attributes unchanged | |

Which paint each state moves in a lit material is in lighting.md › States. A state's way in is instant, so a press never
lags the finger; a part eases back to rest over one settle duration, a constant of the consuming system (200 ms is a
starting value). Under reduced motion every state switches at once and stays distinct.

### The system's state table

A consuming system writes its states once, in one table, and cites this skill in every cell. Rows are the states its
parts can hold; columns are the levers. A cell that departs from this skill names the system's choice and its reason; an
empty cell means the lever is as at rest. The table is the source for the system's components, its showcase and its
review. It adds no rule. The template gives the rows, the columns and the rule each row follows; the system writes every
answer in its own tokens, read from the rule cited:

| State | Face | Relief | Light · emissive | Line (`line`) | Motion in · out | Rule |
|---|---|---|---|---|---|---|
| rest | | | | | | rule 1; lighting.md › States |
| hover | | | | | | fills.md › States in colour only; line-and-mono.md › `delineation: line` |
| pressed (held) | | | | | | rule 5; lighting.md › States; fills.md › States in colour only |
| latched | | | | | | rule 5; construction.md › States |
| selected alone | | | | | | fills.md › Role colours per relief × face |
| selected among several | | | | | | fills.md › Role colours per relief × face; line-and-mono.md › `delineation: line` |
| open | | | | | | construction.md › States; line-and-mono.md › `delineation: line` |
| disabled | | | | | | construction.md › States |
| live | | | | | | rule 4; lighting.md › Lamps and holes |
| focus | | | | | | construction.md › States |
| review, dragging (where the system has them) | | | | | | construction.md › States |

Under reduced motion every row switches at once. A row with nothing in the Rule column is a gap in the system, not a
choice: say what it does and why.

## Shadow DOM and context

- Custom properties inherit through shadow roots, so the setting attributes on any ancestor reach every component
  unchanged. Never read the material in script.
- **The nearest setting wins.** A part may set its own material or transmission value inside an ancestor that sets
  another. Selectors on the part and from the ancestor have equal specificity, so source order decides: emit every
  value's rule for the part itself after all the ancestor rules, or scope them with `@scope`. Test a part set to one
  value inside an ancestor set to each other value.
- Mark each part's attributes on its `part=""` or with `data-layer`, `data-relief` and `data-face`, and style only with
  material tokens inside `:host` styles.
- Put overlays in the top layer (`popover`, `<dialog>`) or a portal at the body (to avoid the backdrop-root trap in transmission.md).
- Engine-dependent refraction is decided once, on `<html>` (`data-lens`). Components never branch on the engine.
- A part with a solid or selected face sets the mark tokens for what sits on it (its on-colour and its quiet and disabled
  inks, from ui-colors); a neutral face resets them; a part with no face passes its host's on.

## Enforcing it in a consuming project

1. **The token → attribute table** is [terms.json](terms.json) › `tokens`: each material token names its relief, face and
   layer, and the passes that write it. Read it; don't copy it.
2. **Classify every rule.** For each CSS rule (and each inline style in demos), read the `background`, `box-shadow` and
   `backdrop-filter` tokens, and fail when:
   - the face and the shadow imply different reliefs, except a pressed part (a raised face with the pressed shadow)
   - a pair is incompatible (a display face that isn't recessed, an emissive face that is raised)
   - an overlay token appears without the other two
   - a solid or emissive face takes a backdrop filter
3. **Stamp** `data-layer`, `data-relief` and `data-face` on rendered parts, so a page can show its anatomy.
4. **Hold transmission to its reach**: it may write only the tokens in [terms.json](terms.json) › `transmissionReach`
   (this skill's own tables are held to it by `scripts/check.mjs`).
5. **Read the render.** Split each computed `box-shadow` into layers: outer with blur = cast, inset with blur = recess or
   press, no blur = a line (bevel, lip, ring). Fail a selected, latched or current part with an inset blurred layer. In a lit
   material, fail a part that holds whose first layer is not inset with a positive y offset, or that has an outer blurred
   layer.

The instrumental-modernism build implements the earlier, single-attribute form of this check (`im/planes.py`: one
`data-plane` per part). Its planes map to these attributes as [terms.json](terms.json) › `retired` records: housing → ground;
on → raised; in → recessed; window → recessed · display; over → overlay · ground; solid → solid face (raised or recessed);
light → emissive face (recessed).

## Adopting materials in an existing system

In a system that already paints its parts, keep its paint as the default material: each part reads
`var(<material token>, <its own role>)`, every token is unset with no material attribute, and the default computes exactly
what it did before. Prove it by snapshotting every element's paint (colour, background, box shadow, outline, border,
backdrop filter, filter, opacity, box) in both schemes, before and after, with no attribute and with the default named,
matching elements by key and occurrence, not by index, so one added element does not hide every later difference. Derive
each part's layer, relief and face from what it already paints (the shared control paint is a raised control; an entry look
a recessed, operable field; a floating edge or an elevation an overlay at that level; a muted fill a well or track; text and
line colours marks), and declare them only where the paint does not say. Name a cast token per elevation level when the
system has more than two.

## Verification checklist

Render each component in every material preset × scheme, and at least one off-preset combination (Flat + frosted, Physical + mono):

- [ ] every part's box is identical across materials (compare `getBoundingClientRect()`)
- [ ] every part's attributes agree with its tokens, and overlays use all three
- [ ] in the computed shadows, no selected, latched or current part has an inset blurred layer; when lit, every part that holds starts with an inset layer falling from the top and has no outer blurred layer
- [ ] unlit: reliefs distinguishable, operable boundaries at ui-colors' `apca.ui` threshold or marked by an even ring
- [ ] lit: one light direction everywhere, no shading on marks, no grey lit smears in the dark scheme
- [ ] transmission: only overlay bodies and cover panes changed; text legible over the worst backdrop (read at the face's thinnest stop, composited over black and over white; include layers under the text that are not its ancestors, such as a sliding thumb or a highlight; fail a material only where it is worse than the default material); no nested glass; lens on/off shown
- [ ] line: fields meet ui-colors' `apca.ui` threshold; no part has a fill, a cast or a one-sided line; states are told apart by ring and text weight. Mono: no information carried by colour alone.
- [ ] etched, disabled and editable parts side by side are three different faces in Flat and three different rings under line
- [ ] disabled parts carry no primary, tinted or status colour
- [ ] reduced transparency, forced colours and more contrast fall back as composition.md says; a hover or selection highlight still paints under forced colours
- [ ] states move attributes as the system's state table says, and every cell of that table cites its rule; focus identical everywhere
- [ ] no page errors, no overflow, nothing clipped by its container

## Objects with their own colours

A part that depicts a real object keeps that object's colours in every scheme: piano keys are ivory and ebony in light and
dark, never the theme's raised face and its inverse. Use the fixed endpoints (ui-colors `white` and `black`, or a system's
ink materials), shade them with the material's lighting, and give hover and press one step toward the other colour.
(Added 2026-11-13: a keyboard drawn with the neutral solid inverted in the dark scheme.)
