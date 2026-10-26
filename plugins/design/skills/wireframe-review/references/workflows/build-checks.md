# Conditional build checks

Read the section routed by [build and verify](build.md). Commands are scoped fixtures, not blanket acceptance; never count an unrun check as passed.

For generated markup/reference integrity and advisory geometry lint, use [preventive checks](preventive-checks.md). Its change selector suggests existing checks without running them; this document remains the routing authority.

## Shell and feedback

When adapting the proposal count, verify every selector, comparison control and subtitle against the actual proposal IDs. Exercise all exposed options; successful rendering of A alone cannot verify a one-proposal shell. Keep the complete builder dependency set, including its token index, available to verification.

For review-shell fallback changes, run `check-shell-fallback.mjs PLAYWRIGHT OUTPUT`: scripts-disabled native disclosure and all raw proposals, declared page compositions, escaped labels, hidden inactive review chrome and document containment in three engines, plus script-enabled startup. Follow with `check-proposal-count.mjs` for feedback and selection behavior. Static previews do not run prototype controllers or represent imported choices.

## Geometry and composition

For forms/cards, run `node scripts/check-spacing.mjs PLAYWRIGHT`. This isolated fixture checks the spacing recipe at narrow/wide widths and three geometry sizes, and must reject zero gaps, oversized gaps/insets and added child margins. In the actual artifact, bind equivalent relationships: tight content = local inset, content = twice inset, major groups = three times inset, card padding = four times inset; measure both lower and upper bounds with subpixel tolerance. Check actual heading/body/footer boundaries as well as nested fieldsets, wrapped choice rows and inline clusters. Distinguish major-group gaps from field gaps; a flat stack does not satisfy the hierarchy. A global minimum-gap check is insufficient. Exceptions need an explicit local purpose, not an arbitrary pixel patch.

Resolve measured CSS lengths through computed layout (for example a temporary probe sized with the custom property). `parseFloat` on a custom property's `calc(...)` expression is not a measurement. Match the asserted relationship to the content: an inline action cluster uses the tight gap, not the field-group gap.

For compact product heading contexts, run `check-heading-context.mjs PLAYWRIGHT OUTPUT`; it checks all six ranks, explicit/nested content contexts and independence from control density. For breadcrumbs, run `check-breadcrumbs.mjs PLAYWRIGHT OUTPUT`. Summary header geometry and Phosphor caret states are covered by `check-native-patterns.mjs`. The source-sheet verifier covers grouped color inventory, OKLCH/alpha fidelity, shared sample geometry and swatch popover interaction. These checks complement source review; they do not establish fresh-context model efficacy.

For collection-to-task composition, run `check-collection-workflow.mjs PLAYWRIGHT OUTPUT`: 36 engine/width/scheme/density cases, original inset/gap relationships, content retention, named step access, saved/draft state, an expanded explanation that does not precede the task, and a repeated-card-inset counterexample. Compare rendered grouping separately; shorter page height alone is not proof of better design.

## Controls and behavior

After ownership-contract changes, run `check-implementation-ownership.mjs`: all registered pattern declarations, owned CSS/verifier/guidance paths and missing-owner negative controls. Browser support is verified through the linked pattern checks, not by this declaration gate.

For an account/navigation menu, read and adapt assets/recipes/navigation-menu.html with its bundled styles and native popover/anchor behavior, or verify the same behavior in a custom implementation. Replace example destinations with actual routes. Read its contract through style/discovery.json; don't recreate disclosure slot spacing from memory. `check-declarations.mjs PLAYWRIGHT` verifies schemas, negative controls, static reporting and the live recipe.

`check-product-foundation.mjs PLAYWRIGHT OUTPUT` covers controller assembly, dirty approval, rerender persistence, proposal isolation, wrapping navigation and clipped menus, with negative controls. It is an authored fixture, not model efficacy evidence. Check actual text/surface contrast, open-overlay containment, long content and meaningful proposal differences separately from document overflow. No blanket visual pass follows from geometric gates.

