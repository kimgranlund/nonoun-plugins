# Base UI extraction and wireframe-review integration

Status: first compatible extraction installed and packaged; generated compatibility views retained.
Date: 2026-10-11
Scope: personal skills and their release/build interfaces. Implementation was subsequently authorized in this side conversation. No model evaluation or peer-owned sheet replacement was performed.

## 1. Outcome and design decision

Create two independently usable skills with a one-way implementation dependency:

- `base-ui` owns reusable UI foundations, components, interaction mechanics, contracts, recipes, discovery and component verification.
- `wireframe-review` owns alternative proposals, review identity, preview composition, annotations, feedback and review-artifact delivery. It consumes the actual base UI package.
- `generative-systems` remains methodology for developing and evaluating either system. It is not a mandatory runtime or author-context dependency.

Done means the same maintained component recipe renders and behaves correctly standalone and in the review tool, without a second maintained implementation, while previous review manifests/controllers remain supported through a compatibility adapter. Package identity, evidence scope and existing limitations remain explicit.

Non-goals: new framework, conversion to web components, broad CSS renaming, redesigned tokens, new component inventory, replacement of existing review schema, historical-evidence relocation, or another broad model benchmark.

## 2. Research and implications

| Primary source | Relevant observation | Decision for this system |
| --- | --- | --- |
| [Adobe Spectrum architecture RFC](https://github.com/adobe/react-spectrum/blob/main/rfcs/2019-v3-architecture.md) | Separates state, behavior and themed components. This is a historical architecture proposal, not a requirement to adopt React. | Split reusable behavior from review-host lifecycle; preserve existing vanilla implementation. |
| [Node package entry points](https://nodejs.org/api/packages.html#package-entry-points) | Explicit exports define supported package entry points; adding exports can break previously available deep imports. | Inventory callers first; introduce stable entry points and temporary compatibility forwarding. Export maps are not a filesystem security boundary. |
| [Shoelace installation](https://shoelace.style/getting-started/installation) | Supports selected component imports and requires asset base-path handling in relevant configurations; warns against depending on generated internals. | Publish explicit asset/dependency metadata and a stable consumer API. Do not make consumers infer internal paths. |
| [Storybook publication](https://storybook.js.org/docs/sharing/publish-storybook) | Produces a static build for deployment. | Treat documentation/catalog output as a derived consumer of components. Do not make catalog code the component runtime. No Storybook adoption proposed. |
| [Base UI quick start](https://base-ui.com/react/overview/quick-start) | An existing React component library uses the Base UI name and `@base-ui/react`. | Local `base-ui` is a working skill name, not a dependency on that library. Select a distinct namespace before public package publication. |

These are architectural precedents. Proposed interfaces and migration gates below are local design decisions, not claims that another framework validates this implementation.

## 3. Current coupling confirmed by source inspection

Paths below are relative to the installed `wireframe-review` skill.

- `scripts/build.mjs` directly reads four foundation stylesheets plus `assets/wireframe.css`; concatenates `control-markup.mjs`, `prototype-runtime.js`, authored controllers, model and app; and compiles both proposal and shell control markup.
- `scripts/generate.mjs` imports its `root` from `scripts/token-index.mjs`. Moving token indexing without separating root ownership could redirect generation to the wrong scripts directory.
- `scripts/token-index.mjs` combines foundation indexing with `tokenCheck(manifest, index)`, which traverses the review-specific unit/variant shape.
- `assets/prototype-runtime.js` combines state/reducer/render/bind lifecycle with `[data-unit-id]`, variant-specific state keys, read-only views, registration and optional business-plan helpers.
- `scripts/component-context.mjs` already supports `--root`, validates source containment, reports source hashes and bounds record batches. Preserve these useful properties.
- `scripts/build-sheets.mjs` directly reads style sources, recipes and contracts, copies source excerpts and records source identity. It also serves delivery/gap records with a different owner from UI documentation.

The recent disposable-kit DOM study does not establish full wireframe fidelity. Its UA fieldset geometry, omitted field grouping and native heading scale must not be carried into a new base UI implementation. Extract the actual maintained system; keep disposable studies as historical behavioral/context evidence.

## 4. Ownership map

| Existing material | Destination / treatment |
| --- | --- |
| `assets/foundation/**`, token-source provenance and licenses | base-ui; keep upstream provenance and generation ownership intact |
| UI portions of `assets/wireframe.css` | base-ui; keep current filename/classes initially |
| `references/style/**` | classify individually: component/style owners to base-ui; review integration stays with wireframe |
| `assets/icons/**`, control markup/compiler | base-ui |
| Component recipes and demonstration contracts | base-ui; remove dependence on review host through explicit standalone adapters |
| Generic reducer/render/bind lifecycle and focus helper | base-ui runtime |
| `registerPrototype`, unit/variant identity, read-only review adapter | wireframe-review compatibility/host adapter |
| Approval-plan helpers | optional workflow recipe/module; never mandatory base runtime business policy |
| `assets/app.mjs`, `model.mjs`, review shell, manifest/feedback schemas | wireframe-review |
| Shell-specific layout CSS | wireframe-review; primitive controls consume base-ui |
| Token scanner and component rules | base-ui; accept UI inputs without review manifest knowledge |
| Review manifest traversal, review-ID checks, feedback checks | wireframe-review; adapt into base validation inputs |
| Component/color/token sheets and specimen construction | base-ui-owned generator modules |
| Gap/disposition ledger, delivery records and historical evidence | retain existing owner/path; composed documentation may link them |
| Generation/revision orchestration | wireframe-review for review artifacts; base-ui gets only the standalone assembly needed for UI consumption |

Do not move entire directories solely by name. Phase 0 must classify every file and caller; this table is a starting allocation, not a complete inventory.

## 5. Dependency and release contract

Maintain one authoritative base-ui source. Consumers use an explicit resolved root and public interface. No writes to a sibling skill during ordinary generation.

Recommended resolution:

1. Explicit `--ui-kit ROOT` when supplied, validated against compatibility and any lock.
2. Otherwise the installed sibling `base-ui`, resolved relative to the skill location.
3. If absent or incompatible, stop before emission with an actionable diagnostic. No silent fallback to stale copied CSS or network installation.

A reproducible project build uses a lock containing exact kit identity and content hash. A compatible major alone is insufficient to reproduce an older artifact. Changing the resolved kit updates the lock through an intentional upgrade step, never silently.

Proposed descriptor fields: `schemaVersion`, `packageId`, `version`, `runtimeApiVersion`, `capabilities`, public entries, asset dependency closure and per-file hashes. Distinguish descriptor schema compatibility from runtime API compatibility and package release version. Hashes verify identity/integrity, not trust in an arbitrary root.

Publish separate skill ZIPs plus, if needed, a convenience archive containing both sibling folders. The combined archive is assembled from the same release bytes. Avoid vendoring an independently maintained UI tree inside wireframe-review. Capture compatible versions in release verification.

Generated review artifacts embed the required kit closure and adapter, with recorded source/version/hash metadata. They must continue to open after installation folders move or disappear. External URLs, fonts and dynamic assets must be explicitly declared; preserve the existing font-fallback limitations.

## 6. Proposed public API and runtime boundary

These names are design targets, not existing APIs:

- `describeKit(root)`: descriptor and capability identity.
- `getComponentContext(ids, options)`: bounded contracts with dependencies/provenance.
- `compileControls(html, options)`: idempotent native-control markup compilation.
- `getAssetBundle(profile, capabilities)`: ordered CSS/runtime/icon closure for embedding.
- `validateUI({html, css, capabilities}, options)`: UI findings independent of review schema.
- `mount({root, definition, store, stateKey, readOnly})`: a scoped view handle with cleanup. Exact signature to be finalized against current lifecycle semantics before extraction.

The review adapter continues exposing existing authored `registerPrototype` semantics during migration. It maps unit/variant identity to explicit state keys, owns view replacement and supplies read-only policy. Base-ui owns dispatch/render/bind cleanup mechanics and operates on a caller-supplied mounted root.

Required preserved behavior: multiple views sharing the same intended state key repaint together; different proposals stay isolated; repeated mounts do not accumulate listeners; read-only views cannot mutate state; heading focus uses the owning document and only committed transitions. Controllers are trusted author code, not sandboxed code. Extraction must not create a new security claim.

CSS classes/tokens including `wf-*` remain stable during extraction. Root scoping must preserve product/content typography and prevent shell styles leaking into previews. Renaming is a separate compatibility project after the split is stable.

## 7. Context routes

Base-ui entry: intended surface/profile → used component families → exact anatomy/dependencies → optional adaptation recipe → affected checks.

Wireframe entry: review task and variant intent → review source/schema seam → base-ui bounded records → review controller adapter when needed → generation and review acceptance.

Read shared constraints once. Existing source and duplicate recipes are not both default input. Retrieve a recipe to resolve an adaptation gap. Keep historical reports and generative-systems methodology out of routine author context. Dependency loading must be explicit; do not assume invoking one skill automatically loads another.

Migration acceptance must cover route fidelity as well as imports: instructions and examples must point to public kit entries, and code output must actually use their anatomy. Measure retrieval bytes separately from diagnostic output and task outcomes. No speed target is asserted before measurements.

## 8. Phased migration checklist

### Phase 0: freeze and classify

- [x] Snapshot current installed skills, release hashes, canonical sheet identity and peer reservations.
- [x] Produce file ownership/caller inventory, including CLI callers, tests, recipes and docs.
- [x] Select a compact fixture set from existing evidence; declare which checks can be reused.
- [x] Record old paths requiring forwarding and public naming decision.

Exit: every affected file has one owner; no unresolved dual ownership in runtime, token indexing or sheets.

### Phase 1: introduce boundaries in place

- [x] Separate review-tool root resolution from token-index root.
- [x] Split review-manifest traversal from generic token/UI inspection.
- [x] Add descriptor and public entry facade around existing bytes.
- [x] Define runtime store/stateKey/view lifecycle and review adapter semantics.
- [x] Check consumers through facade without changing emitted component behavior.

Exit: wireframe build can use an explicit kit root through public entries; no folder moves needed yet.

### Phase 2: extract base-ui

- [x] Move classified owners into base-ui; retain required provenance/licenses.
- [x] Provide standalone assembly and one maintained specimen per selected fixture.
- [x] Replace old entry points with small forwarding adapters where compatibility requires them.
- [x] Make missing/version-mismatched dependency failures actionable.
- [x] Validate standalone base-ui with wireframe-review unavailable in an isolated test workspace.

Exit: base-ui functions independently; no reverse runtime imports.

### Phase 3: integrate and dogfood

- [x] Build proposals, static fallback and shell controls from the same resolved kit.
- [x] Preserve existing manifest/controller/feedback interfaces via review adapter.
- [x] Verify state isolation, cleanup, read-only behavior and focus transfer.
- [x] Compare standalone/review recipe geometry, type, color and interaction in equivalent contexts.
- [x] Verify portable emitted artifacts without access to either installed skill.

Exit: same recipe, same kit bytes, supported behavior in both hosts; no local component reimplementation.

### Phase 4: docs and catalog ownership

- [x] Give UI sheet generation explicit base-ui source roots and provenance.
- [x] Keep the existing canonical `sheets/system-review` destination and deep links during migration.
- [x] Preserve peer-owned live `components.html`; stage integration separately until ownership handoff.
- [x] Keep delivery/gap ledgers and historical evidence at existing paths.
- [x] Update skill routes, examples and compatibility notices; check local links.

Exit: published current documentation identifies its owner; historical material remains historical.

### Phase 5: qualify and release

- [x] Run affected unit/component/adapter checks and negative controls below.
- [x] Validate each ZIP and extracted file parity; qualify missing dependency behavior.
- [ ] Publish refreshed canonical sheets after peer coordination. Staged sheet assembly passed; existing published sheets remain untouched.
- [x] Archive old releases; publish a tested compatible pair and exact identity records.
- [x] Document rollback and remaining limitations; retire forwarding only in a later explicit compatibility change.

Exit: criteria-to-evidence matrix complete, with unverified environments explicitly retained.

## 9. Acceptance and negative controls

| Criterion | Positive evidence | Discriminating fault |
| --- | --- | --- |
| Dependency direction | standalone kit builds without review installation | a reverse import is detected |
| Resolution and identity | explicit/installed root resolves exact compatible descriptor | missing kit, incompatible API or lock/hash mismatch blocks before emission |
| Single UI authority | standalone + review share source asset hashes | altered embedded asset fails parity |
| Compatibility | retained representative manifests/controllers/feedback still work | wrong unit/variant mapping reveals state bleed |
| Lifecycle | remount preserves state and single dispatch; cleanup runs | duplicate listeners or skipped cleanup fail |
| Read-only mode | render works, actions cannot mutate state | dispatch allowed in review mode fails |
| Dogfooding | product heading, field group, actions, select, choices and disclosure use declared geometry/state roles | omit field wrapper, allow UA fieldset border, or substitute literal geometry; relevant check fails |
| Validation recovery | all affected controls/groups stay associated until predicate resolves | unrelated same-group edit clearing an active error fails |
| Portability | emitted artifact opens with installed roots inaccessible | unresolved local asset import fails |
| Context | public bounded records carry needed prerequisites | missing dependency signature or private-file route is detected |
| Packaging | archive membership and extracted hashes match declared source closure | changed byte or missing asset fails |

Reuse tests only where source, dependency, criteria and environment still match. UI-source byte parity does not waive adapter integration testing. Do not repeat all model studies to validate a file move. Consider one separately authorized actual-kit generation/revision probe only after deterministic integration is stable.

## 10. Rollback, evidence and decisions

Rollback the compatible release pair and resolver/adapter configuration together. Retain new failed artifacts and diagnostics; never replace historical evidence with repaired output. Do not overwrite an original project artifact during migration. Freeze further phase advancement on identity drift, unresolved reverse dependency, changed feedback identity or peer ownership conflict.

Accepted limitations survive extraction with their original scope. Passing new integration checks does not certify screen readers, physical devices, all browsers or fresh-generation reliability. Experimental context packages remain unpromoted.

Defaults proposed for review: local name base-ui; stable wf-* API; explicit kit root plus installed sibling resolution; separate ZIPs; existing canonical review destination. Decisions required before release: distinct public package namespace if publishing beyond local skills, minimum supported runtime versions, and compatibility-forwarding retirement policy. These do not block Phase 0 inventory.

## 11. Source traceability

Local files inspected on 2026-10-11: wireframe-review `scripts/build.mjs`, `generate.mjs`, `token-index.mjs`, `component-context.mjs`, `build-sheets.mjs`, `compile-controls.mjs`, `assets/prototype-runtime.js`, `assets/wireframe.css`, and `references/workflows/build-core.md`. Methodology: generative-systems `references/context-architecture.md` and `materials-and-contracts.md`.

This file remains optional architecture context. Implementation details and scoped verification are recorded in the wireframe-review extraction report; it is not a mandatory authoring packet.


## 12. Implemented first-release choices

The public kit facade is scripts/api.mjs; generic runtime uses createUIRuntime().mount({root, definition, stateKey, readOnly}). Existing wf-* classes stay intact. Exact kit identity is locked. Generated compatibility views, validated before consumption, preserve old source paths without symlinks or independently editable UI source. Node 22+ is the stated CLI floor; the performed checks used Node 24.9.0. No public npm namespace is claimed.

Base-owned catalog collection and pure UI sheet renderers are consumed directly through the locked kit API by the retained review page assembler. Standalone base-ui has no reverse runtime dependency; optional historical/review documentation links are explicitly labelled. Standalone UI checks have since moved to base-ui with forwarding review entry points; the UI extraction coordinator is now base-owned; review page/status/history assembly intentionally remains review-owned. The canonical sheet publication checkbox remains open to preserve peer ownership.

Report: extraction report (`design:wireframe-review` skill, `resources/reports/base-ui-extraction-2026-10-11/report.md`). Peer message: paste-ready handoff (`design:wireframe-review` skill, `resources/reports/base-ui-extraction-2026-10-11/peer-message.md`).


Follow-up evidence: icon generation and UI check ownership (`design:base-ui` skill, `resources/reports/check-ownership-2026-10-11/report.md`). The icon-generator parity failure is resolved without CSS changes; the pre-existing stepper state-vocabulary mismatch was subsequently corrected by declaring current/completed/upcoming, with omission controls.

Current follow-up: catalog boundary and vocabulary (`design:base-ui` skill, `resources/reports/catalog-boundary-2026-10-11/report.md`). Canonical sheet publication remains unperformed to preserve peer ownership.
