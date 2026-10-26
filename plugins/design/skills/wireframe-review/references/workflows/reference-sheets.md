# Source-derived reference sheets

Use this workflow when asked for browsable sheets of the installed core/default system. A reference site is one coherent design; do not manufacture A/B/C copies. Use the sheets builder for source-derived documentation; use the review shell only when design decisions need review.

Use `node scripts/build-sheets.mjs --help` for the command interface; reading generator implementation is unnecessary for ordinary builds. Custom catalogs consume the contracts and recipes directly. Read generator source only to modify generation itself.

Build and verify in a fresh `/private/tmp/*` staging directory outside the skill source:

```sh
node scripts/generate-token-index.mjs --check
node scripts/build-sheets.mjs OUTPUT PLAYWRIGHT
node scripts/check-sheets.mjs OUTPUT PLAYWRIGHT
```

OUTPUT contains index.html, tokens.html, colors.html, components.html, gaps.html, inventory.json, gaps.json, source snapshots, shared CSS/runtime and verification evidence. Serve as static files or open index.html directly. Header navigation is native select; colors and component geometry can be inspected with local controls.

Authority: token-index owns inventory membership and hashes; its referenced CSS owns declarations. CSSOM extraction preserves selector/condition/value relationships but normalizes formatting; snapshots preserve original bytes. Components come from the family contract, dedicated select/menu contracts, compact composition families and remaining recipe__slot profile classes. Class discovery is an implementation inventory, not an invented component registry.

A disclosure must distinguish a source declaration from a manifest, and an illustrative code binding from usage guidance. Never fabricate missing intent, not-for rules or supported states. Gaps are separate data with impact and a suggested owner. Do not fix authoritative source gaps as a side effect of generating sheets. The root-context default is product/md/md; unresolved component-scoped variables remain explicitly unresolved. A custom-property expression is not necessarily a used pixel length.

Working specimens reuse the maintained catalog and runtime in isolated documents. Source extraction maps registered families to those recipe sections; when a new family has no mapping, the builder fails rather than silently displaying an unrelated example. Dedicated select/menu specimens consume authored native anatomy; dialog and exclusive-disclosure specimens consume the native-patterns recipe. Each contract records platform limits. Additional profile classes expose source CSS without claiming standalone behavior.

The verifier checks source bytes and inventory coverage, page/anchor/source links, native navigation, disclosures, search, header containment and bounded specimen transitions. It deliberately removes token entries to confirm coverage checks reject omission. It does not establish complete accessibility, browser parity or every declared component state. Color ratios cover only explicitly paired profile aliases, use Chromium-resolved opaque sRGB samples and WCAG relative luminance, and must not be advertised as a whole-system contrast pass.

The generator groups direct page content into page sections, heading/description groups and content flows at build time. Native disclosures receive explicit content wrappers. Shared geometry owns 6u page / 3u section / 1u heading spacing; the sheet stylesheet must not restore per-item margins or compact card padding. Run `node scripts/check-page-rhythm.mjs OUTPUT PLAYWRIGHT` after rebuilding. It measures 30 page/width/size cases plus open disclosures and rejects deliberate page-gap, heading-gap and child-margin defects.

Sheet controls consume canonical authored native-select anatomy, including local Phosphor SVG indicator slots. Decoration and native selection must work with JavaScript disabled; navigation and scheme changes remain application behavior. Run `check-static-select.mjs OUTPUT PLAYWRIGHT` to measure every select slot and text clearance across geometry sizes, schemes and widths.

Color sheets group numeric steps into complete source-named palettes and semantic declarations by family. Keep individual token anchors and source disclosures inside each group; never give each ramp step its own card. Display resolved color values and sample literals as OKLCH, with at least two decimal places per numeric channel and sufficient precision to preserve the source color (default L/C six decimals, hue/alpha four). Preserve alpha and light/dark differences. Source excerpts remain verbatim evidence, including legacy syntax. Do not change or invent source values to match a display format.

