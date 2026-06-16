#!/usr/bin/env python3
"""heartbeat.py — the dark factory's pulse: the bounded 30s outer loop (TDD §8).

By the routing law the loop is DETERMINISTIC and lives in the server — scanning, dependency-filtering,
ranking, and dispatching are graph/arithmetic over the lattice + the coordination index, never inference.
Agents enter only INSIDE a dispatched unit. One tick:

    on_tick():
      if paused: return
      reconcile_leases()                       # expire dead workers (dispatch.py)
      if budget_exhausted(): return            # SURFACE the ceiling — never burn through it (Failure 4)
      slots = max_concurrency - running()
      for t in compass.next_batch(tier, slots):   # ready + ranked (compass.py)
          dispatch_unit(t)                          # provision, claim, run, validate (dispatch.py)
      emit_metrics()

The loop is BOUNDED by construction — the same discipline harness-forge's I-9 run budget enforces, here
dev-native over dev's ledger: a window with a wall-clock deadline, a max-dispatch cap, and a token
ceiling, armed before the loop runs. An exhausted window halts dispatch; the budget file lives under the
worker-protected run/ perimeter, so a worker cannot lift its own ceiling.

Usage:
  heartbeat.py arm   --dir DIR [--deadline-s N] [--max-dispatches N] [--token-ceiling N]
  heartbeat.py tick  --dir DIR [--tier T] [--max-concurrency N]    # one tick (mock adapter)
  heartbeat.py selftest
Stdlib only; Python 3.8+.
"""
import datetime
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
import api as _api          # noqa: E402
import dispatch as _disp    # noqa: E402
sys.path.insert(0, _api._store._KERNEL_BIN)
import compass as _compass  # noqa: E402
import ledger as _led       # noqa: E402
import autonomy as _auto    # noqa: E402


def _now():
    return datetime.datetime.now().astimezone()


def _budget_path(d):
    return os.path.join(d, "run", "heartbeat.json")


def arm(d, now=None, deadline_s=None, max_dispatches=None, token_ceiling=None):
    """Arm the loop's window. MUST be called before the loop runs (the arming discipline): an unarmed loop
    does not dispatch (fail-closed)."""
    now = now or _now()
    b = {"start_ts": now.isoformat(timespec="seconds"), "ticks": 0,
         "deadline_ts": (now + datetime.timedelta(seconds=deadline_s)).isoformat(timespec="seconds") if deadline_s else None,
         "max_dispatches": max_dispatches, "token_ceiling": token_ceiling}
    os.makedirs(os.path.dirname(_budget_path(d)), exist_ok=True)
    json.dump(b, open(_budget_path(d), "w"), indent=2)
    return b


def load_budget(d):
    p = _budget_path(d)
    return json.load(open(p, encoding="utf-8")) if os.path.isfile(p) else None


def clear(d):
    p = _budget_path(d)
    if os.path.isfile(p):
        os.remove(p)


def _dispatches_since(d, start_ts):
    return sum(1 for e in _led.read(d, since=start_ts) if e.get("event") == "dispatch")


def _tokens_since(d, start_ts):
    tot = 0
    for e in _led.read(d, since=start_ts):
        m = e.get("metrics") or {}
        if isinstance(m.get("tokens"), (int, float)):
            tot += m["tokens"]
    return tot


def budget_exhausted(d, now=None):
    """(exhausted, reason). Unarmed → fail-closed (the loop must arm first). Computed from code + the
    ledger, never an agent's counting."""
    now = now or _now()
    b = load_budget(d)
    if b is None:
        return True, "loop not armed — arm the heartbeat window before dispatching (fail-closed)"
    if b.get("deadline_ts") and now.isoformat(timespec="seconds") >= b["deadline_ts"]:
        return True, f"wall-clock deadline reached ({b['deadline_ts']})"
    if b.get("max_dispatches") is not None:
        n = _dispatches_since(d, b["start_ts"])
        if n >= b["max_dispatches"]:
            return True, f"max-dispatches reached ({n}/{b['max_dispatches']})"
    if b.get("token_ceiling") is not None:
        t = _tokens_since(d, b["start_ts"])
        if t >= b["token_ceiling"]:
            return True, f"token ceiling reached ({t}/{b['token_ceiling']})"
    return False, None


