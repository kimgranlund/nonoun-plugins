#!/usr/bin/env python3
"""verdict.py — did the factory build a reasonably solid app?

    python3 debug/bin/verdict.py <name> [--quiet]

A structured health check the ralph loop reads as its stop condition. Three signals:
  - lattice_built : every build cell (spec + capability) reached `validated`/`operating` — the knowledge is built.
  - artifact      : a real app artifact exists in the project (index.html / package.json / a source tree).
  - smoke         : optional — `npm run build` is clean if there is a package.json (skipped otherwise).

`ok` is gated on lattice_built (the factory's own definition of done — the lattice is the source of truth). The
artifact + smoke are additional real-world signals reported alongside (a live run should show them too; the mock
plumbing proof builds the lattice without a project-root artifact, which is expected).

Stdlib only; Python 3.8+.
"""
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C   # noqa: E402

BUILD_LAYERS = ("spec", "capability")
SETTLED = ("validated", "operating")
SHIP_CELL = "capability.system.app"   # the integrator: its verify.mjs is the SHIP gate (compose + build + acceptance + smoke)


def _artifact(inst):
    """The produced app artifact — the integrator's source dir under the instance (where the app is authored)."""
    appdir = os.path.join(inst, "capability", "app")
    if os.path.isdir(appdir):
        files = sorted(f for f in os.listdir(appdir) if f != "verify.mjs")
        if files:
            return f"capability/app/ ({len(files)} file(s): {', '.join(files[:4])}{'…' if len(files) > 4 else ''})"
    return None


def _smoke(proj):
    """If there's a package.json with a build script, run it. Returns (ran, ok, detail)."""
    pkg = os.path.join(proj, "package.json")
    if not os.path.isfile(pkg) or shutil.which("npm") is None:
        return False, None, "no package.json / npm — smoke skipped"
    try:
        import json
        scripts = (json.load(open(pkg)).get("scripts") or {})
        if "build" not in scripts:
            return False, None, "no build script"
        C.sh(["npm", "install", "--silent"], cwd=proj, check=True)
        r = C.sh(["npm", "run", "build", "--silent"], cwd=proj, check=False, capture=True)
        return True, r.returncode == 0, f"npm run build exit {r.returncode}"
    except Exception as e:
        return True, False, f"smoke error: {e}"


def verdict(name, quiet=False, smoke=False):
    api = C._import_api()
    inst, proj = C.instance_dir(name), C.project_dir(name)
    grid = api.lattice_grid(inst)
    build = [c for c in grid if c["layer"] in BUILD_LAYERS]
    unbuilt = [c["id"] for c in build if c["maturity"] not in SETTLED]
    lattice_built = bool(build) and not unbuilt
    ship = next((c for c in grid if c["id"] == SHIP_CELL), None)
    # SHIPPED = the integrator cell validated. Its verify.mjs IS the ship gate (composes every capability +,
    # live, runs the build + the spec's acceptance criteria + the browser smoke). So a validated ship cell means
    # those gates already passed — the verdict reads the gate's verdict, it doesn't re-grade.
    shipped = bool(ship) and ship.get("maturity") in SETTLED
    artifact = _artifact(inst)
    sm_ran, sm_ok, sm_detail = _smoke(proj) if (smoke and shipped) else (False, None, "smoke not requested (the ship cell's verify.mjs is the gate)")

    ok = lattice_built
    result = {"ok": ok, "lattice_built": lattice_built, "shipped": shipped, "ship_cell": SHIP_CELL,
              "build_cells": len(build), "unbuilt": unbuilt, "artifact": artifact,
              "smoke": {"ran": sm_ran, "ok": sm_ok, "detail": sm_detail}}
    if not quiet:
        C.banner(f"verdict for '{name}'")
        print(f"  lattice built : {'YES' if lattice_built else 'NO'} ({len(build) - len(unbuilt)}/{len(build)} build cells settled)")
        if unbuilt:
            print(f"     unbuilt    : {', '.join(unbuilt)}")
        print(f"  ship cell     : {SHIP_CELL} → {(ship or {}).get('maturity', 'absent')}")
        print(f"  app artifact  : {artifact or 'none authored yet'}")
        print(f"  SHIPPED       : {'YES ✓ — the integrator validated (its verify.mjs gate passed)' if shipped else 'NO ✗'}")
        print(f"  VERDICT       : {'PASS ✓' if ok else 'FAIL ✗'}")
    return result


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    name = argv[0]
    r = verdict(name, quiet="--quiet" in argv, smoke="--smoke" in argv)
    return 0 if r["ok"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
