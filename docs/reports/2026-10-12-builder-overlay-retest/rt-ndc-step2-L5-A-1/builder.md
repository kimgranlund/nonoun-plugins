<!-- role=builder level=L5 model=fable effort=xhigh -->
## Status
blocked

## Changes
- src/ui/sections/color.js: graphLC, graphTone, graphChroma, graphDamping, graphHueWheel and _hueCircle build a spec and return renderChart(spec); two new import lines (STROKE, polar, scaleLinear from ../charts/core.mjs; renderChart from ../charts/render.mjs). No html: or SVG string remains.
- src/ui/styles.css: chart block after .an-empty (.an-chart, .ch-marks, .ch-ribbon, .ch-band, .ch-rule, .ch-dot, .ch-ring, .ch-rect, .ch-circle, .ch-label with ch-a-* transforms, .vh); series paint moved to --series (lc-ceiling, lc-toneline with --dash and --rule-style, lc-applied, lc-dot, hw-circle, hw-dot, hc-rim, hc-axis, hc-dot); lc-axis and dg-unity keep stroke and gain --series (dg-unity also --rule-style: dashed); .an-svg.hw, .an-svg.hw text, .an-svg .lc-toneline, .an-svg .lc-applied, .newpal-hc svg, .hw-ring and .hc-ring deleted; .newpal-hc { max-width: 300px; margin-inline: auto }; forced-color-adjust: none for .an-chart .ch-marks inside the forced-colors block.
- test/repo/dom-charts.mjs: the color.js ALLOW entry is [].
- test/ui/headless-boot.mjs: q3 dgBefore/dgAfter read .querySelector(".damp-graph").querySelector(".ch-ribbon").getAttribute("style").
- test/smoke/smoke.mjs: the new-palette assertion queries .newpal-hc .ch-dot.
- docs/references/component-inventory.md: 34 cites on the 32 STALE lines renumbered.
- docs/reports/2026-08-20-reactivity/01-core-reactivity.md: 2 cites on line 39 renumbered.
- docs/specs/app-shell.md: 2 cites (lines 87, 137) renumbered.

## Checks
- `redck.py record <handoff>` before the first edit: exit 0, 6 pre-edit controls red.
- (red) criterion 1 (no html:/<svg in color.js, renderChart import line): pass.
- (red) criterion 2 (bare-mock render of the six functions): exit 0.
- (red) criterion 3 (`node test/repo/dom-charts.mjs`, ALLOW names gone): pass, `dom-charts: 6 html: attributes in 6 allowlisted chart functions (color 0, geometry 3, typography 3), 4 line classes qualified with fill: none`.
- (red) criterion 4 (.an-chart, .vh, -webkit-mask-image, forced-color-adjust in the forced-colors block): pass.
- (red) criterion 5 (no stroke/fill in lc-*/hw-*/hc-* rules, SVG-only rules gone): pass.
- (red) criterion 6 (q3 selector, no children[0]?.innerHTML, smoke selector swap): pass.
- `node test/ui/headless-boot.mjs`: exit 0, HEADLESS BOOT PASS; `grep -qF 'app.graphTone({ palettes: [] }, 0)' test/ui/headless-boot.mjs`: pass.
- `node test/ui/charts.mjs`: exit 0.
- (guard) `node test/repo/citations.mjs`: exit 1 after the port (35 STALE lines: component-inventory.md 32, 01-core-reactivity.md 1, app-shell.md 2), exit 0 after the repair (STALE 0 across 12 docs, symbol homes 44 checked, 0 stale).
- (guard) `node test/repo/em-dash.mjs`: exit 0, clean (1630 files).
- (guard) scope criterion with SDLC_BASE_SHA=7f05eb50: pass; `git status` shows only the eight files above.
- `npm run smoke`: exit 1. `vite build` completed, then `npm run bundle` threw `bundle.mjs preflight found 2 registry problems`: `src/ui/sections/color.js: import path "../charts/core.mjs" is not registered in KEY (and its module, if new, is not in MODS)` and the same line for `../charts/render.mjs`. No smoke-out/ was produced, so the color rail and the new-palette dialog were not looked at in Chrome.
- `npm test` in this tree: not run, it starts with the same `npm run bundle` step and would fail identically.
- `npm test` in a throwaway worktree at HEAD with this step's diff applied plus the 2-line registry change below: exit 0, `all 56 test files passed`. The worktree is removed; the tree here is untouched by it.

