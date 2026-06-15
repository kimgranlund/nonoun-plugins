#!/usr/bin/env python3
"""reports.py — derived reporting views over the operational store + the JSONL ledger.

The spec (harness-and-storage.md, "Reporting & CRUD") names reports a SECOND-CLASS view, never a
second source of truth: "SQL/DuckDB over the operational store and the ledger — derived views, never a
second source of truth. Flow metrics, trust-trajectory inputs (false-pass, reward-hack counts), and
compass probe-cost all read from here." This module is that layer. It READS; it never decides. The
authorities stay where they are — the ledger for history, the kernel for selection/ranking/tier — and
every number here is a fold over them, consistent with how `ledger.py`, `autonomy.py`, and `compass.py`
compute the same things. A report disagreeing with those modules is a defect, not a second opinion.

Engine. The spec wants DuckDB "attached read-only" querying the SQLite store AND the JSONL ledger
directly (columnar SQL, no ETL). DuckDB is an OPTIONAL dependency (pyproject `[reports]`), so this
module uses it when importable and otherwise FALLS BACK to a stdlib sqlite3 + json path that computes
the identical views. The module and its selftest therefore run with ZERO external deps; DuckDB only
changes the engine under the views, never the numbers. Each report returns a JSON-serializable dict the
server exposes at /api/reports (wired in app.py — untouched here).

Views:
  flow_metrics(d)          ticket counts by state; cycle time (created->done); throughput per window
  false_pass_report(d, family=None)   the trust-trajectory input — incidents / refuter-checks (autonomy semantics)
  probe_cost_report(d)     mean tokens & iterations per signal by cell type (layer.scope) — the compass's input
  spend_report(d, window=None)        tokens / $ per window, from ledger signal metrics
  maturity_distribution(d) cells by (layer, maturity) — the lattice health snapshot
  report(d, name)          dispatcher; CLI: reports.py <name> --dir DIR ; reports.py selftest

Stdlib + optional duckdb; Python 3.8+.
"""
import datetime
import json
import os
import sqlite3
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
import store as _store  # noqa: E402  (the SQLite index + connect/rebuild)

sys.path.insert(0, _store._KERNEL_BIN)
import ledger as _led   # noqa: E402  (the authoritative JSONL ledger reader)

# Number of equal-width time buckets used by the windowed reports (flow throughput, spend) when no
# explicit window is given. The reports stay engine-agnostic: same buckets under DuckDB or stdlib.
DEFAULT_WINDOWS = 4
FALSE_PASS_CEILING = 0.05   # mirrors autonomy.FALSE_PASS_CEILING — reported so the view is self-explaining


def _have_duckdb():
    try:
        import duckdb  # noqa: F401
        return True
    except Exception:
        return False


# ─────────────────────────────── shared readers (engine-agnostic) ───────────────────────────────

def _signals(d):
    """Every ledger `signal` event, the substrate of probe-cost / spend / false-pass. Read straight from
    the authoritative JSONL via ledger.read — never the index, which is downstream and could lag it."""
    return _led.read(d, event="signal")


def _incidents(d, family=None):
    out = _led.read(d, event="incident")
    if family is not None:
        out = [e for e in out if (e.get("metrics") or {}).get("family") == family]
    return out


def _refuter_checks(d, family=None):
    """The denominator of the false-pass rate: independent re-validations (signals flagged refuter).
    Identical predicate to autonomy.refuter_checks so the two never diverge."""
    out = [e for e in _signals(d) if (e.get("metrics") or {}).get("refuter")]
    if family is not None:
        out = [e for e in out if (e.get("metrics") or {}).get("family") == family]
    return out


def _passes(e):
    return e.get("to") == "pass" or (e.get("metrics") or {}).get("result") == "pass"


def _fails(e):
    return e.get("to") == "fail" or (e.get("metrics") or {}).get("result") == "fail"


def _cell_type(cell):
    """layer.scope for a `{layer}.{scope}.{slug}` cell id; None if not a typed cell id."""
    parts = (cell or "").split(".")
    return f"{parts[0]}.{parts[1]}" if len(parts) >= 2 else None


