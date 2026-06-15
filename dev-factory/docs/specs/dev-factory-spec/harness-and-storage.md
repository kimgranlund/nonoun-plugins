# Harness & Storage — Leveraging the Substrate the Factory Runs On

`Cell: methodology.fleet.harness-and-storage · Status: defined · Register: established (Claude Code surfaces, event sourcing, embedded/columnar/relational DB practice); the two-plane typing rule is house synthesis`

## The Harness Is the Unit of Engineering

An agent is a model using tools in a loop; everything that makes it reliable lives *around*
the model. Engineering the factory means mapping each system function onto a concrete
harness surface, not an abstract box. The safety boundary in particular is not a diagram —
it is hooks denying writes and a database accepting writes from exactly one process.

| System function | Harness surface |
|---|---|
| Substrate artifacts, worktrees, ledger, signals | **filesystem + git** (the substrate plane) |
| Worker / critic / architect roster; delegation | **subagents** |
| Compound capabilities (lattice-management, cell-engine, …) | **skills** (folders, model-invoked) |
| Gates and feedback — where policy becomes enforcement | **hooks** (PreToolUse deny on protected paths; PostToolUse feedback) |
| Deterministic computation (scan, rank, staleness, lease reconcile, reports) | **bash / code execution** |
| Operational status + queryable history + CRUD + reports | **database** (the operational plane) |
| Exchange across boundaries; DB read access for agents; runtime dispatch | **MCP tools** (the protocol boundary) |

Two principles fall out immediately. **Gates live at the harness's actual control points**
— the immutable/rewritable boundary is realized by hooks that deny writes to `rubric/`,
`signals/`, `ledger/`, and the hooks themselves, not by a sentence in a doc. And
**computation routes to code** — the compass and staleness propagation are bash/Python over
the data, never inference.

## Two Planes, One Typing Rule

The corpus splits into two planes with different durability and audit needs. The rule that
assigns data to a plane:

> **Artifact bodies → files. Tensed status and queryable history → database.**

| | Substrate plane (files + git) | Operational plane (database) |
|---|---|---|
| Holds | spec/rubric/policy/pattern **content**, signal files, cell artifacts | ticket lifecycle **state**, cell maturity **status**, leases, timestamps, metrics, the lattice grid |
| Why here | the outer loop rewrites/diffs/reviews/gates it; a model edits files more safely than opaque rows | fast filtered queries, joins, aggregations, reports, live CRUD |
| Authority | files-of-record, git-versioned | a **materialized projection** — derived, rebuildable |

Conflating "the ticket" (operational) with "the spec it advances" (substrate) is the
category error this rule prevents. The database stores *pointers* to artifacts (`asset_ref`,
`signal_refs`, hashes), never the artifact text.

## Event-Sourced Core

The two planes reconcile through one spine:

- **The append-only ledger is the source of truth for every state transition** (git-native
  JSONL; provenance cannot be retrofitted, so the ledger is authoritative and the database
  is downstream of it).
- **Current state is a materialized view of the ledger** in the database. Ticket states, the
  lattice grid, leases, and metrics are *folds over the event log* — and the entire operational
  store is **rebuildable by replaying the ledger**. A corrupted index is not a disaster; it is
  a `DROP` and a replay.
- **The single-writer server is where the planes meet.** One write path: append the ledger
  event → materialize the affected rows → (the artifact write itself went to the filesystem
  through a gated worker) → push the diff to connected UIs.

## What Kind of Database

The choice is scope-dependent. Resolving the prior open decision:

**Instance scope (now): SQLite, + DuckDB for reports.**
- SQLite is embedded, zero-ops, one file on disk (aligns with durable-state-on-disk), and in
  WAL mode serves many concurrent readers alongside the single writer the design already has.
  It is the operational store: ticket state, cell status, leases, metrics, grid.
- **DuckDB attached read-only** is the reporting engine: it queries the SQLite store *and* the
  JSONL ledger directly (SQLite scanner + JSON reader), so analytics — false-pass rate, probe
  cost per cell type, throughput, spend per window — are columnar SQL with no ETL.
- Live UI feeds need no DB change-feed: the single-writer server sees every change and pushes
  it over SSE/WebSocket directly.

**Fleet scope (later, resolves the multi-instance decision): PostgreSQL.**
- Concurrent writers across instances; JSONB for flexible fields; `LISTEN/NOTIFY` for
  cross-process change feeds; mature analytics; `pgvector` *only if* semantic retrieval over
  patterns/corpus is added for the context-engineering retrieval strategy.

**Two shiny options to resist.**
- A **graph database** for dependency/staleness: unwarranted at instance scope. The cell graph
  is small, staleness propagation is already a deterministic script over hashes, and recursive
  CTEs answer readiness queries. Reconsider only at fleet scale.
- A **vector database**: only if the retrieval methodology needs semantic search. Not mandated;
  `pgvector` as a sidecar covers it when it does.

## Reporting & CRUD

- **Reports** are SQL/DuckDB over the operational store and the ledger — derived views, never
  a second source of truth. Flow metrics, trust-trajectory inputs (false-pass, reward-hack
  counts), and compass probe-cost all read from here.
- **CRUD** is the server API (the coordination spec's `/api/*`). Every mutation is
  server-mediated, gate-checked, and ledgered; a UI drag is a transition *request*, not a
  direct write.
- **Agent access to the DB is read-only**, exposed through an **MCP query tool**. Agents may
  *read* status to inform judgment; they never *write* operational state — mutation routes
  through the gated single-writer server, exactly as workers never write their own signals.

## Write-Path Invariants

1. Operational-state writes happen in exactly one process (the server). No agent, worker, or
   UI writes the database directly.
2. Every operational write is preceded by a ledger append; the database is never ahead of the
   ledger.
3. Artifact-body writes happen on the filesystem, through a worker, under active hooks; the
   database row referencing the artifact is updated by the server after the gated write
   succeeds.
4. The operational store is reconstructible from ledger + filesystem at any time; losing it is
   a rebuild, not a loss.

## Harness & Storage Failure Modes

Database as source of truth (forfeits git-nativity, diffability, ledger replay; the model
cannot reason over opaque rows as it can over JSON). Artifact bodies in the database (loses
review and gating of the rewritable substrate). Operational store ahead of the ledger
(unreplayable; provenance gaps). Multi-writer operational state (reintroduces the race the
single-writer server eliminates). Gates in prose instead of hooks (advisory under pressure).
Graph/vector databases adopted before instance scope needs them (over-engineering the
substrate past the least fixpoint).
