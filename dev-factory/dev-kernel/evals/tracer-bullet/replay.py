#!/usr/bin/env python3
"""replay.py — the tracer bullet: the falsifiable proof of the central reconciliation (TDD §4).

This drives ONE cell from `instantiated` to `validated` entirely through a ticket's lifecycle — no
server, no UI, no kit — and asserts the thesis the entire dev-factory rests on:

    A ticket reaches `done` IF AND ONLY IF its target cell advanced to the ticket's to-maturity, and
    that advance was minted by the validation path (a critic-written signal). The board (Kanban) and the
    lattice (grid) pass through the SAME gate-signal, so they cannot disagree.

The four properties it falsifies (each would sink the architecture if it failed):
  P1  done ⟹ the cell is `validated` and carries a signal_ref (no "validated by assertion").
  P2  a FAILING verifier neither closes the ticket nor advances the cell (reward-hack designed out).
  P3  the worker is MECHANICALLY unable to write the signal (gate-signal denies it) — so the signal's
      existence proves a critic, not the worker, produced it.
  P4  the ticket's signal_refs == the cell's signal_refs, and the whole run is in the append-only ledger.

Exit 0 = all properties hold; 1 = a property was falsified. Stdlib only; Python 3.8+.
The answer key (what each property means and why it is load-bearing) is in README.md — never inside the
fixture, so a cold judge run stays honest.
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


def run():
    fails = []
    def check(cond, label):
        print(f"  {'PASS' if cond else 'FAIL'}  {label}")
        if not cond:
            fails.append(label)

    with tempfile.TemporaryDirectory() as root:
        d = os.path.join(root, ".agents/dev-factory")
        _lat.scaffold(d)
        # Seed: a VALIDATED rubric (the bound verifier) + an INSTANTIATED spec cell (asset authored by a worker).
        lat = {"cells": [
            {"layer": "rubric", "scope": "task", "slug": "first-slice", "maturity": "validated",
             "signal_refs": ["signals/rubric.task.first-slice/seed.json"], "depends_on": []},
            {"layer": "spec", "scope": "task", "slug": "first-slice", "maturity": "instantiated",
             "asset_ref": "spec/first-slice.md", "depends_on": [], "signal_refs": []},
        ]}
        _lat.save(d, lat)
        os.makedirs(os.path.join(d, "spec"), exist_ok=True)
        open(os.path.join(d, "spec", "first-slice.md"), "w").write("# first slice\n\nThe authored asset.\n")

        tid = _led.ulid("tkt-")
        ticket = {
            "id": tid, "type": "feature", "title": "drive the first slice to validated",
            "body": "Crawl tracer bullet.", "state": "draft",
            "target_cell": "spec.task.first-slice",
            "target_transition": {"from": "instantiated", "to": "validated"},
            "acceptance": {"rubric_cell": "rubric.task.first-slice"},
            "budget": {"iterations": 3, "tokens": 100000},
            "dependencies": {},
            "provenance": {"created_by": "human", "ledger_refs": []},
            "timestamps": {"created": "2026-06-14T00:00:00+00:00", "updated": "2026-06-14T00:00:00+00:00"},
        }
        srv = {"kind": "server", "id": "dev-server"}

        print("· driving the lifecycle: draft -> active -> claimed -> in-progress -> in-review")
        for to in ["active", "claimed", "in-progress", "in-review"]:
            ok, ticket, msg = _lc.transition(d, ticket, to, srv)
            if not ok:
                check(False, f"reached {to} ({msg})")
                break

        print("· P2: a FAILING verifier must NOT close the ticket or advance the cell")
        ok, ticket, msg = _lc.transition(d, ticket, "done", srv, verifier="python3 -c 'import sys; sys.exit(1)'")
        cell_after_fail = _lat.find(_lat.load(d), "spec.task.first-slice")
        check(not ok, "P2a: done refused on a failing verifier")
        check(cell_after_fail["maturity"] == "instantiated", "P2b: cell NOT advanced by a failing verifier")
        check(ticket["state"] == "in-review", "P2c: ticket stays in-review (feedback path, not done)")

        print("· P3: the worker is mechanically unable to forge the signal (gate-signal denies the write)")
        forge = {"tool_name": "Write",
                 "tool_input": {"file_path": ".agents/dev-factory/signals/spec.task.first-slice/forged.json"}}
        proc = subprocess.run(["python3", os.path.join(_BIN, "gate-signal"), "--hook"],
                              input=json.dumps(forge), capture_output=True, text=True)
        check(proc.returncode == 2, "P3a: gate-signal DENIES a worker write to signals/ (exit 2)")
        allow = {"tool_name": "Write", "tool_input": {"file_path": ".agents/dev-factory/spec/first-slice.md"}}
        proc2 = subprocess.run(["python3", os.path.join(_BIN, "gate-signal"), "--hook"],
                               input=json.dumps(allow), capture_output=True, text=True)
        check(proc2.returncode == 0, "P3b: gate-signal ALLOWS a worker write to its own spec asset (exit 0)")

        print("· P1 + P4: a PASSING verifier mints the critic's signal, advances the cell, closes the ticket")
        ok, ticket, msg = _lc.transition(d, ticket, "done", srv, verifier="python3 -c 'import sys; sys.exit(0)'")
        cell = _lat.find(_lat.load(d), "spec.task.first-slice")
        check(ok and ticket["state"] == "done", "P1a: ticket reached done")
        check(cell["maturity"] == "validated", "P1b: cell advanced instantiated -> validated")
        check(bool(cell.get("signal_refs")), "P1c: the validated cell carries a signal_ref (the currency)")
        # the signal file on disk was written by the validation path, not the worker
        sig_dir = os.path.join(d, "signals", "spec.task.first-slice")
        sig_files = [f for f in os.listdir(sig_dir) if "forged" not in f]
        check(len(sig_files) >= 1 and not os.path.exists(os.path.join(sig_dir, "forged.json")),
              "P4a: a real signal exists on disk; the forged one never landed")
        check(ticket.get("signal_refs") == cell.get("signal_refs"),
              "P4b: ticket.signal_refs == cell.signal_refs (the board cannot disagree with the lattice)")
        led = _led.read(d, ticket=ticket["id"])
        events = {e["event"] for e in led}
        check("transition" in events and any(e["event"] == "signal" and e.get("to") == "pass" for e in _led.read(d)),
              "P4c: the whole run — transitions + the pass signal — is in the append-only ledger")

    print()
    if fails:
        print(f"tracer-bullet: FALSIFIED — {len(fails)} propert(ies) failed:")
        for f in fails:
            print(f"  - {f}")
        return 1
    print("tracer-bullet: OK — the central reconciliation holds. Ticket `done` <=> cell `validated` via a "
          "critic-minted signal the worker could not forge; board and lattice pass through one gate-signal.")
    return 0


if __name__ == "__main__":
    sys.exit(run())