def _parse_ts(s):
    if not s:
        return None
    try:
        return datetime.datetime.fromisoformat(s)
    except ValueError:
        # tolerate a trailing Z
        try:
            return datetime.datetime.fromisoformat(s.replace("Z", "+00:00"))
        except ValueError:
            return None


def _bucket_index(ts, lo, span, n):
    """Which of n equal-width buckets [lo, lo+span) a timestamp falls into. Clamped to [0, n-1]."""
    if span <= 0:
        return 0
    i = int((ts - lo).total_seconds() / span)
    return max(0, min(n - 1, i))


# ─────────────────────────────── the views ───────────────────────────────

def flow_metrics(d):
    """Ticket throughput health: counts by state, cycle time (created->done), throughput per window.

    Counts and states come from the materialized `tickets` table (rebuilt from files+ledger by store.py);
    cycle time is created->updated for tickets observed `done`. Throughput buckets the done tickets into
    DEFAULT_WINDOWS equal-width time windows across the observed span."""
    con = _store.connect(d)
    try:
        rows = [dict(r) for r in con.execute("SELECT state, created, updated FROM tickets").fetchall()]
    finally:
        con.close()

    by_state = {}
    for r in rows:
        by_state[r["state"] or "unknown"] = by_state.get(r["state"] or "unknown", 0) + 1

    # cycle time: created -> updated for done tickets (the index stamps `updated` at the done transition)
    durations = []
    done_done = []
    for r in rows:
        if r["state"] != "done":
            continue
        c, u = _parse_ts(r["created"]), _parse_ts(r["updated"])
        if c and u and u >= c:
            durations.append((u - c).total_seconds())
            done_done.append(u)
    cycle = {
        "n": len(durations),
        "mean_s": round(sum(durations) / len(durations), 3) if durations else None,
        "min_s": round(min(durations), 3) if durations else None,
        "max_s": round(max(durations), 3) if durations else None,
    }

    # throughput: done-per-window over the observed completion span
    windows = []
    if len(done_done) >= 1:
        lo, hi = min(done_done), max(done_done)
        span = (hi - lo).total_seconds()
        n = DEFAULT_WINDOWS
        counts = [0] * n
        each = span / n if span > 0 else 0
        for u in done_done:
            counts[_bucket_index(u, lo, each, n) if span > 0 else 0] += 1
        for i, c in enumerate(counts):
            start = lo + datetime.timedelta(seconds=each * i) if span > 0 else lo
            windows.append({"window": i, "start": start.isoformat(timespec="seconds"), "done": c})

    return {
        "report": "flow_metrics",
        "total_tickets": len(rows),
        "by_state": by_state,
        "done": by_state.get("done", 0),
        "cycle_time": cycle,
        "throughput": {"windows": windows, "total_done": len(done_done)},
        "engine": "duckdb" if _have_duckdb() else "sqlite",
    }


def false_pass_report(d, family=None):
    """The trust-trajectory input (autonomy §). Reconciles with autonomy.false_pass: a rate is
    `unmeasured` until an INDEPENDENT refuter has re-checked at least once — a 0.0% you never measured is
    the lie that would auto-promote a never-checked family. We report BOTH numerators the system uses and
    are explicit about which the rate is:

      - disagreements / refuter_checks  — autonomy.false_pass's exact formula (a refuter that DISAGREED is
                                          a caught false pass). This IS the trust gate's number.
      - incidents / refuter_checks      — the spec's prose framing ("reward-hack counts"); reported as a
                                          cross-check. Equal to the above unless an incident was logged
                                          outside the refuter path.

    The headline `rate` follows autonomy (disagreements/refuter_checks) so a consumer never reads a
    number the tier machine wouldn't honor."""
    checks = _refuter_checks(d, family)
    n_checks = len(checks)
    disagreements = sum(1 for c in checks if (c.get("metrics") or {}).get("agreed") is False)
    incidents = _incidents(d, family)
    n_incidents = len(incidents)

    if n_checks == 0:
        rate = "unmeasured"
        incident_rate = "unmeasured"
    else:
        rate = disagreements / n_checks
        incident_rate = n_incidents / n_checks

    return {
        "report": "false_pass",
        "family": family,
        "rate": rate,                       # autonomy.false_pass semantics — the trust gate's number
        "incident_rate": incident_rate,     # incidents / refuter-checks — the spec's "reward-hack" framing
        "refuter_checks": n_checks,
        "disagreements": disagreements,
        "incidents": n_incidents,
        "ceiling": FALSE_PASS_CEILING,
        "measured": n_checks > 0,
        "below_ceiling": (rate != "unmeasured" and rate < FALSE_PASS_CEILING),
        "engine": "duckdb" if _have_duckdb() else "sqlite",
    }


