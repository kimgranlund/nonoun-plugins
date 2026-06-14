#!/usr/bin/env python3
"""harness-status.py — the operator dashboard: one cheap read of where the harness stands, no agent dispatch.

The council's observability finding (Charity, CV2): a running `/harness-run` was a black box, and `/harness-audit`
/ `/harness-council` are expensive multi-agent analyses, not a quick "is it healthy / what just happened." This
is the missing cheap signal — a single read over `.agents/harness/` + the wiring + the run budget, printing:
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


def render(project, hd=".agents/harness", n=8):
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

    # the run budget (the global bound) — show X/Y, not just the numerator, so an operator sees the cliff BEFORE it
    now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    ex, why, det = _lat.run_budget_exhausted(d, now)
    unb, _ = _lat.loop_unbudgeted(d, now)
    marked = _lat.loop_marker_active(d)
    stale_marker = marked and _lat.loop_marker_stale(d, now) and _lat.run_budget_load(d) is None
    if stale_marker:
        # a crashed run left a corpse marker (older than the TTL) — surfaced so the operator can clear it (Charity).
        age_min = int((_lat.loop_marker_age_s(d, now) or 0) // 60)
        out.append(f"  run:      ⚠ STALE loop marker — marked active {age_min} min ago, no budget, past the "
                   f"{_lat.LOOP_TTL_S // 60}-min TTL: a crashed run, not a live loop. The gate no longer wedges writes; "
                   f"clear the corpse with `run-budget.py stop`.")
    elif unb:
        # the I-9 state, now DETECTABLE (not a generic warning): a LIVE loop is marked active but un-budgeted, so the
        # wired gate-budget is denying every write. The arming gap fails closed; the operator sees exactly why.
        out.append("  run:      ⚠ ARMING GAP — a loop is MARKED ACTIVE but no budget is armed; gate-budget is denying "
                   "every write. Arm a ceiling (`run-budget.py start --max-cells N --max-iterations M`) or end it (`run-budget.py stop`).")
    elif not det.get("active"):
        out.append("  run:      no active run budget — the loop is idle (manual edits + /harness-advance are free; "
                   "/harness-run will `mark` then `start` to bound itself)." if not marked else
                   "  run:      ⚠ loop marked active — arm a budget or `run-budget.py stop`.")
    elif ex:
        out.append(f"  run:      ⚠ EXHAUSTED — {why}; gate-budget is denying every write. Stop the loop / clear the run.")
    else:
        mi, mc = det.get("max_iterations"), det.get("max_cells")
        i_s = f"{det.get('iterations',0)}/{mi} iters" if mi else f"{det.get('iterations',0)} iters"
        c_s = f"{det.get('cells',0)}/{mc} cells" if mc else f"{det.get('cells',0)} cells"
        out.append(f"  run:      active — {i_s} · {c_s}" + (f" · deadline {det['deadline_ts']}" if det.get('deadline_ts') else ""))

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
        d = os.path.join(proj, ".agents/harness")
        _lat.scaffold(d)
        _lat.save(d, _lat.seed_lattice("status-demo"))
        s = render(proj)
        for token in ("maturity:", "frontier:", "run:", "wiring:", "gate-fires:", "ledger:"):
            expect(token in s, f"status missing the {token} line")
        # a fresh project (no budget, NO marker) is idle, not alarming — manual edits / /harness-advance are free
        expect("no active run budget" in s and "idle" in s and "NOT WIRED" in s,
               "a fresh unmarked project must read as idle (not a false UNBOUNDED alarm), + show NOT WIRED")
        # I-9: MARK a FRESH loop with no budget → the dashboard shows the ARMING GAP (the gate is denying every write)
        import datetime as _dt
        fresh = _dt.datetime.now().astimezone().isoformat(timespec="seconds")
        _lat.loop_marker_set(d, fresh, label="harness-run")
        expect("ARMING GAP" in render(proj) and "denying every write" in render(proj),
               "a live marked-but-unbudgeted loop must surface the arming gap")
        # a STALE marker (older than the TTL) shows STALE, not ARMING GAP — the crash-wedge fix (Charity C1)
        old = (_dt.datetime.now().astimezone() - _dt.timedelta(seconds=_lat.LOOP_TTL_S + 120)).isoformat(timespec="seconds")
        _lat.loop_marker_set(d, old, label="crashed")
        expect("STALE loop marker" in render(proj), "an old marker must surface as STALE (the gate no longer wedges)")
        _lat.loop_marker_clear(d)
        # an active budget renders X/Y (the caps, not just the numerator) so the operator sees the cliff before it
        _lat.run_budget_start(d, "2026-06-13T12:00:00-07:00", max_iterations=8, max_cells=4)
        expect("0/8 iters" in render(proj) and "0/4 cells" in render(proj), "the run line must show X/Y caps, not just the count")
        _lat.run_budget_clear(d)
        # after a block + a wire, the dashboard reflects both
        _wire.apply(proj, ".agents/harness")
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
    hd = argv[argv.index("--harness-dir") + 1] if "--harness-dir" in argv else ".agents/harness"
    n = int(argv[argv.index("-n") + 1]) if "-n" in argv else 8
    print(render(project, hd, n))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
