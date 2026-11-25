# Equations

Every length is a line in the scope's font size: a·n + b px. A unit preset gives its constants as multiples of one unit q = a_q·n + b_q, so each length k·q is the line k·a_q·n + k·b_q; an exact preset gives each constant its own line (section 21). `references/lines.md` lists every row below as its line, for the standard, ladder and affine presets. The equations hold for any preset. The numbers are the standard preset. All lengths are in q unless they carry px. The worked column uses n = 14, so q = 4px, at default density (δ = 1) with κ = ¾.

For another preset, substitute its constants: a_q, b_q in q = a_q·n + b_q; I_δ for I; g_c; S; soft and κ_s in r(κ); d_c; the level multipliers ℓ. Values at the three densities are written compact / default / loose.

## 1. Scale

| Symbol | Equation | n = 12 | 14 | 15 | 16 | 18 | 20 |
|---|---|---|---|---|---|---|---|
| q | n/2 − 3 | 3 | 4 | 4.5 | 5 | 6 | 7 |
| q (ladder) | ¾n − 6.75 | 2.25 | 3.75 | 4.5 | 5.25 | 6.75 | 8.25 |
| h (ladder, crisp) | 8q = 6n − 54 | 18 | 30 | 36 | 42 | 54 | 66 |

- Pixel grid: n·q is a whole px when n·(n/2 − 3) is an integer.
- All four icon sizes land on whole px when n ≡ 2 (mod 4), that is n = 10, 14, 18 or 22. Icon md (4q) is whole for every whole n.
- **The ladder preset** (a unit preset; the default before affine, section 21)**.** h = 6n − 54 straight from the scope's size (18, 24, 30, 36, 48, 60 at n 12, 13, 14, 15, 17, 19), q = h/8 = ¾n − 6.75; every other constant is the standard preset's, and crisp snapping lands each ladder step on whole px (at 14: I 6, S 18, g_c 2). A kit may name its sizes as steps of one ladder of n taken from the scope (sm one step down, lg one up), so a nested control reads its n from its parent, never the root; step tokens must then resolve on the element that uses them. The worked values below are the standard preset's (`--preset standard`).

## 2. Type

A role has two numbers m_t and k_t. Its size is s_t = F + m_t·q and its line height is s_t + k_t·q.

| Role | m_t | k_t | 14px s_t / line |
|---|---|---|---|
| display-lg | 12.5 | 1 | 64 / 68 |
| display-md | 8.5 | 1 | 48 / 52 |
| display-sm | 5.5 | 1 | 36 / 40 |
| heading-lg | 4 | 1.5 | 30 / 36 |
| heading-md | 2.5 | 1.5 | 24 / 30 |
| heading-sm | 1.5 | 1.5 | 20 / 26 |
| title-lg | ¾ | 1 | 17 / 21 |
| title-md | ¼ | 1 | 15 / 19 |
| title-sm (control label) | 0 | 1 | 14 / 18 |
| body-lg | ½ | 1.5 | 16 / 22 |
| body-md | 0 | 1.5 | 14 / 20 |
| body-sm, code | −¼ | 1.5 | 13 / 19 |
| label | −½ | 1 | 12 / 16 |
| kicker-lg | 0 | ½ | 14 / 16 |
| kicker-md | −½ | ½ | 12 / 14 |
| kicker-sm | −1 | ½ | 10 / 12 |

- The control label's line box is F + q. It fits the slot S = 5q when F + q ≤ 5q, that is for n ≥ 12.
- Line height in the text's own em: s_t·(1 + k_t/(2 + m_t)) + k_t·(3m_t/(2 + m_t) − 3) px.
- Weight is not a length, but it sets a label's width. Control text (labels, input values and placeholders) takes one weight, chosen by the consuming system (500 or less in product interfaces; 600 to 700 is common in civic, calm and toy ones), and keeps it in every state, so a selected or current item is exactly as wide as it was at rest. Which weights a typeface has, and the weight of headings and body text, belong to the consuming system.

## 3. Control

| Symbol | Equation | q (compact / default / loose) | 14px |
|---|---|---|---|
| I | 1 + δ/2 | 1 / 1.5 / 2 | 4 / 6 / 8 |
| m_c | I − ½ | 0.5 / 1 / 1.5 | 2 / 4 / 6 |
| g_c | ½ | 0.5 | 2 |
| S | 5 | 5 | 20 |
| h | S + 2I | 7 / 8 / 9 | 28 / 32 / 36 |
| h_o | S + 2g_c | 6 | 24 |
| B | h + 2: the title bar | 9 / 10 / 11 | 36 / 40 / 44 |
| T | 2I: the text edge | 2 / 3 / 4 | 8 / 12 / 16 |
| D | I/2: the composite edge | 0.5 / 0.75 / 1 | 2 / 3 / 4 |

These nest: control box (margin m_c) › content (gutter g_c) › slot S. So the slot sits exactly I in, and h = S + 2I.

I may be any value from 0. At I = 0 the control is its slot, h = S, and g_c must also be 0 so that m_c is not negative. Control height over the font size, h/F, is the figure to compare across systems: 2 / 2.29 / 2.57 with the standard insets at n = 14. A system outside that band sets its own `inset`. Checked: "a control with no inset is its slot, and h/F is 2 to 2.57 with the standard insets".

## 4. Icons in controls

| Size | a | 14px | offset from edge I + (S − a)/2 | 14px |
|---|---|---|---|---|
| sm | F (the text size) | 14 | 2.25 | 9 |
| md | 4 | 16 | 2 | 8 |
| lg | 4.5 | 18 | 1.75 | 7 |
| full | 5 = S | 20 | 1.5 | 6 |

- Leading icon then label: the label starts at I + S + I = 2I + S.
- Icon-only control: h × h, with the icon centred. Every icon size centres in the same S box, margin (S − a)/2: 3, 2, 1, 0 px at 14px. sm is tethered to the text size, so a small icon is always as tall as the type beside it; md and lg sit on the q ladder and snap to even px, and full is S (at 16px: 16, 20, 22, 24 with margins 4, 2, 1, 0; at 18px: 18, 24, 28, 30).

**Building it without wrappers.** Padding follows what sits at each edge, so no element wraps the icon or the label:

| At the edge | Padding | 14px |
|---|---|---|
| text | T = 2I | 12 |
| icon | I | 6 |

The icon owns an S-square box with its glyph a centred, a margin of (S − a)/2 that keeps the label still when the icon size changes. Icon and label sit I apart (a flex gap). The label is a bare text node, wrapped only when it must truncate. Horizontal margins never collapse in CSS, so the edge rule takes their place:

| Control (14px) | Edges and gap | Glyph at | Text at |
|---|---|---|---|
| label | 12 · label · 12 | — | 12 |
| leading icon | 6 · [20] · 6 · label · 12 | 8 | 32 = 2I + S |
| trailing icon | 12 · label · 6 · [20] · 6 | — | 12 |
| icon only | 6 · [20] · 6 | 8 | — |

The same rule serves chips, segments and menu rows with an optional icon at either end.
- Inline control (a chip or tag): h_o tall, offset g_c + (S − a)/2. A button inside an input is an item: h − 2d_c, inset d_c, like a segment.

## 4b. Marks, tracks and rows

Marks and tracks ignore density. A cell of a one-time code is square (1:1) at every width: when the code fills its host, the cells grow by aspect-ratio, never in width alone. A choice (checkbox, radio, switch) is a row h tall with no shape around it, so its mark is the visible edge and starts on the content edge, like headings, captions and shapes; the label follows at I + (S − a)/2 (8 at 14px, so the label sits at 24). One left edge holds for everything outside a shape; text inside a shape sits at T, and a field label sits at T over its control's value.

A group caption (a kicker) over shapes that hold text (a navigation section's heading, a menu's, listbox's or command list's group) is built as a field label is: a wrapper padded T at its text edge, so its text lands on T, where a text-only button's label, a row's text with no icon and an input's value land, also over rows that lead with an icon. Only a caption over loose content (headings, paragraphs, unframed marks) stays on the content edge. Inside a control frame the wrapper pads T − d_c from the frame's padding, as the rows do.

