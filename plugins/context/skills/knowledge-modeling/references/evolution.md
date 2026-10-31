# Evolution and historical compatibility

Use when changing definitions, classifications, mappings or rules that existing
data or consumers already use. Renaming a file is not necessarily a semantic
change; a short definition edit can be one.

## Identify what changed

| Change | Check |
| --- | --- |
| Label, prose or location | Identity and meaning remain stable; aliases/links still resolve |
| Definition, relation or applicability | Which entities or conclusions now differ? Does the ID still denote the same thing? |
| Record shape | Which readers/writers need migration or compatibility handling? |
| Mapping or eligibility policy | Which operations change even when source facts are unchanged? |
| Source release or method | Which observations and derivations refer to the old evidence/context? |

Use distinct model, schema and policy identities where they evolve independently.
A single version can suffice for a tiny jointly released artifact if consumers
cannot confuse its meanings; do not force an elaborate version system without need.
Avoid claiming semantic-version numbers alone guarantee meaning preservation.

## Preserve the old interpretation

Retain released definitions and evidence needed to interpret existing records.
Bind consumers to the intended model/policy release, not a mutable `latest` view.
If an ID's referents materially change, introduce a distinct identity or an explicit
version-scoped replacement under the project's compatibility contract. Do not
silently reuse an unversioned ID for a different meaning.

Document supersession, deprecation and replacement precisely. A replaced term may
have several candidates rather than one exact successor. A discovery redirect
does not authorize rewriting historical data or transferring every old assertion.

Use a preview or migration proposal where appropriate, then follow the existing
adoption process and user authorization. A check should not implicitly promote a
new release or rewrite generated authorities.

## Impact and verification

Inspect dependent queries, mappings, exports, descriptors and caches. Check the
inputs actually consumed by generated outputs; unchanged output bytes alone may
hide a changed meaning. For consequential revisions, demonstrate:

- One old record/query still resolves to its original interpretation or takes an
  explicitly documented migration path.
- One new case receives the new intended behavior.
- One previously valid neighbor remains valid, while an unsupported mixed-version
  or context combination is rejected or left unresolved as appropriate.

Record whether the production reader can actually select the new version. A new
registry file without storage/query support is a proposed release, not a completed
migration. Keep the project's requested format. The
[change assessment](../templates/change-assessment.md) is an optional starting point
when no suitable local record exists; reading it is not a migration prerequisite.

## Basis

[OBO term stability](https://obofoundry.org/principles/fp-019-term-stability.html)
distinguishes meaning-preserving clarifications from changes requiring new identity.
Reuse that preservation principle without imposing OBO-specific identifiers or
biomedical governance on unrelated domains.
