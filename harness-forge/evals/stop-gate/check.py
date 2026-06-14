#!/usr/bin/env python3
"""check.py — the wired stop-gate halts a runaway loop, proven end to end with code (the v0.4 behavioral eval).

The /harness-run loop's safety rests on one claim: a cell stuck in a repeated-failure signature is HALTED
mechanically, not by the worker remembering to stop. This replays that mechanic with only the public
machinery — no model agent — so CI proves the circuit breaker actually breaks:

  seed + wire a project → a cell with an asset + budget{no_progress_n:3}
  → validate.py runs a FAILING verifier 3× (each ledgers a fail)
  → ledger.py no-progress DETECTS the stuck cell
  → lattice.py block flips it
  → ASSERT: it leaves the ready set (rank no longer offers it), the wired gate-budget DENIES the next write
    to its asset (exit 2), and the loop would halt (no ready cells). The before/after is the control:
    before the block the cell IS rankable and the write IS allowed.

Usage:
  check.py            # run hermetically; exit 0 = the stop-gate halts the loop
  check.py selftest   # alias
Stdlib only; Python 3.8+.
"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
BIN = os.path.normpath(os.path.join(HERE, "..", "..", "bin"))
sys.path.insert(0, BIN)
import lattice as _lat  # noqa: E402


def _py(script, *args, **kw):
    return subprocess.run([sys.executable, os.path.join(BIN, script)] + list(args), capture_output=True, text=True, **kw)


def main():
    fails = []
    def expect(cond, label):
        print(("  PASS  " if cond else "  FAIL  ") + label)
        if not cond:
            fails.append(label)

    with tempfile.TemporaryDirectory() as proj:
        d = os.path.join(proj, ".agents/harness")
        _py("lattice.py", "init", "stop-gate-demo", "--dir", d)
        _py("wire.py", "apply", "--project", proj)

        # a capability cell stuck on pytest, with an asset + a no_progress budget of 3. Its upstream layers
        # (spec + ontology at task scope, per the partial order) must be validated for it to be rankable —
        # validate the two seed footholds so the control "it IS rankable before blocking" is real.
        asset_rel = ".agents/harness/capability/parse.py"
        os.makedirs(os.path.join(proj, ".agents/harness", "capability"), exist_ok=True)
        open(os.path.join(proj, asset_rel), "w").write("def parse(): ...\n")
        lat = _lat.load(d)
        for c in lat["cells"]:
            if _lat.cid(c) in ("ontology.task.domain", "spec.task.first-slice"):
                c["maturity"] = "validated"
                c["signal_refs"] = ["signals/seed/ok.json"]
        lat["cells"].append({"layer": "capability", "scope": "task", "slug": "parse", "maturity": "defined",
                             "depends_on": [], "asset_ref": asset_rel, "budget": {"no_progress_n": 3}})
        _lat.save(d, lat)
        cell = "capability.task.parse"

        # CONTROL (before): the cell is rankable, and a write to its asset is allowed by gate-budget.
        ranked_before = _py("lattice.py", "rank", "--dir", d).stdout
        expect(cell in ranked_before, "control: the cell is rankable before it is blocked")
        gb = _py("gate-budget", "check", asset_rel, cwd=proj)
        expect(gb.returncode == 0, "control: gate-budget allows a write to the un-blocked cell")

        # the loop runs the verifier 3× and it FAILS each time (a real failing command), ledgering a fail each pass
        for _ in range(3):
            _py("validate.py", cell, "--dir", d, "--harness", "pytest",
                "--", sys.executable, "-c", "import sys; sys.exit(1)")
            _py("ledger.py", "append",
                json.dumps({"operation": "validate", "actor": "advancer", "cell_id": cell, "result": "fail",
                            "rationale": "pytest: 2 assertions still red"}), "--dir", d)

        # DETECT: ledger.py no-progress flags the stuck cell (exit 1)
        npg = _py("ledger.py", "no-progress", "--dir", d)
        expect(npg.returncode == 1 and cell in npg.stdout, "no-progress detects the cell stuck on 3 consecutive fails")

        # BLOCK: the orchestrator's mechanical action
        blk = _py("lattice.py", "block", cell, "--reason", "no-progress: 3 consecutive fails", "--dir", d)
        expect(blk.returncode == 0, "lattice.py block flips the stuck cell")

        # ASSERT the halt: out of the ready set, and the wired gate-budget DENIES the next write to its asset.
        ranked_after = _py("lattice.py", "rank", "--dir", d).stdout
        expect(cell not in ranked_after, "the blocked cell left the ready set (the loop will not re-pick it)")
        gb2 = _py("gate-budget", "check", asset_rel, cwd=proj)
        expect(gb2.returncode == 2, "the WIRED gate-budget now DENIES a write to the blocked cell (exit 2 = halt)")
        # the wired hook, from its installed location, also denies (end to end)
        wired_gb = os.path.join(proj, ".agents/harness", "hooks", "gate-budget")
        r = subprocess.run([sys.executable, wired_gb, "--hook"],
                           input=json.dumps({"tool_input": {"file_path": asset_rel}}), capture_output=True, text=True, cwd=proj)
        expect(r.returncode == 2, "the installed gate-budget hook denies the blocked cell's write from its wired location")
        # the validity gate also refuses to advance it
        val = _py("lattice.py", "validity", cell, "--dir", d)
        expect(val.returncode == 1, "advance-validity refuses the blocked cell")

    if fails:
        print(f"\nRESULT: FAIL — {len(fails)} assertion(s) broken")
        return 1
    print("\nRESULT: PASS (stop-gate) — a repeated-failure loop is detected, blocked, and HALTED mechanically "
          "(out of rank + denied by the wired gate-budget); the worker's restraint is not what bounds it")
    return 0


if __name__ == "__main__":
    sys.exit(main())
