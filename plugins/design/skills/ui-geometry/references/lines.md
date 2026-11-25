# Every length as a line

Each row of `node scripts/derive.mjs` at default density and κ, as the line a·n + b px it follows from n = 14 (sampled at 14, 16 and 18): the standard and ladder presets with snapping off (`crisp: false`), and the affine preset, which never snaps. "not a line here" marks a row that crosses a floor, a cap or a maximum at those sizes; "—" a row the preset does not print. A card depth is `card-4` (4q) in the unit presets and `card-d` (the slot) in affine, so those rows sit apart. The table is generated: `node scripts/docs.mjs` rewrites it and `--check` fails on drift. `references/equations.md` holds the equations themselves; section 21 explains lines and exact presets.

<!-- generated:every -->
| Row | Expression | standard | ladder | affine |
|---|---|---|---|---|
| `unit.scale.f` | n | n | n | n |
| `unit.scale.q` | 0.5·n − 3 | 0.5n − 3 | 0.75n − 6.75 | 1 |
| `unit.type.display-lg` | F + 12.5q | 7.25n − 37.5 | 10.375n − 84.375 | 4n − 18 |
| `unit.type.display-lg-line` | size + 1q | 7.75n − 40.5 | 11.125n − 91.125 | 5n − 24 |
| `unit.type.display-md` | F + 8.5q | 5.25n − 25.5 | 7.375n − 57.375 | 4n − 26 |
| `unit.type.display-md-line` | size + 1q | 5.75n − 28.5 | 8.125n − 64.125 | 5n − 34 |
| `unit.type.display-sm` | F + 5.5q | 3.75n − 16.5 | 5.125n − 37.125 | 4n − 34 |
| `unit.type.display-sm-line` | size + 1q | 4.25n − 19.5 | 5.875n − 43.875 | 5n − 44 |
| `unit.type.heading-lg` | F + 4q | 3n − 12 | 4n − 27 | 2n − 4 |
| `unit.type.heading-lg-line` | size + 1.5q | 3.75n − 16.5 | 5.125n − 37.125 | 3n − 10 |
| `unit.type.heading-md` | F + 2.5q | 2.25n − 7.5 | 2.875n − 16.875 | 2n − 8 |
| `unit.type.heading-md-line` | size + 1.5q | 3n − 12 | 4n − 27 | 3n − 16 |
| `unit.type.heading-sm` | F + 1.5q | 1.75n − 4.5 | 2.125n − 10.125 | 2n − 10 |
| `unit.type.heading-sm-line` | size + 1.5q | 2.5n − 9 | 3.25n − 20.25 | 3n − 18 |
| `unit.type.title-lg` | F + 0.75q | 1.375n − 2.25 | 1.563n − 5.063 | n + 4 |
| `unit.type.title-lg-line` | size + 1q | 1.875n − 5.25 | 2.313n − 11.813 | 2n − 2 |
| `unit.type.title-md` | F + 0.25q | 1.125n − 0.75 | 1.188n − 1.688 | n + 2 |
| `unit.type.title-md-line` | size + 1q | 1.625n − 3.75 | 1.938n − 8.438 | 2n − 6 |
| `unit.type.title-sm` | F + 0q | n | n | n |
| `unit.type.title-sm-line` | size + 1q | 1.5n − 3 | 1.75n − 6.75 | 2n − 10 |
| `unit.type.body-lg` | F + 0.5q | 1.25n − 1.5 | 1.375n − 3.375 | n + 2 |
| `unit.type.body-lg-line` | size + 1.5q | 2n − 6 | 2.5n − 13.5 | 2n − 4 |
| `unit.type.body-md` | F + 0q | n | n | n |
| `unit.type.body-md-line` | size + 1.5q | 1.75n − 4.5 | 2.125n − 10.125 | 2n − 8 |
| `unit.type.body-sm` | F + -0.25q | 0.875n + 0.75 | 0.813n + 1.688 | n − 2 |
| `unit.type.body-sm-line` | size + 1.5q | 1.625n − 3.75 | 1.938n − 8.438 | 2n − 12 |
| `unit.type.label` | F + -0.5q | 0.75n + 1.5 | 0.625n + 3.375 | n − 2 |
| `unit.type.label-line` | size + 1q | 1.25n − 1.5 | 1.375n − 3.375 | 2n − 10 |
| `unit.type.kicker-lg` | F + 0q | n | n | n |
| `unit.type.kicker-lg-line` | size + 0.5q | 1.25n − 1.5 | 1.375n − 3.375 | 2n − 8 |
| `unit.type.kicker-md` | F + -0.5q | 0.75n + 1.5 | 0.625n + 3.375 | n − 2 |
| `unit.type.kicker-md-line` | size + 0.5q | n | n | 2n − 10 |
| `unit.type.kicker-sm` | F + -1q | 0.5n + 3 | 0.25n + 6.75 | n − 4 |
| `unit.type.kicker-sm-line` | size + 0.5q | 0.75n + 1.5 | 0.625n + 3.375 | 2n − 12 |
| `unit.type.code` | F + -0.25q | 0.875n + 0.75 | 0.813n + 1.688 | n − 2 |
| `unit.type.code-line` | size + 1.5q | 1.625n − 3.75 | 1.938n − 8.438 | 2n − 10 |
| `unit.border.b` | 1px | 1 | 1 | 1 |
| `unit.text.cap-offset` | (ascent − descent − cap)/2 · F (+ = cap centre below line centre) | −0n | −0n | −0n |
| `unit.text.label-line-box-in-s` | S − (F + q): half-leading room in the slot | n − 12 | 2n − 27 | n − 9 |
| `unit.text.heading-md-off-the-q-grid-by` | line height mod q | not a line here | not a line here | — |
| `unit.text.heading-sm-off-the-q-grid-by` | line height mod q | not a line here | not a line here | — |
| `unit.text.title-lg-off-the-q-grid-by` | line height mod q | not a line here | not a line here | — |
| `unit.text.title-md-off-the-q-grid-by` | line height mod q | −0.375n + 8.25 | not a line here | — |
| `unit.text.title-sm-off-the-q-grid-by` | line height mod q | not a line here | not a line here | — |
| `unit.text.body-lg-off-the-q-grid-by` | line height mod q | not a line here | not a line here | — |
| `unit.text.body-sm-off-the-q-grid-by` | line height mod q | −0.375n + 8.25 | not a line here | — |
| `unit.text.kicker-md-off-the-q-grid-by` | line height mod q | not a line here | not a line here | — |
| `unit.text.code-off-the-q-grid-by` | line height mod q | −0.375n + 8.25 | not a line here | — |
| `controls.control.i` | by density | 0.75n − 4.5 | 1.125n − 10.125 | n − 9 |
| `controls.control.m_c` | I − g_c | 0.5n − 3 | 0.75n − 6.75 | n − 9 |
| `controls.control.g_c` | 0.5 | 0.25n − 1.5 | 0.375n − 3.375 | 0 |
| `controls.control.s` | 5 | 2.5n − 15 | 3.75n − 33.75 | 2n − 8 |
| `controls.control.h` | S + 2I | 4n − 24 | 6n − 54 | 4n − 26 |
| `controls.control.h_o` | S + 2g_c | 3n − 18 | 4.5n − 40.5 | 2n − 8 |
| `controls.control.b` | h + 2 (title bar) | 5n − 30 | 7.5n − 67.5 | 4n − 24 |
| `controls.control.t` | 2I (text edge) | 1.5n − 9 | 2.25n − 20.25 | 2n − 18 |
| `controls.control.d` | I/2 (composite edge) | 0.375n − 2.25 | 0.563n − 5.063 | 0.5n − 4.5 |
| `controls.icon.a.sm` | 3.5 | n | n | n |
| `controls.icon.a.sm-offset` | I + (S − a)/2 | 1.5n − 12 | 2.5n − 27 | 1.5n − 13 |
| `controls.icon.a.md` | 4 | 2n − 12 | 3n − 27 | 1.5n − 4 |
| `controls.icon.a.md-offset` | I + (S − a)/2 | n − 6 | 1.5n − 13.5 | 1.25n − 11 |
| `controls.icon.a.lg` | 4.5 | 2.25n − 13.5 | 3.375n − 30.375 | 2n − 8 |
| `controls.icon.a.lg-offset` | I + (S − a)/2 | 0.875n − 5.25 | 1.313n − 11.813 | n − 9 |
| `controls.icon.a.full` | 5 | 2.5n − 15 | 3.75n − 33.75 | 2n − 8 |
| `controls.icon.a.full-offset` | I + (S − a)/2 | 0.75n − 4.5 | 1.125n − 10.125 | n − 9 |
| `controls.icon.label-after-icon` | 2I + S | 4n − 24 | 6n − 54 | 4n − 26 |
| `controls.icon.padding-at-a-text-edge` | T = 2I | 1.5n − 9 | 2.25n − 20.25 | 2n − 18 |
| `controls.icon.padding-at-an-icon-edge` | I | 0.75n − 4.5 | 1.125n − 10.125 | n − 9 |
| `controls.icon.icon-box-label` | I (flex gap; no wrapper, no collapsing margins) | 0.75n − 4.5 | 1.125n − 10.125 | n − 9 |
| `controls.icon.icon-only` | h × h | 4n − 24 | 6n − 54 | 4n − 26 |
| `controls.icon-stroke.a.sm` | max(1px, 0.09375·a) | 0.094n | 0.094n | 0.094n |
| `controls.icon-stroke.a.md` | max(1px, 0.09375·a) | 0.188n − 1.125 | 0.281n − 2.531 | 0.141n − 0.375 |
| `controls.icon-stroke.a.lg` | max(1px, 0.09375·a) | 0.211n − 1.266 | 0.316n − 2.848 | 0.188n − 0.75 |
| `controls.icon-stroke.a.full` | max(1px, 0.09375·a) | 0.234n − 1.406 | 0.352n − 3.164 | 0.188n − 0.75 |
| `controls.mark.choice-row` | h; the mark is the visible edge and starts on the content edge | 4n − 24 | 6n − 54 | 4n − 26 |
| `controls.mark.choice-label` | a + I + (S − a)/2 | 3n − 18 | 4.5n − 40.5 | 2.75n − 15 |
| `controls.mark.checkbox-box` | a.md | 2n − 12 | 3n − 27 | 1.5n − 4 |
| `controls.mark.checkbox-radius` | 1 | 0.5n − 3 | 0.75n − 6.75 | 0.375n − 1 |
| `controls.mark.radio-box` | a.md, round | 2n − 12 | 3n − 27 | 1.5n − 4 |
| `controls.mark.radio-dot` | a.md / 2 | n − 6 | 1.5n − 13.5 | 0.75n − 2 |
| `controls.mark.switch-track` | 7 × a.md, round | 3.5n − 21 | 5.25n − 47.25 | 3n − 12 |
| `controls.mark.switch-thumb` | a.md − 2g_c | 1.5n − 9 | 2.25n − 20.25 | 1.5n − 8 |
| `controls.mark.badge` | S | 2.5n − 15 | 3.75n − 33.75 | 2n − 8 |
| `controls.mark.badge-dot` | 2 | n − 6 | 1.5n − 13.5 | n − 9 |
| `controls.mark.separator` | hairline, g_c above and below | 0.25n − 1.5 | 0.375n − 3.375 | 0 |
| `controls.mark.tree-indent` | S per level | 2.5n − 15 | 3.75n − 33.75 | 2n − 8 |
| `controls.track.progress-slider-track` | 1 | 0.5n − 3 | 0.75n − 6.75 | 0.5n − 4 |
| `controls.track.meter-track` | 2 | n − 6 | 1.5n − 13.5 | n − 8 |
| `controls.track.slider-hit-area` | S | 2.5n − 15 | 3.75n − 33.75 | 2n − 8 |
| `controls.track.slider-thumb` | a.md, round | 2n − 12 | 3n − 27 | 1.5n − 4 |
| `controls.track.slider-minimum-length` | 10 | 5n − 30 | 7.5n − 67.5 | 8n − 42 |
| `controls.curvature.r` | r(κ) | 1.5n − 9 | 2.25n − 20.25 | n − 6 |
| `controls.curvature.r_o` | r − m_c | n − 6 | 1.5n − 13.5 | 3 |
| `controls.curvature.r_s` | r − I | 0.75n − 4.5 | 1.125n − 10.125 | 3 |
| `controls.border.control-inner-radius` | r − b | 1.5n − 10 | 2.25n − 21.25 | n − 7 |
| `controls.border.heavy-rule` | I | 0.75n − 4.5 | 1.125n − 10.125 | n − 9 |
| `controls.focus.ring-width-w` | 0.5 | 0.25n − 1.5 | 0.375n − 3.375 | 2 |
| `controls.focus.ring-offset-o` | 0.5 | 0.25n − 1.5 | 0.375n − 3.375 | 0 |
| `controls.focus.ring-outer-radius` | r + o + w | 2n − 12 | 3n − 27 | n − 4 |
| `controls.focus.ring-centre-radius` | r + o + w/2 | 1.875n − 11.25 | 2.813n − 25.313 | n − 5 |
| `controls.focus.clearance-needed` | o + w (each side; ≤ the gap to a neighbour) | 0.5n − 3 | 0.75n − 6.75 | 2 |
| `controls.focus.inset-ring-radius-hosted-option` | r_o − w/2, drawn inside | 0.875n − 5.25 | 1.313n − 11.813 | 2 |
| `controls.target.t_hit-pointer` | 24px | 24 | 24 | 24 |
| `controls.target.expansion-of-h-pointer` | max(0, (T_hit − h)/2) each side | 0 | 0 | 0 |
| `controls.target.expansion-of-h_o-pointer` | max(0, (T_hit − h_o)/2) each side | 0 | not a line here | not a line here |
| `controls.target.minimum-i-for-h-to-meet-t_hit-pointer` | (T_hit − S)/2 | −1.25n + 19.5 | −1.875n + 28.875 | −n + 16 |
| `controls.target.t_hit-touch` | 44px | 44 | 44 | 44 |
| `controls.target.expansion-of-h-touch` | max(0, (T_hit − h)/2) each side | not a line here | not a line here | not a line here |
| `controls.target.expansion-of-h_o-touch` | max(0, (T_hit − h_o)/2) each side | −1.5n + 31 | −2.25n + 42.25 | −n + 26 |
| `controls.target.minimum-i-for-h-to-meet-t_hit-touch` | (T_hit − S)/2 | −1.25n + 29.5 | −1.875n + 38.875 | −n + 26 |
| `controls.media.avatar-xs` | 4 | 2n − 12 | 3n − 27 | 1.5n − 4 |
| `controls.media.avatar-xs-radius` | r(κ_control) at size 4: min(r(κ)·size/h, size/2) | 0.75n − 4.5 | 1.125n − 10.125 | not a line here |
| `controls.media.avatar-sm` | 5 | 2.5n − 15 | 3.75n − 33.75 | 2n − 8 |
| `controls.media.avatar-sm-radius` | r(κ_control) at size 5: min(r(κ)·size/h, size/2) | 0.938n − 5.625 | 1.406n − 12.656 | not a line here |
| `controls.media.avatar-md` | 6 | 3n − 18 | 4.5n − 40.5 | 3n − 17 |
| `controls.media.avatar-md-radius` | r(κ_control) at size 6: min(r(κ)·size/h, size/2) | 1.125n − 6.75 | 1.688n − 15.188 | not a line here |
| `controls.media.avatar-lg` | 8 | 4n − 24 | 6n − 54 | 4n − 26 |
| `controls.media.avatar-lg-radius` | r(κ_control) at size 8: min(r(κ)·size/h, size/2) | 1.5n − 9 | 2.25n − 20.25 | n − 6 |
| `controls.media.avatar-xl` | 10 | 5n − 30 | 7.5n − 67.5 | 4n − 16 |
| `controls.media.avatar-xl-radius` | r(κ_control) at size 10: min(r(κ)·size/h, size/2) | 1.875n − 11.25 | 2.813n − 25.313 | not a line here |
| `controls.media.avatar-xxl` | 20 | 10n − 60 | 15n − 135 | 8n − 32 |
| `controls.media.avatar-xxl-radius` | r(κ_control) at size 20: min(r(κ)·size/h, size/2) | 3.75n − 22.5 | 5.625n − 50.625 | not a line here |
| `controls.media.avatar-in-slot-radius` | r − I (concentric with the control) | 0.75n − 4.5 | 1.125n − 10.125 | 3 |
| `controls.gap.joined` | 0 | 0 | 0 | 0 |
| `controls.gap.seam` | g_c each side | 0.25n − 1.5 | 0.375n − 3.375 | 0 |
| `controls.gap.hosted` | m_c | 0.5n − 3 | 0.75n − 6.75 | n − 9 |
| `controls.gap.grouped` | min(2, I) | 0.75n − 4.5 | 1.125n − 10.125 | n − 9 |
| `collections.rows.row` | h (read from controls) | 4n − 24 | 6n − 54 | 4n − 26 |
| `collections.rows.cell-inline-padding` | I | 0.75n − 4.5 | 1.125n − 10.125 | n − 9 |
| `collections.rows.cell-label` | ≥ S, one line | 2.5n − 15 | 3.75n − 33.75 | 2n − 8 |
| `collections.rows.control-in-a-table-cell` | item h − 2d_c, inset (h − item)/2 | 3.25n − 19.5 | 4.875n − 43.875 | 2n − 8 |
| `collections.rows.edge-cell-of-a-flush-table-or-list` | the parent depth (d in a card, M on a page) | 2n − 12 | 3n − 27 | 2n − 8 |
| `collections.rows.segment-tab` | the item height, inside an h-tall host | 3.25n − 19.5 | 4.875n − 43.875 | 2n − 8 |
| `collections.rows.menu-row` | h − 2d_c (one row + 2d_c = h) | 3.25n − 19.5 | 4.875n − 43.875 | 2n − 8 |
| `collections.frame.d_c` | 0.75 | 0.375n − 2.25 | 0.563n − 5.063 | n − 9 |
| `collections.gap.popup-offset-from-its-trigger` | d_c (the gap matches the padding inside the popup) | 0.375n − 2.25 | 0.563n − 5.063 | n − 9 |
| `collections.frame.host-pad` | (h − item)/2 | 0.375n − 2.25 | 0.563n − 5.063 | n − 9 |
| `collections.curvature.r_frame` | min(r(κ), soft) | 1.5n − 9 | 2.25n − 20.25 | n − 6 |
| `collections.curvature.r_row` | r_frame − d_c | 1.125n − 6.75 | 1.688n − 15.188 | 3 |
| `collections.width.tooltip` | 60 | 30n − 180 | 45n − 405 | 16n + 16 |
| `collections.width.popover` | 80 | 40n − 240 | 60n − 540 | 24n − 16 |
| `containers.curvature.r-card-0` | r(κ) | n − 6 | 1.5n − 13.5 | 2n − 15 |
| `containers.curvature.r-card-1` | d + min(r(κ), soft) | 1.5n − 9 | 2.25n − 20.25 | — |
| `containers.curvature.r-card-2` | d + min(r(κ), soft) | 2n − 12 | 3n − 27 | — |
| `containers.curvature.r-card-3` | d + min(r(κ), soft) | 2.5n − 15 | 3.75n − 33.75 | — |
| `containers.curvature.r-card-4` | d + min(r(κ), soft) | 3n − 18 | 4.5n − 40.5 | — |
| `containers.curvature.r-card-5` | d + min(r(κ), soft) | 3.5n − 21 | 5.25n − 47.25 | — |
| `containers.curvature.r-card-6` | d + min(r(κ), soft) | 4n − 24 | 6n − 54 | — |
| `containers.curvature.r-card-7` | d + min(r(κ), soft) | 4.5n − 27 | 6.75n − 60.75 | — |
| `containers.curvature.r-card-8` | d + min(r(κ), soft) | 5n − 30 | 7.5n − 67.5 | — |
| `containers.curvature.r-card-9` | d + min(r(κ), soft) | 5.5n − 33 | 8.25n − 74.25 | — |
| `containers.curvature.nest-f-0-in-card-4` | R − f·d | 0 | 0 | — |
| `containers.frame.nest-f-0-depth` | (1 − f)·d | 2n − 12 | 3n − 27 | 2n − 8 |
| `containers.curvature.nest-f-0.25-in-card-4` | R − f·d | 2.5n − 15 | 3.75n − 33.75 | — |
| `containers.frame.nest-f-0.25-depth` | (1 − f)·d | 1.5n − 9 | 2.25n − 20.25 | 1.5n − 6 |
| `containers.curvature.nest-f-0.5-in-card-4` | R − f·d | 2n − 12 | 3n − 27 | — |
| `containers.frame.nest-f-0.5-depth` | (1 − f)·d | n − 6 | 1.5n − 13.5 | n − 4 |
| `containers.curvature.nest-f-0.75-in-card-4` | R − f·d | 1.5n − 9 | 2.25n − 20.25 | — |
| `containers.frame.nest-f-0.75-depth` | (1 − f)·d | 0.5n − 3 | 0.75n − 6.75 | 0.5n − 2 |
| `containers.curvature.nest-f-1-in-card-4` | R − f·d | n − 6 | 1.5n − 13.5 | — |
| `containers.frame.nest-f-1-depth` | (1 − f)·d | 0 | 0 | 0 |
| `containers.curvature.r-panel-card-at-2i` | 2I + min(r(κ_card), soft) | 2.5n − 15 | 3.75n − 33.75 | 2n − 15 |
| `containers.frame.composite-inset` | 0.5·I | 0.375n − 2.25 | 0.563n − 5.063 | 0.5n − 4.5 |
| `containers.frame.group-inset` | 1·I | 0.75n − 4.5 | 1.125n − 10.125 | n − 9 |
| `containers.frame.collection-inset` | 2·I | 1.5n − 9 | 2.25n − 20.25 | 2n − 18 |
| `containers.frame.panel-inset` | 2·I | 1.5n − 9 | 2.25n − 20.25 | 2n − 8 |
| `containers.frame.page-inset` | 4·I | 3n − 18 | 4.5n − 40.5 | 4n − 26 |
| `containers.frame.dialog-inset` | d_d = 1.5·d | 3n − 18 | 4.5n − 40.5 | 4n − 26 |
| `containers.gap.groups-in-card-4` | d | 2n − 12 | 3n − 27 | — |
| `containers.gap.blocks-in-a-group-card-4` | d/2 | n − 6 | 1.5n − 13.5 | — |
| `containers.gap.group-caption-content` | I | 0.75n − 4.5 | 1.125n − 10.125 | n − 9 |
| `containers.gap.header-content-card-4` | d | 2n − 12 | 3n − 27 | — |
| `containers.gap.band-content-card-4` | max(0, d/2 − I) | 0.25n − 1.5 | 0.375n − 3.375 | — |
| `containers.gap.separate-rows-card-4` | d/4, snapped to ½q | 0.5n − 3 | 0.75n − 6.75 | — |
| `containers.gap.before-actions-card-4` | d | 2n − 12 | 3n − 27 | — |
| `containers.gap.between-form-fields` | 2I (as table columns) | 1.5n − 9 | 2.25n − 20.25 | 2n − 18 |
| `containers.gap.label-control-control-help` | g_c | 0.25n − 1.5 | 0.375n − 3.375 | n − 9 |
| `containers.gap.around-a-field-group` | max(d, 3g_c): the gap between groups | 2n − 12 | 3n − 27 | 2n − 8 |
| `containers.border.card-4-inner-padding` | d − b | 2n − 13 | 3n − 28 | — |
| `containers.border.card-4-inner-radius` | R − b | 3n − 19 | 4.5n − 41.5 | — |
| `containers.width.dialog` | 120 | 60n − 360 | 90n − 810 | 32n + 32 |
| `containers.width.panel` | 72 | 36n − 216 | 54n − 486 | 16n + 16 |
| `containers.width.rail` | 56 | 28n − 168 | 42n − 378 | 8n − 42 |
| `containers.width.collapse` | 2 × panel: two panels side by side | 72n − 432 | 108n − 972 | 32n + 32 |
| `containers.media.square-1-1-height-at-w-40` | w · 1/1 | 20n − 120 | 30n − 270 | 40 |
| `containers.media.photo-4-3-height-at-w-40` | w · 3/4 | 15n − 90 | 22.5n − 202.5 | 30 |
| `containers.media.classic-3-2-height-at-w-40` | w · 2/3 | 13.333n − 80 | 20n − 180 | 26.667 |
| `containers.media.video-16-9-height-at-w-40` | w · 9/16 | 11.25n − 67.5 | 16.875n − 151.875 | 22.5 |
| `containers.media.cinema-21-9-height-at-w-40` | w · 9/21 | 8.571n − 51.429 | 12.857n − 115.714 | 17.143 |
| `layout.grid.m` | 4I | 3n − 18 | 4.5n − 40.5 | 4n − 26 |
| `layout.grid.g` | M/2, snapped to ½q | 1.5n − 9 | 2.25n − 20.25 | 2n − 18 |
| `layout.gap.card` | G | 1.5n − 9 | 2.25n − 20.25 | 2n − 18 |
| `layout.flow.kicker-to-heading` | 1·F | not a line here | not a line here | n |
| `layout.flow.heading-to-text` | 1.25·F | not a line here | not a line here | n |
| `layout.flow.paragraphs` | 1.25·F | not a line here | not a line here | n |
| `layout.flow.text-to-actions` | 2.5·F | not a line here | not a line here | 2n |
| `layout.flow.action-to-note` | 1·F | not a line here | not a line here | n |
| `layout.flow.section-padding` | 3.25·F above and below | not a line here | not a line here | 3n |
| `layout.width.viewport-margin` | 4 | 2n − 12 | 3n − 27 | 2n − 8 |
| `layout.width.measure` | 160 | 80n − 480 | 120n − 1080 | 44n |
| `layout.breakpoint.1-column` | k·w_min + (k − 1)G + 2M, w_min 40 | 26n − 156 | 39n − 351 | 16n − 4 |
| `layout.breakpoint.2-columns` | k·w_min + (k − 1)G + 2M, w_min 40 | 47.5n − 285 | 71.25n − 641.25 | 24n + 44 |
| `layout.breakpoint.3-columns` | k·w_min + (k − 1)G + 2M, w_min 40 | 69n − 414 | 103.5n − 931.5 | 32n + 92 |
| `layout.breakpoint.4-columns` | k·w_min + (k − 1)G + 2M, w_min 40 | 90.5n − 543 | 135.75n − 1221.75 | 40n + 140 |
| `layout.breakpoint.5-columns` | k·w_min + (k − 1)G + 2M, w_min 40 | 112n − 672 | 168n − 1512 | 48n + 188 |
| `layout.breakpoint.6-columns` | k·w_min + (k − 1)G + 2M, w_min 40 | 133.5n − 801 | 200.25n − 1802.25 | 56n + 236 |
| `layout.measure.min-45-ch` | c · charWidth · F | 22.5n | 22.5n | 22.5n |
| `layout.measure.ideal-66-ch` | c · charWidth · F | 33n | 33n | 33n |
| `layout.measure.max-75-ch` | c · charWidth · F | 37.5n | 37.5n | 37.5n |
| `controls.mark.mark.sm` | a.sm | — | — | n |
| `controls.mark.mark-radius.sm` | 0.25·a | — | — | 0.25n |
| `controls.mark.switch-track.sm` | 2a − 4b | — | — | 2n − 4 |
| `controls.mark.switch-thumb.sm` | a − 4b | — | — | n − 4 |
| `controls.mark.range-thumb.sm` | 0.5·a | — | — | 0.5n |
| `controls.mark.range-track.sm` | max((a − 8px)/3, b) | — | — | 0.333n − 2.667 |
| `controls.mark.mark.md` | a.md | — | — | 1.5n − 4 |
| `controls.mark.mark-radius.md` | 0.25·a | — | — | 0.375n − 1 |
| `controls.mark.switch-track.md` | 2a − 4b | — | — | 3n − 12 |
| `controls.mark.switch-thumb.md` | a − 4b | — | — | 1.5n − 8 |
| `controls.mark.range-thumb.md` | 0.5·a | — | — | 0.75n − 2 |
| `controls.mark.range-track.md` | max((a − 8px)/3, b) | — | — | 0.5n − 4 |
| `controls.mark.mark.lg` | a.lg | — | — | 2n − 8 |
| `controls.mark.mark-radius.lg` | 0.25·a | — | — | 0.5n − 2 |
| `controls.mark.switch-track.lg` | 2a − 4b | — | — | 4n − 20 |
| `controls.mark.switch-thumb.lg` | a − 4b | — | — | 2n − 12 |
| `controls.mark.range-thumb.lg` | 0.5·a | — | — | n − 4 |
| `controls.mark.range-track.lg` | max((a − 8px)/3, b) | — | — | 0.667n − 5.333 |
| `containers.curvature.r-card-inset` | r(κ_control) + I | — | — | 2n − 15 |
| `containers.curvature.r-card-text-edge` | r(κ_control) + I | — | — | 2n − 15 |
| `containers.curvature.r-card-slot` | r(κ_control) + I | — | — | 2n − 15 |
| `containers.curvature.r-card-control` | r(κ_control) + I | — | — | 2n − 15 |
| `containers.curvature.r-dialog` | r(κ_control) + 2I | — | — | 3n − 24 |
| `containers.curvature.nest-f-0-in-card-d` | r(κ_control): one level in, 0 when flush | — | — | 0 |
| `containers.curvature.nest-f-0.25-in-card-d` | r(κ_control): one level in, 0 when flush | — | — | n − 6 |
| `containers.curvature.nest-f-0.5-in-card-d` | r(κ_control): one level in, 0 when flush | — | — | n − 6 |
| `containers.curvature.nest-f-0.75-in-card-d` | r(κ_control): one level in, 0 when flush | — | — | n − 6 |
| `containers.curvature.nest-f-1-in-card-d` | r(κ_control): one level in, 0 when flush | — | — | n − 6 |
| `containers.gap.groups-in-card-d` | d | — | — | 2n − 8 |
| `containers.gap.blocks-in-a-group-card-d` | d/2 | — | — | n − 4 |
| `containers.gap.header-content-card-d` | d | — | — | 2n − 8 |
| `containers.gap.band-content-card-d` | max(0, d/2 − I) | — | — | 5 |
| `containers.gap.separate-rows-card-d` | d/4 | — | — | 0.5n − 2 |
| `containers.gap.before-actions-card-d` | d | — | — | 2n − 8 |
| `containers.border.card-d-inner-padding` | d − b | — | — | 2n − 9 |
| `containers.border.card-d-inner-radius` | R − b | — | — | 2n − 16 |
| `layout.grid.column-inset` | G/2: what sits on a column pads itself; the columns have no gap | — | — | n − 9 |
| `layout.width.header` | 50 | — | — | 6n − 34 |
| `layout.width.docking-width` | panel + measure + 2M: under it the panel does not fit beside a full measure | — | — | 68n − 36 |
<!-- /generated:every -->
