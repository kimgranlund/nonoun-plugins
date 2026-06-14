#!/usr/bin/env python3
"""council-precheck.py — the harness-council's Step-0 mechanical pass, as ONE bundled, auditable call.

The harness-council orchestrator needs the kernel's deterministic gate outputs (the "anchor block") before
it fans out the critics. Running those as several free-form `Bash` calls is the lethal-trifecta surface the
council itself flagged (Simon W.): an agent that holds a general shell AND reads an untrusted harness can be
steered into a sixth command. This driver collapses the entire legitimate Step-0 need into a single fixed
invocation — `python3 council-precheck.py --project <path>` — so the orchestrator's only shell call is this
one, and a malicious harness has no free-form Bash to borrow. It reads the artifact; it NEVER executes
anything inside it (no hooks, no verifier commands, no scripts in its tree) — every check is the plugin's
own trusted code reading the harness's data.

Usage:
  council-precheck.py --project DIR [--harness-dir D]   # print the anchor block for the harness under review
  council-precheck.py selftest
Exit 0 always (this is a read; findings are content for the critics, not a pass/fail gate). Stdlib only; 3.8+.
"""
import os
import sys

_BIN = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _BIN)
import lattice as _lat     # noqa: E402
import ledger as _led      # noqa: E402
import wire as _wire       # noqa: E402


def anchor_block(project, hd=".agents/harness"):
    """Return the deterministic Step-0 anchor block (a string the orchestrator pastes into each critic dispatch)."""
    d = os.path.join(project, hd)
    out = ["== MECHANICAL ANCHOR BLOCK (kernel gates, read-only — interpret, never re-derive) =="]

    # H1 — structural + retro-integrity + phantom signals + stale-but-trusted
    try:
        findings = _lat.check(_lat.load(d), d=d)
        out.append("lattice.py check  → " + (f"FAIL — {len(findings)} finding(s):" if findings else "PASS — 0 findings"))
        out += [f"    [INVALID] {f}" for f in findings]
    except OSError:
        out.append(f"lattice.py check  → NO LATTICE at {d}/lattice.json (the harness may be unseeded)")

    # the frontier gap-set
    try:
        gaps = _lat.scan(_lat.load(d))
        out.append(f"lattice.py scan   → {len(gaps)} open/stale cell(s) at the frontier" +
                   (": " + ", ".join(_lat.cid(c) for c in gaps[:8]) if gaps else ""))
    except OSError:
        out.append("lattice.py scan   → (no lattice)")

    # H3 — is the blocking gate WIRED (not merely present in bin/)?
    wired = _wire.check(project, hd, quiet=True)
    out.append(f"wire.py check     → {'WIRED (exit 0)' if wired == 0 else 'NOT WIRED (exit 1) — the gate is not installed in this project loop'}")

    # H6 — the false-pass rate (UNMEASURED is not 0%) ; H5 — the no-progress detector
    evs = _led.read(d)
    rate, fp, tot, refn = _led.false_pass_rate(evs)
    out.append("ledger false-pass → " + (f"UNMEASURED — {tot} pass(es), 0 refute events (absence of bad news, not evidence)"
               if rate is None else f"{rate:.1%} ({fp}/{tot}, {refn} refuter(s))"))
    stuck = _led.no_progress(evs)
    out.append("ledger no-progress→ " + ("none" if not stuck else
               "; ".join(f"{s['cell_id']} stuck {s['fails']}×" for s in stuck) + " → should halt"))

    # H4 — the grammar classes the naming sweep validates against
    out.append("naming classes    → " + " ".join(__import__("naming").name_classes()))
    return "\n".join(out)


def selftest():
    import tempfile
    fails = []
    def expect(cond, label):
        if not cond:
            fails.append(label)
    with tempfile.TemporaryDirectory() as proj:
        d = os.path.join(proj, ".agents/harness")
        _lat.scaffold(d)
        _lat.save(d, _lat.seed_lattice("precheck"))
        block = anchor_block(proj)
        for token in ("lattice.py check", "lattice.py scan", "wire.py check", "ledger false-pass",
                      "ledger no-progress", "naming classes"):
            expect(token in block, f"anchor block missing the {token} line")
        expect("NOT WIRED" in block, "a freshly seeded (unwired) project should report NOT WIRED")
        # after wiring, the block flips to WIRED — and the driver never executes anything in the harness
        _wire.apply(proj, ".agents/harness")
        sys.stdout = open(os.devnull, "w")     # silence apply's print during the second pass
        block2 = anchor_block(proj)
        sys.stdout = sys.__stdout__
        expect("WIRED (exit 0)" in block2, "a wired project should report WIRED in the anchor block")
    if fails:
        sys.stderr.write("council-precheck selftest: FAIL\n")
        for f in fails:
            sys.stderr.write(f"  - {f}\n")
        return 1
    print("council-precheck selftest: OK (one bundled call emits the 6-line anchor block; reflects wired/unwired; "
          "reads the harness, never executes it — the orchestrator's only Bash call)")
    return 0


def main(argv):
    if argv and argv[0] == "selftest":
        return selftest()
    if "--project" not in argv:
        print(__doc__.split("Usage:")[1].split("Stdlib")[0].strip(), file=sys.stderr)
        return 2
    project = argv[argv.index("--project") + 1]
    hd = argv[argv.index("--harness-dir") + 1] if "--harness-dir" in argv else ".agents/harness"
    print(anchor_block(project, hd))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
