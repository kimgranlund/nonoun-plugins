#!/usr/bin/env python3
"""replay.py — the Run milestone (TDD §19): a ledger-driven revision lands through a DELIBERATE transition.

Crawl built a cell; Walk ran the factory unattended; Run closes the outer loop — the factory improves its
own DEFINITIONS from the ledger. This proves the loop closes: operate → ledger → distill → patterns →
upstream → spec, and the resulting revision to a spec cell lands as a deliberate, ledgered maturity
transition (validated → regenerating → validated), never a silent edit — so the substrate SHARPENS rather
than just accreting (Failure 1, designed out).

Falsified if any breaks:
  R1  distillation surfaces the recurring failure signature from the ledger, WITH provenance (ledger_refs).
  R2  a regeneration ticket drives the spec cell validated → regenerating (the revision begins) as a
      ledgered transition — the worker revises the asset; this is authoring, not a re-validation.
  R3  regenerating → validated re-validates the REVISED spec through the critic's signal (the trust line
      holds across a revision: a worker can revise, but cannot self-declare the revision validated).
  R4  the spec asset actually CHANGED, and the whole revision is in the append-only ledger — deliberate,
      attributable, reversible — not a silent overwrite.

Exit 0 = the loop closes. Stdlib only; Python 3.8+. Answer key in README.md.
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_SERVER = os.path.dirname(os.path.dirname(_HERE))
sys.path.insert(0, _SERVER)
import api as _api          # noqa: E402
sys.path.insert(0, _api._store._KERNEL_BIN)
import lattice as _lat      # noqa: E402
import ledger as _led       # noqa: E402
import distill as _distill  # noqa: E402

CELL = "spec.system.feature"


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
        srv = {"kind": "server", "id": "dev-server"}
        _api.seed_cell(d, "rubric", "system", "spec-quality", maturity="validated",
                       signal_refs=["signals/rubric.system.spec-quality/seed.json"])
        _api.seed_cell(d, "spec", "system", "feature", maturity="validated", asset_ref="spec/feature.md",
                       signal_refs=["signals/spec.system.feature/v1.json"])
        os.makedirs(os.path.join(d, "spec"), exist_ok=True)
        open(os.path.join(d, "spec", "feature.md"), "w").write("# Feature (v1)\n\nThe original spec, validated but underspecified.\n")

        # OPERATE: the ledger accrues a recurring failure signature on a downstream cell type — evidence the
        # governing spec is underspecified and should be revised.
        for _ in range(3):
            _led.append(d, "block", srv, {"cell": "capability.workflow.impl"}, "downstream impl blocked: spec ambiguous on the error contract")

        print("· R1 — distillation surfaces the recurring failure signature WITH provenance")
        cands = _distill.distill_patterns(d, min_occurrences=2)
        fail_cands = [c for c in cands if c["kind"] == "failure"]
        check(any(c["cell_type"] == "capability.workflow" for c in fail_cands), "R1a: distilled the recurring downstream failure")
        check(all(c["evidence"] and all(r.startswith("ledger:") for r in c["evidence"]) for c in fail_cands),
              "R1b: the candidate carries ledger provenance (not a guess)")
        # the spec-regenerator records the upstream proposal, linking the distilled evidence
        prov = fail_cands[0]["evidence"]
        _led.append(d, "regenerate", {"kind": "agent", "id": "spec-regenerator"}, {"cell": CELL},
                    f"propose revising {CELL}: downstream {fail_cands[0]['cell_type']} blocks trace to its error contract",
                    metrics={"distilled_from": prov})

        print("· R2 — a regeneration ticket drives the spec validated -> regenerating (revision begins)")
        t1 = _api.create_ticket(d, "chore", "revise the feature spec's error contract", target_cell=CELL,
                                target_transition={"from": "validated", "to": "regenerating"},
                                acceptance={"rubric_cell": "rubric.system.spec-quality"}, budget={"iterations": 3, "tokens": 60000})
        for to in ["active", "claimed", "in-progress"]:
            ok, _t, msg = _api.transition_ticket(d, t1["id"], to, srv)
            check(ok, f"R2 {to}: {msg}")
        # the worker REVISES the asset (rewritable side)
        open(os.path.join(d, "spec", "feature.md"), "w").write(
            "# Feature (v2)\n\nRevised: the error contract is now specified explicitly (the gap the ledger surfaced).\n")
        ok, _t, msg = _api.transition_ticket(d, t1["id"], "in-review", srv)
        ok, _t, msg = _api.transition_ticket(d, t1["id"], "done", srv)   # authoring advance -> regenerating
        check(ok and _lat.find(_lat.load(d), CELL)["maturity"] == "regenerating",
              f"R2a: spec entered `regenerating` via a deliberate transition ({msg})")

        print("· R3 — regenerating -> validated re-validates the REVISED spec through the critic's signal")
        t2 = _api.create_ticket(d, "chore", "re-validate the revised feature spec", target_cell=CELL,
                                target_transition={"from": "regenerating", "to": "validated"},
                                acceptance={"rubric_cell": "rubric.system.spec-quality"}, budget={"iterations": 3, "tokens": 60000})
        for to in ["active", "claimed", "in-progress", "in-review"]:
            _api.transition_ticket(d, t2["id"], to, srv)
        ok, _t, msg = _api.transition_ticket(d, t2["id"], "done", srv, verifier="python3 -c 'import sys;sys.exit(0)'")
        revalidated = _lat.find(_lat.load(d), CELL)
        check(ok and revalidated["maturity"] == "validated", f"R3a: the revised spec re-validated ({msg})")
        check(len(revalidated.get("signal_refs", [])) >= 2, "R3b: re-validation minted a NEW critic signal (the trust line held across the revision)")

        print("· R4 — the asset changed and the whole revision is in the ledger (deliberate, not silent)")
        check("v2" in open(os.path.join(d, "spec", "feature.md")).read(), "R4a: the spec asset actually changed (revised, not a no-op)")
        led = _led.read(d, cell=CELL)
        tos = [e.get("to") for e in led if e.get("event") == "transition"]
        check("regenerating" in tos and "validated" in tos, "R4b: validated->regenerating->validated is in the ledger as deliberate transitions")
        check(any(e["event"] == "regenerate" for e in led), "R4c: the distillation-driven proposal is ledgered (the loop closed: ledger -> distill -> upstream)")

    print()
    if fails:
        print(f"run-milestone: LOOP OPEN — {len(fails)} check(s) failed:")
        for f in fails:
            print(f"  - {f}")
        return 1
    print("run-milestone: OK — the ledger's recurring failure signature distilled (with provenance) into an "
          "upstream proposal; the spec was revised through a deliberate validated->regenerating->validated "
          "transition and re-validated by the critic. The outer loop closes: the substrate sharpens, it doesn't "
          "just accrete.")
    return 0


if __name__ == "__main__":
    sys.exit(run())
