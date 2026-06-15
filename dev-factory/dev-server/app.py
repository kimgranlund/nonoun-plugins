#!/usr/bin/env python3
"""app.py — the dev-factory server: a thin FastAPI/uvicorn transport over the tested operations layer.

All coordination logic lives in api.py (stdlib, CI-tested); this module is *only* transport + the
heartbeat scheduler + the SSE stream. The same `api.transition_ticket` a human drag calls is what the
heartbeat will call in Walk — the loop is not a separate code path, it is the scheduler calling the API.

Crawl posture: the heartbeat is DISABLED (`HEARTBEAT_ENABLED = False`). Walk flips it on at Tier 1.

Run:  pip install fastapi uvicorn   &&   DEV_FACTORY_DIR=/path/.agents/dev-factory uvicorn app:app
The operations layer needs no FastAPI — `python3 api.py selftest` verifies the whole path headless.

Python 3.8+. FastAPI/uvicorn are the server's only non-stdlib deps (it is NOT a plugin — plugins are
stdlib-only; the server is a separately-distributed app, per the architecture).
"""
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
import api  # noqa: E402  (the tested operations layer — stdlib)

DIR = os.environ.get("DEV_FACTORY_DIR", ".agents/dev-factory")
HEARTBEAT_ENABLED = os.environ.get("DEV_FACTORY_HEARTBEAT") == "1"   # OFF in Crawl; Walk sets it
SERVER_ACTOR = {"kind": "server", "id": "dev-server"}

try:
    from fastapi import FastAPI, HTTPException, Request
    from fastapi.responses import StreamingResponse, JSONResponse
    from fastapi.staticfiles import StaticFiles
    _HAVE_FASTAPI = True
except ImportError:
    _HAVE_FASTAPI = False


# ─────────────────────────── the live stream (single-writer pushes diffs to UIs) ───────────────────────────

class Stream:
    """The server sees every committed write and pushes it over SSE — no DB change-feed needed."""
    def __init__(self):
        self._subs = []

    def publish(self, kind, payload):
        for q in list(self._subs):
            q.append({"kind": kind, "payload": payload})

    def subscribe(self):
        q = []
        self._subs.append(q)
        return q


STREAM = Stream()


def build_app():
    if not _HAVE_FASTAPI:
        return None
    app = FastAPI(title="dev-factory", version="0.1.0")
    api.init_instance(DIR)

    @app.get("/api/tickets")
    def list_tickets(state: str = None):
        return api.list_tickets(DIR, state=state)

    @app.post("/api/tickets")
    async def create_ticket(req: Request):
        b = await req.json()
        t = api.create_ticket(DIR, b.get("type", "task"), b.get("title", ""), b.get("body", ""),
                              target_cell=b.get("target_cell"), target_transition=b.get("target_transition"),
                              acceptance=b.get("acceptance"), budget=b.get("budget"),
                              dependencies=b.get("dependencies"), priority=b.get("priority"),
                              created_by=b.get("created_by", "human"))
        STREAM.publish("ticket", t)
        return t

    @app.get("/api/tickets/{tid}")
    def get_ticket(tid: str):
        t = api.get_ticket(DIR, tid)
        if t is None:
            raise HTTPException(404, "no such ticket")
        return t

    @app.patch("/api/tickets/{tid}")
    async def edit_ticket(tid: str, req: Request):
        t, msg = api.edit_ticket(DIR, tid, await req.json())
        if t is None:
            raise HTTPException(409, msg)
        STREAM.publish("ticket", t)
        return t

    @app.post("/api/tickets/{tid}/transition")
    async def transition(tid: str, req: Request):
        b = await req.json()
        # a UI drag is a transition REQUEST — the gate runs server-side; an illegal one is refused with a reason
        ok, t, msg = api.transition_ticket(DIR, tid, b.get("to"), SERVER_ACTOR, verifier=b.get("verifier"))
        STREAM.publish("ticket", t)
        STREAM.publish("lattice", api.lattice_grid(DIR))
        if not ok:
            return JSONResponse({"ok": False, "reason": msg, "ticket": t}, status_code=409)
        return {"ok": True, "message": msg, "ticket": t}

    @app.delete("/api/tickets/{tid}")
    def cancel(tid: str):
        ok, t, msg = api.cancel_ticket(DIR, tid, SERVER_ACTOR)
        STREAM.publish("ticket", t)
        return {"ok": ok, "message": msg}

    @app.get("/api/lattice")
    def lattice():
        return api.lattice_grid(DIR)

    @app.get("/api/ledger")
    def ledger(cell: str = None, since: str = None):
        return api.ledger_query(DIR, cell=cell, since=since)

    @app.get("/api/roadmap")
    def roadmap():
        return api.roadmap(DIR)

    @app.post("/api/roadmap")
    async def create_epic(req: Request):
        b = await req.json()
        return api.create_epic(DIR, b.get("title", ""), b.get("body", ""), b.get("target_cell"),
                              b.get("tickets"), b.get("created_by", "human"))

    @app.get("/api/activities")
    def activities(status: str = None):
        return api.list_activities(DIR, status=status)

    @app.get("/api/agents/running")
    def agents_running():
        return api.agents_running(DIR)

    @app.get("/api/issues")
    def issues():
        return api.list_issues(DIR)

    @app.post("/api/issues")
    async def create_issue(req: Request):
        b = await req.json()
        return api.create_issue(DIR, b.get("title", ""), b.get("body", ""), b.get("created_by", "human"))

    @app.post("/api/issues/{iss_id}/triage")
    async def triage(iss_id: str, req: Request):
        b = await req.json()
        t, msg = api.triage_issue(DIR, iss_id, b.get("type", "task"), b.get("target_cell"),
                                  b.get("target_transition"), b.get("acceptance"), budget=b.get("budget"),
                                  dependencies=b.get("dependencies"), priority=b.get("priority"))
        if t is None:
            raise HTTPException(409, msg)
        STREAM.publish("ticket", t)
        return t

    @app.get("/api/status")
    def status_view():
        return api.status(DIR)

    @app.get("/api/reports/{name}")
    def reports(name: str, family: str = None, window: int = None):
        kw = {k: v for k, v in (("family", family), ("window", window)) if v is not None}
        try:
            return api.report(DIR, name, **kw)
        except (ValueError, KeyError) as e:
            raise HTTPException(404, f"unknown report: {name} ({e})")

    @app.post("/api/control/demote/{family}")
    async def demote(family: str, req: Request):
        b = await req.json()
        r = api.demote(DIR, family, b.get("cell"), b.get("reason", "manual demotion"))
        STREAM.publish("lattice", api.lattice_grid(DIR))
        return {"family": family, "demoted_to_tier": r}

    @app.post("/api/control/pause")
    def pause():
        global HEARTBEAT_ENABLED
        HEARTBEAT_ENABLED = False
        return {"paused": True}

    @app.post("/api/control/resume")
    def resume():
        global HEARTBEAT_ENABLED
        HEARTBEAT_ENABLED = True
        return {"paused": False}

    @app.get("/api/stream")
    def stream():
        q = STREAM.subscribe()
        def gen():
            import time
            while True:
                while q:
                    yield f"data: {json.dumps(q.pop(0))}\n\n"
                time.sleep(0.5)
        return StreamingResponse(gen(), media_type="text/event-stream")

    # Walk: the 30s heartbeat is wired here, calling the SAME api as a human drag. OFF in Crawl.
    if HEARTBEAT_ENABLED:
        _wire_heartbeat(app)
    # the buildless web UI (the five views over SSE) — mounted LAST so /api/* stays ahead of the catch-all
    ui_dir = os.path.join(_HERE, "ui")
    if os.path.isdir(ui_dir):
        app.mount("/", StaticFiles(directory=ui_dir, html=True), name="ui")
    return app


