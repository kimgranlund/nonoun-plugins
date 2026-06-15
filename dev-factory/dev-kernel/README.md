# dev-kernel

The invariant kernel of **dev-factory** — the typed contracts and deterministic computation a "dark factory" agentic system runs on. dev-kernel is the **substrate**; the running system is the separate **dev-server** app.

## What it ships

| Primitive | What |
|---|---|
| **Schemas** (11) | cell · ticket · ledger-entry · activity · dispatch-policy/execution-plan · budget · lattice · roadmap · kit · adapter · naming |
| **The kernel** (`bin/`) | the **vendored** harness-forge lattice/validation kernel (drift-gated) + native lifecycle · compass · execplan · autonomy · distill · the tamper-evident hash-chained ledger |
| **Gates** | 4 protective scripts (`gate-signal` · `gate-verifier` · `gate-ledger` · `gate-naming`) + 2 lifecycle transition predicates (`gate-ticket-ready` · `gate-dispatch`) + `check-kit-conform` |
| **MCP** | read-only `factory-query` — 8 tools over the lattice / index / ledger |
| **Command** | one typed entry point — `/factory-init` (the single deterministic action: scaffold an instance) |
| **Roster + skills** | a 12-agent dispatcher roster (`agents/`) across 7 skills — **6 core lattice** skills + **1 meta** skill (see *Skill layering*) |

## The thesis

Ticket `done` ⟺ the target cell advances through the **same** `gate-signal` — the coordination board cannot disagree with the knowledge lattice. Workers are mechanically denied writes to `signals/`, the ledger, `rubric/`, and `lattice.json`. Computation routes to code; the model's judgment lives *inside* a cell.

## Scope — substrate, not the running system

**dev-kernel installed alone provides the contracts, the selftested kernel scripts, and the read perimeter — it does not run the factory.** The protective gates BLOCK only once consent-wired into a worker loop; the autonomous loop, the live operational state (the SQLite index the MCP reads), and the trust-tier enforcement are the separate **dev-server** app's. The dark factory runs when dev-server drives this kernel against an instance under `.agents/dev-factory/`.

## Skill layering — core vs meta

The **6 core lattice skills** operate the invariant machine over the on-disk grid: `lattice-management` · `ticket-orchestration` · `cell-engine` · `verification` · `regeneration` · `autonomy-governance`. One **meta skill** — `kit-authoring` — extends the *family*: it builds **family kits** (the stateless plugins in `../dev-kit-*`, never the kernel), and the kernel's own `check-kit-conform.py` mechanically enforces that boundary (a kit that needs a kernel edit has leaked). It ships here because the kit-conform contract it authors against *is* a kernel gate.

**Operating the runtime is not a kernel skill.** The dev-server runbook — running the server, arming the bounded heartbeat, tending worktrees, crash recovery, the metrics to watch — lives with the code it drives, at [`../dev-server/RUNBOOK.md`](../dev-server/RUNBOOK.md), the same line already drawn for the system-evals in `../dev-server/evals/`. That operational knowledge documents `heartbeat.py`/`dispatch.py`/`store.py` (dev-server code, not the kernel), so binding it to the kernel would invite silent cross-distribution drift; it belongs where an operator already is, running `uvicorn`.

## Getting started — step by step

```bash
# 1. Enable dev-kernel + a kit for your project (project-local), via .claude/settings.json or /plugin.
# 2. Initialize the instance — just run the command:  /factory-init <project>
#    (or by hand — scaffold the lattice + the layer/coordination dirs:)
LATTICE_PRODUCED_BY=dev-factory python3 bin/lattice.py init --dir .agents/dev-factory
mkdir -p .agents/dev-factory/coordination/{tickets,roadmap,issues}
# 3. The 7 compound skills are now model-invoked — drive the factory in natural language (below).
# 4. To run the autonomous loop + UI, start the separate dev-server (see ../dev-server/README.md):
#      DEV_FACTORY_DIR=$PWD/.agents/dev-factory DEV_FACTORY_KIT=../dev-kit-corpus \
#        DEV_FACTORY_HEARTBEAT=1 uvicorn dev-server.app:app
```

## Sample prompts

There is one typed command — **`/factory-init`** (the single deterministic action: scaffold an instance under `.agents/dev-factory/`). Everything else is **model-invoked** — the skills trigger on natural language:

- *"seed a dev-factory lattice for this project"* · *"decompose this domain into layers and scopes"* — **lattice-management**
- *"what cell should we advance next?"* · *"rank the frontier"* · *"why is this cell stale?"* — the compass
- *"create a ticket to validate the auth spec"* · *"triage this issue"* · *"decompose this epic"* — **ticket-orchestration**
- *"advance the spec.system.auth cell"* · *"validate this artifact against its rubric"* — **cell-engine**
- *"author and calibrate a rubric for the spec layer"* — **verification**
- *"distill patterns from the ledger"* · *"propose a spec revision from what we've learned"* — **regeneration**
- *"has this family earned autonomy — what tier?"* — **autonomy-governance**
- *"author a kit"* · *"add a new family to dev-factory"* · *"write a validation adapter"* — **kit-authoring** (meta)

> Operating the running factory (start the server, arm the loop, a worker is stuck, the index is corrupted) is the runtime's job — see [`../dev-server/RUNBOOK.md`](../dev-server/RUNBOOK.md), not a kernel skill.

## Verify

```bash
for b in bin/*.py; do python3 "$b" selftest; done    # every kernel script selftests
python3 bin/ledger.py verify --dir <instance>         # the tamper-evident audit chain (stand-alone signal)
python3 evals/tracer-bullet/replay.py                 # the morphism, in isolation
python3 bin/check-kit-conform.py kit ../dev-kit-corpus # the kernel/kit boundary
```

The system-level proofs (Crawl · Walk · Run · Fly · demotion · integration · server-smoke) live with the runtime in `../dev-server/evals/`. The design of record is `../docs/specs/dev-factory-spec/`.
