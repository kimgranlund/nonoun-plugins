#!/usr/bin/env python3
"""rubric-check.py — the corpus family's rubric-cell verifier (a kit validation harness).

The validation adapter `rubric-calibration-check` binds this to rubric-layer cells. A rubric is only a
verifier if it carries at least one mechanical `[gate]` criterion AND a pristine-reference / calibration
hook the worker cannot reach (else it is "scoring vibes"). validate.py mints the signal from this exit
status — so a rubric becomes a trusted verifier only once it passes its own meta-verifier.

Usage:  rubric-check.py <asset-path>   |   rubric-check.py selftest
Exit 0 = pass; 1 = fail; 2 = bad invocation. Stdlib only; Python 3.8+.
"""
import json
import os
import sys


def check(path):
    if not path or not os.path.isfile(path):
        return False, f"no asset at {path!r}"
    raw = open(path, encoding="utf-8", errors="replace").read()
    try:
        doc = json.loads(raw)
    except json.JSONDecodeError as e:
        return False, f"rubric is not valid JSON ({e})"
    blob = json.dumps(doc)
    if "[gate]" not in blob:
        return False, "rubric has no [gate] criterion (a rubric with only [review] dims is scoring vibes)"
    if not any(k in blob for k in ("pristine", "reference", "calibration", "exemplar")):
        return False, "rubric carries no pristine-reference / calibration hook the worker cannot reach"
    return True, "rubric is a calibrated verifier ([gate] + pristine reference)"


def selftest():
    import tempfile
    fails = []
    with tempfile.TemporaryDirectory() as d:
        good = os.path.join(d, "g.rubric.json")
        json.dump({"dimensions": [{"name": "entailment", "label": "[gate]", "scored_against": "pristine reference set"}],
                   "calibration": {"exemplars": 3}}, open(good, "w"))
        if not check(good)[0]:
            fails.append("rejected a calibrated [gate] rubric")
        weak = os.path.join(d, "w.rubric.json")
        json.dump({"dimensions": [{"name": "vibes", "label": "[review]"}]}, open(weak, "w"))
        if check(weak)[0]:
            fails.append("accepted a [review]-only rubric with no gate")
        bad = os.path.join(d, "b.rubric.json")
        open(bad, "w").write("not json")
        if check(bad)[0]:
            fails.append("accepted invalid JSON")
    if fails:
        sys.stderr.write("rubric-check selftest: FAIL\n")
        for f in fails:
            sys.stderr.write(f"  - {f}\n")
        return 1
    print("rubric-check selftest: OK (a [gate]+pristine-reference rubric passes; a [review]-only rubric and "
          "invalid JSON fail — a rubric earns 'verifier' only by passing its own meta-verifier)")
    return 0


def main(argv):
    if not argv:
        sys.stderr.write("usage: rubric-check.py <asset-path> | selftest\n")
        return 2
    if argv[0] == "selftest":
        return selftest()
    ok, msg = check(argv[0])
    print(msg, file=sys.stderr if not ok else sys.stdout)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
