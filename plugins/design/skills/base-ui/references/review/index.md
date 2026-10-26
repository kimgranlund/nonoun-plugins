# Review rubric index and checklist workflow

Use this review for generated UI delivery and material composition changes, alongside executable contract audits. For small edits, inspect the changed region and its neighboring relationships; mark unrelated topics with a reason. For image-only review, limit claims to visible frames: DOM, behavior and unseen states remain unverified. This is a review of an artifact, not a request to generate alternatives or redesign the entire product.

Start with the [design principles and subtraction pass](principles.md). These define quality across topics; a mechanically valid UI can still fail simplicity, hierarchy or balance.

The maintained [rubric catalog](rubrics.json) contains stable check IDs, questions and inspection methods. Read the index first, then retrieve relevant topics with `python3 scripts/run.py review-checklist.mjs show TOPIC`. Do not load every component contract to review one surface.

| Topic ID | Review subject | When |
|---|---|---|
| purpose | Task hierarchy and visual emphasis | Every review |
| layout | Grid, alignment rails, ownership and wrapping | Every review |
| density | Proximity, whitespace and information density | Every review |
| content | Typography, field labels, help and reading measure | Every review |
| consistency | Component anatomy and semantic colors | Every review |
| responsive | Recomposition, scrolling, positioning and layers | UI; supplied frames only for images |
| interaction | Naming, focus, activation and state transitions | Interactive UI |
| data | Truthful encodings, comparisons and quantities | Data-bearing surfaces |
| image | Focal composition, crop and image artifacts | Generated images or image assets |

Use the [executable review session](session.md) for UI: define app state setup once, capture the full machine matrix, inspect the generated risk-based visual sample, and record judgments by topic using paginated next-topic packets. It creates the bound record and links evidence; no automatic visual passes. Use its status queue until coverage is complete. Manual schema editing below remains available for image-only or specialist reviews.

## Work through the review

1. **Set scope and acceptance intent.** Identify the exact artifact/version, user task and reviewer. List state IDs with viewport, scheme, content and interaction state. For an image list intended display size and supplied frames. Add states when new findings expose a coverage gap.
2. **Review outside-in.** Inspect purpose, layout and density at actual viewing size. Describe the intended rails and groups; compare them to the screenshot. A full-page thumbnail is useful for hierarchy but insufficient for control alignment or text legibility.
3. **Review inside-out.** Inspect content and consistency, then the relevant responsive, interaction, data or image topics. Inspect component crops and computed layout where available. Compare repeated instances. Select the narrow/wide, wrapped, expanded and error states that can falsify the proposed composition.
4. **Measure consumer contrast and mobile task access.** Follow [consumer review measurements](measurements.md). Run these on the generated app, including relevant dynamic states; kit fixtures are not consumer evidence. Then **record every check.** Use `pass`, `fail`, `na`, `blocked` or leave `unreviewed`. Pass/fail requires state IDs and evidence references with concrete observations. `na` requires a scope reason; lack of time or access is blocked, not not-applicable. Automated results do not substitute for visual inspection. A source read supports a cause, not the rendered appearance.
5. **Diagnose failures.** Record severity, owning parent/component, cause and confidence, proposed repair and a discriminating recheck. Follow symptom → measured relationship → CSS/DOM or data owner → reusable contract/mechanism. Keep suspected causes labelled hypotheses. For images, use composition/asset ownership; do not invent DOM causes.
6. **Repair and revisit.** Preserve the before record. Apply authorized fixes to the responsible owner, then create a new review record against the new artifact/version and repeat affected checks plus neighboring relationships. A repaired component can change wrapping elsewhere. Do not mark a failure passed because code changed.
7. **Finish through the [delivery gate](delivery.md).** Begin an artifact-bound record before inspection; after recording every check, run the gate to validate evidence and produce a completion receipt. Run the checklist checker for intermediate feedback. Separate mechanical test results from composition findings and unresolved coverage. A complete review can still require changes. Do not average failures into a numeric quality score or claim full acceptance while checks are blocked/unreviewed. Document any delivered limitations explicitly.

## Concrete negative cases

Apply the bounded [composition negative-case checklist](composition-negative-cases.md) to relevant collection, nested disclosure, field-help, action-row and completed states. It makes recurring visual failures explicit under existing check IDs; it adds no gate or schema. Inspect actual pixels and record the relevant pass/fail observation, or a scope reason when the composition is absent.

## Create and check a record

Run from the base-ui directory (or use absolute script paths):

```sh
python3 scripts/run.py review-checklist.mjs topics
python3 scripts/run.py review-checklist.mjs show layout
python3 scripts/run.py review-delivery.mjs begin /absolute/app.html /absolute/evidence/review-before.json
python3 scripts/run.py review-checklist.mjs check /absolute/evidence/review-before.json
```

`init` refuses to overwrite a record. Fill `scope` and the item fields in the generated JSON. `scope.states` contains `{id, description}` entries; descriptions identify viewport/scheme/state or image frame. Evidence entries use `{kind, ref, observation}`; kind is visual, dom, interaction, measurement or source. References should resolve to preserved screenshots, source lines or check outputs, not merely “looks good”. For failed checks add `severity` (blocker/major/minor) and `diagnosis: {owner, cause, confidence, repair, recheck}`; confidence is confirmed/hypothesis/unknown. Root cause may be explicitly unknown rather than fabricated.

Severity: blocker prevents task completion or materially misrepresents data; major impairs grouping, reading or navigation; minor is localized inconsistency without task loss. Severity is contextual, not determined by how many pixels differ.

The checker validates completeness and evidence fields, not screenshot authenticity, correctness of judgment, contrast, or actual browser behavior. It exits nonzero for malformed records, unreviewed/blocked checks or unresolved failures. A passing record means only the reviewer recorded passes in the named scope. Keep review records with the task evidence, outside the installed skill. Fog-of-War publication remains a separate workflow when requested; this checklist does not create a report registry entry.

## Related mechanisms

- [Composition contracts](../style/composition.md): spacing relationships and layout ownership.
- [Rendered audit](../rendered-audit.md): executable anatomy and bounded geometry checks.
- [Reading regions](../reading-regions.md): deep nesting and prose width.
- [Verification reporting](../verification-reporting.md): author/evaluator attribution and acceptance evidence.
- [Review patterns](../review-patterns.md): truthful comparisons, intervals and allocation.

For bounded principle-to-implementation discovery, use `python3 scripts/run.py design-context.mjs --list` then a concept ID such as `simple`. The [concept index](concepts.json) links existing rubric IDs and authoritative mechanisms; it is not a design verdict.

`show` accepts one or more topic IDs, returning each requested topic. Invalid IDs or batches above12000 bytes fail before emitting a partial topic set. Split larger batches rather than assuming trailing arguments were read.
