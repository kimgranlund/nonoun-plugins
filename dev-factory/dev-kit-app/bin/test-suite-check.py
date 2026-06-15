#!/usr/bin/env python3
"""test-suite-check.py — the REAL verifier the app capability + protocol adapters bind.

Two modes, one bin (the app family's two validation rubrics share a result shape):
  * default / `suite`    → rubric.system.test-suite (capability layer): tests-exist, tests-pass, coverage-floor
  * `contract`           → rubric.workflow.contract-tests (protocol layer): every-boundary-has-a-contract-test,
                            failure-modes-covered (+ schema-valid)

This mechanizes the [gate] dimensions ONLY; oracle-quality / mutation-resistance / consumer-fidelity /
breaking-change-discipline are a calibrated critic's job. validate.py runs it on the cell's asset and mints
the signal from its EXIT STATUS (0 = all gates pass). The verdict rests on the EXTERNAL test runner's
recorded result — the worker writes tests, the runner decides pass/fail. The asset is the runner's
machine-readable result (JSON, or a ```json block in a `.md` report):

  suite mode:
    { "tests": <int>, "failures": <int>, "errors": <int>, "coverage": <0..100>, "coverage_floor": <0..100> }
  contract mode:
    { "declared_boundaries": [ {"id":"b1","failure_modes":["timeout","denied"]}, ... ],
      "contract_tests":     [ {"boundary":"b1","failure_mode":null,"failures":0,"errors":0}, ... ] }

The declared_boundaries set is the PRISTINE reference (supplied read-only) — coverage is scored against it,
so a worker cannot shrink the set to pass. Stdlib only; Python 3.8+.

Usage:  test-suite-check.py <asset-path>            (suite mode)
        test-suite-check.py contract <asset-path>   (contract mode)
        test-suite-check.py selftest
Exit 0 = all gates pass; 1 = a gate failed; 2 = bad invocation.
"""
import json
import os
import re
import sys

DEFAULT_COVERAGE_FLOOR = 70.0


def _load_result(path):
    raw = open(path, encoding="utf-8", errors="replace").read()
    if raw.lstrip().startswith("{"):
        return json.loads(raw)
    m = re.search(r"```json\s*(\{.*?\})\s*```", raw, re.DOTALL)
    if m:
        return json.loads(m.group(1))
    raise ValueError("test asset carries no machine-readable result (expected JSON or a ```json block) — "
                     "a green claim with no runner result is the worker's opinion, not a measured signal")


# ---- suite mode (capability) -------------------------------------------------

def _suite_tests_exist(r):
    n = r.get("tests")
    if not isinstance(n, int) or n < 1:
        return False, f"no tests in the runner result (tests={n!r}) — 'validated' would be an opinion"
    return True, f"{n} tests discovered"


def _suite_tests_pass(r):
    f, e = r.get("failures"), r.get("errors")
    if not isinstance(f, int) or not isinstance(e, int):
        return False, f"runner result missing failures/errors counts (failures={f!r}, errors={e!r})"
    if f or e:
        return False, f"suite is RED: {f} failures, {e} errors (a known-broken cell)"
    return True, "suite runs green (0 failures, 0 errors)"


def _suite_coverage_floor(r):
    cov = r.get("coverage")
    floor = r.get("coverage_floor", DEFAULT_COVERAGE_FLOOR)
    if not isinstance(cov, (int, float)):
        return False, f"no measured coverage in the runner result (coverage={cov!r})"
    if cov < floor:
        return False, f"coverage {cov}% below the floor {floor}% (untested code is unverified)"
    return True, f"coverage {cov}% clears the floor {floor}%"


SUITE_GATES = [
    ("tests-exist", _suite_tests_exist),
    ("tests-pass", _suite_tests_pass),
    ("coverage-floor", _suite_coverage_floor),
]


# ---- contract mode (protocol) ------------------------------------------------

def _contract_schema_valid(r):
    db = r.get("declared_boundaries")
    ct = r.get("contract_tests")
    if not isinstance(db, list) or not db:
        return False, "no declared_boundaries (the pristine boundary set) — coverage would pass vacuously"
    if not isinstance(ct, list):
        return False, "no contract_tests list"
    for b in db:
        if not isinstance(b, dict) or not b.get("id"):
            return False, f"malformed declared boundary {b!r} (needs an id)"
    return True, f"{len(db)} declared boundaries, {len(ct)} contract tests"


def _green_tests_for(ct):
    """A contract test counts only if it ran green (an external-runner result)."""
    return [t for t in ct if isinstance(t, dict) and not t.get("failures") and not t.get("errors")]


def _contract_every_boundary_tested(r):
    db = r.get("declared_boundaries") or []
    green = _green_tests_for(r.get("contract_tests") or [])
    tested = {t.get("boundary") for t in green}
    missing = [b["id"] for b in db if b["id"] not in tested]
    if missing:
        return False, f"boundaries with no green contract test: {missing} (unverified contracts)"
    return True, f"all {len(db)} declared boundaries have a green contract test"


def _contract_failure_modes_covered(r):
    db = r.get("declared_boundaries") or []
    green = _green_tests_for(r.get("contract_tests") or [])
    covered = {(t.get("boundary"), t.get("failure_mode")) for t in green if t.get("failure_mode")}
    gaps = []
    for b in db:
        for fm in b.get("failure_modes", []):
            if (b["id"], fm) not in covered:
                gaps.append(f"{b['id']}:{fm}")
    if gaps:
        return False, f"failure modes with no green contract test: {gaps} (boundary tested only on the happy path)"
    return True, "every declared failure mode has a green contract test"


