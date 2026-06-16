#!/usr/bin/env python3
"""replay.py — the /debug/ ralph harness builds SHIPPABLE software, proven CI-safe end to end with the MockAdapter.

The harness drives the whole Software Dark Factory from a one-paragraph brief through MILESTONE rubrics to a
shipped app. A LIVE run authors real multi-file code + a real-browser smoke; this replay proves the same ARC
deterministically (no model, no server, no tokens beyond a local `node`) and pins the load-bearing properties:

  M1  brief → a PROMPT ticket → cold-start triages it into a hydrated MILESTONE lattice: three validated
      milestone rubrics (spec-quality · test-suite · ship — dynamic rubric generation), an ontology foothold,
      a spec cell, per-capability CODE cells each with a planner-authored verify.mjs critic harness, and the
      capability.system.app INTEGRATOR (depends on every capability).
  M2  the bounded loop drives every cell to validated IN MILESTONE ORDER (spec → capabilities → integrator),
      each capability graded by `node verify.mjs` (a real exit-status gate), and the verdict says SHIPPED.
  SEC a gate-wired worker CANNOT write a per-cell verify.mjs (it grades the worker — generator/critic split)
      NOR forge operator guidance (run/input.jsonl); it CAN write ordinary source.
  BI  bi-directional spec work: a build learning flows UPSTREAM (revise the spec, ledgered) and propagates
      staleness DOWNSTREAM to every dependent, which then re-validate against the revised spec — and re-ship.

Exit 0 = the whole arc holds. node is required for the per-cell verifiers; absent → SKIP (exit 0). Stdlib only.
Run by .github/workflows/dev-factory.yml. Answer key: this docstring (cold-run discipline).
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = _HERE
for _ in range(4):
    _REPO = os.path.dirname(_REPO)
_DEBUG_BIN = os.path.join(_REPO, "debug", "bin")
_KERNEL_BIN = os.path.join(_REPO, "dev-factory", "dev-kernel", "bin")
sys.path.insert(0, _DEBUG_BIN)
import _common as C       # noqa: E402


def _gate(path):
    payload = json.dumps({"tool_name": "Write", "tool_input": {"file_path": path}})
    return subprocess.run(["python3", os.path.join(_KERNEL_BIN, "gate-verifier"), "--hook"],
                          input=payload, capture_output=True, text=True).returncode


def run():
    if shutil.which("node") is None:
        print("debug-coldstart: SKIP — `node` not on PATH (the per-cell verify.mjs gates need it; CI has node).")
        return 0
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
        C.bind_env(name)   # apply DEV_FACTORY_KIT=dev-kit-app for the in-process planner + build
        check(any(t["type"] == "prompt" for t in api.list_tickets(inst)), "scaffold seeds a PROMPT intake ticket")

        print("· cold-start — the MILESTONE lattice (dynamic rubric generation + per-cell verify.mjs gates)")
        coldstart.coldstart(name, mock=True)
        grid = {c["id"]: c["maturity"] for c in api.lattice_grid(inst)}
        check(all(grid.get(r) == "validated" for r in ("rubric.system.prd-quality", "rubric.system.spec-quality", "rubric.system.test-suite", "rubric.system.ship")),
              "the planner seeded FOUR validated milestone rubrics (prd-quality · spec-quality · test-suite · ship)")
        check(grid.get("spec.system.app-prd") == "instantiated", "MILESTONE 1: a PRD cell (outside-in) is seeded")
        check(grid.get("spec.system.app") == "instantiated", "MILESTONE 2: the SPEC cell (inside-out) is seeded")
        spec_full = api._lat.find(api._lat.load(inst), "spec.system.app")
        check("spec.system.app-prd" in (spec_full.get("depends_on") or []), "the SPEC (inside-out) REALIZES the PRD — it depends on it")
        caps = [k for k in grid if k.startswith("capability.system.") and k != "capability.system.app"]
        check(len(caps) >= 3, f"the planner decomposed the brief into capability code cells ({len(caps)})")
        check("capability.system.app" in grid, "the planner seeded the capability.system.app INTEGRATOR (the ship cell)")
        full = api._lat.find(api._lat.load(inst), "capability.system.app")
        check(all(c in (full.get("depends_on") or []) for c in caps), "the integrator depends on every capability")
        check(os.path.isfile(os.path.join(inst, "capability", "core", "verify.mjs")), "each capability has a planner-authored verify.mjs critic harness")
        layers = {c["layer"] for c in api.lattice_grid(inst)}
        check({"policy", "methodology", "protocol", "ledger"} <= layers,
              f"the build's lattice seeds the full KNOWLEDGE foundation — policy/methodology/protocol/ledger, not just spec+caps ({len(layers)}/9 layers)")
        check("pattern" not in layers, "the `pattern` layer is correctly ABSENT at cold-start (it is emergent — distilled from operating)")
        for kf in ("policy.system.dispatch", "methodology.system.build", "protocol.system.integration", "ledger.system.provenance"):
            check(grid.get(kf) == "validated", f"foundation seeded validated: {kf}")

        print("· build — the bounded loop ships in milestone order (spec → capabilities → integrator)")
        ralph._mock_build(name, api, max_iters=40)
        g2 = {c["id"]: c["maturity"] for c in api.lattice_grid(inst)}
        build = [k for k in g2 if k.split(".")[0] in ("spec", "capability")]
        check(all(g2[k] == "validated" for k in build), f"every build cell validated via its real verifier ({len(build)} cells)")
        check(os.path.isfile(os.path.join(inst, "capability", "core", "index.mjs")), "the worker authored real multi-file source (index.mjs)")
        v = verdict.verdict(name, quiet=True)
        check(v["shipped"] and v["ok"], "verdict: SHIPPED (the capability.system.app integrator validated — its verify.mjs gate passed)")

        print("· ORCHESTRATION + OBSERVABILITY — the planned team is recorded, spend attributed, the roadmap hydrated")
        epics = [e for e in api.roadmap(inst) if str(e.get("title", "")).startswith("Milestone")]
        check(len(epics) == 4, "the roadmap is hydrated — one epic per milestone (PRD · SPEC · CAPABILITY · SHIP)")
        team = [e for e in api.ledger_query(inst, n=500) if e["event"] == "activity-start" and (e.get("metrics") or {}).get("delegation_mode") == "team"]
        check(bool(team) and all((e["metrics"].get("depth") == 2 and e["metrics"].get("model_tier")) for e in team),
              "capability dispatches record the PLANNED orchestrator-workers team (delegation=team, depth 2, model tier)")
        snap = api.token_snapshot(inst)
        check(snap["total_tokens"] > 0 and snap["by_model"] and snap["by_effort"],
              "token spend is snapshotted + attributed per model tier + reasoning effort (the burn-graph feed)")
        import dispatch as _disp
        check(_disp.adapter_name() == "mock", "the server defaults to the FREE mock adapter (headless real workers are opt-in via DEV_FACTORY_ADAPTER)")
        check(isinstance(api.agents_running(inst), list), "agents_running serves the live-worker slice (enriched with the team's orchestration shape/depth/model)")

        print("· SECURITY — generator/critic split + the guidance channel are worker-protected")
        check(_gate(".agents/dev-factory/capability/core/verify.mjs") == 2, "a worker write to a per-cell verify.mjs is DENIED (it can't grade its own homework)")
        check(_gate(".agents/dev-factory/capability/core/index.mjs") == 0, "a worker write to ordinary source is ALLOWED (no false block on the build)")
        check(_gate(".agents/dev-factory/run/input.jsonl") == 2, "a worker write to run/input.jsonl is DENIED (operator guidance can't be forged)")

        print("· BI-DIRECTIONAL — a learning routes UPSTREAM to the SPEC (inside-out) or the PRD (outside-in)")
        # a TECHNICAL learning → the SPEC (inside-out, the default route)
        spec_asset = os.path.join(inst, "spec", "app.md")
        before = open(spec_asset, encoding="utf-8").read()
        restaled = ralph._regenerate_spec(name, api, "the leaderboard capability revealed the SPEC under-specified tie-breaking")
        check(before != open(spec_asset, encoding="utf-8").read(), "SPEC route: a technical learning revised the inside-out SPEC asset")
        check(restaled and "capability.system.app" in restaled, "SPEC route: staleness propagated to the dependent capabilities + the integrator")
        ralph._revalidate_stale(name, api)
        # a PRODUCT/UX learning → the PRD (outside-in), and it cascades TRANSITIVELY through the SPEC to the capabilities
        prd_asset = os.path.join(inst, "spec", "app-prd.md")
        before_prd = open(prd_asset, encoding="utf-8").read()
        prd_restaled = ralph._regenerate_spec(name, api, "users need an undo — a product gap", target=ralph.PRD_ID)
        check(before_prd != open(prd_asset, encoding="utf-8").read(), "PRD route: a product/UX learning revised the outside-in PRD asset")
        check("spec.system.app" in prd_restaled and "capability.system.app" in prd_restaled,
              "PRD route: revising the PRD re-stales the SPEC AND the capabilities TRANSITIVELY (the full downstream cone)")
        led = api.ledger_query(inst, n=500)
        check(any(e["event"] == "regenerate" for e in led) and any(e["event"] == "stale-propagated" for e in led),
              "every revision + propagation is ledgered (a deliberate, audited revision — not a silent patch)")
        ralph._revalidate_stale(name, api)
        g3 = {c["id"]: c["maturity"] for c in api.lattice_grid(inst)}
        check(g3.get("capability.system.app") == "validated", "the app re-validated against the revised PRD+SPEC — re-SHIPPED")

        print("· BEHAVIORAL — the LIVE gate generators verify the logic WORKS, not just that exports exist")
        import coldstart as _cs

        def _runnode(files, gate):
            wd = tempfile.mkdtemp()
            for fn, content in files.items():
                open(os.path.join(wd, fn), "w", encoding="utf-8").write(content)
            open(os.path.join(wd, "verify.mjs"), "w", encoding="utf-8").write(gate)
            rc = subprocess.run(["node", "verify.mjs"], cwd=wd, capture_output=True, text=True).returncode
            shutil.rmtree(wd)
            return rc

        good = "export const createDeck = () => Array.from({length: 52}, (_, i) => i);"
        wrong = "export const createDeck = () => Array.from({length: 51}, (_, i) => i);"  # exports exist, logic wrong
        capgate = _cs._gen_cap_verify(["createDeck"], ["createDeck().length === 52"])
        check(_runnode({"index.mjs": good}, capgate) == 0, "cap gate PASSES correct logic")
        check(_runnode({"index.mjs": wrong}, capgate) == 1, "cap gate CATCHES wrong logic an API-surface check would pass")
        shipgate = _cs._gen_ship_verify([{"slug": "c", "exports": ["createDeck"]}])
        boots = {"index.mjs": good, "index.html": '<div id="app"></div><script type="module" src="./main.mjs"></script>',
                 "main.mjs": "import {createDeck} from './index.mjs'; export function mount(r){ r.appendChild(document.createElement('div')); }"}
        throws = {**boots, "main.mjs": "import {createDeck} from './index.mjs'; export function mount(r){ throw new Error('boom'); }"}
        check(_runnode(boots, shipgate) == 0, "ship gate PASSES an app that boots + renders (boot smoke)")
        check(_runnode(throws, shipgate) == 1, "ship gate CATCHES an app that throws on mount()")

    print()
    if fails:
        print(f"debug-coldstart: FAIL — {len(fails)} check(s) failed:")
        for f in fails:
            print(f"  - {f}")
        return 1
    print("debug-coldstart: OK — a brief becomes a milestone lattice (3 dynamic rubrics + per-cell verify.mjs gates), "
          "the bounded loop ships it in milestone order (spec → capabilities → integrator) graded by real node "
          "verifiers, the generator/critic split + the guidance channel are worker-protected, and a build learning "
          "flows bi-directionally upstream to revise the spec, propagate, and re-ship. The whole shippable-software "
          "arc is sound — proven without a model, a server, or a token.")
    return 0


if __name__ == "__main__":
    sys.exit(run())