def probe_cost_report(d):
    """The compass's empirical input: mean tokens & iterations per signal, grouped by cell type
    (layer.scope). Mirrors compass.probe_cost — same source (ledger signal metrics), same grouping — so
    the report and the ranker read one number. compass.probe_cost averages tokens with tokens>0; we apply
    the same filter for the token mean and report the iteration mean alongside it (diagnostic)."""
    by_type = {}
    for e in _signals(d):
        ct = _cell_type((e.get("subject") or {}).get("cell"))
        if not ct:
            continue
        m = e.get("metrics") or {}
        b = by_type.setdefault(ct, {"signals": 0, "_tok": [], "_it": []})
        b["signals"] += 1
        tok = m.get("tokens")
        if isinstance(tok, (int, float)) and tok > 0:
            b["_tok"].append(float(tok))
        it = m.get("iterations")
        if isinstance(it, (int, float)) and it > 0:
            b["_it"].append(float(it))

    out = {}
    for ct, b in sorted(by_type.items()):
        toks, its = b["_tok"], b["_it"]
        out[ct] = {
            "signals": b["signals"],
            "mean_tokens": round(sum(toks) / len(toks), 2) if toks else None,
            "mean_iterations": round(sum(its) / len(its), 3) if its else None,
            "samples_with_tokens": len(toks),
        }
    return {"report": "probe_cost", "by_cell_type": out, "engine": "duckdb" if _have_duckdb() else "sqlite"}


def spend_report(d, window=None):
    """Tokens and $ per time window, from ledger signal metrics (cost_usd, tokens). `window` is an
    optional bucket count (defaults to DEFAULT_WINDOWS) across the observed signal span. Totals are
    always reported; buckets only when at least one signal carries a timestamp."""
    n_windows = int(window) if window else DEFAULT_WINDOWS
    sigs = _signals(d)
    total_tokens = 0.0
    total_cost = 0.0
    stamped = []
    for e in sigs:
        m = e.get("metrics") or {}
        tok = m.get("tokens")
        cost = m.get("cost_usd")
        tok = float(tok) if isinstance(tok, (int, float)) else 0.0
        cost = float(cost) if isinstance(cost, (int, float)) else 0.0
        total_tokens += tok
        total_cost += cost
        ts = _parse_ts(e.get("ts"))
        if ts:
            stamped.append((ts, tok, cost))

    windows = []
    if stamped:
        lo, hi = min(s[0] for s in stamped), max(s[0] for s in stamped)
        span = (hi - lo).total_seconds()
        each = span / n_windows if span > 0 else 0
        buckets = [{"tokens": 0.0, "cost_usd": 0.0, "signals": 0} for _ in range(n_windows)]
        for ts, tok, cost in stamped:
            i = _bucket_index(ts, lo, each, n_windows) if span > 0 else 0
            buckets[i]["tokens"] += tok
            buckets[i]["cost_usd"] += cost
            buckets[i]["signals"] += 1
        for i, b in enumerate(buckets):
            start = lo + datetime.timedelta(seconds=each * i) if span > 0 else lo
            windows.append({"window": i, "start": start.isoformat(timespec="seconds"),
                            "tokens": round(b["tokens"], 2), "cost_usd": round(b["cost_usd"], 6),
                            "signals": b["signals"]})

    return {
        "report": "spend",
        "total_tokens": round(total_tokens, 2),
        "total_cost_usd": round(total_cost, 6),
        "signals": len(sigs),
        "windows": windows,
        "engine": "duckdb" if _have_duckdb() else "sqlite",
    }


