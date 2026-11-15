# Default component showcase

Use this brief when asked to generate a default showcase of what the geometry system can produce. It defines the content, layout constraints, and verification criteria for a static component bento. It is not required for ordinary geometry calculations.

The geometry skill supplies dimensions and relationships. The rendering environment supplies markup or drawing implementation. This brief does not prescribe a palette, typeface, icon family, theme, shadow treatment, or other visual styling beyond the chosen geometry parameters.

## Output

Generate a static specimen sheet **1280px wide**, containing **24 representative ARIA UI patterns in eight groups** and **two more groups, Type and Space**, that show the type scale and the use of space: ten groups in all. Demonstrate component anatomy, relevant states, the type roles, the gap and padding ladders, and consistent geometry without implementing interactive behavior.

These are representative patterns, not a ranked or exhaustive ARIA catalogue. Pattern names such as accordion and breadcrumb do not necessarily correspond to literal ARIA roles. The Type and Space specimens are not patterns and are not counted among the 24.

Use the defaults below unless the user supplies different parameters. User-supplied canvas dimensions, geometry, and component requirements take precedence; recompute the layout when they change.

At full specimen size the ten group regions need about 1,509px of height, so the canvas must be at least that tall; a 1280 × 960 canvas cannot hold them without shrinking specimens, which acceptance criterion 4 forbids. The eight pattern groups take 1,161px of that; Type and Space add one row of 336px and its gutter. Their room comes from the canvas height: no pattern is scaled, narrowed or dropped to make it. The renderer sets the canvas (ui-showcase-bento uses 1280 × 1600 for this brief). With a shorter canvas, raise its height or change a parameter (density, tile depth), and say so. Never scale.

## Geometry

Read [equations.md](equations.md) and derive dimensions with `../scripts/derive.mjs`. The equations and calculator remain the authority; the values below document the default configuration.

| Parameter | Default |
|---|---|
| Preset | Standard |
| Root font size, n | 14px |
| Density, δ | Default |
| Curvature, κ | 0.75 for controls and lists, 0.5 for cards |
| Card depth, d | 4q; the group regions (tiles) use 5q |

| Symbol | Expression | q | px |
|---|---|---:|---:|
| Unit, q | n/2 − 3px | 1 | 4 |
| Inset, I | Default density inset | 1.5 | 6 |
| Slot, S | 5q | 5 | 20 |
| Control height, h | S + 2I | 8 | 32 |
| Control margin, m_c | I − 0.5q | 1 | 4 |
| Control radius, r | r(0.75) | 3 | 12 |
| Card depth, d | 4q | 4 | 16 |
| Card radius, R | d + min(r(κ_card), 3q) | 6 | 24 |
| Item (menu row, segment) | h − 2d_c, d_c = ¾q | 6.5 | 26 |
| Page margin, M | 4I | 6 | 24 |
| Page gutter, G | M/2 | 3 | 12 |

The group regions are cards at the tile depth, 5q. Their chrome:

| Tile part | Expression | q | px |
|---|---|---:|---:|
| Sheet margin | (1280 − 1208)/2, so the usable area is 1208 wide | 9 | 36 |
| Gutter between tiles | G | 3 | 12 |
| Tile depth (padding) | 5q | 5 | 20 |
| Tile radius | d + 2q (κ_card ½) | 7 | 28 |
| Group title row | h, kicker type | 8 | 32 |
| Title row → specimens | d/2 − I | 1 | 4 |
| Between specimens | d | 5 | 20 |
| Specimen caption → specimen | I | 1.5 | 6 |
| Grid paper rulings, where the renderer draws them | 2q, and 8q = h, from the tile's content edge | 2 / 8 | 8 / 32 |

The title row keeps the compact gap of a flush title band, d/2 − I, though a tile's title is unpainted and a card's header takes d below it. The sheet is a fixed canvas: d would add 16px to each of the five rows of tiles, and 1,509 + 80 no longer fits the 1,528 usable height. A showcase on a taller canvas may use d.

All listed defaults land on whole pixels; the crisp preset keeps lengths whole at other sizes. Flag any off-grid value (only radii can fall off at odd q). `node ../scripts/derive.mjs --containers` lists the padding, gap and radius of every container.

Derive remaining lengths from the equations, including type sizes and line heights. Marks, tracks, rows and cells (checkbox, radio, switch, slider, meter, progress, tree indent, menu separator, data grid, tabs) are in section 4b of equations.md; floating widths are in its grid section. Every specimen dimension comes from one of these; do not invent a length. Preserve tier boundaries: a control uses its own curvature calculation, independently of its containing card. Geometry does not determine typeface selection or color.

## Grouping

