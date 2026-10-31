# Handoff to semantic modeling

Use when a retrieval problem depends on what domain concepts or relationships mean.
Progressive-context owns required discovery and delivery. When available, the
`knowledge-modeling` skill can define, reconcile, audit or evolve domain meaning;
its context-integration reference owns the semantic side of this handoff.

Keep the domain model in its project authority. Route to its definitions, mapping
decisions and interpretation policy as the task requires. A semantic summary can
select sources but cannot replace required contracts.

## Consuming a domain model

- Domain concept IDs and retrievable artifact IDs have different scopes and a
  many-to-many relationship. Preserve references between them rather than copying
  definitions into the discovery registry.
- Domain synonyms are not the local JSON profile's `aliases` (previous artifact IDs).
  Disambiguate source/language/model scope before selecting a governing document.
- A domain relation does not automatically become a required retrieval edge.
  Justify `governed_by` and `depends_on` for the actual task; related material can
  remain optional. Domain dependencies and retrieval dependencies may differ.
- An extension metadata field has no executable effect in the existing profile.
  A semantic resolver or projection needs its own tested adapter before it can be
  advertised as functioning runtime integration.

Verify the handoff with both semantic acceptance and this skill's
[delivery evaluation](evaluation.md). Include a task needing a governing definition
and one related-but-optional source, so both omission and indiscriminate expansion
can be detected. The [descriptor contract](contracts.md) and its executable tools
remain unchanged by this optional companion.

If knowledge-modeling is unavailable, follow the local domain authority directly.
Neither skill introduces a new approval authority or runtime permission boundary.
