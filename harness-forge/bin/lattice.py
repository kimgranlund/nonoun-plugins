#!/usr/bin/env python3
"""lattice.py — the canonical lattice operations: scan, rank, advance-validity, staleness.

The lattice is layers × scopes; a cell is one layer at one scope with a maturity state. "What should we
work on next?" is a SELECTION FUNCTION over this grid, not a planning meeting — and selection, ranking,
readiness, and staleness are deterministic graph computations, so they live in code, never in inference
(the routing law: computation routes to code, a model-predicted computation is a hallucination surface).
This script is that code. Canonical state is `.harness/lattice.json`; every other view is derived.

Operations:
  - scan      — sweep the modality axis at the frontier scope → the open/stale gap set (detects gaps; does not rank)
  - rank      — order the gaps by priority ≈ (risk × unlock) ÷ probe-cost, subject to dependency readiness
  - validity  — may this cell advance? (deps validated · verifier-rubric validated · layer partial-order · not blocked)
  - stale     — propagate staleness: an upstream content-hash change flips every dependent to `stale`

The partial order it enforces (a rubric before its spec scores vibes):
  ontology + spec → rubric, policy, capability → methodology, protocol → ledger → pattern

See references/agentic-systems-foundations/lattice-model.md and layer-*.md.

Usage:
  lattice.py init <project> [--dir DIR]          # seed a lattice.json (an ontology+spec slice at task scope)
  lattice.py scan [--dir DIR]                    # the gap set at the frontier scope
  lattice.py rank [--dir DIR]                    # ranked, dependency-ready gaps
  lattice.py validity <cell-id> [--dir DIR]      # can this cell advance? exit 0 = yes
  lattice.py stale <cell-id> <hash> [--dir DIR]  # flip dependents of <cell-id> to stale; print + persist
  lattice.py selftest
Exit codes are operation-specific (see each). Stdlib only; Python 3.8+.
"""
import json
import os
import sys

LAYERS = ["ontology", "spec", "rubric", "policy", "capability", "methodology", "protocol", "ledger", "pattern"]
SCOPES = ["call", "task", "workflow", "system", "fleet"]
ADVANCEABLE = {"absent", "defined", "instantiated", "stale"}          # maturities an engine pass may act on
SETTLED = {"validated", "operating"}                                  # maturities that count as a foothold

# The layer partial order: which upstream layers (at the same scope) a layer requires a validated foothold in.
# Ledger sits early (schema cannot be retrofitted) so it has no upstream layer dep; pattern sits last (needs operation).
LAYER_DEPS = {
    "ontology": [], "spec": ["ontology"],
    "rubric": ["spec"], "policy": ["spec"], "capability": ["spec", "ontology"],
    "methodology": ["spec", "rubric"], "protocol": ["capability"],
    "ledger": ["ontology"], "pattern": ["ledger"],
}
LAYER_RANK = {l: i for i, (l, _) in enumerate(
    [("ontology", 0), ("spec", 0), ("rubric", 1), ("policy", 1), ("capability", 1),
     ("methodology", 2), ("protocol", 2), ("ledger", 2), ("pattern", 3)])}


def cid(c):
    return f"{c['layer']}.{c['scope']}.{c['slug']}"


def load(d):
    return json.load(open(os.path.join(d, "lattice.json"), encoding="utf-8"))


def save(d, lat):
    json.dump(lat, open(os.path.join(d, "lattice.json"), "w", encoding="utf-8"), indent=2)


def find(lat, cell_id):
    return next((c for c in lat["cells"] if cid(c) == cell_id), None)


def _validated_at(lat, layer, scope):
    """Is there a validated/operating cell of `layer` at `scope`? (a same-scope upstream foothold)."""
    return any(c["layer"] == layer and c["scope"] == scope and c["maturity"] in SETTLED for c in lat["cells"])


def ready(lat, c):
    """A cell is dependency-ready iff its explicit depends_on are all validated, its verifier rubric (if any) is
    validated, and every upstream LAYER it requires has a validated foothold at its scope. Returns (bool, reasons)."""
    reasons = []
    for dep in c.get("depends_on", []):
        d = find(lat, dep)
        if d is None or d["maturity"] not in SETTLED:
            reasons.append(f"depends_on {dep} is {'absent' if d is None else d['maturity']}, not validated")
    v = c.get("verifier")
    if v:
        vc = find(lat, v)
        if vc is None or vc["maturity"] != "validated":
            reasons.append(f"verifier {v} is {'absent' if vc is None else vc['maturity']}, not validated (a cell advances only against a validated rubric)")
    for up in LAYER_DEPS.get(c["layer"], []):
        if not _validated_at(lat, up, c["scope"]):
            reasons.append(f"no validated {up} cell at scope {c['scope']} (partial order: {c['layer']} requires {up} upstream)")
    return (not reasons, reasons)