| Group | Entries |
|---|---|
| Actions | Button, link, toolbar |
| Choices | Checkbox, radio group, switch |
| Input | Textbox, combobox, spinbutton |
| Selection | Listbox, menu, tree view |
| Navigation | Tabs, menu bar, breadcrumb |
| Disclosure | Accordion, dialog, alert dialog |
| Feedback | Alert, tooltip, progress bar |
| Values and data | Slider, meter, data grid |
| Type | Display and heading roles, title, body, label and kicker roles |
| Space | Gap ladder, container padding ladder |

Label every group and each of its entries: three patterns in each of the eight pattern groups, two specimens in Type and two in Space. Treat state comparisons as variants within one entry, not as additional patterns.

## Composition

- Fit the complete sheet within the canvas without scrolling, clipping, or overlapping content.
- Use ten group regions. Allow unequal dimensions and allocate space according to anatomy and state coverage rather than assigning every pattern an equal square.
- Keep specimens at their intended component scale. Allocate more room to dialogs, grids, and open menus instead of shrinking them.
- Draw the dialog and the alert dialog at the popover width, 80q (320px at the defaults). A dialog's 120q is a maximum, not its size, and drawing it at its content width is not scaling it down. Menus and the combobox list take their content width up to 80q; the tooltip up to 60q.
- Keep each pattern label adjacent to its specimen. Group labels and component labels must remain distinguishable.
- Show comparison states side by side where space allows. Preserve the same content and dimensions when comparing states of one component.
- Keep overlays inside their allocated region. Show their relationship to a trigger or surrounding content where that relationship is part of the pattern. An overlay sits d_c (¾q) from its trigger, the same as its frame's padding.
- Let overlays sit directly on their group region, with no backdrop of their own. Where the renderer rules the region as grid paper (ui-showcase-bento does), the rulings fall on 2q and 8q = h from the content edge. Ruling gives transmissive materials something behind them and lets a reviewer read heights and insets. Do not draw a separate backdrop under each overlay: it costs space on every side, and a trigger standing on it needs a ground of its own.
- Put an annotation on its specimen's caption, after the name, rather than on a line of its own, so it costs no height.
- Reserve space for labels and required annotations before allocating specimen space. A header is optional; it must fit within the same canvas budget.
- Do not add application navigation, unrelated metrics, decorative filler, or a surrounding fictional application.

For the default parameters, the usable area inside the margins is **1208 × 1528px** on a 1280 × 1600 canvas. Subtract group gutters and any header from this area. Select the packing arrangement to fit the specimens; no fixed group proportions are prescribed. Measure each region's content first, then size the columns and rows to those minimums: a region with a tall specimen (dialog) gets the height, and a group that fits its specimens on one line costs one caption row.

A tested arrangement for the defaults, in five rows of grid areas over five columns:

```
disclosure disclosure disclosure  disclosure choices
selection  selection  navigation  navigation navigation
input      input      input       actions    actions
values     values     values      feedback   feedback
type       space      space       space      space
```

Its measured minimum region sizes (w × h, px) are: disclosure 955 × 311, choices 241 × 300, selection 599 × 208, navigation 597 × 264, input 802 × 266, actions 394 × 266, values 802 × 194, feedback 394 × 284, type 463 × 336 and space 676 × 329. The rows need 311 + 264 + 266 + 284 + 336 and four gutters of 12, 1,509px in all. They hold for specimens of the reference sizes (three textboxes at 120px, the accordion at 150px, dialogs at 320px, and the Type and Space reference specimens below).

The eight pattern minimums were measured on the reference sheet of the 24 patterns and are unchanged; that sheet's first four rows are this arrangement's. Type and Space were measured apart from it: each group alone in one tile with the tile chrome above, in headless Chromium in the system UI typeface, as the smallest tile that passes ui-showcase-bento's in-page check, with 1px less in either direction failing. A sheet with all 28 entries drawn has not been measured as a whole. Type's width follows the typeface, so another face needs its own measurement.

## Required anatomy and states

| Pattern | Required depiction |
|---|---|
| Button | Default, focused, and disabled states of the same labelled action |
| Link | Inline link and external destination indicator |
| Toolbar | Related actions with one selected toggle |
| Checkbox | Unchecked, checked, and indeterminate states |
| Radio group | At least three options with exactly one selected |
| Switch | On and off states |
| Textbox | Labelled default, focused, and invalid states; invalid state includes an error message |
| Combobox | Editable value, expanded suggestion list, and highlighted suggestion |
| Spinbutton | Value, decrement action, and increment action |
| Listbox | At least three options with one selected |
| Menu | Open action menu with a disabled item and a separated action group |
| Tree view | Expanded parent, child items, collapsed branch, and selected item |
| Tabs | At least two tabs, one selected, and its associated content region |
| Menu bar | Multiple top-level items with one associated menu open |
| Breadcrumb | At least three levels with the current location identified; fit on one line |
| Accordion | One expanded section with content and one collapsed section |
| Dialog | Title, supporting content, and completion or dismissal action |
| Alert dialog | Consequence statement and two clearly distinguished decisions |
| Alert | Status indicator and concise message |
| Tooltip | Visible tooltip associated with a trigger |
| Progress bar | Determinate progress with a matching numeric value |
| Slider | Track, thumb, current value, and range endpoints |
| Meter | Bounded measurement with value, unit, and capacity or range |
| Data grid | Column headers, at least two data rows, and one focused or selected cell |

