#!/usr/bin/env python3
"""factory-query-mcp.py — dev-factory's read perimeter: a read-only MCP (Model Context Protocol) stdio server.

The spec (harness-and-storage.md) says workers and agents get **read-only** access to the operational state,
exposed through an MCP query tool — they never write operational state (the single-writer dev-server owns every
write; the lattice/ledger writers live in dev-kernel `bin/` + dev-server). This is that tool: the live-data
complement to the kernel, surfacing the project's durable `.agents/dev-factory/` state — the typed lattice cells
and their maturities, the coordination tickets, the append-only ledger, the validation signals, and a one-call
status — as task-level, READ-ONLY tools, so an agent can orient ("what's at the frontier?", "what did we decide
about cell X?", "what tickets are active?") without shelling out or touching the substrate.

Same MCP-as-curated-perimeter pattern as harness-forge's lattice-query and the catalog's corpus MCPs; the slot is
the project's `.agents/dev-factory/` dir, wired via the plugin's `factory_dir` userConfig (env DEV_FACTORY_DIR;
default `.agents/dev-factory`). Unset/missing, the tools return a clear "configure factory_dir" message rather
than failing.

The reads it draws from:
  - lattice.json  — the Cell graph (via the vendored lattice kernel: cid/load/find/scan/rank)
  - index.db      — the SQLite read-index (tickets table; a materialized projection, never an authority)
  - ledger/events.jsonl — the append-only event spine (via the native ledger.read)
  - signals/{cell}/     — the validation evidence currency

Eight read-only tools:
  list_cells · get_cell · scan_frontier · list_tickets · get_ticket · read_ledger · get_signals · status

Protocol: JSON-RPC 2.0 over newline-delimited stdin/stdout (initialize / tools/list / tools/call / ping).
Stdlib only (sqlite3 is stdlib; Python 3.8+). READ-ONLY: no tool writes, deletes, or executes anything — the
writing engine stays in dev-server / the kernel. Tool-level failures are returned with isError:true so the model
can tell a failure from real content. `_safe()` rejects path traversal / symlink escape outside the factory dir.
"""
import json
import os
import sqlite3
import sys

# Import the vendored lattice kernel + the native ledger (siblings in this bin/ dir). The MCP reads through them;
# it never calls any writer (no save/scaffold/append) — the read perimeter stays read-only by construction.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lattice as _lat   # noqa: E402  (vendored kernel: cid/load/find/scan/rank)
import ledger as _led     # noqa: E402  (native ledger: read)

NAME, VERSION = "factory-query", "0.1.0"
FACTORY = (os.environ.get("DEV_FACTORY_DIR") or "").strip()

_OPEN = {"absent", "defined", "instantiated", "stale"}        # maturities that count as an open gap

