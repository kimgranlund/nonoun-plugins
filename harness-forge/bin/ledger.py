#!/usr/bin/env python3
"""ledger.py — append-only provenance, and the three loops it closes.

The ledger is the tensed layer: the append-only record of what occurred, what was decided, by whom, and
WHY (rationale alongside the what — future iterations will not have this context window). Its schema
belongs in the first slice because provenance cannot be retrofitted. A ledger nobody reads is storage,
not a layer; this script routes it back into the three downstream consumers that close three loops:

  - cost       — probe cost per layer/scope (tokens & iterations per prior signal) → the compass's value function
  - false-pass — false-pass rate (validate said pass, an independent check later failed) → the policy trust trajectory
  - distill    — recent event windows → pattern candidates for the regeneration loop

Append-only is enforced mechanically by the protected-path gate (workers are deny-on-write to ledger/);
this script only ever appends. State lives in `.harness/ledger/events.jsonl`.

See references/agentic-systems-foundations/layer-ledger.md and evals-and-verification.md.

Usage:
  ledger.py append '<json-event>' [--dir DIR]    # append one event (operation, actor, cell_id, result, rationale, cost)
  ledger.py query [--cell ID] [--op OP] [--dir DIR]
  ledger.py cost [--dir DIR]                      # probe cost per layer/scope
  ledger.py false-pass [--dir DIR]               # false-pass rate (gates autonomy: target < ~5%)
  ledger.py distill [--n N] [--dir DIR]          # the last N events as a distillation window
  ledger.py selftest
Stdlib only; Python 3.8+.
"""
import json
import os
import statistics
import sys

REQUIRED = ("operation", "actor")            # an entry attests an action by an actor; the rest is optional context


def _path(d):
    return os.path.join(d, "ledger", "events.jsonl")


def append(d, event):
    """Append one event as a JSONL line. Never rewrites existing lines (append-only)."""
    missing = [k for k in REQUIRED if k not in event]
    if missing:
        raise ValueError(f"event missing required field(s): {missing}")
    os.makedirs(os.path.join(d, "ledger"), exist_ok=True)
    with open(_path(d), "a", encoding="utf-8") as f:
        f.write(json.dumps(event, separators=(",", ":")) + "\n")


def read(d):
    p = _path(d)
    if not os.path.isfile(p):
        return []
    out = []
    for line in open(p, encoding="utf-8"):
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except ValueError:
                pass
    return out


def query(events, cell=None, op=None):
    return [e for e in events if (cell is None or e.get("cell_id") == cell) and (op is None or e.get("operation") == op)]


def probe_cost(events):
    """{layer: {scope: median iterations}} from validate events that carry a cost. Replaces estimates with evidence."""
    buckets = {}
    for e in events:
        if e.get("operation") != "validate":
            continue
        cidv = e.get("cell_id", "")
        parts = cidv.split(".")
        if len(parts) < 2:
            continue
        layer, scope = parts[0], parts[1]
        iters = (e.get("cost") or {}).get("iterations")
        if iters is None:
            continue
        buckets.setdefault(layer, {}).setdefault(scope, []).append(iters)
    return {l: {s: round(statistics.median(v)) for s, v in sc.items()} for l, sc in buckets.items()}


def false_pass_rate(events):
    """Fraction of validate=pass entries later contradicted by an INDEPENDENT check (a `refute` event on the same cell).
    The number that gates unattended autonomy (practitioner convention: < ~5%). Measured, never self-reported —
    and CRUCIALLY, `unmeasured` when no independent refuter exists: a 0.0% with zero refute events is the ABSENCE
    of bad news, not evidence of correctness, and must not read as an earned 0.0%. Returns (rate_or_None, fp, passes,
    refute_count); rate is None ⇒ unmeasured (register an independent refuter before trusting autonomy)."""
    passes = [e for e in events if e.get("operation") == "validate" and e.get("result") == "pass"]
    refutes = [e for e in events if e.get("operation") == "refute"]
    if not refutes:                                   # no independent check has ever run → the rate is not measured
        return None, 0, len(passes), 0
    if not passes:
        return 0.0, 0, 0, len(refutes)
    refuted_cells = {e.get("cell_id") for e in refutes}
    fp = sum(1 for e in passes if e.get("cell_id") in refuted_cells)
    return round(fp / len(passes), 4), fp, len(passes), len(refutes)


def distill_window(events, n=20):
    return events[-n:]


