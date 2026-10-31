# Identity, terminology and classification

Use when labels collide, a catalog is being classified, or a concept is being
introduced or renamed. Keep enough identity to distinguish the decisions at hand.

## Identity before names

Distinguish a concept/type from an instance, release, observation and the document
that describes it. A package family, versioned release and installed copy may need
different IDs even when the display name is identical. A document can describe
several concepts; a concept can be described by several documents.

For an identified concept, record a definition, scope, examples and counterexamples.
Keep a stable ID independent of its display label and location. IDs must be unique
within the declared namespace; do not require one global vocabulary of unique words.
Clarify whether the namespace identifies concepts across releases or individual
versioned records. Consumers must resolve the intended model revision.

Qualify aliases by source, domain, language, release or context when those change
meaning. A lexical alias aids lookup; a cross-system correspondence belongs in a
[mapping record](mappings.md). Ambiguous aliases should return candidates with
their scopes, not silently resolve to whichever record appears first.

## Choose classification deliberately

- Use a subclass relationship only when every instance of the narrower class is
  an instance of the broader class under the stated interpretation.
- Use independent facets for orthogonal properties such as renderer, platform,
  interaction style or maturity. Do not force every combination into a deep tree.
- Multiple parents can be legitimate. A strict tree or acyclic hierarchy is a
  local modeling constraint, not a universal fact about all knowledge graphs.
- An instance-of relation links an individual to a class. A broader concept label
  in a thesaurus does not automatically establish formal class membership.
- A collection, tag or topic membership can organize discovery without changing
  the entity's type or authorizing a downstream comparison.

If using SKOS, distinguish `broader` from `broaderTransitive`, labels from concepts,
and concept schemes from logical class ontologies. Do not import formal subclass
inference into a looser classification unless it is explicitly defined.

## Useful checks

Try a homonym with two valid scopes, an unambiguous synonym, a renamed label with
the same identity, and two different instances of the same class. Check the actual
lookup or interpretation. A string uniqueness check cannot establish conceptual
distinctness, and matching numeric values cannot establish property equivalence.

If a requested definition change alters what the ID denotes, use the
[evolution procedure](evolution.md) rather than treating it as a spelling edit.

## Basis

[SKOS Reference](https://www.w3.org/TR/skos-reference/) defines concepts, labels,
concept schemes and semantic relations. Its preferred-label constraints are not
a guarantee of globally unique names. Use the [SKOS Primer](https://www.w3.org/TR/skos-primer/)
for patterns; local profiles must state any stronger constraints they enforce.
