# Tracer bullet — the answer key

`replay.py` is the **falsifiable proof of the central reconciliation** (TDD §4): the one slice that
de-risks the entire dev-factory before any server, UI, or kit exists. It drives a single cell from
`instantiated` to `validated` through a ticket's lifecycle and asserts that the coordination board and
the knowledge lattice **cannot disagree**, because both transitions pass through the same `gate-signal`.

This README is the answer key. It is deliberately **outside** the fixture in `replay.py`, so a cold
judge (or a critic council) can run the replay without reading what it is "supposed" to find.

## What it proves

| Property | Claim | Why it is load-bearing |
|---|---|---|
| **P1** | `done` ⟹ the cell is `validated` and carries a `signal_ref` | Without it, the lattice fills with "validated by assertion" — confident claims that never held (Anti-pattern §17). |
| **P2** | a **failing** verifier neither closes the ticket nor advances the cell | The reward-hack is *designed out*: a clean board a worker produced by failing-then-asserting is structurally impossible. |
| **P3** | the worker is **mechanically unable** to write the signal (`gate-signal` exit 2) | The signal's existence therefore *proves* a critic — not the worker — validated the work (the generator/critic split, made executable). |
| **P4** | `ticket.signal_refs == cell.signal_refs`, and the whole run is in the append-only ledger | The board *is* the lattice, projected; provenance is complete and cannot be retrofitted. |

## How the morphism works

1. A ticket declares a `target_cell` and a `target_transition` (`from → to`).
2. `draft → active` is gated by **gate-ticket-ready**: the target cell exists, the transition is legal in
   the maturity machine, and `acceptance.rubric_cell` is itself **validated** (doneness is a validated
   rubric, never prose).
3. `active → claimed` is **server-set** (the claim race is designed out), gated by **gate-dispatch**.
4. `in-review → done` runs the **validation path** (`validate.py`): it executes the verifier, mints a
   `Signal` from its **exit status**, and advances the cell `instantiated → validated` only on pass. The
   ticket reaches `done` only if that signal landed — `gate-signal` denies any worker attempt to write it.

## Run it

```bash
python3 dev-factory/dev-kernel/evals/tracer-bullet/replay.py    # exit 0 = the thesis holds
```

The same property set is asserted inline by `bin/lifecycle.py selftest` (the unit form); this replay is
the **standalone, end-to-end** form that also exercises the real `gate-signal` hook as a subprocess and
the ledger on disk — the durable CI proof that Crawl's milestone is met.