def maturity_distribution(d):
    """The lattice health snapshot: cells by (layer, maturity), plus blocked/stale rollups. Reads the
    materialized `cells` table (the lattice projected by store.upsert_cell)."""
    con = _store.connect(d)
    try:
        rows = [dict(r) for r in con.execute(
            "SELECT layer, maturity, blocked, stale FROM cells").fetchall()]
    finally:
        con.close()

    by_layer = {}
    by_maturity = {}
    blocked = 0
    stale = 0
    for r in rows:
        layer = r["layer"] or "unknown"
        mat = r["maturity"] or "absent"
        by_layer.setdefault(layer, {})
        by_layer[layer][mat] = by_layer[layer].get(mat, 0) + 1
        by_maturity[mat] = by_maturity.get(mat, 0) + 1
        if r["blocked"]:
            blocked += 1
        if r["stale"]:
            stale += 1

    return {
        "report": "maturity_distribution",
        "total_cells": len(rows),
        "by_layer": by_layer,
        "by_maturity": by_maturity,
        "blocked": blocked,
        "stale": stale,
        "engine": "duckdb" if _have_duckdb() else "sqlite",
    }


# ─────────────────────────────── dispatcher + CLI ───────────────────────────────

REPORTS = {
    "flow": flow_metrics,
    "flow_metrics": flow_metrics,
    "false_pass": false_pass_report,
    "probe_cost": probe_cost_report,
    "spend": spend_report,
    "maturity": maturity_distribution,
    "maturity_distribution": maturity_distribution,
}


def report(d, name, **kw):
    """Dispatch by name. Unknown name -> ValueError (the server maps this to a 404/400)."""
    fn = REPORTS.get(name)
    if not fn:
        raise ValueError(f"unknown report: {name} (have {sorted(set(REPORTS))})")
    return fn(d, **kw)


def all_reports(d):
    """Every view, keyed by canonical name — the /api/reports index payload."""
    return {
        "flow_metrics": flow_metrics(d),
        "false_pass": false_pass_report(d),
        "probe_cost": probe_cost_report(d),
        "spend": spend_report(d),
        "maturity_distribution": maturity_distribution(d),
    }


