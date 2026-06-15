# Server smoke — the answer key

`replay.py` exercises the **real FastAPI transport** through Starlette's `TestClient` — the one surface the
headless selftests couldn't reach (the operations layer is stdlib-tested; the HTTP layer needs FastAPI). It
**skips cleanly when FastAPI isn't installed**, so it's CI-safe; with `pip install fastapi uvicorn httpx` it
runs the live app in-process.

It asserts:
- **GET /** serves the buildless web UI.
- Every read endpoint responds 200: `tickets · lattice · ledger · roadmap · activities · agents/running · issues · status · reports/{name}`.
- **POST /api/tickets** creates a draft; **POST /api/tickets/{id}/transition** drives it through the gate over HTTP; an **illegal transition is refused 409 with a reason** (a UI drag is a gate-checked request, never a silent write).
- **POST /api/issues** creates an untriaged issue and it lists.
- The **/api/stream** SSE channel is wired (its generator is infinite by design, so the test asserts the route rather than consuming it).

```bash
pip install fastapi uvicorn httpx
python3 dev-factory/dev-server/evals/server-smoke/replay.py   # exit 0 = the server serves (or FastAPI absent → skip)
```
