# Common component families

Added a compact family contract, conditional SKILL/discovery routing, opt-in styles in wireframe.css, and an interactive catalog fragment/runtime. Families cover choices, switches, ranges, fields, actions, navigation, collection rows/tables, disclosure, feedback, identity and native modal styling. Existing select and navigation-menu contracts remain owners of those patterns. No engine tokens or consumer repository files changed.

Geometry relationships: mark/thumb=icon; checkbox glyph=text bounded by available icon across observed cells; switch clearance=inset/4, track height=icon+inset/2, track width=2icon+inset/2; range rail=inset/2; table cell block=inset/2 and inline=inset. Wrapping rows are content-sized. Choice/switch/range interaction frames retain a 24px floor independent of visible mark size. Card/content hierarchy remains 4u/3u/2u/1u. These component ratios are recipe decisions, not newly asserted engine laws.

Native checkbox/radio semantics are retained with opt-in custom paint. Check/minus glyphs are embedded Phosphor 2.1.1 regular SVG masks; MIT attribution is bundled. Forced-colors uses native checkbox/radio rendering. Switch checked state, range values, tab visibility, table order/filtering and dialog behavior are exercised as actual transitions. Native disclosures keep native indicators. No default animation was added.

## Verification

- check-components.mjs: 12 width/size/scheme cases; 27 tier/scale/size relationship contexts; 12 task/state check groups, including four deliberately broken geometry/hidden-state cases detected by assertions. Extreme content-tier overflow is excluded from the 27-context check.
- Independent glyph measurement: no glyph wider than its mark across all 27 contexts.
- check-spacing.mjs: six relationship cases and 30 negative controls passed.
- check-product-foundation.mjs: 13 product regressions passed, including executable-gate rejection of untested claims.
- selftest.mjs: 26 build/data checks passed.
- Token index regenerated and freshness checked; skill validation passed.
- Narrow dark screenshot visually inspected; full desktop light/dark and narrow screenshots retained with catalog output.

The first catalog test caught repeated-script global redeclaration; its runtime was isolated and the complete component test rerun successfully. A shared hidden-state rule prevents display declarations from revealing filtered rows or inactive panels, and table tests compare actual visible records rather than only selected IDs.

## Limits

Chromium only; no Safari/Firefox or assistive-technology certification, full measured contrast audit, or 200% browser-zoom review. Native range pseudo-element rules include WebKit and Firefox implementations, but Firefox remains untested. Authored recipes do not establish agent uptake; no new generative trial was run. No tooltip, toast, drawer, combobox, tree, date-picker, rich-text or ARIA-grid runtime is claimed. Skeleton/progress/empty states have baseline styling; they require actual application state bindings. Table sorting is a small demonstrator, not a general data-grid library.

Catalog and browser evidence: /Users/kimgranlund/.codex/skill-previews/wireframe-review/components/index.html and report.json. Product regression evidence: /tmp/wf-component-regression/wireframe-product-wVzEzs. Spacing evidence: /var/folders/n0/b1pq09652mbd8kncmz8tgkvc0000gn/T/wireframe-spacing-3KFY6N.