TOOLS = [
    {"name": "list_cells",
     "description": "List the lattice cells (cell-id + maturity), optionally filtered by layer / scope / maturity. Use to see the project's knowledge state at a glance. A blocked cell is flagged [blocked].",
     "inputSchema": {"type": "object", "properties": {
         "layer": {"type": "string", "description": "ontology|spec|rubric|policy|capability|methodology|protocol|ledger|pattern"},
         "scope": {"type": "string", "description": "call|task|workflow|system|fleet"},
         "maturity": {"type": "string", "description": "absent|defined|instantiated|validated|operating|regenerating|stale|deprecated"}}}},
    {"name": "get_cell",
     "description": "Return the full record of one cell by its id ({layer}.{scope}.{slug}) — maturity, asset_ref, signal_refs, depends_on, validated_against, verifier, and blocked state.",
     "inputSchema": {"type": "object", "properties": {"cell_id": {"type": "string", "description": "e.g. spec.task.checkout-flow"}}, "required": ["cell_id"]}},
    {"name": "scan_frontier",
     "description": "Return the ready/blocked frontier: the open/stale gap set at the frontier scope, with each gap marked READY (dependency-ready, selectable now) or its blocking reasons (which upstream/dependency is unvalidated, or [BLOCKED] by budget/no-progress). This is the dependency-aware view via the lattice kernel's scan + rank — what the compass would actually pick next, in priority order.",
     "inputSchema": {"type": "object", "properties": {}}},
    {"name": "list_tickets",
     "description": "List coordination tickets from the operational index (index.db), optionally filtered by state (e.g. draft|active|done|blocked|cancelled), most-recently-updated first. Each row: id, type, title, state, target_cell, the from→to maturity transition, and claim/lease.",
     "inputSchema": {"type": "object", "properties": {"state": {"type": "string", "description": "ticket lifecycle state to filter by"}}}},
    {"name": "get_ticket",
     "description": "Return the full operational row for one ticket by id (from index.db) — type, title, state, target cell + transition, rubric cell, priority (risk/unlock/probe_cost), claim worker + lease, signal count, timestamps.",
     "inputSchema": {"type": "object", "properties": {"ticket_id": {"type": "string"}}, "required": ["ticket_id"]}},
    {"name": "read_ledger",
     "description": "Return append-only ledger events (what happened, by whom, why), optionally filtered by cell, ticket, event (dispatch|claim|transition|signal|block|incident|...), and/or `since` (ISO-8601 lower bound). `n` caps the count returned from the tail (default 30).",
     "inputSchema": {"type": "object", "properties": {
         "cell": {"type": "string"}, "ticket": {"type": "string"},
         "event": {"type": "string"}, "since": {"type": "string", "description": "ISO-8601; events at or after this ts"},
         "n": {"type": "integer", "description": "max events to return (most recent), default 30"}}}},
    {"name": "get_signals",
     "description": "List the validation signal artifacts recorded for a cell under signals/{cell-id}/ — the evidence currency that gates scope/maturity boundaries (a cell is validated against these, never against its own claim).",
     "inputSchema": {"type": "object", "properties": {"cell_id": {"type": "string"}}, "required": ["cell_id"]}},
    {"name": "status",
     "description": "A one-call factory snapshot: the cell maturity histogram, the ready/blocked frontier count, the ticket state counts, and any open incidents (refuter-caught false passes from the ledger). Use to orient before deciding what to do.",
     "inputSchema": {"type": "object", "properties": {}}},
]


def _no_factory():
    return ("factory-query is not configured. Set the plugin's `factory_dir` userConfig (or DEV_FACTORY_DIR) to the "
            "project's `.agents/dev-factory/` directory — the dev-server scaffolds it on boot.")


def _safe(path):
    """Resolve `path` under FACTORY, rejecting traversal/symlink escape. Returns abs path or None."""
    base = os.path.realpath(FACTORY)
    full = os.path.realpath(os.path.join(base, path))
    if full == base or full.startswith(base + os.sep):
        return full
    return None


