#!/usr/bin/env python3
"""distill.py — the deterministic half of regeneration: pattern candidates from the ledger (TDD §10.3, §19).

The regeneration loop closes the system: operate → ledger → distill → patterns → upstream → spec. The
JUDGMENT (is this candidate a real, reusable pattern? what spec revision does it imply?) is the
pattern-distiller / spec-regenerator agents'. The SCAN — finding the recurring signatures in the ledger
window — is computation, and lives here (the routing law). Every candidate carries provenance (the
ledger_refs it was distilled from); a pattern without provenance is a guess, and the next iteration
won't have this context window to reconstruct it from.

It surfaces three signature kinds:
  - success   : a cell type that repeatedly validated → a "what works" candidate for the pattern layer.
  - failure   : a cell type with repeated blocks / no-progress → a "what to revise" candidate (a spec/
                rubric smell the spec-regenerator turns into an upstream proposal).
  - probe-cost: a cell type whose measured cost is an outlier → a compass-calibration candidate.

Usage:
  distill.py scan --dir DIR [--since ISO] [--min-occurrences N]
  distill.py selftest
Stdlib only; Python 3.8+.
"""
import json
import os
import sys
from collections import defaultdict

_ROOT = os.environ.get("CLAUDE_PLUGIN_ROOT") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "bin"))
import ledger as _led  # noqa: E402


def _cell_type(cell_id):
    parts = (cell_id or "").split(".")
    return ".".join(parts[:2]) if len(parts) >= 2 else cell_id


def _ref(i):
    return f"ledger:{i}"


def distill_patterns(d, since=None, min_occurrences=2):
    """Return pattern candidates [{kind, signature, cell_type, occurrences, evidence:[ledger_refs]}].
    Deterministic — pure counting over the ledger window. The agent decides which candidates are real."""
    events = _led.read(d, since=since)
    # index by 1-based position so provenance refs match ledger.append's scheme
    indexed = list(enumerate(_led.read(d), start=1))
    if since:
        indexed = [(i, e) for i, e in indexed if e.get("ts", "") >= since]

    success = defaultdict(list)   # cell_type -> [refs] of validating transitions
    failure = defaultdict(list)   # cell_type -> [refs] of block/no-progress
    costs = defaultdict(list)     # cell_type -> [tokens]
    for i, e in indexed:
        ct = _cell_type((e.get("subject") or {}).get("cell"))
        if not ct:
            continue
        ev = e.get("event")
        if ev == "transition" and e.get("to") in ("validated", "operating"):
            success[ct].append(_ref(i))
        if ev in ("block",) or (ev == "signal" and e.get("to") == "fail"):
            failure[ct].append(_ref(i))
        m = e.get("metrics") or {}
        if isinstance(m.get("tokens"), (int, float)) and m["tokens"] > 0:
            costs[ct].append(m["tokens"])

    candidates = []
    for ct, refs in success.items():
        if len(refs) >= min_occurrences:
            candidates.append({"kind": "success", "cell_type": ct, "signature": f"{ct} validates reliably",
                               "occurrences": len(refs), "evidence": refs})
    for ct, refs in failure.items():
        if len(refs) >= min_occurrences:
            candidates.append({"kind": "failure", "cell_type": ct,
                               "signature": f"{ct} repeatedly blocks/fails — a spec or rubric smell to revise upstream",
                               "occurrences": len(refs), "evidence": refs})
    # probe-cost outliers: a cell type whose mean cost exceeds 2x the mean of the OTHER types' means
    # (comparing to others, not the global mean, so a dominant outlier doesn't dilute its own signal).
    type_means = {ct: sum(cs) / len(cs) for ct, cs in costs.items() if len(cs) >= min_occurrences}
    for ct, mean in type_means.items():
        others = [m for t, m in type_means.items() if t != ct]
        if others and mean > 2 * (sum(others) / len(others)):
            candidates.append({"kind": "probe-cost", "cell_type": ct,
                               "signature": f"{ct} costs {int(mean)} tok/signal (>2x the other types' mean) — compass calibration",
                               "occurrences": len(costs[ct]), "evidence": []})
    return candidates


def selftest():
    import tempfile
    fails = []
    def expect(c, m):
        if not c:
            fails.append(m)
    with tempfile.TemporaryDirectory() as root:
        d = os.path.join(root, ".agents/dev-factory")
        os.makedirs(os.path.join(d, "ledger"))
        srv = {"kind": "server", "id": "s"}
        # two validations of spec.task → a success candidate; three blocks of rubric.task → a failure candidate
        _led.append(d, "transition", srv, {"cell": "spec.task.a"}, "validated a", to="validated")
        _led.append(d, "transition", srv, {"cell": "spec.task.b"}, "validated b", to="validated")
        for _ in range(3):
            _led.append(d, "block", srv, {"cell": "rubric.task.c"}, "verifier failed: same signature")
        # an expensive cell type (policy.system) against a cheap baseline type (spec.task), both with >=2 signals
        _led.append(d, "signal", srv, {"cell": "policy.system.x"}, "v", to="pass", metrics={"tokens": 100000})
        _led.append(d, "signal", srv, {"cell": "policy.system.y"}, "v", to="pass", metrics={"tokens": 120000})
        _led.append(d, "signal", srv, {"cell": "spec.task.z"}, "v", to="pass", metrics={"tokens": 5000})
        _led.append(d, "signal", srv, {"cell": "spec.task.w"}, "v", to="pass", metrics={"tokens": 6000})

        cands = distill_patterns(d, min_occurrences=2)
        kinds = {(c["kind"], c["cell_type"]) for c in cands}
        expect(("success", "spec.task") in kinds, "did not distill the recurring success signature")
        expect(("failure", "rubric.task") in kinds, "did not distill the recurring failure signature")
        expect(("probe-cost", "policy.system") in kinds, "did not flag the expensive cell type")
        # provenance: every success/failure candidate carries ledger_refs
        for c in cands:
            if c["kind"] in ("success", "failure"):
                expect(c["evidence"] and all(r.startswith("ledger:") for r in c["evidence"]),
                       f"candidate {c['cell_type']} has no provenance — a pattern without provenance is a guess")
        # a one-off does not become a candidate (min_occurrences guards against noise)
        expect(not any(c["cell_type"] == "spec.task" and c["occurrences"] < 2 for c in cands), "a one-off leaked through")
    if fails:
        sys.stderr.write("distill selftest: FAIL\n")
        for f in fails:
            sys.stderr.write(f"  - {f}\n")
        return 1
    print("distill selftest: OK (recurring success/failure signatures + probe-cost outliers become candidates, "
          "each with ledger provenance; a one-off below min-occurrences is filtered as noise — the scan is code, "
          "the judgment 'is this a real pattern' is the distiller agent's)")
    return 0


def _arg(argv, flag, default=None):
    return argv[argv.index(flag) + 1] if flag in argv else default


def main(argv):
    if not argv or argv[0] == "selftest":
        return selftest()
    if argv[0] == "scan":
        d = _arg(argv, "--dir", ".agents/dev-factory")
        cands = distill_patterns(d, since=_arg(argv, "--since"),
                                 min_occurrences=int(_arg(argv, "--min-occurrences", "2")))
        print(json.dumps(cands, indent=2))
        return 0
    print(f"distill.py: unknown verb {argv[0]}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
