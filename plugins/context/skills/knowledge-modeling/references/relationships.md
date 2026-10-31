# Relationships, composition and inference

Use when decomposing a system or assigning meaning to graph edges. A generic
`has_a` or `related_to` may be adequate for discovery, but cannot support a precise
inference until its meaning is defined.

| Relationship | Meaning to establish | Common invalid inference |
| --- | --- | --- |
| Subclass | Every instance of A is an instance of B | A component is a subtype of its enclosing system |
| Instance of | Individual A is classified by type B | Two instances are the same entity because they share a type |
| Part of | A is a constituent of B in a stated composition/context | A may read or modify every resource belonging to B |
| Member of | A belongs to a collection/group | Every group member is a structural part or inherits every property |
| Contained in | A occupies a physical or logical container | A necessarily depends on, is owned by or is a component of the container |
| Depends on | A requires B for a named behavior or lifecycle stage | B is shipped inside A, or every dependency requires reading all of B |
| Associated with | A relevant connection exists | The connection is equivalence, causality or transitive |
| Derived from | A was produced using B by a stated activity | A preserves every fact or has the same authority as B |

The table supplies questions, not mandatory predicate names. Adopt the project's
established relation vocabulary where its definitions fit.

## Specify only the inference you need

For consequential relations, declare direction, allowed endpoint kinds, relevant
context/time, and any cardinality, inverse or transitivity assumption. Include a
positive example and a misleading neighbor. Use the
[concept/relation record](../templates/concept-relation.md) if helpful.

Direct component membership and transitive parthood serve different queries.
Transitivity may be appropriate for a defined part relation; do not apply it to
every containment, membership, dependency or mixed-edge path. A cycle check also
depends on relation semantics: equivalence cycles are expected; some strict
composition hierarchies prohibit them.

Where composition changes over time or configurations, qualify the relation.
Distinguish an optional part, a required part and an actually observed part. Do not
turn a product's possible anatomy into a claim that every instance contains it.

In RDF/OWL, domain and range axioms commonly entail types; they are not ordinary
input rejection rules. If invalid endpoint types should reject data, express and
test an applicable validation constraint as described in [validation](validation.md).

## Trace the consequence

Ask what each proposed edge allows a consumer to conclude. If the requested
operation is aggregation, numerical comparison, migration, retrieval or permission,
identify that operation's separate conditions. A semantic relationship can supply
facts to those conditions; it does not implement the operation or grant authority.

Test the consumer on a mixed path or reversed edge, not just whether the JSON has
`subject`, `predicate` and `object` fields. Preserve unknown edges where evidence
does not support a more precise assertion.

## Basis

[OWL 2 Primer](https://www.w3.org/TR/owl2-primer/) explains individuals, classes,
properties and entailment. [W3C's simple part-whole pattern](https://www.w3.org/2001/sw/BestPractices/OEP/SimplePartWhole/)
is an older editor's draft useful for direct/transitive part patterns; do not use
its historical tool limitations as current implementation guidance.
