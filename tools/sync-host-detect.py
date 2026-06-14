#!/usr/bin/env python3
"""sync-host-detect.py — keep the vendored host_detect.py byte-identical to the canonical one.

Canonical: tools/host-detect/host_detect.py. The self-contained rule forbids cross-plugin imports (an installed
plugin is copied into the host's version-keyed cache and can't reach a sibling), so each RUNTIME consumer gets
its own vendored copy — today harness-forge/bin/host_detect.py (consumed by wire.py for host-aware install).
Default: copy canonical -> each vendored. --check: verify byte-equality (the CI drift gate); exit 1 on drift.
Stdlib only; Python 3.8+.
"""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CANON = os.path.join(ROOT, "tools", "host-detect", "host_detect.py")
VENDORED = [os.path.join(ROOT, "harness-forge", "bin", "host_detect.py")]


def main(argv):
    check = "--check" in argv
    canon = open(CANON, "rb").read()
    drift = []
    for v in VENDORED:
        if check:
            if not os.path.isfile(v) or open(v, "rb").read() != canon:
                drift.append(v)
        else:
            os.makedirs(os.path.dirname(v), exist_ok=True)
            shutil.copyfile(CANON, v)
            print("synced " + os.path.relpath(v, ROOT))
    if check:
        if drift:
            sys.stderr.write("sync-host-detect: DRIFT — re-run `python3 tools/sync-host-detect.py` to refresh:\n")
            for d in drift:
                sys.stderr.write("  - " + os.path.relpath(d, ROOT) + "\n")
            return 1
        print("sync-host-detect: OK ({} vendored copy byte-identical to canonical)".format(len(VENDORED)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
