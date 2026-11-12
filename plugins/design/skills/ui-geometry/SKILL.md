---
name: ui-geometry
description: UI geometry as pure mathematics. Derives every length of an interface from a root font size n and one unit q, in four tiers (controls, collections, containers, layout): insets, slots, control heights, icons and stroke, type scale, marks and rows, card and popup frames, a curvature κ ∈ [0,1] with concentric radii per tier, focus rings, hit targets, borders and pixel snapping, text centring, fluid scale and breakpoints, measure, avatars, 4–5 layer elevation shadows, control gaps and page grids. Also fits an existing project's components to the nearest system, tier by tier, with a notation report and a before/after canvas. Ships a Massimo preset; any kit can bring its own. Use for "what is h at 16px", "radius at κ 0.4", "button gap", "grid columns at 1280", "a soft 5-layer shadow", "define a size system", "what system does this app use", "fit our components", or a showcase brief. NOT for implementing components or choosing colour, typefaces, motion or styling.
---

# UI geometry

One input, the scope font size n in px, and four dials: density δ, curvature κ per tier, card depth d, and a preset. Every length is a multiple of one unit q, snapped to whole px by default (crisp). Answer in symbols and multiples of q first, then px at n.

## Axioms

1. **Unit.** F = n and q = a·n + b. A nested scope with its own n′ restarts the whole system.
2. **Inset.** I_δ is one value per density. Density reaches spacing only through I.
3. **Control.** g_c is the fixed gutter, m_c = I − g_c the margin, S the slot, h = S + 2I the height.
4. **Frames.** A card has a depth d from a ladder that moves one q per density step (3q, 4q, 5q in massimo), so cards grow with their contents; popover and dialog follow at ¾d and 1½d. A panel of controls is a card at d = 2I. A page section shares the page edge and pads only above and below. Segmented hosts and control frames (menu, listbox) both pad d_c = ¾q around items h − 2d_c, so one item plus its padding is exactly h.
5. **Curvature.** Each tier t has κ_t ∈ [0, 1]. Radii are concentric within a tier, and the chain restarts at a tier boundary.
6. **Spacing.** Every gap is one of a few: the full depth d between groups in a card and before actions, half of it (p/2) between blocks inside a group, the label inset 2I between form fields and table columns, I under a group caption, g_c under a field label and between parts that belong together, or 0 between joined parts. Three label levels, three gaps. Text sits at T = 2I from the edge of every control, menu, list and table, so text in a stack lines up.
7. **Floors.** Hit targets and the reading measure are set in px and characters, not q. The geometry is checked against them, never scaled to fit them.
8. **Elevation.** A shadow is L layers in a geometric series. A level scales their lengths, never their alpha, so a higher surface casts a wider halo, not a darker one.
9. **Tiers.** Controls, collections, containers and layout each own their constants. A tier reads only named values from the tier below, so each can be fitted, tuned or adopted alone.

## Presets

A preset fixes the constants. The equations never change.

| Constant | Meaning | massimo |
|---|---|---|
| a, b | unit q = a·n + b | ½, −3 (q = 4px at 14) |
| I_δ | inset by density | 1 / 1.5 / 2 |
| g_c | control gutter | ½ |
| S | slot | 5 |
| soft, κ_s | radius at the soft anchor, and its κ | 3, ¾ |
| d_c, frame row | padding of menus, listboxes and segmented hosts (a number in q, g_c or m_c) and their item height (fit: h − 2d_c; m_c: S + 2m_c; h_o; h) | ¾, fit |
| card depths | frame ladder | 0…9 |
| ℓ | level multipliers of I: composite, group, collection, panel (region band), region (page section), page | ½, 1, 2, 2, 4, 4 |
| icons | sm (tethered to the text size F), md, lg, full (= S) | F, 4, 4.5, 5 |
| type (m, k) | size F + m·q, line size + k·q | see `references/equations.md` |
| e.y, ρ, k_a, β, σ, θ | elevation: key offset, layer ratio, anchor layer, blur ratio, spread ratio, light angle | 1, 2, 2, 2, 0, 0° |
| L, λ, B | layers, alpha decay, alpha budget (light / dark) | 4, ¾, 0.19 / 0.45 |
| s | elevation levels: raised, popup, floating, modal | ½, 1, 1½, 2 |
| w, o | focus ring width and offset | ½, ½ |
| T | hit targets, pointer / touch (px) | 24 / 44 |
| b | border (px) | 1 |
| A, D, c, w̄ | font ascent, descent, cap height, average advance (em) | 0.969, 0.242, 0.727, 0.5 |
| fluid | n(W) endpoints, step, align | (360, 14) → (1440, 16), step 2 |
| units, dials | optional: a unit per tier; default κ per tier, card depth and density | dials: κ_card ½ |
| spacing | popover and dialog depth as ratios of d, nesting f | ¾, 1½, ½ |
| measure, aspects, avatars, ρ_s | characters per line, ratios, avatar ladder, icon stroke ratio | 45 / 66 / 75; 1:1 … 21:9; 4, 5, 6, 8, 10, 20; 3/32 |

To define another system, write a JSON file with any of the keys from `PRESETS.massimo` in `scripts/derive.mjs`. Keys left out default to massimo.

## Procedure

