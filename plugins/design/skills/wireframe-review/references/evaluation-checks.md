# Independent acceptance and read evidence

Use for context evaluations or artifacts whose brief requires working interactions. The evaluator writes acceptance before generation, stores it outside the generator's writable run directory, and preserves its bytes. The runner hashes it; hashes expose changes but do not enforce filesystem ownership. The generator's manifest is implementation metadata, not the acceptance oracle.

Run both the existing artifact/build gate and:

```sh
node scripts/verify-acceptance.mjs artifact.html acceptance.json new-report.json PLAYWRIGHT
```

A JSON acceptance file has `version: 1`, `surface: "review"` or `"document"`, nonempty `cases` and `requirements`. Review cases specify unique `id`, `targetType` (page/unit), `target` (actual manifest ID), `variant` (A/B/C), `viewport` (desktop/mobile) and `scheme` (light/dark). Select the page explicitly; all-pages overview is read-only. Document cases can specify `width`, `height` and `scheme`. Each case starts in a fresh browser page; requirements within it run in order, inventory last. Make scenario state setup explicit.

Every requirement has a unique `id`, a brief-derived `description`, and a supported `type`:

| Type | Fields and evidence |
| --- | --- |
| scenario | `steps`: each has `selector` and `action` or `assert`, plus `value` when needed. Actions: click, fill, check, uncheck, press, focus. Assertions: text (substring), textEquals, value, disabled, visible, checked. Include an observable assertion; prefer exact state text when ambiguity matters. |
| contrast | `selector`, explicit `min` ratio. Checks target text against nearest opaque background, including ancestors. Images, filters, opacity, translucent layers and hidden targets fail as unsupported; they are not certified. Select each relevant descendant role. |
| gap | `before`, `after`, positive `min`, optional `max`, in CSS pixels. Measures vertical edge separation. Pick meaningful sibling boundaries; token validity alone is insufficient. |
| width | `selector`, positive `min` in CSS pixels. Tests useful rendered width, not automatic aesthetic quality. |
| menu | `trigger`, `panel`, surrounding `anchor`; optional `outside` click target. Tests top layer, viewport bounds, no anchor movement, Escape and focus return. Supply outside to test outside dismissal. Choose targets that remain visible together. |
| disabled | `selector`. Requires a native disabled input/button/select/textarea that cannot take focus. Inspectable unavailable choices instead need a scenario proving selection works and the consequential action is blocked. |
| inventory | Optional control `selector`; `bindings` of selector + requirement ID. Visible controls must map to a passed scenario/menu/disabled check. Review the bindings: broad mappings can overstate coverage. Hidden menu items need a separate open-state scenario. |

Missing elements, omitted required behavior, unsupported checks and browser errors prevent a passing report. A missing requirement in the evaluator's own list is still a human coverage error. This tooling does not infer intent from arbitrary HTML or prove accessibility, visual completeness or business correctness. It currently runs Chromium only. Check modules and runner hashes bind reports to their implementation.

`check-acceptance.mjs PLAYWRIGHT NEW_OUTPUT` writes a runnable fixture and acceptance example, verifies its baseline at two widths/schemes, then independently mutates contrast, spacing, card width, menu opening, outside dismissal, native disabled state, revision invalidation, required-field presence and control inventory. Each mutation must fail its corresponding requirement. Keep these negative controls when extending detectors.

## Context read recording

During a fresh-context evaluation, use this instead of direct corpus reads:

```sh
node scripts/read-context.mjs CORPUS_ROOT RELATIVE_FILE OUTSIDE_CORPUS.jsonl START_LINE END_LINE MAX_BYTES
```

The reader returns the requested text and appends path/range, source hash, exact returned content/hash, byte count and local truncation status. Read the next range when truncated. Logs must stay outside the corpus. Execute token-group lookup separately, save its output as a text artifact, and record that file with this reader using its containing directory as root. Record the command and source hashes in the evaluator run record; file provenance alone cannot prove which command produced it.

This observes the reader's output boundary, not the model's attention. Inspect tool-response truncation separately; the reader cannot detect a downstream tool cap. Direct reads, hidden filesystem access and omitted calls are not intercepted. Enforce the allowed read path through the evaluation harness and disclose bypasses. Token counts remain null unless measured with a named tokenizer. `check-context-reader.mjs` verifies ranges, hashes, truncation, append behavior and path/write guards.

## Visual capture integrity

