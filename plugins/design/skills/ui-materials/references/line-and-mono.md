# Delineation `line` and chroma `mono`

Two independent settings. The Outline preset uses both (with no lighting and opaque transmission), but either works alone.

## `delineation: line`

Every face loses its fill and every part draws an even 1px line **inside** its box, as `box-shadow: inset 0 0 0 1px …`,
so the box doesn't change. No part keeps a fill, and no line implies depth: never a cast, a heavier or doubled lower edge,
a one-sided line or an offset. Parts and states differ only by the ring's weight, its ink, dots, text weight and marks.

| Part | Face | Shadow |
|---|---|---|
| ground (base) | `--bg` | none |
| raised · neutral | `--bg` | `--line-strong` ring for a field-like trigger, `--line` ring for a button or key |
| pressed | `--bg` | a 2px `--line-strong` ring |
| open (a trigger whose list is shown) | `--bg` | the pressed ring, a 2px `--line-strong` ring: open takes the pressed face as a tint, so it takes the pressed weight |
| etched · neutral (a shown value) | transparent | `--line` ring at its faintest: the same ring whatever the lit form is |
| recessed · neutral (well, tray, track) | transparent | `--line` ring |
| recessed · neutral, operable (a field) | transparent | `--line-strong` ring: its boundary must meet ui-colors' `apca.ui` threshold |
| recessed · display | transparent; its marks in `--ink` | `--line-strong` ring |
| overlay body | `--bg`, opaque (or translucent when transmission isn't opaque) | `--line-strong` ring, no cast |
| solid (primary, selected) | transparent | a 2px ring in `--ink`, with heavier text in `--ink` |
| tint (a row chosen among several) | transparent | a `--line` ring; the checked box carries the selection |
| emissive | a filled dot in `--ink` (it is the size of a mark) | none |
| hole | transparent | `--line-strong` ring: an unlit lamp is an empty ring |
| disabled | transparent | a dotted `--line` ring, with faded ink |
| hover, highlighted row | transparent | hover: the ring one weight up (`--line` to `--line-strong`; a part already on `--line-strong` strengthens its ink); a highlighted row: a `--line` ring; no fill |

- **Line colours:** `--line-strong` (ui-colors `border-strong`) is the line for operable boundaries: ui-colors reports its
  APCA contrast on the page against `apca.ui`. `--line` (ui-colors `border`) is the step below it.
- **Marks follow the fill.** Where a face loses its fill, the marks drawn for it lose their fill too: `--on-display` and
  `--on-solid` become `--ink` (a muted mark on such a face, `--ink-muted`), as `--on-selected` does. A light mark left on
  a transparent face lands on the page and disappears.
- **Dashed is not used.** Dotted means disabled; weight means pressed or selected.
- **State fills, kept.** A system that must read state at a glance may keep, under `line`, the fills that carry state:
  `--pressed-face` while held (a solid part: `--solid-pressed-face`), the solid face (primary, latched, selected),
  `--tint-face` and the emissive face (a lamp on keeps its colour and size). Every neutral face still becomes `--bg` or
  transparent, and so does a container in a dark or solid fill (a bar of keys on the display fill, an ink tooltip or
  toast, a display window): that fill says what the part is, not its state, so it becomes the page with its ring, its
  marks in `--ink`; the state fills inside it stay, and every part keeps its even ring, so no box moves. Hover is not a state fill: it stays the ring one
  weight up, with no fill. This is a documented variant of `line`, not a new value; name it apart from Outline (for
  example "Outline with state fills"). Outline itself keeps no fill.
- **With lighting** (an off-preset mix), `line` keeps the cast and replaces only the bevel, giving a lit line drawing. The
  Outline preset has no lighting, so it has no cast.
- Use `line` for `prefers-contrast: more` and as the base for `forced-colors: active` (map the lines to `CanvasText`, faces
  to `Canvas`, selected and highlighted parts to `Highlight` with `HighlightText`). A part that shows only as a fill in
  other materials (a hover or selection highlight) must be given this paint, or it paints nothing. ui-colors serves its
  contrast modes under the same query; both apply.

## `chroma: mono`

Every colour that isn't a neutral maps to one ink:

| Token | Mono value |
|---|---|
| the primary solid, solid faces (held as well: `--solid-pressed-face`) | the text colour (`--ink`); `--on-solid` becomes `--bg`. Under `line` the solid has no fill, so it is the ink ring above |
| emissive | `--ink`; its glow drops, so a lamp on is a filled dot and a lamp off is an empty ring (or a hole when lit) |
| data series | `--on-display` or `--ink`. Series then need direct labels or patterns, never colour alone. |
| danger and status text | `--ink`, with the meaning carried by the words or an icon; a status mark carries its meaning in its shape (hollow, filled, bar, halo), never strike-through, which reads as cancelled |
| media | `--media-filter: grayscale(1)`, applied to the media element itself, never an ancestor of an overlay |

Neutral greys, ink and lines stay as they are. Contrast never drops below the colour version's, because solid and emissive
faces become the strongest ink there is.