A mark beside a column of lines (an avatar or an icon beside a title line over a quiet line) aligns to the first line, never to the column's centre. The first line's box is at least S tall with its text centred in it. The mark, the column and any trailing controls are top-aligned: a mark of S or less sits in an S box level with the first line, a taller mark (2S beside two lines of S) starts at the first line's top, and trailing controls sit in an S-tall box level with the first line. The column starts the mark's width plus I + (S − a.md)/2 past the mark's start edge, and nothing wraps under the mark. A title that wraps grows the column downward and moves neither the mark nor the controls.

| Part | Size in q | Radius in q | 14px |
|---|---|---|---|
| checkbox box | a.md = 4 | 1 | 16, r 4 |
| radio box | a.md = 4 | round | 16 |
| radio dot | a.md/2 = 2 | round | 8 |
| switch track | 7 × a.md | round | 28 × 16 |
| switch thumb | a.md − 2g_c = 3 | round | 12 |
| badge | S | | 20 |
| badge dot | 2 | | 8 |
| swatch | S | 1 + g_c | 20, r 6 |
| separator | hairline, g_c above and below | | 2 + 2 |
| tree level indent | S per level | | 20 |
| progress or slider track | 1 | round | 4 |
| meter track | 2 | round | 8 |
| slider hit area | S tall | | 20 |
| slider thumb | a.md | round | 16 |
| slider minimum length | 10 | | 40 |

Rows and cells:

| Part | Equation | 14px |
|---|---|---|
| table or data-grid row | h, one line | 32 |
| cell inline padding | I | 6 |
| cell label | ≥ S, centred | 20 |
| tab, segment | h − 2d_c inside an h-tall host padded d_c = ¾q | 26 in 32 |
| menu or listbox row | h − 2d_c, corner r_f − d_c | 22 / 26 / 30, r 9 |

## 5. Curvature

Base curve, one per tier, with κ ∈ [0, 1]:

```
r(κ) = (κ / ¾) · 3                     for 0 ≤ κ ≤ ¾
r(κ) = 3 + ((κ − ¾) / ¼) · (h/2 − 3)   for ¾ < κ ≤ 1
```

- The anchors are square (κ = 0, r = 0), soft (κ = ¾, r = 3q) and pill (κ = 1, r = h/2).
- Below ¾ the curve ignores density. Above ¾ it follows h.
- r never exceeds h/2, since h ≥ 7q puts soft (3q) below h/2 at every density.

Concentric operators:

- Inward: r′ = max(0, r − e), for a child set in by e.
- Outward: R = r + e, for a parent wrapping by e.
- Cap: a frame of depth d > 0 never passes soft. It uses r̂ = min(r(κ), 3).

| Tier | Radius | 14px, κ = ¾ | κ = 1 |
|---|---|---|---|
| control | r = r(κ_control) | 12 | 16 |
| option in host | r_o = r − m_c | 8 | 12 |
| key cap in slot | r_s = r − I | 6 | 10 |
| control frame | r_f = min(r(κ_frame), 3) | 12 | 12 |
| frame row | r_f − d_c | 9 | 9 |
| card size 0 | r(κ_card) | 12 | 16 |
| card size d > 0 | R = d + min(r(κ_card), 3), and 0 when κ_card = 0 (a square child gives no arc to be concentric with); κ_card ½ by default | 4 + 2 = 6q = 24 | 4 + 3 = 28 |
| any card, nested card or panel, with `cardRadius: 'control'` | r(κ_control), whatever its padding; a flush nested card stays 0. A control inside is then not concentric with the corner | 12 | 16 |
| nested card at f | R′ = R − f·d (0 when f = 0) | f = ½: 16 | |
| panel (a card at d = 2I) | 2I + min(r(κ_card), 3), and 0 when κ_card = 0 | 12 + 8 = 20 | 24 |

- Composition: a chain carries one κ. A child in a different tier recomputes from its own κ, never from the parent's R.
- When κ_card = κ_control and r ≤ 3, a control at nest inset 1 inside a card is concentric for free: R − d = r. At the standard preset's κ_card ½, R − d = 2q and controls inside keep their own 3q.
- **Mixed corners on one box.** Where two adjacent radii sum past the side they share, the browser scales every radius of the box by one factor (CSS Backgrounds, corner overlap). A pill written as a huge length (9999px) beside a small corner sends the small one to almost 0, so a joined control's inner corner renders square though its computed value is right. Write a pill as h/2, or cap every corner at min(r, h/2), before giving one corner its own value. Check the rendered shape, not the computed radius.

## 6. Frames

| Frame | Depth | Children at | Text at |
|---|---|---|---|
| host (segmented, tabs) | pads (h − item)/2 = d_c = ¾q | d_c | T, from the host edge |
| control frame (listbox, popup) | d_c = ¾q, rows h − 2d_c padded T − d_c | ¾ | T, as the select's value |
| card size d | d from the ladder 0…9, moving depthStep·ΔI per density step (one q in the standard preset: 3q / 4q / 5q at d = 4) | d apart (groups) | d, the content edge |
| nested card at f | (1 − f)·d | f·d from the parent edge | |

The non-card levels have inset ℓ·I:

| Level | composite | group | collection | panel (region band) | page |
|---|---|---|---|---|---|
| ℓ | ½ | 1 | 2 | 2 | 4 |

List and table rows are h tall with text at T; menu, listbox and segment items are h − 2d_c with text at T (menus) in a d_c inset.

## 7. Gaps between siblings

Write a gap as gap(relation). G alone is the page gutter (section 8).

| Relation | gap | Kind | 14px (compact / default / loose) |
|---|---|---|---|
| joined: options in a host, rows in a body | 0 | | 0 |
| seam: a separator between control groups | g_c each side | fixed | 2 + 2 |
| hosted: wrapping controls inside one host | m_c | I − ½ | 2 / 4 / 6 |
| grouped: free buttons in an action row | min(2, I) | ℓ·I, capped | 4 / 6 / 8 |
| groups in a card | d (the full depth) | follows d | 16 in a d = 4 card |
| blocks inside a group | p/2 (half its padding p) | follows p | 8 in a d = 4 card |
| group caption → its content | I | ℓ·I | 6 |
| under a header (an unpainted title row) | p, as above it | follows p | 16 in a d = 4 card |
| under a painted, flush title band | max(0, p/2 − I) | optical | 2 in a d = 4 card |
| separate rows in a card | d/4, snapped to ½q | fixed | 4 at d = 4 |
| before an action row | p | follows p | 16 in a d = 4 card |
| form fields | 2I, as table columns | ℓ·I | 8 / 12 / 16 |
| label → control, control → help | g_c | fixed | 2 |
| around a field group | max(d, 3g_c): the gap between groups | follows d | 16 in a d = 4 card |
| sibling cards, grid columns | G = M/2 | ℓ·I | 12 |