Each light/dark swatch pair is one contained shape. The wrapper owns the control radius, presentation corner factor/scale, border and overflow clipping. Its equal-width light and dark halves meet without a gap; inner samples have no individual border or radius. Do not hard-code a pixel radius.

Use `button.swatch__root > span + span` for the split sample; both spans are decorative (`aria-hidden="true"`). Shared CSS owns zero gap and padding, equal widths and one containing control radius. Assign source-derived light/dark fills to the halves. The entire split light/dark swatch is a native button opening values and source details in an auto popover card, using a uniquely paired trigger/anchor and labelled panel. Give the button an accessible token-specific name, decorative halves and visible keyboard focus; omit a separate Values & sources button. Use shared popover__root styling, a half-inset trigger gap, control radius and card inset. Keep the panel outside layout flow, bounded and scrollable; support Escape, outside dismissal and an explicit Close action. Retain per-token anchors and source disclosures inside the panel. No opening initializer is needed.

Profile pairing samples use the shared card__root class for card inset, border and presentation radius. Only the demonstrated background/foreground and color scheme are sample-specific; do not replace container geometry with local pixel padding or square borders.

Implementation and source excerpts use the shared `pre.card__root > code` pattern. The generator must consume card geometry and inherited density, not restyle snippets with local pixel padding or radius. Keep source text escaped and verbatim; wrapping is presentation only.

Token-family intent is authored in `references/style/contract.json#tokenUsage`; sheets render it verbatim and retain raw declarations as value authority. `scopedTokens` specifies representative component fixtures for variables undefined at document root; those observations are not global defaults. Component `classGroups` classifies composition, layout/context utilities and subparts separately from interactive families. Run `check-context-coverage.mjs OUTPUT` after building; omission controls reject missing guidance, ownership and fixture evidence.

Numeric palette ramps use compact repeated swatches (minimum 8 local inset units) rather than semantic-card widths. At narrow widths keep at least two columns when the available content width permits, while preserving readable step labels, full token access and split light/dark shapes. Semantic tokens may use wider cells for names. Verify ramp height and label wrapping, not just horizontal overflow.

Classify primitive versus semantic membership from the authoritative export sections. Prime colors and scrims are primitives even when their names are not bare numeric steps. Semantic roles may resolve to equal light/dark colors; equality alone is not a classification rule. The builder reads the export section labels with `classifyExportColors`; unknown declarations remain shared/unclassified rather than being promoted by name.

Content popovers use a direct `popover__header` followed by `popover__body`. The shared grid reserves header space; only the body scrolls. The body reserves focus-ring clearance. Verify a scrolled disclosure can be pointer-activated and keyboard-focused without header occlusion, alongside Close visibility. Do not restore a sticky header over the scrolling content.

## Component reference presentation

Present families as unboxed sections with a heading, visible working specimen and source disclosure. The maintained specimen owns its card geometry; do not add both an outer card and a bordered iframe around it. Preserve component geometry inside the specimen. Size isolated previews to content, including changes caused by width, density and disclosure state; avoid uniform-height scroll windows. Initial generated heights are estimates from one build viewport, not proof that every browser or narrow no-JS view fits. A presentation-only ResizeObserver follows live content changes. Every isolated preview also links to a full-page document generated from the exact same specimen HTML, CSS and conditional runtime. This native link is the fallback when a constrained iframe is inconvenient or cannot expose its content. No-JS notices retain explicit application/output limits. Verify those links, source parity and native document access separately; iframe height alone neither proves usability nor proves clipping. Record actual scroll/focus reachability and native input-tool limits. Run `check-component-static-fallback.mjs SHEETS PLAYWRIGHT NEW_EXTERNAL_REPORT` to verify full-page/srcdoc byte parity, complete rendered dependencies, no-JS document availability and native link navigation. Its scrolling-policy check is not a complete traversal or accessibility claim.

