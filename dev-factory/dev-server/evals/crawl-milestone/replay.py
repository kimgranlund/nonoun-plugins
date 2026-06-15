#!/usr/bin/env python3
"""replay.py — the Crawl milestone (TDD §19): one cell driven absent -> validated THROUGH the server API.

Where the kernel's tracer bullet proves the morphism on the validate step in isolation, this proves the
WHOLE Crawl phase: a cell advanced from `absent` to `validated` entirely through the server's operations
layer (api.py) — the full engine define -> create -> validate as a sequence of tickets — with every gate
firing, a real critic-written signal on disk, the index materializing each step, and the complete arc in
the append-only ledger. No heartbeat (it stays OFF in Crawl), no UI, no auto-dispatch: a human drives it.

The milestone is falsified if any of these breaks:
  M1  the cell traverses absent -> defined -> validated, applied only by the server (single-writer).
  M2  the AUTHORING advance (absent->defined) needs no critic signal, but the VALIDATED advance does.
  M3  a worker cannot forge the validation signal (gate-signal denies it) nor the maturity (lattice.json).
  M4  the index grid shows the cell `validated`; the ledger holds the full arc; both tickets are `done`.

Exit 0 = milestone met. Stdlib only; Python 3.8+. Answer key in README.md (outside the fixture).
"""
import json
import os
import subprocess
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_SERVER = os.path.dirname(os.path.dirname(_HERE))
sys.path.insert(0, _SERVER)
import api          # noqa: E402  (the server operations layer)
import store as _store  # noqa: E402
sys.path.insert(0, _store._KERNEL_BIN)
import lattice as _lat  # noqa: E402

CELL = "spec.system.first-feature"
RUBRIC = "rubric.system.first-feature"


def _drive(d, tid, states, srv, **kw):
    for to in states:
        ok, _t, msg = api.transition_ticket(d, tid, to, srv, **(kw if to == "done" else {}))
        if not ok:
            return False, f"{to}: {msg}"
    return True, "ok"