def count_running(d):
    return sum(1 for t in _api.list_tickets(d) if t.get("state") in ("claimed", "in-progress"))


PAUSED = {"v": False}


def on_tick(d, adapter=None, tier=None, max_concurrency=2, now=None):
    """One heartbeat tick. Deterministic end to end; agents run only inside dispatch_unit. The autonomy
    tier is READ from the ledger (autonomy.tier_for) unless overridden: Tier 0 dispatches nothing; Tier 1
    dispatches but stops at in-review for human review; Tier 2+ drives the unit to done unattended. Returns
    a summary {tier, dispatched, reconciled, halted, reason}."""
    now = now or _now()
    if PAUSED["v"]:
        return {"halted": True, "reason": "paused (human kill-switch)", "dispatched": []}
    if tier is None:
        tier = _auto.tier_for(d, now=now)          # the EARNED tier — mechanically demoted on incident
    adapter = adapter or _disp.resolve_adapter()   # DEV_FACTORY_ADAPTER=headless → live workers; default mock (free)
    reconciled = _disp.reconcile_leases(d, now=now)
    exhausted, reason = budget_exhausted(d, now=now)
    if exhausted:
        return {"halted": True, "reason": reason, "tier": tier, "dispatched": [], "reconciled": reconciled}
    slots = max_concurrency - count_running(d)
    if slots <= 0:
        return {"halted": False, "reason": "no free slot (backpressure)", "tier": tier, "dispatched": [], "reconciled": reconciled}
    batch = _compass.next_batch(d, tier=tier, slots_free=slots)
    auto = tier >= 2                                # Tier 1 dispatches but pauses at in-review (human reviews)
    dispatched = []
    for t in batch:
        ok, _t, _msg = _disp.dispatch_unit(d, _api.get_ticket(d, t["id"]), adapter,
                                           {"kind": "server", "id": "heartbeat"}, tier=tier, auto_validate=auto)
        dispatched.append({"ticket": t["id"], "ok": ok, "to": "done" if auto else "in-review"})
    b = load_budget(d)
    if b is not None:
        b["ticks"] = b.get("ticks", 0) + 1
        json.dump(b, open(_budget_path(d), "w"), indent=2)
    return {"halted": False, "reason": None, "tier": tier, "dispatched": dispatched, "reconciled": reconciled}


def run(d, adapter=None, tier=1, max_concurrency=2, period_s=30):
    """The live loop (the server's scheduler calls this). Blocks; the server runs it as a task."""
    import time
    while True:
        summ = on_tick(d, adapter=adapter, tier=tier, max_concurrency=max_concurrency)
        if summ.get("halted") and "deadline" in (summ.get("reason") or ""):
            return summ
        time.sleep(period_s)


