# Build and verify

The default authoring route is [generation core](build-core.md). Read affected sections here for delivery checks or troubleshooting. Resolve SKILL to the installed skill directory. Start from assets/minimal.manifest.json; open references/artifact-contract.md only for unresolved composition/interchange details. Build with:

```sh
node "$SKILL/scripts/generate.mjs" manifest.json new-output-directory /absolute/path/to/playwright
```

This is the standard generation command. Supply the available Playwright module path; if unavailable, generation fails rather than skipping lint. Optional `--controller controller.js`, `--review review.json` and `--policy lint-policy.json` are forwarded from captured inputs. It builds in staging, validates the emitted manifest/artifact and token references, runs document-reference/style lint, then publishes `artifact.html`, source/compiled manifests, `verification.json`, `lint.json` and `generation.json` together. An existing output directory is rejected. Failed gates retain diagnostics in a staging directory and do not publish the requested destination. Fix the source and retry to a fresh destination; do not deliver a failed staging artifact.

Read `generation.json`: errors block output; style warnings are advisory and dynamic-reference deferrals remain explicitly unverified. This automatic gate does not replace the interaction, visual and environment acceptance below. See [preventive checks](preventive-checks.md) for rule scope and narrow deferrals.

`build.mjs` remains the low-level draft compiler for isolated fixtures and debugging. Its successful exit alone does not establish delivery readiness.

The optional `--review` input is validated initial review JSON. Browser-saved feedback of the same revision takes precedence. A changed reviewed design needs a new revision; preserve its previous package and explicitly map retained feedback. Shell-only corrections need not change design identity.

## Acceptance before implementation

Extract every required operation and state from the brief before writing the manifest. Keep that acceptance list separate from generator-selected interaction declarations. For each item record its UI entry, expected transition and browser evidence or explicit failure/untested status. Static placeholders cannot satisfy required behavior. In evaluations, the evaluator owns this list; the generator must not remove requirements to match its output.

Inspect visible controls as well as declared interactions. Check menus, scope-changing edits, disabled choices, both color schemes and sibling spacing. A passing declaration report is insufficient when the brief or visible UI contains untested operations. Use the [independent acceptance runner](../evaluation-checks.md) for evaluator-owned requirements, targeted contrast/gaps, menus and visible-control coverage. It does not infer omitted requirements: the evaluator must derive them from the brief. The existing declared-interaction gate alone does not cover these checks.

## Long collections and persistent actions

