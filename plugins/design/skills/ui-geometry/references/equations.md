# Equations

The equations hold for any preset. The numbers are the massimo preset. All lengths are in q unless they carry px. The worked column uses n = 14, so q = 4px, at default density (δ = 1) with κ = ¾.

For another preset, substitute its constants: a, b in q; I_δ for I; g_c; S; soft and κ_s in r(κ); d_c; the level multipliers ℓ. Compact and loose values are written c / d / l.

## 1. Scale

| Symbol | Equation | n = 12 | 14 | 15 | 16 | 18 | 20 |
|---|---|---|---|---|---|---|---|
| q | n/2 − 3 | 3 | 4 | 4.5 | 5 | 6 | 7 |

- Pixel grid: n·q is a whole px when n·(n/2 − 3) is an integer.
- All four icon sizes land on whole px when n ≡ 2 (mod 4), that is n = 10, 14, 18 or 22. Icon md (4q) is whole for every whole n.

## 2. Type

A role has two numbers m and k. Its size is s = F + m·q and its line height is s + k·q.

| Role | m | k | 14px s / line |
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
- Line height in the text's own em: s·(1 + k/(2 + m)) + k·(3m/(2 + m) − 3) px.

## 3. Control

| Symbol | Equation | q (c / d / l) | 14px |
|---|---|---|---|
| I | 1 + δ/2 | 1 / 1.5 / 2 | 4 / 6 / 8 |
| m_c | I − ½ | 0.5 / 1 / 1.5 | 2 / 4 / 6 |
| g_c | ½ | 0.5 | 2 |
| S | 5 | 5 | 20 |
| h | S + 2I | 7 / 8 / 9 | 28 / 32 / 36 |
| h_o | S + 2g_c | 6 | 24 |
| B | h + 2 | 9 / 10 / 11 | 36 / 40 / 44 |
| T | 2I | 2 / 3 / 4 | 8 / 12 / 16 |
| D | I/2 | 0.5 / 0.75 / 1 | 2 / 3 / 4 |

These nest: control box (margin m_c) › content (gutter g_c) › slot S. So the slot sits exactly I in, and h = S + 2I.

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

Marks and tracks ignore density. A choice (checkbox, radio, switch) is a row h tall with no shape around it, so its mark is the visible edge and starts on the content edge, like headings, captions and shapes; the label follows at I + (S − a)/2 (8 at 14px, so the label sits at 24). One left edge holds for everything outside a shape; text inside a shape sits at T, and a field label sits at T over its control's value.

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
| card size d > 0 | R = d + min(r(κ_card), 3); κ_card ½ by default | 4 + 2 = 6q = 24 | 4 + 3 = 28 |
| nested card at f | R′ = R − f·d (0 when f = 0) | f = ½: 16 | |
| panel (a card at d = 2I) | 2I + min(r(κ_card), 3) | 12 + 8 = 20 | 24 |

- Composition: a chain carries one κ. A child in a different tier recomputes from its own κ, never from the parent's R.
- When κ_card = κ_control and r ≤ 3, a control at nest inset 1 inside a card is concentric for free: R − d = r. At massimo's κ_card ½, R − d = 2q and controls inside keep their own 3q.

## 6. Frames

| Frame | Depth | Children at | Text at |
|---|---|---|---|
| host (segmented, tabs) | pads (h − item)/2 = g_c | g_c | g_c + I |
| control frame (listbox, popup) | d_c = ¾q, rows h − 2d_c padded T − d_c | ¾ | T, as the select's value |
| card size d | d from the ladder 0…9, one q per density step (3q / 4q / 5q at d = 4) | d apart (groups) | d, the content edge |
| nested card at f | (1 − f)·d | f·d from the parent edge | |

The non-card levels have inset ℓ·I:

| Level | composite | group | collection | panel (region band) | region (page section) | page |
|---|---|---|---|---|---|---|
| ℓ | ½ | 1 | 2 | 2 | 4 | 4 |

List and table rows are h tall with text at T; menu, listbox and segment items are h − 2d_c with text at T (menus) in a d_c inset.

## 7. Gaps between siblings

Write a gap as G(relation).

| Relation | G | Kind | 14px (c / d / l) |
|---|---|---|---|
| joined: options in a host, rows in a body | 0 | | 0 |
| seam: a separator between control groups | g_c each side | fixed | 2 + 2 |
| hosted: wrapping controls inside one host | m_c | I − ½ | 2 / 4 / 6 |
| grouped: free buttons in an action row | min(2, I) | ℓ·I, capped | 4 / 6 / 8 |
| groups in a card | d (the full depth) | follows d | 16 in a d = 4 card |
| blocks inside a group | p/2 (half its padding p) | follows p | 8 in a d = 4 card |
| group caption → its content | I | ℓ·I | 6 |
| under a title row | max(0, p/2 − I) | optical | 2 in a d = 4 card |
| separate rows in a card | d/4, snapped to ½q | fixed | 4 at d = 4 |
| before an action row | p | follows p | 16 in a d = 4 card |
| form fields | 2I, as table columns | ℓ·I | 8 / 12 / 16 |
| label → control, control → help | g_c | fixed | 2 |
| sibling cards, grid columns | G = M/2 | ℓ·I | 12 |