Composition contracts link to the relevant working examples. Utilities and subparts belong in a compact expandable source reference, not empty component cards. Do not claim every declaration is a demonstrated component. Inventory must report live family previews, composition references and declaration-only utilities separately. Check long and short previews, narrow wrapping, open disclosures and a deliberately undersized frame; inventory counts alone are insufficient.

## Capability review units

The component sheet is a review workbench for canonical implementations and agent-facing context. Each registered contract has a focused specimen selected by `references/style/components/specimens.json`. This registry owns extraction metadata only; it must not invent capabilities or replace contracts. Never map several entries to the same complete catalog section. Keep cross-component dependencies explicit. Extraction must preserve required controller controls and status/output peers; partial family markup is not a complete behavioral example.

Each unit provides four contained native details/summary inspectors: Implementation (exact displayed markup plus stylesheet/runtime dependencies), Manifest (verbatim authoritative record), Context (applicable source fields plus shared-context links), and Verification (declared states, source evidence and explicit limits). Render shared guidance once in an inspectable section. Missing evidence is unverified, never inferred from documentation completeness. A family specimen may contain several related component states; this does not establish coverage of every state.

## Specimen extraction boundaries

Maintained member instructions come from `references/style/components/demonstrations.json`, not renderer prose. The builder validates exact registry membership, selected recipe, keyed dependency hashes, contract selection and authored/observed separation before rendering. Display each member’s operation and inspection text with its canonical unit; retain its exact guide and source identity in Context. Render shared typed dependency declarations once and link local records to them. Declared instructions remain unverified observations.

Use `node scripts/demonstration-context.mjs MEMBER_ID` for one authored example guide; `--list` lists members. This is example context, not a substitute for the family’s semantics or an assertion that its states passed. Prepared source bindings reject changed dependencies; review and update instructions with source changes rather than silently blessing stale guidance. Run `check-demonstration-guidance.mjs SHEETS PLAYWRIGHT NEW_EXTERNAL_REPORT` after integration. It checks source routing and visible/context parity at two no-JS widths, with semantic and rendered omission/misrouting controls. It does not verify interaction outcomes or reflected paint.


State checks identify the native/data owner separately from its reflected presentation target. A checked input does not verify label, card or track paint. Resolve instructions to actual source selections; a missing reference or family-state list supplies no reachable task instructions. Native-impossible states are not missing examples; conditional host data and sibling examples remain distinct from member-specific demonstrations.

Verify observable outcomes, not only state markers. Busy checks include status, completion and runtime errors; sorting checks include actual row order. Copied fixtures missing the controller or a required DOM peer must fail the same outcome predicate. Metadata equality protects identity but does not establish applicability, ownership, dependencies or external report compatibility. Keep observed owner state, observed presentation and unverified capabilities separate. The local busy simulation requires both its button and status peer; incomplete markup leaves the operation unavailable.


The staged strict extractor checks supported registry/contract versions, exact family membership, every required direct-child selector, unique DOM/member IDs and explicitly labelled cross-family dependencies. Identical selected markup cannot be assigned to unrelated families. Member names and selectors are presentation metadata; the family contract remains the authority for state applicability. Source-element presence establishes extraction coverage only. It does not verify mixed state, focus, sorting, persistence or other state transitions. Keep declared, demonstrated, tested and unverified fields separate.

Native specimens require uniquely resolved source sections and member selectors too. Preserve reachable opening/closing controls and source markup in Implementation. A heading added for review identification must also appear in the shown markup. Reject omissions with deliberate failing fixtures before accepting an extraction check.

## Review accounting and source routing

When a work register is supplied as an explicit external build input, preserve its classification, normalized canonical status, separate generation status and item-local source selections. Join raw source observations to matched records and count those observations separately; deduplication must not erase their wording. Preserve historical acceptance without promoting it to current artifact or generation verification. Missing compatible evidence stays unverified.