def scan(lat):
    """The gap set: cells at the frontier scope whose maturity is open (absent/defined/instantiated) or stale."""
    fs = lat.get("frontier_scope", "task")
    return [c for c in lat["cells"] if c["scope"] == fs and c["maturity"] in (ADVANCEABLE | {"stale"})]


def _probe_cost(lat, c):
    """Probe cost ≈ prior iterations for this layer/scope, read from the ledger when history exists, else 1."""
    led = lat.get("_ledger_cost", {})            # injected by the CLI from ledger.py; default-free in pure use
    return led.get(c["layer"], {}).get(c["scope"], 1) or 1


def rank(lat):
    """Order the dependency-ready gaps by priority ≈ (risk × unlock) ÷ probe-cost. Returns [(priority, cell, reasons)]."""
    gaps = scan(lat)
    # unlock = how many other cells declare this one as a dependency (out-degree of being depended-on).
    depended = {}
    for c in lat["cells"]:
        for dep in c.get("depends_on", []):
            depended[dep] = depended.get(dep, 0) + 1
    out = []
    for c in gaps:
        ok, reasons = ready(lat, c)
        if not ok:
            continue                              # not yet selectable — dependency filter
        risk = 4 - LAYER_RANK[c["layer"]]         # upstream layers concentrate risk (block more downstream)
        unlock = 1 + depended.get(cid(c), 0)
        priority = (risk * unlock) / _probe_cost(lat, c)
        out.append((round(priority, 3), c, reasons))
    out.sort(key=lambda t: -t[0])
    return out


def advance_validity(lat, cell_id):
    """Return (ok, reasons) — may an engine pass advance this cell right now?"""
    c = find(lat, cell_id)
    if c is None:
        return False, [f"no such cell: {cell_id}"]
    reasons = []
    if c.get("blocked"):
        reasons.append("cell is blocked (budget cap or no-progress signature) — surface to the compass, do not burn tokens")
    if c["maturity"] not in ADVANCEABLE:
        reasons.append(f"maturity {c['maturity']} is not advanceable (advanceable: {sorted(ADVANCEABLE)})")
    ok, dep_reasons = ready(lat, c)
    reasons += dep_reasons
    return (not reasons, reasons)


def propagate_staleness(lat, changed_cell_id, new_hash):
    """Flip every cell that was validated against an old hash of `changed_cell_id` to `stale`. Returns flipped ids."""
    flipped = []
    for c in lat["cells"]:
        va = c.get("validated_against", {})
        if changed_cell_id in va and va[changed_cell_id] != new_hash and c["maturity"] in SETTLED:
            c["maturity"] = "stale"
            flipped.append(cid(c))
    return flipped


def seed_lattice(project):
    """A first slice: an ontology + spec foothold at task scope, plus the rubric that will verify the spec."""
    return {
        "version": "1", "project": project, "created": "", "frontier_scope": "task",
        "cells": [
            {"layer": "ontology", "scope": "task", "slug": "domain", "maturity": "defined", "depends_on": []},
            {"layer": "spec", "scope": "task", "slug": "first-slice", "maturity": "defined",
             "depends_on": ["ontology.task.domain"], "verifier": "rubric.task.first-slice"},
            {"layer": "rubric", "scope": "task", "slug": "first-slice", "maturity": "defined",
             "depends_on": ["spec.task.first-slice"]},
            {"layer": "ledger", "scope": "task", "slug": "events", "maturity": "defined",
             "depends_on": ["ontology.task.domain"]},
        ],
    }


def _demo():
    """A synthetic lattice exercising the partial order + staleness, for the selftest."""
    return {
        "version": "1", "project": "demo", "frontier_scope": "task",
        "cells": [
            {"layer": "ontology", "scope": "task", "slug": "domain", "maturity": "validated", "depends_on": []},
            {"layer": "spec", "scope": "task", "slug": "x", "maturity": "validated",
             "depends_on": ["ontology.task.domain"], "validated_against": {"ontology.task.domain": "h1"}},
            {"layer": "rubric", "scope": "task", "slug": "x", "maturity": "defined", "depends_on": ["spec.task.x"]},
            {"layer": "spec", "scope": "task", "slug": "y", "maturity": "defined", "depends_on": []},
            {"layer": "rubric", "scope": "task", "slug": "y", "maturity": "defined", "depends_on": ["spec.task.y"]},
            {"layer": "methodology", "scope": "task", "slug": "loop", "maturity": "defined",
             "depends_on": [], "verifier": "rubric.task.x"},
        ],
    }


