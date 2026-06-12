#!/usr/bin/env python3
"""validate.py — the validation path: run a cell's verifier and write the signal from its EXIT STATUS.

This is the executable the loop's legitimacy rests on. The engine is define → create → validate, and the
whole anti-reward-hacking story is that the *verdict comes from an external check, not the worker's
opinion*. That check is a command — pytest, a linter, a link-check, a rubric scorer, a build — and THIS
script runs it and mints the signal from the command's exit status (0 = pass, nonzero = fail), captures
its output as localized evidence, stamps the validated cell's `validated_against` with the asset's content
hash (for staleness propagation), and advances the cell. The worker never runs this on its own homework:
verifier assets (`signals/`) are deny-on-write to the worker via `gate-signal`, so the worker cannot forge
a signal — the generator/critic split, made executable. A signal whose result is computed by code from an
external command is the currency; a worker hand-asserting "pass" into the ledger is not.

See references/agentic-systems-foundations/evals-and-verification.md and layer-rubric.md.

Usage:
  validate.py <cell-id> [--dir DIR] [--harness NAME] -- <command> [args...]
  validate.py selftest
Exit 0 = the verifier passed (cell advanced to `validated`); 1 = it failed (cell NOT advanced); 2 = bad invocation.
Stdlib only; Python 3.8+.
"""
import datetime
import hashlib
import json
import os
import subprocess
import sys

_ROOT = os.environ.get("CLAUDE_PLUGIN_ROOT") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "bin"))
import lattice as _lat  # noqa: E402  (sibling kernel module: load/save/find/cid/transition machine)


def _hash(path):
    try:
        return "sha256:" + hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]
    except OSError:
        return ""


def run_validation(d, cell_id, harness, command):
    """Run `command`, mint a Signal from its exit status, advance the cell on pass. Returns (ok, signal, msg)."""
    lat = _lat.load(d)
    cell = _lat.find(lat, cell_id)
    if cell is None:
        return False, None, f"no such cell: {cell_id}"
    try:
        proc = subprocess.run(command, capture_output=True, text=True, timeout=600)
        passed = proc.returncode == 0
        out = (proc.stdout or "") + (proc.stderr or "")
    except (OSError, subprocess.SubprocessError) as e:
        passed, out = False, f"verifier could not run: {e}"

    ts = datetime.datetime.now().astimezone().isoformat(timespec="seconds").replace(":", "-")
    asset = cell.get("asset_ref")
    against = {}
    for dep in cell.get("depends_on", []):
        dc = _lat.find(lat, dep)
        if dc and dc.get("asset_ref"):
            against[dep] = _hash(os.path.join(os.path.dirname(d.rstrip("/")) or ".", dc["asset_ref"]))
    signal = {
        "cell_id": cell_id, "ts": ts, "harness": harness,
        "kind": "gate", "result": "pass" if passed else "fail",
        "evidence": out.strip()[-1500:] or None, "validated_against": against,
    }
    sig_dir = os.path.join(d, "signals", cell_id)
    os.makedirs(sig_dir, exist_ok=True)
    sig_path = os.path.join(sig_dir, f"{ts}--{harness}.json")
    json.dump(signal, open(sig_path, "w", encoding="utf-8"), indent=2)
    rel = os.path.join("signals", cell_id, f"{ts}--{harness}.json")

    if passed:
        if cell["maturity"] == "defined":                 # the asset now exists → instantiated → validated
            cell["maturity"] = "instantiated"
        if _lat.transition_ok(cell["maturity"], "validated"):
            cell["maturity"] = "validated"
        cell.setdefault("signal_refs", []).append(rel)
        cell["validated_against"] = against
        _lat.save(d, lat)
        if asset:
            against[cell_id] = _hash(os.path.join(os.path.dirname(d.rstrip("/")) or ".", asset))
        return True, signal, f"PASS — {cell_id} → validated (signal: {rel})"
    return False, signal, f"FAIL — {cell_id} not advanced ({harness} exited nonzero; signal: {rel})"


