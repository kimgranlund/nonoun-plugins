# Legacy dependency removal, 2026-10-09

## Completed migration

Maintained source consumers now use canonical native markup. The artifact compiler emits select wrappers and local icon slots before delivery. Explicit dynamic review controls use createSelectControl; no DOM-wide select scanner remains. Icons come from 23 bundled Phosphor 2.1.1 SVG sources embedded as data URIs. Generation and rendering no longer resolve icons over a CDN.

Removed styleSelects, resolvePrototypeIcons and installPrototypeMenus; removed the old details-menu CSS. Navigation and product-account recipes use native auto popovers with explicit CSS anchors. Catalog dialogs and simple shell feedback/JSON controls use native commands. Conditional workflow dialogs still use application JavaScript to prepare state, validate, retain drafts or handle clipboard failure. Those are deliberate application responsibilities, not legacy component initializers.

The review iframe previously cancelled all default button actions. Native type=button invokers now reach browser behavior; annotation/overview modes, submits and external navigation retain their existing guards. Declaration/product integration tests exposed this issue; standalone native fixtures would not have caught it.

## Corpus and build authority

Bootstrap, SKILL routes, select/navigation contracts, discovery guidance, shell/artifact styling, product foundations and build instructions now describe authored anatomy, build-time compilation and the supported native feature baseline. Legacy fallback advice was removed. Older browser support is not promised. The three verified engines were Chromium151, Firefox153 and WebKit26.5; this does not certify installed Safari or assistive technologies.

The navigation-menu filename remains as the small canonical native recipe, not a compatibility implementation. Historical dated reports, evaluation runs and previous-demo snapshots are preserved; their embedded old code is historical evidence, not a supported construction path. Maintained nine-scenario builds, starter, sheets, native-patterns, component and product-foundation previews were refreshed.

## Verification

- Compiler: repeat compilation, optional option closing tags, quoted angle brackets, comments/raw-text preservation, native attributes, unknown-icon rejection and removed-markup rejection.
- Legacy guard: rejects seeded installer/resolver/CDN reintroductions and scans maintained source/generated output.
- Select contract: 12 configurations across Chromium/Firefox/WebKit; native focus/value behavior and slot-distortion negatives.
- Review shell: interaction/state/focus/layout suite at 320/390/1500 widths. Obsolete20px card assertion updated to the previously approved32px baseline.
- Nine scenarios: 360 rendered page proposals at two viewport sizes, links and export.
- Declarations: four rendered configurations plus schema/target/token/report negatives.
- Product: 13 regressions plus the implemented-behavior gate's reject/accept controls.
- Components: 12 responsive cases,27 geometry contexts,12 state groups including native dialog behavior.
- Sheets:20 responsive cases and native interactions;60 no-script select cases plus3 negative controls;30 rhythm cases plus3 negatives.
- Native patterns:36 no-script cases across three engines plus3 positioning negatives.
- Offline generated shell: canonical select wrappers/local glyphs, zero HTTP requests.
- Core self-test:26 checks. Token/icon/observation hashes and skill validation checked before packaging.

Evidence lives in /Users/kimgranlund/.codex/skill-previews/wireframe-review/ and its sheets, native-patterns, components and select-verification directories. Supporting integration outputs: /tmp/wf-remove-legacy-product/wireframe-product-JIiWc9 and /var/folders/n0/b1pq09652mbd8kncmz8tgkvc0000gn/T/wireframe-declarations-I8ZGZs. Generated completion audits record current source/output hashes and package byte parity.

Remaining JavaScript: application state, tabs, coordinated checkboxes, live value synchronization, filtering/sorting, review persistence and feedback workflows. Native-popup keyboard selection, screen-reader/physical-device coverage and a complete browser-zoom audit remain bounded verification limits. The20 reference-sheet documentation/state gaps are unrelated to the removed runtime dependencies and are not represented as closed.