def selftest():
    fails = []
    def expect(cond, label):
        if not cond:
            fails.append(label)
    lat = _demo()

    gaps = {cid(c) for c in scan(lat)}
    expect("rubric.task.x" in gaps and "spec.task.y" in gaps, f"scan missed open cells: {gaps}")
    expect("ontology.task.domain" not in gaps, "scan returned a validated cell as a gap")

    # rubric.task.x is ready (its spec is validated); rubric.task.y is NOT (its spec is only defined) — the partial order.
    expect(ready(lat, find(lat, "rubric.task.x"))[0], "rubric.task.x should be ready (validated spec upstream)")
    expect(not ready(lat, find(lat, "rubric.task.y"))[0], "rubric.task.y should NOT be ready (rubric-before-validated-spec)")

    # advance against an unvalidated verifier is blocked (verifier-maturity precondition).
    ok, reasons = advance_validity(lat, "methodology.task.loop")
    expect(not ok and any("verifier" in r for r in reasons), f"advance should fail on unvalidated verifier: {reasons}")

    # rank yields the ready gaps only, ordered; the rubric-before-spec cell is filtered out.
    ranked = [cid(c) for _, c, _ in rank(lat)]
    expect("rubric.task.x" in ranked, "rank dropped a ready gap")
    expect("rubric.task.y" not in ranked, "rank included a not-ready cell (dependency filter failed)")

    # staleness propagation: change ontology's hash → spec.task.x (validated against h1) flips to stale.
    flipped = propagate_staleness(lat, "ontology.task.domain", "h2")
    expect("spec.task.x" in flipped and find(lat, "spec.task.x")["maturity"] == "stale", f"staleness did not propagate: {flipped}")

    # the seed lattice is structurally sound (every cell well-typed).
    seed = seed_lattice("p")
    expect(all(c["layer"] in LAYERS and c["scope"] in SCOPES for c in seed["cells"]), "seed lattice has an ill-typed cell")

    if fails:
        sys.stderr.write("lattice selftest: FAIL\n")
        for f in fails:
            sys.stderr.write(f"  - {f}\n")
        return 1
    print("lattice selftest: OK (scan finds gaps; partial order blocks rubric-before-validated-spec; verifier-maturity "
          "precondition enforced; rank dependency-filters; staleness propagates as a graph computation)")
    return 0


def _dir(argv):
    return argv[argv.index("--dir") + 1] if "--dir" in argv else ".harness"


def main(argv):
    if argv and argv[0] == "selftest":
        return selftest()
    d = _dir(argv)
    pos = [a for a in argv if not a.startswith("--") and a != d]
    if pos and pos[0] == "init":
        os.makedirs(d, exist_ok=True)
        lat = seed_lattice(pos[1] if len(pos) > 1 else os.path.basename(os.getcwd()))
        save(d, lat)
        print(f"seeded {os.path.join(d, 'lattice.json')} — {len(lat['cells'])} cells (ontology+spec+rubric+ledger task slice)")
        return 0
    try:
        lat = load(d)
    except OSError:
        print(f"no lattice at {d}/lattice.json — run `lattice.py init <project> --dir {d}` first", file=sys.stderr)
        return 2
    if pos and pos[0] == "scan":
        for c in scan(lat):
            print(f"  {c['maturity']:12} {cid(c)}")
        print(f"\n{len(scan(lat))} open/stale cell(s) at frontier scope {lat.get('frontier_scope','task')}")
        return 0
    if pos and pos[0] == "rank":
        ranked = rank(lat)
        for p, c, _ in ranked:
            print(f"  {p:7.3f}  {cid(c)}  ({c['maturity']})")
        print(f"\n{len(ranked)} ready, ranked cell(s) — priority ≈ (risk × unlock) ÷ probe-cost")
        return 0
    if len(pos) >= 2 and pos[0] == "validity":
        ok, reasons = advance_validity(lat, pos[1])
        print(f"{'CAN ADVANCE' if ok else 'BLOCKED'}: {pos[1]}")
        for r in reasons:
            print(f"  - {r}")
        return 0 if ok else 1
    if len(pos) >= 3 and pos[0] == "stale":
        flipped = propagate_staleness(lat, pos[1], pos[2])
        save(d, lat)
        print(f"propagate-staleness from {pos[1]}: flipped {len(flipped)} cell(s) → stale: {flipped}")
        return 0
    print(__doc__.split("Usage:")[1].split("Stdlib")[0].strip(), file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