- The gap rule: inside any container or layout band the gap is half its padding, and the gap before actions is the full padding. Every gap snaps to ½q, then to whole px under crisp (section 12).
- **A field group.** A field with its label, its help and the actions that submit it alone is one group. Inside it the parts are g_c apart (under a line grid, nothing beyond each control's box); around it the gap is the gap between groups, never under three times the gap inside (under a line grid, one body line). A form of several fields with one set of actions was not drawn and is not covered. Checked: "a field with its help and its own actions is one group: g_c inside, the gap between groups around it, never under three times the inside".
- A header is spaced as every other child of its container: the padding p above its row and a gap of p below it, so its text, I inside an h-tall row, has p + I on both sides. A smaller gap under it (p/2 − I) leaves p + I above the text and p/2 below, and the header reads pressed onto its content.
- Optical, for a band only: a title band is painted flush to the container's edges, so its own fill already separates it; the gap under it gives back the row's inset I, and text-to-text spacing reads p/2.
- **The flow of a page** is the one place the gap rule does not reach. Headings, paragraphs, actions and notes that run down a page section are spaced in body sizes F, not in insets, and so do not move with density:

  | gap(relation) | value | at F 14 / 16 / 18 |
  |---|---|---|
  | kicker → heading | F | 14 / 16 / 18 |
  | heading → the text under it | 1¼F | 18 / 20 / 22 |
  | paragraph → paragraph | 1¼F | 18 / 20 / 22 |
  | text → the actions under it | 2½F | 35 / 40 / 45 |
  | action → its note | F | 14 / 16 / 18 |
  | page section, above and below | 3¼F (6½F between sections) | 46 / 52 / 58 |

  Each snaps to whole px under crisp (ties to even), else to ½q. A gap is between glyph boxes (1¼ × the type size per line); a margin between line boxes is the gap less each line's half-leading. The preset key is `flow`. The constants are the medians of 156 measured pages (kicker and heading 1.1, paragraphs 1.19, heading to text 1.37, text to actions 2.49, sections 5.67 over all pages and 6.56 on marketing pages), chosen by the owner from five drawn rule sets; the measured ranges are wide, and section spacing on application screens was not measured. Inside a card, popover, dialog, panel or region the gap rule stands. Checked by `derive.test.mjs` › "the flow of a page is spaced in body sizes".
- Inside a padded container (popover, card, nested card, dialog, region, page section, page), no gap exceeds that container's largest padding. Containers padded 0 (a control row, a table, a form) are spaced by their gaps alone. Checked by `derive.test.mjs` › "no gap exceeds its container's padding".
- A control's own parts are spaced by its paddings and the icon gap I, never by a sibling gap from this table.
- A pair that acts as one control but whose halves each have their own fill, states and ring (a split button) is two controls a grouped gap apart, each with its full corner r. Join them (gap 0, r on the outside only) only when the pair is one shape, and then draw the ring inside (section 10).
- **A run** (a button group, a split button, a stepper's − value +) can sit between the two: whole controls a frame (2px) apart, r outside, and the corners that face each other closed to a fraction of h (h/3 chosen by an owner over h/5, which read as sharp), so the run reads as one shape with seams and each member keeps its own fill and ring. A run's members never dip on press, or the seams open.

## 8. Page grid

| Symbol | Equation | 14px |
|---|---|---|
| margin M | ℓ_page·I = 4I; or stepped by page width, ℓ_page ∈ { narrow, base, wide } | 16 / 24 / 32 |
| gutter G | M/2, snapped to ½q | 12 |
| column w | (W − 2M − (N − 1)·G) / N | W = 1280, N = 12: 22.92q = 91.7 |
| max columns | N_max = ⌊(W − 2M + G) / (w_min + G)⌋, w_min = 40 | 1280: 7 |
| span of j columns | j·w + (j − 1)·G | |
| multi-count grid | page = U + 2g units, u = W / (U + 2g), margin = gutter = g·u; n columns when n divides U + g, each (U − (n − 1)·g) / n units | U = 58, g = 2: 62 units; n ∈ {1, 2, 3, 4, 5, 6, 10, 12} |

- **A stepped margin.** `levels.page` is a number (4 in the standard preset, so M is one length at every width) or `{ narrow, base, wide }`, with `marginSteps` giving the two page widths in px at which it changes (600 and 1000 by default): M = narrow·I below the first, base·I between, wide·I from the second. `node scripts/derive.mjs --width W` reports M at W. The gutter G stays half the base margin, so columns do not jump at a step. Marketing carries 2, 4 and 8: its measured pages have a margin of 20px at 390 and 80px at 1440, which at I = 10 is 2I and 8I; the step widths are a starting choice, not measured.
- **A grid for several column counts.** Where one page holds passages of different column counts on one field, choose U and g so that every count you need divides U + g, and set the margin equal to the gutter. U = 58, g = 2 (Gerstner) gives 1–6, 10 and 12; U + g = 60 is the smallest field for 1–6. The field may also divide vertically into rows on the same counts (a square matrix). Snap u to the device grid as for w (section 12), so the columns line up across every count. `node scripts/derive.mjs --field U --gutter g --width W [--dpr 2]` prints u, the margin and every whole count up to 12 (`--max-columns`) with its column width in units and px. Checked: "every listed count fills the field in whole units".
- **Margin from the measure.** Where text is held to a measure, the page's margin is what the measure leaves, max(M, (W − content) / 2). A page with wide margins and one column (a public service page, an article) has not got a large M; `marginShare` in the profiles records the result (0.17 of the width for civic, 0.03 for instrument), not the constant.

Fixed widths, all maximums, all in q:

| Width | q | 14px |
|---|---|---|
| tooltip | 60 | 240 |
| popover, hover card, menu | 80 | 320 |
| dialog | 120 | 480 |
| rail | 56 | 224 |
| panel | 72 | 288 |
| reading measure | 160 | 640 |
| viewport margin | 4 | 16 |

A floating surface's width is w_f = min(max(w_a, min(content, maximum)), W − 2·viewport margin), from `floatingWidth()` in `derive.mjs`, where w_a is the width of the control that opens it and fills it (a select, a combobox, a pair of buttons that share one menu), and 0 otherwise. Its height is h_f = min(content, H − 2·viewport margin), with H the viewport's height (`floatingHeight()`). Content taller than h_f scrolls inside the frame, within its corner R. The frame never grows past the viewport and never scrolls as a whole, so a header and a closing row can hold to its top and bottom.

- Collapse breakpoint: two panels side by side, 2 × panel width = 144q (the `collapse` row of `derive.mjs`).
- Anchored placement: a popup's start edge sits on its anchor's start edge, d_c from it (section 19), so text at T in a row stands under text at T in the control. An inline control whose value sits at its row's end aligns end edges. When w_f does not fit toward the inline end, the end edges align; when the popup's height plus d_c does not fit below, it opens above. It is centred only when it is wider than the room on either side, and it is never narrowed below its longest row to fit one side.
- Sticky bands: bands held at the top and bottom of a scroller of height H_s stick while Σh_band ≤ H_s/2. Above that they fall back to flow. Once fallen, they stick again only when Σh_band ≤ H_s/2 − B: the gap of one bar keeps the fallback from switching back and forth while the scroller is resized around the half. With no height to measure against, they stick. While they stick, the room between them is H_s − Σh_band.

## 9. Elevation

A shadow is a stack of L layers, k = 0 (contact) to L − 1 (far halo), at a level scale s. Lengths are in q, and the alpha has no unit.

```
y_k      = e.y · s · ρ^(k − k_a)          offset, straight down
x_k      = y_k · tan θ                    light angle θ from vertical; 0 = overhead
blur_k   = β · y_k                        a higher layer is softer
spread_k = −σ · y_k                       σ > 0 tucks the penumbra under the surface
α_k      = B_α · (1 − λ) · λ^k / (1 − λ^L)  each layer λ times the one before; Σ α_k = B_α
A        = 1 − Π (1 − α_k)                composite alpha where every layer overlaps
```

- **Realistic softness.** Real shadows have a dense contact penumbra and a wide, faint ambient halo. Doubling offsets (ρ = 2) with blur proportional to offset and alpha decaying geometrically approximates that falloff. More layers (L = 5) smooth the transition between them.
- **Levels.** s scales the lengths only. B_α, and so A, is the same at every level, so elevation reads as height, not as darkness.
- **Layer count.** Going from 4 to 5 layers keeps k_a, which adds a halo layer at ρ times the largest. The budget B_α is redistributed over five layers, not added to.
- **Colour.** Each layer is pure black (or white for a glow) at α_k. A tinted shadow is a choice outside this skill.

The standard preset: e.y = 1, ρ = 2, k_a = 2, β = 2, σ = 0, θ = 0, λ = ¾, B_α = 0.19 light and 0.45 dark.

| Level | s | 4-layer offsets y (q) | 5-layer adds | Far blur (q) |
|---|---|---|---|---|
| raised | ½ | ⅛, ¼, ½, 1 | 2 | 2 (4 with 5 layers) |
| popup | 1 | ¼, ½, 1, 2 | 4 | 4 (8) |
| floating | 1½ | ⅜, ¾, 1½, 3 | 6 | 6 (12) |
| modal | 2 | ½, 1, 2, 4 | 8 | 8 (16) |

| Layers | α_k light (%) | α_k dark (%) | A light | A dark |
|---|---|---|---|---|
| 4 | 6.9, 5.2, 3.9, 2.9 (rounded 7, 5, 4, 3) | 16.5, 12.3, 9.3, 6.9 | 17.7% | 38.2% |
| 5 | 6.2, 4.7, 3.5, 2.6, 2.0 | 14.8, 11.1, 8.3, 6.2, 4.7 | 17.7% | 37.8% |

Worked at n = 14, popup, 4 layers, light: offsets of 1, 2, 4 and 8px, blurred 2, 4, 8 and 16px, at 7, 5, 4 and 3%.


## 10. Focus rings

A ring of width w sits o outside the control. Its outer edge is concentric with the control's corner.

| Symbol | Equation | standard q | 14px |
|---|---|---|---|
| w | ring width | ½ | 2 |
| o | ring offset | ½ | 2 |
| outer radius | r + o + w | 4 | 16 |
| stroke-centre radius | r + o + w/2 | 3.75 | 15 |
| clearance | o + w per side | 1 | 4 |
| inset ring (an option in a host) | drawn inside, r_o − w/2 | 1.75 | 7 |

- The clearance must not exceed the gap to a neighbour, or the ring overlaps it. That gap is min(2, I) for free buttons, and m_c for hosted controls, which use the inset ring.

## 11. Hit targets

A hit target T_hit is an accessibility floor in px, not a multiple of q. The visual box can be smaller; the difference is invisible padding.

| Symbol | Equation | 14px pointer (24) | 14px touch (44) |
|---|---|---|---|
| expansion of h | max(0, (T_hit − h)/2) per side | 0 | 6 |
| expansion of h_o | max(0, (T_hit − h_o)/2) per side | 0 | 10 |
| minimum I | (T_hit − S)/2, the inset at which h itself meets T_hit | 2 | 12 |

- A coarse-pointer mode raises I to at least the minimum I, or keeps h and adds the expansion as hit area.
- The smallest scope at which h meets T_hit is n ≥ 2·(T_hit/(S + 2I) + 3). For standard: pointer (24px) needs n ≥ 12 at default density and n ≥ 13 at compact. Touch (44px) needs n ≥ 17 at default density and n ≥ 16 at loose.

## 12. Borders and pixel snapping

A border b sits inside the box, so it eats padding and radius.

- Inner padding = d − b. Inner radius = max(0, R − b) for a card, or max(0, r − b) for a control.
- **Heavy rule.** Every rule is b. Where a system also has a heavy rule (the bar beside an inset note, under a header band, above a list of related links), it is I wide, the control's inset, so it grows with the unit and with density: 6px at n 14 default, 8px at n 16 default. There is no second border weight between the two. Measured: the heaviest rule on a civic page is 2, 6 and 10px at the quartiles, against 1 to 2px for every other archetype; the widths were read in px only, so the tie to I is a choice made on a drawn specimen, not a finding.
- At 14px with b = 1px: a card-4 has 15px inner padding and a 27px inner radius, and a control has an 11px inner radius.
- **Device grid.** A length lands on whole device pixels when px · dpr is a whole number. Snap with round(px · dpr) / dpr.
- **Fine patterns.** A pattern whose period is a few pixels (a dot or line grid, a hatch) is crisp only when its unit is whole device pixels: u_p = max(1, round(dpr)) / dpr CSS px (1px at 1x and 2x, 0.8px at 1.25x, 1.33px at 1.5x), re-read when the ratio changes (a `resolution` media query). Draw it as a small tile image scaled nearest-neighbour (`image-rendering: pixelated`) and sized in u_p, never with CSS gradients: a gradient is resampled smoothly, so at a fractional ratio every line smears into a band of in-between values.
- **Crisp.** By default a preset is crisp at n: I and g_c snap to whole px (round half to even) and S to even px, then depths and gaps snap to whole px. At 14 and 18 nothing moves. At 16 (q = 5) S = 24, I = 8, g_c = 2, h = 40, item 36. Radii may still land on half px at odd q (13.5 at 15px); a curve anti-aliases anyway. With `crisp: false`, the old rule holds: half-q lengths are whole when n ≡ 2 mod 4, quarter-q lengths when n ≡ 6 mod 8.
- **Exact.** A preset with `exact: true` snaps nothing: no inset, depth, gap or gutter is rounded, so every length is the line its constants give, at every n. Whether a line lands on whole px is then a property of its slope and offset, not of a rounding rule: a whole slope and a whole offset are whole at every whole n; a half slope is whole at every even n. `node scripts/derive.mjs --whole` lists every length that is not whole at every n, and where it is; a preset names the rows it accepts in `fractional`, and the command exits 1 on a row it does not name or a name that is whole after all (section 21). A fractional px there means a constant is wrong for that n, not that a `round()` is missing.
- **Stretched SVG.** A stroke drawn in an SVG that stretches to its box takes `vector-effect: non-scaling-stroke`, so the stroke width stays the system's width in CSS pixels; markers, dashes and text that must not stretch are drawn in HTML over it.

## 13. Vertical text centring

For a font with ascent A_f, descent D_f and cap height c_f (each a fraction of the em), set in a line box of height H:

```
baseline       = H/2 + (A_f − D_f)·F/2
cap centre     = baseline − c_f·F/2
optical offset = (A_f − D_f − c_f)·F/2       0 = the cap height is centred in the line box
```

- **Correction.** Shift the text by −offset to centre the caps optically. Inter-like metrics (A_f 0.969, D_f 0.242, c_f 0.727) give 0 to within 0.003px at 14px.
- **Label room.** A control label's line box is F + q, so the slot S leaves S − (F + q) of half-leading room. At 14px that's ½q = 2px; at the 12px minimum scope it's 0.
- **Baseline grid.** A role's line height is on a q baseline grid when (F + m_t·q + k_t·q) mod q = 0. The calculator lists every role that is off the grid, and by how much.
- **Line grid.** A preset may set `rhythm: 'line'` (the default is `'formula'`, the lines above). The body line then becomes a vertical module, L: the body-md line, or the running text's line under a `text` dial, rounded to an even px and raised by 2 where that does not divide by 4 (20px at n 14, 24px at n 16, 36px for running text on 35.25px). The half-line is L/2. Five rules follow.
  1. A text role's line is the next half-line multiple at or above 1.15 × its size; the module's own role sits on L.
  2. A heading or display role keeps a line of 1.15 × its size, to a whole px, and its block is padded below to the next half-line. The lines of a heading after its first are off the grid; what follows it is on.
  3. Small text under a large module, where rule 1 would give more than 1.8 × the size, is treated as a heading is: a line of 1.5 × its size, the block padded.
  4. A gap is rounded to the half-line and is never under one.
  5. A control is centred in a box of the next half-line multiple at or above h, and a row is that box.
  The cost is height: a 32px row becomes 40px and a 40px control takes 48px, which made a list 15% and a form 12% taller when drawn. Chosen from drawn specimens over no grid and over the unit as the grid, on five archetypes. The floor for a text line is 1.15: 1.3 was tried and dropped when both were drawn side by side on a list, where it moved one title from a 20px to a 30px line. The 1.15 for headings was chosen; the factor 1.8 and the divide-by-4 rule are starting values. `node scripts/derive.mjs --archetype <name>` prints the rows for an archetype that sets it. Checked: "rhythm 'line' puts text lines, gaps, control boxes and rows on half of the body line; a heading keeps its own line; the default prints nothing".

## 14. Fluid scale and container breakpoints

```
n(W) = clamp(min(n1, n2), n1 + (W − w1)·(n2 − n1)/(w2 − w1), max(n1, n2)), then rounded to step from align
```

- **Steps.** step 2 keeps q whole. step 4 with align 2 keeps half-q lengths whole. step 8 with align 6 keeps every length whole. Since every length is a multiple of q, the whole system scales with n.
- **Breakpoints.** The width at which a layout of j columns, each at least w_min wide, first fits is W_j = j·w_min + (j − 1)·G + 2M. At 14px with w_min = 40q: 208, 380, 552, 724, 896 and 1068px for 1 to 6 columns.
- **Container queries.** Measure W against the container instead of the viewport.
- **Threshold order.** A build tool that orders container or media queries by their text (Panda CSS does) puts `108em` before `54em`, so the wider rule loses. Write thresholds at a fixed digit count (`054em`, `108em`) and check the order in the built CSS.
- **Fit count.** A row of N items with natural widths w_1 … w_N (each as it renders unfolded, at its own scope and density) has a room W_r: its content box less its own padding. All N stay when Σw_i ≤ W_r + ε. Otherwise the first k stay, for the largest k < N with w_1 + … + w_k + w_more ≤ W_r + ε, and the rest fold into a trailing trigger w_more wide; k may be 0, the trigger alone. Reserve w_more only when something folds. When the trigger stands in for a folded item, w_more is that item's width plus the trigger's caret. ε = ½px absorbs the rounding of measured widths, so an item that fits is never folded.
- **Fold gap.** A fit read from natural widths against a room the fold does not change is stable and needs no margin: one threshold serves both ways. Where folding changes the room by δ (a sibling that narrows or widens with the fold), unfold only when W_r ≥ Σw_i + g with g ≥ δ; a smaller g still switches back and forth across a band δ − g wide. Where the fit is read from the live items (does the row overflow as it stands), a folded row never overflows, so keep the unfolded width from the moment of folding and unfold only when W_r exceeds it. Sticky bands take the same kind of gap (section 8).

## 15. Reading measure

A line of N_ch characters is N_ch · w̄ · F wide, where w̄ is the font's average advance in em (about 0.5 for Latin text faces).

| N_ch | Use | 14px, w̄ = 0.5 |
|---|---|---|
| 45 | minimum | 315px (78.75q) |
| 66 | ideal | 462px (115.5q) |
| 75 | maximum | 525px (131.25q) |

A fixed measure width (the standard preset's 160q) can be checked against this: 640 / (0.5 · 14) ≈ 91 characters, which suits a summary rather than running body text.

## 16. Media and avatars

- **Aspect ratios.** Height = w · h_r/w_r: 1:1, 4:3, 3:2, 16:9, 21:9.
- **Avatar ladder.** Each size is a length already in the system: a.md (4q), S, h_o, h, 2S, 4S.
- **Avatar radius.** Scale the control radius to the avatar's size: min(r(κ) · size/h, size/2). An h-sized avatar takes r. At κ = 1 every avatar is round.
- **Avatar in a slot.** Inside a control's slot, concentric with the control, the radius is r − I.

## 17. Icon stroke

stroke(a) = max(s_min, ρ_s · a). With ρ_s = 3/32 and s_min = 1px, strokes are 1.31, 1.5, 1.69 and 1.88px for icons sm to full at 14px. The stroke-to-size ratio stays fixed, so every tier reads at the same weight. Below the floor, the stroke stops thinning.

## 18. Tiers and fitting

Every length belongs to one tier; `unit` (F, q, type, b) is shared.

| Tier | Owns | Reads from below |
|---|---|---|
| controls | q, I, S, h, g_c, κ_control, icons, marks, focus, targets | — |
| collections | rows (menus h − 2d_c, lists and tables h), d_c = ¾q, r_f = min(r(κ_frame), soft), r_row = r_f − d_c | h, r(κ) |
| containers | d, R = d + min(r(κ_card), soft), nesting, gaps p/2 (title p/2 − I, actions p) | r(κ), I |
| layout | G, M = ℓ_page·I, columns, breakpoints; the flow gaps and section padding, in F | I, F (unit), w_min |

A tier t may run on its own unit q_t = a_t·n + b_t. A value read across tiers converts through px: v_t = v_s·q_s / q_t.

**Fitting** reverses the derivation. For measured lengths x_i:

- Unit: q* = argmax hit(q) − ¼·|ln(q / q(n))|, where hit(q) is the share of x_i within ¼px of a multiple of q/2. Fitted on the controls tier. A padding on the grid only at x − b is read as x − b. With scopes n_i, q = a_q·n + b_q by least squares through (n_i, q*_i).
- Controls: I = T/2 from the label inset, S = h − 2I.
- Curvature: κ(r) = κ_s·r/soft for r ≤ soft; κ_s + (1 − κ_s)(r − soft)/(h/2 − soft) above; 1 at r ≥ h/2. For a card, r = R − d.
- Conformance of a tier: the share of its lengths within ¼px of the target.

At n = 16 a Tailwind-like kit (h 40, label inset 16, r 6, card 24 / 12) fits q = 4, I = 2q, S = 6q, κ_control = 0.38, and fails R − d ≥ 0: its cards are less round than their padding.

## 19. Container spacing ladder

Every container, inside out, with its padding, gap and radius. A gap follows density (ℓ·I) or is fixed (a multiple of q). Inner radii stay concentric: inner = outer − the padding between. At n = 14, default density, κ = ¾ for controls and lists and κ = ½ for cards (the standard dials), d = 4 (q = 4, I = 6):

<!-- generated:ladder -->
| Tier | Container | Padding (px) | Gap (px) | Radius (px) | Height (px) |
|---|---|---|---|---|---|
| controls | Button, input, select | block I (6); text edge T = 2I (12); icon edge I (6) | icon box ↔ label I (6); glyph margin (S − a)/2 (2) | r(κ) (12) | h = S + 2I (32); icon box S (20) |
| controls | Icon button | icon edge I (6) | glyph margin (S − a)/2, a.md (2); a.sm (3); a.lg (1); a.full (0) | r (12) | h × h = I + S + I (32) |
| controls | Choice row | to the mark: 0, on the content edge (0); to a switch track: 0 (0) | mark ↔ label I + (S − a)/2 (8) | checkbox r_mark, radio round (4) | row h (32); mark a (16) |
| controls | Inline control | g_c (2); I (6) | — | r_o = r − m_c (8) | h_o = S + 2g_c (24) |
| controls | Hosted control | inset (h − item)/2 = d_c (3) | 0, or g_c between two (0) | r − d_c (9) | item h − 2d_c (26) |
| controls | Control row | 0 (0) | min(cap, I) (6) | r each (12) | h (32) |
| controls | Joined controls | 0 (0) | 0, shared edge (0) | r outside, 0 inside (12) | h (32) |
| collections | Segmented control, tab list | (h − item)/2 = d_c (3) | 0 (0) | host r (12); segment r − d_c (9) | host h (32); segment h − 2d_c (26) |
| collections | Listbox, menu, select popup | d_c (3); rows inline: T − d_c (text at T) (9) | rows 0 (0); separator g_c each side (2); popup offset from its trigger d_c (3) | r_f = min(r, soft) (12); rows r_f − d_c (9) | rows h − 2d_c (26) |
| collections | List, flush | 0, on the content edge (0); text at T = 2I, as a button label (12) | 0, hairline inside the row (0) | outline r, as a button; rows clip (12) | rows h (32) |
| collections | Table | 0, on the content edge (0); cells I each side (6); edge cells T = 2I, as a button label (12) | columns 2I (12); rows 0, hairline inside the row (0) | outline r, as a button; rows clip (12) | rows and header h (32); control in a cell: item h − 2d_c (26); its inset (h − item)/2 = d_c (3) |
| collections | List, inset | d_c (3); items inline: T − d_c (text at T) (9) | 0, selection is a fill (0) | outline r (12); selection r − d_c (9) | rows h, as a button (32) |
| collections | Form | control on the content edge (0); label and help at T, over the value (12) | between fields: 2I, as table columns (12); label → control g_c (2); control → help g_c (2) | — | fields h (32) |
| containers | Popover, tooltip | d_p (12) | d_p / 2 (6) | d_p + min(r, soft) (20) | — |
| containers | Card | d (16) | blocks in a group d / 2 (8); band → content max(0, d/2 − I) (2); header → content d (16); rows d / 4 (4); before actions d (16); groups d (16); group caption → content I (6) | R = d + min(r, soft) (24) | title row h (32) |
| containers | Nested card, well | (1 − f)·d (8) | (1 − f)·d / 2 (4) | R − f·d (16) | — |
| containers | Dialog, sheet | d_d (24) | band → body max(0, d_d/2 − I) (6); header → body d_d (24); body blocks d_d / 2 (12); before actions d_d (24) | d_d + min(r, soft) (32) | title row h (32) |
| layout | Region | 2·I (12) | 2·I / 2 (6) | 0 (0) | — |
| layout | Page section | 3.25·F block (46); 0 inline (0) | flow: kicker → heading 1·F (14); flow: heading → text 1.25·F (18); flow: paragraphs 1.25·F (18); flow: text → actions 2.5·F (35); flow: action → note 1·F (14) | 0 (0) | — |
| layout | Page | M = 4·I (24) | G = M / 2 (12) | 0 (0) | — |
<!-- /generated:ladder -->

The table is generated from `containers()` (`node scripts/docs.mjs`); `node scripts/docs.mjs --check` fails when it drifts.

- **Items.** Menus, listboxes, segmented controls and tab lists run items of h − 2d_c (22 / 26 / 30 by density) in a frame or host padded d_c = ¾q, so one item plus its padding is exactly h, the height of the select that opens the menu. Items take the corner r_f − d_c. A button inside an input (a hosted control) and a control in a table cell are items too: h − 2d_c, inset d_c.
- **Heights.** Three heights: h = S + 2I for a control and a list or table row, h − 2d_c for an item, h_o = S + 2g_c for an inline control (chip, tag).
- **Lists and tables.** They take the control radius r on their outline (rows clip to it), keep rows h with the hairline drawn inside the row, sit on the content edge with buttons and inputs, and pad their edge cells T = 2I, so cell text lines up with a button label. Between columns, each cell pads half the column gap on each side, so neighbours split it and columns stand one gap apart, not two; only the edge cells keep T. A checkbox column centres its box where a leading icon would sit and keeps the half gap on its far side. A row height that is a fractional multiple of h (1.25h) lands on half px at some n: prefer h, or h plus whole q. An inset list pads d_c, with a concentric selection r − d_c and text at T. A table may run its own density.
- **Gaps from the card tier out.** The gap is half the padding (p/2), the gap under a header is the full padding (equal space above and below its text), the gap under a painted, flush title band gives back the row's inset (p/2 − I), and the gap before actions is the full padding. Gaps snap to ½q, then to whole px under crisp (section 12).
- **Popover and dialog** depths follow the card depth, ¾d and 1½d (`spacing.popoverRatio`, `spacing.dialogRatio`); nesting f is the one free rung. Cards default to κ = ½ (`dials.kappa.card`), so their corner is d + 2q and the content area inside has 2q corners. Controls in the card keep their own r, because the chain restarts at the tier boundary. At κ_card = ¾ the corner is d + 3q.
- **Layout** levels: region 2I and page margin M = 4I, each with gaps of half that. A page section is padded 3¼F above and below and 0 at the sides (it shares the page's side edge, so content never sits 2M in); its gaps are the flow gaps of section 7.
- **Touch.** An item of 26px meets the 24px pointer target, not the 44px touch target: on touch, set `frameRow: 'h'` or raise the density (section 11).

## 20. Archetypes

An archetype is a named character held as a profile: for each observable, the band [25th percentile, median, 75th percentile] of the pages measured for it (`references/archetypes.json`, 115 public pages at 1440 × 900, one per site). It is not a preset. Many presets belong to one archetype, and a preset or a page is scored against it.

- **Distance.** For a value v and a band [lo, hi], the distance is max(0, lo − v, v − hi) over the observable's scale (its 10th to 90th percentile spread across all pages), capped at 3. An archetype's distance is the mean over the observables given, and 0 means inside every band. Nearest first; at equal distance the archetype with more bands for those values comes first. Checked: "an archetype's own medians score 0 against it, its dials rank it nearest among the derived values, and distance grows outside a band".
- **What a preset fixes.** Six observables: the body size n, h/F, control curvature r / (h/2), icon size over F, control text over F, and the measure. Type contrast is a cap: the largest type role whose size over F is inside the band. Everything else in a profile is page composition, which no preset sets: text and image coverage, capitals and weight; the typeface (serif share, stroke contrast, face weight); colour (tone of page and text, chroma, hues, contrast); grouping (gap sizes and their number, regions, radii in use, centring); and layout and pixels (columns, margins, white space, colourfulness, page length). A fit or a preset cannot tell two archetypes apart when they differ only there, as product and instrument do, and toy and marketing.
- **Measuring a page.** `scripts/observe.js`, evaluated in the page, returns 63 observables from the first three viewports at the current width: sizes and coverage, the typeface from pixels, colour in HCT with APCA and WCAG contrast, grouping, and layout. `scripts/observe.mjs` adds the other nine: pixel measures of a first-viewport screenshot, whether the page turns dark under a dark preference, and body size at 390px over body size at 1440px. Measure at 1440 × 900 preferring light, as the profiles were. A null is an observable that was looked for and not found, and is left out of the distance. Checked: "observe.js loads without a page and names exactly the observables of archetypes.json, and a stray one is caught".
- **Dials.** Each archetype carries an n, a density, κ per tier, an icon size and a type cap that land inside its bands, with the control on whole px. Where no standard density reaches its h/F it also carries `constants` (an `inset`, a `gutter`). A dial may sit outside its own band where the owner set it from a drawn specimen; `outsideBand` names the observable and the reason. Marketing's body size is one (18px, chosen over the measured 14 to 16px; by dials alone it then ranks calm first). Civic's is another (16px at the default density, chosen over the measured 18 to 19px; it still ranks civic first, with instrument close). Terminal's h/F is another: an inset of 0 reaches the band but takes every spacing to 0 with it, so it uses the standard compact density. Product carries `cardRadius: 'control'` in its `constants`: drawn, a 24px card beside 8px buttons and tables was called too big, and measured products draw surfaces nearly square (`kappaSurface` 0 to 0.07). Calm is 18px on the default density, chosen from a drawn specimen over the loose density of the measured middle; its h/F of 2.67 is the bottom edge of its band. Toy is 18px on the loose density with the `full` icon and `cardRadius: 'control'`, chosen from a drawn specimen: the body is above the measured 14 to 17px, the icon moves from 1.25 to 1.67 times the body (measured 1.29 to 2.29), and the derived card corner (36px) turned small tiles into circles; by dials alone toy then ranks first, where the measured middle ranked marketing first. Editorial is 16px on the default density with a `text` dial, chosen from a drawn specimen over the measured middle of 20px for both: controls stay at 16px and the article is set in the heading-sm role, 23.5px, above the measured 20 to 21px; its kickers are capitals (`label`), and its cards take the control's corner. Product, civic, editorial, calm and marketing carry `rhythm: 'line'` in their `constants`: each was drawn on the line grid and kept. Toy was drawn on it and kept off it. A dial may also be chosen inside its band: instrument's are 13px with the `lg` icon (16px), chosen from a drawn specimen over the measured middle of 14px; at 13px q is 3.5px, so half-unit lengths are fractions that snap to whole px. `node scripts/derive.mjs --archetype <name>` starts from them; flags override. Checked: "--archetype takes n, density and κ from the dials, a flag still overrides them, and an unknown name is refused".
- **Recognised** counts how often the profile model names the archetype for one of its own pages left out of the bands: first, and within two guesses. Product is the default: it is the middle, with no extreme of its own, so it is recognised least.
- **Families and soft edges.** The names are regions, not kinds. Clustering the measured pages with no knowledge of the names recovers most of them (adjusted Rand index 0.37 to 0.46 against at most 0.05 for shuffled names), but the grouping is weak (mean silhouette 0.18), with no preferred number of groups. So each archetype carries a `family`, and `near` lists those it cannot be told from: instrument and product are one family (application); calm and toy sit inside marketing's spread (expressive); editorial and civic are reading; fashion and terminal stand alone, terminal on six pages. When the runner-up is `near` the nearest and within 0.05, the report names the family.
- **Position.** `scripts/dimensions.mjs` places a measured page on the nine dimensions the pages vary along (`references/dimensions.json`): principal components of 66 rank-normalised observables that pass parallel analysis, together 51 percent of the variance. Six can be named from what loads on them: richness (type contrast, sizes in use, columns, largest type, colours, fills, image cover), body size, colour, white space, text cover, lightness. Three cannot. A score is in standard deviations of the measured pages; the report gives the archetypes whose means lie on either side. Nine scores name a page as well as the 68 bands do (120 of 156, each page left out, against 120), so position is the fuller answer for a page or a kit that sits between names. It needs 40 of the 66 observables: a preset alone fixes six and is refused. Curvature, though a dial, does not load at 0.5 on any kept dimension: pages differ more in richness, body size and colour than in corner radius.
- **What the sample cannot show.** The sites were chosen by one person to exemplify the names, one page per site, so agreement between groups and names is partly built in; the marketing pages were measured with this skill's runner and the others with an earlier one; no person judged the pages. A grouping by purpose (operate, read, sell) was tried and did no better than the names.
- **Running text.** One number, n, sets a control's label and the body text together, and reading pages set labels at 0.67 to 0.9 of the text. An archetype may carry a `text` dial, `{ role, line }`: running text is set in that type role, on a line of `line` × its size (1.5 where it is not given; measured reading pages 1.4 to 1.55), in place of the role's own heading line. The profile then takes `body` as that size and measures icon ÷ body, label ÷ body and type contrast against it; h/F stays against the control's own label, n, and no length changes. Without the dial running text is body-md at n, as before. Editorial carries it: heading-sm at n 16 is 23.5px on a 35.25px line, with labels at 0.68 of it; without the dial the same dials rank marketing first. Checked: "a text dial sets running text in a type role: body and the ratios against it move, h/F and the lengths do not; no dial, nothing changes".
- **Label tracking.** An archetype may carry a `label` dial: `{ case, tracking, role }`. Tracking τ is in ems of the label's own size F_l and adds τ·F_l after every letter, the last included. A label of c letters is c·τ·F_l wider, and its ink sits τ·F_l / 2 off centre in its control; take τ·F_l back at the label's end (a negative end margin of τ) so the text inset T holds on both sides. Fashion carries it (capitals, τ 0.22, at the label size), set from a drawn specimen and declared so in its `note`: it is above what was measured. Measured on text controls of the archetype pages (`ctlTracking`, `ctlUpperShare`): tracking is 0 at every quartile of every archetype and 0.13 at most; capitals are 0 at every median, with fashion's upper quartile at 0.5. Navigation links, read later on 98 pages: fashion sets capitals on 7 of 11 pages and tracks above 0.03 on two, 0.10 at most; one page of any archetype reaches 0.2.
- **Card κ** was not measured on this skill's scale. The card dial follows the share of square and pill surfaces: 0 where most surfaces are square, 1 where most are pills, ½ otherwise.

<!-- generated:archetypes -->
| Archetype | Family | Hero | n | Density | κ control / card | h/F derived | h/F band | Type cap | Signature | Recognised first / in two |
|---|---|---|---|---|---|---|---|---|---|---|
| instrument | application, near product | the control and the work surface | 13 | compact | 0.41 / 0.5 | 2 | 1.87 to 2.3 | heading-md | dispWeight, displayVh, gridShare4, iconOnlyShare, edgeDensity, textCov | 14 / 15 of 16 |
| product | application, near instrument | the task | 14 | default | 0.5 / 0.5 | 2.29 | 2.13 to 2.29 | heading-lg | regularity, mirrorLR, faceWidth, bgShare, imgCov, borderShare | 4 / 7 of 11 |
| civic | reading | the instruction | 16 | default | 0 / 0 | 2.5 | 2.31 to 2.51 | heading-lg | bwMax, marginShare, heavyShare, squareShare, ctlChroma, edgeTop3Share | 12 / 12 of 12 |
| editorial | reading | the text | 16 | default | 0.19 / 0.5 | 2.5 | 2.5 to 2.86 | display-md | serifShare, strokeContrast, dispContrast, pagesLong, circleShare, textCov | 13 / 13 of 14 |
| fashion | fashion | the object, in the image | 14 | default (own inset) | 0 / 0 | 3.14 | 2.69 to 3.43 | heading-lg | upperShare, maxChroma, imgCov, lineRatioDisplay, squareShare, nSizes | 19 / 20 of 20 |
| calm | expressive, near marketing | the person's state | 18 | default | 1 / 1 | 2.67 | 2.67 to 3 | display-md | pillShare, kappaSurface, proximityRatio, kappa2, nGaps, marginShare | 6 / 7 of 10 |
| toy | expressive, near marketing | the act of touching | 18 | loose | 0.4 / 0.5 | 3 | 2.6 to 3.2 | display-sm | colourfulness, meanWeight, heavyShare, iconToBody, dispWeight, colourCount | 14 / 16 of 17 |
| terminal | terminal | the character grid | 16 | compact | 0 / 0 | 2.13 | 1.5 to 1.58 | title-md | monoShare, darkShare, faceWidth, regularity, occupancy, nSizes | 5 / 5 of 6 |
| marketing | expressive | one message about the product | 18 | loose (stepped margin) | 1 / 0.5 | 3 | 2.5 to 3.32 | display-md | displayVh, contrast, nRadii, pagesLong, squareShare, nSizes | 27 / 37 of 41 |
<!-- /generated:archetypes -->

## 21. Lines and exact presets

**The primitive.** A length is a line a·n + b, in px, of the scope's font size n. `node scripts/derive.mjs --lines` prints the line beside every row, for any preset; it is found by sampling the row at n, n + 2 and n + 4, so a row that crosses a floor, a cap, a snap or the bend of r(κ) there prints "not a line here". Under the standard preset without snapping h = 8q = 4n − 24 and I = 1.5q = 0.75n − 4.5.

**Why a unit is not enough.** A unit preset ties every slope to every offset: each length is k·(a_q·n + b_q). A system whose slot is S = 2n − 8 and whose inset is I = n − 9 (so h = S + 2I = 4n − 26) has no such q, since S / I is not constant. So a preset constant may be a line, written `{ "a": 2, "b": -8 }`, with an optional floor `min` and cap `max` in px. With a unit, a line constant resolves at n to line(n) / q(n) multiples of q, and the equations do not change. A type role may be `[size line, leading line]`; a level may be a line, which is that length whatever I is; a card depth may be a named line, `{ "name": "slot", "a": 2, "b": -8 }`.

**An exact preset** sets `unit` to 0·n + 1 (q is one px), `exact: true` and `crisp: false`, and gives its constants as lines. Three more keys serve it and any other preset:

- `cardRadius: 'level'`: the radius steps one inset per level out, whatever the padding: a nested control r − I, a control r, a card or panel r + I, a dialog r + 2I. A card inside a card is one level in, r.
- `spacing.fieldGap`, `spacing.popover` and `spacing.dialog`: the label gap and the popover and dialog depths as their own lines, where they are not g_c, ¾d and 1½d.
- `grid`: `gutter`, `inset` and `columns` for a gutterless grid. The columns touch; what is placed on them pads itself by the column inset, half the gutter, so a rule or a band can still run the full width and nothing needs a negative margin.

- `marks.sizes`: the small controls at each icon size (sm, md, lg), each from the mark of its size alone. `corner` is a check box's corner as a share of the mark; a switch is two marks wide less `switchInset` borders, and its thumb one mark less the same; a range's handle is `rangeThumb` of the mark, and its track (mark − `rangeCut` px) / `rangeParts`, never under a border. The rows are `mark.sm` … `range track.lg`; with it the plain `switch thumb` row follows the same rule at md.
- `widths.header`: a shell's header height. A preset that gives one also gets the docking width, panel + measure + 2M: the page width under which the side panel does not fit beside a full measure. It is a line in n, so a media or container query cannot hold it (a query does not read a custom property): compare against it in a `clamp()`, or set the breakpoint per scope size.
- `fractional`: the rows the preset accepts as not whole px at every n. `--whole` fails on any other, and on a name that is whole after all.

`reasons` holds, per input, why it is what it is. A constant with no reason is derived from those, or inherited.

**Density.** In an exact preset the three insets may be one line. A denser or looser region is then a scope with another n, which restarts the system (axiom 1); `--density` still selects among the three where they differ.

**Curvature.** r(κ) is a line in n at any fixed κ on one side of the soft anchor, and at the anchor it is the preset's `soft` line (r = n − 6 in the affine preset), capped at h/2.

**Finding the lines of a project.** `node scripts/fit.mjs lengths.json --lines` takes lengths measured at two or more n and prints each one's line, its largest residual and the n at which it crosses zero. Every line of a unit system crosses zero at the same n, −b_q / a_q (6 for standard, 9 for ladder); where the zeros spread, no one unit holds the system and each constant is written as its own line.

**The affine preset** is such a system, and the default: `node scripts/derive.mjs` with no `--preset` answers in it. A caller that needs a unit preset names it. The rows below are a measured kit's own lines, and `scripts/derive.test.mjs` holds the calculator to them (`PRESETS.affine.source`); its other constants are the nearest expression of the standard preset's rows in the same lines, and are not that kit's. Two rows are not that kit's and are not in the list: the popover depth and the menu item, which it does not state as lines.

<!-- generated:lines -->
| Length | Row | Line | n = 10 | 14 | 22 |
|---|---|---|---|---|---|
| S | `controls.control.s` | 2n − 8 | 12 | 20 | 36 |
| I | `controls.control.i` | n − 9 | 1 | 5 | 13 |
| h | `controls.control.h` | 4n − 26 | 14 | 30 | 62 |
| h_o | `controls.control.h_o` | 2n − 8 | 12 | 20 | 36 |
| T | `controls.control.t` | 2n − 18 | 2 | 10 | 26 |
| a.sm | `controls.icon.a.sm` | n | 10 | 14 | 22 |
| a.md | `controls.icon.a.md` | 1.5n − 4 | 11 | 17 | 29 |
| a.lg | `controls.icon.a.lg` | 2n − 8 | 12 | 20 | 36 |
| r | `controls.curvature.r` | n − 6 | 4 | 8 | 16 |
| r_s | `controls.curvature.r_s` | 3 | 3 | 3 | 3 |
| switch track | `controls.mark.switch-track` | 3n − 12 | 18 | 30 | 54 |
| switch thumb | `controls.mark.switch-thumb` | 1.5n − 8 | 7 | 13 | 25 |
| checkbox radius | `controls.mark.checkbox-radius` | 0.375n − 1 | 2.75 | 4.25 | 7.25 |
| mark.sm | `controls.mark.mark.sm` | n | 10 | 14 | 22 |
| mark.md | `controls.mark.mark.md` | 1.5n − 4 | 11 | 17 | 29 |
| mark.lg | `controls.mark.mark.lg` | 2n − 8 | 12 | 20 | 36 |
| mark radius.sm | `controls.mark.mark-radius.sm` | 0.25n | 2.5 | 3.5 | 5.5 |
| mark radius.md | `controls.mark.mark-radius.md` | 0.375n − 1 | 2.75 | 4.25 | 7.25 |
| mark radius.lg | `controls.mark.mark-radius.lg` | 0.5n − 2 | 3 | 5 | 9 |
| switch track.sm | `controls.mark.switch-track.sm` | 2n − 4 | 16 | 24 | 40 |
| switch track.md | `controls.mark.switch-track.md` | 3n − 12 | 18 | 30 | 54 |
| switch track.lg | `controls.mark.switch-track.lg` | 4n − 20 | 20 | 36 | 68 |
| switch thumb.sm | `controls.mark.switch-thumb.sm` | n − 4 | 6 | 10 | 18 |
| switch thumb.md | `controls.mark.switch-thumb.md` | 1.5n − 8 | 7 | 13 | 25 |
| switch thumb.lg | `controls.mark.switch-thumb.lg` | 2n − 12 | 8 | 16 | 32 |
| range thumb.sm | `controls.mark.range-thumb.sm` | 0.5n | 5 | 7 | 11 |
| range thumb.md | `controls.mark.range-thumb.md` | 0.75n − 2 | 5.5 | 8.5 | 14.5 |
| range thumb.lg | `controls.mark.range-thumb.lg` | n − 4 | 6 | 10 | 18 |
| range track.sm | `controls.mark.range-track.sm` | 0.333n − 2.667 | 1 | 2 | 4.667 |
| range track.md | `controls.mark.range-track.md` | 0.5n − 4 | 1 | 3 | 7 |
| range track.lg | `controls.mark.range-track.lg` | 0.667n − 5.333 | 1.333 | 4 | 9.333 |
| header | `layout.width.header` | 6n − 34 | 26 | 50 | 98 |
| docking width | `layout.width.docking-width` | 68n − 36 | 644 | 916 | 1460 |
| R card-slot | `containers.curvature.r-card-slot` | 2n − 15 | 5 | 13 | 29 |
| R dialog | `containers.curvature.r-dialog` | 3n − 24 | 6 | 18 | 42 |
| dialog inset | `containers.frame.dialog-inset` | 4n − 26 | 14 | 30 | 62 |
| page inset | `containers.frame.page-inset` | 4n − 26 | 14 | 30 | 62 |
| panel inset | `containers.frame.panel-inset` | 2n − 8 | 12 | 20 | 36 |
| label → control, control → help | `containers.gap.label-control-control-help` | n − 9 | 1 | 5 | 13 |
| rail | `containers.width.rail` | 8n − 42 | 38 | 70 | 134 |
| panel | `containers.width.panel` | 16n + 16 | 176 | 240 | 368 |
| measure | `layout.width.measure` | 44n | 440 | 616 | 968 |
| G | `layout.grid.g` | 2n − 18 | 2 | 10 | 26 |
| column inset | `layout.grid.column-inset` | n − 9 | 1 | 5 | 13 |
| label | `unit.type.label` | n − 2 | 9 | 12 | 20 |
| body-md | `unit.type.body-md` | n | 10 | 14 | 22 |
| title-md | `unit.type.title-md` | n + 2 | 12 | 16 | 24 |
| heading-sm | `unit.type.heading-sm` | 2n − 10 | 10 | 18 | 34 |
| heading-md | `unit.type.heading-md` | 2n − 8 | 12 | 20 | 36 |
| display-md | `unit.type.display-md` | 4n − 26 | 14 | 30 | 62 |
| body-md line | `unit.type.body-md-line` | 2n − 8 | 12 | 20 | 36 |

Whole px with nothing snapped, n = 10 to 24: 175 lengths checked, 149 whole at every n.

| Row | Whole at |
|---|---|
| `controls.control.d` | odd n |
| `controls.icon.a.md-offset` | n = 12, 16, 20, 24 |
| `controls.mark.choice-label` | n = 12, 16, 20, 24 |
| `controls.mark.checkbox-radius` | n = 16, 24 |
| `controls.mark.radio-dot` | n = 12, 16, 20, 24 |
| `controls.mark.mark-radius.sm` | n = 12, 16, 20, 24 |
| `controls.mark.range-track.sm` | n = 10, 11, 14, 17, 20, 23 |
| `controls.mark.mark-radius.md` | n = 16, 24 |
| `controls.mark.range-thumb.md` | n = 12, 16, 20, 24 |
| `controls.mark.range-track.lg` | n = 11, 14, 17, 20, 23 |
| `containers.frame.composite-inset` | odd n |
| `controls.icon.a.sm-offset` | even n |
| `controls.icon.a.md` | even n |
| `controls.mark.checkbox-box` | even n |
| `controls.mark.radio-box` | even n |
| `controls.mark.switch-thumb` | even n |
| `controls.mark.range-thumb.sm` | even n |
| `controls.mark.mark.md` | even n |
| `controls.mark.switch-thumb.md` | even n |
| `controls.mark.range-track.md` | even n |
| `controls.mark.mark-radius.lg` | even n |
| `controls.track.progress-slider-track` | even n |
| `controls.track.slider-thumb` | even n |
| `containers.frame.nest-f-0.25-depth` | even n |
| `containers.frame.nest-f-0.75-depth` | even n |
| `containers.gap.separate-rows-card-d` | even n |
<!-- /generated:lines -->

The fractional rows all come from two places: the medium icon and mark, a blend halfway between the text size and the slot (1.5n − 4), whose half and quarter (its margin in the slot, a radio dot, a check box corner) land between px except at every second or fourth n; and I/2, the composite edge. A kit that needs them whole at every n changes the blend, not the rounding.

**What a kit reads.** `node scripts/derive.mjs --emit css` prints one custom property per length that is a line, `calc(a * 1em + b px)`, named by its row id, with its fallback at n = 16 as an exact ratio in em (`calc(19 / 8 * 1em)`, never truncated digits); `--emit json` prints the same as a manifest (id, name, line, px, declaration, fallback). An unregistered custom property keeps `1em` unresolved until a declaration uses it, so each line is read at the font size of the element that uses it and a scope is any element with its own font size. The cost: an element whose own font size is not its scope's (a heading, a label) reads the lines at its own size, so set a length on the box that has the scope's size, or give the scope a registered length equal to its `1em` and read that.
