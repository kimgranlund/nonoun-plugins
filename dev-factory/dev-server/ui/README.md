# dev-factory web UI — the board IS the repo, projected

The buildless static front-end for the dev-server (TDD §9.4, REQ-UI-001..005). Three files, no framework, no build step, no npm: `index.html` + `app.js` (vanilla web components on a tiny inlined reactive base) + `styles.css` (OKLCH design tokens, themed via `color-scheme: light dark`). House style is borrowed from `tools/corpus-reader/` — light-DOM custom elements, a perceptual OKLCH palette driven by a few hue + chroma axes, and a single-file-friendly shape.

It is a *window onto substrate*: every card and grid cell is a rendering of a git-tracked file the server materialized, and every mutating action is a server-mediated, ledgered request — the UI never writes substrate directly. A Kanban drag POSTs a transition *request*; the gate runs server-side; an illegal one comes back `409` and the UI surfaces the refusal reason as a toast.

## The five views

A top nav switches five views (routed off `location.hash`, so each is deep-linkable — `#kanban`, `#lattice`, `#ledger`, `#monitor`, `#roadmap`):

1. **Kanban — two lenses.** A lens toggle swaps between (a) the **Ticket lens** — columns are the ticket states (`draft·active·claimed·in-progress·in-review·done` + `blocked·paused·cancelled`), cards are tickets, a drag from one column to another `POST`s `/api/tickets/{id}/transition {to}` (keyboard-draggable too: focus a card, Space to pick up, ← → to move, Enter to drop, Esc to cancel), and a per-column `+` opens a create modal that `POST`s `/api/tickets`; and (b) the **Agent / activity lens** — swimlanes per agent, activity cards in live status columns (`queued·running·handed-off·completed` + `blocked·failed`) badged with the operation kind, target cell, an `orchestration_shape`/`loop_strategy` badge, a burning-budget bar, and a `parent_activity` delegation tree. Activities come from a future `/api/activities`; until it exists the lens degrades, deriving cards from the ledger's `activity-*`/`dispatch`/`handoff` events, and shows an empty state when there are none.
2. **Lattice grid.** Rows are the nine layers, columns the five scopes; each cell is colored by maturity (`absent → deprecated`), badged with signal count + a staleness/blocked flag; click a cell for a detail panel (artifact ref, signals, the tickets and ledger events targeting it). Data: `GET /api/lattice`.
3. **Ledger feed.** A live append-only stream of events (`dispatch·claim·transition·signal·block·demote·regenerate` + `activity-*`), newest first, with a fresh-event flash. Data: `GET /api/ledger`, live via SSE.
4. **Agent monitor.** The running slice — live workers, target cells, worktrees, delegation depth, and iteration/token/wall-clock budget gauges, with `Cancel` (→ `DELETE /api/tickets/{id}`) and `Checkpoint` (a dispatcher control stub) controls. Prefers a future `GET /api/agents/running`; degrades to claimed/in-progress tickets. In Crawl the heartbeat is OFF, so this is empty until dispatch runs.
5. **Roadmap & backlog.** Epics from `GET /api/roadmap` decomposing into their member tickets (with a done-rollup progress bar and dependency order), plus a backlog of issues awaiting triage. Tickets cross-reference `GET /api/tickets`.

## Live wiring (no polling)

The shell subscribes once to `GET /api/stream` (Server-Sent Events). Each event is `data: {"kind": "ticket"|"lattice"|"tick", "payload": ...}`; the client patches only the affected view in place — a `ticket` payload upserts that ticket (normalizing the file-of-record shape to the flat materialized shape the board renders), a `lattice` payload replaces the grid, a `tick` payload updates the heartbeat summary + grid. Any committed write also cheaply re-pulls the ledger tail. On a dropped stream the connection indicator flips to *reconnecting…* and the client reconnects with exponential backoff (1s → 15s), re-syncing the active view on reconnect — never a full reload. Every endpoint loads independently, so an empty or `404` view (e.g. the not-yet-built `/api/activities`) renders a graceful empty state instead of blanking the others.

## How `app.py` serves it

The UI is meant to be served *by the dev-server* so it shares an origin with the API and the SSE stream (no CORS, same-origin `fetch`). Mount this folder as static files. Add **one** of these to `app.py`'s `build_app()` (the maintainer wires the static mount — the UI does not touch `app.py`/`api.py`/`store.py`):

```python
# at the top of app.py:
from fastapi.staticfiles import StaticFiles

# inside build_app(), AFTER the /api routes are registered (so /api/* wins over the catch-all):
app.mount("/", StaticFiles(directory=os.path.join(_HERE, "ui"), html=True), name="ui")
```

`html=True` serves `ui/index.html` at `/`. Mounting at `/` last keeps the `/api/*` routes ahead of the static catch-all. Then:

```bash
pip install fastapi uvicorn
DEV_FACTORY_DIR=/path/to/project/.agents/dev-factory uvicorn app:app --port 8731
# open http://localhost:8731/
```

Opening `index.html` directly over `file://` is blocked (ES modules, `fetch`, and same-origin SSE all require HTTP) — the page detects this and tells you to run the server instead.
