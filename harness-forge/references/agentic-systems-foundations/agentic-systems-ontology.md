# Agentic Systems Ontology

`Cell: ontology.fleet.agentic-systems · Status: defined · Register: synthesis over PROV, BPMN/CMMN, and frontier-lab vocabulary`

This document is the vocabulary source of truth for the knowledge base. Every other
document composes its terms from the controlled vocabularies defined here. A term not
defined here is not yet part of the system; adding one is an ontology revision — a
ledgered change, not an ad-hoc usage.

## Units of Work (UOW)

A **Unit of Work (UOW)** is a Property, Activity, or Entity. The trichotomy splits on
a classical ontological distinction:

- **Entity** — a continuant: a thing that exists and is consumed or produced. Inputs,
  outputs, documents, schemas, artifacts. A *plan* is an Entity (the document); its
  execution is an Activity. (W3C PROV makes the same call: `prov:Plan` is an Entity.)
- **Activity** — an occurrent: a thing that happens over time. Tasks, runs, jobs,
  steps, loop iterations.
- **Property** — an attribute borne by an Entity or Activity: a maturity state, a
  score, a budget, a timestamp.

## The Agent Class

**Agent** is the fourth class, deliberately separate from UOW: the actor that performs
Activities and produces Entities. PROV's trichotomy is Entity / Activity / Agent;
dropping the Agent class is the root cause of foundations that cannot describe actors,
authority, or delegation. Agents are described by the Capability layer and interact
through the Protocol layer.

**Principal** — the special case of an Agent that originates intent (a human, an
organization, or a delegating agent). Principals form a precedence hierarchy
(see `layer-capability.md`).

## The Nine Foundation Layers (Modality Axis)

Each layer is a kind of declarative knowledge about UOW, distinguished by the question
it answers. The set is closed; extending it is an ontology revision.

| Layer | Modality — the question it answers |
|---|---|
| `ontology` | Descriptive — what is it, how does it relate |
| `spec` | Constitutive / teleological — what counts as done; the target |
| `rubric` | Evaluative — how well does it score |
| `policy` | Deontic — what is permitted, obligatory, forbidden |
| `capability` | Attributive — who may act, with what competence and authority |
| `methodology` | Procedural — how work is decomposed and orchestrated |
| `protocol` | Interactional — lawful exchange across autonomy boundaries |
| `ledger` | Veridical — what happened, what was decided, and why |
| `pattern` | Precedential — what has worked in this context before |

One layer-per-document treatment lives in the `layer-*.md` files. Intent is
deliberately not a layer: it is the working fluid the layers process
(see `layer-spec.md` for its canonical residence).

## Scope Ladder

The grain axis of work. Five rungs, smallest to largest:

| Scope | Definition |
|---|---|
| `call` | A single model or tool invocation |
| `task` | One unit of work with its own acceptance criteria |
| `workflow` | An end-to-end slice composed of tasks |
| `system` | A deployed, multi-workflow or multi-agent system |
| `fleet` | A portfolio of systems sharing substrate |

The same layer at two scopes is two distinct assets. A task-scope rubric does not
validate a system-scope one.

## Maturity States

Every knowledge asset (cell) carries exactly one maturity state:

| State | Meaning |
|---|---|
| `absent` | Identified by the scan; does not exist |
| `defined` | Schema or intent drafted; typed but unproven |
| `instantiated` | The artifact exists and is wired in |
| `validated` | A signal artifact evidences it at the current scope |
| `operating` | In production; emitting ledger entries |
| `regenerating` | Under deliberate, ledgered revision |
| `stale` | An upstream dependency changed; validity unknown |
| `deprecated` | Retired; retained for provenance |

`blocked` is a condition flag, not a maturity state: it marks a cell whose advancement
loop hit a budget cap or a no-progress signature.

## Core Nouns

- **Cell** — one layer at one scope with a maturity state; the unit of the lattice.
  Identity: `{layer}.{scope}.{slug}` (e.g., `rubric.workflow.citation-integrity`).
  Maturity is a Property, never part of the identity.
- **Lattice** — the full grid of cells for one project; canonical state in
  `lattice.json`; everything else is a derived view.
- **Signal** — the evidence artifact produced by validation; the only currency
  accepted at scope boundaries.
- **Loop** — one closed-control run: generate → execute → verify → decide → repeat
  until a stop condition. One engine pass on one cell is one loop.
- **Verifier** — the mechanism that checks a loop's output: a rubric cell bound to a
  harness adapter. A loop without a verifier is a random walk.
- **Stop condition** — the predicate that ends a loop: signal produced, budget
  exhausted, or no-progress detected.
- **Harness** — everything around the model: environment, tools, durable state,
  gates, and orchestration. The kernel is a harness factory.
- **Kernel / Kit / Instance** — the three tiers: invariant machinery (kernel),
  family bindings (kit), and accreted project state (instance). Flow is one-way:
  kernel defines contracts → kits implement → instances bind and accrete.

## Vocabulary Discipline

Directory names mirror enum values byte-for-byte (`spec/`, never `specs/`). Composed
names draw only from the controlled vocabularies in `naming-conventions.md`. The
naming system is itself a cell in this ontology and is mechanically enforced.
