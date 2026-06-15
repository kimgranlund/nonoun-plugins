#!/usr/bin/env python3
"""coldstart.py — the privileged planner: a brief becomes a spec + a hydrated lattice + build tickets.

    python3 debug/bin/coldstart.py <name> [--mock] [--model opus]

This realises "prompt = triaged": it reads the scaffolded PROMPT ticket (the brief), produces a PLAN (the spec
asset + the lattice cells + the build tickets), and APPLIES it through the single-writer ops layer (api.seed_cell
/ create_ticket). It runs as a PRIVILEGED operator process — NOT a gate-wired cell-worker — because seeding
lattice.json + tickets is denied to gate-wired workers; the privilege split is the design, not a hole. It must
run BEFORE the dev-server boots (so it is the single writer); ralph.py sequences it that way.

  --mock : use a deterministic CANNED plan (no model) — the CI plumbing proof. Default when DEBUG_RALPH_LIVE
           is unset and `claude` is absent.
  live   : run a `claude -p` planner that emits the plan as JSON, then apply it (spends tokens).

Stdlib only; Python 3.8+.
"""
import json
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common as C   # noqa: E402

SLUG = "app"          # the system-scope slug the plan builds under (spec.system.app, capability.system.app)
ACTOR = {"kind": "agent", "id": "cold-start-planner"}

# The three MILESTONE rubrics the planner authors/seeds (dynamic rubric generation — "make as many as we need").
R_SPEC, R_CAP, R_SHIP = "rubric.system.spec-quality", "rubric.system.test-suite", "rubric.system.ship"


def _mock_cap_verify():
    """A per-cell CRITIC harness (mock) — authored by the planner, gate-denied to the worker. It imports the
    worker's code and gates on it; a live planner authors real checkable predicates + a pristine reference."""
    return ("// per-cell critic harness (mock). The planner authors this; the worker is gate-denied from writing it.\n"
            "import { ready } from './index.mjs';\n"
            "if (ready !== true) { console.error('FAIL: index.mjs must export ready=true'); process.exit(1); }\n"
            "console.log('pass'); process.exit(0);\n")


def _mock_ship_verify(features):
    """The SHIP gate (mock): the app integrator composes EVERY capability. A live planner also runs the build +
    the acceptance criteria + (with DEV_FACTORY_BROWSER_SMOKE=1) a real-browser smoke."""
    imports = "\n".join(f"import {{ ready as r_{f} }} from '../{f}/index.mjs';" for f in features)
    checks = " && ".join(f"r_{f} === true" for f in features) or "true"
    return ("// SHIP gate (mock) — the app integrator composes every capability. The planner authors it.\n"
            + imports + "\n"
            + f"if (!({checks})) {{ console.error('FAIL: not every capability composed'); process.exit(1); }}\n"
            "console.log('pass: all capabilities composed'); process.exit(0);\n")


# ─────────────────────────── the plan shape ───────────────────────────
# plan = {
#   "assets":  [{"path": "spec/app.md", "content": "..."}],          # files to write into the instance
#   "cells":   [{"layer","scope","slug","maturity","asset_ref"?,"depends_on"?,"signal_refs"?}],
#   "tickets": [{"target_cell","from","to","rubric_cell","deps":[cell ids],"title"}],
# }

