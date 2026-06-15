# nonoun Factory — Build Plan

**Status:** plan (the design `TDD-01-nonoun-factory` is a `defined`, unvalidated cell). **Companion to:** `docs/specs/nonoun-factory-spec/` (the design + 5 schemas + the `spec-author` skill scaffold). **This document is:** the build sequence, the load-bearing decisions, what to reuse, and the risks — not a restatement of the spec.

---

## 0 · The one decision that shapes everything: build ON harness-forge

The spec describes `nonoun-kernel` as if from scratch. It is not from scratch — **the lattice machine it specifies already ships, proven and CI-gated, as `harness-forge`** (the catalog's lattice kernel, hardened end-to-end through ROADMAP Track 5). The single highest-leverage call in this whole build: `nonoun-kernel` **extends harness-forge**, it does not re-implement it. Re-deriving the maturity machine, the engine, the compass, the gates, and staleness-as-graph would be the grid-filling anti-pattern (§17) applied to our own foundation.

| nonoun-kernel needs (TDD) | harness-forge already ships | the gap to build |
|---|---|---|
| Lattice + 8-state maturity machine + staleness-as-graph | `bin/lattice.py` (scan · rank · validity · advance · check · scaffold · block) | **reuse as-is** |
| Cell / lattice / signal / ledger schemas | `schemas/{cell,lattice,signal,run-budget,loop-active}.schema.json` | reuse; **add** `ticket`, `activity`, `dispatch-policy` (already drafted in `specs/.../schemas/`) |
| The engine (`define→create→validate`; signal minted from a verifier's **exit status**) | `bin/validate.py` (the validation path) | **reuse** |
| The compass (`rank` by `(risk × unlock) ÷ probe-cost`, dependency-gated) | `lattice.py` scan/rank | reuse; **add** the ticket-readiness filter (`deps_validated ∧ budget ∧ tier`) |
| The immutable/rewritable boundary, mechanical | `bin/gate-signal` (deny worker writes to verifier assets) + `wire.py` (consent-install) | reuse; **add** `gate-ticket-ready`, `gate-dispatch` |
| The global budget bound, enforced in code | `bin/run-budget.py` + `gate-budget` + `evals/global-bound/` | **reuse** — the server's heartbeat replaces the `/harness-run` orchestrator, the budget gates stay |
| Append-only provenance ledger | `bin/ledger.py` | reuse; **add** the coordination + activity-lifecycle events |
| Typed naming grammar (`gate-naming`) | `bin/naming.py` + `schemas/naming.schema.json` | reuse with `ns = nonoun` |
| The structural-critic council pattern | `agents/critic-*` + `harness-council` + `bin/council-precheck.py` | reuse the pattern for the new rubric cells |
| Host-aware install | `wire.py` + the vendored `host_detect.py` (Track 5 increment 5) | **reuse** |

**Consequence:** the build is *not* "implement the lattice machine." It is "**add the coordination layer, the server, and the kit tiering on top of a battle-tested lattice kernel.**" That reframing collapses the riskiest ~two-thirds of the spec into reuse.

---

## 1 · What's genuinely new (the actual build surface)

1. **The coordination corpus** — tickets (`feature/task/bug/chore/spike/epic/issue`), the **ticket lifecycle machine** (`draft→active→claimed→in-progress→in-review→done` + `blocked/paused/cancelled`), and **the typed link** (`ticket → {target_cell, target_transition}`; `done ⟹ cell advances`, the *same* `gate-signal`). This is the spec's central reconciliation (§4) and it is genuinely new — harness-forge has cells, not tickets.
2. **The Python server** — the bulk of the new code, and a **new competency for the catalog** (which is stdlib bins + MCPs, zero servers): FastAPI/uvicorn + an APScheduler 30s heartbeat + a SQLite operational store (+ DuckDB read-only for reports) materialized from the ledger + SSE/WebSocket + a web UI (Kanban · lattice grid · ledger feed · agent monitor · roadmap). **Single-writer discipline** is the spine (the server is the sole writer of operational state; agents read via an MCP query tool, never write).
3. **The `DispatchAdapter`** (OD-003) — the seam from the server to a **headless agent runtime** (Claude Agent SDK / headless Claude Code) that actually runs a worker in a hermetic worktree under active gates. The riskiest external dependency; its concrete binding must be pinned against current product docs at build time, not guessed.
4. **The kernel / kit / instance / server tiering** — harness-forge is single-tier; the factory is a three-tier substrate + a runtime. The new contracts: `kit.schema.json`, `adapter.schema.json`, and the `kit-conform` gate (the boundary's falsification test: adding `nonoun-kit-app` must require **zero kernel edits**).
5. **The autonomy trust-trajectory** — harness-forge ships the *bounded* loop + `gate-budget`; the factory adds the **tier ladder** (0 Attended → 3 Scheduled/lights-out) with **mechanical, ledger-measured demotion** (a false-pass spike or reward-hack incident drops the family a tier with no human in the demotion path).
6. **The agent roster + the 8 compound skills** — harness-forge has a subset (`harness-builder/advancer/auditor/distiller`); the factory adds architects (`lattice/spec/rubric/kit`), orchestrators (`roadmap-planner/ticket-triager/dependency-arbiter`), and the rest, packaged as **compound skills** (folders carrying their own `agents/ rubric/ policy/ methodologies/ scripts/`). `spec-author` is already scaffolded.

---

## 2 · Layout (where the pieces live)

- **`nonoun-kernel/`** — a plugin: the new schemas (`ticket`, `activity`, `dispatch-policy`, `kit`, `adapter`), the ticket lifecycle machine + `gate-ticket-ready`/`gate-dispatch`, the `DispatchAdapter` contract, the base roster + the 8 compound skills. **Depends on harness-forge** for the lattice kernel (vendored or marketplace-installed — decide in §5). Must pass plugins-factory's gate suite (validate · integration-contract · trust-boundary · context-cost · the J `stateNamespace` = `.agents/factory`).
- **`nonoun-kit-corpus/`, `nonoun-kit-app/`** — kit plugins: family ontology, rubric manifests, harness adapters, seed patterns. `kit-app` exists only to prove the kernel/kit boundary (Fly milestone).
- **`nonoun-server/`** — **not a plugin** — a Python app (the runtime). Lives beside the plugins; consumes an instance as single-writer + a `DispatchAdapter`.
- **Instance repo** — a user project: `lattice.json · coordination/ · spec/ rubric/ … · signals/ · ledger/` + `.factory/index.db` (derived). The only stateful tier.
- **Marketplace home** (decide §5): the kernel + kits are plugins → either a dedicated `nonoun-factory` marketplace or entries in `nonoun-plugins`. The server is distributed separately (pip/uvx), not via the plugin marketplace.

---

## 3 · Build sequence — the substrate-engineering arc (each phase earns the next; skipping ahead is the canonical failure)

### Crawl — Instrumentation (the walking-skeleton). **No UI beyond a list. No second kit. No auto-dispatch.**
- **Reuse:** harness-forge's `lattice.py`, `validate.py`, `gate-signal`, `gate-budget`, `ledger.py`, `naming.py` wholesale.
- **Build:** `ticket.schema.json` + the ticket lifecycle machine (a `bin/` script, deterministic) + `gate-ticket-ready` + `gate-dispatch`. The **server skeleton** — FastAPI + the SQLite store materialized from the ledger + the `/api/tickets`, `/api/lattice`, `/api/ledger` endpoints + the `POST /transition` gate path — **with the heartbeat DISABLED**. The `cell-advancer` + `cell-validator` agent pair (the generator/critic split).
- **Milestone (the falsifiable one):** *one* corpus-family cell driven **`absent → validated` by hand through the API** — every gate firing, the ticket's `done` and the cell's maturity advancing through the **same** `gate-signal`, a real signal artifact on disk written by the critic (not the worker), the whole transition in the ledger. This proves the typed link (§4) end-to-end before any automation.

### Walk — Delegation.
- **Build:** enable the heartbeat at **Tier 1** (the server dispatches; a human reviews at `in-review`). The Kanban + lattice-grid UI + the live SSE stream (the two lenses — ticket + agent/activity). Bind budgets + no-progress (reuse `gate-budget` + harness-forge's `no-progress` detector). The `DispatchAdapter` concrete binding (OD-003) lands here.
- **Milestone:** a full vertical slice reaches `done` **unattended within budget**, false-pass under threshold, **zero reward-hack incidents** — the precondition the trust ladder reads to permit Tier 2.

### Run — Regeneration.
- **Build:** `pattern-distiller` + `spec-regenerator` (extend harness-forge's distill concept); the outer loop proposes upstream revisions (PRs against `spec/`/`rubric/`, merge policy-gated). Promote the corpus family toward Tier 2.
- **Milestone:** a **ledger-driven revision to a spec/rubric cell lands** through a deliberate transition, and the next run is **measurably better** (substrate sharpens, not just accretes — Failure 1, designed out).

### Fly — Dark Factory.
- **Build:** Tier 3 lights-out at fleet scope; ship **`nonoun-kit-app`** — adding it must require **zero kernel edits** (the boundary's falsification test). Hermetic sandbox + tamper-evident audit trail for unattended operation.
- **Milestone:** the factory **improves its own definitional knowledge across a window**, substrate-accretion as the watched metric, reward-hack incidents held at zero.

---

## 4 · The hard parts (where this is genuinely difficult, ranked)

1. **The server is a new class of artifact for the catalog.** Everything shipped to date is stdlib-only bins + MCP subprocesses. The server is a stateful async web app (FastAPI · APScheduler · SQLite/DuckDB · SSE · a JS UI) that supervises subprocesses and holds leases. This is the largest single chunk of new engineering, and it sits *outside* the plugin-primitive model — plan it as its own component with its own tests, not as plugin `bin/`.
2. **The `DispatchAdapter` to a headless runtime (OD-003).** The factory's whole leverage is the server launching agent workers unattended. The binding to the Claude Agent SDK / headless Claude Code (flags, session handling, streaming tool events into the ledger, enforcing the gate boundary inside the worktree) is the integration risk. **Verify against current product docs before Walk** — do not hard-code a guessed interface.
3. **Grid-filling the meta-system (§17, the anti-pattern most likely to bite *us*).** The temptation is to build the Kanban UI, the kits, and the dashboards first. The spec is explicit: building dashboards/kits before one cell reaches `validated` is grid-filling the factory itself. **The Crawl milestone is one cell, by hand, no UI — earn the rest.**
4. **Unattended safety must be mechanical, not aspirational.** The immutable/rewritable boundary (workers deny-on-write to verifier assets/`signals`/`ledger`/hooks/schemas), the trust ladder, and mechanical demotion are the difference between leverage and a reward-hack shipping overnight. Reuse harness-forge's proven `gate-signal`/`gate-budget` as the foundation; the tier ladder + ledger-measured demotion is the new safety code and must be gated, not prose.

---

## 5 · Decisions to resolve before Crawl

- **D-A · harness-forge reuse boundary.** *Recommend:* `nonoun-kernel` declares harness-forge a dependency (the kernel's lattice/engine/compass/gates ARE harness-forge's bins, vendored via a sync-gate like the corpus-reader / host-detect pattern, since the self-contained rule forbids a cross-plugin import). Re-implementing them is rejected as grid-filling.
- **D-B · marketplace home.** *Recommend:* a dedicated `nonoun-factory` marketplace for the kernel + kits (the catalog `nonoun-plugins` stays the *tool* catalog; the factory is a *system*). The server ships separately (uvx/pip).
- **OD-003 · the DispatchAdapter binding** — must be pinned against current Claude Agent SDK docs. **Resolve at the start of Walk** (Crawl runs cells by hand through the API, so it doesn't need the adapter yet).
- **OD-005 · fleet scope** — start **instance-scope** (one server per instance, SQLite). Postgres/fleet is a later horizon; don't build it before the boundary needs it (§harness-and-storage failure modes).
- **OD-002 · cold-start risk estimation** — start with kit priors + triage judgment; the compass goes empirical the moment the ledger has data. Not blocking for Crawl.
- **OD-001, OD-004, OD-006** — OD-001 is decided (files-of-record + single-writer); OD-004 (cross-cell re-validation ordering) and OD-006 (regenerator merge granularity) are Run/Fly concerns, not Crawl blockers.

---

## 6 · The immediate first slice (what to build first)

Smaller than the whole Crawl phase — the tracer bullet that de-risks everything:

1. **Add `ticket.schema.json` + a deterministic ticket-lifecycle `bin/` script** to a `nonoun-kernel` scaffold that vendors harness-forge's `lattice.py` + `gate-signal` + `validate.py` (D-A). Prove `gate-ticket-ready` and the `done ⟹ cell-advances-through-gate-signal` link with a `selftest` — no server, no API yet.
2. **Then** the minimal FastAPI skeleton (heartbeat OFF) exposing `POST /api/tickets/{id}/transition` that applies the gate and, on `in-review → done`, drives the cell's maturity via the reused `validate.py` path.
3. **Hit the Crawl milestone by hand:** one cell `absent → validated`, every gate firing, a real critic-written signal on disk, the whole thing in the ledger.

That single vertical slice validates the central reconciliation (§4) — the typed morphism between the Kanban and the lattice — which is the thesis the entire system rests on. Everything else (UI, kits, the heartbeat, regeneration, fleet) is earned from there.