1. Fix the preset, n, δ, κ for each tier and d. The defaults are massimo, δ = default, κ = κ_s for controls, lists and panels, κ = ½ for cards (so R = d + 2q at default density), and d = 4.
2. Compute q, I, m_c and h. Then compute the tier that is asked for, from `references/equations.md`.
3. For a full table, run `node scripts/derive.mjs --n <n> --density <δ> --kappa <κ>`. Add `--kappa-control`, `--kappa-frame`, `--kappa-card` or `--kappa-panel` to split tiers. Use `--card <d>`, `--width <px> --columns <N>` for a grid, `--preset <file.json>` for another system, and `--json` for data. Use `--viewport <px>` to take n from the fluid scale and `--dpr <x>` to list lengths off the device grid. For the padding, gap and radius of every container, inside out, run `node scripts/derive.mjs --containers [--card 4 --nest 0.5]` (section 19); popover and dialog default to ¾d and 1½d, and `--popover`/`--dialog` fix them. For shadows run `node scripts/derive.mjs --elevation <level|s|all> [--layers 5] [--scheme dark]`.
4. Check that the identities below hold. A value that breaks one is wrong.
5. Report a table with the columns symbol, expression, q, px. Flag any px that falls off the whole-pixel grid.

## Identities

- h = S + 2I. m_c + g_c = I. The inline height is h_o = h − 2m_c = S + 2g_c. Menu rows and segments are items of h − 2d_c (26 at 14px with d_c = ¾q), so one item padded d_c is h.
- Text sits at T = 2I in a control, a menu row (d_c + (T − d_c)), a list row and a table's edge cell. One left edge: headings, captions, loose text, shapes and unframed marks (checkbox, radio, switch) all start on the content edge. Text inside a shape sits at T, and a field label sits at T over its control's value.
- An icon of size a sits I + (S − a)/2 from the control edge. A label sits 2I in, or 2I + S after a leading icon. Built without wrappers: padding 2I at a text edge and I at an icon edge, an S-square icon box, a gap I.
- r(0) = 0, r(κ_s) = soft, r(1) = h/2. r is continuous and monotonic.
- For a card at d > 0, R − d = min(r(κ_card), soft): 2q at massimo's κ_card ½, so every card's content corner is 2q.
- Nesting at f: the child has depth (1 − f)·d and radius R − f·d, so depth is conserved.
- No radius is negative or larger than half its box.
- Grid: N·w + (N − 1)·G + 2M = W.
- Focus ring outer radius = r + o + w. A border leaves R − b and d − b inside.
- A target never shrinks the box: expansion = max(0, (T − h)/2).
- Crisp: at every n, I and g_c snap to whole px and S to even px (at 16px: S 24, I 8, h 40), and depths and gaps snap to whole px. Only radii may land on half px at odd q. Set `crisp: false` for exact q.
- Elevation: blur_k = β·y_k. Σα_k = B at every level and every L. α falls with k, so the contact layer is the darkest. Layer k_a sits at e.y·s.

## Tiers

Four tiers, each with its own constants and κ. A tier reads only the named values from the tier below it, so any tier can be fitted, tuned or adopted on its own. `unit` (F, q, type, b) is shared input. A preset may give a tier its own unit in `units`.

| Tier | Members | Owns | Reads | Concentric chain |
|---|---|---|---|---|
| 1 controls | button, input, select, chip, marks, icons | q, I, S, h, κ_control | — | r → r − m_c → r − I |
| 2 collections | listbox, menu, segmented, flush list, table, inset list, toolbar | items h − 2d_c (menus, segments) in a d_c = ¾q inset; rows h with an r outline (lists, tables); κ_frame | h, r(κ), T | r_f = min(r, soft) → item r_f − d_c |
| 3 containers | card, dialog (1½d), popover (¾d), panel (a card at 2I) | d by density, κ_card, nesting, elevation | r(κ), content edge | R = d + min(r(κ_card), soft) → R − f·d |
| 4 layout | page, grid, region, section | M = 4I, G = M/2, columns, breakpoints | minimum card width | — |

A control in a card reads κ_control, never the card's R. Two tiers share one chain only when their κ are equal. `derive.mjs` tags every length with its tier; `--tier <name>` prints one.

## Fitting a project

To find the system an existing project follows, read `references/fit.md`. In short: collect lengths from the rendered components (`scripts/collect.js` in the page) or from tokens, run `node scripts/fit.mjs lengths.json --md report.md --preset-out fitted.json --html compare.html`, check the result, then report per tier and show the before/after canvas. The fitted preset runs through `derive.mjs --preset fitted.json` like any other.

## Files

Paths are relative to this file's folder. Run the calculator by its full path from any working directory.

- `references/equations.md`: every equation, worked at n = 14 with the massimo preset, including marks, tracks, rows and floating widths (4b), grid (8), elevation (9), focus rings (10), hit targets (11), borders and snapping (12), text centring (13), fluid scale and breakpoints (14), measure (15), media and avatars (16), icon stroke (17), tiers and fitting (18) and the container spacing ladder (19).
- [references/showcase.md](references/showcase.md): optional default brief for a static 24-pattern component bento; read when asked for a showcase. Supplies content and geometry requirements for a renderer, without extending this skill into component implementation.
- `references/fit.md`: fitting a project: the tiers, the lengths.json roles, how the unit and κ are inferred, the report template and the canvas.
- `scripts/derive.mjs`: the calculator and its presets. `scripts/derive.test.mjs` asserts the identities (`node --test`).
- `scripts/fit.mjs`: the fitter (report, fitted preset, before/after page). `scripts/collect.js`: the in-page length collector. `scripts/fit.test.mjs` tests both against massimo and a Tailwind-like project.
