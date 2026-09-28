# Construct model and ontology

Status: proposed v0.1. This document owns the shared terminology.

## Core entities

| Entity | Definition |
| --- | --- |
| Construct | A persistent identity for a proposed or realized capability |
| Revision | An immutable snapshot of the construct's normative resources and dependency references |
| Instance | One use of a revision, with its own inputs, interaction state, and outputs |
| Intent | Desired outcomes, beneficiaries, scope, assumptions, and exclusions |
| Contract | Public inputs, outputs, actions, preconditions, guarantees, and limitations |
| Realization | The artifact or artifact set that attempts to satisfy intent |
| Criterion | An assessable claim with a method, expected result, and requiredness |
| Evidence | An observation from an evaluation of an identified target under recorded conditions |
| Assessment | A derived interpretation of applicable evidence against criteria |
| Release | A publication record pointing to one qualified revision and its public contract |
| Run | A recorded activity that reads resources and produces changes, artifacts, or evidence |

“Component” is a role a construct plays in another construct. It does not imply completeness. An A2UI renderer component is a separate implementation concept defined in [document 5](05-a2ui-composition-and-runtime.md).

## Identity and version rules

- `constructId` is stable across revisions. Names and storage locations may change.
- `revisionId` identifies an immutable snapshot. A content digest detects accidental modification.
- Draft edits create new snapshots; a `draftHead` pointer tracks the latest one.
- A release pins one snapshot. Updating the draft head cannot modify that release.
- Each runtime `instanceId` references a release or explicit revision and records the effective environment.
- Evidence and transition decisions are appended separately; they do not mutate their target snapshot.

This avoids a circular revision change every time evidence is added. The current summary is a derived view over snapshots, evidence, and lifecycle events.

## Logical record shape

The following is an application model, not A2UI wire syntax or a finalized database schema:

```ts
type Ref = { constructId: string; revisionId: string };
type ResourceRef = { id: string; digest: string; mediaType: string };

type ConstructRevision = {
  constructId: string;
  revisionId: string;
  parentRevisionId?: string;
  kind: "ui-composition" | "reference" | "procedure";
  summary: string;
  resources: {
    intent: ResourceRef;
    semantics: ResourceRef;
    contract: ResourceRef;
    criteria: ResourceRef;
    realization?: ResourceRef;
    decisions?: ResourceRef;
  };
  relationships: Array<{
    relation: "uses" | "contains" | "derivedFrom";
    target: Ref;
  }>;
  applicability: string[];
  limitations: string[];
};
```

The prototype implements `ui-composition`; other kinds reserve conceptual scope. Realization may be absent in a proposed construct. Missing content must be marked unresolved rather than filled with invented claims.

## Relationships

| Relationship | Meaning | Effect of upstream changes |
| --- | --- | --- |
| Uses | Depends on another pinned revision | No silent upgrade; selecting a newer revision creates a new dependent revision |
| Contains | Owns a constituent definition within this composition | Constituent changes require a new composition snapshot |
| Derived from | Records the origin of an independently maintained adaptation | Preserves lineage without an implied live dependency |

References form a graph. Physical or visual nesting is a navigation choice. The prototype rejects cycles in `uses` and `contains`; derivation remains a historical relation. Missing dependencies are errors, not instructions to substitute something similar.

## Two levels of semantics

The core ontology above describes the system. Domain definitions supply the concepts that make intent and evaluation meaningful. Each revision references a versioned domain resource; it can introduce local terms without silently redefining shared ones.

Prototype invoice definitions:

- An invoice has an ID, customer ID, ISO calendar due date, currency, outstanding amount in integer minor units, and a status.
- Supported statuses are `open`, `paid`, and `cancelled`.
- An invoice is overdue when status is `open`, outstanding amount is positive, and `dueDate < asOfDate`.
- An invoice due on `asOfDate` is not overdue. Both dates use the declared business timezone and calendar-date semantics.
- Totals are grouped by currency. Conversion and a combined cross-currency total are outside the contract.
- Missing or invalid required fields produce a visible invalid-record result; they must not silently become zero or current values.

These are test-domain assumptions. Future policy changes must create a new semantic revision.

## Traceability

Requirements and criteria have stable local IDs. Example:

```text
semantic term: invoice.overdue
  -> intent outcome: identify invoices needing review
  -> requirement R-01: show only eligible overdue invoices
  -> criterion C-01: displayed IDs equal expected fixture IDs
  -> evidence E-17: result for workspace revision r3, fixture f2
```

Evidence records target revision, criterion IDs and digest, dependency revisions, fixture digest, evaluator identity/method version, environment fingerprint, timestamp, observations, and result. For generation runs, also record model and harness versions and loaded-resource references. Do not require private chain-of-thought; observable actions and artifacts provide the audit trail.

## Invariants

1. A status assertion must resolve to an assessment or explicit transition event.
2. An instance cannot change a published definition by editing its local state.
3. Every published dependency reference resolves to an exact revision.
4. Unknown evidence is distinguishable from failure and success.
5. Readable summaries include material limitations and link to deeper context.
6. Domain meaning, public interface, and assessment criteria remain distinct resources even when a UI editor presents them together.

Provenance terminology is informed by [W3C PROV](https://www.w3.org/TR/prov-primer/). This draft does not require RDF or claim PROV conformance.