def _canned_plan(brief_text):
    """A deterministic MILESTONE plan — the CI plumbing proof (no model). Hydrates the full arc:

      MILESTONE 1 (SPEC)       spec.system.app, gated by rubric.system.spec-quality (a real acceptance contract)
      MILESTONE 2 (CAPABILITY) capability.system.<feature> per feature — multi-file code, each with a
                               planner-authored per-cell verify.mjs critic harness, gated by rubric.system.test-suite
      MILESTONE 3 (SHIP)       capability.system.app — the integrator that composes every capability, gated by
                               rubric.system.ship (its verify.mjs is the ship gate)

    The planner SEEDS the three milestone rubrics (dynamic rubric generation) + an ontology foothold, AUTHORS the
    per-cell critic harnesses (the gates a worker can't write), and creates the milestone build tickets. A live
    planner authors real specs + real verify.mjs predicates; the apply logic is identical."""
    title = brief_text.strip().splitlines()[0].lstrip("# ").strip() or "the app"
    features = ["core", "ui", "persistence"]   # generic slice; a live planner derives real feature slugs from the brief
    spec_id = f"spec.system.{SLUG}"
    app_id = f"capability.system.{SLUG}"
    cap_ids = [f"capability.system.{f}" for f in features]

    # MILESTONE 1 — the spec, with an acceptance contract the spec-contract verifier checks for
    contract = {"title": title, "cell": spec_id, "binds_rubric": R_SHIP,
                "acceptance_criteria": [{"id": "ac-ship", "rubric_cell": R_SHIP}],
                "non_goals": ["no backend / accounts in the first cut"]}
    spec_md = f"# Spec — {title}\n\n{brief_text.strip()}\n\n```json\n{json.dumps(contract, indent=2)}\n```\n"
    assets = [{"path": f"spec/{SLUG}.md", "content": spec_md}]

    # dynamic rubric generation — seed the three validated milestone rubrics + the ontology foothold
    cells = [{"layer": "rubric", "scope": "system", "slug": r.split(".")[-1], "maturity": "validated",
              "signal_refs": [f"signals/{r}/seed.json"]} for r in (R_SPEC, R_CAP, R_SHIP)]
    cells.append({"layer": "ontology", "scope": "system", "slug": SLUG, "maturity": "validated",
                  "signal_refs": [f"signals/ontology.system.{SLUG}/seed.json"]})
    cells.append({"layer": "spec", "scope": "system", "slug": SLUG, "maturity": "instantiated", "asset_ref": f"spec/{SLUG}.md"})
    tickets = [{"target_cell": spec_id, "from": "instantiated", "to": "validated", "rubric_cell": R_SPEC,
                "deps": [], "milestone": "SPEC", "title": f"MILESTONE 1 · spec: {title}"}]

    # MILESTONE 2 — per-capability code cells, each with its planner-authored verify.mjs critic harness
    for f in features:
        assets.append({"path": f"capability/{f}/verify.mjs", "content": _mock_cap_verify()})
        cells.append({"layer": "capability", "scope": "system", "slug": f, "maturity": "instantiated",
                      "asset_ref": f"capability/{f}", "depends_on": [spec_id]})
        tickets.append({"target_cell": f"capability.system.{f}", "from": "instantiated", "to": "validated",
                        "rubric_cell": R_CAP, "deps": [spec_id], "milestone": "CAPABILITY", "title": f"MILESTONE 2 · build: {f}"})

    # MILESTONE 3 — the app integrator (SHIP): composes every capability, gated by its own ship verify.mjs
    assets.append({"path": f"capability/{SLUG}/verify.mjs", "content": _mock_ship_verify(features)})
    cells.append({"layer": "capability", "scope": "system", "slug": SLUG, "maturity": "instantiated",
                  "asset_ref": f"capability/{SLUG}", "depends_on": [spec_id] + cap_ids})
    tickets.append({"target_cell": app_id, "from": "instantiated", "to": "validated", "rubric_cell": R_SHIP,
                    "deps": [spec_id] + cap_ids, "milestone": "SHIP", "title": f"MILESTONE 3 · ship: {title}"})
    return {"assets": assets, "cells": cells, "tickets": tickets}


def _live_plan(name, brief_text, model):
    """Run a `claude -p` planner: emit the plan as JSON. The planner reads the kernel + kit (spec-author,
    lattice-management) via --add-dir as LOCAL source. Falls back to the canned plan if `claude` is absent or
    the output won't parse (so a live run degrades to the proven slice rather than failing the whole loop)."""
    if shutil.which("claude") is None:
        print("  [live] `claude` not on PATH — falling back to the canned plan", file=sys.stderr)
        return _canned_plan(brief_text)
    schema = ('{"assets":[{"path":"spec/app.md","content":"<the spec, SKILL-format with an embedded ```json '
              'contract>"}],"cells":[{"layer":"capability","scope":"system","slug":"<feature>","maturity":'
              '"defined","depends_on":["spec.system.app"]}],"tickets":[{"target_cell":"capability.system.'
              '<feature>","from":"defined","to":"instantiated","rubric_cell":"rubric.system.app","deps":'
              '["spec.system.app"],"title":"build <feature>"}]}')
    prompt = (
        "You are the dev-factory cold-start PLANNER. Turn this product brief into a build plan for a typed "
        "knowledge lattice. Author the spec for spec.system.app (SKILL-format: intent + brief + an embedded "
        "```json acceptance contract), seed a validated bootstrap rubric.system.app, and decompose the app into "
        "capability.system.<feature> cells with build tickets (one legal maturity step each) that depend on the "
        "validated spec. Output ONLY a single JSON object of this shape (no prose):\n" + schema +
        "\n\nThe brief:\n" + brief_text)
    add = []
    for p in (C.KERNEL_BIN, C.KIT_CORPUS):
        add += ["--add-dir", p]
    cmd = ["claude", "-p", prompt, *add, "--allowedTools", "Read,Glob,Grep", "--output-format", "text"]
    if model:
        cmd += ["--model", model]
    try:
        r = C.sh(cmd, capture=True, check=False)
        m = re.search(r"\{.*\}", r.stdout or "", re.DOTALL)
        plan = json.loads(m.group(0)) if m else None
        if not plan or "cells" not in plan or "tickets" not in plan:
            raise ValueError("planner output missing cells/tickets")
        # always include the validated bootstrap rubric the build tickets bind to
        rid = f"rubric.system.{SLUG}"
        if not any(c.get("layer") == "rubric" for c in plan["cells"]):
            plan["cells"].insert(0, {"layer": "rubric", "scope": "system", "slug": SLUG, "maturity": "validated",
                                     "signal_refs": [f"signals/{rid}/seed.json"]})
        return plan
    except Exception as e:
        print(f"  [live] planner failed ({e}); falling back to the canned plan", file=sys.stderr)
        return _canned_plan(brief_text)


