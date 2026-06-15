#!/usr/bin/env python3
"""compass.py — the deterministic selection: which READY ticket to dispatch next.

The compass is two functions the spec is emphatic must never be conflated: **scan** (detect what is
ready) and **rank** (order the ready set by value). Both are arithmetic/graph computation over the
lattice + the coordination index + the ledger — NEVER inference (TDD §8.2; the routing law). A
model-predicted ranking is a hallucination surface; the model's judgment lives INSIDE a dispatched
unit, never in choosing which unit runs.

  priority(t) = (risk_concentration(t) × unlock_value(t)) / probe_cost(t)     subject to readiness

  - risk_concentration : the ticket's triage estimate (priority.risk), cold-start only — replaced by
                         ledger evidence as it accrues.
  - unlock_value       : COMPUTED from the dependency graph — how many other tickets are waiting on
                         this ticket's target cell. Pure graph traversal, not a stored guess.
  - probe_cost         : MEASURED from the ledger (mean tokens per prior signal for this cell's
                         layer.scope) once history exists; a fixed prior on cold start. The value
                         function goes empirical the moment the ledger has data.

Readiness (the `scan` half) reuses the kernel's gate-dispatch predicate (deps validated, budget,
autonomy tier, target not blocked) — one source of truth for "dispatchable".

Usage:
  compass.py next   --dir DIR [--tier T] [--slots N]    # the ready+ranked batch the heartbeat dispatches
  compass.py rank   --dir DIR                            # rank ALL active tickets (diagnostic)
  compass.py selftest
Stdlib only; Python 3.8+.
"""
import json
import os
import sys

_ROOT = os.environ.get("CLAUDE_PLUGIN_ROOT") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "bin"))
import lattice as _lat      # noqa: E402
import lifecycle as _lc     # noqa: E402
import ledger as _led       # noqa: E402

COLD_START_PROBE = 50000.0   # a token prior for an unseen cell type, before the ledger has evidence


