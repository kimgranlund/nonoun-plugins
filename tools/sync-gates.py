#!/usr/bin/env python3
"""sync-gates.py — keep tools/gates/ byte-identical to nonoun-factory's plugins-factory/bin (cross-repo drift gate).

The catalog split (D-18, 2026-06-17): plugins-factory moved to the sibling **nonoun-factory** repo, but its gate
suite still validates THIS repo's products (brand-forge, product-forge) in CI. So the gate bins are VENDORED into
`tools/gates/` — the corpus-reader vendoring pattern, made cross-repo. This script copies the canonical gates from a
nonoun-factory checkout and, in `--check`, asserts the vendored copies are byte-identical: drift FAILS CI, so a fix
to a gate in nonoun-factory can't silently rot the products' validation here. (Only the `.py` gates are synced — the
re-homed `recall-corpus/` + `scores/` are nonoun-plugins-owned, since their checkers/subjects are the products.)

Usage:
  sync-gates.py            # copy the canonical gates from nonoun-factory into tools/gates/ (refresh the vendor)
  sync-gates.py --check    # FAIL if any vendored gate drifted from nonoun-factory (clones it; needs network)
Exit 0 = in sync (or copied); 1 = drift; 2 = cannot reach nonoun-factory. Stdlib only; Python 3.8+.
"""
import filecmp
import os
import shutil
import subprocess
import sys
import tempfile

REPO = os.environ.get("NONOUN_FACTORY_REPO", "https://github.com/kimgranlund/nonoun-factory.git")
HERE = os.path.dirname(os.path.abspath(__file__))            # tools/
GATES = os.path.join(HERE, "gates")


def _vendored():
    return [f for f in sorted(os.listdir(GATES)) if f.endswith(".py")]


def main(argv):
    check = "--check" in argv
    vendored = _vendored()
    with tempfile.TemporaryDirectory() as tmp:
        try:
            subprocess.run(["git", "clone", "--depth", "1", "--quiet", REPO, tmp + "/nf"], check=True,
                           capture_output=True)
        except (OSError, subprocess.CalledProcessError) as e:
            print(f"sync-gates: cannot clone nonoun-factory ({REPO}): {e}", file=sys.stderr)
            return 2
        src = os.path.join(tmp, "nf", "plugins-factory", "bin")
        drift, copied = [], 0
        for g in vendored:
            s, d = os.path.join(src, g), os.path.join(GATES, g)
            if not os.path.isfile(s):
                print(f"sync-gates: {g} is vendored here but absent from nonoun-factory/plugins-factory/bin", file=sys.stderr)
                drift.append(g)
                continue
            if check:
                if not filecmp.cmp(s, d, shallow=False):
                    drift.append(g)
            else:
                shutil.copyfile(s, d)
                copied += 1
        if check:
            if drift:
                print(f"RESULT: FAIL — {len(drift)} vendored gate(s) drifted from nonoun-factory: {sorted(drift)}. "
                      f"Refresh with `python3 tools/sync-gates.py`.", file=sys.stderr)
                return 1
            print(f"RESULT: PASS — {len(vendored)} vendored gate(s) byte-identical to nonoun-factory")
            return 0
        print(f"sync-gates: copied {copied}/{len(vendored)} gate(s) from nonoun-factory")
        return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
