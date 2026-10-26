# Page stylesheet contract

Scope: generated pages. Store page content, source, styles and runtime in the consuming project. The reference site lives in /Users/kimba/Projects/ui-kit/apps/site/. Maintain one version in place.

## New consumer generation

Run `python3 scripts/run.py build-page.mjs FRAGMENT.html NEW_DIRECTORY [CONTROLLER.js]` from the kit (use an absolute launcher path elsewhere). This one-time scaffold validates token references and classic controller syntax, compiles maintained controls, and copies actual offline font declarations, kit CSS and runtime into the consumer. Fragment style blocks become styles/pages/page.css. The optional controller is a classic script sharing the runtime's helper scope; module imports need a consumer-owned build.

The directory must not exist, even if empty. Subsequent changes belong in its editable HTML, CSS and controller; rerunning this scaffold never overwrites or reseeds them. styles/index.css imports the recipe barrel and page arrangement; the recipe barrel imports shared/index.css once. Add recipe imports to styles/recipes/index.css. A kit refresh is a deliberate vendor/runtime update followed by affected checks. For an explicitly single-file export only, use build.mjs instead.

Generation is a draft, with index.html.review-status.json. Review index.html using the rendered audit and delivery gate; its transitive local stylesheets and scripts are bound with it. Deliver the entire directory. The targeted maintainer check is `python3 scripts/run.py check-build-page.mjs PLAYWRIGHT [CHROME]`; it checks offline loading and editing/binding behavior, not visual acceptance.

## Files and ownership

| File | Owner | Required content |
|---|---|---|
| styles/index.css | Page | Ordered imports. The HTML loads this barrel once. |
| styles/vendor/tokens.css | System projection | Source tokens, derived units, geometry and typography. |
| styles/shared/tokens.css | Page/system mapping | Authored source colors and semantic mappings; do not duplicate geometry formulas. |
| styles/shared/recipe-tokens.css | Recipe mapping | Explicit recipe semantic palette. |
| styles/vendor/fonts.css | System projection | Offline font declarations. |
| styles/vendor/kit.css | Shared compatibility layer | Maintained base-ui rules. Refresh only when adopting a kit change. |
| styles/recipes/RECIPE.css | Component recipe | Slot, variant and state rules for one generated component. |
| styles/pages/PAGE.css | Page composition | Page-specific arrangement, including Home hero layout. |
| styles/shared/index.css | Shared barrel | Ordered vendor, mapping, common layout and component imports. |
| styles/recipes/index.css | Recipe barrel | Shared imports plus recipe styles; exclude reference-only page layouts. |
| styles/shared/core.css | Page | Page layout, section arrangement and page-only patterns. |

Rule STYLE-01. When changing a component, edit its stylesheet. Do not regenerate the entire page to change CSS.

Rule STYLE-02. Create styles in their owning directories. HTML builds preserve authored styles and must not reseed or overwrite them. The reference build does not seed styles; a missing stylesheet requires explicit repair. A deliberate kit refresh must identify affected files.

Rule STYLE-03. Keep the import order explicit. Keep vendor compatibility rules separate from authored component rules. Component-local calculated variables may remain beside their recipe; shared design tokens belong in tokens.css.

Rule NAME-01. Use component__slot classes. Use data attributes for variants and ARIA/native attributes for state. Preserve maintained recipe__slot aliases where required by the runtime.

Rule TEXT-01. Write rules as Scope, Condition, Requirement, Exception and Verification when those fields add information. Use one normative statement per rule. Name the owner. Define symbols before formulas. Separate adopted behavior from proposals and examples.

Rule REVIEW-01. Bind local CSS imports and scripts with the HTML during review. Any bound asset change invalidates that review. Copy the same asset tree when delivering the page.

Reference: [interaction colors and states](interaction-states.md). Geometry authority: [geometry contract](../../../../Projects/ui-kit/docs/system/geometry-contract.md).

