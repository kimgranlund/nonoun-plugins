# Manifests, registries and modes

Load when a corpus describes its items in per-item files (component manifests, skill frontmatter, API descriptors, dataset cards) and indexes them upstream (a registry, catalog, index or CONTEXT file), or when an author route and a consumer route need separating. For vocabulary inside the manifests, use [the vocabulary layer](vocabulary/model.md); for relation semantics, [relationships](modeling/relationships.md); for how agents reach the files, [entry files](routing/entry-files.md).

Contents: [Layers](#layers) · [Manifests](#manifests) · [Registries](#registries) · [Rules and checks](#rules-and-checks) · [Authoring and consuming](#authoring-and-consuming) · [Operations](#operations) · [JSON or TypeScript](#json-or-typescript) · [Review checklist](#review-checklist)

## Layers

| Layer | Holds | Source or generated |
|---|---|---|
| Vocabulary | Terms: one meaning each, aliases, retired labels | Source (`vocabulary.yaml`, `terms.json`) |
| Taxonomy | Closed classifications: kinds, families, levels, statuses | Source (enums in the schema) |
| Ontology | Typed relations and the constraints on them (`composes`, `family`, "never upward") | Source (schema plus lint) |
| Manifest | One item: identity, intent, contract, relations, guidance, provenance | Source, one file per item |
| Registry | The index of items, for routing | Generated from manifests |
| Entry files | Routes from a task to the files it needs | Source, with generated inventories |

Every fact has one home in that table. A copy elsewhere is generated from it, says so in its header, and is checked for staleness.

## Manifests

One file per item, named for its stable id (`<id>.manifest.json`). Fields, in reading order:

- **Identity:** `id` (stable, lowercase-hyphenated, never reused), `kind`, classification fields (`family`, `role`, `level`), `status`.
- **Intent:** `summary` (one sentence: what it is and why its shape is what it is), when to use it, `instead` (`{when, use}` pointing at another id).
- **Contract:** what a consumer may rely on: anatomy or parts, inputs (props, variants, states), outputs or events, accessibility, keys.
- **Relations:** typed edges by id (`composes`, `family`, `dependsOn`). An edge permits only the inferences its definition gives.
- **Guidance:** rules with a reason each, do/don't pairs that a specimen can show, examples.
- **Provenance:** source, version or revision, what generated it when it is not hand-written.

Keep normative data (the contract), guidance and examples apart, so a tool can read the contract without parsing prose. Inheritance is explicit: a family or base file sets defaults and the manifest writes only what differs; the generator writes the merged form.

## Registries

A registry is generated from the manifests and never edited by hand. Each entry carries enough to choose an item without opening its manifest: id, kind, every classification field consumers route by, status, a one-line summary and the path to the full record. Dropping a routing field in the projection is a defect (a consumer can no longer tell a part from a pattern). A registry also states what generated it.

`scripts/check_registry.py` checks this for JSON manifests and registries: closure both ways (`missing-entry`, `orphan-entry`), duplicate and malformed ids, routing fields kept unchanged (`--keep family,role,status`), entry paths that resolve, and a `generated` marker.

```bash
python3 scripts/check_registry.py --registry dist/registry.json --entries patterns \
  --manifests 'src/patterns/*/*.pattern.json' --keep role,family,status
```

## Rules and checks

- **A rule stated in an entry file that no check enforces is a wish.** For each classification or relation rule, name the lint or test that fails when it breaks, or mark the rule as judgement.
- **Closure both ways.** Everything declared is used and everything used is declared: `composes` against the layout, the ordered list against the folders, a terms catalogue against the names a generator emits.
- **Every check has a negative control.** A mutated copy (a dropped field, a cross-family edge, an empty class) must fail it. A check that passes everything proves nothing.
- **No catch-all classes.** Every item has exactly one value per classification; an empty class is either removed or declared intentional (`role: foundation`).
- **Status measures evidence, not completeness.** A score that only counts filled sections cannot tell a mature item from a drafted one; tie `stable` to criteria that need evidence (reviewed, used in a shell, tested).

## Authoring and consuming

Two audiences, two routes:

| | Consumer (uses items) | Author (changes items) |
|---|---|---|
| Reads | Registry or index, then one manifest, then examples | Authoring guide, schema, lint, build steps |
| Gets | Generated artifacts (a packaged skill, an index, a context file) | Sources |
| Never needs | Authoring guides, lint internals, build order | Consumer tutorials |
| Done means | The item is used as its contract says | The build, lint and tests are green |

The entry file splits the two in its first lines ("Using the kit → …; changing the kit → …"), and each document states which mode it serves. A consumer route that passes through authoring documents is a routing defect; test it as described in [briefs and acceptance](review/briefs-and-acceptance.md).

## Operations

Each operation is a procedure with a tool, not a habit:

- **Create:** scaffold from a template, add the id to the ordered list, run the build that lints and regenerates the registry.
- **Rename:** keep the id or record the old one as an alias; rewrite references in the same change; the old label becomes a retired label in the vocabulary.
- **Deprecate:** `status: deprecated` with `replacedBy` and a removal date; keep the entry until no consumer uses it.
- **Delete:** only after a reverse-reference check finds no user; history lives in version control, not in copies.
- **Change the schema:** version it, migrate every manifest in the same change, and regenerate.

## JSON or TypeScript

Prefer JSON plus JSON Schema as the source: every tool, language and agent reads it without a build, and the schema doubles as documentation. Generate TypeScript types from the schema (or check manifests with `satisfies` against generated types). Use TypeScript as the source only when values must be computed; then emit JSON as the published form, so consumers never execute code to read a manifest. YAML suits hand-edited vocabularies and rule sets with comments; keep machine-generated files JSON.

## Review checklist

1. Each fact has one home; every copy is generated, marked and drift-checked.
2. Ids are stable; renames keep aliases.
3. Every closed set is declared once in a schema; no catch-all values.
4. Every stated rule names its check, and every check has a negative control.
5. Closure holds both ways for each declared/used pair.
6. The registry keeps every field consumers route by.
7. Entry files split author and consumer routes in their first lines.
8. Create, rename, deprecate and delete each have a procedure.
