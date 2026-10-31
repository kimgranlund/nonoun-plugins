---
name: knowledge-modeling
description: >
  Define and evolve domain concepts, typed relationships, evidence-backed mappings
  and interpretation rules. Use to model knowledge, reconcile vocabularies, audit
  semantic decisions or preserve meaning across revisions; not for ordinary prose
  edits or documentation navigation alone.
---

# Knowledge Modeling

Model, reconcile, audit or evolve the knowledge needed for the requested decision.
Start with the local definitions, source evidence and consumer contract. If they
settle the decision, use this entry and finish; supporting files are not prerequisites.
The project owns its meanings and policies. Use its existing output format.

## Decision checks

- Keep identities distinct from labels, and source/model scope explicit.
- Distinguish type, instance, part, membership and dependency; an edge permits only
  its defined inferences, not equivalence or access rights by association.
- Preserve source assertions, derivations and observations separately. Missing,
  unknown, inapplicable and zero are different outcomes.
- Apply mappings only for their evidenced purpose and context. Candidate matches,
  adopted correspondences and eligibility for an operation can differ.
- Separate shape validity, semantic correctness, inference and enforcement.
- Preserve historical interpretation when meaning or policy changes; bind consumers
  to the intended revisions rather than silently replacing old definitions.

## Open a reference only for an unresolved question

Identify the specific decision that more guidance could resolve. Read the relevant
module, then return to the task; a link to another module is not a required next step.
Missing domain evidence calls for a qualified answer or the missing source, not a
search through generic guidance. Do not load modules merely because their topic
appears in the request.

| Unresolved question | Reference |
| --- | --- |
| What must this model answer, and how much structure is needed? | [Scoping](references/scoping.md) |
| Are these different identities, classes, instances or scoped labels? | [Identity](references/identity.md) |
| What does this relationship permit a consumer to infer? | [Relationships](references/relationships.md) |
| How should claims, derivations, missingness or disagreement be represented? | [Evidence](references/evidence.md) |
| What correspondence supports this particular use across sources? | [Mappings](references/mappings.md) |
| How should an executable schema/check or representation conversion work? | [Validation](references/validation.md) |
| How can changed meaning coexist with retained records and consumers? | [Evolution](references/evolution.md) |
| How should concepts link to task-required documents? | [Context integration](references/context-integration.md) |

## Verify and stop

Check decisions against the governing evidence, including a supported case and a
misleading neighbor. For revisions, check a retained interpretation. Use actual
consumer tests when changing executable behavior. A source-only review can establish
these checks directly from evidence; do not create a test that only reasserts the
answer you just wrote.

Deliver the requested artifact, evidence, compatibility outcome and unresolved
limits. Stop when those decisions are supported or explicitly unknown and required
context has arrived. Do not expand every related concept or reference.

## Optional authoring and evaluation aids

When creating an artifact with no suitable local format, choose the relevant
[model brief](templates/model-brief.md), [concept/relation record](templates/concept-relation.md),
[mapping record](templates/mapping-decision.md) or [change assessment](templates/change-assessment.md).
If a representation pattern remains unclear, consult the relevant
[UI](examples/ui-catalog.md), [software](examples/software-catalog.md) or
[research](examples/research-corpus.md) example. They are synthetic illustrations,
not domain policy, and need not be read to perform a review.

Read [evaluation](references/evaluation.md) when designing a skill benchmark,
fresh-agent trial or comparative evaluation. It is not required for ordinary task
verification. Progressive-context owns discovery/delivery; use its guidance only
when those mechanisms need work. Neither companion is required for standalone modeling.