## Notes
plan defect: (guard) scope criterion omits scripts/bundle.mjs, which criterion 1's mandated import of ../charts/core.mjs and ../charts/render.mjs requires editing (bundle.mjs's hand-maintained MODS/KEY registry rejects the two unregistered imports at preflight, so `npm run bundle`, the `npm test` floor and Do item 7's `npm run smoke` cannot run). The step cannot satisfy the scope guard and the build at once; the tree is left with every in-scope change done and the scope guard green.

- The change the replan needs, proven green in the worktree run above: in `scripts/bundle.mjs` MODS, insert `["chartsCore", "src/ui/charts/core.mjs"], ["chartsRender", "src/ui/charts/render.mjs"],` after the `["appHelpers", ...]` entry and before `["colorSection", ...]` (render.mjs imports app-helpers.mjs and core.mjs, and preflight check (d) enforces MODS order); in KEY add `"core.mjs": "chartsCore", "render.mjs": "chartsRender"`. KEY is keyed by basename, so any future module named core.mjs or render.mjs would collide; the planner may want to name the keys deliberately. The replan should add scripts/bundle.mjs to the scope list and a Do item for the registry, then re-run Do item 7 (smoke, light and dark screenshots), which this attempt could not do.
- Step 1 could not have caught this: nothing imported the chart modules until now, so the bundle preflight was silent.
- Every (red) criterion, the headless suite, charts.mjs, citations, em-dash and the scope guard are green on the tree as left. Only the bundle-dependent checks are unrun.
- Judgment calls the verifier should see:
  - Domain-to-px mappings are written with scaleLinear and give the same px as the old inline arrows (graphLC X: [0, maxC] to [pad, W-8], Y: [100, 0] to [8, H-pad]; graphChroma and graphDamping Y: [0, max] to [H-pad+8, 16]).
  - `hw-tick` is a new class on the hue-wheel tick labels (color: var(--ink-faint), the old `.an-svg.hw text` colour); the handoff named no class for them.
  - `.hw-ring` and `.hc-ring` were deleted although the handoff's delete list does not name them: the ring is now the `ch-ring` class on the same dot, so no element emits them.
  - `.hw-dot` and `.hc-dot` keep their old outlines as box-shadow (the SVG stroke had no native equivalent that follows border-radius on older Safari); `.ch-dot.ch-ring` wins over them by specificity.
  - `.ch-rect` is an outline (border var(--chart-ref) solid var(--series)), a choice for step 4 to revise.
  - `.ch-label` puts the point at the text baseline with translateY(-100%) (line-height 1), within about 1px of the SVG baseline for 9px text.
  - renderChart sets `max-width: 280px` inline on the disc root, so the `.newpal-hc { max-width: 300px }` rule the handoff asked for is capped at 280px by the inline style; the disc was 280px wide in SVG too.
  - Dots carry `label` (palette name, "proposed") and every chart sets `columns` for its hidden table; the handoff asked for columns only on the wheel.
- Citations were repaired by number only, with a mapping derived from the diff hunks; every remapped target reads the same line it did at base. Two cites pointed inside rewritten rule blocks and now point at the replacement rules: component-inventory.md:382 styles.css:540-542 (.hw-circle to .hw-tick) and :387 styles.css:879-883 (.lc-axis to .lc-dot). Several pre-existing NEAR cites (off by 1 to 3 lines, gate-tolerated) were left alone. Step 5 owns the chart prose.
- No commit was made. One throwaway worktree (bundlefix) was created under the tmp prefix and removed.