For common component styling, read [component families](../style/components/README.md). Run `node scripts/check-components.mjs PLAYWRIGHT OUTPUT` to generate an interactive catalog and check its geometry/state relationships. It covers custom native checkbox/radio marks, switch geometry and focus, native range endpoints with numeric entry, field errors, tabs, segmented density, visible table filtering/sorting/selection, dialog dismissal/focus return, and negative controls. Preserve the distinction between its authored recipe evidence and fresh-context generation efficacy. Safari/Firefox and assistive technology remain separate verification tasks.

For destination popovers, declarative modal commands or exclusive accordions, read [native-first guidance](../style/native-first.md) and consume [native patterns](../../assets/recipes/native-patterns.html). Give each panel a unique ID/anchor pair and each independent accordion a unique name. Run `check-native-patterns.mjs` with page scripts disabled; record actual engines and unsupported features. The native browser baseline is Chromium 151, Firefox 153 and WebKit 26.5; no removed runtime fallback is promised.

For action appearance changes, run `check-action-contrast.mjs PLAYWRIGHT OUTPUT`: three engines, both schemes, rest/focus/hover/active, disabled-hover stability, and deliberate old-rule failures. A static screenshot or rest-state contrast check does not cover hover.

For choice defaults and disabled presentation, run `check-choice-defaults.mjs PLAYWRIGHT OUTPUT`. It checks unselected marks, plain-row versus card insets, retained disabled values, once-only row dimming and switch track geometry across engines, widths, schemes and sizes. False selected marks and double dimming are negative controls. These are authored visual/native assertions, not screen-reader or generation certification.

For field help/error associations, run `check-field-descriptions.mjs PLAYWRIGHT OUTPUT`: persistent caption geometry, empty/focus/read-only/disabled hosts, attempted validation and correction/restore transitions. It rejects retained hidden-error references and invisible help. Actual assistive-technology output is a separate gate.

For non-tabular collection data states, run `check-list-states.mjs PLAYWRIGHT OUTPUT`. It verifies flat row/body geometry, native selection retained across filtering/sorting, empty recovery, no-script content and negatives for lost hidden selection or repeated card padding. Do not apply table-only `aria-sort` to list items.

For default feedback/navigation presentation, run `check-feedback-navigation.mjs PLAYWRIGHT OUTPUT`: notice lifecycle/container geometry, progress labels, empty recovery, decorative loading/identity, badges, tabs/segments, breadcrumbs and native table foundations. Its negative controls reject independent notice padding and exposed decorative skeletons.

For action-group state reflection and native overlay defaults, run `check-action-overlay-hosts.mjs PLAYWRIGHT OUTPUT`. It checks descendant-owned action states, busy lifecycle, hidden/modal dialog geometry, popup expansion/focus/scrolling and negative controls for wrong action gaps or missing focus clearance.

For composed input/card/navigation states, run `check-composed-states.mjs PLAYWRIGHT OUTPUT`: three engines, both schemes and all sizes, including a negative control for missing invalid wrapper paint. It complements the component task checks; per-class/state and assistive-technology completeness remain separate audits.

For save/apply status changes, run `check-save-status.mjs PLAYWRIGHT OUTPUT`: successful save, later edit, invalid save preserving snapshot, restore, manual return to saved values, and distinct primary/reset paint in three engines and both schemes/widths. Fresh-generation action recognition remains a separate evaluation.

For compound saved tasks, run `node scripts/check-compound-save.mjs PLAYWRIGHT NEW_OUTPUT`. This review-owned recipe is generated through the installed delivery pipeline and verified on the final artifact in Chromium desktop/light and mobile/dark. It covers each saved field invalidating both primary and secondary success, full restore, invalid-save snapshot preservation, manual return, selection-set order, independent preferences/filter, keyboard Save and remount. Five mutated controllers must fail the named acceptance assertions: stale secondary success, omitted capacity, omitted selected identities, count-only identity comparisons and order-sensitive identity sets. Adapt these checks to every success surface and domain field in the actual brief. The authored fixture is not fresh-generation adoption evidence or Safari/accessibility certification.

## Source sheets and popovers

For page-level spacing, use the semantic parents in product-foundation.md#page-level-rhythm and assets/recipes/page-rhythm.html. In source-derived sheets, run check-page-rhythm.mjs OUTPUT PLAYWRIGHT after rebuilding. Check preceding-section clearance as well as heading-to-description spacing; a zero preceding gap cannot be excused by a correct heading bottom margin.