## Heading, description and data layout

Scope: explanatory sections with a heading, prose and a related spec list. This pattern does not change Card/Tile header-body-footer flow rules.

Rule LAYOUT-01. Place the semantic heading in its own grid row, spanning the description and data columns. Use the same semantic heading color as peer headings. Muted description color must not leak into the heading.

Rule LAYOUT-02. Place the description and spec list in the next row. Align their outer top edges with align-items:start. Do not align the data list with the heading or vertically center it beside the prose.

Rule LAYOUT-03. Let the description fill its available column. Remove a generic intro max-width for this pattern; do not constrain it to a second narrow measure within the column. Use two equal minmax(0, 1fr) columns, a 4d column gutter and a d row gutter for the reference pattern.

Rule LAYOUT-04. When columns no longer accommodate content, use one column in reading order: heading, description, data list. Keep internal spec rows as label/value pairs with wrapping. Choose the breakpoint for content fit; do not copy a screenshot width as a universal breakpoint.

Rule DATA-01. Component spec lists use the [compact specification data-list contract](../../../../Projects/ui-kit/docs/system/geometry-contract.md#compact-specification-data-lists-adopted). Numeric, text and formula values share the same row pattern. Preserve bold labels, trailing value alignment and the existing semantic text/border roles.

Ownership: styles/shared/core.css owns the section grid and heading treatment. styles/recipes/data-list.css owns spec-row layout. New recipes use component__slot naming; existing maintained selectors may remain compatible.

Verification: at wide and narrow widths, check heading color against a peer heading, description width against its grid column, top alignment of prose/list when side by side, wrapping of long formulas, reading order, and absence of horizontal overflow. Current specimen: [reference site](../../../../Projects/ui-kit/apps/site/index.html), curvature summary and component specs.

## Reorganized reference sources

The maintained site separates source/pages/ (templates and per-page recipe modules), source/runtime/ (interactions), and source/shared/ (rendering and spec helpers). scripts/build.mjs assembles generated index.html, app.js, recipes.js, recipes/*.html and manifest.json. CSS remains independently authored. Keep public page URLs stable and update imports, manifests, checker registrations and discovery docs together when moving owners. Historical review evidence retains its original paths and hashes.

For the specific four-example Home composition, follow the [Home hero contract](../../../../Projects/ui-kit/apps/site/docs/home-hero.md). Its on-canvas measurement annotations are a scoped teaching exception, not a reason to move ordinary headings and descriptions into every artifact.

## Canvas and control containment

Rule SELECT-01. For a maintained native select, apply width constraints to select__root/select__root and keep the select filling that wrapper. Do not override the child to width:auto while its indicator remains anchored to the wider wrapper. The indicator must lie inside the visible select frame. Check actual compiled geometry at narrow widths and enlarged text using SELECT_INDICATOR_BOUNDS, SELECT_ANATOMY and SELECT_TEXT_FIT; valid anatomy alone does not establish containment. See the [native-select contract](style/select/contract.json).

Rule DATA-02. Teaching specification lists describe the demonstration and stay outside its grid canvas. Group the example canvas and its adjacent specification in a page-owned wrapper. In the reference recipe helper, use section(id, title, description, body, specification): the fifth argument renders as recipe__specification[data-context=outside], beside recipe__example under recipe__demo. Do not concatenate teaching spec lists into body.

Exception: real product data, including invoice totals, belongs inside its reusable artifact. Do not extract every data list based on its tag or class. Home's height/width/radius annotations remain the explicitly authorized on-canvas teaching exception; see the [Home hero contract](../../../../Projects/ui-kit/apps/site/docs/home-hero.md).

Verification: inspect the example/spec boundary at narrow and wide widths, including long formula wrapping. Confirm teaching lists have no canvas ancestor, product totals remain inside the invoice, and Home annotations still track the measured control. Shared audit select bounds are automated; deciding teaching versus product content remains an author review obligation.
