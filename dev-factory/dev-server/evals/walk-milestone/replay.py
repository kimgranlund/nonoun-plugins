#!/usr/bin/env python3
"""replay.py — the Walk milestone (TDD §19): a vertical slice reaches done UNATTENDED, within budget.

Crawl proved a human can drive a cell to validated through the API. Walk proves the FACTORY can: the
30s heartbeat — compass selects, the dispatcher provisions+runs+validates, the lease recovers crashes —
drives a dependency-ordered slice to done with NO human transitions, bounded by a budget it surfaces
rather than burns, and with the reward-hack boundary mechanically intact. This is the precondition the
trust ladder reads to permit Tier 2.

Driven UNATTENDED: after a human triages the two tickets to `active`, the replay calls ONLY
`heartbeat.on_tick()` — every claim, dispatch, validation, and close is the loop's, not the test's.

Falsified if any breaks:
  W1  both tickets reach `done` driven only by heartbeat ticks (unattended).
  W2  readiness order is respected: B (depends on A's cell) is NOT dispatched until A's cell validates.
  W3  bounded: the run never exceeds its window; an exhausted budget HALTS dispatch, it does not burn through.
  W4  no reward-hack: a worker cannot forge a signal (gate-signal active); false-pass is `unmeasured`/0 incidents.

Exit 0 = Walk met. Stdlib only; Python 3.8+. Answer key in README.md.
"""
import json
import os
import subprocess
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_SERVER = os.path.dirname(os.path.dirname(_HERE))
sys.path.insert(0, _SERVER)
import api as _api          # noqa: E402
import heartbeat as _hb     # noqa: E402
sys.path.insert(0, _api._store._KERNEL_BIN)
import lattice as _lat      # noqa: E402
import ledger as _led       # noqa: E402
import autonomy as _auto    # noqa: E402