def selftest():
    import tempfile
    fails = []
    def expect(cond, label):
        if not cond:
            fails.append(label)
    with tempfile.TemporaryDirectory() as d:
        append(d, {"operation": "validate", "actor": "advancer", "cell_id": "spec.task.x", "result": "pass",
                   "rationale": "criteria executable", "cost": {"tokens": 800, "iterations": 2}})
        append(d, {"operation": "validate", "actor": "advancer", "cell_id": "spec.task.y", "result": "pass",
                   "rationale": "bound to rubric", "cost": {"tokens": 1200, "iterations": 4}})
        append(d, {"operation": "refute", "actor": "auditor", "cell_id": "spec.task.y",
                   "rationale": "independent check failed in production"})
        evs = read(d)
        expect(len(evs) == 3, f"append/read round-trip wrong: {len(evs)} events")
        expect(len(query(evs, op="validate")) == 2, "query by op failed")
        expect(len(query(evs, cell="spec.task.x")) == 1, "query by cell failed")

        cost = probe_cost(evs)
        expect(cost.get("spec", {}).get("task") == 3, f"probe cost (median of 2,4) wrong: {cost}")

        rate, fp, tot, refn = false_pass_rate(evs)
        expect(fp == 1 and tot == 2 and rate == 0.5 and refn == 1, f"false-pass (1 of 2) wrong: {rate} {fp}/{tot}")
        # unmeasured when no refute source exists — two passes, zero refutes → None, NOT a misleading 0.0%
        no_refute = [e for e in evs if e.get("operation") != "refute"]
        urate, _, utot, urefn = false_pass_rate(no_refute)
        expect(urate is None and utot == 2 and urefn == 0, f"false-pass should be unmeasured with no refuter, got {urate}")

        # append-only: a second append must not rewrite the first line.
        first_line = open(_path(d), encoding="utf-8").readline()
        append(d, {"operation": "record", "actor": "scribe"})
        expect(open(_path(d), encoding="utf-8").readline() == first_line, "append rewrote an existing line (not append-only)")

        # a missing required field is rejected (an entry must attest an actor).
        try:
            append(d, {"cell_id": "x"})
            expect(False, "append accepted an event with no operation/actor")
        except ValueError:
            pass

    if fails:
        sys.stderr.write("ledger selftest: FAIL\n")
        for f in fails:
            sys.stderr.write(f"  - {f}\n")
        return 1
    print("ledger selftest: OK (append-only round-trip; query; probe-cost median; false-pass rate; rejects entry with no actor)")
    return 0


def _dir(argv):
    return argv[argv.index("--dir") + 1] if "--dir" in argv else ".harness"


def _flag(argv, name, default=None):
    return argv[argv.index(name) + 1] if name in argv and argv.index(name) + 1 < len(argv) else default


def main(argv):
    if argv and argv[0] == "selftest":
        return selftest()
    d = _dir(argv)
    if argv and argv[0] == "append":
        try:
            append(d, json.loads(argv[1]))
        except (IndexError, ValueError) as e:
            print(f"append: {e}", file=sys.stderr)
            return 2
        print(f"appended → {_path(d)}")
        return 0
    evs = read(d)
    if argv and argv[0] == "query":
        for e in query(evs, cell=_flag(argv, "--cell"), op=_flag(argv, "--op")):
            print(f"  {e.get('operation','?'):10} {e.get('actor','?'):11} {e.get('cell_id','-')}  {e.get('result','')}")
        return 0
    if argv and argv[0] == "cost":
        print(json.dumps(probe_cost(evs), indent=2))
        return 0
    if argv and argv[0] == "false-pass":
        rate, fp, tot, refn = false_pass_rate(evs)
        if rate is None:
            print(f"false-pass rate: UNMEASURED — {tot} pass(es), 0 independent `refute` events. A 0% with no refuter is "
                  f"the absence of bad news, not evidence; register an independent refuter before trusting autonomy.")
        else:
            print(f"false-pass rate: {rate:.1%} ({fp}/{tot}, {refn} refute source(s))  — autonomy gate: < ~5% with zero reward-hacking incidents")
        return 0
    if argv and argv[0] == "distill":
        for e in distill_window(evs, int(_flag(argv, "--n", "20"))):
            print(f"  {e.get('operation','?'):10} {e.get('cell_id','-')}  {e.get('rationale','')}")
        return 0
    print(__doc__.split("Usage:")[1].split("Stdlib")[0].strip(), file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