def run():
    import tempfile
    fails = []
    def check(cond, label):
        print(f"  {'PASS' if cond else 'FAIL'}  {label}")
        if not cond:
            fails.append(label)

    with tempfile.TemporaryDirectory() as root:
        d = os.path.join(root, ".agents/dev-factory")
        api.init_instance(d)
        srv = {"kind": "server", "id": "dev-server"}

        # Bootstrapping: the kit supplies a VALIDATED rubric (the verifier the spec is graded against).
        api.seed_cell(d, "rubric", "system", "first-feature", maturity="validated",
                      signal_refs=["signals/rubric.system.first-feature/kit-seed.json"])
        # The target cell begins ABSENT.
        api.seed_cell(d, "spec", "system", "first-feature", maturity="absent")
        check(api.lattice_grid(d) and next(c for c in api.lattice_grid(d) if c["id"] == CELL)["maturity"] == "absent",
              "M1a: target cell begins `absent`")

        print("· DEFINE ticket — absent -> defined (authoring; no critic signal)")
        t1 = api.create_ticket(d, "task", "define the first feature", target_cell=CELL,
                               target_transition={"from": "absent", "to": "defined"},
                               acceptance={"rubric_cell": RUBRIC}, budget={"iterations": 2, "tokens": 50000})
        ok, msg = _drive(d, t1["id"], ["active", "claimed", "in-progress"], srv)
        check(ok, f"M1b: define ticket reached in-progress ({msg})")
        # the worker authors the asset (rewritable side); the server records asset_ref (still absent until done)
        os.makedirs(os.path.join(d, "spec"), exist_ok=True)
        open(os.path.join(d, "spec", "first-feature.md"), "w").write("# First feature\n\nThe authored spec.\n")
        api.seed_cell(d, "spec", "system", "first-feature", maturity="absent", asset_ref="spec/first-feature.md")
        ok, msg = _drive(d, t1["id"], ["in-review", "done"], srv)   # done(to=defined) → _author_advance, no verifier
        defined = next(c for c in api.lattice_grid(d) if c["id"] == CELL)
        check(ok and defined["maturity"] == "defined", f"M2a: authoring done advanced absent->defined with NO signal ({msg})")
        check(api.get_ticket(d, t1["id"])["state"] == "done", "M1c: define ticket is done")

        print("· CREATE ticket — defined -> instantiated (authoring; the worker writes the artifact)")
        tc = api.create_ticket(d, "task", "create the first feature artifact", target_cell=CELL,
                               target_transition={"from": "defined", "to": "instantiated"},
                               acceptance={"rubric_cell": RUBRIC}, budget={"iterations": 2, "tokens": 50000})
        ok, msg = _drive(d, tc["id"], ["active", "claimed", "in-progress", "in-review", "done"], srv)
        inst = next(c for c in api.lattice_grid(d) if c["id"] == CELL)
        check(ok and inst["maturity"] == "instantiated", f"M2b: create advanced defined->instantiated with NO signal ({msg})")

        print("· worker tries to forge the validation signal — gate-signal must DENY it")
        forge = {"tool_name": "Write", "tool_input": {"file_path": f".agents/dev-factory/signals/{CELL}/forged.json"}}
        gs = subprocess.run(["python3", os.path.join(_store._KERNEL_BIN, "gate-signal"), "--hook"],
                            input=json.dumps(forge), capture_output=True, text=True)
        check(gs.returncode == 2, "M3a: gate-signal DENIES a worker forging the signal (exit 2)")
        latw = {"tool_name": "Edit", "tool_input": {"file_path": ".agents/dev-factory/lattice.json"}}
        gv = subprocess.run(["python3", os.path.join(_store._KERNEL_BIN, "gate-verifier"), "--hook"],
                            input=json.dumps(latw), capture_output=True, text=True)
        check(gv.returncode == 2, "M3b: gate-verifier DENIES a worker writing lattice.json (the maturity is server-only)")

        print("· VALIDATE ticket — instantiated -> validated (critic-gated; a real signal is minted)")
        t2 = api.create_ticket(d, "task", "validate the first feature", target_cell=CELL,
                               target_transition={"from": "instantiated", "to": "validated"},
                               acceptance={"rubric_cell": RUBRIC}, budget={"iterations": 3, "tokens": 100000})
        ok, msg = _drive(d, t2["id"], ["active", "claimed", "in-progress", "in-review"], srv)
        check(ok, f"M1d: validate ticket reached in-review ({msg})")
        ok, _t, msg = api.transition_ticket(d, t2["id"], "done", srv, verifier="python3 -c 'import sys;sys.exit(0)'")
        validated = next(c for c in api.lattice_grid(d) if c["id"] == CELL)
        check(ok and validated["maturity"] == "validated", f"M2c: validated advance is signal-gated and passed ({msg})")
        check(validated["signal_count"] >= 1, "M2d: the validated cell carries a real signal (minted by the validation path)")
        check(api.get_ticket(d, t2["id"])["state"] == "done", "M1e: validate ticket is done")

        print("· M4 — the index + ledger reflect the full arc")
        # a real signal file exists on disk; the forged one never landed
        sig_dir = os.path.join(d, "signals", CELL)
        sigs = os.listdir(sig_dir) if os.path.isdir(sig_dir) else []
        check("forged.json" not in sigs and any(s.endswith(".json") for s in sigs),
              "M4a: a real signal file is on disk; the forged one never landed")
        led = api.ledger_query(d, cell=CELL)
        tos = [e.get("to") for e in led if e.get("event") == "transition"]
        check("defined" in tos and "validated" in tos, "M4b: the ledger holds absent->defined and ->validated transitions")
        check(any(e["event"] == "signal" and e.get("to") == "pass" for e in led), "M4c: the critic's pass signal is ledgered")
        grid = {c["id"]: c for c in api.lattice_grid(d)}
        check(grid[CELL]["maturity"] == "validated", "M4d: the lattice grid (the index) shows the cell `validated`")

    print()
    if fails:
        print(f"crawl-milestone: NOT MET — {len(fails)} check(s) failed:")
        for f in fails:
            print(f"  - {f}")
        return 1
    print("crawl-milestone: OK — one cell driven absent -> defined -> validated entirely through the server "
          "API; authoring needs no signal, validation does; the worker can forge neither the signal nor the "
          "maturity; the index and ledger hold the full, gated arc. Crawl is met — Walk (the heartbeat) is earned.")
    return 0


if __name__ == "__main__":
    sys.exit(run())
