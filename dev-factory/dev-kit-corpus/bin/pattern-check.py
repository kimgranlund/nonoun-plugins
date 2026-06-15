#!/usr/bin/env python3
"""pattern-check.py — the REAL verifier the corpus pattern adapter binds (rubric.system.pattern-quality).

This mechanizes the pattern-quality rubric's [gate] dimensions. validate.py runs it on a pattern cell's
asset and mints the signal from its EXIT STATUS (0 = all gates pass). It runs ONLY the [gate] dimensions —
generality and signal-to-noise are a calibrated critic's job. A pattern asset is a structured pattern
(JSON, or a ```json block inside a `.md`) carrying the Alexandrian pattern shape + its provenance:

    cell           : "pattern.<scope>.<slug>"
    context        : the situation it applies in (the retrieval index)
    forces         : what was in tension
    solution_shape | failure_mechanism : the transferable form (one of the two)
    consequences   : what it costs and what it buys
    provenance     : { ledger_refs: ["ledger:12", ...], refuted_when: "...", confirmed: bool }

Gate dimensions enforced here:
  schema-valid       — parses; cell id is pattern.* and excludes maturity; carries the pattern shape
  provenance-present — names >=1 ledger ref it was distilled from (untraceable otherwise)
  reusable           — keyed by context + transferable solution; >=2 refs OR an honest confirmed:false flag
  falsifiable        — states consequences AND a refutation condition (a claim a run cluster could disprove)

Usage:  pattern-check.py <asset-path>   |   pattern-check.py selftest
Exit 0 = all gates pass; 1 = a gate failed; 2 = bad invocation. Stdlib only; Python 3.8+.
"""
import json
import os
import re
import sys

_CELL_ID_RE = re.compile(r"^pattern\.(call|task|workflow|system|fleet)\.[a-z0-9]+(-[a-z0-9]+)*$")
_MATURITY = {"absent", "defined", "instantiated", "validated", "operating", "regenerating", "stale", "deprecated"}
_LEDGER_REF_RE = re.compile(r"^ledger:\d+$|^ledger:\d+\.\.\d+$")  # ledger:N or an event window ledger:N..M


def _load_pattern(path):
    raw = open(path, encoding="utf-8", errors="replace").read()
    if raw.lstrip().startswith("{"):
        return json.loads(raw)
    m = re.search(r"```json\s*(\{.*?\})\s*```", raw, re.DOTALL)
    if m:
        return json.loads(m.group(1))
    raise ValueError("pattern asset carries no structured pattern (expected JSON or a ```json block) — "
                     "a prose-only pattern cannot be mechanically gated for provenance")


def _gate_schema_valid(p):
    if not isinstance(p, dict):
        return False, "pattern is not a JSON object"
    cell = p.get("cell") or p.get("id")
    if not cell or not _CELL_ID_RE.match(str(cell)):
        return False, f"cell id {cell!r} is not a well-formed pattern.{{scope}}.{{slug}}"
    if str(cell).rsplit(".", 1)[-1] in _MATURITY:
        return False, f"cell id {cell!r} encodes maturity (identity must exclude state)"
    if not p.get("context"):
        return False, "pattern carries no `context` (patterns are retrieved by context)"
    if not (p.get("solution_shape") or p.get("failure_mechanism")):
        return False, "pattern carries neither solution_shape nor failure_mechanism (no transferable form)"
    return True, "schema-valid"


def _gate_provenance_present(p):
    prov = p.get("provenance") or {}
    refs = prov.get("ledger_refs") or []
    if not isinstance(refs, list) or not refs:
        return False, "no ledger_refs in provenance (untraceable: cannot check the precedent really recurred)"
    bad = [r for r in refs if not _LEDGER_REF_RE.match(str(r))]
    if bad:
        return False, f"malformed ledger refs (expected 'ledger:N' or 'ledger:N..M'): {bad}"
    return True, f"provenance names {len(refs)} ledger ref(s)"


def _gate_reusable(p):
    prov = p.get("provenance") or {}
    refs = prov.get("ledger_refs") or []
    if not p.get("context"):
        return False, "not keyed by context (cannot be retrieved as a reusable precedent)"
    confirmed = prov.get("confirmed")
    # Re-applied (>=2 distinct refs) => confirmed pattern. Cited once => must declare confirmed:false (a hypothesis).
    if len(set(map(str, refs))) >= 2:
        return True, "reusable: re-applied across >=2 distinct distillation refs (confirmed precedent)"
    if confirmed is False:
        return True, "reusable: a single-cite hypothesis honestly flagged confirmed:false (a compass prior, not a rule)"
    return False, ("cited from a single run without re-application and not flagged confirmed:false — "
                   "a one-off masquerading as a confirmed pattern (pollutes retrieval)")


