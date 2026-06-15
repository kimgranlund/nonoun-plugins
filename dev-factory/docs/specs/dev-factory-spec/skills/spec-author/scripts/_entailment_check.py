#!/usr/bin/env python3
"""_entailment_check.py — deterministic decomposition-soundness check.

Computation routes to code, never to inference. Given a parent spec and a proposed
decomposition (child cells + ticket batch), verify that satisfying the children would
entail satisfying the parent, and that the constituent parts are well formed for the
operating loop.

Exit 0 with a JSON proof on success; exit 1 with the gap list on failure. The result is
the signal artifact backing the `decomposition-entailment` rubric gate.
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
    gaps: list[str] = []
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


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: _entailment_check.py parent.json decomposition.json", file=sys.stderr)
        return 2
    parent = json.load(open(sys.argv[1]))
    decomposition = json.load(open(sys.argv[2]))
    proof = check(parent, decomposition)
    print(json.dumps(proof, indent=2))
    return 0 if proof["entailed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
