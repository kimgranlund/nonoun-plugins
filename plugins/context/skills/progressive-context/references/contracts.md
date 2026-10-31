# Optional local JSON contract

Use this profile when deterministic discovery is useful. Small corpora may keep
ordinary Markdown indexes. YAML, databases and remote APIs need explicit adapters;
the supplied tools implement local UTF-8 files and JSON only.

Canonical schemas: [descriptor](../schemas/descriptor.schema.json) and
[registry](../schemas/registry.schema.json). `validate.py` checks required fields,
identity, file/hash integrity, aliases, references, dependency cycles and routes.
It is a focused validator for this profile, not a general JSON Schema interpreter.

## Descriptor fields

Required: `id`, `location`, `kind`, `summary`, `revision`, `sha256`, all nonempty
strings. SHA256 is lowercase hex of the exact referenced file bytes. A revision
is a publisher-supplied identifier; a hash detects byte drift, not conceptual age.
`location` is relative to the explicitly supplied corpus root, never cwd or the
registry file. Absolute paths and symlink escapes outside that root are rejected.

Optional: `aliases` (previous IDs), `owner`, `authority` (corpus-local declaration),
`status` (active or deprecated), `relationships`, `directives`, `sourceDigests`.
Additional extension fields are allowed but have no executable meaning here.
Use ownership and lifecycle when needed; they are not universal minimums.

Domain vocabulary and concept-to-artifact links follow the optional
[semantic handoff](semantic-handoff.md). Domain synonyms are not previous artifact
IDs; new semantic metadata does not change this profile's traversal behavior.

Relationships are ID arrays: `governed_by` and `depends_on` are required route
edges; `references` and `supersedes` are inspectable metadata and are not followed
eagerly. References use canonical IDs; aliases are only external entry locators.
IDs and aliases must be unique. Supersession never silently overrides constraints.

`directives` is an optional string-valued map of comparable corpus policy facts.
The replay blocks if required artifacts declare different values for the same key.
This catches declared conflicts only, not contradictions in arbitrary prose. No
field grants precedence over actual harness instructions.

`sourceDigests` maps root-relative source paths to SHA256 for generated artifacts.
Its check detects changed declared inputs. It does not prove generator correctness
or that all inputs were declared. The generator must be separately tested. Prefer
authored descriptors as the source of truth and a generated registry; record the
generator/owner in extension metadata. Refresh by regenerating, never copying stale
hashes merely to silence a check. Keep stable IDs and aliases across moves.

## Registry fields

`schemaVersion: 1`, `entry` (root-relative entry path), `artifacts` (inline canonical
descriptors), and optional `routes` (`intent`, `target` pairs). Exact intent keys
are for deterministic routing; ambiguous natural-language requests need a resolver
outside this tool. A task may also supply a known ID/alias directly.

A standalone descriptor check validates its own shape and bytes; relationship
resolution requires registry validation. Registry validation is deliberately global
and fails closed on a broken declared contract. Interactive discovery can instead
review the relevant local scope under the traversal workflow.

## Integrity boundaries

Hashes are not signatures or claims of trusted authority. Do not execute commands
in corpus files. The validator reads declared files only and does no network access.
Report structural success separately from semantic summary quality and observed
model delivery. Add a task acceptance check for any summary that could misroute.

## Discovery metadata versus delivery receipts

`summary` is routing metadata, not the component contract. Follow the location to
establish task-required anatomy, dependencies, runtime prerequisites and implementation
entry. Keep these requirements in the authoritative source; do not copy them all
into a growing index. Required relationships should lead to governing/runtime
contracts; optional examples remain references.

Delivery receipts belong to run evidence, not durable descriptors. Bind every
receipt to source identity/revision/hash and distinguish summary, projected fields
or records, pages and full content. Store exact return coverage, truncation reason
and continuation when available. A known source hash proves identity, not complete
delivery. The [replay contract](evaluation.md) defines this local simulation's
receipt format and conservative full-contract acceptance.
