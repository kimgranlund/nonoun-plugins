# Fitting a project

Use this to analyse an existing project: find the nearest geometry system its components already follow, write it in this skill's notation, and show the difference side by side. The fit runs per tier, so a project can match on controls and not on cards, and adopt one tier at a time.

## The four tiers

| Tier | Members | Owns | Reads from below |
|---|---|---|---|
| 1 controls | buttons, inputs, selects, chips, toggles, marks, icons in controls | q, I, S, h, κ_control, icons, focus, targets | nothing |
| 2 collections | listboxes, menus, segmented controls, lists, tables, toolbars, tabs | row, d_c, r_frame (κ_frame), row gaps | h, and r(κ) through κ_frame |
| 3 containers | cards, dialogs, popovers, panels, sheets | d, R (κ_card), nesting, card gaps, elevation | r(κ) through κ_card, the content edge |
| 4 layout | pages, grids, regions | G, M, columns, breakpoints, measure | the minimum card width |

`unit` (F, q, the type scale, b) is shared input, not a tier. A tier may run on its own unit (`units.<tier>` in a preset) when the project genuinely does; the fit decides that, never the agent.

## Steps

1. **Pick the specimens.** One or two of each: the primary button, a text input, a menu or listbox with its items, a segmented control, a card, the page grid. List the primary control first: ties in the fit go to the first listed.
2. **Collect the lengths.** Two sources, and prefer the rendered one when they disagree, because that is what ships:
   - Rendered: open the project in a browser at a desktop width (kits change sizes at breakpoints), evaluate `scripts/collect.js` in the page, then call `uiGeometryCollect(spec, { source })` with a spec of `{ id, kind, selector, item? }` (kinds: control, group, frame, host, card, layout, mark). List one control per size (sm, default, lg), the default first. It returns `lengths.json`. Save it.
   - A tab list or segmented control is a `host` (joined controls), not a `frame`: its padding is d_c = (h − item)/2 and its segments are items of h − 2d_c, like menu rows. A menu, listbox or popover list is a `frame`.
   - Tokens: read the theme (CSS custom properties, a Tailwind config, a tokens file) and write the same shape by hand. Use this when nothing renders, and to name where a rendered value came from.
3. **Fit.** `node scripts/fit.mjs lengths.json --md report.md --preset-out fitted.json --html compare.html`. Add `--preset <file.json>` to compare against a system other than the standard preset.
4. **Read the result before reporting it.** Check that the unit is plausible (the runners-up are listed), that each tier's constants look like the components, and that every ✗ identity is a real property of the project and not a wrong selector.
5. **Report** using the template below, and render `compare.html` (or publish it) so the user sees the specimens before and after.
6. **Mind odd q.** Targets use the crisp preset (I, g_c, S on whole px). At odd q (16px gives q = 5) crisp lengths sit off exact q multiples, so the unit search may also report 2.5px or 4px as close fits; read the runners-up.
7. **Iterate.** `node scripts/derive.mjs --preset fitted.json --n <n>` prints the whole fitted system; `--tier <tier>` prints one tier. To try a variant, edit `fitted.json` (a κ, a depth, an inset) and run derive again.

## lengths.json

```json
{ "source": "acme web", "n": 16, "lengths": [
  { "id": "button.height", "role": "height", "px": 40 },
  { "id": "menu.row", "role": "row", "px": 36, "tier": "collections" },
  { "id": "card.padding", "role": "card-depth", "px": 24, "n": 16 }
] }
```

- `n` is the control text size in px (the font size of the primary button), not the document's root font size, when they differ.
- `tier` defaults from the role. `n` on a length tags another scope; with two or more scopes the fit solves q = a_q·n + b_q, otherwise it keeps the preset's slope a_q.
- Paddings include the border (the system measures depth from the outer edge, and d − b is inside). Record the border a padding includes as `border` (the collector does). Only a recorded border is ever taken off; without the field none is assumed, because ¼q paddings (a ¾q frame) sit off the ½q grid by design.

<!-- generated:roles -->
| Role | Tier | Compared with |
|---|---|---|
| height | controls | h = S + 2I |
| label-inset | controls | T = 2I |
| inset | controls | I (not collected) |
| icon | controls | the nearest icon size |
| radius | controls | r(κ_control) |
| control-gap | controls | the nearest of 0, g_c, m_c, min(cap, I) |
| mark | controls | itself, snapped to q/2 |
| row | collections | h at the nearest density |
| row-radius | collections | r_frame − d_c, or r when the frame has no radius |
| frame-depth | collections | d_c |
| frame-radius | collections | r_frame = min(r(κ_frame), soft) |
| row-gap | collections | the nearest of 0, g_c, the level gutter |
| cell-inset | collections | I (table cells) (not collected) |
| item-inset | collections | T − d_c (menu and listbox rows, text at T) |
| cell-control | collections | the item height h − 2d_c (not collected) |
| host-height | collections | h |
| host-depth | collections | (h − item)/2 = d_c |
| host-radius | collections | r |
| segment | collections | the item height h − 2d_c |
| segment-radius | collections | r − d_c |
| card-depth | containers | d |
| card-radius | containers | d + min(r(κ_card), soft); 0 at κ_card 0 |
| card-gap | containers | the nearest of d/4, d/2 − I, d/2, d |
| gutter | layout | G = M/2 |
| margin | layout | M = ℓ_page·I |
| hosted-control | controls | the item height h − 2d_c (not collected) |
| inline-control | controls | h_o = S + 2g_c (not collected) |
| focus-ring | controls | w (not collected) |
| popup-offset | collections | d_c (not collected) |
| field-gap | collections | 2I, as table columns (not collected) |
| label-gap | collections | g_c (not collected) |
| popover-depth | containers | d_p = popoverRatio·d, snapped to q/2 (not collected) |
| dialog-depth | containers | d_d = dialogRatio·d, snapped to q/2 (not collected) |
| title-gap | containers | max(0, d/2 − I) (not collected) |
| section-pad | layout | flow.section·F = 3¼F (not collected) |
<!-- /generated:roles -->

