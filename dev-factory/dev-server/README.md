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

## Run

```bash
# headless verification (no deps): the whole coordination path
python3 store.py selftest && python3 api.py selftest

# the live server (Crawl: heartbeat OFF)
pip install fastapi uvicorn
DEV_FACTORY_DIR=/path/to/project/.agents/dev-factory uvicorn app:app --port 8731

# point the server at a different kernel checkout
DEV_KERNEL_BIN=/path/to/dev-kernel/bin uvicorn app:app
```

## Bootstrapping status

- **Crawl — MET.** `evals/crawl-milestone/replay.py`: a cell driven `absent → validated` through the API,
  every gate firing, a critic-written signal on disk, the full arc in the ledger + index. Heartbeat OFF.
- **Walk — next.** Enable the 30s heartbeat at Tier 1 (dispatch, human reviews at `in-review`); add the
  compass `rank`, the dispatcher + `DispatchAdapter`, and the web UI over the SSE stream.
