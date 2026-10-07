---
status: proposed
---
# A2UI composition and runtime specification

Status: proposed v0.1. Adapter-neutral requirements precede AdiaUI-specific notes.


> Shipped status: the Progressive Context skill implements a smaller subset of this proposal under different words. This document's terms (construct, revision, instance) map to the skill's capability, contract and assessment as listed in the [vocabulary table](../../specs/generative-constructs/README.md#vocabulary-proposal-and-shipped-skill). The skill specification and the shipped skill record later refinements; reconcile any difference before implementing from this document.

## Boundary

A2UI represents the UI realization through declarative components, surface updates, and data bindings. The construct system supplies intent, semantic definitions, evaluation, and reuse policy. The JS harness supplies persistence, action dispatch, data resolution, and generation operations. [A2UI concepts](https://a2ui.org/concepts/overview/).

Exact message syntax and validation schemas must match one pinned protocol and renderer version. Do not mix examples from different A2UI versions or assume an AdiaUI extension is part of the general protocol.

## Renderer catalog and construct library

| Layer | Owns | Example |
| --- | --- | --- |
| Renderer catalog | Implemented component types, properties, functions, themes | Table, text, button, supported domain widget |
| Construct library | Qualified compositions, binding contracts, intent, evidence | Overdue-invoice review workspace |

Catalogs describe the capabilities available to an A2UI renderer. [Reference](https://a2ui.org/concepts/glossary/).

A generated composition can enter the construct library after qualification. It cannot introduce an unimplemented renderer type by naming it. New renderer types need implementation, registration, and their own checks outside the initial prototype.

## Composition package

A UI realization resource contains:

- A composition template in an adapter-defined, versioned format.
- Required renderer/catalog identifiers and dependency revisions.
- Input schema and binding map.
- Named action contracts and handler requirements.
- Public outputs and instance-state schema.
- Declared empty, loading, invalid-input, and error behavior.

These fields belong to the application package; they are not proposed additions to the A2UI protocol. The adapter expands the package into valid messages for the pinned renderer.

## Instantiation

Given a published revision and input:

1. Resolve every pinned composition dependency and reject missing references or cycles.
2. Check the effective renderer/catalog against the package requirements.
3. Validate input against its schema and relevant semantic constraints.
4. Allocate an instance namespace and remap local component and surface IDs, including all references.
5. Map bindings into the instance's data scope; bind action names to registered handlers.
6. Validate the final expanded representation and adapter-specific rules.
7. Register data resolvers, then render through a single owner per surface.
8. Record the effective configuration on the instance and make errors observable.

Published templates remain immutable. Instance interaction state does not write back into them. Two instances must not share mutable bindings or event destinations by accident.

## Invoice contract example

```text
Inputs:
  invoices[]: id, customerId, dueDate, currency,
              outstandingMinor, status
  customers[]: id, displayName
  asOfDate: ISO calendar date
  businessTimezone: declared timezone

Local actions:
  selectInvoice(invoiceId)
  prepareFollowUp(invoiceId)

Outputs/state:
  selectedInvoiceId
  followUpDrafts[]

Limits:
  No outbound delivery, payment initiation, or currency conversion.
```

Overdue semantics come from [the domain model](../../specs/generative-constructs/02-construct-model.md). Implement filtering and aggregation in deterministic application logic. The model may select or configure that capability; it need not regenerate arithmetic on every interaction.

`prepareFollowUp` creates a local draft for the selected eligible invoice. The registered handler validates the invoice reference and records an idempotent action result. Surface text claiming success is not proof that the draft exists.

## Interaction classes

| Event | Handling |
| --- | --- |
| Selection or filter change | Ordinary state update and binding reconciliation |
| Load selected customer's details | Bounded data resolution with visible loading/error state |
| Prepare follow-up | Registered local handler and recorded state result |
| Request a new arrangement | Generation run that proposes a new construct revision |
| Change “overdue” policy | Semantic revision, impact assessment, and reevaluation |

Only events requiring generative reasoning invoke the model. The host distinguishes instance interactions from edits to a construct definition.

## Validation, rendering, and recovery

Validate incoming generated descriptions as untrusted data. Check schema, catalog membership, ID/reference integrity, binding paths, handler availability, and unresolved dependencies before application. Schema validity alone cannot establish domain correctness or task fitness.

For the prototype, buffer a complete candidate update before validation and rendering. Preserve the previous valid preview if the candidate fails, and display the errors to the builder. Streaming is deferred until the adapter defines message boundaries, partial-state validation, cancellation, and rollback. Progressive context disclosure works independently of streaming.

Prevent an old generation run from overwriting a newer preview by checking its target revision/run ID. Dispose surfaces and subscriptions when instances close. Capture renderer errors as evidence, not only console output.

## Evaluation layers

Use [document 3's criteria](../../specs/generative-constructs/03-lifecycle-and-evaluation.md) to evaluate protocol validity, integration, rendered states, domain behavior, the user's task, and independent reuse. Inspect the actual rendered output. A schema pass does not count as render or usability evidence.

Record protocol, renderer, catalog, resolver, and handler versions in the environment fingerprint. Changes to these versions trigger the reassessment policy.

## AdiaUI adapter profile

The installed `adia-ui-kit-factory` plugin's `gen-ui-wiring` skill, version 0.8.51, specifies these implementation behaviors:

- Ground generation in an explicit intent and retrieved examples.
- Run `validate_schema` and `check_anti_patterns` on generated messages before serialization, storage, streaming, or assignment to a render root.
- Register referenced data schemes before rendering; unresolved schemes can otherwise render empty without an error.
- Use one owning root per surface. `<a2ui-root>` supports document assignment or transport-driven updates; switching from a stream requires disconnecting it first.
- Revalidate after refinement. Custom corpus chunks trace to real pages.

These are AdiaUI-specific constraints to verify again against the installed runtime when implementing. Invalid candidate bodies should remain transient under this profile; persist failure diagnostics and identifying digests rather than serializing the rejected message document. A validated artifact may still be stored as an unevaluated draft.

Source: the `gen-ui-wiring` skill of the `adia-ui-kit-factory` plugin (0.8.51, installed locally, not in this repo). The prototype need not choose this adapter until compatibility with its catalog has been checked.