- The gap rule: inside any container or layout band the gap is half its padding, and the gap before actions is the full padding. Every gap snaps to ½q.
- Optical: a title row is h tall around one line, so it already carries I + (S − line)/2 above its text. The gap under it gives back I, so text-to-text spacing reads p/2.
- A gap never exceeds the inset of the frame that holds it.
- Controls never use a gap internally: their spacing is m_c + g_c.

## 8. Page grid

| Symbol | Equation | 14px |
|---|---|---|
| margin M | 4I (page level) | 16 / 24 / 32 |
| gutter G | M/2, snapped to ½q | 12 |
| column w | (W − 2M − (N − 1)·G) / N | W = 1280, N = 12: 22.92q = 91.7 |
| max columns | N_max = ⌊(W − 2M + G) / (w_min + G)⌋, w_min = 40 | 1280: 7 |
| span of k columns | k·w + (k − 1)·G | |

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

A floating surface takes its content width up to its maximum. It never exceeds the viewport less 2 × viewport margin.

- Collapse breakpoint: two panels, 2·72 = 144q.

## 9. Elevation

A shadow is a stack of L layers, k = 0 (contact) to L − 1 (far halo), at a level scale s. Lengths are in q, and the alpha has no unit.

```
y_k      = e.y · s · ρ^(k − k_a)          offset, straight down
x_k      = y_k · tan θ                    light angle θ from vertical; 0 = overhead
blur_k   = β · y_k                        a higher layer is softer
spread_k = −σ · y_k                       σ > 0 tucks the penumbra under the surface
α_k      = B · (1 − λ) · λ^k / (1 − λ^L)  each layer λ times the one before; Σ α_k = B
A        = 1 − Π (1 − α_k)                composite alpha where every layer overlaps
```

- **Realistic softness.** Real shadows have a dense contact penumbra and a wide, faint ambient halo. Doubling offsets (ρ = 2) with blur proportional to offset and alpha decaying geometrically approximates that falloff. More layers (L = 5) smooth the transition between them.
- **Levels.** s scales the lengths only. B, and so A, is the same at every level, so elevation reads as height, not as darkness.
- **Layer count.** Going from 4 to 5 layers keeps k_a, which adds a halo layer at ρ times the largest. The budget B is redistributed over five layers, not added to.
- **Colour.** Each layer is pure black (or white for a glow) at α_k. A tinted shadow is a choice outside this skill.

The massimo preset: e.y = 1, ρ = 2, k_a = 2, β = 2, σ = 0, θ = 0, λ = ¾, B = 0.19 light and 0.45 dark.

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

| Symbol | Equation | massimo q | 14px |
|---|---|---|---|
| w | ring width | ½ | 2 |
| o | ring offset | ½ | 2 |
| outer radius | r + o + w | 4 | 16 |
| stroke-centre radius | r + o + w/2 | 3.75 | 15 |
| clearance | o + w per side | 1 | 4 |
| inset ring (an option in a host) | drawn inside, r_o − w/2 | 1.75 | 7 |

- The clearance must not exceed the gap to a neighbour, or the ring overlaps it. That gap is min(2, I) for free buttons, and m_c for hosted controls, which use the inset ring.

## 11. Hit targets

A target T is an accessibility floor in px, not a multiple of q. The visual box can be smaller; the difference is invisible padding.

| Symbol | Equation | 14px pointer (24) | 14px touch (44) |
|---|---|---|---|
| expansion of h | max(0, (T − h)/2) per side | 0 | 6 |
| expansion of h_o | max(0, (T − h_o)/2) per side | 0 | 10 |
| minimum I | (T − S)/2, the inset at which h itself meets T | 2 | 12 |

- A coarse-pointer mode raises I to at least the minimum I, or keeps h and adds the expansion as hit area.
- The smallest scope at which h meets T is n ≥ 2·(T/(S + 2I) + 3). For massimo: pointer (24px) needs n ≥ 12 at default density and n ≥ 13 at compact. Touch (44px) needs n ≥ 17 at default density and n ≥ 16 at loose.

## 12. Borders and pixel snapping

A border b sits inside the box, so it eats padding and radius.

