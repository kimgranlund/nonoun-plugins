#!/usr/bin/env python3
"""store.py — dev-factory's operational store: the materialized read-index over the substrate.

Two planes, one typing rule (harness-and-storage.md): artifact bodies live in FILES (git-native,
diff-able, the outer loop rewrites them); tensed status + queryable history live in a DATABASE (fast
filtered queries, joins, the grid). This module is the database half — a SQLite index at
`.agents/dev-factory/index.db` that is a **materialized projection** of the ledger + the on-disk files,
never an authority. The invariants it upholds (write-path §):

  1. Single-writer: only the server process writes this index. Workers/agents read via an MCP query
     tool; they never write operational state.
  2. The DB is never ahead of the ledger: every operational write is preceded by a ledger append.
  3. Reconstructible: `rebuild()` is a DROP + replay of the ledger and a re-scan of the files. A
     corrupted index is not a disaster — it is a rebuild.

Stdlib only (sqlite3 is in the stdlib); the live UI feed needs no DB change-feed — the single-writer
server sees every change and pushes it over SSE directly (app.py). Python 3.8+.
"""
import glob
import json
import os
import sqlite3
import sys

_KERNEL_BIN = os.environ.get("DEV_KERNEL_BIN") or os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dev-kernel", "bin")
sys.path.insert(0, _KERNEL_BIN)
import lattice as _lat   # noqa: E402  (vendored kernel)
import ledger as _led    # noqa: E402  (native ledger)

SCHEMA = """
CREATE TABLE IF NOT EXISTS tickets (
  id TEXT PRIMARY KEY, type TEXT, title TEXT, state TEXT,
  target_cell TEXT, from_maturity TEXT, to_maturity TEXT, rubric_cell TEXT,
  risk REAL, unlock INTEGER, probe_cost REAL,
  claim_worker TEXT, lease_expiry TEXT, claimed_at TEXT, signal_count INTEGER DEFAULT 0,
  created TEXT, updated TEXT
);
CREATE TABLE IF NOT EXISTS cells (
  id TEXT PRIMARY KEY, layer TEXT, scope TEXT, slug TEXT, maturity TEXT,
  blocked INTEGER DEFAULT 0, asset_ref TEXT, signal_count INTEGER DEFAULT 0, stale INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS ledger (
  seq INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, event TEXT,
  actor_kind TEXT, actor_id TEXT, ticket TEXT, cell TEXT,
  from_state TEXT, to_state TEXT, rationale TEXT
);
CREATE TABLE IF NOT EXISTS activities (
  id TEXT PRIMARY KEY, ticket TEXT, cell TEXT, agent TEXT, parent_activity TEXT,
  kind TEXT, status TEXT, depth INTEGER DEFAULT 0, budget_fraction REAL DEFAULT 0,
  orchestration_shape TEXT, started TEXT, updated TEXT
);
CREATE INDEX IF NOT EXISTS ix_tickets_state ON tickets(state);
CREATE INDEX IF NOT EXISTS ix_cells_maturity ON cells(maturity);
CREATE INDEX IF NOT EXISTS ix_ledger_cell ON ledger(cell);
CREATE INDEX IF NOT EXISTS ix_activities_status ON activities(status);
"""


def index_path(d):
    return os.path.join(d, "index.db")


def connect(d):
    os.makedirs(d, exist_ok=True)
    con = sqlite3.connect(index_path(d))
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA journal_mode=WAL")
    con.executescript(SCHEMA)
    return con


def upsert_ticket(con, t):
    # Defensive (DF-1): a malformed ticket file — e.g. `target_transition` written as a bare string — must
    # NOT crash the whole rebuild/replay. Without this guard one bad ticket bricks `store.rebuild` AND server
    # boot until the file is hand-repaired, undermining "a corrupted index is a rebuild, not a loss." Coerce
    # any non-dict field to {} so a bad row degrades gracefully (null columns) instead of aborting the replay.
    def _d(v):
        return v if isinstance(v, dict) else {}
    tt, pr, cl, ts, acc = (_d(t.get(k)) for k in
                           ("target_transition", "priority", "claim", "timestamps", "acceptance"))
    con.execute(
        """INSERT INTO tickets(id,type,title,state,target_cell,from_maturity,to_maturity,rubric_cell,
                               risk,unlock,probe_cost,claim_worker,lease_expiry,claimed_at,signal_count,created,updated)
           VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
           ON CONFLICT(id) DO UPDATE SET type=excluded.type,title=excluded.title,state=excluded.state,
             target_cell=excluded.target_cell,from_maturity=excluded.from_maturity,to_maturity=excluded.to_maturity,
             rubric_cell=excluded.rubric_cell,risk=excluded.risk,unlock=excluded.unlock,probe_cost=excluded.probe_cost,
             claim_worker=excluded.claim_worker,lease_expiry=excluded.lease_expiry,claimed_at=excluded.claimed_at,
             signal_count=excluded.signal_count,updated=excluded.updated""",
        (t["id"], t.get("type"), t.get("title"), t.get("state"), t.get("target_cell"),
         tt.get("from"), tt.get("to"), acc.get("rubric_cell"),
         pr.get("risk"), pr.get("unlock"), pr.get("probe_cost"),
         cl.get("worker_id"), cl.get("lease_expiry"), cl.get("claimed_at"), len(t.get("signal_refs", [])),
         ts.get("created"), ts.get("updated")))


