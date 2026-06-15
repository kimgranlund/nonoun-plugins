# dev-factory

A self-hosting **"dark factory" for software engineering**: a kernel that advances a typed knowledge **lattice** by running a bounded, autonomous outer loop over a coordination corpus of work **tickets** — selecting what to advance, dispatching a worker against one cell, letting a separate critic validate it, and improving its own definitions from the ledger — all under **earned, measured, mechanically-revocable autonomy**, while a human governs only the boundary of what it may rewrite.

It models building an agentic system as **best-first search over a knowledge lattice**, and it is built on `harness-forge`'s proven lattice kernel — vendored byte-identical and drift-gated (decision D-A), so harness-forge stays untouched and dev-factory adds the coordination layer, the server, the kits, and the trust trajectory on top.

## The central reconciliation (the thesis)

Two lifecycles, one link. A **ticket** is coordination work (`draft → active → claimed → in-progress → in-review → done`); a **cell** is a knowledge asset with a maturity (`absent → defined → instantiated → validated → …`). Every ticket declares a target cell + a target maturity transition, and:

> **ticket `done` ⟺ the target cell advanced — through the *same* `gate-signal`.**

The Kanban board cannot disagree with the lattice grid, by construction. A worker can author and revise, but **cannot forge the signal** that declares its own work validated (`gate-signal` denies it; the validation path mints it from a verifier's exit status). That property is proven, in code, with no server: `dev-kernel/evals/tracer-bullet/`.

## Architecture — kernel / kit / instance / server

| Tier | Is | Holds |
|---|---|---|
| **dev-kernel** | a plugin (invariant machinery) | the 11 schemas, the two state machines, the 6 gates, the compass, the **execution-plan assembly** (`dispatch-policy → plan`), the validation path, **autonomy** (trust tiers + mechanical demotion) + **distillation**, the **tamper-evident hash-chained ledger**, a read-only **MCP query perimeter** (`factory-query`), and the 12-agent roster across 8 compound skills |
| **dev-kit-corpus · dev-kit-app** | plugins (family bindings) | ontology · rubric manifest · **real validation harness verifiers** (spec-quality / pattern / test-suite — not a file-exists check) · dispatch policy · seed patterns. `check-kit-conform` enforces **zero kernel edits** |
| **Instance** | a user project's `.agents/dev-factory/` | the only stateful tier: `lattice.json · coordination/ · the layer dirs · signals/ · ledger/ · index.db` |
| **dev-server** | a Python app (NOT a plugin) | the bounded 30s heartbeat, the dispatcher + DispatchAdapter (mock + headless), the SQLite read-index, the **reporting layer** (DuckDB/stdlib), the REST API, the SSE stream, the **web UI** (Kanban two-lens · lattice grid · ledger · agent monitor · roadmap) |

The one law (inherited): **computation routes to code, never to inference.** Selection, ranking, readiness, staleness, the ledger, validation are scripts; the model supplies the judgment *inside* a cell. Every `bin/` ships a `selftest`.

## The bootstrapping arc — each phase earns the next

| Phase | Proof | What it shows |
|---|---|---|
| **Crawl** | `dev-server/evals/crawl-milestone/` | one cell driven `absent → validated` by hand through the API; every gate firing; a critic-written signal on disk |
| **Walk** | `dev-server/evals/walk-milestone/` | the heartbeat drives a dependency-ordered slice to `done` **unattended**, in readiness order, **bounded** (halts rather than burns), reward-hack-proof |
| **Run** | `dev-server/evals/run-milestone/` | the ledger's failure signature distills (with provenance) into an upstream proposal; a spec is revised through a deliberate `validated → regenerating → validated` transition — the substrate **sharpens** |
| **Fly** | `dev-server/evals/fly-milestone/` | two families bind one **unchanged** kernel (the boundary's falsification test); Tier 3 lights-out is reachable only when earned, and revocable by a single incident |

Plus three cross-cutting proofs: `dev-server/evals/demotion/` (mechanical demotion has *teeth* — a caught false-pass revokes autonomy with no human in the path), `dev-server/evals/integration-milestone/` (the kit actually *drives* the loop — the dispatch policy is consumed, the roster staffs it, the family's real rubric gates it), and `dev-server/evals/server-smoke/` (the live FastAPI app serves the UI + every endpoint over a real client). The kernel's `dev-kernel/evals/tracer-bullet/` proves the morphism in isolation. **Eight falsifiable replays in all** — and `dev-server/demo.py` runs the whole integrated system live for a human to watch.

## Run it

```bash
# the whole system, headless (stdlib + sqlite3 only — no FastAPI, no live model):
for b in dev-kernel/bin/*.py; do python3 "$b" selftest; done
for r in dev-kernel/evals/*/replay.py dev-server/evals/*/replay.py; do python3 "$r"; done

# WATCH it run end-to-end — kit-bound heartbeat advances a lattice unattended + lens + reports + MCP:
python3 dev-server/demo.py

# the live server (heartbeat ON at the EARNED tier, the corpus family bound):
pip install fastapi uvicorn
DEV_FACTORY_DIR=/path/to/project/.agents/dev-factory DEV_FACTORY_KIT=$PWD/dev-kit-corpus \
  DEV_FACTORY_HEARTBEAT=1 uvicorn dev-server.app:app --port 8731     # the web UI at http://127.0.0.1:8731/

# kit conformance (the boundary) + the read-only MCP perimeter:
python3 dev-kernel/bin/check-kit-conform.py kit dev-kit-corpus
DEV_FACTORY_DIR=… python3 dev-kernel/bin/factory-query-mcp.py   # JSON-RPC over stdio
```

The design of record is `docs/specs/dev-factory-spec/TDD-01-nonoun-factory.md`; the build narrative is `docs/PLAN.md`.