- Inner padding = d − b. Inner radius = max(0, R − b) for a card, or max(0, r − b) for a control.
- At 14px with b = 1px: a card-4 has 15px inner padding and a 27px inner radius, and a control has an 11px inner radius.
- **Device grid.** A length lands on whole device pixels when px · dpr is a whole number. Snap with round(px · dpr) / dpr.
- **Crisp.** By default a preset is crisp at n: I and g_c snap to whole px (round half to even) and S to even px, then depths and gaps snap to whole px. At 14 and 18 nothing moves. At 16 (q = 5) S = 24, I = 8, g_c = 2, h = 40, item 36. Radii may still land on half px at odd q (13.5 at 15px); a curve anti-aliases anyway. With `crisp: false`, the old rule holds: half-q lengths are whole when n ≡ 2 mod 4, quarter-q lengths when n ≡ 6 mod 8.

## 13. Vertical text centring

For a font with ascent A, descent D and cap height c (each a fraction of the em), set in a line box of height L:

```
baseline       = L/2 + (A − D)·F/2
cap centre     = baseline − c·F/2
optical offset = (A − D − c)·F/2       0 = the cap height is centred in the line box
```

- **Correction.** Shift the text by −offset to centre the caps optically. Inter-like metrics (A 0.969, D 0.242, c 0.727) give 0 to within 0.003px at 14px.
- **Label room.** A control label's line box is F + q, so the slot S leaves S − (F + q) of half-leading room. At 14px that's ½q = 2px; at the 12px minimum scope it's 0.
- **Baseline grid.** A role's line height is on a q baseline grid when (F + m·q + k·q) mod q = 0. The calculator lists every role that is off the grid, and by how much.

## 14. Fluid scale and container breakpoints

```
n(W) = clamp(min(n1, n2), n1 + (W − w1)·(n2 − n1)/(w2 − w1), max(n1, n2)), then rounded to step from align
```

- **Steps.** step 2 keeps q whole. step 4 with align 2 keeps half-q lengths whole. step 8 with align 6 keeps every length whole. Since every length is a multiple of q, the whole system scales with n.
- **Breakpoints.** The width at which a layout of k columns, each at least w_min wide, first fits is B_k = k·w_min + (k − 1)·G + 2M. At 14px with w_min = 40q: 208, 380, 552, 724, 896 and 1068px for 1 to 6 columns.
- **Container queries.** Measure W against the container instead of the viewport.

## 15. Reading measure

A line of c characters is c · w̄ · F wide, where w̄ is the font's average advance in em (about 0.5 for Latin text faces).

| c | Use | 14px, w̄ = 0.5 |
|---|---|---|
| 45 | minimum | 315px (78.75q) |
| 66 | ideal | 462px (115.5q) |
| 75 | maximum | 525px (131.25q) |

