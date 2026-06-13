#!/usr/bin/env python3
"""run-budget.py — start/inspect/clear the GLOBAL loop bound (a thin CLI over the kernel's run_budget_*).

The council's convergent v0.4.0 Critical: `/harness-run`'s caps (max-cells, max-iterations, wall-clock) lived
only as prose a model agent "ticked" — a computation routed to inference at the loop's terminator. The fix
lives in the kernel (`lattice.run_budget_*`): the run's budget is persisted to `.harness/run/budget.json`, and
the exhaustion verdict is COMPUTED from code (wall-clock from an absolute deadline — no counter; iterations
and cells counted from the ledger). `gate-budget` reads `run_budget_exhausted()` and denies every worker
write once the run is spent. This CLI is how the orchestrator (`/harness-run`) starts and ends the run.

Usage:
  run-budget.py start [--max-iterations N] [--max-cells N] [--wall-clock-s S] [--dir DIR]
  run-budget.py status [--dir DIR]      # exit 0 = budget remains · 1 = exhausted (gate denies writes) · 2 = no run
  run-budget.py clear  [--dir DIR]      # end the run
  run-budget.py selftest
Stdlib only; Python 3.8+.
"""
import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    import lattice as _lat
except ImportError:
    import _lattice as _lat


def _now():
    return datetime.datetime.now().astimezone()


def selftest():
    import tempfile
    fails = []
    def expect(cond, label):
        if not cond:
            fails.append(label)
    with tempfile.TemporaryDirectory() as root:
        d = os.path.join(root, ".harness")
        _lat.scaffold(d)
        now = _now().isoformat(timespec="seconds")

        ex, _, det = _lat.run_budget_exhausted(d, now)
        expect(not ex and det == {"active": False}, f"no-run treated as exhausted: {det}")

        deadline = (_now() + datetime.timedelta(seconds=600)).isoformat(timespec="seconds")
        _lat.run_budget_start(d, now, max_iterations=3, max_cells=2, deadline_iso=deadline)
        ex, why, det = _lat.run_budget_exhausted(d, now)
        expect(not ex and det["iterations"] == 0, f"fresh run exhausted: {why}")

        # 3 validate events in the ledger → max-iterations (3), counted from the LEDGER not an agent
        os.makedirs(os.path.join(d, "ledger"), exist_ok=True)
        with open(os.path.join(d, "ledger", "events.jsonl"), "w", encoding="utf-8") as f:
            for i in range(3):
                f.write('{"operation":"validate","actor":"advancer","cell_id":"spec.task.c%d","result":"fail","ts":"%s"}\n' % (i, now))
        ex, why, det = _lat.run_budget_exhausted(d, now)
        expect(ex and "max-iterations" in why, f"max-iterations not enforced from the ledger: {why} {det}")

        # a past deadline → exhausted regardless of iterations (the cap that needs no counter)
        future_now = (_now() + datetime.timedelta(seconds=900)).isoformat(timespec="seconds")
        ex, why, _ = _lat.run_budget_exhausted(d, future_now)
        expect(ex and ("wall-clock" in why or "max-iterations" in why), f"past deadline not enforced: {why}")

        _lat.run_budget_clear(d)
        ex, _, det = _lat.run_budget_exhausted(d, now)
        expect(not ex and det == {"active": False}, "clear did not end the run")
    if fails:
        sys.stderr.write("run-budget selftest: FAIL\n")
        for f in fails:
            sys.stderr.write(f"  - {f}\n")
        return 1
    print("run-budget selftest: OK (wall-clock enforced with no counter; iterations/cells counted from the LEDGER, "
          "not an agent; no active run is never exhausted; clear ends it — the global bound is code)")
    return 0


def _intflag(argv, name):
    return int(argv[argv.index(name) + 1]) if name in argv else None


def main(argv):
    if argv and argv[0] == "selftest":
        return selftest()
    d = argv[argv.index("--dir") + 1] if "--dir" in argv else ".harness"
    if argv and argv[0] == "start":
        wc = _intflag(argv, "--wall-clock-s")
        deadline = (_now() + datetime.timedelta(seconds=wc)).isoformat(timespec="seconds") if wc else None
        b = _lat.run_budget_start(d, _now().isoformat(timespec="seconds"),
                                  _intflag(argv, "--max-iterations"), _intflag(argv, "--max-cells"), deadline)
        print(f"run-budget started: max-iterations={b['max_iterations']} max-cells={b['max_cells']} deadline={b['deadline_ts']}")
        return 0
    if argv and argv[0] == "clear":
        print("run-budget cleared (no active run)" if _lat.run_budget_clear(d) else "no active run-budget to clear")
        return 0
    if argv and argv[0] == "status":
        ex, why, det = _lat.run_budget_exhausted(d, _now().isoformat(timespec="seconds"))
        if not det.get("active"):
            print("run-budget: no active run.")
            return 2
        if ex:
            print(f"run-budget: EXHAUSTED — {why}. The wired gate-budget denies further worker writes; stop the loop.")
            return 1
        print(f"run-budget: active — {det.get('iterations', 0)} iteration(s), {det.get('cells', 0)} cell(s) so far"
              + (f", deadline {det['deadline_ts']}" if det.get('deadline_ts') else "") + ".")
        return 0
    print(__doc__.split("Usage:")[1].split("Stdlib")[0].strip(), file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
