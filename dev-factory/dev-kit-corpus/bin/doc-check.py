#!/usr/bin/env python3
"""doc-check.py — the corpus family's spec-cell verifier (a kit validation harness).

The validation adapter `spec-doc-check` binds this to spec-layer cells: validate.py runs it on the cell's
asset and mints the signal from its EXIT STATUS. A spec asset is valid when it exists, carries a heading,
and is substantive (not a stub). This is deliberately mechanical — the deep quality judgment is the
critic's; this is the pristine, worker-unreachable gate the signal rests on.

Usage:  doc-check.py <asset-path>   |   doc-check.py selftest
Exit 0 = pass; 1 = fail; 2 = bad invocation. Stdlib only; Python 3.8+.
"""
import os
import sys

MIN_CHARS = 80


def check(path):
    if not path or not os.path.isfile(path):
        return False, f"no asset at {path!r}"
    text = open(path, encoding="utf-8", errors="replace").read()
    if not any(line.lstrip().startswith("#") for line in text.splitlines()):
        return False, "spec has no markdown heading (a stub, not a spec)"
    if len(text.strip()) < MIN_CHARS:
        return False, f"spec is below the substance floor ({len(text.strip())} < {MIN_CHARS} chars)"
    return True, "spec asset is substantive"


def selftest():
    import tempfile
    fails = []
    with tempfile.TemporaryDirectory() as d:
        good = os.path.join(d, "g.md")
        open(good, "w").write("# A real spec\n\n" + "It declares the intent in enough detail to be worth validating. " * 3)
        if not check(good)[0]:
            fails.append("rejected a substantive spec")
        stub = os.path.join(d, "s.md")
        open(stub, "w").write("# x\n")
        if check(stub)[0]:
            fails.append("accepted a stub")
        if check(os.path.join(d, "missing.md"))[0]:
            fails.append("accepted a missing asset")
    if fails:
        sys.stderr.write("doc-check selftest: FAIL\n")
        for f in fails:
            sys.stderr.write(f"  - {f}\n")
        return 1
    print("doc-check selftest: OK (a substantive spec passes; a stub and a missing asset fail)")
    return 0


def main(argv):
    if not argv:
        sys.stderr.write("usage: doc-check.py <asset-path> | selftest\n")
        return 2
    if argv[0] == "selftest":
        return selftest()
    ok, msg = check(argv[0])
    print(msg, file=sys.stderr if not ok else sys.stdout)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
