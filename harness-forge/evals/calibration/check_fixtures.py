#!/usr/bin/env python3
"""check_fixtures.py — the gates prove themselves on real planted defects (the calibration CI gate).

Each fixture under fixtures/ plants ONE headline defect in an otherwise-clean `.harness/` tree; this
script asserts the right `bin/` gate FAILS it with the right finding — and, as the directionality
control, that a freshly seeded + wired project PASSES the same gates (a checker that fails everything
proves nothing). The answer key is README.md, one level up — never inside a fixture, so judge runs
against the fixtures stay cold.

Usage:
  check_fixtures.py            # run all fixture assertions + the clean control; exit 0 = all hold
  check_fixtures.py selftest   # alias (the run IS the self-proof: defects caught, control clean)
Stdlib only; Python 3.8+.
"""
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
BIN = os.path.normpath(os.path.join(HERE, "..", "..", "bin"))
FIX = os.path.join(HERE, "fixtures")


def run(args, **kw):
    return subprocess.run([sys.executable] + args, capture_output=True, text=True, **kw)


def main():
    fails = []

    def expect(cond, label):
        print(("  PASS  " if cond else "  FAIL  ") + label)
        if not cond:
            fails.append(label)

    print("fixture gates (each planted defect is CAUGHT):")

    # F1 — rubric-before-spec: the retroactive partial-order violation
    r = run([os.path.join(BIN, "lattice.py"), "check", "--dir", os.path.join(FIX, "rubric-before-spec", ".harness")])
    expect(r.returncode == 1 and "violated retroactively" in r.stdout,
           "rubric-before-spec → lattice.py check exits 1 with the retro-order finding")

    # F2 — unwired-gate: signals minted, nothing blocking the worker
    r = run([os.path.join(BIN, "wire.py"), "check", "--project", os.path.join(FIX, "unwired-gate")])
    expect(r.returncode == 1 and "missing" in r.stdout,
           "unwired-gate → wire.py check exits 1 (present-but-unwired is the H3 false pass)")

    # F3 — unearned-autonomy: a Tier-3 claim atop an UNMEASURED false-pass rate
    r = run([os.path.join(BIN, "ledger.py"), "false-pass", "--dir", os.path.join(FIX, "unearned-autonomy", ".harness")])
    expect("UNMEASURED" in r.stdout, "unearned-autonomy → ledger.py false-pass reports UNMEASURED (no refuter)")
    policy = open(os.path.join(FIX, "unearned-autonomy", ".harness", "policy", "trust-trajectory.md"), encoding="utf-8").read()
    expect("Tier 3" in policy and "unattended" in policy,
           "unearned-autonomy → the policy doc claims Tier 3 unattended (the contradiction the judge must catch)")
    # F3's phantom signals — the live council's emergent find, folded back into the kernel (0.3.0)
    r = run([os.path.join(BIN, "lattice.py"), "check", "--dir", os.path.join(FIX, "unearned-autonomy", ".harness")])
    expect(r.returncode == 1 and "does not exist on disk" in r.stdout,
           "unearned-autonomy → lattice.py check catches the phantom signal refs (asserted, not earned)")

    # F4 — stale-but-trusted: the rubric trusts a hash the spec asset no longer has
    r = run([os.path.join(BIN, "lattice.py"), "check", "--dir", os.path.join(FIX, "stale-but-trusted", ".harness")])
    expect(r.returncode == 1 and "stale-but-trusted" in r.stdout,
           "stale-but-trusted → lattice.py check exits 1 with the hash-mismatch finding")

    print("directionality control (a clean project PASSES the same gates):")
    with tempfile.TemporaryDirectory() as proj:
        hd = os.path.join(proj, ".harness")
        r = run([os.path.join(BIN, "lattice.py"), "init", "clean-control", "--dir", hd])
        expect(r.returncode == 0, "control: seed succeeds")
        r = run([os.path.join(BIN, "lattice.py"), "check", "--dir", hd])
        expect(r.returncode == 0, "control: a fresh seed passes lattice.py check")
        r = run([os.path.join(BIN, "wire.py"), "apply", "--project", proj])
        expect(r.returncode == 0, "control: wire.py apply succeeds")
        r = run([os.path.join(BIN, "wire.py"), "check", "--project", proj])
        expect(r.returncode == 0, "control: a wired project passes wire.py check")

    if fails:
        print(f"\nRESULT: FAIL — {len(fails)} assertion(s) broken")
        return 1
    print("\nRESULT: PASS (calibration fixtures) — every planted defect caught; the clean control passes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
