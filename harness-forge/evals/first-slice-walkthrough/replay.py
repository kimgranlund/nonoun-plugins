#!/usr/bin/env python3
"""replay.py — the first-slice walkthrough: the kernel's behavioral baseline, end to end and CI-replayable.

Selftests prove the units; THIS proves the loop. It drives a real first slice on a toy project
(invoice-parser, the README's example) using only the public machinery — no hand-set maturities,
no forged signals:

  seed (lattice.py init) → wire (wire.py apply + check) → loop [ rank picks the next ready cell →
  the "worker" writes its asset → validate.py runs a REAL predicate verifier and mints the signal
  from its exit status → ledger.py append records the why ] → distill / cost / false-pass → final
  asserts (frontier empty · every cell validated with an on-disk signal · lattice.py check PASSES
  including content-hash verification · the wiring still checks · false-pass honestly UNMEASURED).

The committed `baseline/` tree is one recorded run — the positive control the judge scores against
(the calibration fixtures are the negatives).

Usage:
  replay.py                # run hermetically in a temp dir; exit 0 = the loop closed end to end
  replay.py --keep DIR     # materialize the run into DIR (how baseline/ was recorded)
  replay.py selftest       # alias for the hermetic run (the run IS the proof)
Stdlib only; Python 3.8+.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
BIN = os.path.normpath(os.path.join(HERE, "..", "..", "bin"))
sys.path.insert(0, BIN)
import lattice as _lat  # noqa: E402

# ---- the toy project: each seeded cell's asset content + the REAL predicate that verifies it ----
ASSETS = {
    "ontology.task.domain": (".agents/harness/ontology/domain.md", """# Ontology — invoice-parser (task scope)

## Entities
Invoice · LineItem · Vendor · TypedRecord — an Invoice has 1..n LineItems and exactly one Vendor.

## Operations
parse(pdf) → Invoice · validate(Invoice) → list[Violation] · to_record(Invoice) → TypedRecord

## States
received → parsed → validated → exported (a malformed PDF dead-ends in `rejected`, never a partial record)
"""),
    "spec.task.first-slice": (".agents/harness/spec/first-slice.md", """# spec.task.first-slice — parse one well-formed PDF invoice into a typed record

## Acceptance criteria (checkable predicates, not prose hopes)
1. `parse(fixture.pdf)` returns an `Invoice` whose `total == sum(line.amount for line in lines)`.
2. Every required field (vendor, date, total, currency) is present and typed — no silent defaults.
3. A malformed PDF raises `InvoiceParseError`; it never returns a partial record.
"""),
    "rubric.task.first-slice": (".agents/harness/rubric/first-slice.md", """# rubric.task.first-slice — scores the slice's work against the spec

| Score | Evidence |
| --- | --- |
| 5 | All three spec predicates pass on the fixture set; error paths covered; deterministic across 3 runs. |
| 3 | Predicates pass on the happy path; the malformed-PDF predicate is untested. |
| 1 | "It looks right" — no predicate executed. |

D1 `[gate]` — the three acceptance predicates, run as code. D2 `[review]` — field-mapping judgment at the boundary.
"""),
    "ledger.task.events": (".agents/harness/ledger/SCHEMA.md", """# ledger.task.events — the append-only event schema

