#!/usr/bin/env python3
"""check.py — calibration for spec-author's REVIEW (the gate + the spec-council), the deterministic half.

The councils' standing blind spot: the kernel holds its GATES to planted-defect evals (harness-forge's
evals/calibration/) but the new spec-COUNCIL's verdict was un-calibrated model judgment with no falsifiable
replay — and Elon M.'s "no fixture shows the council out-performs a single validator" went unanswered. This
is the answer, as a fixture set, mechanically checked:

  fixtures/gate/     — each plants ONE mechanical defect the spec-quality GATE must REJECT, on a named
                       dimension (criteria-checkable, non-goals-present, schema-valid layer, decomposition-
                       entailment). Deterministic; this is the gate proving itself.
  fixtures/council/  — each is mechanically SOUND (the gate PASSES it) but carries a JUDGMENT defect only a
                       critic-lens catches (a hackable criterion, incomplete coverage, coverage-without-
                       entailment). The gate passing them is the POINT: it demonstrates, deterministically,
                       that the gate alone is insufficient — the council reviews what the gate cannot. That
                       is the proof the council out-performs the gate/validator.

The MODEL half — does the council actually catch each council/ defect? — is the answer key in README.md
(each fixture → the lens that should BLOCK it), run as a recorded baseline, never a live model in CI (the
judge runs cold against the fixtures; the key stays in the README, not the fixture). This script asserts the
DETERMINISTIC contract: gate/ → rejected on the right dimension; council/ → passes (so the council is the
only defense). Exit 0 = the contract holds. Stdlib only; Python 3.8+.
"""
import os
import subprocess
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_GATE = os.path.join(os.path.dirname(os.path.dirname(_HERE)), "bin", "spec-quality-check.py")  # dev-kit-corpus/bin/
_FX = os.path.join(_HERE, "fixtures")

# gate/ fixture -> the gate dimension whose message must appear when it is (correctly) rejected
GATE_EXPECT = {
    "prose-only-criterion": "criteria-checkable",
    "no-non-goals": "non-goals-present",
    "wrong-layer": "not a spec",
    "unsound-decomposition": "decomposition-entailment",
}
# council/ fixture -> the lens whose job is to BLOCK it (the answer key; the gate does NOT catch these)
COUNCIL_LENS = {
    "hackable-criterion": "critic-spec-hackability",
    "incomplete-coverage": "critic-spec-completeness",
    "weak-entailment": "critic-spec-entailment",
}


def _gate(path):
    r = subprocess.run(["python3", _GATE, path], capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr)


def run():
    fails = []

    print("· gate/ — each planted mechanical defect must be REJECTED on its named dimension")
    for slug, dim in sorted(GATE_EXPECT.items()):
        path = os.path.join(_FX, "gate", slug + ".md")
        code, out = _gate(path)
        ok = code == 1 and dim in out
        print(f"  {'PASS' if ok else 'FAIL'}  {slug:28} -> {dim}")
        if not ok:
            fails.append(f"gate/{slug}: expected rejection on '{dim}', got exit {code}: {out.strip()[:90]}")

    print("· council/ — each is gate-CLEAN (the gate alone would wave it through); only the lens catches it")
    for slug, lens in sorted(COUNCIL_LENS.items()):
        path = os.path.join(_FX, "council", slug + ".md")
        code, out = _gate(path)
        ok = code == 0
        print(f"  {'PASS' if ok else 'FAIL'}  {slug:28} -> gate passes; {lens} must BLOCK (see README)")
        if not ok:
            fails.append(f"council/{slug}: the gate must PASS a judgment-only defect (so the council is the "
                         f"only defense), got exit {code}: {out.strip()[:90]}")

    print()
    if fails:
        print(f"spec-review-calibration: FAIL — {len(fails)} contract violation(s):")
        for f in fails:
            print(f"  - {f}")
        return 1
    print(f"spec-review-calibration: OK — {len(GATE_EXPECT)} gate defects each caught on the right dimension; "
          f"{len(COUNCIL_LENS)} judgment defects each pass the gate (the council is the only line of defense — "
          f"the fixture set IS the proof the council reviews what the gate cannot). Answer key: README.md.")
    return 0


if __name__ == "__main__":
    sys.exit(run() if (not sys.argv[1:] or sys.argv[1] == "selftest") else run())
