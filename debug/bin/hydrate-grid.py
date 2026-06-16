#!/usr/bin/env python3
"""hydrate-grid.py — seed a FULL 9x5 coverage lattice into a run instance.

A deliberate COVERAGE demo (distinct from a lean app build, which is sparse by design): one honest cell at every
(layer x scope) coordinate the harness supports, all at `instantiated` with an advance ticket, so the mock build
drives the WHOLE grid to `validated` in dependency WAVES set by the layer partial order:

    ontology  ->  spec, ledger  ->  rubric, policy, capability, pattern  ->  methodology, protocol

This shows the harness's complete coordinate space filling out on the dashboard. Single-file cells throughout
(no kit bound) so every cell uses the asset-exists verifier and the fill is uniform + reliable.

    python3 debug/bin/hydrate-grid.py <name>
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C  # noqa: E402

LAYERS = ["ontology", "spec", "rubric", "policy", "capability", "methodology", "protocol", "ledger", "pattern"]
SCOPES = ["call", "task", "workflow", "system", "fleet"]

# one honest cell-type per (layer x scope). Slugs are unique WITHIN a layer (the asset path is `{layer}/{slug}.md`).
GRID = {
    "ontology":    {"call": "token",            "task": "card",          "workflow": "deal",          "system": "app",         "fleet": "domain"},
    "spec":        {"call": "shuffle-contract", "task": "card-contract", "workflow": "move",          "system": "app",         "fleet": "charter"},
    "rubric":      {"call": "unit",             "task": "card-quality",  "workflow": "flow-quality",  "system": "ship",        "fleet": "portfolio"},
    "policy":      {"call": "effort",           "task": "purity",        "workflow": "parallelism",   "system": "dispatch",    "fleet": "budget"},
    "capability":  {"call": "shuffle",          "task": "move-validator","workflow": "deal-sequence", "system": "app",         "fleet": "orchestrate"},
    "methodology": {"call": "prompt",           "task": "test",          "workflow": "review",        "system": "build",       "fleet": "scale"},
    "protocol":    {"call": "invoke",           "task": "claim",         "workflow": "handoff",       "system": "integration", "fleet": "coordinate"},
    "ledger":      {"call": "usage",            "task": "audit",         "workflow": "trace",         "system": "provenance",  "fleet": "fleet-audit"},
    "pattern":     {"call": "one-shot",         "task": "pure-module",   "workflow": "tracer-bullet", "system": "app-shell",   "fleet": "regeneration"},
}


def main(argv):
    name = argv[0] if argv else "full-grid"
    inst = C.instance_dir(name)
    api = C._import_api()
    api.init_instance(inst)  # idempotent
    srv = {"kind": "server", "id": "dev-server"}
    import json as _json
    seeded = ticketed = failed = 0

    # The rubric ROW is the BOOTSTRAP: the kernel refuses to advance any cell whose doneness is not a *validated*
    # rubric (the anti-reward-hacking gate). So the 5 rubric cells (one per scope) are seeded already-validated with
    # a seed signal, and every other cell binds its scope's rubric. (This mirrors the cold-start, which seeds the
    # milestone rubrics validated.) The rubric row starts green; the other 8 layers animate from instantiated.
    scope_rubric = {}
    for scope in SCOPES:
        slug = GRID["rubric"][scope]
        cid = f"rubric.{scope}.{slug}"
        sig_rel = f"signals/{cid}/seed.json"
        sig_abs = os.path.join(inst, sig_rel)
        os.makedirs(os.path.dirname(sig_abs), exist_ok=True)
        _json.dump({"cell": cid, "verdict": "pass", "source": "bootstrap-seed",
                    "note": "coverage-demo bootstrap rubric"}, open(sig_abs, "w"), indent=2)
        api.seed_cell(inst, "rubric", scope, slug, maturity="validated", signal_refs=[sig_rel])
        scope_rubric[scope] = cid
        seeded += 1

    # the other 8 layers: instantiated, each bound to its scope's bootstrap rubric, with an advance ticket.
    for layer in LAYERS:
        if layer == "rubric":
            continue
        for scope in SCOPES:
            slug = GRID[layer][scope]
            cid = f"{layer}.{scope}.{slug}"
            api.seed_cell(inst, layer, scope, slug, maturity="instantiated", asset_ref=f"{layer}/{slug}.md")
            seeded += 1
            tk = api.create_ticket(inst, "feature", f"advance {cid}", target_cell=cid,
                                   target_transition={"from": "instantiated", "to": "validated"},
                                   acceptance={"rubric_cell": scope_rubric[scope]},
                                   budget={"iterations": 2, "tokens": 50000})
            ok, _t, msg = api.transition_ticket(inst, tk["id"], "active", srv)
            if ok:
                ticketed += 1
            else:
                failed += 1
                print(f"  ! {cid}: {msg}", file=sys.stderr)
    api._store.rebuild(inst)
    print(f"hydrated {seeded} cells = {len(LAYERS)} layers x {len(SCOPES)} scopes; "
          f"5 bootstrap rubrics validated, {ticketed} advance tickets active"
          + (f"; {failed} failed" if failed else ""))
    print("the mock build validates them in waves: ontology -> spec/ledger -> policy/capability/pattern -> methodology/protocol")
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
