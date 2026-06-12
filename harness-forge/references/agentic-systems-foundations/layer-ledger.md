# Ledger Layer — What Happened, What Was Decided, and Why

`Cell: ontology.fleet.layer-ledger · Status: defined · Register: established (W3C PROV, event sourcing, ADRs, telemetry practice)`

## Ledger Layer Definition

The ledger is veridical knowledge: the append-only record of what occurred, what was
decided, by whom, and why. It is the tensed layer — history and present state — where
the ontology is timeless structure. Every other layer describes or prescribes; the
ledger attests.

Lineage: W3C PROV (entity/activity/agent provenance graphs), event sourcing,
architecture decision records, distributed tracing and telemetry.

## Schema Early, Content Late

The ledger's content arrives last in any project, but its schema belongs in the first
slice: provenance cannot be retrofitted onto executions that did not record it. A
trivial ledger schema in week one beats a sophisticated one bolted on after the
incident that made everyone wish they had it.

## The Ledger as Intent History

The decision ledger is where intent provenance lives: who intended what, when, and
why it changed. Intent drift — divergence between the principal's current want and
the spec of record — is detectable only against this history. Every `regenerating`
transition is a ledger event; silent edits are the definition of drift.

## The Ledger Feeds the System That Writes It

Three downstream consumers close three loops:

- **Selection** — probe cost in the compass's value function is measured from ledger
  data (tokens and iterations per prior signal), replacing estimates with evidence.
- **Trust** — false-pass rates and reward-hacking incidents computed from the ledger
  drive the autonomy tiers in the policy layer's trust trajectory.
- **Regeneration** — distilled ledger windows become pattern candidates and upstream
  revision proposals.

## Durable State and Audit Discipline

State that must survive context windows lives on disk, not in conversation: the
lattice file, progress logs, signal artifacts, git history. Loop runs export a
tamper-evident audit trail (hook events to append-only JSONL). Workers record the
*why* alongside the what — rationale written into commits and artifacts, because
future iterations will not have this context window.

## Staleness Propagation

Cells record content hashes of the upstream cells they were validated against. When
an upstream cell changes, every dependent flips to `stale` mechanically — drift
detection as a graph computation, not a quarterly archaeology project.

## Ledger vs Ontology Boundary

Structure versus history. The ontology says what kinds of things exist; the ledger
says which things happened.

## Ledger Artifact Forms

Append-only event logs (JSONL; versioned stores where checkpoint semantics are
needed); decision records; signal artifacts under `signals/{cell-id}/`; trace exports;
`validated_against` hash sets on cells.

## Ledger Validation Signal

A ledger cell is `validated` when entries are demonstrably append-only (mutation
attempt blocked), every agent mission terminates in an entry (no silent work), and a
staleness propagation has been observed end-to-end.

## Ledger Failure Modes

Retrofitted provenance. Mutable history. Silent work (missions without entries).
Rationale-free records (what without why — useless for regeneration). Telemetry
collected but never routed back into selection, trust, or regeneration (a ledger
nobody reads is storage, not a layer).
