# Methodology Layer — How Work Is Decomposed and Orchestrated

`Cell: ontology.fleet.layer-methodology · Status: defined · Register: established lineage (PDCA, TDD, published workflow patterns); routing law is house synthesis`

## Methodology Layer Definition

A methodology is procedural knowledge: how units of work are decomposed, sequenced,
and orchestrated *within one controller's authority*. The moment coordination crosses
an autonomy boundary — parties that do not share a controller — methodology ends and
protocol begins.

## The Engine as Core Procedure

The canonical inner procedure is the engine: `define → create → validate` on one cell
at the smallest scope that yields signal. Lineage: Shewhart/Deming PDCA,
red–green–refactor, build–measure–learn, tracer bullets and walking skeletons,
eval-driven development. Shared discipline: the probe is sized to the assumption, not
the ambition.

## Workflow Patterns (Established Vocabulary)

The published frontier-lab pattern set for composing model calls, in ascending
structure: prompt chaining, routing, parallelization, orchestrator–workers, and
evaluator–optimizer — with the standing rule to start with the simplest pattern that
works and add structure only when it pays for itself. The evaluator–optimizer pattern
is the generator/critic loop; orchestrator–workers is the dispatch shape behind
one-cell-per-agent execution.

## The Routing Law

Every behavior is placed by one rule:

> Deterministic → a script.
> Judgment in one pass → the main thread, equipped with procedural knowledge.
> Judgment across many steps, needing isolated context → a delegated agent.

Computation routes to code, never to inference: selection, ranking, staleness
propagation, and graph traversal are scripts. Model-predicted computation is a
hallucination surface.

## The Trajectory Rule

Depth-first along one thin vertical slice to `validated`; widen only from validated
footholds; rescan the full modality axis at every widening. The trajectory's shape is
the methodology's signature — see `lattice-model.md` for the three trajectory
cultures and their outcomes.

## Methodology vs Protocol Boundary

Methodology governs decomposition and sequencing inside one authority. Protocol
governs lawful interaction across autonomy boundaries. With two agents under one
orchestrator, methodology suffices; with two systems negotiating, protocol is
mandatory.

## Methodology vs Spec Boundary

The spec owns the *what*; methodology owns the *how*. Goals smuggled into procedure
let the how dictate the what — a category error the partial order exists to prevent.

## Methodology Artifact Forms

Engine procedure documents; workflow-pattern selections per loop family; dispatch
rules (one cell per worker, fresh context per dispatch); orchestration graphs with
explicit steps, retries, and stop conditions; the routing-law table itself.

## Methodology Validation Signal

A methodology cell is `validated` when a real slice has been driven through it
end-to-end with the gates firing — the procedure demonstrated, not described.

## Methodology Failure Modes

Orchestration maximalism (structure added before the simple pattern fails).
Computation by inference (the model "calculating" what a script should). Methodology
crossing autonomy boundaries it has no authority over. Procedures that exist only as
prose and have never produced a signal.
