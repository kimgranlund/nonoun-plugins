---
description: Initialize a dev-factory instance under .agents/dev-factory/ — scaffold the nine layer dirs + signals/ + ledger/ + the canonical lattice.json + the coordination dirs, stamped with this instance's producer + kernel version. The one deterministic action a human types; cell-seeding then routes to the lattice-management skill.
argument-hint: "[project name + the domain to decompose]"
---

Initialize the dark factory's instance. **$ARGUMENTS**

This is the one deterministic setup action — it routes to the kernel's `lattice.py`, then hands off to the **`lattice-management`** skill for the judgment (decomposing the domain into typed cells). Run, in order:

1. **Scaffold + seed the lattice** (the nine layer dirs mirroring the layer enum byte-for-byte, `signals/`, `ledger/`, the typed naming schema, and the canonical `lattice.json`):

   ```bash
   LATTICE_PRODUCED_BY=dev-factory python3 "${CLAUDE_PLUGIN_ROOT}/bin/lattice.py" init <project> --dir .agents/dev-factory
   ```

   `LATTICE_PRODUCED_BY=dev-factory` stamps the instance's producer correctly (not the vendored kernel's `harness-forge` default), and `save()` stamps the writing `kernel_version` — together the migration anchor `kernel_compat()` reads back on boot. It refuses to clobber an existing `lattice.json` (pass `--force` to reseed).

2. **Lay the coordination corpus dirs** the ticket lifecycle writes into (the vendored init scaffolds the substrate plane; these are the coordination plane):

   ```bash
   mkdir -p .agents/dev-factory/coordination/{tickets,roadmap,issues}
   ```

3. **Decompose the domain into cells** — invoke the **`lattice-management`** skill (*"design the lattice for this instance — decompose this domain into layers and scopes"*). Seed cells at **honest** maturity (`absent`/`defined` — never a green grid the factory has not earned), placing dependency edges that respect the partial order. Per the trajectory rule, seed one thin vertical slice first, then `scan`/`rank` the frontier — do not breadth-fill.

To then run the bounded autonomous loop + the live UI, start the separate **dev-server** (`../../dev-server/RUNBOOK.md`): the kernel is the substrate; the server is what runs it.
