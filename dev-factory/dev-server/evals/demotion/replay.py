#!/usr/bin/env python3
"""replay.py — mechanical demotion has teeth (TDD §14.2 REQ-SAFE-004): a caught false-pass revokes autonomy.

The autonomy unit-test proves the tier math; this proves the OPERATIONAL consequence end-to-end: the very
same heartbeat that drove a slice to `done` unattended at Tier 2 stops at `in-review` once a refuter catches
a false pass — and NO human approved that demotion. Autonomy is revocable by construction.

Falsified if any breaks:
  D1  pre-incident, the family is Tier 2 and the heartbeat drives a ready slice to `done` unattended.
  D2  a refuter that DISAGREES with the critic (a caught false pass) MECHANICALLY demotes the family to <=1
      and flags its verifier `stale` — recorded in the ledger, with no human in the demotion path.
  D3  post-incident, the SAME heartbeat dispatches the next ready slice but stops at `in-review` (Tier 1),
      NOT `done` — autonomy was revoked, not merely flagged.

Exit 0 = demotion has teeth. Stdlib only; Python 3.8+. Answer key in README.md.
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_SERVER = os.path.dirname(os.path.dirname(_HERE))
sys.path.insert(0, _SERVER)
import api as _api          # noqa: E402
import heartbeat as _hb     # noqa: E402
sys.path.insert(0, _api._store._KERNEL_BIN)
import lattice as _lat      # noqa: E402
import ledger as _led       # noqa: E402
import autonomy as _auto    # noqa: E402


def run():
    import tempfile
    fails = []
    def check(cond, label):
        print(f"  {'PASS' if cond else 'FAIL'}  {label}")
        if not cond:
            fails.append(label)

    with tempfile.TemporaryDirectory() as root:
        d = os.path.join(root, ".agents/dev-factory")
        _api.init_instance(d)
        human = {"kind": "human", "id": "operator"}
        _api.seed_cell(d, "rubric", "task", "r", maturity="validated", signal_refs=["signals/rubric.task.r/seed.json"])
        for slug in ("a", "b"):
            _api.seed_cell(d, "spec", "task", slug, maturity="instantiated", asset_ref=f"spec/{slug}.md")
            os.makedirs(os.path.join(d, "spec"), exist_ok=True)
            open(os.path.join(d, "spec", f"{slug}.md"), "w").write(f"# {slug}\n")

        A = _api.create_ticket(d, "feature", "advance A", target_cell="spec.task.a",
                               target_transition={"from": "instantiated", "to": "validated"},
                               acceptance={"rubric_cell": "rubric.task.r"}, budget={"iterations": 2, "tokens": 40000})
        B = _api.create_ticket(d, "feature", "advance B (needs A)", target_cell="spec.task.b",
                               target_transition={"from": "instantiated", "to": "validated"},
                               acceptance={"rubric_cell": "rubric.task.r"}, budget={"iterations": 2, "tokens": 40000},
                               dependencies={"cells_ready": ["spec.task.a"]})
        _api.transition_ticket(d, A["id"], "active", human)
        _api.transition_ticket(d, B["id"], "active", human)

        # earn Tier 2: validated verifier + a clean refuter check + an armed budget
        _hb.arm(d, max_dispatches=9, deadline_s=3600)
        _auto.record_refuter_check(d, "rubric.task.r", agreed=True)
        check(_auto.tier_for(d) == 2, f"family earned Tier 2; got {_auto.tier_for(d)}")

        print("· D1 — at Tier 2 the heartbeat drives A to done UNATTENDED")
        s1 = _hb.on_tick(d, max_concurrency=1)
        check(s1.get("tier") == 2 and _api.get_ticket(d, A["id"])["state"] == "done",
              "D1: tick drove A to done unattended at Tier 2")
        check(_lat.find(_lat.load(d), "spec.task.a")["maturity"] == "validated", "A's cell validated")

        print("· D2 — a refuter catches a false pass on A's cell → MECHANICAL demotion (no human)")
        tier_after = _auto.record_refuter_check(d, "spec.task.a", agreed=False)   # the refuter DISAGREES
        check(tier_after <= 1 and _auto.tier_for(d) <= 1, f"family not demoted after a caught false pass: tier {tier_after}")
        rub = next(c for c in _lat.load(d)["cells"] if c["layer"] == "rubric")
        check(rub["maturity"] == "stale", "the implicated verifier was not flagged stale")
        evs = {e["event"] for e in _led.read(d)}
        check("incident" in evs and "demote" in evs, "the incident + mechanical demotion were not ledgered")
        # no human actor drove the demotion
        demote_actors = {e["actor"]["kind"] for e in _led.read(d) if e["event"] in ("incident", "demote")}
        check("human" not in demote_actors, "a human was in the demotion path (it must be mechanical)")

        print("· D3 — the SAME heartbeat now REFUSES to dispatch B — autonomy revoked to Tier 0 (verifier staled)")
        s2 = _hb.on_tick(d, max_concurrency=1)   # B is now ready (A validated), but the family is demoted
        # the demotion staled the only verifier, so Tier 1 (which REQUIRES a validated verifier) isn't met
        # either — the family falls all the way to Tier 0 (fully attended) until the verifier is re-validated.
        check(s2.get("tier") == 0, f"demotion did not reach Tier 0 (verifier staled); tier {s2.get('tier')}")
        bstate = _api.get_ticket(d, B["id"])["state"]
        check(bstate == "active", f"D3: demoted heartbeat dispatched B anyway (it is {bstate}) — autonomy not revoked")
        check(_lat.find(_lat.load(d), "spec.task.b")["maturity"] != "validated",
              "B was validated despite the demotion (autonomy not actually revoked)")

    print()
    if fails:
        print(f"demotion: NO TEETH — {len(fails)} check(s) failed:")
        for f in fails:
            print(f"  - {f}")
        return 1
    print("demotion: OK — the same heartbeat that drove a slice to done unattended at Tier 2 REFUSES to dispatch "
          "the next once a refuter catches a false pass (the verifier is staled → Tier 0); the demotion + "
          "stale-verifier are ledgered with no human in the path. Autonomy is earned, measured, and mechanically "
          "revocable.")
    return 0


if __name__ == "__main__":
    sys.exit(run())