For selection followed by a required form, read [bounded selection with an adjacent task](../style/composition.md#bounded-selection-with-an-adjacent-task). Choose document flow, staged tasks or a named bounded collection region according to the task. Keep all content and native keyboard access. Check collapsed, expanded, invalid and enlarged states; measure grouping and task completion separately from shortcut access. Verify that focused controls remain visible and hit-testable above persistent chrome. Do not treat body padding or a full-page capture as proof. Verify the fixed authored recipe with `node scripts/check-bounded-collection-task.mjs PLAYWRIGHT NEW_OUTPUT`; pass a supplied Playwright module path and a fresh output directory. `--help` is read-only. Its synthetic doubled-text cases are not native zoom or generation acceptance.

## Automatic baseline

Builder rejects unresolved token references and malformed assembled JavaScript before writing output. Builder: doctype, charset, viewport, language (manifest.language; default en), foundation embedding, review controls, isolated previews and portable feedback. Language metadata does not translate interface strings. CSS: border-box including pseudo-elements, body typography/colors/margin reset, responsive media, geometry-based controls and radio/checkbox sizing, label roles, focus rings, fixed icon slots and hidden scrollbars. Preview body uses natural height; only the review shell owns viewport scroll lock. Reduced-motion media handling prevents smooth document scrolling; authored animation still needs an appropriate reduction strategy.

## Author decisions

- Audience, task, content responsibilities, meaningful variants and realistic edge states.
- Correct language, names, headings, image alternatives, keyboard semantics and interaction boundaries.
- Appropriate semantic roles, hierarchy, density and responsive composition; inherited contexts override only selected axes.
- Actual font availability: the typography snapshot references preferred fonts but ships no font files. Platform fallbacks apply. Bundle licensed fonts separately if exact metrics matter.
- Stable review IDs and complete routes; no real submissions or external operations in specimens.

## Delivery gate

Validate the manifest; render desktop/mobile and both schemes; inspect long text, media, empty states, radios/checkboxes, disabled controls, focus and overlays. Confirm no clipping, unintended horizontal overflow, stretched glyphs or layout movement between states. Test keyboard operation, annotations and export/import. Verify scroll continuity and context selection when touching the shell. At 200% zoom, content and controls must remain reachable. Run reduced-motion checks if motion is authored. Record unavailable browser coverage rather than treating it as passed.

The token-reference preflight detects unknown `var()` references, including references with fallbacks against bundled and authored declarations. It is a lexical check, not a CSS cascade evaluator, semantic-pair check or contrast test. Review custom fallback usage explicitly; do not hide mistakes behind fallback literals.

For standalone HTML outside the review builder, run `node scripts/check-standalone-token-refs.mjs ARTIFACT.html LINKED.css ...`, passing every linked CSS file. It checks references even inside fallbacks: an invented semantic name must not silently inherit or fall back. Locally declared custom properties are permitted. The check excludes implementation snippets and scripts; runtime-injected styles, scoped availability, foreground/background pairing and actual paint still need separate verification.

Token names are generated in references/style/token-index.json. Read only the relevant group through `generate-token-index.mjs --group color` (typography/geometry/layout/profile also available); the full index is validator input. Regenerate with generate-token-index.mjs after foundation changes and check freshness with --check. `--help`, `--check` and `--group NAME` are read-only; unknown or combined options fail without writing. Local declarations may extend the set; lexical reference validity is not permitted-role or contrast proof.

Use `--controller controller.js` with generate.mjs for required local behavior; read only its Controller interface and User activation and form defaults sections, plus Local save and restore or Bounded approval when used. Never post-process closing body/script tags. After complete assembly run `node scripts/verify-rendered.mjs OUTPUT/manifest.json OUTPUT/artifact.html NEW_REPORT PLAYWRIGHT [TASK_CHECKS.mjs]`. The optional module exports `verify({page,manifest})`, returning `{id,status,detail}` for declared interactions. Unverified implemented interactions fail this gate. Missing declarations still require comparison with the brief. Reports bind to final artifact bytes; regenerate after any change.

`check-product-foundation.mjs` creates a fresh child directory under OUTPUT; it must never overwrite the submitted artifact. Keep evaluation artifacts frozen. Record newly verified rules in the owning contract/recipe and limitations in an evidence report; update the entry route only when discovery changes.

For context retrieval, read generation core once and applicable bounded routes, then use each tool’s documented command interface. Large implementation files are not usage guides. During evaluation, `read-context.mjs` logs requested ranges, returned bytes, hashes and reader truncation. A truncated read is incomplete evidence: request the missing range if needed. Transport truncation and model token consumption are separate observations; bytes must not be labelled tokens.

`selftest.mjs` covers data/build contracts. `check-shell.mjs PLAYWRIGHT` covers shell interactions. `check-demo-suite.mjs OUTPUT PLAYWRIGHT` covers the demo suite. `check-style-contract.mjs PLAYWRIGHT OUTPUT` and `check-select-contract.mjs PLAYWRIGHT OUTPUT` provide focused relationship checks. Run checks appropriate to the changed inputs; these are not accessibility certification or model-efficacy tests.

## Read the checks for the changed surface

These routes are required when their condition applies. Run the relevant checks and inspect the actual artifact; a recipe pass does not certify a generated interface. Skip unrelated test implementation files.

| Changed surface | Detailed checks |
| --- | --- |
| Review shell, proposal count, feedback or static fallback | [Shell and feedback](build-checks.md#shell-and-feedback) |
| Cards/forms, nesting, typography, breadcrumbs or collection-to-task layout | [Geometry and composition](build-checks.md#geometry-and-composition) |
| Controls, application state, native behavior, action appearance or save status | [Controls and behavior](build-checks.md#controls-and-behavior) |
| Reference sheets, page rhythm or anchored content | [Source sheets and popovers](build-checks.md#source-sheets-and-popovers) |
| Foundation snapshots, icons, select compilation or packaging | [Generated assets and construction](build-checks.md#generated-assets-and-construction) |

For a logged section-only read: `node scripts/read-context.mjs CORPUS_ROOT references/workflows/build-checks.md OUTSIDE_LOG.jsonl --section "Controls and behavior" 12000`. Use the exact routed heading; nested headings are included, ambiguous/missing headings fail, and truncation is explicit.

For generation-pipeline changes, run `node scripts/check-generation-pipeline.mjs PLAYWRIGHT`. It verifies successful publication, compiled-select binding, token/reference rejection, advisory/unverified reporting, missing-runtime failure and preservation of existing delivery. It is not a replacement for rendered interaction acceptance.

For skill maintenance and verification/evaluation runs, use unique `/private/tmp/*` directories for generated staging, fixtures and disposable reports. Keep source changes within the skill and publish system-review sheets only to the existing canonical `sheets/system-review` destination. Temporary output may be system-purged; retain required evidence before linking it durably. Preserve historical evidence and peer-owned files; see [output boundaries](reference-sheets.md#output-boundaries).

## Wireframe artifact organization

Before the first user-facing wireframe generation for a project, ask where the user wants the artifacts organized. Suggest `docs/wireframes/` as the default parent and `wireframes/` as an alternative, both relative to the project root. Honor another user-selected location. A parent directory already supplied or confirmed by the user satisfies this step; reuse it rather than asking again for every iteration. Do not infer the destination from an ambient browser tab or create an unsolicited preview root.

Under that parent, use a fresh `###-{descriptive-name}/` directory for each independently generated variant or new iteration, starting at `001` and selecting the next unused sequential number. Use at least three digits, expanding beyond `999` if needed. Keep each artifact’s manifests, controller, generation reports and dependencies together in its numbered directory. Preserve earlier folders and evidence; record predecessor relationships when relevant. A/B/C proposals contained in one review artifact share that artifact’s folder. Independently generated variants receive separate numbers.

Pass the fresh numbered path to `generate.mjs`; its existing-output rejection remains in force. Disposable verification/evaluation runs use `/private/tmp/*` instead. Source-derived system-review sheets continue to publish only to the existing canonical `sheets/system-review` destination.

For generated controls and task compositions, follow the bounded [component authoring route](../style/components/authoring.md). Before acceptance, inspect narrow table word readability, chooser-before-detail DOM/focus order, research grouping/task distance, current-step paint, and actual Save/Start activation where applicable. These checks supplement document overflow and static lint; do not infer their success from those gates.
