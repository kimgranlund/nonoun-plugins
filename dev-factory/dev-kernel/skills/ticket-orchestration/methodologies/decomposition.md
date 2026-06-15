# Decomposition — epic → dependency-ordered ticket set

`Cell: methodology.system.decomposition · Status: defined · Register: established lineage (work breakdown structures, dependency-ordered planning, vertical slicing / tracer bullets); the partial-order-as-ordering-constraint is house (dev-factory's lattice partial order)`

This is the playbook `roadmap-planner` and `ticket-triager` run: how an epic becomes a backlog of tickets that are *dispatchable when their turn comes*, and how a raw draft/issue becomes one well-formed ticket. The *ordering arithmetic* (readiness, ranking) is the compass's; this methodology is the *carving* judgment that precedes it.

## The unit a ticket targets

Every ticket targets **one cell** and **one maturity transition** (`from → to`). That is the atom. A "ticket" that would advance several cells is not a ticket; it is an epic that has not been decomposed yet.

- **epic** → a `workflow`/`system`-scope cell; decomposes into the finer-grained cells (and their tickets) that *entail* its outcome.
- **feature / task** → a cell + transition delivering capability.
- **bug** → a correction to an `operating`/`validated` cell (target `regenerating → validated`).
- **spike** → a time-boxed probe sized to one assumption; usually `defined`-only, may produce a pattern.
- **issue** → an observation not yet triaged; targets nothing until triage binds a cell.

## Decomposing an epic (the planner's pass)

1. **Name the epic's cell and outcome.** What `workflow`/`system` cell does this epic advance, and to what maturity? That is the parent the decomposition must entail.
2. **Carve into child cells along real seams.** Break the outcome into the cells that, jointly satisfied, *entail* the parent's outcome — across layers and down the scope ladder. A covering that does not entail is unsound: satisfying the children would leave the parent unmet.
3. **Order by the layer partial order.** `ontology + spec → rubric, policy, capability → methodology, protocol → ledger → pattern`. The verifier-producing cells (rubrics) go **upstream** of the work they verify, because a downstream ticket cannot pass `gate-ticket-ready` until its `acceptance` rubric is already `validated`. Plan the rubric ticket before the spec ticket that binds to it.
4. **Slice vertically first (tracer-bullet).** Order the thinnest end-to-end chain to the *first real signal* ahead of breadth. A vertical slice to `validated` beats a wide plan at `draft`. Widen only from validated footholds.
5. **Declare every dependency edge.** Each ticket records its `dependencies` (upstream tickets + cells that must be `validated`). The partial-order filter reasons over these; an undeclared edge is an unready ticket the compass cannot place.
6. **Check for cycles.** If two tickets depend on each other, the decomposition is unsound — hand the contested subgraph to the `dependency-arbiter`, do not order around it. A circular-verifier deadlock that ships is the canonical decomposition failure.

## Triaging one draft/issue into a ready ticket (the triager's pass)

The output must satisfy `gate-ticket-ready` (`lifecycle.py`), so produce each predicate:

| Field | What makes it ready |
| --- | --- |
| `target_cell` | a cell that exists in the lattice (an issue with no target is triaged into a feature/task first) |
| `target_transition` `{from, to}` | a transition the maturity machine permits |
| `acceptance.rubric_cell` | bound to a rubric cell that is **itself `validated`** — doneness is a validated rubric, not prose |
| `budget` | iterations **and** tokens (a prose budget is advisory under pressure) |
| `dependencies` | declared, even if `{}` |
| `priority` `{risk, unlock}` | the compass's cold-start estimate, replaced by ledger evidence as it accrues |

The binding that most often fails: **acceptance must point at a `validated` rubric.** If none exists, the rubric's create+validate ticket is a *dependency* you declare and order upstream — never a prose criterion you slip past the gate.

## What stays deterministic (not this methodology)

Readiness (are this ticket's dependencies validated?), ranking (`(risk × unlock) ÷ probe-cost`), and cycle *detection* are `lifecycle.py`/`compass.py`/`lattice.py` — arithmetic and graph traversal, never inference. This methodology is the carving and binding *judgment*; the moment the question becomes "which is ready / which is highest-value / is this a cycle," the answer is the kernel's, not the planner's.

## Failure modes

A ticket targeting several cells (not decomposed). A leaf with prose acceptance (no validated rubric bound — the gate denies it downstream). A rubric ordered *after* the work it verifies (the downstream ticket never goes active). A breadth-first plan at `draft` with no vertical slice to a real signal. A declared "no dependencies" that is really undeclared ones. A cycle ordered around instead of resolved (circular-verifier deadlock).
