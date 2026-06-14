#!/usr/bin/env python3
"""check.py — the GLOBAL loop bound is enforced in code, proven with no model agent (the v0.4.1 eval).

The v0.4.0 council's convergent Critical: "/harness-run is bounded by construction" was true only for the
per-cell stop; the global caps (max-cells / max-iterations / wall-clock) were prose the orchestrator AGENT
ticked. Chip H. noted the eval that would prove the global bound "cannot be written, because there is no
code artifact to assert against." This release builds the artifact (`run-budget.py` + `gate-budget`'s global
check), so the eval can be written — and here it is:

  seed + wire → start a run budget → CONTROL: a write is allowed
  → exhaust the budget (a wall-clock deadline in the past; then a max-iterations cap via the ledger)
  → ASSERT: the WIRED gate-budget denies EVERY worker write (exit 2), from its installed location, with NO
    model agent in the loop. The orchestrator's belief about its counter is irrelevant — code is the floor.

Usage:
  check.py            # run hermetically; exit 0 = the global bound is enforced in code
  check.py selftest   # alias
Stdlib only; Python 3.8+.
"""
import datetime
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
BIN = os.path.normpath(os.path.join(HERE, "..", "..", "bin"))
sys.path.insert(0, BIN)
import lattice as _lat  # noqa: E402


def _now():
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def _wired_gate(proj, payload_path):
    """Run the INSTALLED gate-budget hook (from .agents/harness/hooks/) against a write to payload_path. Returns exit code."""
    gb = os.path.join(proj, ".agents/harness", "hooks", "gate-budget")
    r = subprocess.run([sys.executable, gb, "--hook"],
                       input=json.dumps({"tool_input": {"file_path": payload_path}}),
                       capture_output=True, text=True, cwd=proj)
    return r.returncode


