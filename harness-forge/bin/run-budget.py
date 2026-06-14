#!/usr/bin/env python3
"""run-budget.py — start/inspect/clear the GLOBAL loop bound (a thin CLI over the kernel's run_budget_*).

The council's convergent v0.4.0 Critical: `/harness-run`'s caps (max-cells, max-iterations, wall-clock) lived
only as prose a model agent "ticked" — a computation routed to inference at the loop's terminator. The fix
lives in the kernel (`lattice.run_budget_*`): the run's budget is persisted to `.harness/run/budget.json`, and
the exhaustion verdict is COMPUTED from code (wall-clock from an absolute deadline — no counter; iterations
and cells counted from the ledger). `gate-budget` reads `run_budget_exhausted()` and denies every worker
write once the run is spent. This CLI is how the orchestrator (`/harness-run`) starts and ends the run.

The arming gap (I-9): the gate can only enforce a budget that EXISTS, and the orchestrator armed it at step 0
— skip that and the loop was silently unbounded. The fix is the **loop-active marker**: `/harness-run` calls
`mark` as step 0a (the mechanical signal that an autonomous loop is running), THEN `start` as step 0b (the
ceiling). `gate-budget` now denies every write while the loop is marked but un-budgeted, so a skipped `start`
fails CLOSED instead of running free. `start` also sets the marker (armed ⟹ marked); `stop` clears both.

Usage:
  run-budget.py mark   [--label L] [--dir DIR]     # step 0a — mark the autonomous loop active (gate the arming gap)
  run-budget.py start  [--max-iterations N] [--max-cells N] [--wall-clock-s S] [--label L] [--dir DIR]   # step 0b — arm the ceiling (also marks)
  run-budget.py status [--dir DIR]      # exit 0 = budget remains · 1 = exhausted · 2 = no run (3 = marked but un-budgeted: the arming gap)
  run-budget.py stop   [--dir DIR]      # end the loop — clears BOTH the budget and the marker
  run-budget.py clear  [--dir DIR]      # clear the budget only (leaves the marker; prefer `stop`)
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

        # the arming-gap marker (I-9): mark → unbudgeted (gate denies); start → marked+budgeted; stop → both cleared.
        # (suppress the commands' stdout so selftest output stays clean)
        _stdout = sys.stdout
        sys.stdout = open(os.devnull, "w")
        try:
            rc_mark = main(["mark", "--dir", d])
            unb_after_mark = _lat.loop_unbudgeted(d)[0]
            rc_status = main(["status", "--dir", d])
            rc_start = main(["start", "--max-cells", "5", "--dir", d])
            armed_marked = not _lat.loop_unbudgeted(d)[0] and _lat.loop_marker_active(d)
            rc_stop = main(["stop", "--dir", d])
            stopped = not _lat.loop_marker_active(d) and _lat.run_budget_load(d) is None
        finally:
            sys.stdout.close()
            sys.stdout = _stdout
        expect(rc_mark == 0, "mark command failed")
        expect(unb_after_mark, "mark did not produce the marked-but-unbudgeted (arming-gap) state")
        expect(rc_status == 3, "status did not return 3 (arming gap) for a marked, unbudgeted loop")
        expect(rc_start == 0, "start command failed")
        expect(armed_marked, "start did not leave the loop marked + budgeted")
        expect(rc_stop == 0, "stop command failed")
        expect(stopped, "stop did not clear both marker and budget")
    if fails:
        sys.stderr.write("run-budget selftest: FAIL\n")
        for f in fails:
            sys.stderr.write(f"  - {f}\n")
        return 1
    print("run-budget selftest: OK (wall-clock enforced with no counter; iterations/cells counted from the LEDGER, "
          "not an agent; no active run is never exhausted; clear ends it; the I-9 marker — mark→arming-gap, "
          "start→marked+budgeted, stop→both cleared — closes the arming gap; the global bound is code)")
    return 0


def _intflag(argv, name):
    return int(argv[argv.index(name) + 1]) if name in argv else None


def _strflag(argv, name, default=None):
    return argv[argv.index(name) + 1] if name in argv and argv.index(name) + 1 < len(argv) else default


def main(argv):
    if argv and argv[0] == "selftest":
        return selftest()
    d = argv[argv.index("--dir") + 1] if "--dir" in argv else ".harness"
    if argv and argv[0] == "mark":
        m = _lat.loop_marker_set(d, _now().isoformat(timespec="seconds"), _strflag(argv, "--label", "harness-run"))
        print(f"loop marked active: {m['label']} (started {m['started_ts']}). Arm a ceiling with "
              f"`run-budget.py start …` — until then the wired gate-budget denies every write (the arming gap is closed).")
        return 0
    if argv and argv[0] == "start":
        try:
            wc = _intflag(argv, "--wall-clock-s")
            deadline = (_now() + datetime.timedelta(seconds=wc)).isoformat(timespec="seconds") if wc else None
            now = _now().isoformat(timespec="seconds")
            b = _lat.run_budget_start(d, now, _intflag(argv, "--max-iterations"), _intflag(argv, "--max-cells"), deadline)
            _lat.loop_marker_set(d, now, _strflag(argv, "--label", "harness-run"))   # armed ⟹ marked
        except ValueError as e:
            print(f"run-budget start: {e}", file=sys.stderr)   # vacuous / non-positive / non-int caps → clean error, not a traceback
            return 2
        print(f"run-budget started: max-iterations={b['max_iterations']} max-cells={b['max_cells']} deadline={b['deadline_ts']} (loop marked active)")
        return 0
    if argv and argv[0] == "stop":
        cleared = _lat.run_budget_clear(d)
        marked = _lat.loop_marker_clear(d)
        print(f"loop stopped — budget {'cleared' if cleared else 'none'}, marker {'cleared' if marked else 'none'}.")
        return 0
    if argv and argv[0] == "clear":
        print("run-budget cleared (no active run)" if _lat.run_budget_clear(d) else "no active run-budget to clear")
        return 0
    if argv and argv[0] == "status":
        now = _now().isoformat(timespec="seconds")
        unb, detail = _lat.loop_unbudgeted(d, now)
        if _lat.loop_marker_active(d) and _lat.loop_marker_stale(d, now) and _lat.run_budget_load(d) is None:
            age_min = int((_lat.loop_marker_age_s(d, now) or 0) // 60)
            print(f"run-budget: STALE loop marker — marked active {age_min} min ago with no budget, past the "
                  f"{_lat.LOOP_TTL_S // 60}-min TTL. This is a crashed run's corpse, not a live loop; the gate no "
                  f"longer wedges writes. Clear it: `run-budget.py stop`.")
            return 3
        if unb:
            print(f"run-budget: ARMING GAP — {detail}. The wired gate-budget denies every write; arm a ceiling "
                  f"(`run-budget.py start …`) or end the loop (`run-budget.py stop`).")
            return 3
        ex, why, det = _lat.run_budget_exhausted(d, now)
        if not det.get("active"):
            print("run-budget: no active run." + ("  (loop marked active)" if _lat.loop_marker_active(d) else ""))
            return 2
        if ex:
            print(f"run-budget: EXHAUSTED — {why}. The wired gate-budget denies further worker writes; stop the loop.")
            return 1
        print(f"run-budget: active — {det.get('iterations', 0)} iteration(s), {det.get('cells', 0)} cell(s) so far"
              + (f", deadline {det['deadline_ts']}" if det.get('deadline_ts') else "")
              + (", loop marked" if _lat.loop_marker_active(d) else "") + ".")
        return 0
    print(__doc__.split("Usage:")[1].split("Stdlib")[0].strip(), file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