A fixed measure width (massimo's 160q) can be checked against this: 640 / (0.5 · 14) ≈ 91 characters, which suits a summary rather than running body text.

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
| containers | d, R = d + min(r(κ_card), soft), nesting, gaps p/2 (title p/2 − I, actions p) | r(κ) |
| layout | G, M = ℓ_page·I, columns, breakpoints | w_min |

A tier t may run on its own unit q_t = a_t·n + b_t. A value read across tiers converts through px: v_t = v_s·q_s / q_t.

**Fitting** reverses the derivation. For measured lengths x_i:

- Unit: q* = argmax hit(q) − ¼·|ln(q / q(n))|, where hit(q) is the share of x_i within ¼px of a multiple of q/2. Fitted on the controls tier. A padding on the grid only at x − b is read as x − b. With scopes n_j, q = a·n + b by least squares through (n_j, q*_j).
- Controls: I = T/2 from the label inset, S = h − 2I.
- Curvature: κ(r) = κ_s·r/soft for r ≤ soft; κ_s + (1 − κ_s)(r − soft)/(h/2 − soft) above; 1 at r ≥ h/2. For a card, r = R − d.
- Conformance of a tier: the share of its lengths within ¼px of the target.

At n = 16 a Tailwind-like kit (h 40, label inset 16, r 6, card 24 / 12) fits q = 4, I = 2q, S = 6q, κ_control = 0.38, and fails R − d ≥ 0: its cards are less round than their padding.

## 19. Container spacing ladder

Every container, inside out, with its padding, gap and radius. A gap follows density (ℓ·I) or is fixed (k·q). Inner radii stay concentric: inner = outer − the padding between. At n = 14, default density, κ = ¾ for controls and lists and κ = ½ for cards (the massimo dials), d = 4 (q = 4, I = 6):

| Tier | Container | Padding | Gap | Radius | Height |
|---|---|---|---|---|---|
| controls | button, input | I, T = 2I (6, 12) | icon ↔ label I + (S − a)/2 (8) | r (12) | h (32) |
| controls | icon button | I + (S − a)/2 (8) | — | r | h × h |
| controls | choice row (checkbox, radio, switch) | 0: the mark starts on the content edge, as does a switch track | mark ↔ label I + (S − a)/2 (8) | checkbox 4, radio round | row h |
| controls | hosted control (a button inside an input) | inset d_c (3) | 0, or g_c between two | r − d_c (9) | item h − 2d_c (26) |
| controls | inline control (chip, tag) | g_c, I (2, 6) | — | r − m_c (8) | h_o (24) |
| controls | control row | 0 | min(cap, I) (6) | r each | h |
| controls | joined controls | 0 | 0 | r outside, 0 inside | h |
| collections | segmented control, tabs | d_c = ¾q (3) | 0 | r → r − d_c (12 → 9) | h, segments h − 2d_c (26) |
| collections | listbox, menu | d_c = ¾q (3), rows T − d_c inline (9), so text at T (12) | rows 0, separator g_c each side ; popup offset from its trigger d_c (3) | r_f → r_f − d_c (12 → 10) | rows h − 2d_c (26) |
| collections | list, flush | 0 on the content edge; text at T = 2I (12) | 0, hairline inside the row | outline r (12), rows clip | rows h |
| collections | table | 0 on the content edge; cells I each side; edge cells T = 2I (12) | columns 2I (12) | outline r (12), rows clip | rows and header h; cell controls S + 2m_c (28) inset g_c |
| collections | list, inset | g_c (2), items T − g_c (10), so text at T = 2I (12) | 0, selection is a fill | outline r (12), selection r − g_c (10) | rows h (32), as a button |
| collections | form | control on the content edge; label and help text at T (12), over the value | between fields 2I (12), as table columns; label → control and control → help g_c (2) | — | fields h |
| containers | popover | d_p = ¾d (9 / 12 / 15) | d_p/2 (6) | d_p + min(r(κ_card), soft) (20) | — |
| containers | card (a panel is a card at d = 2I) | d = 3q / 4q / 5q by density (12 / 16 / 20) | groups d (16), blocks d/2 (8), caption → content I (6), under title d/2 − I (2 at every density), rows d/4 (4), before actions d (16) | d + min(r(κ_card), soft) (24) | title row h |
| containers | nested card | (1 − f)·d (8) | (1 − f)·d/2 (4) | R − f·d (16) | — |
| containers | dialog | d_d = 1½d (18 / 24 / 30) | under title d_d/2 − I (6), blocks d_d/2 (12), before actions d_d (24) | d_d + min(r(κ_card), soft) (32) | title row h |
| layout | region | ℓ_panel·I = 2I (12) | I (6) | 0 | — |
| layout | page section | ℓ_region·I = 4I above and below (24), 0 at the sides | 2I (12) | 0 | — |
| layout | page | M = ℓ_page·I = 4I (24) | G = M/2 (12) | 0 | — |

Menus and listboxes run rows of h − 2d_c (22 / 26 / 30 by density) in a frame padded d_c = ¾q, so one row plus its frame is exactly h, the height of the select that opens it. Segments use the same item height inside a segmented host padded g_c, so a menu and a segmented control share item height, padding and corner (r − g_c). Three heights use the heights: h = S + 2I for a control, h − 2d_c for an item, h_o = S + 2g_c for an inline control (chip, tag, a button inside an input). Rows stay concentric at r_f − g_c. Flush lists and tables take the control radius r on their outline (rows clip to it), keep full rows h with the hairline drawn inside the row, sit on the same content edge as buttons and inputs, and pad their edge cells T = 2I, so cell text lines up with a button label above or below. A table row is a host: a control in a cell is an item (h − 2d_c) inset d_c, so rows stay h with controls in them. Every list and table row is h, the height of a button or input, so a row and the control beside it match. A table may run its own density. An inset list (navigation, a selectable list) has the same r outline, rows h tall (a button's height) in a g_c inset with a concentric selection (r − g_c), and text at T = 2I, aligned with button labels. A 28px row meets the pointer target, not touch: on touch, set frameRow h. One rule sets every gap from the card tier out: the gap is half the padding (p/2), the gap under a title row gives back the row's inset (p/2 − I), and the gap before actions is the full padding. Every gap snaps to ½q. Popover and dialog depths follow the card depth, ¾d and 1½d snapped to ½q (`spacing.popoverRatio`, `spacing.dialogRatio`); nesting f is the one free rung. Cards default to κ = ½ (`dials.kappa.card`), so their corner is d + 2q and the content area inside has 2q corners. Controls in the card keep their own 3q, because the chain restarts at the tier boundary. At κ_card = ¾ the corner is d + 3q (card 28, dialog 36). Layout is app-dense: region 2I, page section 4I above and below (it shares the page's side edge, so content never sits 2M in) and page margin 4I (levels panel 2, region 4, page 4), each with gaps of half that. Everything else follows from the constants above.
