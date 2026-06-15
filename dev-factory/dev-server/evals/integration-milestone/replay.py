#!/usr/bin/env python3
"""replay.py — the integration milestone: the kit ACTUALLY drives the loop (closing the declared-but-not-wired gap).

Earlier milestones proved the spine with a generic worker + an asset-exists check. This proves the layer
that was specced + schema'd but inert: when a kit is bound, the dispatcher ASSEMBLES the execution plan
from the kit's dispatch policy (not a generic single-pass), picks the worker from the roster, runs the
kit's REAL rubric verifier (spec-quality-check, not 'a file exists'), and materializes the activity lens.

Falsified if any breaks:
  I1  the execution plan is ASSEMBLED from the kit's dispatch policy — a spec unit runs as the policy's
      evaluator-optimizer/team shape, NOT the default single-pass. (dispatch-policy is consumed, not ignored.)
  I2  the roster picks the right worker — a spec cell is advanced by spec-architect.
  I3  the kit's REAL verifier runs: a STRUCTURED spec clears spec-quality's [gate] dimensions and validates.
  I4  that verifier has TEETH a file-exists check lacks: a PROSE spec asset FAILS spec-quality-check, so the
      ticket does NOT reach done — 'validated' now means the family's rubric, not 'a file is present'.
  I5  the activity/agent lens is populated (agent, kind, orchestration_shape) from the run.

Exit 0 = the kit drives the loop. Stdlib only; Python 3.8+. Answer key in README.md.
"""
import json
import os
import sys
import tempfile

_HERE = os.path.dirname(os.path.abspath(__file__))
_SERVER = os.path.dirname(os.path.dirname(_HERE))
_DF = os.path.dirname(_SERVER)
os.environ["DEV_FACTORY_KIT"] = os.path.join(_DF, "dev-kit-corpus")   # bind the corpus family
sys.path.insert(0, _SERVER)
import api as _api          # noqa: E402
import dispatch as _disp    # noqa: E402
sys.path.insert(0, _api._store._KERNEL_BIN)
import lattice as _lat      # noqa: E402

CELL = "spec.system.feature"
STRUCTURED = {
    "title": "First feature", "cell": CELL,
    "acceptance_criteria": [{"id": "c1", "check": "POST /x returns 200"}, {"id": "c2", "rubric_cell": "rubric.system.test"}],
    "non_goals": ["password reset", "SSO"],
    "binds_rubric": "rubric.system.spec-quality",
}


def _seed(d, structured):
    _api.init_instance(d)
    _api.seed_cell(d, "rubric", "system", "spec-quality", maturity="validated", signal_refs=["signals/rubric.system.spec-quality/seed.json"])
    _api.seed_cell(d, "spec", "system", "feature", maturity="instantiated", asset_ref="spec/feature.md")
    os.makedirs(os.path.join(d, "spec"), exist_ok=True)
    body = ("# First feature\n\n```json\n" + json.dumps(STRUCTURED, indent=2) + "\n```\n") if structured \
           else "# First feature\n\nA prose spec — words, but nothing a rubric can mechanically gate.\n"
    open(os.path.join(d, "spec", "feature.md"), "w").write(body)


def _ticket(d, srv):
    t = _api.create_ticket(d, "feature", "validate the feature spec", target_cell=CELL,
                           target_transition={"from": "instantiated", "to": "validated"},
                           acceptance={"rubric_cell": "rubric.system.spec-quality"},
                           budget={"iterations": 4, "tokens": 80000}, priority={"risk": 0.9})  # high → the team rule
    _api.transition_ticket(d, t["id"], "active", srv)
    return t


def run():
    fails = []
    def check(cond, label):
        print(f"  {'PASS' if cond else 'FAIL'}  {label}")
        if not cond:
            fails.append(label)
    srv = {"kind": "server", "id": "dev-server"}

    print("· a STRUCTURED spec, the corpus kit bound — the kit drives the dispatch")
    with tempfile.TemporaryDirectory() as root:
        d = os.path.join(root, ".agents/dev-factory")
        _seed(d, structured=True)
        t = _ticket(d, srv)
        ok, ticket, msg = _disp.dispatch_unit(d, _api.get_ticket(d, t["id"]), _disp.MockAdapter(), srv, tier=2, auto_validate=True)
        acts = _api.list_activities(d)
        a = acts[0] if acts else {}
        check(a.get("orchestration_shape") == "evaluator-optimizer",
              f"I1: execution plan ASSEMBLED from the kit policy (got {a.get('orchestration_shape')!r}, not the default single-pass)")
        check(a.get("agent") == "spec-architect", f"I2: roster picked spec-architect (got {a.get('agent')!r})")
        check(ok and _lat.find(_lat.load(d), CELL)["maturity"] == "validated",
              f"I3: the structured spec cleared the kit's REAL spec-quality verifier → validated ({msg})")
        check(a.get("kind") == "validate" and a.get("status") == "completed", "I5: the activity lens is populated from the run")

    print("· the SAME pipeline with a PROSE spec — the real rubric must REJECT it")
    with tempfile.TemporaryDirectory() as root:
        d = os.path.join(root, ".agents/dev-factory")
        _seed(d, structured=False)
        t = _ticket(d, srv)
        ok, ticket, msg = _disp.dispatch_unit(d, _api.get_ticket(d, t["id"]), _disp.MockAdapter(), srv, tier=2, auto_validate=True)
        check(not ok and _lat.find(_lat.load(d), CELL)["maturity"] == "instantiated",
              f"I4: a PROSE spec FAILS spec-quality-check — NOT validated (a file-exists check would have passed it). msg={msg[:80]}")

    print()
    if fails:
        print(f"integration-milestone: GAP OPEN — {len(fails)} check(s) failed:")
        for f in fails:
            print(f"  - {f}")
        return 1
    print("integration-milestone: OK — with a kit bound, the dispatcher assembles the execution plan from the "
          "kit's dispatch policy, the roster picks spec-architect, and the kit's REAL spec-quality rubric runs: a "
          "structured spec validates, a prose one is rejected. 'validated' means the family's rubric, not 'a file "
          "exists' — the execution-strategy + rubric layers are wired, not just declared.")
    return 0


if __name__ == "__main__":
    sys.exit(run())
