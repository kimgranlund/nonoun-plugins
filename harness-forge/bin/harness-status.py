#!/usr/bin/env python3
"""harness-status.py — the operator dashboard: one cheap read of where the harness stands, no agent dispatch.

The council's observability finding (Charity, CV2): a running `/harness-run` was a black box, and `/harness-audit`
/ `/harness-council` are expensive multi-agent analyses, not a quick "is it healthy / what just happened." This
is the missing cheap signal — a single read over `.harness/` + the wiring + the run budget, printing:
  · cell maturity histogram + the frontier gap count
  · the active run budget (iterations/cells/deadline, or none)
  · the wiring verdict (and the kernel-drift check)
  · the gate-fire count (how many times the stop-gate denied a write — the bounding mechanism, no longer mute)
  · the last N ledger events (what just happened, incl. block/unblock decisions)

Usage:
  harness-status.py [--project DIR] [--harness-dir D] [-n N]
  harness-status.py selftest
Exit 0 (a read; never a gate). Stdlib only; Python 3.8+.
"""
import datetime
import os
import sys

_BIN = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _BIN)
import lattice as _lat     # noqa: E402
import wire as _wire       # noqa: E402


def render(project, hd=".harness", n=8):
    d = os.path.join(project, hd)
    out = [f"═══ harness-status · {os.path.abspath(project)} ═══"]
    try:
        lat = _lat.load(d)
    except OSError:
        return "\n".join(out + [f"  no lattice at {hd}/lattice.json — run /harness-seed first."])

    cells = lat.get("cells", [])
    hist = {}
    for c in cells:
        key = c.get("maturity", "?") + (" [blocked]" if c.get("blocked") else "")
        hist[key] = hist.get(key, 0) + 1
    out.append("  maturity: " + (", ".join(f"{k}×{v}" for k, v in sorted(hist.items())) or "(no cells)"))
    gaps = _lat.scan(lat)
    out.append(f"  frontier: {len(gaps)} open/stale gap(s) at scope {lat.get('frontier_scope','task')}"
               + (": " + ", ".join(_lat.cid(c) for c in gaps[:6]) if gaps else ""))
    blocked = [c for c in cells if c.get("blocked")]
    if blocked:
        out.append("  blocked:  " + ", ".join(f"{_lat.cid(c)} ({c.get('blocked_reason','?')})" for c in blocked))

    # the run budget (the global bound)
    ex, why, det = _lat.run_budget_exhausted(d, datetime.datetime.now().astimezone().isoformat(timespec="seconds"))
    if not det.get("active"):
        out.append("  run:      no active /harness-run budget")
    elif ex:
        out.append(f"  run:      EXHAUSTED — {why} (gate-budget is denying writes; stop the loop)")
    else:
        out.append(f"  run:      active — {det.get('iterations',0)} iteration(s), {det.get('cells',0)} cell(s)"
                   + (f", deadline {det['deadline_ts']}" if det.get('deadline_ts') else ""))

    # wiring + drift
    wired = _wire.check(project, hd, quiet=True)
    out.append(f"  wiring:   {'WIRED (gate-signal + gate-budget + feedback hooks)' if wired == 0 else 'NOT WIRED — the stop-gate is not installed (wire.py apply)'}")

    # the ledger: gate-fire count + the tail
    evs = _lat._read_ledger_events(d)
    denies = sum(1 for e in evs if e.get("actor") == "hook:gate-budget" and e.get("result") == "deny")
    out.append(f"  gate-fires: {denies} stop-gate denial(s) recorded" + (" (the loop hit its bound)" if denies else ""))
    out.append(f"  ledger:   {len(evs)} event(s); last {min(n, len(evs))}:")
    for e in evs[-n:]:
        out.append(f"     {e.get('operation','?'):9} {e.get('cell_id') or e.get('path') or '-':28} "
                   f"{e.get('result',''):8} {(e.get('rationale','') or '')[:48]}")
    return "\n".join(out)


def selftest():
    import tempfile
    fails = []
    def expect(cond, label):
        if not cond:
            fails.append(label)
    with tempfile.TemporaryDirectory() as proj:
        d = os.path.join(proj, ".harness")
        _lat.scaffold(d)
        _lat.save(d, _lat.seed_lattice("status-demo"))
        s = render(proj)
        for token in ("maturity:", "frontier:", "run:", "wiring:", "gate-fires:", "ledger:"):
            expect(token in s, f"status missing the {token} line")
        expect("no active" in s and "NOT WIRED" in s, "a fresh unseeded-wiring project should show no run + NOT WIRED")
        # after a block + a wire, the dashboard reflects both
        _wire.apply(proj, ".harness")
        lat = _lat.load(d); _lat.set_blocked(lat, "spec.task.first-slice", True, reason="no-progress"); _lat.save(d, lat)
        _lat._append_ledger_event(d, {"operation": "record", "actor": "hook:gate-budget", "result": "deny",
                                      "rationale": "blocked cell", "ts": "2026-06-13T12:00:00-07:00"})
        s2 = render(proj)
        expect("WIRED" in s2 and "[blocked]" in s2 and "1 stop-gate denial" in s2,
               "status did not reflect wired + blocked + a gate-fire")
    if fails:
        sys.stderr.write("harness-status selftest: FAIL\n")
        for f in fails:
            sys.stderr.write(f"  - {f}\n")
        return 1
    print("harness-status selftest: OK (one read renders maturity/frontier/run-budget/wiring/gate-fires/ledger; "
          "reflects blocked cells + denials + wiring state — the cheap operator signal, no agent dispatch)")
    return 0


def main(argv):
    if argv and argv[0] == "selftest":
        return selftest()
    project = argv[argv.index("--project") + 1] if "--project" in argv else "."
    hd = argv[argv.index("--harness-dir") + 1] if "--harness-dir" in argv else ".harness"
    n = int(argv[argv.index("-n") + 1]) if "-n" in argv else 8
    print(render(project, hd, n))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
