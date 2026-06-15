# lattice-kernel — the pointer to the vendored kernel (do NOT re-implement)

`lattice-management` carries no lattice code of its own. The grid operations — scan, rank, validity, staleness, block/unblock, init — are the **vendored** `lattice.py` at `${CLAUDE_PLUGIN_ROOT}/bin/lattice.py`: byte-identical from `harness-forge/bin/lattice.py`, selftested, CI-gated, kept in sync by `tools/sync-dev-kernel.py` (see `bin/VENDOR.md`). Per build-plan decision D-A, dev-factory does **not** fork the lattice machine. This file is the invocation contract; it deliberately contains **no Python**, because re-implementing scan/rank/staleness here would be a second copy that drifts — the exact failure the routing law forbids.

`DIR` is the instance state dir under the `.agents/dev-factory/` namespace (the `stateNamespace` in `plugin.json`). The kernel reads/writes `lattice.json` there; every other view is derived.

## The operations this skill exposes

```
# stand up a new instance's grid (the architect drafts cells into it afterward)
python3 ${CLAUDE_PLUGIN_ROOT}/bin/lattice.py init <project> --dir DIR

# scan — the gap set at the frontier scope (detects gaps; does NOT rank)
python3 ${CLAUDE_PLUGIN_ROOT}/bin/lattice.py scan --dir DIR

# rank — order the gaps by (risk × unlock) ÷ probe-cost, subject to dependency readiness
python3 ${CLAUDE_PLUGIN_ROOT}/bin/lattice.py rank --dir DIR

# validity — may this cell advance? exit 0 = yes (deps validated · verifier rubric validated · partial order · not blocked)
python3 ${CLAUDE_PLUGIN_ROOT}/bin/lattice.py validity <cell-id> --dir DIR

# stale — propagate staleness: an upstream content-hash change flips every dependent to `stale`
python3 ${CLAUDE_PLUGIN_ROOT}/bin/lattice.py stale <cell-id> <hash> --dir DIR

# block / unblock — flip the budget/no-progress condition flag (a blocked cell drops out of rank)
python3 ${CLAUDE_PLUGIN_ROOT}/bin/lattice.py block <cell-id> [--reason R] --dir DIR
python3 ${CLAUDE_PLUGIN_ROOT}/bin/lattice.py unblock <cell-id> --dir DIR

# the kernel proves itself
python3 ${CLAUDE_PLUGIN_ROOT}/bin/lattice.py selftest
```

## Invariants the kernel guarantees (so this skill never re-asserts them)

- **scan ≠ rank.** Two functions, never conflated. `scan` returns the open/stale gap set; `rank` orders it. A model reading the grid and "ranking by judgment" is the routing-law violation this split prevents.
- **The partial order is mechanical.** `ready(lat, cell)` requires every `depends_on` upstream to be `validated` and the bound `verifier` rubric to be `validated`; `rank` only ever returns dependency-ready gaps.
- **Staleness is a graph cascade.** `propagate_staleness` flips every cell whose `validated_against` carries the changed upstream hash — transitively, in code.
- **`lattice.json` is canonical; all grid views are derived.** The server's SQLite index and the UI grid are folds over it (and over the ledger), rebuildable and never authoritative.
- **Maturity is identity-free.** A cell ID is `{layer}.{scope}.{slug}`; maturity is a Property, never encoded in the ID — a cell is never renamed when it advances.

If `lattice-management` ever needs a kernel behavior these don't expose, the fix is an **upstream change to harness-forge, re-vendored** — never a local edit here (`bin/VENDOR.md`).
