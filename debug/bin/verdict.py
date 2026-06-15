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


def _artifact(proj):
    """Heuristic: does the project carry a real app artifact a human could run?"""
    for f in ("index.html", "package.json"):
        if os.path.isfile(os.path.join(proj, f)):
            return f
    for sub in ("src", "app", "public"):
        if os.path.isdir(os.path.join(proj, sub)) and os.listdir(os.path.join(proj, sub)):
            return sub + "/"
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
    artifact = _artifact(proj)
    sm_ran, sm_ok, sm_detail = _smoke(proj) if (smoke and lattice_built) else (False, None, "smoke not requested")

    # lattice_built = the loop converged (the stop condition). app_built = a REAL runnable artifact exists.
    # They diverge by design today (DF-9): the shipped adapters author one {layer}/{slug}.md per cell, so a
    # live run builds a *markdown lattice*, not runnable software — app_built needs the DF-9 code-authoring
    # adapter. ok is gated on lattice_built (the factory's own done); app_built is reported loudly + honestly.
    app_built = lattice_built and bool(artifact) and (sm_ok is not False)
    ok = lattice_built and (sm_ok is not False)
    result = {"ok": ok, "lattice_built": lattice_built, "app_built": app_built, "build_cells": len(build),
              "unbuilt": unbuilt, "artifact": artifact, "smoke": {"ran": sm_ran, "ok": sm_ok, "detail": sm_detail}}
    if not quiet:
        C.banner(f"verdict for '{name}'")
        print(f"  lattice built : {'YES' if lattice_built else 'NO'} ({len(build) - len(unbuilt)}/{len(build)} build cells settled)")
        if unbuilt:
            print(f"     unbuilt    : {', '.join(unbuilt)}")
        print(f"  app artifact  : {artifact or 'NONE in the project root'}")
        print(f"  smoke         : {sm_detail}")
        print(f"  app built     : {'YES' if app_built else 'NO'}")
        if lattice_built and not app_built:
            print("     note       : the lattice is built but there is no runnable artifact — the shipped dispatch")
            print("                  adapters author one .md per cell, not multi-file source (DF-9). A real app")
            print("                  needs the DF-9 code-authoring adapter; today's live run is a loop-mechanics build.")
        print(f"  VERDICT       : {'PASS ✓ (lattice built)' if ok else 'FAIL ✗'}")
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