Use `check-component-review-routing.mjs OUTPUT PLAYWRIGHT REPORT` to check every family/dedicated inspector against its source and reject swapped local context, misrouted manifests, missing named members and duplicated rendered examples. Registry-member presence is extraction coverage, not state-transition evidence. Dedicated native select/navigation specimens use comparable version, selector, identity and dependency guards.

Code overflow must be measured on the containing `pre` and actual non-whitespace text bounds. Inline `code.clientWidth` can be zero in a valid wrapped block; comparing its scroll width to zero is not evidence of clipping. Preserve source whitespace, and distinguish hanging whitespace rectangles from visible glyph overflow. Use narrow/wide samples plus a deliberately unwrapped long-word fault.

Renderer-owned page flows remain page-level content; do not place an entire generated page inside its introductory heading group. The coordinator normalizes their direct sections while preserving stable IDs and the 6u/3u/1u page/section/heading ownership.

## Evidence attachment

Build first, verify that exact output, then run `node scripts/attach-sheet-evidence.mjs INPUT OUTPUT REPORT ROUTES PLAYWRIGHT`. OUTPUT must be a new directory outside INPUT. This step does not rebuild sources or publish live files. See [evidence format](sheet-evidence.md) for the report and route inputs. Keep unverified requirements visible beside attached results.

Run `node scripts/check-sheet-evidence.mjs SHEETS REPORT` for report-compatibility rejection controls. These synthetic guard fixtures establish identity handling only; never attach them as measurements. REPORT must be a new file outside SHEETS and any evidence presentation. Never reuse a linked measurement-report path. Before publication, hash the linked report and compare it with the attachment manifest; a passing checker summary is not a measurement report. Browser presentation and behavioral evidence require their own recorded checks.

For the fixed product/md/md token geometry demonstration, `node scripts/check-token-rhythm.mjs SHEETS PLAYWRIGHT REPORT` records card-edge, group, field, label/control/help and choice mark/body distances from actual boxes. It separately records the computed custom-property expression and a used-width probe. A `calc(...)` custom property is not a resolved numeric length; do not parse it with `parseFloat`. The expected 32/24/16/8 relationships apply to this declared local context only. The check covers three Playwright engines, two widths and both schemes, with deliberately compact card-padding controls. It does not cover native zoom, loaded fonts or every component state.

## Contextual class specimens

Contextual utilities and compositions may have maintained recipes in `additional-specimens.json` alongside the standard composition recipes. They retain shared class-group ownership; a visible recipe does not create a standalone behavior contract. The Manifest selection key names the actual class-group ID, while the implementation links the exact recipe source. Count these demonstrations separately from family members and tested states.

The builder requires source class anatomy, unique DOM IDs, unambiguous ownership, supported registry versions and distinct whole recipes. Run `check-composition-source.mjs SHEETS PLAYWRIGHT REPORT` for anatomy/ownership rejection controls and `check-component-review-routing.mjs SHEETS PLAYWRIGHT REPORT` for all family, dedicated and contextual inspector/source routes. Source presence and markup parity do not establish state behavior. Preserve separately maintained native behavior helpers and their dependency links when integrating source changes.

Selection controls inside table headers belong to the table specimen. Required direct-child extraction metadata must select the table wrapper and verify the nested header control; do not retain a obsolete sibling requirement or remove the anatomy check.

Choice mark/body separation follows the current choices contract (one full local inset). Distinguish it from the half-inset icon/label gap inside a control. Sheet relationship prose and measurement expectations must resolve against the same authoritative context as the displayed specimen; preserve older failed expectations as historical evidence when source rules change.

Preview measurement must retain the static iframe fallback until the specimen document loads. Skip initial `about:blank` documents, disconnect obsolete observers after navigation, and avoid height writes for hidden/stale frames or an unchanged height. Never silence ResizeObserver errors as a substitute for checking sizing. `check-blank-frame-regression.mjs OLD_SHEETS NEW_SHEETS PLAYWRIGHT REPORT` discriminates old versus repaired delayed-load sizing across three engines. This remains presentation measurement, not a native-control styling initializer.