CONTRACT_GATES = [
    ("schema-valid", _contract_schema_valid),
    ("every-boundary-has-a-contract-test", _contract_every_boundary_tested),
    ("failure-modes-covered", _contract_failure_modes_covered),
]


def check(path, mode="suite"):
    if not path or not os.path.isfile(path):
        return False, f"no asset at {path!r}"
    try:
        r = _load_result(path)
    except (json.JSONDecodeError, ValueError) as e:
        return False, f"schema-valid FAILED: {e}"
    gates = CONTRACT_GATES if mode == "contract" else SUITE_GATES
    failures, passes = [], []
    for name, fn in gates:
        ok, msg = fn(r)
        (passes if ok else failures).append(f"{name}: {msg}")
    if failures:
        return False, f"GATE FAILURES ({mode}) — " + " | ".join(failures)
    return True, f"all {mode} gates pass — " + " | ".join(passes)


def selftest():
    import tempfile
    fails = []

    def expect(cond, msg):
        if not cond:
            fails.append(msg)

    with tempfile.TemporaryDirectory() as d:
        # --- suite mode ---
        good = {"tests": 12, "failures": 0, "errors": 0, "coverage": 84.0, "coverage_floor": 70}
        g = os.path.join(d, "suite-good.json")
        json.dump(good, open(g, "w"))
        ok, msg = check(g)
        expect(ok, f"rejected a green, above-floor suite: {msg}")

        notests = dict(good, tests=0)
        nt = os.path.join(d, "notests.json")
        json.dump(notests, open(nt, "w"))
        ok, msg = check(nt)
        expect(not ok and "tests-exist" in msg, f"accepted a zero-test capability: {msg}")

        red = dict(good, failures=3)
        rd = os.path.join(d, "red.json")
        json.dump(red, open(rd, "w"))
        ok, msg = check(rd)
        expect(not ok and "tests-pass" in msg, f"accepted a red suite: {msg}")

        low = dict(good, coverage=42.0)
        lo = os.path.join(d, "low.json")
        json.dump(low, open(lo, "w"))
        ok, msg = check(lo)
        expect(not ok and "coverage-floor" in msg, f"accepted a below-floor suite: {msg}")

        # --- contract mode ---
        cgood = {
            "declared_boundaries": [
                {"id": "auth-api", "failure_modes": ["timeout", "denied"]},
                {"id": "store-write", "failure_modes": ["conflict"]},
            ],
            "contract_tests": [
                {"boundary": "auth-api", "failure_mode": None, "failures": 0, "errors": 0},
                {"boundary": "auth-api", "failure_mode": "timeout", "failures": 0, "errors": 0},
                {"boundary": "auth-api", "failure_mode": "denied", "failures": 0, "errors": 0},
                {"boundary": "store-write", "failure_mode": None, "failures": 0, "errors": 0},
                {"boundary": "store-write", "failure_mode": "conflict", "failures": 0, "errors": 0},
            ],
        }
        cg = os.path.join(d, "contract-good.json")
        json.dump(cgood, open(cg, "w"))
        ok, msg = check(cg, "contract")
        expect(ok, f"rejected a fully-covered protocol: {msg}")

        # drop a boundary's test -> every-boundary fails
        miss = json.loads(json.dumps(cgood))
        miss["contract_tests"] = [t for t in miss["contract_tests"] if t["boundary"] != "store-write"]
        cm = os.path.join(d, "contract-miss.json")
        json.dump(miss, open(cm, "w"))
        ok, msg = check(cm, "contract")
        expect(not ok and "every-boundary-has-a-contract-test" in msg, f"accepted an untested boundary: {msg}")

        # happy-path only (drop failure-mode tests) -> failure-modes-covered fails
        happy = json.loads(json.dumps(cgood))
        happy["contract_tests"] = [t for t in happy["contract_tests"] if not t["failure_mode"]]
        ch = os.path.join(d, "contract-happy.json")
        json.dump(happy, open(ch, "w"))
        ok, msg = check(ch, "contract")
        expect(not ok and "failure-modes-covered" in msg, f"accepted happy-path-only contract tests: {msg}")

        # a red contract test does not count as coverage. store-write's ONLY tests are turned red
        # (both its happy-path and its conflict test) -> the boundary has no green test -> fails.
        redct = json.loads(json.dumps(cgood))
        for t in redct["contract_tests"]:
            if t["boundary"] == "store-write":
                t["failures"] = 1
        crd = os.path.join(d, "contract-red.json")
        json.dump(redct, open(crd, "w"))
        ok, msg = check(crd, "contract")
        expect(not ok and "every-boundary-has-a-contract-test" in msg,
               f"counted a RED contract test as coverage: {msg}")

        expect(not check(os.path.join(d, "missing.json"))[0], "accepted a missing asset")

    if fails:
        sys.stderr.write("test-suite-check selftest: FAIL\n")
        for f in fails:
            sys.stderr.write(f"  - {f}\n")
        return 1
    print("test-suite-check selftest: OK (suite: a green above-floor suite passes; zero-test, red, and "
          "below-floor each FAIL the right gate. contract: a fully-covered protocol passes; an untested "
          "boundary, happy-path-only, and a RED contract test counted as coverage each FAIL)")
    return 0


def main(argv):
    if not argv:
        sys.stderr.write("usage: test-suite-check.py <asset-path> | contract <asset-path> | selftest\n")
        return 2
    if argv[0] == "selftest":
        return selftest()
    if argv[0] == "contract":
        if len(argv) != 2:
            sys.stderr.write("usage: test-suite-check.py contract <asset-path>\n")
            return 2
        ok, msg = check(argv[1], "contract")
    else:
        ok, msg = check(argv[0], "suite")
    print(msg, file=sys.stdout if ok else sys.stderr)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
