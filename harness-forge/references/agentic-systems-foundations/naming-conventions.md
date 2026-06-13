# Naming Conventions — Typed Names for the Whole System

`Cell: ontology.fleet.naming · Status: defined · Register: house convention; BEM and token-hierarchy lineage`

## Naming Principle

Names carry type. Every composed name in the system decomposes into atoms drawn from
closed, declared vocabularies. A name that cannot be parsed against the grammar is a
defect, caught mechanically. The convention itself is a cell in the ontology —
versioned, regenerable, and enforced by a gate, not by review comments.

## Tier 1 — Primitive Vocabularies (closed enums)

```
layer    := ontology | spec | rubric | policy | capability
           | methodology | protocol | ledger | pattern
scope    := call | task | workflow | system | fleet
maturity := absent | defined | instantiated | validated | operating
           | regenerating | stale | deprecated
tier     := kernel | kit
block    := lattice | frontier | cell | signal | kit | {layer}
```

## Tier 2 — Operation Vocabulary (closed verb set)

```
operation := seed | audit | scan | rank | advance | define | create
           | validate | record | distill | regenerate | conform
           | author | scaffold | widen | block | unblock
actor     := auditor | advancer | distiller | regenerator | librarian
           | builder | scribe | council
gateverb  := gate | propagate | emit
```

Extending either tier is an ontology revision: a ledgered `regenerating` transition
on this cell, never an ad-hoc coinage. (Revisions on record: `council` actor, added
0.3.0 for the structural council; `block`/`unblock` operations, added 0.4.1 for the
bounded loop's stop-gate. The machine copy is `schemas/naming.schema.json`.)

## Tier 3 — Composition Grammars

| Artifact class | Grammar | Examples |
|---|---|---|
| Plugin | `{ns}-{tier}[-{family}]` | `frontier-kernel`, `frontier-kit-corpus` |
| Skill folder | `{block}-{operation}` | `frontier-rank`, `cell-validate` |
| Agent file | `{object}-{actor}.md` | `cell-advancer.md`, `pattern-distiller.md` |
| Hook script | `{gateverb}-{invariant}` | `gate-signal`, `propagate-staleness`, `emit-ledger` |
| Skill script | `snake_case`; `_` prefix = private | `rank.py`, `_inventory.py` |
| Schema file | `{noun}.schema.json`; `$id` PascalCase | `cell.schema.json` → `Cell` |
| Cell ID | `{layer}.{scope}.{slug}` | `rubric.workflow.citation-integrity` |
| Signal path | `signals/{cell-id}/{ISO-ts}--{harness}.json` | `…/2026-06-11T09-14--link-check.json` |
| Layer directory | identical to layer enum, singular | `spec/`, never `specs/` |

## Naming Rules

1. **Directories mirror enums byte-for-byte.** One vocabulary, two projections
   (filesystem and JSON). No plural drift, no synonyms.
2. **The namespace never repeats inside members.** The plugin is the block scope;
   members never restate it (`frontier-kernel` ships `cell-advance`, never
   `frontier-cell-advance`). BEM scoping applied to plugins.
3. **Public/private split.** Triggerable skills and their descriptions are public
   API; underscore-prefixed scripts are private implementation — the
   `--component-*` / `--_*` token distinction, transposed.
4. **Identity excludes state.** Cell IDs carry layer, scope, and slug; maturity is a
   Property in the record. Renaming on state change is a drift generator.
5. **Casing by class.** `kebab-case` for plugins, skills, and agents; `snake_case`
   for scripts and tool names; `PascalCase` for schema `$id`s; dot-separated axes in
   cell IDs; hyphens inside slugs.
6. **Gateverbs carry semantics.** `gate-*` blocks (invariant enforcement),
   `emit-*` injects (feedback into a running loop), `propagate-*` cascades
   (graph effects like staleness). The verb tells the reader the control species.

## Self-Hosting Enforcement

The convention ships as machine-readable data (`naming.schema.json`); a write-time
gate parses every created path against it. The naming system is governed by the same
maturity machine it names — and a name rejected by the gate is feedback to fix the
name or, deliberately and ledgered, to revise the vocabulary.