def _active_tickets(d):
    out = []
    tdir = os.path.join(d, "coordination", "tickets")
    if not os.path.isdir(tdir):
        return out
    for f in os.listdir(tdir):
        if not f.endswith(".json"):
            continue
        try:
            t = json.load(open(os.path.join(tdir, f), encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        out.append(t)
    return out


def _done_ids(tickets):
    return {t["id"] for t in tickets if t.get("state") == "done"}


def unlock_value(ticket, all_tickets):
    """Graph computation: how many OTHER tickets are waiting on this ticket's target cell to validate.
    Pure traversal of the declared dependency edges — the unblock fan-out, not a stored estimate."""
    tc = ticket.get("target_cell")
    if not tc:
        return 0
    n = 0
    for o in all_tickets:
        if o["id"] == ticket["id"]:
            continue
        if tc in (o.get("dependencies", {}) or {}).get("cells_ready", []):
            n += 1
        if ticket["id"] in (o.get("dependencies", {}) or {}).get("tickets", []):
            n += 1
    return n


def probe_cost(d, layer, scope):
    """Measured mean tokens per prior signal for this cell type (layer.scope), from the ledger; a fixed
    prior on cold start. Reads metrics the dispatcher records on each signal event."""
    costs = []
    for e in _led.read(d, event="signal"):
        cell = (e.get("subject") or {}).get("cell", "")
        parts = cell.split(".")
        if len(parts) >= 2 and parts[0] == layer and parts[1] == scope:
            m = e.get("metrics") or {}
            if isinstance(m.get("tokens"), (int, float)) and m["tokens"] > 0:
                costs.append(float(m["tokens"]))
    return sum(costs) / len(costs) if costs else COLD_START_PROBE


def priority(d, ticket, all_tickets):
    pr = ticket.get("priority", {}) or {}
    risk = float(pr.get("risk", 0.5))                       # cold-start triage estimate
    unlock = max(unlock_value(ticket, all_tickets), 1)      # >=1 so an unblocking-nothing ticket still ranks
    tc = ticket.get("target_cell", "")
    parts = tc.split(".")
    cost = probe_cost(d, parts[0], parts[1]) if len(parts) >= 2 else COLD_START_PROBE
    return (risk * unlock) / max(cost, 1.0)


def rank(d, tickets):
    """Order a list of tickets by priority, descending. Stable on ties (by id) for determinism."""
    allt = _active_tickets(d)
    return sorted(tickets, key=lambda t: (-priority(d, t, allt), t["id"]))


def ready(d, tickets, tier=1, slots_free=999):
    """The scan half: filter to dispatchable tickets via the kernel's gate-dispatch predicate. A ticket
    is ready iff it is `active`, its deps are validated, budget remains, the autonomy tier permits an
    unattended dispatch, and its target cell isn't blocked."""
    lat = _lat.load(d)
    done = _done_ids(_active_tickets(d))
    out = []
    for t in tickets:
        if t.get("state") != "active":
            continue
        ok, _why = _lc.gate_dispatch(d, t, lat, slots_free=slots_free, tier=tier, done_tickets=done)
        if ok:
            out.append(t)
    return out


def next_batch(d, tier=1, slots_free=1):
    """The full compass step the heartbeat calls: active -> ready -> ranked -> top `slots_free`."""
    active = [t for t in _active_tickets(d) if t.get("state") == "active"]
    rd = ready(d, active, tier=tier, slots_free=slots_free)
    return rank(d, rd)[:max(slots_free, 0)]


def selftest():
    import tempfile
    fails = []
    def expect(c, m):
        if not c:
            fails.append(m)
    with tempfile.TemporaryDirectory() as root:
        d = os.path.join(root, ".agents/dev-factory")
        _lat.scaffold(d)
        _lat.save(d, {"cells": [
            {"layer": "spec", "scope": "task", "slug": "a", "maturity": "validated", "depends_on": [], "signal_refs": ["x"]},
            {"layer": "spec", "scope": "task", "slug": "b", "maturity": "instantiated", "depends_on": [], "signal_refs": []},
            {"layer": "spec", "scope": "task", "slug": "c", "maturity": "instantiated", "depends_on": [], "signal_refs": []},
            {"layer": "rubric", "scope": "task", "slug": "r", "maturity": "validated", "depends_on": [], "signal_refs": ["x"]},
        ]})
        os.makedirs(os.path.join(d, "coordination", "tickets"), exist_ok=True)
        def mk(slug, target, risk, unlock_deps=None, state="active", deps=None):
            tid = _led.ulid("tkt-")
            t = {"id": tid, "type": "task", "title": slug, "body": "", "state": state,
                 "target_cell": target, "target_transition": {"from": "instantiated", "to": "validated"},
                 "acceptance": {"rubric_cell": "rubric.task.r"}, "budget": {"iterations": 2, "tokens": 1000},
                 "dependencies": deps or {}, "priority": {"risk": risk},
                 "provenance": {"created_by": "h", "ledger_refs": []},
                 "timestamps": {"created": "2026-06-14T00:00:00+00:00", "updated": "2026-06-14T00:00:00+00:00"}}
            json.dump(t, open(os.path.join(d, "coordination", "tickets", f"{tid}.json"), "w"))
            return t
        # B is high-risk AND unblocks C (C depends on spec.task.b); A-target is already validated.
        tB = mk("B", "spec.task.b", 0.9, deps={})
        tC = mk("C", "spec.task.c", 0.3, deps={"cells_ready": ["spec.task.b"]})

        # unlock_value: B unblocks C (C waits on spec.task.b)
        allt = _active_tickets(d)
        expect(unlock_value(tB, allt) == 1, f"B should unlock 1 (C); got {unlock_value(tB, allt)}")
        expect(unlock_value(tC, allt) == 0, f"C should unlock 0; got {unlock_value(tC, allt)}")

        # readiness: C is NOT ready (its dep cell spec.task.b is not validated); B is ready
        rd = ready(d, allt, tier=1)
        ids = {t["id"] for t in rd}
        expect(tB["id"] in ids, "B (no unmet deps) should be ready")
        expect(tC["id"] not in ids, "C should be blocked: its dependency cell spec.task.b isn't validated")

        # tier 0 → nothing ready (no unattended dispatch)
        expect(ready(d, allt, tier=0) == [], "tier 0 must permit no unattended dispatch")

        # rank: B outranks C (higher risk × it unblocks more), and next_batch(slots=1) returns B
        batch = next_batch(d, tier=1, slots_free=1)
        expect(len(batch) == 1 and batch[0]["id"] == tB["id"], "compass did not rank the high-risk unblocking ticket first")

        # probe_cost: cold start = the prior; after a ledger signal w/ metrics, it goes empirical
        expect(probe_cost(d, "spec", "task") == COLD_START_PROBE, "probe_cost should be the cold-start prior")
        _led.append(d, "signal", {"kind": "agent", "id": "v"}, {"cell": "spec.task.b"}, "validated",
                    to="pass", metrics={"tokens": 12000})
        expect(abs(probe_cost(d, "spec", "task") - 12000.0) < 1, "probe_cost did not go empirical from the ledger")
    if fails:
        sys.stderr.write("compass selftest: FAIL\n")
        for f in fails:
            sys.stderr.write(f"  - {f}\n")
        return 1
    print("compass selftest: OK (unlock_value is graph-computed; readiness reuses gate-dispatch — an unmet "
          "dependency or tier 0 blocks dispatch; rank orders by (risk×unlock)/probe_cost; probe_cost is the "
          "cold-start prior until the ledger has signal metrics, then empirical)")
    return 0


def _arg(argv, flag, default=None):
    return argv[argv.index(flag) + 1] if flag in argv else default


def main(argv):
    if not argv or argv[0] == "selftest":
        return selftest()
    d = _arg(argv, "--dir", ".agents/dev-factory")
    if argv[0] == "next":
        batch = next_batch(d, tier=int(_arg(argv, "--tier", "1")), slots_free=int(_arg(argv, "--slots", "1")))
        for t in batch:
            print(t["id"], t.get("target_cell"))
        return 0
    if argv[0] == "rank":
        for t in rank(d, [t for t in _active_tickets(d) if t.get("state") == "active"]):
            print(f"{priority(d, t, _active_tickets(d)):.6f}  {t['id']}  {t.get('target_cell')}")
        return 0
    print(f"compass.py: unknown verb {argv[0]}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