def selftest():
    import tempfile
    fails = []
    def expect(c, m):
        if not c:
            fails.append(m)
    with tempfile.TemporaryDirectory() as root:
        d = os.path.join(root, ".agents/dev-factory")
        _api.init_instance(d)
        srv = {"kind": "server", "id": "dev-server"}
        _api.seed_cell(d, "rubric", "task", "r", maturity="validated", signal_refs=["signals/rubric.task.r/seed.json"])
        _api.seed_cell(d, "spec", "task", "s", maturity="instantiated", asset_ref="spec/s.md")
        os.makedirs(os.path.join(d, "spec"), exist_ok=True)
        open(os.path.join(d, "spec", "s.md"), "w").write("# s\n")
        t = _api.create_ticket(d, "feature", "the slice", target_cell="spec.task.s",
                               target_transition={"from": "instantiated", "to": "validated"},
                               acceptance={"rubric_cell": "rubric.task.r"}, budget={"iterations": 2, "tokens": 50000})
        _api.transition_ticket(d, t["id"], "active", srv)

        # UNARMED → fail-closed (no dispatch)
        s0 = on_tick(d)
        expect(s0["halted"] and "not armed" in s0["reason"], f"unarmed loop did not fail closed: {s0}")
        expect(_api.get_ticket(d, t["id"])["state"] == "active", "unarmed loop dispatched anyway")

        # armed + the family has EARNED Tier 2 (a validated verifier + an agreeing refuter check + a budget)
        # → the tick drives the ready ticket to done, UNATTENDED (Tier 1 would stop at in-review)
        arm(d, max_dispatches=5, deadline_s=3600)
        _auto.record_refuter_check(d, "spec.task.s", agreed=True)    # measured-clean false-pass → Tier 2
        s1 = on_tick(d, max_concurrency=2)                            # no tier override → the EARNED tier
        expect(s1.get("tier") == 2, f"family should have earned Tier 2; got tier {s1.get('tier')}")
        expect(not s1["halted"] and any(x["ok"] for x in s1["dispatched"]), f"armed tick did not dispatch: {s1}")
        expect(_api.get_ticket(d, t["id"])["state"] == "done", "heartbeat did not drive the slice to done unattended")
        cell = next(c for c in _api.lattice_grid(d) if c["id"] == "spec.task.s")
        expect(cell["maturity"] == "validated", "heartbeat-dispatched cell not validated")

        # the bound HALTS: a past deadline stops dispatch (surface, not burn)
        arm(d, deadline_s=-1, max_dispatches=5)
        _api.seed_cell(d, "spec", "task", "s2", maturity="instantiated", asset_ref="spec/s2.md")
        open(os.path.join(d, "spec", "s2.md"), "w").write("# s2\n")
        t2 = _api.create_ticket(d, "feature", "slice2", target_cell="spec.task.s2",
                                target_transition={"from": "instantiated", "to": "validated"},
                                acceptance={"rubric_cell": "rubric.task.r"}, budget={"iterations": 2, "tokens": 50000})
        _api.transition_ticket(d, t2["id"], "active", srv)
        s2 = on_tick(d)
        expect(s2["halted"] and "deadline" in s2["reason"], f"exhausted budget did not halt: {s2}")
        expect(_api.get_ticket(d, t2["id"])["state"] == "active", "dispatched past the deadline (burned through the bound)")
    if fails:
        sys.stderr.write("heartbeat selftest: FAIL\n")
        for f in fails:
            sys.stderr.write(f"  - {f}\n")
        return 1
    print("heartbeat selftest: OK (UNARMED fails closed; an armed tick drives a ready slice to done unattended "
          "via the compass+dispatcher; an exhausted window — past deadline — HALTS dispatch rather than burning "
          "through it; the budget lives under the worker-protected run/ perimeter)")
    return 0


def _arg(argv, flag, default=None):
    return argv[argv.index(flag) + 1] if flag in argv else default


def main(argv):
    if not argv or argv[0] == "selftest":
        return selftest()
    d = _arg(argv, "--dir", ".agents/dev-factory")
    if argv[0] == "arm":
        b = arm(d, deadline_s=int(_arg(argv, "--deadline-s", "0")) or None,
                max_dispatches=int(_arg(argv, "--max-dispatches", "0")) or None,
                token_ceiling=int(_arg(argv, "--token-ceiling", "0")) or None)
        print(json.dumps(b))
        return 0
    if argv[0] == "tick":
        print(json.dumps(on_tick(d, tier=int(_arg(argv, "--tier", "1")),
                                 max_concurrency=int(_arg(argv, "--max-concurrency", "2")))))
        return 0
    print(f"heartbeat.py: unknown verb {argv[0]}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