Keep initial viewport captures separate from full-page captures. Log failed local resource responses as well as script errors and blocked external requests. Offscreen `content-visibility:auto` regions can appear blank in full-page screenshots even when their content renders during normal scrolling. Diagnose a blank region against the DOM and a scrolled viewport before classifying it as interface drift. If full-page capture needs `content-visibility:visible`, apply it only during capture, consistently across conditions; retain originals and label the normalized images. Do not use normalized screenshots to prove normal layout stability or behavior. Correct affected blind reviews without revealing conditions, and preserve the original scores and their qualifications.

## Corpus graph and growth

Run `node scripts/check-corpus-graph.mjs CORPUS_ROOT` to check local Markdown targets/fragments and supported contract version envelopes. It does not validate full contract semantics, external destinations or JSON/HTML fragments. For the growth experiment, snapshot a temporary copy, record selected routes with the measured reader, then add an unrelated branch and repeat those same reads. Compare exact returned content hashes and bytes, while checking that the whole graph includes the new branch. Inject missing-target and unsupported-version faults and require their specific errors. Change a selected file as a negative control for the stability comparison. Fixed-route stability does not prove model attention, adaptive discovery or future generation quality.

For component contracts, use `component-context.mjs ID --output NEW_FILE` to select an exact family/dedicated record plus applicable shared declarations. Record the command and lookup metadata, then read the saved JSON using `read-context.mjs` with its containing directory as root. Place read logs outside that saved-payload directory. Reference paths resolve against the returned source `referenceBase`. This observes the generated context boundary; it does not prove agent uptake or reduce all session reads. `check-component-context.mjs NEW_OUTPUT` verifies all thirteen records, source fidelity, output guards, version rejection and growth/change controls. Never overwrite frozen evaluation outputs to adopt this route.

## Task-faithful state scenarios

Set up each saved-state scenario explicitly. An earlier range endpoint check must not determine the value saved by a later scenario that requires a different value. Assert every saved field after editing and restoring, including selected choices and synchronized outputs.

Draft status and snapshot existence are different observations. An invalid first Save can leave an edited draft labelled “Unsaved changes” without committing a snapshot. Test the required no-commit behavior through an observable restore path; do not invent an intermediate status requirement. If the task leaves restoration without a snapshot undefined, protect a previously valid snapshot through an invalid Save instead of imposing a new default policy.

Popup behavior and source-family fidelity have separate authority. Measure the header's width and height when the task forbids resizing; an unchanged top coordinate does not prove unchanged size. Require native top-layer behavior only when the source contract or task requires it. Record link presence separately from destination semantics and keyboard/focus behavior.

Keep original frozen criteria and reports when a reviewer finds an evaluator overconstraint or omission. A separately hashed, task-faithful correction is supplemental analysis after submission, not preregistered acceptance. Apply it to every comparable submission, preserve failures, and distinguish observed values from asserted behavior. Negative controls prove only their named predicates; passing checks do not cover omitted requirements.


### Persistent task bars in long workflows

A fixed or sticky task bar is not evidence that a long workflow has become easier to complete. Measure task-region distance and grouping separately from access to the persistent shortcut; retain the chosen metric and report hidden regions as unmeasured. Do not shrink the shared spacing hierarchy merely to improve a distance score.

Verify actual keyboard navigation in the ordinary viewport, including selection, disclosures, contact fields and the primary action. A focused control must remain visible and reachable above persistent chrome. Bottom padding alone does not establish that intermediate controls scroll into an unobscured region. Test the actual bar height, wrapped labels and shorter viewports; document the scrollport reservation or another owned placement strategy.

Distinguish a full-page screenshot overlay from an interaction defect. Check the focused element's viewport box and hit-test its center against the bar before classifying occlusion. Record keyboard preferences and the visited control set: a browser's default Tab sequence may omit control types, so absence of observed occlusion is not a complete keyboard pass. Keep source/rubric versions, submitted artifacts, and reports unchanged; guidance added after a frozen generation cohort is excluded from that cohort's efficacy claim.


## Source-style comparison boundaries

Recognize an owner through its assigned source selector, then compare only its qualified properties. An implemented component class or inherited geometry/type context can be legitimate; a prefix or contract vocabulary alone is insufficient. Verify each admitted class, attribute value and conditional property against the frozen source. Keep novel or unsupported conditions unknown, and layout outside a style-only mask excluded. Report those denominators beside matches.

A complete computed typography tuple covers family, size, weight, line-height and tracking together. Its presence is not proof of a declaration, token reference, cascade provenance or loaded primary font. Preserve those unknowns even when a literal value equals the reference. Test missing capture fields separately from style mutations.

