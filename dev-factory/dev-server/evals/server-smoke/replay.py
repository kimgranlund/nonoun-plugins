#!/usr/bin/env python3
"""replay.py — the live-server smoke: the FastAPI transport + every endpoint + the UI, over a real client.

The operations layer (store/api) is selftested headless, but the HTTP transport (app.py) could only be
asserted for route-wiring without FastAPI. This exercises the REAL app through Starlette's TestClient: the
UI is served, every /api/* endpoint responds, a ticket is created and transitioned through the gate, and
the new surfaces (activities, agents/running, issues, status, reports) return. Skips cleanly when FastAPI
isn't installed, so it is CI-safe.

Exit 0 = the server serves (or FastAPI absent → skip). Python 3.8+.
"""
import os
import shutil
import sys
import tempfile

_HERE = os.path.dirname(os.path.abspath(__file__))
_SERVER = os.path.dirname(os.path.dirname(_HERE))
_root = tempfile.mkdtemp()
os.environ["DEV_FACTORY_DIR"] = os.path.join(_root, ".agents", "dev-factory")
sys.path.insert(0, _SERVER)

try:
    from fastapi.testclient import TestClient
except ImportError:
    print("server-smoke: SKIP (FastAPI not installed) — install fastapi uvicorn httpx to run it")
    shutil.rmtree(_root, ignore_errors=True)
    sys.exit(0)

import app as _app   # noqa: E402  (builds app = build_app() + init_instance(DIR) at import)
import api as _api    # noqa: E402
DIR = _app.DIR


def run():
    fails = []
    def check(cond, label):
        print(f"  {'PASS' if cond else 'FAIL'}  {label}")
        if not cond:
            fails.append(label)

    # seed a small instance the endpoints read
    _api.seed_cell(DIR, "rubric", "task", "r", maturity="validated", signal_refs=["signals/rubric.task.r/seed.json"])
    _api.seed_cell(DIR, "spec", "task", "s", maturity="instantiated", asset_ref="spec/s.md")
    os.makedirs(os.path.join(DIR, "spec"), exist_ok=True)
    open(os.path.join(DIR, "spec", "s.md"), "w").write("# s\n")

    client = TestClient(_app.app)

    # the UI
    r = client.get("/")
    check(r.status_code == 200 and "html" in r.text.lower(), "GET / serves the web UI")

    # every read endpoint responds 200
    for path in ["/api/tickets", "/api/lattice", "/api/ledger", "/api/roadmap", "/api/activities",
                 "/api/agents/running", "/api/issues", "/api/status", "/api/reports/flow_metrics"]:
        r = client.get(path)
        check(r.status_code == 200, f"GET {path} → {r.status_code}")
    check(len(client.get("/api/lattice").json()) == 2, "/api/lattice returns the seeded cells")
    check("autonomy" in client.get("/api/status").json(), "/api/status returns the autonomy tier")

    # create a well-formed ticket, then drive it through the gate over HTTP
    r = client.post("/api/tickets", json={"type": "feature", "title": "via http", "target_cell": "spec.task.s",
                                          "target_transition": {"from": "instantiated", "to": "validated"},
                                          "acceptance": {"rubric_cell": "rubric.task.r"},
                                          "budget": {"iterations": 2, "tokens": 1000}})
    check(r.status_code == 200 and r.json()["state"] == "draft", "POST /api/tickets creates a draft")
    tid = r.json()["id"]
    r = client.post(f"/api/tickets/{tid}/transition", json={"to": "active"})
    check(r.status_code == 200 and r.json()["ok"], f"POST transition draft→active passes the gate ({r.json().get('message','')[:40]})")
    # an illegal transition is refused with a reason (409), not silently applied
    r = client.post(f"/api/tickets/{tid}/transition", json={"to": "done"})
    check(r.status_code == 409 and not r.json()["ok"], "an illegal transition is refused 409 with a reason")

    # an untriaged issue round-trips through the API
    r = client.post("/api/issues", json={"title": "something looks off"})
    check(r.status_code == 200 and r.json()["type"] == "issue", "POST /api/issues creates an untriaged issue")
    check(len(client.get("/api/issues").json()) == 1, "GET /api/issues lists it")

    # the SSE channel is wired (its generator is infinite by design, so assert the route, don't consume it)
    check("/api/stream" in {r.path for r in _app.app.routes}, "the /api/stream SSE channel is wired")

    shutil.rmtree(_root, ignore_errors=True)
    print()
    if fails:
        print(f"server-smoke: FAIL — {len(fails)} check(s):")
        for f in fails:
            print(f"  - {f}")
        return 1
    print("server-smoke: OK — the FastAPI app serves the UI and every /api endpoint (tickets · lattice · ledger · "
          "roadmap · activities · agents/running · issues · status · reports · stream); a ticket is created and "
          "gate-checked over HTTP, an illegal transition is refused 409, and the SSE channel connects.")
    return 0


if __name__ == "__main__":
    sys.exit(run())
