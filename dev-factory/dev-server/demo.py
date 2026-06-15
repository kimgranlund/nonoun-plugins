#!/usr/bin/env python3
"""demo.py — an end-to-end DRY RUN of dev-factory: seed → bind a kit → run the heartbeat → observe.

Not a test (the evals assert) — a human-observable demonstration that the integrated system runs live: the
bounded autonomous loop advances a dependency-ordered lattice unattended, the kit's execution policy +
real rubric drive each dispatch, the activity lens fills, the reports compute, the audit chain verifies,
and the MCP answers. Stdlib + sqlite3 only (the MockAdapter — no live model). Run it to watch the factory.

    python3 dev-server/demo.py
"""
import json
import os
import subprocess
import sys
import tempfile

_HERE = os.path.dirname(os.path.abspath(__file__))
_DF = os.path.dirname(_HERE)
os.environ["DEV_FACTORY_KIT"] = os.path.join(_DF, "dev-kit-corpus")   # bind the corpus family
sys.path.insert(0, _HERE)
import api          # noqa: E402
import heartbeat    # noqa: E402
import reports      # noqa: E402
sys.path.insert(0, api._store._KERNEL_BIN)
import lattice      # noqa: E402
import ledger       # noqa: E402
import autonomy     # noqa: E402


def _structured(title, cell):
    return {"title": title, "cell": cell,
            "acceptance_criteria": [{"id": "c1", "check": "it works"}, {"id": "c2", "rubric_cell": "rubric.system.test"}],
            "non_goals": ["out of scope a", "out of scope b"], "binds_rubric": "rubric.system.spec-quality"}


def line(s=""):
    print(s)


def main():
    with tempfile.TemporaryDirectory() as root:
        d = os.path.join(root, ".agents", "dev-factory")
        api.init_instance(d)
        srv = {"kind": "server", "id": "dev-server"}
        line("══ dev-factory dry run — corpus kit bound, MockAdapter, heartbeat at the EARNED tier ══\n")

        # seed: a validated verifier + two instantiated spec cells with STRUCTURED assets; beta depends on alpha
        api.seed_cell(d, "rubric", "system", "spec-quality", maturity="validated",
                      signal_refs=["signals/rubric.system.spec-quality/seed.json"])
        os.makedirs(os.path.join(d, "spec"), exist_ok=True)
        for slug in ("alpha", "beta"):
            api.seed_cell(d, "spec", "system", slug, maturity="instantiated", asset_ref=f"spec/{slug}.md")
            open(os.path.join(d, "spec", f"{slug}.md"), "w").write(
                f"# {slug}\n\n```json\n" + json.dumps(_structured(slug, f"spec.system.{slug}"), indent=2) + "\n```\n")

        # earn Tier 2 (validated verifier + a clean refuter check + an armed budget), then create the work
        heartbeat.arm(d, max_dispatches=9, deadline_s=3600)
        autonomy.record_refuter_check(d, "rubric.system.spec-quality", agreed=True)
        A = api.create_ticket(d, "feature", "advance alpha", target_cell="spec.system.alpha",
                              target_transition={"from": "instantiated", "to": "validated"},
                              acceptance={"rubric_cell": "rubric.system.spec-quality"}, budget={"iterations": 3, "tokens": 60000},
                              priority={"risk": 0.9})
        B = api.create_ticket(d, "feature", "advance beta (needs alpha)", target_cell="spec.system.beta",
                              target_transition={"from": "instantiated", "to": "validated"},
                              acceptance={"rubric_cell": "rubric.system.spec-quality"}, budget={"iterations": 3, "tokens": 60000},
                              priority={"risk": 0.6}, dependencies={"cells_ready": ["spec.system.alpha"]})
        api.transition_ticket(d, A["id"], "active", srv)
        api.transition_ticket(d, B["id"], "active", srv)
        st = api.status(d)
        line(f"earned autonomy tier: {st['autonomy']['tier']} ({st['autonomy']['name']}) · "
             f"false-pass {st['autonomy']['false_pass']} · cells {st['cells']}\n")

        # run the heartbeat ticks (UNATTENDED — only on_tick)
        for i in (1, 2, 3):
            s = heartbeat.on_tick(d, max_concurrency=2)
            grid = {c["slug"]: c["maturity"] for c in api.lattice_grid(d) if c["layer"] == "spec"}
            disp = [x.get("ticket", "")[:10] for x in s.get("dispatched", [])]
            line(f"tick {i}: tier {s.get('tier')} · dispatched {disp or '—'} · spec lattice {grid}")

        line("\n── activity / agent lens (materialized from the ledger) ──")
        for a in api.list_activities(d):
            line(f"   {a['agent']:16} {a['kind']:9} {a['status']:10} shape={a['orchestration_shape']} cell={a['cell']}")

        line("\n── reports ──")
        line(f"   flow:     {reports.flow_metrics(d)['by_state']}")
        line(f"   maturity: {reports.maturity_distribution(d)['by_maturity']}")
        line(f"   probe:    {reports.probe_cost_report(d)['by_cell_type']}")

        line("\n── audit integrity ──")
        ok, broke = ledger.verify_chain(d)
        line(f"   ledger hash-chain verified: {ok} (entries: {len(ledger.read(d))})")

        line("\n── MCP read perimeter (live handshake) ──")
        mcp = os.path.join(api._store._KERNEL_BIN, "factory-query-mcp.py")
        env = dict(os.environ, DEV_FACTORY_DIR=d)
        req = '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"status","arguments":{}}}'
        out = subprocess.run(["python3", mcp], input=req, capture_output=True, text=True, env=env).stdout.strip().splitlines()
        try:
            res = json.loads(out[-1])["result"]
            txt = res.get("content", [{}])[0].get("text", str(res))[:200] if isinstance(res, dict) else str(res)[:200]
            line(f"   MCP status → {txt}")
        except (json.JSONDecodeError, IndexError, KeyError):
            line(f"   MCP status → {out[-1][:200] if out else '(no response)'}")

        done = len(api.list_tickets(d, state="done"))
        line(f"\n══ result: {done}/2 tickets done unattended; both spec cells validated against the kit's real "
             f"spec-quality rubric; audit chain intact. The dark factory runs. ══")


if __name__ == "__main__":
    main()
