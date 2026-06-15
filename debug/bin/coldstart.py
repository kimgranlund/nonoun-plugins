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

SLUG = "app"          # the system-scope slug the plan builds under (spec.system.app, capability.system.*)
ACTOR = {"kind": "agent", "id": "cold-start-planner"}


# ─────────────────────────── the plan shape ───────────────────────────
# plan = {
#   "assets":  [{"path": "spec/app.md", "content": "..."}],          # files to write into the instance
#   "cells":   [{"layer","scope","slug","maturity","asset_ref"?,"depends_on"?,"signal_refs"?}],
#   "tickets": [{"target_cell","from","to","rubric_cell","deps":[cell ids],"title"}],
# }

def _canned_plan(brief_text):
    """A deterministic plan that hydrates a buildable vertical slice — the CI plumbing proof (no model).

    Mirrors the proven dispatch path: a validated bootstrap rubric + a spec cell + three capability cells, all
    seeded `instantiated` (planner stubs) with build tickets that VALIDATE them instantiated->validated. A real
    planner (live mode) seeds capability cells at `defined` and the workers author them; the apply logic is the
    same."""
    title = brief_text.strip().splitlines()[0].lstrip("# ").strip() or "the app"
    features = ["core", "ui", "persistence"]   # generic slice; the live planner derives real feature slugs
    rubric_id = f"rubric.system.{SLUG}"
    spec_id = f"spec.system.{SLUG}"
    assets = [{"path": f"spec/{SLUG}.md", "content": f"# Spec — {title}\n\n{brief_text}\n"}]
    cells = [
        {"layer": "rubric", "scope": "system", "slug": SLUG, "maturity": "validated",
         "signal_refs": [f"signals/{rubric_id}/seed.json"]},
        {"layer": "spec", "scope": "system", "slug": SLUG, "maturity": "instantiated", "asset_ref": f"spec/{SLUG}.md"},
    ]
    tickets = [{"target_cell": spec_id, "from": "instantiated", "to": "validated", "rubric_cell": rubric_id,
                "deps": [], "title": f"validate the spec for {title}"}]
    for feat in features:
        cid = f"capability.system.{feat}"
        assets.append({"path": f"capability/{feat}.md", "content": f"# {feat} (planner stub)\n"})
        cells.append({"layer": "capability", "scope": "system", "slug": feat, "maturity": "instantiated",
                      "asset_ref": f"capability/{feat}.md", "depends_on": [spec_id]})
        tickets.append({"target_cell": cid, "from": "instantiated", "to": "validated", "rubric_cell": rubric_id,
                        "deps": [spec_id], "title": f"build {feat}"})
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
    activated = []
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