Include one annotated construction specimen within an existing entry. Identify its **slot, inset, control height, and concentric radius relationship**. At the default equal tier curvatures, a control inset by d inside a card demonstrates R − d = r. Do not add a twenty-fifth pattern for this annotation.

Derived treatments that every specimen follows, from equations.md:

- **Text edge.** Text sits at T = 2I from the edge of every control, menu row, list row and table edge cell, so a table above a button lines up with its label. One left edge: headings, captions, loose text (slider and meter labels, link sentences, breadcrumbs), shapes and unframed marks all start on the content edge; only text inside a shape, a field label (over its control's value) and a group caption over shapes that hold text (a wrapper padded T, over the rows' text) sit at T. Buttons pad 2I at a text edge and I at an icon edge, with an S-square icon box and a gap I; no wrappers (section 4).
- **Items and rows.** Menu, listbox and segment items are h − 2d_c in a d_c = ¾q inset (26 in 3), so one item plus its padding is h. List and table rows are h with an r outline and hairlines inside the rows (section 19).
- **Card text and gaps.** A card's title is a title row h tall with its text on the content edge. Groups sit d apart, blocks inside a group d/2, a group caption I above its content, a field label g_c above its control; the gap under a header is d (its text has d + I above and below), under a painted, flush title band d/2 − I, and the gap before actions is d. A dialog is a card at 1½d, a popover at ¾d. Form fields sit 2I apart, labels and help text g_c from the control (sections 7 and 19).
- **Elevation.** Floating specimens take the elevation ladder (section 9): menus, open lists and tooltips at the popup level, dialogs at the modal level. In-place frames such as a listbox take none.
- **Focus.** A focused control shows the ring of section 10, w and o outside its edge, with a corner of r + o + w. Where the gap to a neighbour or an attached list is smaller than o + w, the ring is drawn inside instead.
- **Icon stroke.** Strokes follow section 17, a fixed ratio of the icon size.
- **Borders and lines.** Draw outlines, hairlines and field boundaries as inset rings (an inset shadow), not as borders, so every box is identical in every rendering (mode, material) and a frame pads the full d. A frame drawn with a real border pads d − b, so its content keeps the frame's depth (section 12).

## Type and space

Two groups show what holds a layout together: the type scale (equations.md section 2) and the gap and padding ladders (sections 7 and 19). Their specimens are not patterns: they have no states, and each shows the lengths it names.

| Specimen | Required depiction |
|---|---|
| Display and heading roles | display-lg, display-md, display-sm, heading-lg, heading-md and heading-sm, one line each: sample text at the role's true size in a line box of its line height, with a note naming the role, its size and line height in px, and its line height in q |
| Title, body, label and kicker roles | title-lg, title-md, title-sm, body-lg, body-md, body-sm, label, kicker-lg, kicker-md and kicker-sm, drawn and noted the same way |
| Gap ladder | Six rungs, each a pair of siblings with the gap between them marked at its true length and named: groups in a card (d), blocks in a group (d/2), form fields (2I), group caption → content (I), field label → control (g_c), joined parts (0) |
| Container padding ladder | Four frames, each at its own radius with its padding marked at its true length and named: card (d), popover (¾d), dialog (1½d), panel, a card of controls (2I) |

- **Type.** Each role's size is s_t = F + m_t·q and its line height s_t + k_t·q. At the defaults, size / line height in px:

  | Roles | Size / line height |
  |---|---|
  | display-lg, display-md, display-sm | 64 / 68, 48 / 52, 36 / 40 |
  | heading-lg, heading-md, heading-sm | 30 / 36, 24 / 30, 20 / 26 |
  | title-lg, title-md, title-sm | 17 / 21, 15 / 19, 14 / 18 |
  | body-lg, body-md, body-sm | 16 / 22, 14 / 20, 13 / 19 |
  | label | 12 / 16 |
  | kicker-lg, kicker-md, kicker-sm | 14 / 16, 12 / 14, 10 / 12 |

  Draw every role at this size; a role is never scaled to fit, and none is left out. Make the line box visible (a fill or two rules), so the line height reads as well as the size.
