# dev-kernel

The invariant kernel of **dev-factory** — the typed contracts and deterministic computation a "dark factory" agentic system runs on. dev-kernel is the **substrate**; the running system is the separate **dev-server** app.

## What it ships

| Primitive | What |
|---|---|
| **Schemas** (11) | cell · ticket · ledger-entry · activity · dispatch-policy/execution-plan · budget · lattice · roadmap · kit · adapter · naming |
| **The kernel** (`bin/`) | the **vendored** harness-forge lattice/validation kernel (drift-gated) + native lifecycle · compass · execplan · autonomy · distill · the tamper-evident hash-chained ledger |
| **Gates** | 4 protective scripts (`gate-signal` · `gate-verifier` · `gate-ledger` · `gate-naming`) + 2 lifecycle transition predicates (`gate-ticket-ready` · `gate-dispatch`) + `check-kit-conform` |
| **MCP** | read-only `factory-query` — 8 tools over the lattice / index / ledger |
| **Roster + skills** | a 12-agent dispatcher roster (`agents/`) across 8 compound skills (`skills/`) |

## The thesis

Ticket `done` ⟺ the target cell advances through the **same** `gate-signal` — the coordination board cannot disagree with the knowledge lattice. Workers are mechanically denied writes to `signals/`, the ledger, `rubric/`, and `lattice.json`. Computation routes to code; the model's judgment lives *inside* a cell.

## Scope — substrate, not the running system

**dev-kernel installed alone provides the contracts, the selftested kernel scripts, and the read perimeter — it does not run the factory.** The protective gates BLOCK only once consent-wired into a worker loop; the autonomous loop, the live operational state (the SQLite index the MCP reads), and the trust-tier enforcement are the separate **dev-server** app's. The dark factory runs when dev-server drives this kernel against an instance under `.agents/dev-factory/`.

## Getting started — step by step

```bash
# 1. Enable dev-kernel + a kit for your project (project-local), via .claude/settings.json or /plugin.
# 2. Initialize the instance (scaffold the lattice + the layer/coordination dirs):
python3 bin/lattice.py init --dir .agents/dev-factory
# 3. The 8 compound skills are now model-invoked — drive the factory in natural language (below).
# 4. To run the autonomous loop + UI, start the separate dev-server (see ../dev-server/README.md):
#      DEV_FACTORY_DIR=$PWD/.agents/dev-factory DEV_FACTORY_KIT=../dev-kit-corpus \
#        DEV_FACTORY_HEARTBEAT=1 uvicorn dev-server.app:app
```

## Sample prompts

With `dev-kernel` installed, the skills trigger on natural language (no slash commands):

- *"seed a dev-factory lattice for this project"* · *"decompose this domain into layers and scopes"* — **lattice-management**
- *"what cell should we advance next?"* · *"rank the frontier"* · *"why is this cell stale?"* — the compass
- *"create a ticket to validate the auth spec"* · *"triage this issue"* · *"decompose this epic"* — **ticket-orchestration**
- *"advance the spec.system.auth cell"* · *"validate this artifact against its rubric"* — **cell-engine**
- *"author and calibrate a rubric for the spec layer"* — **verification**
- *"distill patterns from the ledger"* · *"propose a spec revision from what we've learned"* — **regeneration**
- *"has this family earned autonomy — what tier?"* — **autonomy-governance**

## Verify

```bash
for b in bin/*.py; do python3 "$b" selftest; done    # every kernel script selftests
python3 bin/ledger.py verify --dir <instance>         # the tamper-evident audit chain (stand-alone signal)
python3 evals/tracer-bullet/replay.py                 # the morphism, in isolation
python3 bin/check-kit-conform.py kit ../dev-kit-corpus # the kernel/kit boundary
```

The system-level proofs (Crawl · Walk · Run · Fly · demotion · integration · server-smoke) live with the runtime in `../dev-server/evals/`. The design of record is `../docs/specs/dev-factory-spec/`.
