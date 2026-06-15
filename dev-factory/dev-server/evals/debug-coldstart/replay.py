#!/usr/bin/env python3
"""replay.py — the /debug/ ralph harness, proven CI-safe end to end (no model, no server, no tokens).

The /debug/ harness drives the whole Software Dark Factory from a one-paragraph brief: scaffold a project,
cold-start (brief -> spec + hydrated lattice + build tickets), run the bounded build loop, and a verdict. A LIVE
run dispatches real `claude` workers; this replay proves the same ARC deterministically with the MockAdapter —
the CI plumbing proof that the wiring is sound before any tokens are spent. It also pins the two new dev-server
features' load-bearing properties:

  C1  brief -> a PROMPT intake ticket -> cold-start triages it into a hydrated lattice + active build tickets
      (prompt = triaged), the bounded loop drives every build cell to `validated`, and the verdict PASSES.
  C2  SECURITY (Feature A): a gate-wired worker CANNOT forge operator guidance — run/input.jsonl is
      deny-on-write (the 5s steering channel is operator->loop only, by construction).

Exit 0 = the arc completes AND the guidance channel is worker-protected. Stdlib only; Python 3.8+.
Run by .github/workflows/dev-factory.yml. Answer key: this docstring (cold-run discipline).
"""
import json
import os
import subprocess
import sys
import tempfile

_HERE = os.path.dirname(os.path.abspath(__file__))
# _HERE = .../dev-factory/dev-server/evals/debug-coldstart -> repo root is four dirnames up
_REPO = _HERE
for _ in range(4):
    _REPO = os.path.dirname(_REPO)
_DEBUG_BIN = os.path.join(_REPO, "debug", "bin")
_KERNEL_BIN = os.path.join(_REPO, "dev-factory", "dev-kernel", "bin")
sys.path.insert(0, _DEBUG_BIN)
import _common as C       # noqa: E402


def run():
    fails = []
    def check(cond, label):
        print(f"  {'PASS' if cond else 'FAIL'}  {label}")
        if not cond:
            fails.append(label)

    with tempfile.TemporaryDirectory() as tmp:
        C.RUNS = tmp      # redirect all run state to a hermetic tempdir — zero debug/runs/ pollution
        import scaffold
        import coldstart
        import ralph
        import verdict
        api = C._import_api()
        name = "ci"
        inst = C.instance_dir(name)

        print("· scaffold — the brief becomes a PROMPT intake ticket")
        scaffold.scaffold(name, "solitaire")
        check(any(t["type"] == "prompt" for t in api.list_tickets(inst)), "scaffold seeds a PROMPT intake ticket (no target_cell)")

        print("· cold-start — prompt = triaged into a hydrated lattice + build tickets")
        coldstart.coldstart(name, mock=True)
        grid = {c["id"]: c["maturity"] for c in api.lattice_grid(inst)}
        check(grid.get("spec.system.app") == "instantiated", "cold-start authored + seeded the spec cell")
        check(any(k.startswith("capability.system.") for k in grid), "cold-start decomposed the brief into capability cells")
        check(len(api.list_tickets(inst, state="active")) >= 4, "cold-start created active build tickets")
        check(not any(t["type"] == "prompt" for t in api.list_tickets(inst)), "the PROMPT intake ticket was triaged away")

        print("· build — the bounded loop drives every build cell to validated")
        iters = ralph._mock_build(name, api, max_iters=40)
        grid2 = {c["id"]: c["maturity"] for c in api.lattice_grid(inst)}
        build = [k for k in grid2 if k.split(".")[0] in ("spec", "capability")]
        check(bool(build) and all(grid2[k] == "validated" for k in build),
              f"every build cell reached validated in {iters} bounded iteration(s)")
        # the dependency order held: the spec validated before the capability cells that depend on it
        check(iters >= 2, "the build respected the dependency order (spec validated before its dependents)")

        print("· verdict — the lattice is built")
        v = verdict.verdict(name, quiet=True)
        check(v["ok"] and v["lattice_built"], "verdict PASSES (lattice_built)")

        print("· SECURITY — a worker cannot forge operator guidance (run/input.jsonl deny-on-write)")
        payload = json.dumps({"tool_name": "Write", "tool_input": {"file_path": ".agents/dev-factory/run/input.jsonl"}})
        rc = subprocess.run(["python3", os.path.join(_KERNEL_BIN, "gate-verifier"), "--hook"],
                            input=payload, capture_output=True, text=True).returncode
        check(rc == 2, "gate-verifier DENIES a worker write to run/input.jsonl (the 5s guidance channel is operator-only)")
        # and a worker write to a normal app file is NOT denied (no false-positive that would block real building)
        ok_payload = json.dumps({"tool_name": "Write", "tool_input": {"file_path": "src/game.js"}})
        rc2 = subprocess.run(["python3", os.path.join(_KERNEL_BIN, "gate-verifier"), "--hook"],
                             input=ok_payload, capture_output=True, text=True).returncode
        check(rc2 == 0, "gate-verifier ALLOWS a worker write to an ordinary app file (no false block)")

    print()
    if fails:
        print(f"debug-coldstart: FAIL — {len(fails)} check(s) failed:")
        for f in fails:
            print(f"  - {f}")
        return 1
    print("debug-coldstart: OK — a brief becomes a PROMPT ticket, the cold-start planner triages it into a "
          "hydrated lattice + build tickets, the bounded loop drives every build cell to validated (dependency "
          "order held), the verdict passes, and the 5s operator-guidance channel is worker-protected. The whole "
          "dark-factory arc is sound — proven without a model, a server, or a token.")
    return 0


if __name__ == "__main__":
    sys.exit(run())