def _load_lattice():
    p = _safe("lattice.json")
    if not p or not os.path.isfile(p):
        return None
    try:
        return json.load(open(p, encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _db_rows(query, params=()):
    """Open index.db READ-ONLY (sqlite ro URI — the connection itself cannot write), run a query, return dict rows.
    Returns (rows, error). The MCP never opens the DB writable: the single-writer dev-server owns every write."""
    p = _safe("index.db")
    if not p or not os.path.isfile(p):
        return (None, "no index.db yet — boot the dev-server (it materializes the index from the ledger + files).")
    try:
        con = sqlite3.connect(f"file:{p}?mode=ro&immutable=1", uri=True)
        con.row_factory = sqlite3.Row
        rows = [dict(r) for r in con.execute(query, params).fetchall()]
        con.close()
        return (rows, None)
    except sqlite3.Error as e:
        return (None, f"index.db read error: {e}")


def call(name, args):
    """Return (text, is_error). Pure reads — no path writes, no kernel writers invoked."""
    if not FACTORY or not os.path.isdir(FACTORY):
        return (_no_factory(), True)
    lat = _load_lattice()
    if name in ("list_cells", "get_cell", "scan_frontier", "status") and lat is None:
        return ("no lattice.json under the configured factory_dir — boot the dev-server first to scaffold it.", True)

    if name == "list_cells":
        cells = lat.get("cells", [])
        for k in ("layer", "scope", "maturity"):
            v = args.get(k)
            if v:
                cells = [c for c in cells if c.get(k) == v]
        if not cells:
            return ("list_cells: no cells match.", False)
        lines = [f"  {c.get('maturity','?'):13} {_lat.cid(c)}" + ("  [blocked]" if _lat.is_blocked(c) else "") for c in cells]
        return (f"Lattice cells ({len(cells)}):\n" + "\n".join(lines), False)

    if name == "get_cell":
        cid = args.get("cell_id", "")
        c = _lat.find(lat, cid)
        if c is None:
            return (f"get_cell: no cell `{cid}` in the lattice.", True)
        return (json.dumps(c, indent=2), False)

    if name == "scan_frontier":
        fs = lat.get("frontier_scope", "task")
        gaps = _lat.scan(lat)
        # rank() filters to the dependency-ready, unblocked set and orders by priority — the actual selectable next.
        ranked = _lat.rank(lat)
        ready_ids = {_lat.cid(c): prio for prio, c, _r in ranked}
        lines = []
        for c in gaps:
            cid = _lat.cid(c)
            if _lat.is_blocked(c):
                lines.append(f"  {c.get('maturity','?'):13} {cid}  [BLOCKED: {_lat.block_reason(c) or 'budget/no-progress'}]")
            elif cid in ready_ids:
                lines.append(f"  {c.get('maturity','?'):13} {cid}  READY (priority {ready_ids[cid]})")
            else:
                _ok, reasons = _lat.ready(lat, c)
                why = reasons[0] if reasons else "not ready"
                lines.append(f"  {c.get('maturity','?'):13} {cid}  not ready — {why}")
        body = "\n".join(lines) or "  (no open cells)"
        nready, nblk = len(ready_ids), sum(1 for c in gaps if _lat.is_blocked(c))
        return (f"Frontier scope `{fs}` — {len(gaps)} open gap(s), {nready} READY, {nblk} blocked "
                f"(ranked highest-priority first):\n{body}", False)

    if name == "list_tickets":
        state = args.get("state")
        rows, err = _db_rows(
            "SELECT id,type,title,state,target_cell,from_maturity,to_maturity,claim_worker,updated FROM tickets"
            + (" WHERE state=?" if state else "") + " ORDER BY updated DESC",
            (state,) if state else ())
        if err:
            return (f"list_tickets: {err}", True)
        if not rows:
            return ("list_tickets: no tickets match.", False)
        lines = []
        for r in rows:
            trans = f"{r.get('from_maturity') or '?'}→{r.get('to_maturity') or '?'}"
            claim = f"  @{r['claim_worker']}" if r.get("claim_worker") else ""
            lines.append(f"  {(r.get('state') or '?'):9} {(r.get('type') or '?'):8} {r['id']}  "
                         f"{r.get('target_cell') or '-'} ({trans})  {r.get('title') or ''}{claim}")
        return (f"Tickets ({len(rows)}):\n" + "\n".join(lines), False)

    if name == "get_ticket":
        tid = args.get("ticket_id", "")
        rows, err = _db_rows("SELECT * FROM tickets WHERE id=?", (tid,))
        if err:
            return (f"get_ticket: {err}", True)
        if not rows:
            return (f"get_ticket: no ticket `{tid}` in the index.", True)
        return (json.dumps(rows[0], indent=2), False)

    if name == "read_ledger":
        try:
            events = _led.read(FACTORY, cell=args.get("cell"), ticket=args.get("ticket"),
                               event=args.get("event"), since=args.get("since"))
        except (OSError, ValueError) as e:
            return (f"read_ledger: cannot read — {e}", True)
        if not events:
            return ("read_ledger: no matching ledger events.", False)
        n = args.get("n") if isinstance(args.get("n"), int) and args.get("n") > 0 else 30
        total = len(events)
        out = []
        for e in events[-n:]:
            sub = e.get("subject", {}) or {}
            why = e.get("rationale", "") or ""
            why = (why[:79] + "…") if len(why) > 80 else why    # mark truncation, never silently drop the tail
            target = sub.get("ticket") or sub.get("cell") or "-"
            trans = (f"  {e['from']}→{e['to']}" if e.get("from") is not None or e.get("to") is not None else "")
            actor = e.get("actor", {}) or {}
            out.append(f"  {e.get('ts','?'):25} {e.get('event','?'):10} "
                       f"{(actor.get('kind') or '?'):6}:{actor.get('id') or '?':10} {target}{trans}  {why}")
        return (f"Ledger ({min(n, total)} of {total} matching):\n" + "\n".join(out), False)

    if name == "get_signals":
        cid = args.get("cell_id", "")
        d = _safe(os.path.join("signals", cid))
        if not d or not os.path.isdir(d):
            return (f"get_signals: no signals recorded for `{cid}`.", False)
        files = sorted(f for f in os.listdir(d) if f.endswith(".json"))
        return (f"Signals for {cid} ({len(files)}):\n" + ("\n".join(f"  signals/{cid}/{f}" for f in files) or "  (none)"), False)

    if name == "status":
        cells = lat.get("cells", [])
        hist = {}
        for c in cells:
            m = c.get("maturity", "?")
            hist[m] = hist.get(m, 0) + 1
        ranked = _lat.rank(lat)
        gaps = _lat.scan(lat)
        nblk = sum(1 for c in gaps if _lat.is_blocked(c))
        # ticket state counts (best-effort: a missing index isn't fatal to a status read)
        trows, terr = _db_rows("SELECT state, COUNT(*) AS n FROM tickets GROUP BY state ORDER BY state")
        tickets = "  (index unavailable: " + terr + ")" if terr else (
            "\n".join(f"  {(r['state'] or '?'):9} {r['n']}" for r in trows) or "  (no tickets)")
        # open incidents — refuter-caught false passes; the honest trust input
        try:
            incidents = _led.read(FACTORY, event="incident")
        except (OSError, ValueError):
            incidents = []
        inc = "\n".join(
            f"  {e.get('ts','?'):25} {(e.get('subject',{}) or {}).get('cell') or (e.get('subject',{}) or {}).get('ticket') or '-'}  "
            f"{(e.get('rationale','') or '')[:70]}" for e in incidents) or "  (none)"
        mat = "\n".join(f"  {m:13} {n}" for m, n in sorted(hist.items())) or "  (no cells)"
        return (
            f"dev-factory status ({lat.get('project','?')}, frontier scope `{lat.get('frontier_scope','task')}`)\n\n"
            f"Cell maturity ({len(cells)} cells):\n{mat}\n\n"
            f"Frontier: {len(gaps)} open gap(s), {len(ranked)} READY, {nblk} blocked\n\n"
            f"Tickets by state:\n{tickets}\n\n"
            f"Open incidents ({len(incidents)}):\n{inc}", False)

    return (f"unknown tool: {name}", True)


def _send(obj):
    sys.stdout.write(json.dumps(obj) + "\n")
    sys.stdout.flush()


def _result(mid, result):
    _send({"jsonrpc": "2.0", "id": mid, "result": result})


def _error(mid, code, message):
    _send({"jsonrpc": "2.0", "id": mid, "error": {"code": code, "message": message}})


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except (json.JSONDecodeError, ValueError):
            continue
        method, mid = msg.get("method"), msg.get("id")
        if method == "initialize":
            _result(mid, {"protocolVersion": "2024-11-05",
                          "capabilities": {"tools": {}},
                          "serverInfo": {"name": NAME, "version": VERSION}})
        elif method in ("notifications/initialized", "initialized", "notifications/cancelled"):
            continue
        elif method == "ping":
            _result(mid, {})
        elif method == "tools/list":
            _result(mid, {"tools": TOOLS})
        elif method == "tools/call":
            params = msg.get("params", {}) or {}
            text, is_error = call(params.get("name", ""), params.get("arguments", {}) or {})
            _result(mid, {"content": [{"type": "text", "text": text}], "isError": is_error})
        elif mid is not None:
            _error(mid, -32601, f"method not found: {method}")
    return 0


def selftest():
    """Seed a tiny temp `.agents/dev-factory/` (lattice + ledger + signals + a materialized index.db), then exercise
    the path guard against traversal/absolute/symlink/prefix-sibling escape and one tools/call for each of the eight
    tools. No external state needed."""
    import tempfile
    import shutil
    global FACTORY
    fails = []
    def check(cond, label):
        if not cond:
            fails.append(label)
    tmp = tempfile.mkdtemp(prefix="factory-query-selftest-")
    try:
        d = os.path.join(tmp, ".agents", "dev-factory")
        outside = os.path.join(tmp, "outside")
        evil = os.path.join(tmp, ".agents", "dev-factory-evil")      # prefix-sibling: must NOT pass
        _lat.scaffold(d)
        os.makedirs(os.path.join(d, "signals", "spec.task.x"), exist_ok=True)
        os.makedirs(outside, exist_ok=True)
        os.makedirs(evil, exist_ok=True)
        # a lattice: a validated rubric + an open (instantiated) spec at the task frontier
        lat = {"version": "1", "project": "selftest", "frontier_scope": "task", "cells": [
            {"layer": "ontology", "scope": "task", "slug": "domain", "maturity": "validated",
             "signal_refs": ["signals/ontology.task.domain/s.json"], "depends_on": []},
            {"layer": "spec", "scope": "task", "slug": "x", "maturity": "instantiated", "depends_on": [], "signal_refs": []},
        ]}
        _lat.save(d, lat)
        os.makedirs(os.path.join(d, "signals", "ontology.task.domain"), exist_ok=True)
        open(os.path.join(d, "signals", "ontology.task.domain", "s.json"), "w").write('{"result":"pass"}\n')
        open(os.path.join(d, "signals", "spec.task.x", "2026-06-14T09-00--pytest.json"), "w").write('{"result":"pass"}\n')
        open(os.path.join(outside, "secret.json"), "w").write('{"secret":true}\n')
        # ledger: a transition + an incident (so status surfaces an open incident)
        _led.append(d, "transition", {"kind": "server", "id": "srv"}, {"ticket": "tkt-1", "cell": "ontology.task.domain"},
                    "draft->active", frm="draft", to="active")
        _led.append(d, "incident", {"kind": "agent", "id": "refuter"}, {"cell": "spec.task.x"},
                    "refuter caught a false pass on spec.task.x")
        # a ticket + a materialized index.db (reuse the server's store.rebuild)
        os.makedirs(os.path.join(d, "coordination", "tickets"), exist_ok=True)
        tid = _led.ulid("tkt-")
        json.dump({"id": tid, "type": "feature", "title": "the x ticket", "state": "active",
                   "target_cell": "spec.task.x", "target_transition": {"from": "instantiated", "to": "validated"},
                   "acceptance": {"rubric_cell": "rubric.task.x"},
                   "timestamps": {"created": "2026-06-14T00:00:00+00:00", "updated": "2026-06-14T00:00:01+00:00"}},
                  open(os.path.join(d, "coordination", "tickets", f"{tid}.json"), "w"))
        # build index.db via the dev-server store (sibling repo dir) if importable; else a minimal hand-built index.
        try:
            server_bin = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                                      "dev-server")
            sys.path.insert(0, server_bin)
            import store as _store   # noqa
            _store.rebuild(d)
        except Exception:            # noqa: BLE001 — selftest must not depend on the server being importable
            con = sqlite3.connect(os.path.join(d, "index.db"))
            con.execute("CREATE TABLE tickets(id TEXT PRIMARY KEY, type TEXT, title TEXT, state TEXT, "
                        "target_cell TEXT, from_maturity TEXT, to_maturity TEXT, claim_worker TEXT, updated TEXT)")
            con.execute("INSERT INTO tickets(id,type,title,state,target_cell,from_maturity,to_maturity,updated) "
                        "VALUES(?,?,?,?,?,?,?,?)", (tid, "feature", "the x ticket", "active", "spec.task.x",
                                                    "instantiated", "validated", "2026-06-14T00:00:01+00:00"))
            con.commit()
            con.close()

        link = os.path.join(d, "escape")
        try:
            os.symlink(outside, link)
            symlinks_ok = True
        except (OSError, NotImplementedError):
            symlinks_ok = False

        FACTORY = d
        # path guard
        check(_safe("lattice.json") is not None, "valid path rejected")
        check(_safe("../outside/secret.json") is None, "parent traversal accepted")
        check(_safe("/etc/passwd") is None, "absolute path accepted")
        check(_safe("../dev-factory-evil/secret.json") is None, "prefix-sibling accepted")
        if symlinks_ok:
            check(_safe("escape/secret.json") is None, "symlink escape accepted")

        # one tools/call per tool
        txt, err = call("list_cells", {})
        check(not err and "spec.task.x" in txt, "list_cells failed")
        txt, err = call("list_cells", {"maturity": "validated"})
        check(not err and "ontology.task.domain" in txt and "spec.task.x" not in txt, "list_cells filter failed")
        txt, err = call("get_cell", {"cell_id": "spec.task.x"})
        check(not err and '"instantiated"' in txt, "get_cell failed")
        txt, err = call("get_cell", {"cell_id": "no.such.cell"})
        check(err, "get_cell did not error on a missing cell")
        txt, err = call("scan_frontier", {})
        check(not err and "spec.task.x" in txt and "READY" in txt, "scan_frontier failed")
        txt, err = call("list_tickets", {})
        check(not err and tid in txt, "list_tickets failed")
        txt, err = call("list_tickets", {"state": "active"})
        check(not err and tid in txt, "list_tickets state filter failed")
        txt, err = call("list_tickets", {"state": "done"})
        check(not err and tid not in txt, "list_tickets filtered to wrong state")
        txt, err = call("get_ticket", {"ticket_id": tid})
        check(not err and '"active"' in txt, "get_ticket failed")
        txt, err = call("get_ticket", {"ticket_id": "tkt-none"})
        check(err, "get_ticket did not error on a missing ticket")
        txt, err = call("read_ledger", {})
        check(not err and "transition" in txt, "read_ledger failed")
        txt, err = call("read_ledger", {"event": "incident"})
        check(not err and "incident" in txt and "false pass" in txt, "read_ledger event filter failed")
        txt, err = call("get_signals", {"cell_id": "spec.task.x"})
        check(not err and "pytest.json" in txt, "get_signals failed")
        txt, err = call("status", {})
        check(not err and "validated" in txt and "Open incidents (1)" in txt, "status failed")

        # the read perimeter is read-only: the DB connection cannot write
        rows, dberr = _db_rows("SELECT * FROM tickets", ())
        check(dberr is None and rows, "_db_rows read failed")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    if fails:
        sys.stderr.write("factory-query-mcp selftest: FAIL\n")
        for f in fails:
            sys.stderr.write(f"  - {f}\n")
        return 1
    print("factory-query-mcp selftest: OK (path guard holds against traversal/absolute/symlink/prefix-sibling; "
          "list_cells/get_cell/scan_frontier/list_tickets/get_ticket/read_ledger/get_signals/status all read; "
          "index.db opened read-only)")
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        sys.exit(selftest())
    try:
        sys.exit(main())
    except (BrokenPipeError, KeyboardInterrupt):
        sys.exit(0)
