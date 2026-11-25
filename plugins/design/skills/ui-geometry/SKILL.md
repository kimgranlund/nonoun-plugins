---
name: ui-geometry
description: Derives every length of a UI as a line in a root font size n, by one unit q or exact lines, in four tiers (controls, collections, containers, layout). Covers insets, slots, control heights, icons, type scale, marks and rows, frames, curvature κ with concentric radii, focus rings, hit targets, borders, pixel snapping, fluid scale, breakpoints, measure, elevation shadows, control gaps and page grids. Holds measured archetypes (editorial, fashion, instrument, product, marketing, civic, calm, toy, terminal) with dials. Also fits an existing project's components to the nearest system and archetype. Ships unit and exact presets. Use for "what is h at 16px", "radius at κ 0.4", "grid columns at 1280", "a soft 5-layer shadow", "define a size system", "make it feel editorial", "what system does this app use", "fit our components", or the geometry a showcase must follow. NOT for colour (ui-colors), paint or materials (ui-materials), the showcase canvas (ui-showcase-bento), implementing components, typefaces or motion.
---

# UI geometry

Every length is a line a·n + b px. One input, the scope font size n in px, and four dials: density δ, curvature κ (one each for controls, frames, cards and panels), card depth d, and a preset. A unit preset makes each a multiple of one unit q, snapped to whole px by default (crisp); an exact preset gives each constant its own line and rounds nothing (› 21). Answer in symbols and multiples of q first, then px at n. The default preset is **ladder** (q = ¾n − 6.75, so h = 8q = 6n − 54: 30px controls at 14, 24 at 13, 36 at 15, 48 at 17, 60 at 19); **standard** (q = n/2 − 3, h = 32 at 14, alias `standard-32`) is the other shipped preset, and the one the worked values in `references/equations.md` and the archetypes use. Every equation takes any preset's constants.

