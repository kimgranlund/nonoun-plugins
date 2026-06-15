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
| **dev-kernel** | a plugin (invariant machinery) | the 11 schemas, the two state machines, the 4 protective gates + 2 lifecycle predicates, the compass, the **execution-plan assembly** (`dispatch-policy → plan`), the validation path, **autonomy** (trust tiers + mechanical demotion) + **distillation**, the **tamper-evident hash-chained ledger**, a read-only **MCP query perimeter** (`factory-query`), and the 12-agent roster across 8 compound skills |
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

## Getting started — step by step

Install into your project (**project-local**, the catalog default), then init an instance and start the loop.

```bash
# 1. Enable the plugins for THIS project (in <project>/.claude/settings.json), or interactively
#    with /plugin marketplace add … then choosing PROJECT scope:
#      "extraKnownMarketplaces": { "dev-factory": { "source": { "source": "github", "repo": "<owner>/dev-factory" } } },
#      "enabledPlugins": { "dev-kernel@dev-factory": true, "dev-kit-corpus@dev-factory": true }
#    (until published, point the marketplace source at this repo / a local path.)

# 2. Initialize the instance — scaffold the lattice + coordination dirs under .agents/dev-factory/:
cd your-project
python3 <plugin-root>/dev-kernel/bin/lattice.py init --dir .agents/dev-factory
#    …or just ask Claude:  "seed a dev-factory lattice for this project"

# 3. Seed the lattice with your project's cells (or let the architect decompose it):
#    "design the lattice for this instance — decompose this domain into layers and scopes"

# 4. Create your first unit of work — by prompt, the API, or the UI:
#    "create a ticket to validate the auth spec"

# 5. Run the factory (the bounded autonomous loop + the live UI), with a kit bound:
pip install fastapi uvicorn
DEV_FACTORY_DIR=$PWD/.agents/dev-factory DEV_FACTORY_KIT=<plugin-root>/dev-kit-corpus \
  DEV_FACTORY_HEARTBEAT=1 uvicorn dev-server.app:app --port 8731
#    open http://127.0.0.1:8731/  →  Kanban (2 lenses) · lattice grid · ledger · agent monitor · roadmap

# 6. Steer: drag a ticket on the board (each drag is a gate-checked request, refused with a reason if
#    illegal), or ask  "what's the frontier — what should we advance next?"
```

No server needed to try it: **`python3 dev-server/demo.py`** drives the whole loop end-to-end against a throwaway instance and prints what happened.

## Sample prompts

dev-factory's skills are **model-invoked** (there are no slash commands) — so with `dev-kernel` installed, you drive it in natural language. What to say:

| Say… | Triggers |
|---|---|
| *"seed a dev-factory lattice for this project"* · *"decompose this domain into layers and scopes"* | **lattice-management** → lattice-architect |
| *"scan for lattice gaps"* · *"what cell should we advance next?"* · *"rank the frontier"* · *"why is this cell stale?"* | the compass |
| *"create a ticket to validate the auth spec"* · *"triage this issue into a ticket"* · *"decompose this epic into tickets"* · *"plan the roadmap"* | **ticket-orchestration** → ticket-triager / roadmap-planner |
| *"advance the spec.system.auth cell"* · *"validate this artifact against its rubric"* · *"why didn't this cell advance?"* | **cell-engine** → cell-advancer + cell-validator |
| *"author and calibrate a rubric for the spec layer"* | **verification** → rubric-architect |
| *"distill patterns from the ledger"* · *"propose a spec revision from what we've learned"* | **regeneration** → pattern-distiller / spec-regenerator |
| *"what tier is this family at — has autonomy been earned?"* · *"demote this family"* | **autonomy-governance** |
| *"how do I run the server / arm the heartbeat?"* · *"show the crash-recovery runbook"* · *"author a kit for a new family"* | **factory-ops** · **kit-authoring** |

The factory's *own* roster agents (cell-advancer, spec-architect, …) are dispatched by dev-server's loop, not invoked directly.

## Run it (verify / develop)

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