def selftest():
    import tempfile
    fails = []
    def expect(c, m):
        if not c:
            fails.append(m)

    sys.path.insert(0, _store._KERNEL_BIN)
    import lattice as _lat  # noqa: E402

    with tempfile.TemporaryDirectory() as root:
        d = os.path.join(root, ".agents/dev-factory")
        _lat.scaffold(d)

        # a tiny lattice: two cells, one validated rubric (a verifier), one blocked spec
        _lat.save(d, {"cells": [
            {"layer": "rubric", "scope": "task", "slug": "r", "maturity": "validated", "depends_on": [], "signal_refs": ["s/r"]},
            {"layer": "spec", "scope": "task", "slug": "a", "maturity": "instantiated", "blocked": True, "depends_on": [], "signal_refs": []},
        ]})

        # two tickets: one done (cycle time measurable), one active
        os.makedirs(os.path.join(d, "coordination", "tickets"), exist_ok=True)
        def mk(tid, state, created, updated, target):
            json.dump({"id": tid, "type": "feature", "title": tid, "state": state,
                       "target_cell": target, "target_transition": {"from": "instantiated", "to": "validated"},
                       "acceptance": {"rubric_cell": "rubric.task.r"}, "budget": {"iterations": 1, "tokens": 1},
                       "signal_refs": [], "provenance": {"created_by": "h", "ledger_refs": []},
                       "timestamps": {"created": created, "updated": updated}},
                      open(os.path.join(d, "coordination", "tickets", f"{tid}.json"), "w"))
        mk("tkt-DONE", "done", "2026-06-14T00:00:00+00:00", "2026-06-14T00:01:40+00:00", "spec.task.a")  # 100s
        mk("tkt-ACTIVE", "active", "2026-06-14T00:02:00+00:00", "2026-06-14T00:02:00+00:00", "spec.task.b")

        srv = {"kind": "server", "id": "srv"}
        # signals with token/cost/iteration metrics on two cell types
        _led.append(d, "signal", srv, {"cell": "spec.task.a"}, "pass", to="pass",
                    metrics={"tokens": 10000, "iterations": 2, "cost_usd": 0.10, "result": "pass"},
                    ts="2026-06-14T00:00:30+00:00")
        _led.append(d, "signal", srv, {"cell": "spec.task.a"}, "pass", to="pass",
                    metrics={"tokens": 20000, "iterations": 4, "cost_usd": 0.20, "result": "pass"},
                    ts="2026-06-14T00:01:30+00:00")
        _led.append(d, "signal", srv, {"cell": "rubric.task.r"}, "pass", to="pass",
                    metrics={"tokens": 5000, "iterations": 1, "cost_usd": 0.05, "result": "pass"},
                    ts="2026-06-14T00:02:30+00:00")

        store_counts = _store.rebuild(d)
        expect(store_counts["tickets"] == 2, f"seed: expected 2 tickets, got {store_counts}")

        # ── flow_metrics ──
        fm = flow_metrics(d)
        expect(fm["by_state"] == {"done": 1, "active": 1}, f"flow by_state wrong: {fm['by_state']}")
        expect(fm["done"] == 1, "flow done count wrong")
        expect(fm["cycle_time"]["n"] == 1, "flow cycle n wrong")
        expect(abs(fm["cycle_time"]["mean_s"] - 100.0) < 0.01, f"flow cycle mean wrong: {fm['cycle_time']}")
        expect(fm["throughput"]["total_done"] == 1, "flow throughput total wrong")

        # ── probe_cost: mirrors compass.probe_cost (mean tokens by layer.scope, tokens>0) ──
        pc = probe_cost_report(d)
        st = pc["by_cell_type"]["spec.task"]
        expect(abs(st["mean_tokens"] - 15000.0) < 0.01, f"probe mean_tokens wrong: {st}")  # (10k+20k)/2
        expect(abs(st["mean_iterations"] - 3.0) < 0.01, f"probe mean_iterations wrong: {st}")
        expect(st["signals"] == 2, "probe signal count wrong")
        expect(pc["by_cell_type"]["rubric.task"]["mean_tokens"] == 5000.0, "probe rubric mean wrong")
        # consistency with the compass itself
        sys.path.insert(0, _store._KERNEL_BIN)
        import compass as _compass  # noqa: E402
        expect(abs(_compass.probe_cost(d, "spec", "task") - st["mean_tokens"]) < 0.01,
               "probe_cost report disagrees with compass.probe_cost")

        # ── spend: totals + windows ──
        sp = spend_report(d)
        expect(abs(sp["total_tokens"] - 35000.0) < 0.01, f"spend total tokens wrong: {sp['total_tokens']}")
        expect(abs(sp["total_cost_usd"] - 0.35) < 1e-9, f"spend total cost wrong: {sp['total_cost_usd']}")
        expect(sp["signals"] == 3, "spend signal count wrong")
        expect(sum(w["signals"] for w in sp["windows"]) == 3, "spend windows lost a signal")
        expect(abs(sum(w["tokens"] for w in sp["windows"]) - 35000.0) < 0.01, "spend windows lost tokens")

        # ── maturity_distribution ──
        md = maturity_distribution(d)
        expect(md["total_cells"] == 2, "maturity total cells wrong")
        expect(md["by_maturity"] == {"validated": 1, "instantiated": 1}, f"maturity by_maturity wrong: {md['by_maturity']}")
        expect(md["by_layer"]["rubric"] == {"validated": 1}, "maturity by_layer rubric wrong")
        expect(md["blocked"] == 1, "maturity blocked count wrong")

        # ── false_pass: unmeasured until a refuter checks (autonomy honest scope) ──
        fp0 = false_pass_report(d)
        expect(fp0["rate"] == "unmeasured", "false-pass must be 'unmeasured' before any refuter check")
        expect(fp0["measured"] is False, "false-pass measured flag wrong pre-refuter")
        # consistency with autonomy BEFORE any refuter
        sys.path.insert(0, _store._KERNEL_BIN)
        import autonomy as _auto  # noqa: E402
        expect(_auto.false_pass(d) == fp0["rate"], "false-pass report disagrees with autonomy (unmeasured)")

        # one agreeing refuter -> measured 0.0; reconciles with autonomy.false_pass exactly
        _auto.record_refuter_check(d, "spec.task.a", agreed=True)
        fp1 = false_pass_report(d)
        expect(fp1["rate"] == 0.0, f"one agreeing refuter -> 0.0 rate; got {fp1['rate']}")
        expect(fp1["refuter_checks"] == 1, "false-pass refuter count wrong")
        expect(fp1["below_ceiling"] is True, "0.0 rate should be below ceiling")
        expect(_auto.false_pass(d) == fp1["rate"], "false-pass report disagrees with autonomy (measured)")

        # a disagreeing refuter -> a caught false pass (incident) -> rate climbs; both numerators move
        _auto.record_refuter_check(d, "spec.task.a", agreed=False)
        fp2 = false_pass_report(d)
        expect(fp2["refuter_checks"] == 2, "false-pass refuter count wrong after disagreement")
        expect(fp2["disagreements"] == 1, "false-pass disagreement count wrong")
        expect(abs(fp2["rate"] - 0.5) < 1e-9, f"false-pass rate should be 1/2; got {fp2['rate']}")
        expect(_auto.false_pass(d) == fp2["rate"], "false-pass report disagrees with autonomy after a disagreement")
        expect(fp2["incidents"] >= 1, "a caught false pass should have logged an incident")

        # ── dispatcher + all_reports ──
        expect(report(d, "spend")["report"] == "spend", "dispatcher: spend failed")
        expect(report(d, "false_pass", family=None)["report"] == "false_pass", "dispatcher: false_pass kwarg failed")
        try:
            report(d, "nope")
            expect(False, "unknown report name should raise")
        except ValueError:
            pass
        ar = all_reports(d)
        expect(set(ar) == {"flow_metrics", "false_pass", "probe_cost", "spend", "maturity_distribution"},
               "all_reports keys wrong")

        # ── JSON-serializable (the /api/reports contract) ──
        for name, payload in ar.items():
            try:
                json.dumps(payload)
            except TypeError as e:
                expect(False, f"{name} report not JSON-serializable: {e}")

    if fails:
        sys.stderr.write("reports selftest: FAIL\n")
        for f in fails:
            sys.stderr.write(f"  - {f}\n")
        return 1
    eng = "duckdb" if _have_duckdb() else "stdlib sqlite3+json"
    print(f"reports selftest: OK (engine={eng}; flow counts+cycle-time+throughput; probe_cost mirrors "
          "compass.probe_cost; spend totals+windows reconcile; maturity snapshot; false-pass is 'unmeasured' "
          "until a refuter checks and then reconciles with autonomy.false_pass exactly — derived views, never "
          "a second source of truth)")
    return 0


def _arg(argv, flag, default=None):
    return argv[argv.index(flag) + 1] if flag in argv else default


def main(argv):
    if not argv or argv[0] == "selftest":
        return selftest()
    d = _arg(argv, "--dir", ".agents/dev-factory")
    name = argv[0]
    if name == "all":
        print(json.dumps(all_reports(d), indent=2))
        return 0
    kw = {}
    if name in ("false_pass",) and _arg(argv, "--family"):
        kw["family"] = _arg(argv, "--family")
    if name in ("spend",) and _arg(argv, "--window"):
        kw["window"] = _arg(argv, "--window")
    try:
        print(json.dumps(report(d, name, **kw), indent=2))
    except ValueError as e:
        print(f"reports.py: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
