#!/usr/bin/env python3
"""sync-dev-kernel.py — vendor harness-forge's lattice kernel into dev-kernel, drift-gated (D-A).

dev-factory does NOT re-implement the lattice machine. Per the build plan's decision D-A, the
kernel's lattice/engine/validation-path ARE harness-forge's proven, selftested, CI-gated bins —
vendored byte-identical here (the same pattern as `sync-corpus-reader.py` and `sync-host-detect.py`),
so harness-forge stays a single source of truth and an untouched, standalone plugin. dev-kernel
operates the vendored kernel against its own instance dir via `--dir .agents/dev-factory`, and adds
the ticket/dispatch/server/tiering layer ON TOP — it never edits the vendored files.

The vendored set is deliberately minimal — only the two files that are pure, `--dir`-parameterized
lattice computation with no harness-forge-specific path coupling:
  - lattice.py  : THE kernel — maturity state machine (TRANSITIONS), scan/rank/validity/advance,
                  staleness-as-graph, scaffold, the run-budget + loop-marker bound machinery.
  - validate.py : the validation path — runs a verifier, mints the Signal from its EXIT STATUS,
                  advances instantiated→validated only on pass. Imports `lattice` as a sibling,
                  which is why both land in dev-kernel/bin/ (not a subdir).

Everything dev-factory-specific (the ticket lifecycle machine, the six gates, the coordination
ledger vocab, dispatch, the server, the autonomy tiers) is NATIVE dev-kernel code that *calls* the
vendored kernel — never a fork of it.

Usage:
  sync-dev-kernel.py            # copy harness-forge/bin/{lattice,validate}.py -> dev-kernel/bin/
  sync-dev-kernel.py --check    # CI: exit 1 if any vendored copy drifted from its source
  sync-dev-kernel.py selftest   # prove the gate catches drift
Stdlib only; Python 3.8+.
"""
import hashlib
import os
import shutil
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# vendored file -> (source under repo, destination under repo)
# lattice.py + validate.py are the kernel computation; cell.schema.json is the contract the vendored
# lattice.py `check()` validates cell keys/enums against — so dev-kernel ADOPTS harness-forge's cell
# shape (separate layer/scope/slug, computed cid, the map-form validated_against). The dev spec's
# independently-drafted cell.schema.json (an explicit `id` field) is superseded by this adopted contract.
VENDORED = {
    "lattice.py": ("harness-forge/bin/lattice.py", "dev-factory/dev-kernel/bin/lattice.py"),
    "validate.py": ("harness-forge/bin/validate.py", "dev-factory/dev-kernel/bin/validate.py"),
    "cell.schema.json": ("harness-forge/schemas/cell.schema.json", "dev-factory/dev-kernel/schemas/cell.schema.json"),
}


def _sha(path):
    try:
        return hashlib.sha256(open(path, "rb").read()).hexdigest()
    except OSError:
        return None


def sync():
    n = 0
    for name, (src, dst) in VENDORED.items():
        sp, dp = os.path.join(_REPO, src), os.path.join(_REPO, dst)
        os.makedirs(os.path.dirname(dp), exist_ok=True)
        shutil.copyfile(sp, dp)
        os.chmod(dp, 0o755)
        print(f"  vendored {name}: {src} -> {dst}")
        n += 1
    print(f"sync-dev-kernel: OK ({n} kernel file(s) vendored from harness-forge)")
    return 0


def check():
    drift = []
    for name, (src, dst) in VENDORED.items():
        sp, dp = os.path.join(_REPO, src), os.path.join(_REPO, dst)
        if not os.path.exists(dp):
            drift.append(f"{name}: MISSING vendored copy ({dst}) — run sync-dev-kernel.py")
            continue
        if _sha(sp) != _sha(dp):
            drift.append(f"{name}: DRIFTED from source ({src}) — re-run sync-dev-kernel.py")
    if drift:
        sys.stderr.write("sync-dev-kernel --check: FAIL\n")
        for d in drift:
            sys.stderr.write(f"  - {d}\n")
        return 1
    print(f"sync-dev-kernel --check: OK ({len(VENDORED)} vendored kernel file(s) in sync with harness-forge)")
    return 0


def selftest():
    import tempfile
    # The gate must (a) report OK when copies match, (b) FAIL when one drifts.
    fails = []
    with tempfile.TemporaryDirectory() as t:
        src = os.path.join(t, "src.py")
        dst = os.path.join(t, "dst.py")
        open(src, "w").write("kernel = 1\n")
        shutil.copyfile(src, dst)
        if _sha(src) != _sha(dst):
            fails.append("identical files hashed differently")
        open(dst, "w").write("kernel = 2  # tampered\n")
        if _sha(src) == _sha(dst):
            fails.append("drift not detected — a tampered vendored copy hashed equal")
    if fails:
        sys.stderr.write("sync-dev-kernel selftest: FAIL\n")
        for f in fails:
            sys.stderr.write(f"  - {f}\n")
        return 1
    print("sync-dev-kernel selftest: OK (matching copies pass; a drifted copy is caught)")
    return 0


def main(argv):
    if argv and argv[0] == "selftest":
        return selftest()
    if argv and argv[0] == "--check":
        return check()
    return sync()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
