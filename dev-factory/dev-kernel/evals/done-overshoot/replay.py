#!/usr/bin/env python3
"""replay.py — DF-7: an author ticket whose cell a verifier already OVERSHOT closes as a satisfied no-op.

The factory's intended order is two tickets per build: an AUTHOR ticket (`defined -> instantiated`, the
worker writes the asset) then a VALIDATE ticket (`instantiated -> validated`, the verifier mints the signal).
But `validate.py` auto-steps `defined -> instantiated -> validated` in ONE pass, so a validate-first run drives
the cell straight to `validated`, OVERSHOOTING the author ticket's `instantiated` target. Before the fix, closing
that author ticket `done` was denied — `_author_advance` ran a bare `transition_ok(validated, instantiated)`
(False: `validated` never steps back to `instantiated`) and reported "illegal maturity advance" — wedging a
ticket whose authoring work was demonstrably already done.

The fix: `_author_advance` recognizes a target the cell has already REACHED on the linear maturation axis
(`lattice.reached`, absent -> defined -> instantiated -> validated -> operating) as a SATISFIED no-op, distinct
from an illegal advance. This replay proves the fix is TIGHT — it accepts the legitimate overshoot WITHOUT
becoming a blanket bypass:

  O1  an author ticket (`defined->instantiated`) on a cell a verifier overshot to `validated` CLOSES `done`,
      and the no-op does NOT mutate the cell's maturity (it stays `validated`).
  O2  the fix is not permissive: an author ticket on an OFF-AXIS cell (`deprecated`) — which `reached()` never
      treats as "beyond" — is STILL denied as an illegal advance. The hole stays closed.
  O3  the recognizer itself: `reached()` is at-or-beyond on the PROGRESS axis, and False for off-axis states.

Exit 0 = the overshoot closes AND a genuinely illegal advance still fails. Stdlib only; Python 3.8+.
Answer key in README.md.
"""
import os
import sys
import tempfile

_BIN = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "bin")
sys.path.insert(0, _BIN)
import lattice as _lat       # noqa: E402
import lifecycle as _lc      # noqa: E402
import ledger as _led        # noqa: E402

SRV = {"kind": "server", "id": "srv"}
TS = {"created": "2026-06-15T00:00:00+00:00", "updated": "2026-06-15T00:00:00+00:00"}


def _author_ticket(slug):
    """An AUTHOR ticket: defined -> instantiated, acceptance bound to the validated rubric `rubric.task.r`."""
    return {"id": _led.ulid("tkt-"), "type": "feature", "title": f"author {slug}", "body": "", "state": "draft",
            "target_cell": f"spec.task.{slug}", "target_transition": {"from": "defined", "to": "instantiated"},
            "acceptance": {"rubric_cell": "rubric.task.r"}, "budget": {"iterations": 2, "tokens": 1000},
            "dependencies": {}, "provenance": {"created_by": "h", "ledger_refs": []},
            "timestamps": dict(TS)}


def _drive_to_review(d, t, check, tag):
    for to in ("active", "claimed", "in-progress", "in-review"):
        ok, t, msg = _lc.transition(d, t, to, SRV)
        check(ok, f"{tag}: {to} reached ({msg if not ok else 'ok'})")
    return t


def run():
    fails = []
    def check(cond, label):
        print(f"  {'PASS' if cond else 'FAIL'}  {label}")
        if not cond:
            fails.append(label)

    with tempfile.TemporaryDirectory() as root:
        d = os.path.join(root, ".agents/dev-factory")
        _lat.scaffold(d)
        _lat.save(d, {"cells": [
            {"layer": "rubric", "scope": "task", "slug": "r", "maturity": "validated",
             "signal_refs": ["signals/rubric.task.r/seed.json"], "depends_on": []},
            # `overshot`: the verifier already drove it to validated (the DF-7 case)
            {"layer": "spec", "scope": "task", "slug": "overshot", "maturity": "validated",
             "asset_ref": "spec/overshot.md", "signal_refs": ["signals/spec.task.overshot/v.json"], "depends_on": []},
            # `dead`: an off-axis cell — reached() must NOT treat it as "beyond" instantiated
            {"layer": "spec", "scope": "task", "slug": "dead", "maturity": "deprecated",
             "asset_ref": "spec/dead.md", "signal_refs": [], "depends_on": []},
        ]})
        os.makedirs(os.path.join(d, "spec"), exist_ok=True)
        for s in ("overshot", "dead"):
            open(os.path.join(d, "spec", f"{s}.md"), "w").write(f"# {s}\n")

        print("· O1 — an author ticket on an overshot (validated) cell CLOSES as a satisfied no-op")
        t = _drive_to_review(d, _author_ticket("overshot"), check, "O1")
        ok, t, msg = _lc.transition(d, t, "done", SRV)   # no verifier — authoring advance
        check(ok, f"O1: author ticket on an already-validated cell closes done ({msg if not ok else 'closed'})")
        cell = _lat.find(_lat.load(d), "spec.task.overshot")
        check(cell["maturity"] == "validated", f"O1: the no-op did NOT mutate maturity (stayed {cell['maturity']})")
        check(t["state"] == "done", "O1: the author ticket reached done")

        print("· O2 — the fix is TIGHT: an author ticket on an OFF-AXIS (deprecated) cell is STILL denied")
        t2 = _drive_to_review(d, _author_ticket("dead"), check, "O2")
        ok2, t2, msg2 = _lc.transition(d, t2, "done", SRV)
        check(not ok2 and "illegal" in msg2.lower(),
              f"O2: a genuinely illegal advance (deprecated->instantiated) is rejected, not bypassed ({msg2})")
        dead = _lat.find(_lat.load(d), "spec.task.dead")
        check(dead["maturity"] == "deprecated", "O2: the off-axis cell was not advanced")

        print("· O3 — the recognizer: reached() is at-or-beyond on the PROGRESS axis, False off-axis")
        check(_lat.reached("validated", "instantiated") and _lat.reached("operating", "defined"),
              "O3: reached() accepts a cell at or past the target")
        check(not _lat.reached("defined", "validated"), "O3: reached() rejects a cell short of the target")
        check(not _lat.reached("deprecated", "instantiated") and not _lat.reached("stale", "defined"),
              "O3: reached() never treats an off-axis state as 'beyond'")

    print()
    if fails:
        print(f"done-overshoot: FAIL — {len(fails)} check(s) failed:")
        for f in fails:
            print(f"  - {f}")
        return 1
    print("done-overshoot: OK — an author ticket whose cell a verifier overshot to validated closes as a "
          "satisfied no-op (maturity untouched), while a genuinely illegal advance (off-axis) is STILL denied. "
          "The DF-7 wedge is gone without opening a permissive hole in the morphism.")
    return 0


if __name__ == "__main__":
    sys.exit(run())