def apply_plan(inst, plan, api):
    """Apply a plan through the single-writer ops layer: write assets, seed cells, create+activate build
    tickets, and close the prompt ticket as triaged. Returns the list of activated build-ticket ids."""
    for a in plan.get("assets", []):
        p = os.path.join(inst, a["path"])
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w", encoding="utf-8").write(a.get("content", ""))
    for c in plan.get("cells", []):
        api.seed_cell(inst, c["layer"], c["scope"], c["slug"], maturity=c.get("maturity", "absent"),
                      asset_ref=c.get("asset_ref"), depends_on=c.get("depends_on"), signal_refs=c.get("signal_refs"))
    activated, by_ms = [], {}
    for t in plan.get("tickets", []):
        deps = {"cells_ready": t.get("deps", [])}
        tk = api.create_ticket(inst, "feature", t.get("title", t["target_cell"]), target_cell=t["target_cell"],
                               target_transition={"from": t["from"], "to": t["to"]},
                               acceptance={"rubric_cell": t["rubric_cell"]},
                               budget={"iterations": 4, "tokens": 200000}, dependencies=deps)
        ok, _t, msg = api.transition_ticket(inst, tk["id"], "active", {"kind": "server", "id": "dev-server"})
        if not ok:
            print(f"  ! build ticket {tk['id']} could not go active: {msg}", file=sys.stderr)
        else:
            activated.append(tk["id"])
            by_ms.setdefault(t.get("milestone", "BUILD"), []).append(tk["id"])
    # hydrate the ROADMAP: one epic per milestone, with its tickets nested (so the Roadmap view fills in)
    ms_order = {"SPEC": 1, "CAPABILITY": 2, "SHIP": 3, "BUILD": 4}
    for ms in sorted(by_ms, key=lambda m: ms_order.get(m, 9)):
        api.create_epic(inst, f"Milestone · {ms}", body=f"The {ms} milestone — {len(by_ms[ms])} ticket(s).",
                        tickets=by_ms[ms], created_by="cold-start-planner")
    return activated


def _close_prompt_ticket(inst, api):
    for t in api.list_tickets(inst):
        if t.get("type") == "prompt":
            ft = api.get_ticket(inst, t["id"])
            ft["type"] = "chore"; ft["state"] = "cancelled"   # park the intake as triaged (out of the way)
            ft.setdefault("provenance", {})["superseded_by"] = "cold-start plan"
            import lifecycle as _lc
            _lc.save_ticket(inst, ft)
            return t["id"]
    return None


def coldstart(name, mock=False, model=None):
    api = C._import_api()
    inst = C.instance_dir(name)
    if not os.path.isdir(inst):
        raise SystemExit(f"no instance for '{name}' — run scaffold.py first.")
    # the brief is the prompt ticket's body
    brief_text = next((api.get_ticket(inst, t["id"]).get("body", "")
                       for t in api.list_tickets(inst) if t.get("type") == "prompt"), "")
    if not brief_text:
        raise SystemExit("no PROMPT ticket found — scaffold seeds one from the brief.")

    live = not mock and (os.environ.get("DEBUG_RALPH_LIVE") == "1")
    C.banner(f"cold-start ({'LIVE planner' if live else 'canned plan'}) — brief -> spec + hydrated lattice + build tickets")
    plan = _live_plan(name, brief_text, model) if live else _canned_plan(brief_text)
    activated = apply_plan(inst, plan, api)
    _close_prompt_ticket(inst, api)
    api._store.rebuild(inst)

    grid = {c["id"]: c["maturity"] for c in api.lattice_grid(inst)}
    print(f"  seeded {len(plan.get('cells', []))} cells, {len(activated)} active build tickets")
    print("  lattice:", json.dumps({k: v for k, v in sorted(grid.items())}, indent=0).replace('"', ''))
    return {"cells": len(plan.get("cells", [])), "tickets": activated}


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    name = argv[0]
    mock = "--mock" in argv
    model = argv[argv.index("--model") + 1] if "--model" in argv else None
    coldstart(name, mock=mock, model=model)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