def _wire_heartbeat(app):
    """Walk: an asyncio interval task that runs one heartbeat tick (compass → dispatcher) every period.
    The loop calls the SAME api a human drag does — it is not a separate code path. Armed on startup; an
    exhausted window halts dispatch (heartbeat.budget_exhausted)."""
    import asyncio
    import heartbeat

    @app.on_event("startup")
    async def _start_heartbeat():
        heartbeat.arm(DIR,
                      deadline_s=int(os.environ.get("DEV_FACTORY_DEADLINE_S", "0")) or None,
                      max_dispatches=int(os.environ.get("DEV_FACTORY_MAX_DISPATCHES", "0")) or None,
                      token_ceiling=int(os.environ.get("DEV_FACTORY_TOKEN_CEILING", "0")) or None)
        tier = int(os.environ.get("DEV_FACTORY_TIER", "1"))
        conc = int(os.environ.get("DEV_FACTORY_CONCURRENCY", "2"))
        period = int(os.environ.get("DEV_FACTORY_PERIOD", "30"))

        async def loop():
            while HEARTBEAT_ENABLED:
                summ = heartbeat.on_tick(DIR, tier=tier, max_concurrency=conc)
                STREAM.publish("tick", {"summary": summ, "lattice": api.lattice_grid(DIR)})
                await asyncio.sleep(period)
        asyncio.create_task(loop())


app = build_app()


def main(argv):
    if argv and argv[0] == "selftest":
        # the transport is thin; the logic is api.py. Here we only assert wiring is importable/consistent.
        if not _HAVE_FASTAPI:
            print("app selftest: SKIP (FastAPI not installed) — the operations layer is tested by `api.py selftest`. "
                  "Install: pip install fastapi uvicorn")
            return 0
        routes = sorted({r.path for r in app.routes if r.path.startswith("/api")})
        expected = {"/api/tickets", "/api/tickets/{tid}", "/api/tickets/{tid}/transition",
                    "/api/lattice", "/api/ledger", "/api/roadmap", "/api/stream"}
        missing = expected - set(routes)
        if missing:
            print(f"app selftest: FAIL — missing routes: {missing}", file=sys.stderr)
            return 1
        print(f"app selftest: OK ({len(routes)} /api routes wired over the tested operations layer; heartbeat "
              f"{'ON' if HEARTBEAT_ENABLED else 'OFF (Crawl)'})")
        return 0
    if not _HAVE_FASTAPI:
        print("dev-factory server needs FastAPI: pip install fastapi uvicorn, then `uvicorn app:app`", file=sys.stderr)
        return 2
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=int(os.environ.get("PORT", "8731")))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
