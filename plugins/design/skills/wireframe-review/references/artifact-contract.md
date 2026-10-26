# Artifact and composition contract

## Files and identity

The editable manifest follows `manifest.schema.json`. `projectId` remains stable across a project; `revision` changes when rendered design or target identity changes. Use a small explicit value such as `r1` or a source hash. The artifact embeds its manifest and schemas so it opens without adjacent files.

A decision unit has a stable `id`, a `kind` (`page`, `section`, or `component`), a title, and one to three variants with contiguous ordered IDs starting at A. Default to A/B/C; use A alone or A/B when the user requests fewer proposals. A variant has a title, rationale, tradeoff, HTML, and composition. Page variants use a nonempty composition and empty HTML. Leaf variants use nonempty HTML and an empty composition. Compositions reference only leaf units, with each leaf occurring once per page variant. This keeps the starter's override semantics deterministic; extend the model deliberately if nested/repeated components are needed.

Example: `home` page proposal B composes `header:A`, `hero:C`, `proof:B`, `footer:A`. The reviewer can globally choose footer C and override hero B only on home. Resolution order is page proposal defaults, global leaf selections, then per-page overrides. Switching page proposals preserves overrides; overrides for absent units are retained but inactive. Show that state rather than losing the choice.

A page's default proposal A and its child variants are preview fallbacks, not recorded approvals. Every unit has a choice record with nullable `selectedVariant`, explicit per-variant review states, and notes. Selecting a rejected variant clears that rejection; rejecting a selected variant clears the selection.

## HTML authoring

Use semantic HTML and the default CSS primitives (`section__root`, `grid__root`, `card__root`, `media__root`, `actions__root`, `button__root`) or supply project CSS in `css`. The shell's grayscale example is a starting point, not a mandated visual language. Set descriptive `data-review-id` attributes on useful nested targets. IDs must be unique within one unit/variant. Reuse an ID across A/B/C only when it means the same conceptual element. Changing wording need not change its ID; replacing its purpose should.

The preview wraps every leaf in `data-unit-id` and `data-variant-id`. Element identity is the tuple `(projectId, revision, unitId, variantId, elementId)`. A page context identifies where a shared component was reviewed. x/y are normalized within the element (0 to 1), not page pixels. Missing targets stay in the feedback list; do not reattach to the nearest DOM node.

Embed images/fonts as data URLs when needed; the default iframe policy blocks external network resources.

Wireframe markup is rendered in a sandboxed iframe with same-origin access for parent annotation listeners, but no script permission. Use `data-page-id="page-id"` on a link/button for starter navigation. It navigates in Browse mode and becomes an annotation target in Annotate mode. Other links/forms are inert in the starter. Specify additional interactions in the task manifest/brief and implement them through the [supported local controller](style/prototype-runtime.md) if required; do not claim this shell simulates form submission or application logic.

## Intent and application flows

Use the [design corpus](design/index.md) to establish goals and content responsibilities before deriving a new surface inventory. A companion intent brief is authoring context, not runtime JSON: the current manifest rejects unknown fields. Application screen states may use page units with stable state-specific IDs; record transitions and compatibility in the brief. Do not claim task completion, permissions, real submissions or state machines from static navigation. If a flow's alternatives cannot safely mix leaf choices, explain that boundary and adapt the model before promising enforced compatibility.

## Delivery and testing

Default scope is all agreed pages with three proposals per decision unit. For large sites, start with representative templates only if the user agreed to that scope; do not silently omit requested pages. The same shell can review one component, an application screen, a dialog family, or a whole website. Leaf-only manifests are supported.

Deliver the HTML, its manifest, and the schema when useful for integrations. A user only needs the HTML to review and the exported JSON to give bulk feedback. Keep the original manifest/revision available to interpret that JSON.

Browser checks should include actual chosen composition, element annotations in the iframe, variant persistence, import round trip, keyboard use, and narrow host width. Unit tests do not prove these. For publication, follow the user's hosting choice and authorization; self-contained does not imply publicly hosted.

## Intent context and interchange 1.1

Manifests accept 1.0 and 1.1. For intent-aware artifacts use 1.1 with optional `intent` at artifact and unit levels. Each supplied intent requires `outcome`; optional prose fields are `means`, `constraints`, `uncertainty`, and `evidence`. Omit unsupported detail. These communicate desired progress, available support, consequential limits, unknowns and ways to evaluate success. Evidence may include a defined KPI with guardrails, but a static review cannot establish business impact. No mandatory metrics or exhaustive brief per component.

The panel progressively discloses artifact, containing-page and current-unit context together; absent local context is not invented. Existing rationale/tradeoff fields describe each variant's hypothesis. Keep substantive intent or hypothesis changes under a new design revision.

New exports use feedback 1.1 and include a `context` snapshot: artifact intent plus each unit's ID, title, optional intent and the supplied proposal titles/rationales/tradeoffs. This preserves interpretable references without exporting HTML. A snapshot must match the supplied manifest. The bundled reader also accepts legacy 1.0 reviews without context; exporting them adds the current manifest context and writes 1.1. Old readers need upgrading before reading 1.1.

New comment scope `decision` targets a unit across alternatives with optional page context and null variant, element and position. It supports missing approaches and conditional feedback without assigning a vote. Existing proposal and element scopes remain precise.

Optional manifest `defaultViewport` sets the initial desktop or mobile preview. Mobile-first specimens can open at the mobile logical viewport while retaining full wrapper-width scaling. Reviewers can still switch viewport; navigation does not change it.

In contextual Browse mode, native text entry, radio/checkbox selection, selects and disclosures can be tried locally. Internal fragment citations navigate and focus their existing target. External links, form submissions and file/action inputs remain blocked by the preview controller. In Annotate mode, interaction targets feedback instead. These native form values are transient prototype state, not review data; rerendering may reset them. Do not imply that choosing a mission option grants operational approval.

Optional `language` is a hyphenated language tag (for example `en` or `sv-SE`), defaulting to `en`. It sets document and preview language metadata; it does not translate the review shell.

## Interaction declarations

Optional `interactions` describe promises, not proof. Each entry has a unique `id`, leaf `unitId`, `variantId` (A/B/C), existing `elementId`, `status` (implemented/static/unavailable), `action`, `expectedResult`, `persistence` (none/current-view/session/reload), and `limitations` array. Static/unavailable entries require a limitation. Declare each relevant variant separately. An editable quantity must identify the observable value change; if totals are illustrative say so in limitations and the UI. Validation resolves targets but does not execute behavior. No declarations does not mean there are no interactions. This is an optional backward-compatible addition to the current artifact schema; older schema copies may reject it.

`verify-artifact.mjs MANIFEST HTML NEW_REPORT` writes a schema-validated static report with byte hashes and explicit untested interactions. A browser evaluator must add coverage and evidence for actual behavior; never promote declarations to passes. Existing reports are not overwritten.

Proposal-count verification: `scripts/check-proposal-count.mjs PLAYWRIGHT OUTPUT` covers one/two/three-proposal rendering and feedback round trips. Each unit state record contains only its actual proposal IDs; selections, overrides and compositions cannot reference an absent proposal. Existing three-proposal manifests and reviews retain their behavior.

## Reuse and evidence boundaries

Preserve the task’s fixed fixture, baseline identity, token source and required assets while varying requested design decisions. Shared review-shell snapshot/export behavior belongs to the builder, not proposal click handlers. Use scoped controller callbacks for domain behavior. For customization seams and state-specific surface measurement records, see [reuse and measured surfaces](workflows/reuse-and-measure.md). These records belong to evaluator evidence; they do not extend the manifest schema.
