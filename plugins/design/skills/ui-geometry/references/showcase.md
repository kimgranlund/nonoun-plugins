# Default component showcase

Use this brief when asked to generate a default showcase of what the geometry system can produce. It defines the content, layout constraints, and verification criteria for a static component bento. It is not required for ordinary geometry calculations.

The geometry skill supplies dimensions and relationships. The rendering environment supplies markup or drawing implementation. This brief does not prescribe a palette, typeface, icon family, theme, shadow treatment, or other visual styling beyond the chosen geometry parameters.

## Output

Generate a static specimen sheet on a **1280 × 960px canvas**, containing **24 representative ARIA UI patterns in eight groups**. Demonstrate component anatomy, relevant states, and consistent geometry without implementing interactive behavior.

These are representative patterns, not a ranked or exhaustive ARIA catalogue. Pattern names such as accordion and breadcrumb do not necessarily correspond to literal ARIA roles.

Use the defaults below unless the user supplies different parameters. User-supplied canvas dimensions, geometry, and component requirements take precedence; recompute the layout when they change.

## Geometry

Read [equations.md](equations.md) and derive dimensions with `../scripts/derive.mjs`. The equations and calculator remain the authority; the values below document the default configuration.

| Parameter | Default |
|---|---|
| Preset | Massimo |
| Root font size, n | 14px |
| Density, δ | Default |
| Curvature, κ | 0.75 for controls and lists, 0.5 for cards |
| Card depth, d | 4q (the bento uses 5q) |

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

All listed defaults land on whole pixels; the crisp preset keeps lengths whole at other sizes. Flag any off-grid value (only radii can fall off at odd q). `node ../scripts/derive.mjs --containers` lists the padding, gap and radius of every container.

Derive remaining lengths from the equations, including type sizes and line heights. Marks, tracks, rows and cells (checkbox, radio, switch, slider, meter, progress, tree indent, menu separator, data grid, tabs) are in section 4b of equations.md; floating widths are in its grid section. Every specimen dimension comes from one of these; do not invent a length. Preserve tier boundaries: a control uses its own curvature calculation, independently of its containing card. Geometry does not determine typeface selection or color.

## Grouping

| Group | Patterns |
|---|---|
| Actions | Button, link, toolbar |
| Choices | Checkbox, radio group, switch |
| Input | Textbox, combobox, spinbutton |
| Selection | Listbox, menu, tree view |
| Navigation | Tabs, menu bar, breadcrumb |
| Disclosure | Accordion, dialog, alert dialog |
| Feedback | Alert, tooltip, progress bar |
| Values and data | Slider, meter, data grid |

Label every group and each of its three patterns. Treat state comparisons as variants within one entry, not as additional patterns.

## Composition

- Fit the complete sheet within the canvas without scrolling, clipping, or overlapping content.
- Use eight group regions. Allow unequal dimensions and allocate space according to anatomy and state coverage rather than assigning every pattern an equal square.
- Keep specimens at their intended component scale. Allocate more room to dialogs, grids, and open menus instead of shrinking them.
- Draw the dialog and the alert dialog at the popover width, 80q (320px at the defaults). A dialog's 120q is a maximum, not its size, and drawing it at its content width is not scaling it down. Menus and the combobox list take their content width up to 80q; the tooltip up to 60q.
- Keep each pattern label adjacent to its specimen. Group labels and component labels must remain distinguishable.
- Show comparison states side by side where space allows. Preserve the same content and dimensions when comparing states of one component.
- Keep overlays inside their allocated region. Show their relationship to a trigger or surrounding content where that relationship is part of the pattern.
- Reserve space for labels and required annotations before allocating specimen space. A header is optional; it must fit within the same canvas budget.
- Do not add application navigation, unrelated metrics, decorative filler, or a surrounding fictional application.

For the default parameters, the usable area inside the margins is **1208 × 888px**. Subtract group gutters and any header from this area. Select the packing arrangement to fit the specimens; no fixed group proportions are prescribed.

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

- **Text edge.** Text sits at T = 2I from the edge of every control, menu row, list row and table edge cell, so a table above a button lines up with its label. One left edge: headings, captions, loose text (slider and meter labels, link sentences, breadcrumbs), shapes and unframed marks all start on the content edge; only text inside a shape and a field label (over its control's value) sit at T. Buttons pad 2I at a text edge and I at an icon edge, with an S-square icon box and a gap I; no wrappers (section 4).
- **Items and rows.** Menu, listbox and segment items are h − 2d_c in a d_c = ¾q inset (26 in 3), so one item plus its padding is h. List and table rows are h with an r outline and hairlines inside the rows (section 19).
- **Card text and gaps.** A card's title is a title row h tall with its text on the content edge. Groups sit d apart, blocks inside a group d/2, a group caption I above its content, a field label g_c above its control; the gap under the title is d/2 − I, and the gap before actions is d. A dialog is a card at 1½d, a popover at ¾d. Form fields sit 2I apart, labels and help text g_c from the control (sections 7 and 19).
- **Elevation.** Floating specimens take the elevation ladder (section 9): menus, open lists and tooltips at the popup level, dialogs at the modal level. In-place frames such as a listbox take none.
- **Focus.** A focused control shows the ring of section 10, w and o outside its edge, with a corner of r + o + w. Where the gap to a neighbour or an attached list is smaller than o + w, the ring is drawn inside instead.
- **Icon stroke.** Strokes follow section 17, a fixed ratio of the icon size.
- **Borders.** A bordered frame pads d − b, so its content keeps the frame's depth (section 12).

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

1. All 24 patterns appear once as labelled entries, organized into the eight specified groups.
2. Each entry contains its required anatomy and states; state variants stay within their entry.
3. The full composition fits within 1280 × 960px at the default parameters.
4. No component has been scaled down to compensate for insufficient space.
5. Dimensions satisfy the geometry equations, including control height, tier radii, nesting, and grid closure.
6. The construction annotation matches the rendered dimensions.
7. Labels, content, overlays, and comparison states remain readable and unobstructed.
8. Numeric labels match their visual representations.
9. Static specimens do not expose misleading interactive semantics or require interaction for inspection.
10. Styling comes from the user's supplied design context or the rendering environment; this brief adds no independent stylistic requirements.

Before delivery, inspect the output at the target canvas size and check the geometry against the calculator. If visual inspection is unavailable, state that limitation rather than claiming the layout was verified.