Contents: [Route](#route) · [Axioms](#axioms) · [Presets](#presets) · [Procedure](#procedure) · [Identities](#identities) · [Tiers](#tiers) · [Fitting a project](#fitting-a-project) · [Commands](#commands) · [Files](#files)

## Route

Read the row whose question is open. Paths are relative to this file.

| Question | Read | Load when |
|---|---|---|
| What is a length (h, r, a gap, a card corner) at n, density or κ? | `scripts/derive.mjs` (Procedure step 3), then `references/equations.md` at its section | Always for a number; read the section only to explain or extend it |
| What do a container's padding, gap and radius come to, inside out? | `node scripts/derive.mjs --containers`; `references/equations.md` › 19 | Laying out a card, menu, list, table, form, dialog or page |
| What does a symbol or term mean here? | `references/terms.json` | A symbol or word could be read two ways, or a sibling skill uses it |
| Which system does an existing project follow? | `references/fit.md` | Fitting, auditing or comparing a project's lengths |
| What must a showcase show, and at which lengths? | `references/showcase.md` | Asked for a showcase; the canvas and packing belong to ui-showcase-bento |
| Which archetype is a preset or a page, or what are an archetype's dials? | `node scripts/derive.mjs --archetype <name>`; `references/archetypes.json`; `references/equations.md` › 20 | Asked for a named character (editorial, fashion, an instrument), or classifying a fitted project |
| Which archetype is a rendered page? | `node scripts/observe.mjs <url or file>` (needs Playwright), or evaluate `scripts/observe.js` in the page and score the result with `node scripts/archetypes.mjs observed.json` (the nearest archetype, its family, and the page's position on the measured dimensions); `references/equations.md` › 20 | Asked what an existing page or kit reads as, or to compare a build with an archetype |
| How do I define another system? | Presets, below, and `PRESETS.standard` in `scripts/derive.mjs` | Writing a preset file; unknown keys are refused |
| Which lengths are whole px unrounded; what line is each? | `derive.mjs --whole`, `--lines`, `--emit css`, `--preset affine`; `references/equations.md` › 21 | A system must not round, or its constants share no unit |


## Axioms

1. **Line and unit.** F = n. A length is a line a·n + b: a multiple of q = a_q·n + b_q, or its own line in an exact preset. A nested scope with its own n′ restarts the whole system.
2. **Inset.** I_δ is one value per density. Density reaches spacing only through I.
3. **Control.** g_c is the fixed gutter, m_c = I − g_c the margin, S the slot, h = S + 2I the height.
4. **Frames.** A card has a depth d from a ladder that moves depthStep·ΔI per density step (the preset's `spacing.depthStep`; 2·ΔI = one q in the standard preset: 3q, 4q, 5q), so cards grow with their contents; popover and dialog follow at ¾d and 1½d. A panel of controls is a card at d = 2I. A page section shares the page edge and pads only above and below. Segmented hosts and control frames (menu, listbox) both pad d_c = ¾q around items h − 2d_c, so one item plus its padding is exactly h.
5. **Curvature.** κ ∈ [0, 1] is set per dial: control, frame, card and panel (the `--kappa-*` flags). Layout has no curvature. Radii are concentric within a tier, and the chain restarts at a tier boundary.
6. **Spacing.** Every gap is a row of the gap table (`references/equations.md` › 7). The main ones: the full padding p (the depth d in a card) between groups, under a header and before actions, half of it (p/2) between blocks inside a group, the label inset 2I between form fields and table columns, I under a group caption, g_c under a field label and between parts that belong together, or 0 between joined parts. Three label levels, three gaps. Text sits at T = 2I from the edge of every control, menu, list and table, so text in a stack lines up.
7. **Floors.** Hit targets and the reading measure are set in px and characters, not q. The geometry is checked against them, never scaled to fit them.
8. **Elevation.** A shadow is L layers in a geometric series. A level scales their lengths, never their alpha, so a higher level casts a wider halo, not a darker one.
9. **Tiers.** Controls, collections, containers and layout each own their constants. A tier reads only the values its row of the Tiers table names, all from tiers below it, so each can be fitted, tuned or adopted alone.

## Presets

A preset fixes the constants. The equations never change. **ladder** is standard on another unit, every other constant shared:

| Constant | Meaning | standard |
|---|---|---|
| a_q, b_q | unit q = a_q·n + b_q (preset key `unit.a`, `unit.b`) | ½, −3 (q = 4px at 14); ladder ¾, −6.75 (q = 3.75px, h = 30 at 14) |
| I_δ | inset by density | 1 / 1.5 / 2 |
| g_c | control gutter | ½ |
| S | slot | 5 |
| soft, κ_s | radius at the soft anchor, and its κ | 3, ¾ |
| d_c, frame row | padding of menus, listboxes and segmented hosts (a number in q, g_c or m_c) and their item height (fit: h − 2d_c; m_c: S + 2m_c; h_o; h) | ¾, fit |
| card depths | card depth ladder | 0…9 |
| ℓ | level multipliers of I: composite, group, collection, panel (region band), page | ½, 1, 2, 2, 4 |
| flow | the gaps down a page section, in body sizes F: kicker, heading, paragraph, actions, note; section padding | 1, 1¼, 1¼, 2½, 1; 3¼ |
| icons | sm (tethered to the text size F), md, lg, full (= S) | F, 4, 4.5, 5 |
| type (m_t, k_t) | size F + m_t·q, line size + k_t·q | see `references/equations.md` |
| e.y, ρ, k_a, β, σ, θ | elevation: key offset, layer ratio, anchor layer, blur ratio, spread ratio, light angle | 1, 2, 2, 2, 0, 0° |
| L, λ, B_α | layers, alpha decay, alpha budget (light / dark) | 4, ¾, 0.19 / 0.45 |
| s | elevation levels: raised, popup, floating, modal | ½, 1, 1½, 2 |
| w, o | focus ring width and offset | ½, ½ |
| T_hit | hit targets, pointer / touch (px) | 24 / 44 |
| b | border (px) | 1 |
| A_f, D_f, c_f, w̄ | font ascent, descent, cap height, average advance (em) | 0.969, 0.242, 0.727, 0.5 |
| fluid | n(W) endpoints, step, align | (360, 14) → (1440, 16), step 2 |
| units, dials | optional: a unit per tier; default κ per tier, card depth and density | dials: κ_card ½ |
| spacing | popover and dialog depth as ratios of d, nesting f | ¾, 1½, ½ |
| measure, aspects, avatars, ρ_s | characters per line, ratios, avatar ladder, icon stroke ratio | 45 / 66 / 75; 1:1 … 21:9; 4, 5, 6, 8, 10, 20; 3/32 |

An archetype is a profile, not a preset: the band its measured pages fall in, per observable (`references/archetypes.json`; `references/equations.md` › 20). A preset or a fitted page is scored by its distance outside the bands. Its `dials` give an n, a density and a κ inside the bands a preset can reach. Checked: "every archetype's dials hold the identities, land the control on whole px and put h/F inside its band".

To define another system, write a JSON file with any of the keys from `PRESETS.standard` in `scripts/derive.mjs`, plus `name`, `units`, `crisp` or `dials`. Keys left out default to the standard preset. Any other key is refused with a "did you mean" (`validatePreset`; tested in `scripts/knowledge.test.mjs`).

## Procedure

1. Fix the preset, n, δ, κ for each tier and d. The defaults are ladder (the CLI's default; `--preset standard` for the 32px system, which an `--archetype` starts from), δ = default, κ = κ_s for controls, lists and panels, κ = ½ for cards (so R = d + 2q at default density), and d = 4.
2. Compute q, I, m_c and h. Then compute the tier that is asked for, from `references/equations.md`.
3. For a full table, run `node scripts/derive.mjs --n <n> --density <δ> --kappa <κ>`. Add `--kappa-control`, `--kappa-frame`, `--kappa-card` or `--kappa-panel` to split tiers. Use `--card <d>`, `--width <px> --columns <N>` for a grid, `--preset <file.json>` for another system, `--archetype <name>` to start from an archetype's dials and print its bands, and `--json` for data. `--viewport <px>` takes n from the fluid scale; `--dpr <x>` lists lengths off the device grid. For every container's padding, gap and radius run `--containers [--card 4 --nest 0.5]` (section 19; `--popover`/`--dialog` fix those depths). For shadows run `--elevation <level|s|all> [--layers 5] [--scheme dark]`. The file's header lists every flag.
4. Check that the identities below hold. A value that breaks one is wrong.
5. Report a table with the columns symbol, expression, q, px. Flag any px that falls off the whole-pixel grid.

## Identities

- h = S + 2I. m_c + g_c = I. The inline height is h_o = h − 2m_c = S + 2g_c. Menu rows and segments are items of h − 2d_c (26 at 14px with d_c = ¾q), so one item padded d_c is h. Checked: `checkIdentities()` in "identities hold at every density", with a mutated table that must fail.
- Text sits at T = 2I in a control, a menu row (d_c + (T − d_c)), a list row and a table's edge cell. One left edge: headings, captions, loose text, shapes and unframed marks (checkbox, radio, switch) all start on the content edge. Text inside a shape sits at T; a field label sits at T over its control's value, and so does a group caption over shapes that hold text (a wrapper padded T, `references/equations.md` › 4b). Checked: "one left edge" and "menu and listbox text sits at T".
- An icon of size a sits I + (S − a)/2 from the control edge. A label sits 2I in, or 2I + S after a leading icon. Built without wrappers: padding 2I at a text edge and I at an icon edge, an S-square icon box, a gap I. Checked: "controls pad by edge".
- r(0) = 0, r(κ_s) = soft, r(1) = h/2. r is continuous and monotonic. Checked: "curvature passes through square, soft and pill" and "curvature is continuous, monotonic and never above h/2".
- For a card at d > 0 and κ_card > 0, R − d = min(r(κ_card), soft) (at κ_card 0 the card is square, R = 0): 2q at the standard preset's κ_card ½, so every card's content corner is 2q. Checked: "standard cards default to κ ½".
- Nesting at f: the child has depth (1 − f)·d and radius R − f·d, so depth is conserved. Checked: "nesting keeps the parent curve".
- No radius is negative or larger than half its box. Checked: "chains never go negative at square".
- Mixed corners stay at or under h/2, or the browser scales all of them and a small one renders square (`references/equations.md` › 5; runs › 7). Measure the rendered shape.
- Grid: N·w + (N − 1)·G + 2M = W. Checked: "grid columns fill the width exactly".
- Grid for several counts: margin = gutter = g·u, u = W / (U + 2g); n columns when n divides U + g (`--field`, `references/equations.md` › 8). Checked: "every listed count fills the field in whole units".
- Focus ring outer radius = r + o + w. A border leaves R − b and d − b inside. Checked: `checkIdentities()`, "focus ring" and "borders eat padding and radius".
- A target never shrinks the box: expansion = max(0, (T_hit − h)/2). Checked: "hit targets".
- Ladder: crisp h = 6n − 54 at n 12, 13, 14, 15, 17 and 19 (18 … 60), h = S + 2I. Checked: "ladder (the default)", with standard at 14 as the negative control.
- Crisp: at every n, I and g_c snap to whole px and S to even px, and depths and gaps snap to whole px. Radii may land on half px at odd q. Set `crisp: false` for exact q. Checked: "crisp: at 16px every padding, gap and height is a whole px".
- Lines and exact presets (› 21). Checked: "affine: every source line is derived" and "wholeness: affine, with unit presets as negative controls".
- Elevation: blur_k = β·y_k. Σα_k = B_α at every level and every L. α falls with k, so the contact layer is the darkest. Layer k_a sits at e.y·s. Checked: the five "elevation" tests.
- Gaps: inside a padded container no gap exceeds its largest padding. Checked: "no gap exceeds its container's padding".

## Tiers

Four tiers, each with its own constants and κ. A tier reads only the named values from the tiers below it, so any tier can be fitted, tuned or adopted on its own. Checked: "a tier's Reads column names every symbol it takes from another tier". `unit` (F, q, type, b) is shared input. A preset may give a tier its own unit in `units`.

| Tier | Members | Owns | Reads | Concentric chain |
|---|---|---|---|---|
| 1 controls | button, input, select, chip, marks, icons | q, I, S, h, κ_control | — | r → r − m_c → r − I |
| 2 collections | listbox, menu, segmented, flush list, table, inset list, toolbar | items h − 2d_c (menus, segments) in a d_c = ¾q inset; rows h with an r outline (lists, tables); κ_frame | h, r(κ), T | r_f = min(r, soft) → item r_f − d_c |
| 3 containers | card, dialog (1½d), popover (¾d), panel (a card at 2I) | d by density, κ_card, nesting, elevation | r(κ), content edge | R = d + min(r(κ_card), soft) → R − f·d |
| 4 layout | page, grid, region, section | M = 4I, G = M/2, columns, breakpoints; the flow gaps and section padding, in F | I, F, minimum card width | — |

A control in a card reads κ_control, never the card's R. Two tiers share one chain only when their κ are equal. `derive.mjs` tags every length with its tier; `--tier <name>` prints one.

## Fitting a project

To find the system an existing project follows, read `references/fit.md`. In short: collect lengths from the rendered components (`scripts/collect.js` in the page) or from tokens, run `node scripts/fit.mjs lengths.json --md report.md --preset-out fitted.json --html compare.html`, check the result, then report per tier and show the before/after canvas. The fitted preset runs through `derive.mjs --preset fitted.json` like any other.

## Commands

Run from this folder. Done means all three are green.

- `node --test scripts/`: the identities, the calculator, the fitter, terms and the generated blocks.
- `node scripts/docs.mjs --check`: the generated tables in `references/` match their sources (`node scripts/docs.mjs` rewrites them).
- `node scripts/terms.mjs --check`: every symbol and role the scripts emit has one entry in `references/terms.json`, and no doc uses a phrase it bans outright (`avoidExact`).

## Files

Paths are relative to this file's folder. Run the calculator by its full path from any working directory.

- `references/equations.md`: every equation in numbered sections 1 to 21, worked at n = 14 with the standard preset; 19 is the container ladder, 20 the archetypes, 21 lines and exact presets.
- `references/showcase.md`: the content and geometry a showcase must follow. ui-showcase-bento owns the canvas, packing and checks.
- `references/fit.md`: fitting a project: the tiers, the lengths.json roles (a generated table), how the unit and κ are inferred, the report template and the canvas.
- `references/terms.json`: the symbols and words of this skill, one meaning each, with how the sibling skills use the same words.
- `scripts/derive.mjs`: the calculator and its presets. `scripts/derive.test.mjs` asserts the identities (`node --test`).
- `references/dimensions.json`: the nine dimensions measured pages vary along, six of them named, with each archetype's mean on each. `scripts/dimensions.mjs` gives a measured page its position on them (`node scripts/dimensions.mjs observed.json`); `scripts/dimensions.test.mjs` checks it.
- `references/archetypes.json`: the archetypes as profiles (family, stance, bands, signature, dials), with each observable's meaning and scale. `scripts/archetypes.mjs` scores a preset or values against them; `scripts/archetypes.test.mjs` checks the file and the dials.
- `scripts/observe.js`: the in-page observer; one evaluation returns 63 of the 72 observables. `scripts/observe.mjs` runs it in Playwright, adds the nine that need a screenshot or a second load, and prints the archetype ranking. `scripts/observe.test.mjs` keeps the observer's names in step with `references/archetypes.json`.
- `scripts/docs.mjs`: writes and checks the generated tables. `scripts/terms.mjs`: checks `terms.json` against what the scripts emit.
- `scripts/fit.mjs`: the fitter (report, fitted preset, before/after page); `ROLES` is the one list of length roles. `scripts/collect.js`: the in-page length collector. `scripts/fit.test.mjs` tests both against the standard preset and a Tailwind-like project.