def run():
    import tempfile
    fails = []
    def check(cond, label):
        print(f"  {'PASS' if cond else 'FAIL'}  {label}")
        if not cond:
            fails.append(label)

    with tempfile.TemporaryDirectory() as root:
        d = os.path.join(root, ".agents/dev-factory")
        _api.init_instance(d)
        human = {"kind": "human", "id": "operator"}
        _api.seed_cell(d, "rubric", "task", "r", maturity="validated", signal_refs=["signals/rubric.task.r/seed.json"])
        _api.seed_cell(d, "spec", "task", "x", maturity="instantiated", asset_ref="spec/x.md")
        _api.seed_cell(d, "spec", "task", "y", maturity="instantiated", asset_ref="spec/y.md")
        os.makedirs(os.path.join(d, "spec"), exist_ok=True)
        open(os.path.join(d, "spec", "x.md"), "w").write("# x\n")
        open(os.path.join(d, "spec", "y.md"), "w").write("# y\n")

        # Two tickets: A advances X; B advances Y but DEPENDS on X being validated first.
        A = _api.create_ticket(d, "feature", "advance X", target_cell="spec.task.x",
                               target_transition={"from": "instantiated", "to": "validated"},
                               acceptance={"rubric_cell": "rubric.task.r"}, budget={"iterations": 2, "tokens": 40000},
                               priority={"risk": 0.8})
        B = _api.create_ticket(d, "feature", "advance Y (needs X)", target_cell="spec.task.y",
                               target_transition={"from": "instantiated", "to": "validated"},
                               acceptance={"rubric_cell": "rubric.task.r"}, budget={"iterations": 2, "tokens": 40000},
                               priority={"risk": 0.9}, dependencies={"cells_ready": ["spec.task.x"]})
        # the human only triages them to active; the heartbeat does the rest
        _api.transition_ticket(d, A["id"], "active", human)
        _api.transition_ticket(d, B["id"], "active", human)

        print("· the family has EARNED Tier 2 (validated verifier + a clean independent refuter check + a budget)")
        _hb.arm(d, max_dispatches=5, deadline_s=3600)
        _auto.record_refuter_check(d, "rubric.task.r", agreed=True)   # the accrued clean track record
        check(_auto.tier_for(d) == 2, f"W0: family earned Tier 2 (unattended-in-budget); got tier {_auto.tier_for(d)}")

        print("· running heartbeat ticks at the EARNED tier (UNATTENDED to done)")

        def st(tid):
            return _api.get_ticket(d, tid)["state"]

        # Tick 1: only A is ready (B's dep cell X isn't validated yet)
        s1 = _hb.on_tick(d, max_concurrency=2)
        check(not s1["halted"], "loop ran (armed, within budget)")
        check(st(A["id"]) == "done", "W1a: tick 1 drove A to done unattended")
        check(st(B["id"]) == "active", "W2a: B NOT dispatched in tick 1 — its dependency cell X wasn't validated")
        check(_lat.find(_lat.load(d), "spec.task.x")["maturity"] == "validated", "A's cell X validated")

        # Tick 2: X is validated → B becomes ready → dispatched to done
        s2 = _hb.on_tick(d, max_concurrency=2)
        check(st(B["id"]) == "done", "W1b/W2b: tick 2 drove B to done once its dependency validated")
        check(_lat.find(_lat.load(d), "spec.task.y")["maturity"] == "validated", "B's cell Y validated")

        print("· W3 — the bound: a past-deadline window HALTS dispatch (surface, not burn)")
        _api.seed_cell(d, "spec", "task", "z", maturity="instantiated", asset_ref="spec/z.md")
        open(os.path.join(d, "spec", "z.md"), "w").write("# z\n")
        Z = _api.create_ticket(d, "feature", "advance Z", target_cell="spec.task.z",
                               target_transition={"from": "instantiated", "to": "validated"},
                               acceptance={"rubric_cell": "rubric.task.r"}, budget={"iterations": 2, "tokens": 40000})
        _api.transition_ticket(d, Z["id"], "active", human)
        _hb.arm(d, deadline_s=-1, max_dispatches=5)
        s3 = _hb.on_tick(d, max_concurrency=2)
        check(s3["halted"] and "deadline" in (s3["reason"] or ""), "W3a: exhausted window halted the tick")
        check(st(Z["id"]) == "active", "W3b: Z was NOT dispatched past the deadline (the bound held)")

        print("· W4 — no reward-hack")
        forge = {"tool_name": "Write", "tool_input": {"file_path": ".agents/dev-factory/signals/spec.task.z/forged.json"}}
        gs = subprocess.run(["python3", os.path.join(_api._store._KERNEL_BIN, "gate-signal"), "--hook"],
                            input=json.dumps(forge), capture_output=True, text=True)
        check(gs.returncode == 2, "W4a: gate-signal denies a worker forging a signal during the unattended run")
        check(_auto.false_pass(d) == 0.0 and len(_auto.refuter_checks(d)) >= 1 and not _auto.open_incidents(d),
              "W4b: false-pass is a REAL measured 0% (backed by an independent refuter, zero incidents) — not a fake 0%")
        # every advance that reached `validated` carries a real critic signal (not the worker's)
        validated = [c for c in _api.lattice_grid(d) if c["maturity"] == "validated" and c["layer"] == "spec"]
        check(all(c["signal_count"] >= 1 for c in validated), "W4c: every validated cell carries a critic-minted signal")
        # the agent/activity lens has data: dispatch + activity events are ledgered
        check(any(e["event"] == "dispatch" for e in _led.read(d)), "W4d: dispatches are ledgered (the agent/activity lens materializes from this)")

    print()
    if fails:
        print(f"walk-milestone: NOT MET — {len(fails)} check(s) failed:")
        for f in fails:
            print(f"  - {f}")
        return 1
    print("walk-milestone: OK — the heartbeat drove a dependency-ordered slice to done UNATTENDED, in readiness "
          "order, within a bounded window that halts rather than burns, with the reward-hack boundary intact and "
          "false-pass honestly unmeasured. Tier 2's precondition is met.")
    return 0


if __name__ == "__main__":
    sys.exit(run())
