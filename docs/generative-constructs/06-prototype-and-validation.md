# Prototype and validation brief

Status: proposed v0.1. Thresholds below are initial experiment decisions, not measured results.


> Shipped status: the Progressive Context skill implements a smaller subset of this proposal under different words. This document's terms (construct, revision, instance) map to the skill's capability, contract and assessment as listed in the [vocabulary table](README.md#vocabulary-proposal-and-shipped-skill). The skill specification and the shipped skill record later refinements; reconcile any difference before implementing from this document.

## Objective

Demonstrate a complete intent → composition → evaluation → publication → independent reuse cycle in a browser JS harness, then test whether the additional structure improves reuse enough to justify its cost.

The prototype is complete only when a fresh agent reuses a qualified revision. Rendering the original generated UI is an intermediate milestone.

## Scope and deliverables

- Single-user browser host with a stable construct editor, catalog browser, preview, findings view, and revision history.
- In-memory storage adapter plus persistent browser adapter and JSON export/import.
- One model adapter and one version-pinned A2UI renderer/catalog adapter.
- Three seeded compositions: invoice table, customer summary, action panel.
- One generated workspace, its qualification evidence, and one derived workspace.
- Deterministic domain logic and local follow-up draft handler.
- Fixture suite, reproducible evaluation runner, and a report of the experimental observations.

Exclude live integrations, outbound messaging, arbitrary generated code, multi-user concurrency, new renderer-component generation, and streaming. The supplied fixtures contain synthetic records only.

## User journey

1. Request an overdue-invoice review workspace.
2. Inspect the interpreted intent and the explicit overdue definition.
3. Discover the seeded compositions and inspect their public contracts.
4. Generate and render a candidate workspace.
5. Evaluate it; inspect any implementation failures or unknowns.
6. Revise, rerun, and accept a specific revision when required criteria pass.
7. Have a fresh agent instantiate it with a second supported fixture without changing the realization.
8. Publish the qualified revision with evidence and limitations.
9. Start a separate task: “Group the review by customer and show currency-specific totals.” Derive a new construct from the published one and evaluate its new obligations.

The fresh agent has a clean conversation context. This is a future prototype procedure, not a direction to delegate document writing in this session.

## Fixtures

Fixture A includes an open overdue invoice, an invoice due today, a future invoice, a paid invoice, a cancelled invoice, and an open zero-balance invoice. Use fixed `asOfDate` and timezone values.

Fixture B changes record IDs, customer names, record order, and amounts while remaining inside the same contract. Include more than one currency and two independent surface instances.

Additional cases include no overdue invoices, malformed required fields, a missing customer reference, resolver failure, and a handler rejection. Define expected IDs, currency-specific totals, selected-customer results, and local draft outputs before running generation. Reuse-publication fixture B is separate from the final research holdout fixtures.

## Implementation milestones

| Milestone | Exit condition |
| --- | --- |
| M1: records and context | Create/read/revise works; summaries are bounded; stale-head writes fail; storage survives restart |
| M2: A2UI adapter | Seeded constructs render; schema/catalog failures are visible; IDs and state are isolated across instances |
| M3: generation loop | Request produces a candidate revision; findings lead to an inspectable revision and reevaluation |
| M4: qualification | All required gates pass; a release points to exact artifact and evidence revisions |
| M5: reuse | Clean-context agent instantiates unchanged release and then creates a separately evaluated derivative |
| M6: comparison | Execute the experiment and report quality, effort, context, costs, and limitations |

Implementation should resolve the exact renderer/catalog compatibility and model configuration at M1–M2 and record them. This specification does not assume a currently installed application or working runtime.

## Comparative experiment

Use three conditions with the same model version, renderer catalog, fixtures, base components, task prompts, and maximum generation budget:

| Condition | Available organization |
| --- | --- |
| A: ordinary artifact library | Realizations and basic descriptions; ordinary search/read access |
| B: stage-scoped context | Same base information arranged by intent/build/evaluate stages, without persistent qualification records |
| C: construct model | Versioned contracts, evidence, operation-specific disclosure, and qualified publication |

Condition B is an ICM-inspired web adaptation, not a replication of the paper's filesystem implementation. All conditions receive the same domain rules and task acceptance requirements. Condition C's curation cost is measured explicitly.

Use five related task variants, each attempted twice per condition in fresh sessions: 30 trials total. Randomize condition order. Keep held-out fixture values and expected outputs out of generation context while disclosing the tested requirements. Run graders against actual resulting state and rendered artifacts. Do not cherry-pick a best attempt from retries; count all work within each trial's budget.

This is an exploratory sample, suitable for spotting failure modes and large effects. It cannot support broad claims of statistical superiority or generalization beyond the chosen tasks.

## Measures

- Required outcome pass rate and failure categories.
- Human corrective interventions and active review minutes.
- Input/output tokens, retrieval count, and estimated model cost.
- Wall-clock time, including retries and evaluation.
- Initial documentation/qualification effort and subsequent maintenance effort.
- Independent reuse success without edits to the reused realization.
- Stale-evidence detection and incorrect publication attempts rejected.

Report raw results and medians, with setup cost separated and also amortized over 1, 5, and 10 uses. Label extrapolated amortization as a projection. Where reviewer blinding is practical, hide the experimental condition during task-outcome scoring.

## Initial decision thresholds

Technical gate: every publication invariant and all required prototype criteria must pass. A false passing publication or stale evidence treated as current blocks release of the prototype regardless of average quality.

Exploratory usefulness signal: condition C achieves at least 8 of 10 task successes, performs no worse on required outcomes than the better baseline, and reduces median human correction time by at least 20% relative to that baseline. Record whether input tokens increase; a reduction in corrections purchased with more context is a tradeoff to assess, not a hidden success.

Report the observed reuse count at which setup effort is recovered, or state that break-even was not observed. Missing time measurements make the efficiency result inconclusive.

If outcome quality improves but effort does not, revise the documentation and disclosure design. If only presentation improves, revisit semantic and task criteria. If independent reuse fails, publication rules or public contracts are inadequate.

## Required report

Include configurations, fixture and artifact revisions, all trial outcomes, representative failures, measured costs, and deviations from this plan. Separate demonstrated behavior from interpretation. Recommend whether to continue, simplify, or abandon parts of the proposal based on the observations.