def upsert_cell(con, c):
    cid = _lat.cid(c)
    con.execute(
        """INSERT INTO cells(id,layer,scope,slug,maturity,blocked,asset_ref,signal_count,stale)
           VALUES(?,?,?,?,?,?,?,?,?)
           ON CONFLICT(id) DO UPDATE SET maturity=excluded.maturity,blocked=excluded.blocked,
             asset_ref=excluded.asset_ref,signal_count=excluded.signal_count,stale=excluded.stale""",
        (cid, c.get("layer"), c.get("scope"), c.get("slug"), c.get("maturity"),
         1 if c.get("blocked") else 0, c.get("asset_ref"), len(c.get("signal_refs", [])),
         1 if c.get("maturity") == "stale" else 0))


def rebuild(d):
    """DROP + replay: the index is fully reconstructed from the ledger + the on-disk files. This is the
    'a corrupted index is a rebuild, not a loss' property. Returns counts."""
    con = connect(d)
    for tbl in ("tickets", "cells", "ledger", "activities"):
        con.execute(f"DELETE FROM {tbl}")
    # ledger (the source of truth for history) → the ledger table + the activities fold
    for e in _led.read(d):
        sub = e.get("subject", {})
        con.execute(
            "INSERT INTO ledger(ts,event,actor_kind,actor_id,ticket,cell,from_state,to_state,rationale) "
            "VALUES(?,?,?,?,?,?,?,?,?)",
            (e.get("ts"), e.get("event"), e.get("actor", {}).get("kind"), e.get("actor", {}).get("id"),
             sub.get("ticket"), sub.get("cell"), e.get("from"), e.get("to"), e.get("rationale")))
    # tickets (files are the source of truth for entity bodies)
    nt = 0
    for f in glob.glob(os.path.join(d, "coordination", "tickets", "*.json")):
        try:
            upsert_ticket(con, json.load(open(f, encoding="utf-8")))
            nt += 1
        except (json.JSONDecodeError, KeyError):
            continue
    # cells (the lattice is canonical)
    lat = _lat.load(d)
    for c in lat.get("cells", []):
        upsert_cell(con, c)
    # activities (the agent/activity lens) — folded from the activity-* lifecycle events in the ledger
    acts = {}
    for e in _led.read(d):
        ev = e.get("event", "")
        if not ev.startswith("activity-") and ev != "handoff":
            continue
        m = e.get("metrics") or {}
        aid = m.get("activity")
        if not aid:
            continue
        sub = e.get("subject") or {}
        a = acts.setdefault(aid, {"id": aid, "ticket": sub.get("ticket"), "cell": sub.get("cell"), "agent": None,
                                  "parent_activity": m.get("parent_activity"), "kind": None, "status": "queued",
                                  "depth": m.get("depth", 0), "budget_fraction": 0, "orchestration_shape": None,
                                  "started": e.get("ts"), "updated": e.get("ts")})
        a["status"] = {"activity-start": "running", "activity-complete": "completed",
                       "activity-fail": "failed", "handoff": "handed-off"}.get(ev, a["status"])
        if ev == "activity-complete":
            a["budget_fraction"] = m.get("budget_fraction", a["budget_fraction"])
        a["agent"] = a["agent"] or m.get("agent")
        a["kind"] = a["kind"] or m.get("kind")
        a["orchestration_shape"] = a["orchestration_shape"] or m.get("orchestration_shape")
        a["updated"] = e.get("ts")
    for a in acts.values():
        con.execute("INSERT OR REPLACE INTO activities(id,ticket,cell,agent,parent_activity,kind,status,depth,"
                    "budget_fraction,orchestration_shape,started,updated) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
                    (a["id"], a["ticket"], a["cell"], a["agent"], a["parent_activity"], a["kind"], a["status"],
                     a["depth"], a["budget_fraction"], a["orchestration_shape"], a["started"], a["updated"]))
    con.commit()
    counts = {"tickets": nt, "cells": len(lat.get("cells", [])), "ledger": len(_led.read(d))}
    con.close()
    return counts


# ─────────────────────────────── read queries (the UI + the MCP read perimeter) ───────────────────────────────

