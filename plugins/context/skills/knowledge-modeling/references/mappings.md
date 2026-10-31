# Mapping and reconciliation

Use to connect vocabularies or source systems without erasing their own meanings.
Record correspondence separately from the original assertions it helps interpret.

## Start with the intended operation

A correspondence sufficient for search expansion may be insufficient for numeric
aggregation, substituting an API or migrating data. Identify the use and what an
incorrect match would change before selecting a mapping relation.

Inspect definitions, scope notes, examples, context and versions on both sides.
Use lexical or embedding similarity to propose candidates; do not treat it as
adjudication. If multiple plausible targets remain, preserve alternatives and the
reason the current evidence cannot select one.

## Record the assertion

Use the project's existing format or the [mapping record](../templates/mapping-decision.md).
Include:

- Source and target identities, including model/source versions that affect meaning.
- Direction and correspondence type: equivalent for the stated scope, broader,
  narrower, related, or unresolved; use an existing formal predicate only when its
  actual semantics apply.
- Intended use and context; exclusions or preconditions for applying the mapping.
- Evidence, method, rationale, uncertainty and decision status/owner where relevant.
- The consuming rule or policy that allows the requested downstream operation.

Do not encode conditional equivalence as an unqualified globally transitive
relation. If the target format cannot retain required scope, use a qualified
mapping record or document the unsupported export instead of silently dropping it.

For SKOS, `exactMatch`, `closeMatch`, `broadMatch`, `narrowMatch` and `relatedMatch`
have different semantics. `exactMatch` supports transitivity; `closeMatch` does not.
Neither a broad/narrow match nor a shared label grants arbitrary substitution.
Class equivalence and identity of individuals are also distinct from SKOS mapping.

## Candidate, adopted and usable are different

Follow the local lifecycle. A proposed match, an accepted correspondence and a
mapping eligible for a particular operation may be separate states. An automated
validator must not promote one by merely changing a label or passing field checks.
Do not impose a new human approval ceremony if the existing task authorization and
local policy already settle the decision.

Preserve native records even after adopting a mapping. Record new mapping/policy
versions without silently changing the interpretation of retained outputs. Use
[evolution](evolution.md) when mappings change.

## Check both sides of the decision

Test an actually supported mapping and a misleading neighbor. Trace one consumer
operation using the stated preconditions. A valid mapping may legitimately be
usable for discovery while a comparison remains ineligible. An unresolved case
should name the missing definition, context or adjudication criterion.

## Basis

[SKOS mapping vocabulary](https://www.w3.org/TR/skos-reference/#mapping) defines
formal mapping properties. [SSSOM](https://mapping-commons.github.io/sssom/dev/)
adds exchangeable mapping metadata such as justification and provenance. Its linked
development docs are a design reference; choose and pin a supported release before
implementing an adapter. An exchange format does not decide local fitness for use.
