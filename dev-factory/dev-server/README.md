# dev-server — the dark-factory runtime

The operational tier of dev-factory (TDD §9): the thing that actually polls, holds leases, serves a
socket, supervises worker subprocesses, and pushes live views. It is **not a plugin** (plugins are
stdlib-only markdown + bins); it is a separately-distributed Python app that drives an instance of the
`dev-kernel` substrate. The same kernel can also be driven by a CI trigger or by a human running one cell
by hand — the server is just the heartbeat that automates it.

## Architecture — a tested stdlib core under a thin transport

The coordination logic is **stdlib + `sqlite3`**, so the whole path is CI-verifiable with no external deps.
FastAPI/uvicorn are only the HTTP transport.

| File | Role | Deps | Tested by |
|---|---|---|---|
| `store.py` | the SQLite read-index — a **materialized projection** of the ledger + files; `rebuild()` is a DROP + replay | stdlib | `store.py selftest` |
| `api.py` | the **single-writer operations layer** — every mutation is gate-checked (via `dev-kernel`), ledgered, written to the file-of-record, then re-materialized, in that order | stdlib | `api.py selftest` |
| `app.py` | the FastAPI/uvicorn transport + the SSE stream + the heartbeat scheduler (OFF in Crawl) | fastapi, uvicorn | `app.py selftest` (skips w/o FastAPI) |

The two planes (harness-and-storage.md): **artifact bodies → files** (git-native, the outer loop rewrites
them); **tensed status + queryable history → the database** (a derived view, rebuildable from the ledger).
The DB is never ahead of the ledger; losing it is a rebuild, not a loss.

## Single-writer discipline

Only the server writes operational state. A UI drag is a transition **request** — the gate runs server-side
and an illegal one is refused with a reason, never silently applied. Workers/agents read via an MCP query
tool; they never write the DB or the lattice. The heartbeat (Walk) calls the **same** `api.transition_ticket`
a human drag does — the loop is the scheduler calling the API, not a separate code path.

## Run — step by step

```bash
# 0. headless verification (no deps): the whole coordination path
python3 store.py selftest && python3 api.py selftest

# 1. init an instance (or the server scaffolds it on boot):
python3 ../dev-kernel/bin/lattice.py init --dir /path/to/project/.agents/dev-factory

# 2. start the live server — family kit bound, heartbeat ON:
pip install fastapi uvicorn
DEV_FACTORY_DIR=/path/to/project/.agents/dev-factory \
  DEV_FACTORY_KIT=/path/to/dev-kit-corpus \
  DEV_FACTORY_HEARTBEAT=1 uvicorn app:app --port 8731
#   open http://127.0.0.1:8731/  for the web UI (Kanban · lattice grid · ledger · agent monitor · roadmap)

# 3. drive it over the API (every mutation is gate-checked + ledgered):
curl -s localhost:8731/api/status                              # autonomy tier · maturity · running agents
curl -s -X POST localhost:8731/api/tickets -d '{"type":"feature","title":"validate auth spec",
  "target_cell":"spec.system.auth","target_transition":{"from":"instantiated","to":"validated"},
  "acceptance":{"rubric_cell":"rubric.system.spec-quality"},"budget":{"iterations":3,"tokens":80000}}'
curl -s -X POST localhost:8731/api/tickets/<id>/transition -d '{"to":"active"}'  # the heartbeat takes it from here
curl -s localhost:8731/api/reports/flow_metrics               # throughput · cycle time

# …or watch the whole loop run end-to-end against a throwaway instance (no live model):
python3 demo.py
```

### Config (env vars)

| Var | Default | What |
|---|---|---|
| `DEV_FACTORY_DIR` | `.agents/dev-factory` | the instance state dir |
| `DEV_KERNEL_BIN` | `../dev-kernel/bin` | the kernel checkout to drive |
| `DEV_FACTORY_KIT` | (none) | the bound family kit dir — its dispatch policy + real verifiers |
| `DEV_FACTORY_HEARTBEAT` | off | `1` enables the bounded 30s autonomous loop |
| `DEV_FACTORY_TIER` · `DEV_FACTORY_CONCURRENCY` · `DEV_FACTORY_PERIOD` | earned · 2 · 30 | loop overrides |

## Bootstrapping status

- **Crawl — MET.** `evals/crawl-milestone/replay.py`: a cell driven `absent → validated` through the API,
  every gate firing, a critic-written signal on disk, the full arc in the ledger + index. Heartbeat OFF.
- **Walk — next.** Enable the 30s heartbeat at Tier 1 (dispatch, human reviews at `in-review`); add the
  compass `rank`, the dispatcher + `DispatchAdapter`, and the web UI over the SSE stream.