For color-sheet popovers, run `check-color-popovers.mjs OUTPUT PLAYWRIGHT` after rebuilding the sheets. It checks native keyboard/pointer dismissal, stable layout, viewport containment, and the entire expanded disclosure boundary with page scripts disabled in three engines.

For anchored content panels, run `scripts/check-popover-sizing.mjs PLAYWRIGHT OUTPUT`: it tests expanded/reopened panels, visible body/Close and anchor gap across three viewport heights, three sizes, two anchor positions and both directions, including deliberately wrong viewport-height overrides. A panel may fit the viewport yet overlap its trigger, so containment alone is insufficient.

For content headers and split source triggers, run `scripts/check-popup-swatch-composition.mjs PLAYWRIGHT NEW_OUTPUT`. It doubles initial computed title/action text sizes and checks long labels across widths, schemes, densities and directions in three engines. Old nowrap header and inherited swatch gap faults must fail. Escape restoration is tested from an explicitly keyboard-focused trigger, not inferred from pointer focus.

For popovers inside clipping/scrolling ancestors or repeated instances, run `scripts/check-popup-instances.mjs PLAYWRIGHT NEW_OUTPUT`. It verifies actual panel and focused-content bounds, independent disclosure/data state, sibling dismissal, keyboard restoration and unchanged following layout. Its oversized top-layer control must fail panel containment even while document overflow passes. On no-script pages, inject faults with direct style mutation through the driver; do not rely on helpers whose completion requires page-script load callbacks. Keep incremental observations so a stopped harness is distinguishable from a failing fixture.

## Generated assets and construction

When changing a generated source dependency, refresh its observations with observe-select.mjs, then run --check. Export the type snapshot with export-type-snapshot.mjs ULTIMATE_TOKENS_SOURCE. Regenerate demos through build-demo-suite.mjs OUTPUT; refresh the portable zip after validation. Never describe an unrun check as passed.

`build.mjs` compiles select anatomy before delivery and injects the explicit dynamic control builder for review-shell controls. Generated artifacts have no select scanner, icon resolver or scripted menu-placement dependency. Application state and conditional workflow dialogs can still use JavaScript.

Bundled Phosphor sources live in `assets/icons/`; `generate-icons.mjs` embeds their data URIs in product/shell CSS without network access. After an intentional glyph update, regenerate icons, token index and select observations. Unknown icon names fail markup compilation. Do not restore CDN URLs as a fallback.

Run `node scripts/check-no-legacy.mjs [generated HTML files or output directories]` to check compiler anatomy/idempotence and reject removed runtime dependencies, including seeded failures. Check only maintained builds; dated evaluation snapshots remain historical evidence. `generate-icons.mjs --check` and `observe-select.mjs --check` verify generated-source freshness.

Latest consolidation evidence and limits: [context consolidation](../reports/context-consolidation-2026-10-09.md).

## Searchable selection, drawers and staged forms

Read [workflow peers](../style/components/workflow-patterns.md). Run `check-workflow-patterns.mjs PLAYWRIGHT NEW_OUTPUT` for interaction/native fallback checks and `check-workflow-controller.mjs PLAYWRIGHT NEW_OUTPUT` for scoped lifecycle, proposal isolation and remount persistence. Fresh sheet builds consume their registered families, specimens and authored guides automatically. Use the standard generation gate for their final review artifact; these fixtures do not replace its acceptance checks.

### Extended component peers

For multi-select, tooltip, toast queue, pagination, tree, date picker, editable grid or basic rich text, run `node scripts/check-extended-patterns.mjs PLAYWRIGHT NEW_OUTPUT` and `node scripts/check-extended-controller.mjs PLAYWRIGHT NEW_OUTPUT`. These cover authored behavior and prototype state isolation; actual assistive technology and installed Safari remain separate. See [bounded patterns](../style/components/extended-patterns.md). Final review artifacts must still pass `generate.mjs` and their declared interactions in the compiled shell.

For filter paint or linear stepper state changes, run `node scripts/check-remediation-states.mjs PLAYWRIGHT NEW_OUTPUT`. It checks content/pressed synchronization, rest paint with a deliberate missing-paint fault, and Next/Back progress labels in three engines, two widths and both schemes. It does not establish agent uptake.