- **Baseline grid.** A role is on the q baseline grid when its line height is a whole multiple of q (section 13). The note's line height in q says so: at the defaults display-lg 17q, display-md 13q, display-sm 10q, heading-lg 9q, body-md 5q, label 4q, kicker-lg 4q and kicker-sm 3q are on the grid, and the other eight are off it (heading-md 7.5q, for example) by the amount the calculator lists.
- **No typeface.** This brief names no typeface and no weight: both belong to the consuming system (section 2). The roles are drawn in the face the design context or the rendering environment supplies, and the sheet says which face that is where it is not the system's own.
- **Gaps.** A rung's siblings are blocks or controls h tall; the caption and the field label are text in the label role, the field label at T over its control's value. At the defaults the six gaps are 16, 8, 12, 6, 2 and 0px (d = 4q card, default density). Keep the rungs in the order of the row above.
- **Padding.** Each frame holds one block and nothing else, so the space between the block and the frame's edge is the padding alone. At the defaults: card 16px at radius 24, popover 12px at radius 20, dialog 24px at radius 32, panel 12px at radius 20.
- **Marks.** Mark a gap or a padding with a band exactly as long as the length it shows (a hatch or a tint; shape as well as colour), and write the symbol and the px beside or under it. The gap of 0 has no band: its two parts share an edge.
- **Reference specimens.** The measured minimums hold for these sizes: the sample "Ag" per role with its note 2I to its right; rungs 24q wide and 2I apart, each 20q tall with its label I below; frames around a block 20q × h, 2I apart, labelled the same way; the two Space specimens one above the other.

## Static rendering

- Show every required state immediately. No hover, click, keyboard input, or animation is needed to reveal content.
- Do not implement navigation, submission, selection changes, timers, or persistent state.
- In HTML, represent specimens as labelled static groupings or images with accessible descriptions. Do not expose nonfunctional examples as operable controls or put them in the tab order.
- Do not assign interactive ARIA roles merely to match the depicted pattern. Provide accessible descriptions of the illustrated state instead.
- Treat the result as a visual demonstration, not as evidence of functional or accessibility conformance for the depicted components.

## Specimen content

- Use short, plausible labels that make the pattern understandable.
- Keep repeated labels consistent across state comparisons.
- Include supporting text only to demonstrate anatomy, state, units, or consequences.
- Ensure numeric labels agree with visual proportions and selected values.
- Distinguish progress toward completion from a measurement within a bounded range.
- Use text or shape as well as color to communicate states and status.

## Acceptance criteria

1. All 24 patterns appear once as labelled entries, organized into the eight specified groups, and the Type and Space groups appear with their two labelled specimens each: ten groups in all.
2. Each entry contains its required anatomy and states; state variants stay within their entry. Each Type and Space specimen contains its required depiction: all 16 type roles, the six gaps and the four paddings.
3. The full composition fits within the canvas (1280 wide, at least 1,509 tall) at the default parameters, and no element runs into a region's padding.
4. No component or type role has been scaled down, and no pattern dropped, to compensate for insufficient space.
5. Dimensions satisfy the geometry equations, including control height, tier radii, nesting, grid closure, each role's size and line height, and every marked gap and padding.
6. The construction annotation matches the rendered dimensions.
7. Labels, content, overlays, and comparison states remain readable and unobstructed.
8. Numeric labels match their visual representations.
9. Static specimens do not expose misleading interactive semantics or require interaction for inspection.
10. Styling comes from the user's supplied design context or the rendering environment; this brief adds no independent stylistic requirements.

Before delivery, inspect the output at the target canvas size and check the geometry against the calculator. If visual inspection is unavailable, state that limitation rather than claiming the layout was verified.

## Rendering with ui-showcase-bento

This brief stands alone. When the `ui-showcase-bento` skill is installed, it can render the brief:
- Use its `ui-geometry` source, with the tile chrome above and the grid paper, plus its `geometry-28-1280` layout source, which holds the arrangement and minimums above. Its `aria-24-1280` layout source holds the eight pattern groups alone, on 1280 × 1280, for a source that shows only the 24 patterns.
- Its in-page checker covers criteria 1 and 3 and part of 4. It fails on overflow, on anything inside a region's padding, on scaled elements, on missing labels or counts, and on boxes that move between modes or materials.
- Check criteria 2 and 5–10 by eye and against the calculator.
- With a colour system, put the regions one step off the raised and overlay faces, so flat dialogs and menus separate from their region. Which steps those are is a colour and paint choice: it belongs to the colour source and to ui-materials' fills, not to this brief.
