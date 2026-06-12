---
date: 2026-06-12
status: draft
version: "0.2.0"
---

# Operating Procedure — the loop, bound to the commands

The seven-step loop from `agentic-systems-foundations/lattice-model.md`, wired to the kernel's `bin/` and commands. Every step that is computation is a script; every step that is judgment is the model's. The boundary is the point.

```
                ┌──────────────── /harness-scan ────────────────┐
                │  lattice.py scan  → the open/stale gap set     │  (detect; do not rank)
                ▼                                                │
   /harness-next                                                 │
   lattice.py rank → ready cells by (risk × unlock) ÷ probe-cost │  (select; partial-order filtered)
                │                                                │
                ▼                                                │
   /harness-advance                                              │
   lattice.py validity <cell>  → CAN ADVANCE / BLOCKED          │  (gate the move)
   dispatch harness-advancer (one cell, fresh context):            │
     define → create → validate                                 │
     validation path writes signals/{cell}/…  (NOT the worker)  │  ← gate-signal protects it (wired: wire.py check = 0)
     ledger.py append  (result + WHY + cost)                    │
                │                                                │
                ▼                                                │
   on signal → mark validated → RESCAN ───────────────────────►─┘  (validation reveals new gaps)
   on budget/no-progress → flip blocked → back to /harness-next
                │
                ▼  (only when the slice's load-bearing cells carry signal)
   widen scope → rescan ALL modalities at the new scope
                │
                ▼
   /harness-distill   ledger.py distill/cost/false-pass → harness-distiller → upstream proposals
```

## The steps

1. **Seed** (`/harness-seed`) — `lattice.py init` lays `.harness/` + the first thin slice (an ontology + spec + rubric + ledger task slice). The ledger schema sits in the first slice; provenance cannot be retrofitted. The seed's final step **offers to wire the blocking gates** into the project's own loop (`wire.py plan` → user consent → `apply` → `check`): the PreToolUse `gate-signal` deny, the `emit-ledger` audit trail, the `propagate-staleness` cascade. Wire before the first unattended pass — `wire.py check` exit 0 is the precondition for claiming the protection is mechanical.
2. **Scan** (`/harness-scan`) — `lattice.py scan` sweeps the modality axis at the frontier scope. A missing whole layer outranks a missing slug.
3. **Rank** (`/harness-next`) — `lattice.py rank` dependency-filters and orders. Probe cost from the ledger once history exists.
4. **Advance** (`/harness-advance`) — gate with `lattice.py validity`, then the `harness-advancer` runs the engine; the validation path writes the signal; `ledger.py append` records the why.
5. **Rescan on signal** — validation reveals new gaps; do not pre-plan the whole grid.
6. **Widen** — only from validated footholds; rescan all modalities at the new scope.
7. **Distill** (`/harness-distill`) — route the ledger back into selection (probe cost), trust (false-pass), and regeneration (patterns).

## The three things the kernel does that a model must not

- **Selection / ranking** — `lattice.py rank`, not "which feels most important."
- **Readiness / partial order** — `lattice.py validity`, not "this seems ready."
- **Staleness propagation** — `lattice.py stale`, not "I think these are affected."

A model-predicted computation is a hallucination surface. The model defines the spec, writes the asset, and calibrates the rubric — the bookkeeping between cells is the kernel's, deterministic and auditable.

## Autonomy, earned

Run **attended** until the verifier has a track record; advance tiers only on the measured precondition (`ledger.py false-pass` < ~5%, zero reward-hacking). Unattended runs need a hermetic sandbox, protected verifier assets, all caps active, and a separate done-judge — see `agentic-systems-foundations/autonomous-long-running-systems.md` and `layer-policy.md`. The loop amplifies operator skill; it does not substitute for it. If you cannot explain the merged work, drop back to attended mode.