Qualification must cover conditional mask branches as well as default examples: an inverse surface's foreground, for example, needs its own color fault. Exercise pointer/focus admission guards before a rest comparator clears them. Remove each guard as a rejection control; a green default fixture does not establish that the omitted branch is safe. Preserve rejected implementations and reviews. A repaired descriptive supplement requires independent qualification before rescoring, and cannot replace original efficacy criteria or turn a previously exposed task into a holdout.

## Isolated acceptance and delivery (version 2)

Version 1 remains supported with its original shared requirement state. Prefer version 2 for task delivery: each requirement starts from a fresh page/route, and its `setup` actions establish known state. Unrelated failures cannot contaminate later scenarios. Steps within a scenario remain sequential. Put prerequisites earlier and name them in `dependsOn`; a failed prerequisite records `blocked`, not another assertion failure. `caseIds` limits applicability to named cases; other cases record `not-applicable`. A required requirement with no applicable execution cannot verify delivery.

Scenario assertions also support `focused` (actual owner-document active element) and `count` (including zero). A review-only step `{ "action":"remount", "value":"mobile" }` changes the owned shell viewport and waits for the replacement preview. Use an actual changed viewport for remount coverage. `execution:"unexecuted"` with `reason` explicitly records missing required coverage. Results distinguish `assertion-failure`, `harness-error` (binding/unsupported operation), `setup-error`, `application-exception`, `unsupported`, `blocked`, `unexecuted` and `not-applicable`. Only applicable required passes can verify delivery; unknown application exceptions always prevent it. No notification class is suppressed by this runner.

For Save/Restore, make the fixture valid under the brief's policy before establishing a snapshot. Fill every required field, verify the snapshot exists, change every saved field, then restore values and synchronized outputs. Test invalid final validation separately. A draft policy may allow incomplete snapshots; do not impose final-validation rules on draft saving. Preserve original misbound or incomplete-fixture observations and qualify them in a successor report rather than silently changing their outcome.

Example of an evaluator-owned staged scenario (selectors must match independently reviewed bindings):
```json
{"version":2,"surface":"review","cases":[{"id":"mobile","targetType":"unit","target":"booking","variant":"A","viewport":"mobile","scheme":"dark"}],"requirements":[{"id":"next-focus","type":"scenario","description":"Committed Next focuses the visible destination heading","caseIds":["mobile"],"setup":[{"selector":"#equipment","action":"check"}],"steps":[{"selector":"#next","action":"click"},{"selector":"#delivery-heading","assert":"focused","value":true}]}]}
```

Revised-search acceptance should have its own fresh setup: select a record, search a mixed-case match, search no matches, clear to recover, assert the same selection and activate its consequential action. It does not depend on a preceding focus scenario. `check-delivery-integration.mjs PLAYWRIGHT NEW_OUTPUT` produces runnable staged/save/search examples, policy variants and failure controls through the actual entry points.

Use `generate.mjs ... --acceptance EVALUATOR_JSON` for an explicitly requested delivery gate. Ordinary generation remains draft emission and records `delivery-incomplete` without task acceptance. With acceptance, applicable required cases must pass before promotion; failures retain the artifact and report in failed-stage diagnostics. Summary source/controller/acceptance hashes and the acceptance report's artifact/runner/check hashes bind the evidence. Criteria must be brief-derived and frozen outside generator-writable output before authoring; copying and hashing do not enforce permissions or establish independence/completeness.

`verify-acceptance.mjs --check-report REPORT HTML ACCEPTANCE` checks current artifact, criteria, runner and check-implementation identities. It rejects changed inputs; it does not review evaluator intent. The rendered checker remains complementary render evidence, not a second task completeness oracle. Both use actual declared route/proposal counts, never manufacture A/B/C coverage. Accepted environment limitations remain named user decisions linked separately; they are not passes or waivers for component failures.

Scheme qualification precedes task assertions: requested scheme must match shell mode and effective preview color-scheme. Reports record requested/control/effective/emulated OS per requirement. Preserve old receipts; corrected successor reports qualify only the identical artifact and criteria actually checked.

Scenario visible:false accepts an absent or hidden element; visible:true, actions and other single-element assertions still require exactly one binding. A negative visibility check alone cannot establish selector correctness; pair it with positive existence/visibility in another state.
Generate with --mode delivery and evaluator --acceptance for a delivery request. Without acceptance, draft mode can emit but remains delivery-incomplete; compilation is not task delivery.
