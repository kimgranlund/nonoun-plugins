# Semantic models and progressive context

Use when a task needs to discover the contracts that define domain meaning, or
when modeling exposes ambiguity in an existing context route. Both skills can
operate independently; their integration is a documented handoff, not a new runtime.

## Ownership

| Owner | Responsibility |
| --- | --- |
| Project/domain authorities | Definitions, native facts, accepted mappings, interpretation and operation policy |
| Knowledge modeling | Methods for designing, reconciling, auditing and evolving those meanings |
| Progressive context | Artifact discovery, task-required retrieval, delivery sufficiency and route evaluation |
| Runtime/application | Executable validation, inference or enforcement actually implemented |

Context Fog-of-War can provide observed retrieval evidence when available. A file
read or successful route does not establish that its semantics were understood.

## Keep identities and edges separate

Concept identity is not artifact identity. A concept may have several defining,
policy and evidence documents; one document may define many concepts. Preserve
model/version/scope in the domain model and artifact/revision/location in the
discovery system. Link the two with explicit references, not copied definitions.

Domain aliases are scoped vocabulary. In progressive-context's optional local JSON
profile, `aliases` means previous artifact IDs. Do not put arbitrary synonyms into
that field or let a homonym silently select one artifact. A separate resolver can
offer scoped candidate concepts and their defining sources.

Domain `part_of`, `is_a`, `related_to` and `depends_on` have domain-specific meanings.
They do not automatically create progressive-context `governed_by` or `depends_on`
retrieval edges. A package's runtime dependency, for example, need not be read in
full to answer a catalog question. No such edge grants execution permission.

## Minimal handoff

Start with ordinary links and a brief explanation of why a task needs each source.
For a consequential mapping task, the required material may include both source
definitions and the eligibility policy; optional related concepts can remain links.
For a label edit, the relevant naming/identity contract may suffice.

When machine-readable discovery is justified, identify the domain concept and
version/scope, the defining artifact(s), and the task that requires each contract.
Translate only explicitly justified requirements into the discovery system's native
relationship vocabulary. Its artifact descriptors retain their own revisions and
integrity checks. Keep semantic definitions authored in the domain authority.

Progressive-context's current local JSON profile accepts extension metadata but
does not execute it. A new `concepts` field, semantic resolver or graph-to-route
projection requires a separate adapter and tests before claiming runtime behavior.
Do not imply this skill supplies such an adapter.

## Verify the handoff

Use the same task to verify semantic decision correctness and required delivery
separately. Include a misleading alias, a related-but-optional source, and one task
that really does require an additional governing document. Verify the authoritative
body is delivered before the decision; a summary is only a locator.

On a model/policy revision, update or regenerate affected discovery metadata through
its owning workflow. Preserve historical routes or explicit version selection where
needed. The [evaluation contract](evaluation.md) describes paired trials without
confusing structural reachability, delivered content and independent correctness.