One JSONL line per event: `operation` + `actor` required; `cell_id`, `result`, `rationale` (the WHY),
`cost` {tokens, iterations} carried whenever known. Append-only — rewriting history is tampering.
"""),
}
VERIFIERS = {  # real content predicates — the verdict is the command's exit status, never an opinion
    "ontology.task.domain":
        "import sys; t = open('.agents/harness/ontology/domain.md').read(); "
        "sys.exit(0 if all(s in t for s in ('## Entities', '## Operations', '## States')) else 1)",
    "spec.task.first-slice":
        "import sys, re; t = open('.agents/harness/spec/first-slice.md').read(); "
        "sys.exit(0 if ('## Acceptance criteria' in t and len(re.findall(r'^\\d+\\.', t, re.M)) >= 3) else 1)",
    "rubric.task.first-slice":
        "import sys; t = open('.agents/harness/rubric/first-slice.md').read(); "
        "sys.exit(0 if ('[gate]' in t and '[review]' in t and '| 5 |' in t) else 1)",
    "ledger.task.events":
        "import sys, json; lines = [l for l in open('.agents/harness/ledger/events.jsonl') if l.strip()]; "
        "sys.exit(0 if lines and all(set(('operation','actor')) <= set(json.loads(l)) for l in lines) else 1)",
}


def sh(args, cwd, label, expect_zero=True):
    r = subprocess.run([sys.executable] + args, cwd=cwd, capture_output=True, text=True)
    if expect_zero and r.returncode != 0:
        raise AssertionError("{} failed (exit {}):\n{}{}".format(label, r.returncode, r.stdout, r.stderr))
    return r


def walkthrough(proj):
    hd = os.path.join(proj, ".agents/harness")
    print("== seed ==")
    sh([os.path.join(BIN, "lattice.py"), "init", "invoice-parser", "--dir", hd], proj, "seed")
    print("== wire (the consent step, pre-granted here) ==")
    sh([os.path.join(BIN, "wire.py"), "apply", "--confirm", "--project", proj], proj, "wire apply")
    sh([os.path.join(BIN, "wire.py"), "check", "--project", proj], proj, "wire check")

    print("== the loop: rank → write asset → validate.py (real predicate) → ledger ==")
    for guard in range(8):                                       # the seed has 4 cells; 8 is the runaway stop
        lat = _lat.load(hd)
        ready_gaps = _lat.rank(lat)
        if not ready_gaps:
            break
        cell = ready_gaps[0][1]                                  # the compass picks; the driver does not choose
        cell_id = _lat.cid(cell)
        rel, content = ASSETS[cell_id]
        path = os.path.join(proj, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if not os.path.exists(path):                             # the ledger schema seeds its own events file
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
        if cell_id == "ledger.task.events":                      # the first event must exist for its own verifier
            sh([os.path.join(BIN, "ledger.py"), "append",
                json.dumps({"operation": "record", "actor": "walkthrough", "cell_id": cell_id,
                            "rationale": "ledger schema laid in the first slice (cannot be retrofitted)"}),
                "--dir", hd], proj, "ledger seed event")
        lat = _lat.load(hd)
        _lat.find(lat, cell_id)["asset_ref"] = rel               # bind the asset (what the engine's create step records)
        _lat.save(hd, lat)
        print("   advancing {} ...".format(cell_id))
        sh([os.path.join(BIN, "validate.py"), cell_id, "--dir", hd, "--harness", "predicate-check",
            "--", sys.executable, "-c", VERIFIERS[cell_id]], proj, "validate {}".format(cell_id))
        sh([os.path.join(BIN, "ledger.py"), "append",
            json.dumps({"operation": "validate", "actor": "validate.py", "cell_id": cell_id, "result": "pass",
                        "rationale": "predicate-check exit 0 (the verifier's exit status, not the worker's opinion)",
                        "cost": {"iterations": 1}}),
            "--dir", hd], proj, "ledger entry for {}".format(cell_id))
    else:
        raise AssertionError("the loop did not converge in 8 passes — the seed deadlocked or rank starved")

    print("== distill / cost / false-pass ==")
    sh([os.path.join(BIN, "ledger.py"), "distill", "--dir", hd], proj, "distill")
    sh([os.path.join(BIN, "ledger.py"), "cost", "--dir", hd], proj, "cost")
    fp = sh([os.path.join(BIN, "ledger.py"), "false-pass", "--dir", hd], proj, "false-pass")

    print("== final asserts (the loop actually closed) ==")
    lat = _lat.load(hd)
    stuck = [_lat.cid(c) for c in lat["cells"] if c["maturity"] != "validated"]
    assert not stuck, "cells not validated at the end: {}".format(stuck)
    assert _lat.scan(lat) == [], "the frontier is not empty after the slice validated"
    for c in lat["cells"]:
        assert c.get("signal_refs"), "{} validated without a signal_ref".format(_lat.cid(c))
        for ref in c["signal_refs"]:
            assert os.path.isfile(os.path.join(hd, ref)), "signal file missing on disk: {}".format(ref)
    sh([os.path.join(BIN, "lattice.py"), "check", "--dir", hd], proj, "lattice.py check (incl. content hashes)")
    sh([os.path.join(BIN, "wire.py"), "check", "--project", proj], proj, "wire.py check (still wired)")
    assert "UNMEASURED" in fp.stdout, "false-pass must read UNMEASURED on a fresh slice (no refuter yet) — honesty gate"
    ledger_lines = open(os.path.join(hd, "ledger", "events.jsonl"), encoding="utf-8").read().strip().splitlines()
    assert len(ledger_lines) >= 5, "expected ≥5 ledger events (1 schema + 4 validations), got {}".format(len(ledger_lines))
    print("\nRESULT: PASS (first-slice walkthrough) — seed → wire → 4× [rank → asset → validate.py → ledger] → "
          "distill; frontier empty, every signal minted from a real predicate's exit status, false-pass honestly "
          "UNMEASURED, the lattice passes its own structural+hash check, the project is still wired")
    return 0


def main(argv):
    keep = argv[argv.index("--keep") + 1] if "--keep" in argv else None
    if keep:
        os.makedirs(keep, exist_ok=True)
        return walkthrough(os.path.abspath(keep))
    with tempfile.TemporaryDirectory() as proj:
        return walkthrough(proj)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