`check-choice-context-parity.mjs SHEETS PLAYWRIGHT REPORT` checks the exact bounded choices geometry context and standard mark/body anatomy, with stale/omission controls. `observe-token-fonts.mjs SHEETS PLAYWRIGHT REPORT` records computed typography and available Chromium platform-font identities. A computed stack is not proof of a loaded/used font; unavailable engine observations remain unknown, and locally installed fonts do not establish portable font availability.

A body-only observer may miss WebKit reveal after hidden content changes. Preview measurement also observes host inline-size transitions (including zero to visible width), and schedules height writes outside ResizeObserver delivery. Height-only host notifications do not request another write. Verify loaded growth, hidden-write avoidance and reveal recovery in each supported engine; filtering success alone does not establish this lifecycle.

## Semantic UI color review

The maintained `assets/recipes/semantic-colors.html` demonstrates profile roles on real fields and actions. Keep its stable `colors-profile-roles` review unit and exact recipe markup in Implementation. CSS aliases and applicable rules are declarations, not an invented per-role intent manifest. Context comes from the bounded color, surface, fields and actions source guidance. A missing required recipe or source selection must remain an error or explicit gap.

Run `check-semantic-colors.mjs SHEETS PLAYWRIGHT REPORT` against the generated artifact. Record enabled text, supporting text, field boundary, default/hover action, actual keyboard focus and disabled composed colors separately by scheme/state/environment. Use the normal-size 4.5:1 text baseline and 3:1 required boundary/focus baseline; do not silently lower thresholds. Inactive controls are exempt from enabled contrast thresholds, but surrounding enabled help/status is not. Alpha and opacity require explicit compositing, or an unsupported/inconclusive result. Real state reachability, contrast, focus area and full accessibility are separate claims.

