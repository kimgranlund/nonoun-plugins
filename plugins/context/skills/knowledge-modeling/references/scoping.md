# Scope and representation

Use this reference to turn a broad modeling request into an adequate, bounded
model. Skip formal machinery that has no effect on the requested decisions.

## Questions before structure

Identify who uses the model, which operation depends on it, and what a wrong
answer would change. Write competency questions in terms of that operation:
"Which releases supply this behavior?" is more useful than "Is the graph complete?"
Include a common answer, a boundary and a case whose answer should remain unknown.
Acceptance concerns decisions and evidence, not the number of classes or edges.

Inspect the current vocabulary, data contract and consumers. A model is a proposal
until adopted through the owning project's normal process. Existing code establishes
behavior; it does not settle disputed intended meaning by itself.

For each consequential ambiguity, state the competing interpretations, the evidence
that could distinguish them and which work can proceed without resolving it. Ask
only for missing decisions that change the outcome; use available contracts first.

## Choose the smallest sufficient representation

| Need | Usually sufficient starting point | Escalate when |
| --- | --- | --- |
| Shared terminology | Definitions, scope notes and examples | Repeated disambiguation or automated consumption needs stable IDs |
| Browsing and discovery | Facets, a concept scheme or a small taxonomy | Typed cross-domain correspondences need explicit mapping records |
| Data interchange | Existing JSON/SQL schema plus a data dictionary | Cross-record rules or derived facts exceed its stated validation capability |
| Typed connected knowledge | Relational tables, JSON records or a property graph | RDF interoperability or formal entailment is an actual requirement |
| Logical classification | A declared OWL profile/reasoner or other formalism | The required inference cannot be expressed or checked in the chosen profile |

These are alternatives, not a ladder. A human-readable model can be exact; a graph
can be ambiguous. Storage format does not determine semantic quality.

Reuse an external vocabulary only where its definition, scope, license and version
fit the use. Preserve the external identity and record the local interpretation or
mapping. Shared labels are insufficient evidence for reuse. Do not claim SKOS,
PROV-O or another serialization's conformance just because their ideas informed
a local JSON model.

## Stop and hand off

The model is sufficient for the bounded task when its questions can be answered
with supported decisions, known unknowns are explicit, and a downstream reader or
consumer can reproduce those decisions. Record broader coverage as a separate
possible extension, not unfinished required work.

Use the [model brief](../templates/model-brief.md) proportionally. For a local
change, a few paragraphs can serve the same purpose.

## Basis

[Noy and McGuinness, Ontology Development 101](https://protege.stanford.edu/publications/ontology_development/ontology101-noy-mcguinness.html)
introduces competency questions, reuse and iterative modeling. It is foundational
method guidance, not a current tool-selection guide or one universally correct
ontology design.