Any other role is snapped to the nearest q/2 of its tier.

## What the fit does

1. **Unit.** A length is on the grid of q when it is a multiple of q/2 within ¼px. Every divisor of a unit also catches its lengths (a 2px unit catches any whole px), so each candidate scores hit(q) − ¼·|ln(q / prior)|, the prior being the preset's q at n. A stray length or two costs a little hit rate, not the unit. The runners-up are reported. The shared q is fitted on the controls tier, which owns it.
2. **Borders.** A padding (label inset, frame depth, card depth) that is on the grid only once its border is taken off is read without it, and named: the project's padding does not absorb its border, where the system's depth includes it (d − b inside).
3. **Own units.** A tier with at least three lengths gets its own unit only when the shared q puts fewer than 75% of them on the grid and its own q puts at least 25 points more.
4. **Constants.** Each constant is the most frequent measured value of its role. For controls, each component with a height and a label inset gives a size: I = label-inset / 2 (or inset) and S = h − 2I. Sizes that keep the slot are densities (the first listed is the default, a smaller I compact, a larger loose), and each control is compared at its own density. A size with another S is named in the notes. Then κ for each tier by inverting r(κ): κ = κ_s·r/soft up to soft, then κ_s + (1 − κ_s)(r − soft)/(h/2 − soft), and 1 at h/2. A card's κ comes from R − d.
5. **Fitted preset.** The constants in q, snapped to q/2, with h snapped first so h = S + 2I holds exactly. It carries `dials` (κ per tier, card depth, density) so derive reproduces it without flags.
6. **Targets.** Every length gets two: the fitted system (the project's own system made consistent, so it moves only what breaks an identity or the grid) and the reference preset at the project's n, with the nearest density and card depth and the fitted κ.
7. **Identities.** The slot holds the icon; h meets the pointer target; every size keeps the slot; segments fill the host (h_o = h − 2m_c) and are concentric with it (r − m_c); r_row = r_frame − d_c; every row is a control height; R − d = min(r, soft) and is not negative; card gaps on the d ladder; M a whole multiple of I.

The report follows its notation with an **Archetype** line: h/F, and the three nearest archetypes by n, h/F and control curvature (`references/equations.md` › 20). Those are the only observables a fit has, so near ones are separated by the page's text and image coverage, not by the fit.

## Report template

1. **Verdict, one line per tier.** "Controls follow q = 4px with I = 2q (88% at the fitted target). Cards are not concentric: R 12px is less than d 24px."
2. **Unit.** q, the expression, and the runners-up.
3. **Notation.** For each tier, its constants as symbol = expression = multiple of q = px.
4. **Identities.** Each ✗ with the measured values and the one-line fix in symbols.
5. **Changes.** The outliers only: id, px, the fitted value, the preset value.
6. **Adoption.** Which tiers can move to the fitted system, or to the preset, without touching the others: a tier is independent of the tiers above it, and depends only on what it reads from below.

## The canvas

`compare.html` is standalone, in the light and dark schemes. Each tier is a section; each component is a row of three specimens drawn with the measured px, the fitted system and the reference preset, with the changed lengths listed under each. To build a richer canvas (a design artifact or a bento), use `references/showcase.md` for the specimens and feed it the `fitted` and `preset` values from `fit.mjs --json`, one board per target, laid out side by side.

## Worked example

shadcn/ui dashboard-01 (new-york-v4) at 1440px, n = 14: q = 4px. Its button sizes are densities: S = 20px = 5q at every size, I = 1.5q (sm, h 32) and 2q (default, h 36), the same slot as the standard preset. Its tab list pads 3px, exactly the standard preset's frame padding d_c = ¾q; the segments inside are 29px where h − 2d_c gives 30, and their 8px corners miss the concentric r − d_c = 9 by a pixel. Sidebar rows are h at the sm density (32px); table rows (53px) are not a control height. It departs in four places: paddings do not absorb their 1px borders (17, 13, 25px), cards are less round than their padding (R 14px < d 24px, so nothing inside a card can be concentric with it), the card grid gutter is 16px where G = M/2 gives 12, and table rows hold 32px controls with 8px padding instead of hosting items. Layout margin fits: M = 6q.