def main():
    fails = []
    def expect(cond, label):
        print(("  PASS  " if cond else "  FAIL  ") + label)
        if not cond:
            fails.append(label)

    with tempfile.TemporaryDirectory() as proj:
        d = os.path.join(proj, ".agents/harness")
        subprocess.run([sys.executable, os.path.join(BIN, "lattice.py"), "init", "gb-demo", "--dir", d], capture_output=True)
        subprocess.run([sys.executable, os.path.join(BIN, "wire.py"), "apply", "--project", proj], capture_output=True)
        write_path = ".agents/harness/spec/anything.md"

        # CONTROL: a fresh run budget with room → the wired gate-budget ALLOWS the write.
        _lat.run_budget_start(d, _now(), max_iterations=5,
                              deadline_iso=(datetime.datetime.now().astimezone() + datetime.timedelta(hours=1)).isoformat(timespec="seconds"))
        expect(_wired_gate(proj, write_path) == 0, "control: a write is allowed while the run budget has room")

        # EXHAUST via wall-clock: a deadline in the past → every write denied (the cap that needs no counter).
        past = (datetime.datetime.now().astimezone() - datetime.timedelta(minutes=1)).isoformat(timespec="seconds")
        _lat.run_budget_start(d, _now(), deadline_iso=past)
        expect(_wired_gate(proj, write_path) == 2, "wall-clock: the wired gate denies EVERY write past the deadline (exit 2)")
        # ...and it denies an UNRELATED path too (global, not per-cell): the whole loop is stopped.
        expect(_wired_gate(proj, "src/main.py") == 2, "wall-clock: the global deny covers any path, not just a cell's asset")

        # EXHAUST via max-iterations, counted from the LEDGER (not an agent): cap 2, ledger 2 validate events.
        _lat.run_budget_start(d, _now(), max_iterations=2,
                              deadline_iso=(datetime.datetime.now().astimezone() + datetime.timedelta(hours=1)).isoformat(timespec="seconds"))
        expect(_wired_gate(proj, write_path) == 0, "control: under the iteration cap, writes are allowed")
        os.makedirs(os.path.join(d, "ledger"), exist_ok=True)
        with open(os.path.join(d, "ledger", "events.jsonl"), "a", encoding="utf-8") as f:
            for i in range(2):
                f.write(json.dumps({"operation": "validate", "actor": "advancer", "cell_id": f"spec.task.c{i}",
                                    "result": "fail", "ts": _now()}) + "\n")
        expect(_wired_gate(proj, write_path) == 2, "max-iterations: 2 ledgered validates hit the cap → the wired gate denies (exit 2)")

        # CLEAR: ending the run lifts the global deny (a fresh run must be started deliberately).
        _lat.run_budget_clear(d)
        expect(_wired_gate(proj, write_path) == 0, "clear: ending the run lifts the global deny")

        # THE ARMING GAP — now CLOSED by the loop-active marker (I-9, v0.5.0). Before, "no budget = unbounded" was a
        # disclosed residual; now the marker distinguishes the running loop from a human editing, and a MARKED loop
        # without a budget fails CLOSED.
        # (a) Unmarked + no budget = manual editing / attended single-cell work → still allowed (the gate must not
        #     brick a human's edits or `/harness-advance`). This is correct behavior, not the gap.
        expect(_wired_gate(proj, write_path) == 0, "unmarked + no budget: manual editing / attended work is free (not the loop)")
        # (b) MARK the loop (run-budget.py mark, step 0a) → still no budget → the wired gate now DENIES every write.
        #     The arming gap is closed: an autonomous loop that skipped `start` (step 0b) cannot write un-budgeted.
        subprocess.run([sys.executable, os.path.join(BIN, "run-budget.py"), "mark", "--dir", d], capture_output=True)
        expect(_wired_gate(proj, write_path) == 2, "I-9: a MARKED loop with no budget is DENIED every write (the arming gap, fail-closed)")
        expect(_wired_gate(proj, "src/main.py") == 2, "I-9: the marked-unbudgeted deny is global (covers any path, not just a cell asset)")

        # the orchestrator's DOCUMENTED command (`run-budget.py start`, not the in-process function) arms a real
        # budget AND keeps the marker → enforcing; proving step 0b actually arms the gate.
        r = subprocess.run([sys.executable, os.path.join(BIN, "run-budget.py"), "start", "--wall-clock-s", "-60", "--dir", d],
                           capture_output=True, text=True)   # a deadline 60s in the past = immediately exhausted
        expect(r.returncode == 0, f"run-budget.py start (the CLI the orchestrator calls) failed: {r.stderr}")
        expect(_wired_gate(proj, write_path) == 2, "the CLI-armed budget is enforced by the wired gate (step 0b works)")
        # `stop` ends the loop — clears BOTH marker and budget → free again (a fresh run must be started deliberately).
        subprocess.run([sys.executable, os.path.join(BIN, "run-budget.py"), "stop", "--dir", d], capture_output=True)
        expect(_wired_gate(proj, write_path) == 0, "stop: clearing the marker + budget lifts the deny (loop ended)")
        # and the CLI refuses a vacuous budget (a 'bound' that bounds nothing)
        r = subprocess.run([sys.executable, os.path.join(BIN, "run-budget.py"), "start", "--dir", d], capture_output=True, text=True)
        expect(r.returncode == 2 and "bounds nothing" in r.stderr, "the CLI accepted a vacuous (capless) budget")

    if fails:
        print(f"\nRESULT: FAIL — {len(fails)} assertion(s) broken")
        return 1
    print("\nRESULT: PASS (global-bound) — the global caps (wall-clock + ledger-counted iterations) are ENFORCED by the "
          "wired gate-budget in CODE, no model agent. The v0.4.1 arming gap is now CLOSED (I-9, v0.5.0): a loop MARKED "
          "active (`run-budget.py mark`, step 0a) but un-budgeted fails CLOSED — every write denied — while manual "
          "editing and attended single-cell work, which never set the marker, stay free. The residual shrank from "
          "'forget step 0' to 'skip the entire run preamble', which `/harness-status` surfaces.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
