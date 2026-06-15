#!/usr/bin/env python3
"""replay.py — the Fly milestone (TDD §19): the kernel/kit boundary holds + Tier 3 lights-out is reachable.

Fly is the dark factory: lights-out at fleet scope, with the kernel/kit boundary proven by a SECOND kit.
This asserts the two structural preconditions for that:

  F1  the boundary's FALSIFICATION TEST: two different families — dev-kit-corpus and dev-kit-app — both
      conform against ONE unchanged dev-kernel. Adding the second family required ZERO kernel edits; a kit
      that needed the kernel changed, or shipped a kernel file, would fail `check-kit-conform`.
  F2  Tier 3 (scheduled / lights-out) is REACHABLE — but only earned: a sustained clean independent-refuter
      track record, a hermetic sandbox, and a tamper-evident audit trail. Absent any one, the family stays
      at Tier 2. Autonomy at the top of the ladder is still measured, never asserted.

Exit 0 = Fly's preconditions hold. Stdlib only; Python 3.8+. Answer key in README.md.
"""
import os
import subprocess
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_SERVER = os.path.dirname(os.path.dirname(_HERE))
_DF = os.path.dirname(_SERVER)
sys.path.insert(0, _SERVER)
import api as _api          # noqa: E402
sys.path.insert(0, _api._store._KERNEL_BIN)
import lattice as _lat      # noqa: E402
import autonomy as _auto    # noqa: E402
import ledger as _led       # noqa: E402

_KC = os.path.join(_DF, "dev-kernel", "bin", "check-kit-conform.py")


def run():
    import tempfile
    import datetime
    fails = []
    def check(cond, label):
        print(f"  {'PASS' if cond else 'FAIL'}  {label}")
        if not cond:
            fails.append(label)

    print("· F1 — the kernel/kit boundary: two families conform against ONE unchanged kernel")
    for kit in ("dev-kit-corpus", "dev-kit-app"):
        r = subprocess.run(["python3", _KC, "kit", os.path.join(_DF, kit)], capture_output=True, text=True)
        check(r.returncode == 0, f"F1: {kit} binds the kernel cleanly (zero kernel edits)")
    # neither kit ships a kernel bin/schema (the structural boundary)
    leaked = []
    for kit in ("dev-kit-corpus", "dev-kit-app"):
        for root, _dirs, files in os.walk(os.path.join(_DF, kit)):
            for f in files:
                if f in {"lattice.py", "validate.py", "lifecycle.py", "compass.py", "ledger.py", "autonomy.py", "cell.schema.json"}:
                    leaked.append(f"{kit}/{f}")
    check(not leaked, f"F1: no kit forks a kernel file (boundary intact); leaks={leaked}")

    print("· F2 — Tier 3 lights-out is REACHABLE, but only when earned")
    with tempfile.TemporaryDirectory() as root:
        d = os.path.join(root, ".agents/dev-factory")
        _lat.scaffold(d)
        _lat.save(d, {"cells": [{"layer": "rubric", "scope": "system", "slug": "r", "maturity": "validated",
                                 "depends_on": [], "signal_refs": ["x"]}]})
        os.makedirs(os.path.join(d, "run"), exist_ok=True)
        import json
        now = datetime.datetime(2026, 6, 14, tzinfo=datetime.timezone.utc)
        json.dump({"start_ts": now.isoformat()}, open(os.path.join(d, "run", "heartbeat.json"), "w"))

        # a SUSTAINED clean record: SUSTAINED_REFUTERS agreeing independent re-checks
        for i in range(_auto.SUSTAINED_REFUTERS):
            _auto.record_refuter_check(d, f"spec.system.c{i}", agreed=True, now=now)

        # tamper_evident is DERIVED from the ledger hash-chain (a real mechanism, not a flag); intact here
        check(_led.verify_chain(d)[0], "F2-pre: the ledger hash-chain verifies (the tamper-evident audit trail)")
        # without a hermetic sandbox, capped at Tier 2 (hermetic is the operator-declared deploy property)
        check(_auto.tier_for(d, now=now, hermetic=False) == 2,
              "F2a: a sustained-clean family WITHOUT a hermetic sandbox is capped at Tier 2")
        # hermetic + an intact, verifiable audit chain → Tier 3 earned
        check(_auto.tier_for(d, now=now, hermetic=True) == 3,
              "F2b: sustained-clean + hermetic + an intact tamper-evident chain EARNS Tier 3 (lights-out)")
        # a single incident still mechanically revokes even Tier 3
        _auto.record_incident(d, "spec.system.c0", "a refuter caught a false pass at fleet scale", now=now)
        check(_auto.tier_for(d, now=now, hermetic=True) <= 1,
              "F2c: an incident mechanically revokes even Tier 3 — autonomy is revocable at every rung")

    print("· F2-tamper — a FORGED audit trail breaks the hash-chain → Tier 3 mechanically unreachable")
    with tempfile.TemporaryDirectory() as root:
        import json as _json
        d = os.path.join(root, ".agents/dev-factory")
        _lat.scaffold(d)
        _lat.save(d, {"cells": [{"layer": "rubric", "scope": "system", "slug": "r", "maturity": "validated", "depends_on": [], "signal_refs": ["x"]}]})
        os.makedirs(os.path.join(d, "run"), exist_ok=True)
        now2 = datetime.datetime(2026, 6, 14, tzinfo=datetime.timezone.utc)
        _json.dump({"start_ts": now2.isoformat()}, open(os.path.join(d, "run", "heartbeat.json"), "w"))
        for i in range(_auto.SUSTAINED_REFUTERS):
            _auto.record_refuter_check(d, f"spec.system.c{i}", agreed=True, now=now2)
        check(_auto.tier_for(d, now=now2, hermetic=True) == 3, "F2d-pre: a clean instance earns Tier 3")
        p = os.path.join(d, "ledger", "events.jsonl")
        lines = open(p).readlines()
        e0 = _json.loads(lines[0]); e0["rationale"] = "FORGED-CLEAN-SCOREBOARD"
        lines[0] = _json.dumps(e0) + "\n"
        open(p, "w").writelines(lines)
        check(not _led.verify_chain(d)[0], "F2d: the forged entry breaks the hash-chain (detected, not trusted)")
        check(_auto.tier_for(d, now=now2, hermetic=True) < 3,
              "F2e: a tampered audit trail makes Tier 3 mechanically unreachable (tamper_evident derives FALSE)")

    print()
    if fails:
        print(f"fly-milestone: NOT READY — {len(fails)} check(s) failed:")
        for f in fails:
            print(f"  - {f}")
        return 1
    print("fly-milestone: OK — two families bind one unchanged kernel (the boundary's falsification test holds), "
          "and Tier 3 lights-out is reachable only on a sustained-clean record + a hermetic, tamper-evident "
          "sandbox — and is still mechanically revocable by a single incident. The dark factory is earned, not "
          "assumed.")
    return 0


if __name__ == "__main__":
    sys.exit(run())