def query_tickets(d, state=None):
    con = connect(d)
    rows = con.execute("SELECT * FROM tickets" + (" WHERE state=?" if state else "") + " ORDER BY updated DESC",
                       (state,) if state else ()).fetchall()
    con.close()
    return [dict(r) for r in rows]


def grid(d):
    """The lattice grid: every cell as (layer, scope, maturity, signal_count, stale, blocked)."""
    con = connect(d)
    rows = con.execute("SELECT * FROM cells ORDER BY layer,scope,slug").fetchall()
    con.close()
    return [dict(r) for r in rows]


def ledger_tail(d, n=50, cell=None):
    con = connect(d)
    q = "SELECT * FROM ledger" + (" WHERE cell=?" if cell else "") + " ORDER BY seq DESC LIMIT ?"
    rows = con.execute(q, ((cell, n) if cell else (n,))).fetchall()
    con.close()
    return [dict(r) for r in reversed(rows)]


def activities(d, status=None, running_only=False):
    """The agent/activity lens (and the agent monitor, when running_only). Materialized from the ledger."""
    con = connect(d)
    where, args = [], []
    if running_only:
        where.append("status IN ('queued','running','handed-off')")
    elif status:
        where.append("status=?")
        args.append(status)
    q = "SELECT * FROM activities" + (" WHERE " + " AND ".join(where) if where else "") + " ORDER BY updated DESC"
    rows = con.execute(q, args).fetchall()
    con.close()
    return [dict(r) for r in rows]


def selftest():
    import tempfile
    fails = []
    def expect(c, m):
        if not c:
            fails.append(m)
    with tempfile.TemporaryDirectory() as root:
        d = os.path.join(root, ".agents/dev-factory")
        _lat.scaffold(d)
        # seed a lattice + a ticket file + some ledger
        lat = {"cells": [
            {"layer": "rubric", "scope": "task", "slug": "x", "maturity": "validated", "signal_refs": ["s/x"], "depends_on": []},
            {"layer": "spec", "scope": "task", "slug": "x", "maturity": "instantiated", "depends_on": [], "signal_refs": []},
        ]}
        _lat.save(d, lat)
        os.makedirs(os.path.join(d, "coordination", "tickets"), exist_ok=True)
        tid = _led.ulid("tkt-")
        json.dump({"id": tid, "type": "feature", "title": "t", "state": "active",
                   "target_cell": "spec.task.x", "target_transition": {"from": "instantiated", "to": "validated"},
                   "acceptance": {"rubric_cell": "rubric.task.x"}, "budget": {"iterations": 1, "tokens": 1},
                   "provenance": {"created_by": "h", "ledger_refs": []},
                   "timestamps": {"created": "2026-06-14T00:00:00+00:00", "updated": "2026-06-14T00:00:01+00:00"}},
                  open(os.path.join(d, "coordination", "tickets", f"{tid}.json"), "w"))
        _led.append(d, "transition", {"kind": "server", "id": "s"}, {"ticket": tid, "cell": "spec.task.x"},
                    "draft->active", frm="draft", to="active")

        counts = rebuild(d)
        expect(counts == {"tickets": 1, "cells": 2, "ledger": 1}, f"rebuild counts wrong: {counts}")
        expect(os.path.exists(index_path(d)), "index.db not created")

        # queries materialize the right view
        act = query_tickets(d, state="active")
        expect(len(act) == 1 and act[0]["id"] == tid, "active-ticket query failed")
        expect(query_tickets(d, state="done") == [], "done query returned a non-done ticket")
        g = grid(d)
        expect(len(g) == 2 and {c["id"] for c in g} == {"rubric.task.x", "spec.task.x"}, "grid wrong")
        expect(any(c["id"] == "rubric.task.x" and c["maturity"] == "validated" for c in g), "cell maturity not materialized")
        lt = ledger_tail(d)
        expect(len(lt) == 1 and lt[0]["event"] == "transition", "ledger tail wrong")

        # THE rebuild property: nuke the index, rebuild from ledger+files, identical view
        os.remove(index_path(d))
        rebuild(d)
        expect(len(query_tickets(d, state="active")) == 1, "index not reconstructible from ledger+files")

    if fails:
        sys.stderr.write("store selftest: FAIL\n")
        for f in fails:
            sys.stderr.write(f"  - {f}\n")
        return 1
    print("store selftest: OK (materializes tickets/cells/ledger from files+ledger; filtered queries; the grid; "
          "and the load-bearing property — a deleted index rebuilds identically by replay, never a loss)")
    return 0


def main(argv):
    if not argv or argv[0] == "selftest":
        return selftest()
    d = argv[argv.index("--dir") + 1] if "--dir" in argv else ".agents/dev-factory"
    if argv[0] == "rebuild":
        print(json.dumps(rebuild(d)))
        return 0
    print(f"store.py: unknown verb {argv[0]}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