def _gate_falsifiable(p):
    if not p.get("consequences"):
        return False, "no `consequences` (a pattern with no stated cost/benefit cannot be weighed)"
    prov = p.get("provenance") or {}
    refuted = p.get("refuted_when") or prov.get("refuted_when")
    if not refuted:
        return False, "no refutation condition (`refuted_when`) — an unfalsifiable pattern can never be demoted by evidence"
    return True, "falsifiable: states consequences + a refutation condition a run cluster could disprove"


GATES = [
    ("schema-valid", _gate_schema_valid),
    ("provenance-present", _gate_provenance_present),
    ("reusable", _gate_reusable),
    ("falsifiable", _gate_falsifiable),
]


def check(path):
    if not path or not os.path.isfile(path):
        return False, f"no asset at {path!r}"
    try:
        p = _load_pattern(path)
    except (json.JSONDecodeError, ValueError) as e:
        return False, f"schema-valid FAILED: {e}"
    failures, passes = [], []
    for name, fn in GATES:
        ok, msg = fn(p)
        (passes if ok else failures).append(f"{name}: {msg}")
    if failures:
        return False, "GATE FAILURES — " + " | ".join(failures)
    return True, "all pattern-quality gates pass — " + " | ".join(passes)


def selftest():
    import tempfile
    fails = []

    def expect(cond, msg):
        if not cond:
            fails.append(msg)

    good = {
        "cell": "pattern.system.spec-decomposition",
        "context": "a spec.system cell with independent sub-capabilities and a clean join",
        "forces": "parallelism vs merge-conflict risk",
        "solution_shape": "fan out sub-specs along real seams under orchestrator-workers",
        "consequences": "buys parallel width; costs an extra join step",
        "refuted_when": "decompositions following this cost MORE per signal than those that didn't, over >=5 runs",
        "provenance": {"ledger_refs": ["ledger:12", "ledger:31"], "confirmed": True},
    }
    with tempfile.TemporaryDirectory() as d:
        gpath = os.path.join(d, "good.json")
        json.dump(good, open(gpath, "w"))
        ok, msg = check(gpath)
        expect(ok, f"rejected a sound pattern: {msg}")

        # no ledger refs -> provenance-present fails
        noprov = json.loads(json.dumps(good))
        noprov["provenance"] = {"ledger_refs": [], "confirmed": True}
        p1 = os.path.join(d, "noprov.json")
        json.dump(noprov, open(p1, "w"))
        ok, msg = check(p1)
        expect(not ok and "provenance-present" in msg, f"accepted a provenance-less pattern: {msg}")

        # single ref, not flagged as hypothesis -> reusable fails
        oneoff = json.loads(json.dumps(good))
        oneoff["provenance"] = {"ledger_refs": ["ledger:7"]}  # one ref, no confirmed:false
        p2 = os.path.join(d, "oneoff.json")
        json.dump(oneoff, open(p2, "w"))
        ok, msg = check(p2)
        expect(not ok and "reusable" in msg, f"accepted a one-off as a confirmed pattern: {msg}")

        # single ref honestly flagged confirmed:false -> reusable passes (a hypothesis prior)
        hypo = json.loads(json.dumps(good))
        hypo["provenance"] = {"ledger_refs": ["ledger:7"], "confirmed": False}
        p2b = os.path.join(d, "hypo.json")
        json.dump(hypo, open(p2b, "w"))
        ok, msg = check(p2b)
        expect(ok, f"rejected an honestly-flagged single-cite hypothesis: {msg}")

        # no refutation condition -> falsifiable fails
        unfal = json.loads(json.dumps(good))
        unfal.pop("refuted_when")
        p3 = os.path.join(d, "unfal.json")
        json.dump(unfal, open(p3, "w"))
        ok, msg = check(p3)
        expect(not ok and "falsifiable" in msg, f"accepted an unfalsifiable pattern: {msg}")

        # malformed cell id -> schema-valid fails
        badcell = json.loads(json.dumps(good))
        badcell["cell"] = "pattern.system.spec-decomposition.validated"  # maturity in identity
        p4 = os.path.join(d, "badcell.json")
        json.dump(badcell, open(p4, "w"))
        ok, msg = check(p4)
        expect(not ok and "schema-valid" in msg, f"accepted a maturity-encoding cell id: {msg}")

        expect(not check(os.path.join(d, "missing.json"))[0], "accepted a missing asset")

    if fails:
        sys.stderr.write("pattern-check selftest: FAIL\n")
        for f in fails:
            sys.stderr.write(f"  - {f}\n")
        return 1
    print("pattern-check selftest: OK (a provenanced, reusable, falsifiable pattern passes; a provenance-less "
          "pattern, an unflagged one-off, an unfalsifiable pattern, and a maturity-encoding cell id each FAIL "
          "the right gate; an honestly-flagged hypothesis passes)")
    return 0


def main(argv):
    if not argv:
        sys.stderr.write("usage: pattern-check.py <asset-path> | selftest\n")
        return 2
    if argv[0] == "selftest":
        return selftest()
    ok, msg = check(argv[0])
    print(msg, file=sys.stdout if ok else sys.stderr)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