Threshold references: [WCAG contrast minimum](https://www.w3.org/TR/WCAG22/#contrast-minimum) and [non-text contrast](https://www.w3.org/WAI/WCAG22/understanding/non-text-contrast.html). A scoped pair report does not certify all semantic roles, browser floors, assistive technology, native zoom or generative efficacy. Keep historical reports stale when their source or rendered inputs change; attach only matching reports through the evidence presentation step.

The semantic action specimen names primary, secondary and ghost appearances separately. Read `actions.colorStates` for their source pairings and test rest, hover, pressed and actual keyboard focus rather than duplicating rest screenshots. Busy is an actual local work/status lifecycle using the maintained semantic-colors controller. Its HTML starts disabled, and the controller enables only a complete fixture; unavailable scripting keeps the operation unavailable with an explanation. This controller owns example work, not component styling. Implementation includes its full code and dependency; artifact-bound evidence must hash `semantic-colors.js` as a required output. Record motion settings and final versus intermediate sampling explicitly.

The Index source chain lists selected authoritative paths and selection keys for each stage. Count each selection, including both typography and geometry; an absent narrative description is not a missing source declaration. Each stage's Implementation, Manifest and Context must select the same recorded sources. Reject missing, duplicated or misrouted selections. The generated-interfaces stage exposes the evaluation plan as guidance, while executed generation outcomes remain separately unavailable until compatible reports exist. Run `check-index-source-chain.mjs SHEETS PLAYWRIGHT REPORT` after changing chain routing.

## External work-register completeness

Use `build-sheets.mjs OUTPUT PLAYWRIGHT WORK_REGISTER` when the review scope includes a planning register. Omitting the optional third input produces a standalone source catalog; it does not account for that register. Run `check-sheet-work-register.mjs OUTPUT WORK_REGISTER` before publishing a registered review. It requires the exact external input bytes, unique IDs, all recorded items, reconciled completion counts and rendered finding anchors. Keep recorded completion separate from current artifact verification. Generic catalogs without a planning register may omit this input; never infer a complete review from a successful source-only build.

## Historical generation results

The optional fourth builder input is a `historical-generation-results` JSON bundle. With no planning register, use `-` in the register position. Each record names task, exact model/effort, frozen corpus manifests, scope and limitations. Task/model/effort must match selected protocol evidence. Result selections are JSON pointers into SHA-256-verified evidence files within the bundle. The generator copies those external files separately from source snapshots and displays their original selected values. Missing selections, changed bytes and unsupported current-acceptance claims fail the build.

Historical cohorts are useful evidence even when the current corpus has changed. Label their current-source applicability unverified; keep them separate from requirement checks and artifact-bound canonical evidence. A copied summary does not independently validate the study measurements. Unmet criteria and posthoc qualifications remain visible in selected records. Keep the confirmation task sealed; do not include its contents in a public review bundle.

Run `check-generation-history.mjs SHEETS PLAYWRIGHT REPORT` after importing a history bundle. It validates copied evidence identities, exact selected values, six no-script browser/width cases and importer corruption/omission controls. This verifies the presentation and its provenance, not an independent replication of study measurements.

Scheme-change checks must distinguish intermediate motion from settled colors. Shared link paint inherits the current surface foreground immediately; it excludes color interpolation while retaining other state paint. A dark screenshot captured during a transition is evidence of that intermediate frame, not proof of a persistent wrong token. Preserve both observations and verify immediate plus settled readability under normal and reduced motion.

Run `check-sheet-link-switch.mjs SHEETS PLAYWRIGHT REPORT` for visible ordinary Index links. It checks immediate inheritance and4.5:1 text contrast as well as settled color under normal/reduced motion, and restores the old color interpolation as a rejection control. The opaque shared Index surface is the bounded comparison; arbitrary translucent/colored surfaces need their own compositing checks.


## Pointer checks after native scrolling

When a keyboard action such as End starts native page scrolling, wait for observed parent and preview scroll positions to settle before a subsequent automated pointer action. Retain the intended native key and click sequence. Record the actual event target and focus result; an automation click can use coordinates calculated before scrolling finishes. Do not infer a component focus defect or disable scroll anchoring from that observation alone. Preserve the failed attempt and verify the same interaction after measured settling; a fixed sleep without observing stability does not establish the cause.

## Gaps and delivery snapshots

Render work items once in open, accepted-limitation or completed groups from explicit normalized register status. Completed work with accepted subpart limitations belongs in the accepted group, with its mixed scope explained; none of these counts is a defect total or a verification pass. Keep archived groups collapsed, preserve item anchors and reveal containing disclosures for deep links. Raw source observations remain separately scoped and mapped without adding work-item counts. Link long histories and shared source documents rather than repeating them per item; use CSS wrapping rather than per-character break markup. Capture the register bytes and identity at build time, then compare them with the canonical register before publication. An intervening change requires reconciliation or an affected rebuild; a static snapshot is not continuously synchronized. Run `check-gaps-delivery.mjs OUTPUT WORK_REGISTER PLAYWRIGHT REPORT` for disposition/count/anchor, snapshot and bounded presentation checks.

Gaps disposition filters use native `button.button__root` controls with label slots inside `cluster__root`, grouped by an accessible name. Use `aria-pressed` for one active filter: All, Open, Accepted limitations or Completed. Shared geometry owns padding, radius and wrapping. Filtering hides other disposition sections and announces the visible register count without changing the fragment or scrolling. Keep provenance available. Direct record/legacy fragment links reveal their group and ancestor disclosures. Without JavaScript, hide the inert filter group and show all disposition sections; native disclosures remain usable. These filters are not ARIA tabs.

## Component catalog presentation

The Components page supports visual review and trying interactions; it is not a human-engineer tutorial. Use readable names and short task-oriented descriptions as presentation labels, not new capability declarations. Group components by purpose, with plain family headings and only component entries collapsed initially. Never nest component entries inside category or reference accordions. Show the working example when a component opens. Keep code, declaration JSON, authored technical guidance and evidence within a closed Source & agent context disclosure. Put layout/subpart examples and shared references in a separate reference section. Preserve source identity, member coverage and full-page example links.

Defer preview document initialization until its component is revealed, and retain the same iframe when it closes so local state survives reopening. Search and fragment links must reveal their containing category/component; clearing search restores the prior expansion state. Collapse all must not delete example data. Without JavaScript, native disclosures and full-page links remain available. Run `check-component-catalog.mjs NEW_SHEETS BASELINE_SHEETS PLAYWRIGHT NEW_REPORT` for browsing, deferred loading, source-example parity, keyboard disclosure and no-script access. Historical page-layout tests assuming every preview is visible need their disclosures opened before behavioral checks; they are not evidence of the new collapsed view.

Component-family filtering reuses the Gaps disposition-filter pattern: native `button.button__root` controls with `data-slot="label"` in a named `cluster__root` group, one `aria-pressed` selection, and `secondary` on inactive controls. Show counts for All and each family. Selecting a family shows its family section without opening individual examples or changing the URL fragment. Search intersects the selected family; fragment navigation can select the destination family. Keep layout/system reference separate. Hide the inert filter group without scripts and retain native component disclosures. Shared CSS owns wrapping, focus and geometry; do not introduce custom pill styling.

## Output boundaries

Keep maintained sources, contracts, recipes and instructions in this skill’s existing structure. Use the existing `sheets/system-review` destination for canonical system-review publication; reuse its configured location rather than inventing another preview root. Do not create sibling review folders or treat historical previews as current destinations.

Generate verification/evaluation fixtures, candidate builds and disposable reports in unique `/private/tmp/*` directories. These files may be purged by the system over time; no cleanup schedule or durable availability is guaranteed. Keep staging separate from the canonical destination and source tree. Promote a verified candidate to the existing canonical destination through the publication workflow. Before linking temporary results as durable evidence, retain the required report/artifact bytes and identities in the existing evidence location. Do not leave canonical pages dependent on temporary files.

Preserve existing evidence, historical reports, accepted limitations and peer-owned files. Do not delete or relocate them as cleanup, overwrite a peer-owned destination, or repeat completed verification solely to change output location. Reconcile source ownership before publication; retain previous evidence without creating another public review destination.


## Documentation currency

Overview and Gaps expose a compact recent-update section from `references/reports/documentation-updates.json`. Its preserved report copies are hash-checked during build. These summaries are reported evidence, not a new replication or current-artifact acceptance. Keep later transfer results and remaining questions separate from the original work-register dispositions. Update this source when new publication or evaluation reports supersede the snapshot; do not edit rendered counts or close old limitations by inference. Keep raw coverage data, agent context and historical evaluation details in closed disclosures on the Overview. Preserve source-chain anchors and all source selections.

Colors begins with source palettes and semantic roles; seed JSON stays inside a closed provenance disclosure. Overview domain navigation uses shared card/grid geometry. These presentation changes preserve all source records and do not change tokens or specimen behavior.


## Split ownership

UI sources and pure token/color/component renderers are owned by base-ui. The current coordinator consumes synchronized views validated against ui-kit.lock.json and records kit identity in inventory.json. Gap/disposition/history inputs remain review-owned. Preserve the existing canonical destination and peer-owned live components.html.


### Split catalog ownership

The builder now calls base-ui `collectCatalog({playwright})` and pure UI renderers through the locked kit API. Kit collection has no review-installation dependency. Keep the review page shell, overview/gaps, demonstration guidance, work register and generation-history ingestion here. Inventory `sourceRoots` resolves each source owner; old inventories without it retain the original sourceRoot behavior. Do not copy review history into the standalone kit catalog.

After changing this seam, build into /private/tmp and use `check-catalog-boundary.mjs BEFORE_SHEETS AFTER_SHEETS STANDALONE_JSON` for data/specimen parity, source-owner identities and negative controls, followed by the affected sheet check. The standalone JSON comes from base-ui `build-catalog.mjs`. This does not authorize overwriting canonical or peer-owned live sheets.
