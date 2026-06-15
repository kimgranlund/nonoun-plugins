# The Coordination Model — two lifecycles, one typed link

`Cell: methodology.system.coordination · Status: defined · Register: established lineage (Kanban / pull systems, event sourcing, single-writer concurrency); the ticket→maturity morphism is house (dev-factory's central reconciliation, TDD §4)`

This reference is the model `ticket-orchestration` operates against. Read it before triaging, planning, or reasoning about a ticket's state. It is the *why* behind the lifecycle machine; the machine itself is `policy/ticket-lifecycle.policy.json` (the typed mirror of `lifecycle.py`'s `LIFECYCLE`).

## The category error this model exists to prevent

A request to "make the ticket states match our lifecycles" hides a trap: the ticket states (draft, active, claimed, …) and the cell maturity machine (absent, defined, validated, …) are **not the same machine**, and fusing them is the category error the whole system is built to avoid (TDD §4). They are two ontological kinds:

| | Ticket | Cell |
| --- | --- | --- |
| **Kind** | Activity — an occurrent, coordination work that *happens* | Entity + maturity Property — a knowledge asset and its state |
| **Lifecycle** | `draft → active → claimed → in-progress → in-review → done` (+ `blocked`, `paused`, `cancelled`) | the eight maturity states |
| **Lives in** | the coordination corpus (the Kanban) | the lattice (`lattice.json`, the grid) |
| **Answers** | "what work is in flight and who holds it" | "what is known, and how well" |

Fuse them and "done in the tracker" and "validated in the system" become the same fact by fiat — which is exactly how drift between *what was claimed* and *what is true* becomes undetectable. The model keeps them distinct and links them with a **typed morphism**.

## The typed link (the morphism)

Every ticket declares a **`target_cell`** and a **`target_transition`** (`from → to` maturity). A ticket's entire purpose is to drive that one maturity transition. The binding rule:

> **Ticket `done` ⟹ the target cell's maturity advances to `to` — and that advance is itself gated by `gate-signal`.** A ticket cannot reach `done` for a signal-bearing transition unless the critic has emitted the signal the maturity transition requires.

This makes the two boards consistent **by construction**. The Kanban shows coordination state; the lattice grid shows knowledge state; the ticket is the typed morphism between them. There is **one gate**, and both transitions pass through it — so drift between "claimed done" and "actually validated" is structurally impossible, not merely policed.

`lifecycle.py` enforces it precisely: at `in-review → done`, a signal-bearing transition runs the validation path (the critic's signal, which the worker could not forge) and asserts the cell reached the ticket's `to`-maturity; an authoring transition (`→ defined`/`instantiated`) is applied by the server with no critic signal, because it makes no validation claim.

## Single-writer discipline (the claim race, designed out)

All coordination-state mutations pass through the **server** as the sole writer (REQ-CORPUS-003). Workers and agents never write ticket state directly. The dispatcher sets `claimed`; the validation path drives `in-review → done`. So the classic distributed-claim race — two workers grabbing one ticket — is **designed out, not mitigated**: workers do not claim, the server assigns, and assignment is serialized by construction. A worker that crashes after assignment is recovered by lease expiry, not by reconciling competing claims. The triager, planner, and arbiter therefore *propose documents*; the server applies the gated transition and appends the ledger event.

## The corpus is substrate, not a side database

The coordination corpus is itself a cell (`methodology.system.coordination`) with a schema, a maturity, and the capacity to go stale. Source of truth is **files on disk, git-versioned** (`coordination/tickets/`, `coordination/roadmap/`, `coordination/issues/`, the append-only `coordination/index.jsonl`); the server's SQLite read-index is **derived, never authoritative** — deletable and reconstructible by replay, exactly as `lattice.json` is canonical and every grid view is derived. JSON is harder for a model to clobber than prose, and a git-native corpus is diff-able and ledger-replayable. The board cannot disagree with the repo because the board *is* the repo, projected.

## Why this matters for every agent in the skill

The triager binds the morphism (a real cell, a legal transition, a validated rubric). The planner orders tickets so the morphism's upstreams validate first. The arbiter resolves the dependency graph that the morphism's readiness depends on. None of them writes ticket state, sets `claimed`, or touches the lattice or signals — those are the server's and the validation path's writes. Their judgment forms the ticket; the kernel and the server move it.
