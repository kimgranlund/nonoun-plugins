# Stage 1 — Linear-inspired domain and task review

## Own

Domain-driven experience design: users' jobs, entities, relationships, permissions, lifecycle states and consequential actions. This is the product's conceptual model, not a request to introduce a software DDD framework. Established domain vocabulary and workflows take precedence over generic productivity-app patterns.

## Ask first

- What is the user accomplishing, for whom, and how is success recognized?
- Which entity is being viewed or changed? Who owns it, and what is shared?
- What do practitioners already call these objects, actions and outcomes?
- What state transitions are legal? Which are provisional, committed, reversible, or externally consequential?
- Are we fighting an established domain workflow, or is departure justified by an actual user benefit?
- Does the model distinguish authorization from execution, selection from mutation, and incomplete work from failed work where those distinctions matter?

## Evaluate

| Criterion | Supported when |
| --- | --- |
| Task fit | The main flow completes a recognizable user job; unnecessary product-internal steps are absent. |
| Domain fidelity | Entities and relationships match the domain; invented abstractions do not require users to translate their work. |
| State integrity | Draft/committed/shared state and action scope are unambiguous, including failure and uncertainty. |
| Convention fit | Relevant conventions are identified with their context; departures have a reason beyond novelty. |

Deliver a small domain vocabulary seed (entity, preferred term, meaning) and state/action map. Do not polish final microcopy, choose visual slots, or prescribe pane geometry here. Flag missing consequential assumptions instead of inventing permission or persistence semantics.

## Exit

The parent can name the primary job, affected entity, owner, valid action/result transitions and relevant domain conventions. If not, explain what upstream information is needed. This map is the input to experience sequencing.

For inside-out validation, specify the outcome and domain invariants that the composed journey must ultimately satisfy. A sequence of valid individual actions is insufficient if the user cannot finish the job or if the final result violates ownership, permissions or commitment scope.
