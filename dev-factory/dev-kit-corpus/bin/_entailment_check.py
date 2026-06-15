#!/usr/bin/env python3
"""_entailment_check.py — deterministic decomposition-soundness check (a library + a selftest).

Computation routes to code, never to inference. Given a parent spec and a proposed decomposition (child
cells + ticket batch), verify that satisfying the children would entail satisfying the parent, and that the
constituent parts are well formed for the operating loop. spec-quality-check.py imports `check()` to run the
`decomposition-entailment` gate; on the command line it prints a JSON proof and exits 0 (entailed) / 1 (gap).

Usage:
  _entailment_check.py parent.json decomposition.json   # JSON proof; exit 0 = entailed, 1 = gap
  _entailment_check.py selftest                          # exit 0 = ok
Stdlib only; Python 3.8+.
"""
from __future__ import annotations
import json
import sys

# Layer partial order: an edge child->parent_layer is legal only if child_layer is
# allowed to depend on parent_layer. Encoded as the set of layers each layer may depend on.
PARTIAL_ORDER = {
    "ontology": set(),
    "spec": {"ontology"},
    "rubric": {"ontology", "spec"},
    "policy": {"ontology", "spec"},
    "capability": {"ontology", "spec"},
    "methodology": {"ontology", "spec", "rubric", "policy", "capability"},
    "protocol": {"ontology", "spec", "rubric", "policy", "capability"},
    "ledger": {"ontology", "spec"},
    "pattern": {"ontology", "spec", "rubric", "policy", "capability",
                "methodology", "protocol", "ledger"},
}


def layer_of(cell_id: str) -> str:
    return cell_id.split(".", 1)[0]


def check(parent: dict, decomposition: dict) -> dict:
    """parent: {criteria: [criterion_id,...]}
    decomposition: {cells: [{id, acceptance_rubric?}], tickets: [{target_cell,
                    acceptance:{rubric_cell}, covers:[criterion_id,...]}],
                    edges: [{from_cell, to_cell}]}
    """
    gaps: list = []
    cells = {c["id"]: c for c in decomposition.get("cells", [])}
    tickets = decomposition.get("tickets", [])
    edges = decomposition.get("edges", [])

    # 1. Coverage: every parent criterion is covered by >=1 ticket's `covers`.
    covered = set()
    for t in tickets:
        covered.update(t.get("covers", []))
    for crit in parent.get("criteria", []):
        if crit not in covered:
            gaps.append(f"uncovered-criterion: parent criterion '{crit}' maps to no child")

    # 2. Orphans: every `covers` entry refers to a real parent criterion.
    parent_set = set(parent.get("criteria", []))
    for t in tickets:
        for crit in t.get("covers", []):
            if crit not in parent_set:
                gaps.append(f"orphan-coverage: ticket '{t.get('target_cell')}' claims "
                            f"criterion '{crit}' not present in parent")

    # 3. Binding: every ticket's acceptance binds to a rubric cell that exists.
    for t in tickets:
        rc = (t.get("acceptance") or {}).get("rubric_cell")
        if not rc:
            gaps.append(f"unbound-acceptance: ticket '{t.get('target_cell')}' has no "
                        f"rubric_cell")
        elif layer_of(rc) != "rubric":
            gaps.append(f"bad-binding: ticket '{t.get('target_cell')}' acceptance "
                        f"'{rc}' is not a rubric cell")

    # 4. Target existence: every ticket target_cell is in the seed delta.
    for t in tickets:
        tc = t.get("target_cell")
        if tc not in cells:
            gaps.append(f"missing-target: ticket target '{tc}' absent from seed delta")

    # 5. Partial-order legality of dependency edges.
    for e in edges:
        cl, pl = layer_of(e["from_cell"]), layer_of(e["to_cell"])
        if cl in PARTIAL_ORDER and pl not in PARTIAL_ORDER[cl] and cl != pl:
            gaps.append(f"illegal-edge: {cl} cell may not depend on {pl} cell "
                        f"({e['from_cell']} -> {e['to_cell']})")

    return {
        "entailed": not gaps,
        "criteria_total": len(parent_set),
        "criteria_covered": len(covered & parent_set),
        "cells": len(cells),
        "tickets": len(tickets),
        "gaps": gaps,
    }


def selftest():
    fails = []
    parent = {"criteria": ["c1", "c2"]}
    sound = {
        "cells": [{"id": "spec.task.a"}, {"id": "spec.task.b"}],
        "tickets": [
            {"target_cell": "spec.task.a", "acceptance": {"rubric_cell": "rubric.task.a"}, "covers": ["c1"]},
            {"target_cell": "spec.task.b", "acceptance": {"rubric_cell": "rubric.task.b"}, "covers": ["c2"]},
        ],
        "edges": [{"from_cell": "rubric.task.a", "to_cell": "spec.task.a"}],
    }
    if not check(parent, sound)["entailed"]:
        fails.append("rejected a sound, fully-covering decomposition")

    # uncovered parent criterion -> gap
    uncovered = json.loads(json.dumps(sound))
    uncovered["tickets"] = uncovered["tickets"][:1]  # drop the ticket covering c2
    r = check(parent, uncovered)
    if r["entailed"] or not any("uncovered-criterion" in g for g in r["gaps"]):
        fails.append("accepted a decomposition leaving a parent criterion uncovered")

    # acceptance not bound to a rubric cell -> gap
    unbound = json.loads(json.dumps(sound))
    unbound["tickets"][0]["acceptance"] = {"rubric_cell": "spec.task.a"}  # not a rubric.* cell
    r = check(parent, unbound)
    if r["entailed"] or not any("bad-binding" in g for g in r["gaps"]):
        fails.append("accepted a child acceptance not bound to a rubric cell")

    # illegal partial-order edge (spec depending on pattern) -> gap
    illegal = json.loads(json.dumps(sound))
    illegal["edges"] = [{"from_cell": "spec.task.a", "to_cell": "pattern.system.x"}]
    r = check(parent, illegal)
    if r["entailed"] or not any("illegal-edge" in g for g in r["gaps"]):
        fails.append("accepted a partial-order-illegal dependency edge")

    if fails:
        sys.stderr.write("_entailment_check selftest: FAIL\n")
        for f in fails:
            sys.stderr.write(f"  - {f}\n")
        return 1
    print("_entailment_check selftest: OK (a sound decomposition entails the parent; an uncovered criterion, "
          "an unbound acceptance, and a partial-order-illegal edge each produce a gap)")
    return 0


def main(argv) -> int:
    if not argv:
        sys.stderr.write("usage: _entailment_check.py parent.json decomposition.json | selftest\n")
        return 2
    if argv[0] == "selftest":
        return selftest()
    if len(argv) != 2:
        sys.stderr.write("usage: _entailment_check.py parent.json decomposition.json | selftest\n")
        return 2
    parent = json.load(open(argv[0]))
    decomposition = json.load(open(argv[1]))
    proof = check(parent, decomposition)
    print(json.dumps(proof, indent=2))
    return 0 if proof["entailed"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
