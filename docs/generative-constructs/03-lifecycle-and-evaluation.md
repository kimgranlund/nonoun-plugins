# Lifecycle and evaluation specification

Status: proposed v0.1. Uses the entities in the [construct model](02-construct-model.md).

## Independent status dimensions

Maturity belongs to a revision: `proposed`, `specified`, `realized`, `accepted`, or `published`. A release can later be `withdrawn` or `retired` without erasing its history. Evidence state is `unassessed`, `passing`, `failing`, `inconclusive`, or `stale`. Applicability describes the specific uses and environments covered.

A published revision can acquire failing evidence. The system must expose that fact and suspend its default reuse eligibility rather than rewriting the historical publication event. A new draft can develop while a previous release remains usable.

## Transitions and guards

| Transition | Required basis |
| --- | --- |
| Create → proposed | Identity, provisional intent, and visible unresolved assumptions |
| Proposed → specified | Bounded outcomes, semantic references, contract, assessable required criteria |
| Specified → realized | A revision containing a candidate artifact and resolved implementation dependencies |
| Realized → accepted | All required acceptance criteria pass with applicable evidence; no unresolved blocking findings |
| Accepted → published | All publication gates below pass and a recorded publication decision names the release |
| Published → withdrawn | A blocking defect or invalidated qualification makes default reuse inappropriate |
| Published → retired | Maintainer ends future recommendation, recording reason and any replacement |

An evaluator records observations; a deterministic policy calculates eligibility. In the prototype, the user records acceptance and publication decisions through the UI. The agent may prepare them but cannot obtain eligibility by editing a status field. This is a proposed product behavior, not a request for approval to write these documents.

## Criterion contract

Each criterion defines an ID, linked requirement, method, expected result or rubric, applicable conditions, requiredness, and evaluator class. Results are `pass`, `fail`, `unknown`, or `not-applicable`. A required criterion cannot be dismissed as not applicable without revising its applicability definition and recording why.

Use executable checks for deterministic behavior, rendered inspection for presentation, and human judgment for task fitness. Model judgment can supplement a rubric but must be labeled and calibrated before substituting for required human assessment. [Background: agent evaluation methods](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents).

## Gap representation

A finding records criterion ID, expected behavior, observed behavior, evidence reference, severity, category, and proposed next action. Categories are implementation defect, missing evidence, ambiguous intent, defective evaluator, integration mismatch, and stale evidence.

The next action depends on category: fix the realization, gather observations, clarify requirements, or repair an evaluator. Closing a finding requires a linked resolution and new evidence where appropriate. A prose claim that the issue is fixed is insufficient.

## Publication contract

All gates are required for the first prototype:

1. **Purpose:** intended outcome, domain assumptions, and exclusions are explicit.
2. **Interface:** inputs, outputs, supported actions, error behavior, and limitations are documented.
3. **Realization:** the exact artifact and dependency revisions are resolvable and render successfully.
4. **Acceptance:** every required criterion has applicable passing evidence; no required result is unknown or stale.
5. **Reuse:** a fresh agent instantiates the candidate in a second supported scenario using its public resources, without the original creation conversation or source modifications.
6. **Inspection:** the task outcome and rendered experience have been reviewed using the declared rubric.
7. **Reproducibility:** the release records runtime/catalog versions, fixtures, evaluator versions, and the entry point for use.
8. **Decision:** an authorized publisher records the release, scope, evidence references, and limitations.

A passing reuse exercise supports the bounded applicability stated in the contract, not a universal reusability claim. An adaptation that changes the artifact is a new construct or revision and cannot substitute for the unchanged-instantiation exercise in gate 5.

## Evidence freshness

Evidence remains a historical fact about its exact target. Applicability to a current candidate is computed separately.

| Change | Default effect |
| --- | --- |
| Realization or bindings | Re-run acceptance and affected integration checks |
| Intent, domain semantics, or contract | Reassess affected criteria and required evidence |
| Criteria or evaluator implementation | Re-run affected evaluations; keep old observations labeled with old versions |
| Dependency, renderer, or catalog version | Re-run runtime and integration evaluation |
| A supported new input instance | Check input contract and instance behavior; does not itself modify the release |
| A new failing observation within scope | Suspend reuse eligibility pending triage |

The prototype conservatively reruns the complete suite after any normative snapshot change. Selective evidence carry-forward is a later optimization requiring explicit impact rules. Documentation-only changes also create a snapshot; this avoids premature exceptions.

## Preventing misleading progress

Criteria are fixed for each evaluation run. If they are changed, compare results against their respective versions and record a change rationale. Never merge them into a score suggesting the realization improved under unchanged expectations.

Assessments must expose required failures separately from optional quality scores. A high visual score cannot offset a failed required domain criterion. Cancellation, evaluator errors, and unavailable dependencies produce incomplete or unknown results, never an automatic pass.

## Invoice workspace acceptance example

| ID | Required result | Method |
| --- | --- | --- |
| C-01 | Displayed invoice IDs exactly match domain eligibility | Fixture assertion |
| C-02 | Selection and customer details refer to the same customer | Interaction test |
| C-03 | Totals remain separated by currency | Fixture assertion |
| C-04 | Empty, invalid-data, loading, and resolver-error states are explicit | Rendered inspection and state checks |
| C-05 | Preparing follow-up creates the correct local draft and sends nothing | Handler/state assertion |
| C-06 | A reviewer can identify an overdue invoice, inspect context, and prepare a draft | Human task rubric |
| C-07 | A second instance renders independently with different supported inputs | Instance-isolation and reuse exercise |

Quality observations such as density and visual polish are recorded separately. If they are essential to acceptance, define a required rubric before evaluation.