def selftest():
    import tempfile
    fails = []
    def expect(cond, label):
        if not cond:
            fails.append(label)
    with tempfile.TemporaryDirectory() as root:
        d = os.path.join(root, ".harness")
        _lat.scaffold(d)
        lat = _lat.seed_lattice("t")
        # make the spec instantiable: give it an asset and a validated verifier
        for c in lat["cells"]:
            if _lat.cid(c) == "rubric.task.first-slice":
                c["maturity"] = "validated"
                c["signal_refs"] = ["signals/rubric.task.first-slice/x.json"]
            if _lat.cid(c) == "spec.task.first-slice":
                c["maturity"] = "instantiated"
                c["asset_ref"] = "spec/first-slice.md"
        _lat.save(d, lat)

        # a PASSING verifier (exit 0) → cell validated + a signal written
        ok, sig, msg = run_validation(d, "spec.task.first-slice", "truecheck", ["python3", "-c", "import sys; sys.exit(0)"])
        expect(ok and sig["result"] == "pass", f"passing verifier did not yield a pass signal: {msg}")
        after = _lat.find(_lat.load(d), "spec.task.first-slice")
        expect(after["maturity"] == "validated", f"passing cell not advanced to validated: {after['maturity']}")
        expect(after.get("signal_refs"), "no signal_ref recorded on the validated cell")
        sig_files = os.listdir(os.path.join(d, "signals", "spec.task.first-slice"))
        expect(any(f.endswith("--truecheck.json") for f in sig_files), f"signal file not written: {sig_files}")

        # a FAILING verifier (exit 1) → fail signal, cell NOT advanced (reset to instantiated first)
        lat2 = _lat.load(d)
        _lat.find(lat2, "spec.task.first-slice")["maturity"] = "instantiated"
        _lat.save(d, lat2)
        ok, sig, msg = run_validation(d, "spec.task.first-slice", "failcheck", ["python3", "-c", "import sys; sys.exit(1)"])
        expect((not ok) and sig["result"] == "fail", f"failing verifier did not yield a fail signal: {msg}")
        expect(_lat.find(_lat.load(d), "spec.task.first-slice")["maturity"] == "instantiated", "failing cell was advanced anyway")
        expect(sig.get("evidence") is None or isinstance(sig["evidence"], str), "evidence malformed")

        # a missing cell errors cleanly
        ok, sig, msg = run_validation(d, "no.such.cell", "x", ["python3", "-c", ""])
        expect(not ok and sig is None, "missing cell did not error")

    if fails:
        sys.stderr.write("validate selftest: FAIL\n")
        for f in fails:
            sys.stderr.write(f"  - {f}\n")
        return 1
    print("validate selftest: OK (a passing verifier mints a pass signal + advances the cell; a failing one writes a "
          "fail signal and does NOT advance; the verdict is the command's exit status, not the worker's opinion)")
    return 0


def main(argv):
    if argv and argv[0] == "selftest":
        return selftest()
    if "--" not in argv or not argv or argv[0].startswith("-"):
        print("usage: validate.py <cell-id> [--dir DIR] [--harness NAME] -- <command...>", file=sys.stderr)
        return 2
    sep = argv.index("--")
    head, command = argv[:sep], argv[sep + 1:]
    if not command:
        print("validate.py: no verifier command after `--`", file=sys.stderr)
        return 2
    cell_id = head[0]
    d = head[head.index("--dir") + 1] if "--dir" in head else ".harness"
    harness = head[head.index("--harness") + 1] if "--harness" in head else os.path.basename(command[0])
    try:
        ok, _sig, msg = run_validation(d, cell_id, harness, command)
    except OSError as e:
        print(f"validate.py: {e}", file=sys.stderr)
        return 2
    print(msg)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
