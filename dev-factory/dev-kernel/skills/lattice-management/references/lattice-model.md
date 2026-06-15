# The Lattice Model — the grid dev-factory advances

`Cell: methodology.system.lattice-model · Status: defined · Register: established lineage (best-first search, partial orders, eval-driven development); the layer×scope×maturity synthesis is house (vendored from harness-forge)`

This is the model `lattice-management` operates against. Read it before any seeding, scanning, ranking, or staleness reasoning. It describes the grid; it does **not** re-implement the kernel that computes over it (that is `scripts/lattice-kernel.md` → `bin/lattice.py`).

## The grid: two axes and a state

A **cell** is one **layer** at one **scope**, carrying one **maturity** state. Identity is `{layer}.{scope}.{slug}`; maturity is a Property of the cell, never part of its name (a cell is never renamed when it advances — that would be a drift generator).

**The nine layers (the modality axis — the *kind* of declarative knowledge):**

| Layer | Carries |
| --- | --- |
| `ontology` | the controlled vocabulary; what terms mean |
| `spec` | what *done* means — commitments, acceptance criteria, non-goals |
| `rubric` | how an artifact is scored — the verifier |
| `policy` | the deontic rules — what is obligatory/forbidden, mechanized as gates |
| `capability` | what an agent/tool can do |
| `methodology` | how the work is done — the playbooks |
| `protocol` | how parts communicate — typed handoffs, the trust boundary between them |
| `ledger` | the provenance schema — what is recorded and how |
| `pattern` | distilled, reusable structure earned from operating evidence |

**The five scopes (the grain axis — the *size* of the unit governed):** `call → task → workflow → system → fleet`, ascending. Probe at the smallest scope that yields decisive signal; widen only from validated footholds.

**The eight maturity states (the state machine):** `absent → defined → instantiated → validated → operating → regenerating`, plus the off-path `stale` and `deprecated`. `blocked` is a separate **condition flag** (budget/no-progress), not a maturity. The kernel's `TRANSITIONS` relation gates every legal move; an engine pass may act on `{absent, defined, instantiated, regenerating, stale}` (the advanceable set).

## Selection is search, not a meeting

"What should we advance next?" is **best-first search over the grid**, computed in three deterministic moves (all `lattice.py`, never inference — TDD §3 routing law, §10.4):

1. **scan** — sweep the modality axis at the frontier scope; return the open/stale **gap set**. Detection only. It does not rank.
2. **rank** — order the gap set by `priority ≈ (risk concentration × unlock value) ÷ probe cost`, subject to **dependency readiness**. `unlock_value` is computed from the dependency graph (how many cells/tickets this one unblocks — pure traversal); `probe_cost` is **measured from the ledger** once history exists, a fixed prior on cold start. The value function goes empirical the moment the ledger has data.
3. **readiness** — the partial order: a cell is rankable only when its `depends_on` upstreams are all `validated` and its bound `verifier` rubric is `validated`.

Scan and rank are two functions the spec is emphatic must **never** be conflated. Conflating them — or letting a model "rank by reading the grid" — is the routing-law violation this skill exists to prevent.

## The partial order (the kernel enforces it)

```
ontology + spec → rubric, policy, capability → methodology, protocol → ledger → (operate) → pattern ──feedback──▶ pattern revises spec
```

A rubric scored before its spec validates is "scoring vibes." `lattice.py validity` refuses to advance a cell whose upstreams or verifier rubric are not yet `validated`. The `lattice-architect` draws edges that respect this order at design time; the kernel enforces it at run time.

## Staleness is a graph computation

Each cell records `validated_against: {upstream-cell-id → content-hash}` — the exact upstream content it was validated against. When an upstream cell's content hash changes, `propagate-staleness` flips **every** dependent (transitively) to `stale`. This is why staleness lives in `lattice.py` and is named in §10.4 as NOT an agent: it is a graph traversal over recorded hashes, not a judgment. A dependent left `validated` while its upstream hash has drifted is a *silent false-validated* — the `lattice-health` rubric's `no-unpropagated-staleness` gate catches exactly this.

## The trajectory rule (the design judgment)

- **Depth-first along one thin vertical slice** to `validated`. Drive the thinnest end-to-end path to a real signal before widening (the tracer-bullet discipline).
- **Widen only from validated footholds** — new layers, larger scope — and **rescan the full modality axis at every widening**, because a new scope can reopen gaps a narrower one hid.
- **Two pathologies frame the rule.** Breadth-first at `defined` (every cell specified, nothing validated) is the **enterprise-architecture pathology** — a beautiful dead grid. Depth-first without rescanning (a working slice missing whole modalities — no rubric, no policy) is the **hacker pathology**. The trajectory threads between them.
- **Honest maturity is non-negotiable.** A cell is `absent` until its asset exists, `defined` until a signal validates it. Seeding a green grid is *grid-filling the meta-system* (TDD §17) — building the appearance of progress the factory has not earned. Signal is the only currency at every scope boundary.

## What is canonical and what is derived

`lattice.json` (under the `.agents/dev-factory/` state namespace) is **canonical**. Every other grid view — the server's SQLite read-index, the UI lattice grid, any status dashboard — is a **fold** over `lattice.json` and the ledger: deletable, rebuildable, never authoritative. The grid cannot disagree with the lattice because the grid *is* the lattice, projected.
