#!/usr/bin/env python3
"""replay.py — the REVERSE direction of the morphism (council M1: the biconditional was half-proven).

tracer-bullet proves the FORWARD direction: ticket `done` ⟹ the cell advanced through a critic-minted
signal. The thesis is a BICONDITIONAL — "the board cannot disagree with the lattice" — so the reverse must
hold too: a cell reaching `validated` ⟹ the board (the append-only ledger) recorded it, and there is NO
out-of-band path to `validated`. This proves the reverse, mechanically:

  R1  a worker CANNOT advance a cell by writing lattice.json (gate-verifier denies) — maturity is server-only.
  R2  a worker CANNOT forge the signal `validated` requires (gate-signal denies) — the currency is critic-only.
  R3  so the ONLY path to `validated` is the validation path, which LEDGERS the advance — every validated
      cell therefore has a recorded transition the board reflects (no silent advance).
  R4  the lattice's own invariant: there is NO `validated` cell without a signal_ref (lattice.py check
      flags `validated-without-signal`), so a maturity the board doesn't know about is unrepresentable.

Together with tracer-bullet, the biconditional holds: board ⟺ lattice. Exit 0 = the reverse holds.
Stdlib only; Python 3.8+. Answer key in README.md.
"""
import json
import os
import subprocess
import sys
import tempfile

_BIN = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "bin")
sys.path.insert(0, _BIN)
import lattice as _lat      # noqa: E402
import lifecycle as _lc     # noqa: E402
import ledger as _led       # noqa: E402


def _hook(gate, path):
    payload = {"tool_name": "Write", "tool_input": {"file_path": path}}
    return subprocess.run(["python3", os.path.join(_BIN, gate), "--hook"],
                          input=json.dumps(payload), capture_output=True, text=True).returncode


def run():
    fails = []
    def check(cond, label):
        print(f"  {'PASS' if cond else 'FAIL'}  {label}")
        if not cond:
            fails.append(label)

    with tempfile.TemporaryDirectory() as root:
        d = os.path.join(root, ".agents/dev-factory")
        _lat.scaffold(d)
        _lat.save(d, {"cells": [
            {"layer": "rubric", "scope": "task", "slug": "r", "maturity": "validated", "signal_refs": ["signals/rubric.task.r/seed.json"], "depends_on": []},
            {"layer": "spec", "scope": "task", "slug": "x", "maturity": "instantiated", "asset_ref": "spec/x.md", "depends_on": [], "signal_refs": []},
        ]})
        os.makedirs(os.path.join(d, "spec"), exist_ok=True)
        open(os.path.join(d, "spec", "x.md"), "w").write("# x\n")

        print("· R1/R2 — out-of-band advance is mechanically denied")
        check(_hook("gate-verifier", ".agents/dev-factory/lattice.json") == 2,
              "R1: a worker write to lattice.json is DENIED (cell maturity is server-only)")
        check(_hook("gate-signal", ".agents/dev-factory/signals/spec.task.x/forged.json") == 2,
              "R2: a worker write to signals/ is DENIED (the validated-currency is critic-only)")

        print("· R3 — the only path to validated LEDGERS the advance")
        tid = _led.ulid("tkt-")
        ticket = {"id": tid, "type": "feature", "title": "t", "body": "", "state": "in-review",
                  "target_cell": "spec.task.x", "target_transition": {"from": "instantiated", "to": "validated"},
                  "acceptance": {"rubric_cell": "rubric.task.r"}, "budget": {"iterations": 2, "tokens": 1000},
                  "provenance": {"created_by": "h", "ledger_refs": []},
                  "timestamps": {"created": "2026-06-14T00:00:00+00:00", "updated": "2026-06-14T00:00:00+00:00"}}
        ok, ticket, _msg = _lc.transition(d, ticket, "done", {"kind": "server", "id": "srv"},
                                          verifier="python3 -c 'import sys;sys.exit(0)'")
        cell = _lat.find(_lat.load(d), "spec.task.x")
        check(ok and cell["maturity"] == "validated", "the validation path advanced the cell to validated")
        led = _led.read(d, cell="spec.task.x")
        check(any(e["event"] == "transition" and e.get("to") == "validated" for e in led),
              "R3: the advance to validated is RECORDED in the ledger (the board reflects the lattice)")
        check(any(e["event"] == "signal" and e.get("to") == "pass" for e in led),
              "R3b: the critic's signal is ledgered — provenance for the advance")

        print("· R4 — a validated cell WITHOUT a signal is unrepresentable (lattice.py check flags it)")
        # forge a validated-without-signal cell directly in lattice.json and assert `check` rejects it
        bad = _lat.load(d)
        bad["cells"].append({"layer": "policy", "scope": "task", "slug": "sneaky", "maturity": "validated",
                             "signal_refs": [], "depends_on": []})
        findings = _lat.check(bad, d)
        check(any("signal" in f.lower() for f in findings),
              f"R4: lattice.py check flags a validated-without-signal cell (findings: {[f[:40] for f in findings][:3]})")

    print()
    if fails:
        print(f"reverse-morphism: HALF-PROVEN — {len(fails)} check(s) failed:")
        for f in fails:
            print(f"  - {f}")
        return 1
    print("reverse-morphism: OK — a cell cannot reach validated out-of-band (lattice.json + signals/ are "
          "deny-on-write to workers), the only path LEDGERS the advance, and a validated-without-signal cell is "
          "structurally rejected. With tracer-bullet's forward direction, the biconditional holds: the board "
          "cannot disagree with the lattice, in EITHER direction.")
    return 0


if __name__ == "__main__":
    sys.exit(run())
