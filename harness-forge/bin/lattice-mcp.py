#!/usr/bin/env python3
"""lattice-mcp.py — a minimal MCP (Model Context Protocol) stdio server for read-only lattice retrieval.

The live-data complement to harness-forge's engine: it surfaces the project's durable `.agents/harness/` state —
the lattice cells and their maturities, the frontier gap-set, the append-only ledger, and the signal
artifacts — as task-level, read-only tools, so an agent can orient ("what's open at the frontier?",
"what did we decide about cell X?") without shelling out. Same MCP-as-curated-perimeter pattern as the
catalog's brand-corpus / product-corpus / repo-memory MCPs; the slot is the project's `.agents/harness/` dir,
wired via the plugin's `harness_dir` userConfig. Unset, the tools return a clear "configure harness_dir"
message rather than failing. The canonical engine (scan/rank/advance/staleness) stays in `lattice.py`;
this server only reads.

Five read-only tools:
  list_cells · get_cell · scan_frontier · read_ledger · get_signals

Protocol: JSON-RPC 2.0 over newline-delimited stdin/stdout (initialize / tools/list / tools/call / ping).
Stdlib only (Python 3.8+). Read-only: no tool writes, deletes, or executes anything. Tool-level failures
are returned with isError:true so the model can tell a failure from real content.
"""
import json
import os
import sys

NAME, VERSION = "lattice-query", "0.1.0"
HARNESS = (os.environ.get("HARNESS_DIR") or "").strip()

_OPEN = {"absent", "defined", "instantiated", "stale"}        # maturities that count as an open gap

TOOLS = [
    {"name": "list_cells",
     "description": "List the lattice cells (cell-id + maturity), optionally filtered by layer / scope / maturity. Use to see the project's knowledge state at a glance.",
     "inputSchema": {"type": "object", "properties": {
         "layer": {"type": "string"}, "scope": {"type": "string"}, "maturity": {"type": "string"}}}},
    {"name": "get_cell",
     "description": "Return the full record of one cell by its id ({layer}.{scope}.{slug}) — maturity, asset_ref, signals, dependencies, verifier, budget.",
     "inputSchema": {"type": "object", "properties": {"cell_id": {"type": "string"}}, "required": ["cell_id"]}},
    {"name": "scan_frontier",
     "description": "Return the open/stale gap set at the lattice's frontier scope — the raw scan (gap detection only), NOT the dependency-filtered ranking. This is what the compass scans, not what it would pick: run `lattice.py rank` for the actual priority-ordered, dependency-ready next cell.",
     "inputSchema": {"type": "object", "properties": {}}},
    {"name": "read_ledger",
     "description": "Return the most recent append-only ledger events (what happened, by whom, why). `n` defaults to 30.",
     "inputSchema": {"type": "object", "properties": {"n": {"type": "integer"}}}},
    {"name": "get_signals",
     "description": "List the validation signal artifacts recorded for a cell under signals/{cell-id}/ — the evidence currency that gates scope boundaries.",
     "inputSchema": {"type": "object", "properties": {"cell_id": {"type": "string"}}, "required": ["cell_id"]}},
]


def _no_harness():
    return "lattice-query is not configured. Set the plugin's `harness_dir` userConfig to the project's `.agents/harness/` directory (run `/harness-seed` first to create it)."


def _safe(path):
    """Resolve `path` under HARNESS, rejecting traversal/symlink escape. Returns abs path or None."""
    base = os.path.realpath(HARNESS)
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


def _cid(c):
    return f"{c['layer']}.{c['scope']}.{c['slug']}"


def _blocked(c):
    """The cell carries an active stop. Dual-reads the canonical `block` object + the legacy `blocked` flag, since
    the MCP reads lattice.json raw (an old, un-migrated instance may still carry the legacy field)."""
    return bool(c.get("block") or c.get("blocked"))


def _breason(c):
    b = c.get("block")
    if isinstance(b, dict):
        return b.get("reason") or ""
    return c.get("blocked_reason") or ""


def call(name, args):
    """Return (text, is_error)."""
    if not HARNESS or not os.path.isdir(HARNESS):
        return (_no_harness(), True)
    lat = _load_lattice()
    if name in ("list_cells", "get_cell", "scan_frontier") and lat is None:
        return ("no lattice.json under the configured harness_dir — run `/harness-seed` first.", True)

    if name == "list_cells":
        cells = lat["cells"]
        for k in ("layer", "scope", "maturity"):
            v = args.get(k)
            if v:
                cells = [c for c in cells if c.get(k) == v]
        if not cells:
            return ("list_cells: no cells match.", False)
        lines = [f"  {c['maturity']:13} {_cid(c)}" + ("  [blocked]" if _blocked(c) else "") for c in cells]
        return (f"Lattice cells ({len(cells)}):\n" + "\n".join(lines), False)

    if name == "get_cell":
        cid = args.get("cell_id", "")
        c = next((c for c in lat["cells"] if _cid(c) == cid), None)
        if c is None:
            return (f"get_cell: no cell `{cid}` in the lattice.", True)
        return (json.dumps(c, indent=2), False)

    if name == "scan_frontier":
        fs = lat.get("frontier_scope", "task")
        gaps = [c for c in lat["cells"] if c["scope"] == fs and c["maturity"] in _OPEN]
        # mark blocked cells (Charity/CV2): a blocked gap is NOT available work — it's out of `rank` until
        # unblocked, and advertising it as open would send an agent to grind a cell the stop-gate denies.
        body = "\n".join(
            f"  {c['maturity']:13} {_cid(c)}" + (f"  [BLOCKED: {_breason(c) or 'budget/no-progress'}]" if _blocked(c) else "")
            for c in gaps) or "  (no open cells)"
        nblk = sum(1 for c in gaps if _blocked(c))
        note = f" — {nblk} blocked (not ready; run `lattice.py rank` for the actual selectable set)" if nblk else ""
        return (f"Gap set at frontier scope `{fs}` ({len(gaps)}{note}):\n{body}", False)

    if name == "read_ledger":
        p = _safe(os.path.join("ledger", "events.jsonl"))
        if not p or not os.path.isfile(p):
            return ("read_ledger: no ledger/events.jsonl yet.", False)
        try:
            lines = [ln.strip() for ln in open(p, encoding="utf-8", errors="replace") if ln.strip()]
        except OSError as e:
            return (f"read_ledger: cannot read — {e}", True)
        n = args.get("n") if isinstance(args.get("n"), int) else 30
        out = []
        for ln in lines[-n:]:
            try:
                e = json.loads(ln)
                why = e.get("rationale", "") or ""
                why = (why[:79] + "…") if len(why) > 80 else why   # mark truncation, never silently drop the tail
                out.append(f"  {e.get('operation','?'):10} {e.get('actor','?'):11} {e.get('cell_id','-')}  {e.get('result','')}  {why}")
            except ValueError:
                continue
        return (f"Ledger (last {min(n, len(lines))} of {len(lines)}):\n" + ("\n".join(out) or "  (empty)"), False)

    if name == "get_signals":
        cid = args.get("cell_id", "")
        d = _safe(os.path.join("signals", cid))
        if not d or not os.path.isdir(d):
            return (f"get_signals: no signals recorded for `{cid}`.", False)
        files = sorted(f for f in os.listdir(d) if f.endswith(".json"))
        return (f"Signals for {cid} ({len(files)}):\n" + ("\n".join(f"  signals/{cid}/{f}" for f in files) or "  (none)"), False)

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
    """Exercise the path guard against traversal/absolute/symlink/prefix-sibling escape, plus a tools smoke
    over a synthetic `.agents/harness/` (lattice + ledger + signals). No external state needed."""
    import tempfile
    import shutil
    global HARNESS
    fails = []
    def check(cond, label):
        if not cond:
            fails.append(label)
    tmp = tempfile.mkdtemp(prefix="lattice-mcp-selftest-")
    try:
        h = os.path.join(tmp, ".agents/harness")
        outside = os.path.join(tmp, "outside")
        evil = os.path.join(tmp, ".agents/harness-evil")           # prefix-sibling: must NOT pass
        os.makedirs(os.path.join(h, "signals", "spec.task.x"))
        os.makedirs(os.path.join(h, "ledger"))
        os.makedirs(outside)
        os.makedirs(evil)
        json.dump({"version": "1", "frontier_scope": "task", "cells": [
            {"layer": "ontology", "scope": "task", "slug": "domain", "maturity": "validated"},
            {"layer": "spec", "scope": "task", "slug": "x", "maturity": "defined"}]},
            open(os.path.join(h, "lattice.json"), "w", encoding="utf-8"))
        open(os.path.join(h, "ledger", "events.jsonl"), "w", encoding="utf-8").write(
            '{"operation":"validate","actor":"advancer","cell_id":"ontology.task.domain","result":"pass","rationale":"typed"}\n')
        open(os.path.join(h, "signals", "spec.task.x", "2026-06-12T09-00--pytest.json"), "w", encoding="utf-8").write('{"result":"pass"}\n')
        open(os.path.join(outside, "secret.json"), "w", encoding="utf-8").write('{"secret":true}\n')
        link = os.path.join(h, "escape")
        try:
            os.symlink(outside, link)
            symlinks_ok = True
        except (OSError, NotImplementedError):
            symlinks_ok = False

        HARNESS = h
        check(_safe("lattice.json") is not None, "valid path rejected")
        check(_safe("../outside/secret.json") is None, "parent traversal accepted")
        check(_safe("/etc/passwd") is None, "absolute path accepted")
        check(_safe("../.agents/harness-evil/secret.json") is None, "prefix-sibling accepted")
        if symlinks_ok:
            check(_safe("escape/secret.json") is None, "symlink escape accepted")

        txt, err = call("list_cells", {})
        check(not err and "spec.task.x" in txt, "list_cells failed")
        txt, err = call("list_cells", {"maturity": "validated"})
        check(not err and "ontology.task.domain" in txt and "spec.task.x" not in txt, "list_cells filter failed")
        txt, err = call("get_cell", {"cell_id": "spec.task.x"})
        check(not err and '"defined"' in txt, "get_cell failed")
        txt, err = call("get_cell", {"cell_id": "no.such.cell"})
        check(err, "get_cell did not error on a missing cell")
        txt, err = call("scan_frontier", {})
        check(not err and "spec.task.x" in txt and "ontology.task.domain" not in txt, "scan_frontier failed")
        txt, err = call("read_ledger", {})
        check(not err and "ontology.task.domain" in txt, "read_ledger failed")
        txt, err = call("get_signals", {"cell_id": "spec.task.x"})
        check(not err and "pytest.json" in txt, "get_signals failed")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    if fails:
        sys.stderr.write("lattice-mcp selftest: FAIL\n")
        for f in fails:
            sys.stderr.write(f"  - {f}\n")
        return 1
    print("lattice-mcp selftest: OK (path guard holds against traversal/absolute/symlink/prefix-sibling; list/get/scan/ledger/signals tools work)")
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        sys.exit(selftest())
    try:
        sys.exit(main())
    except (BrokenPipeError, KeyboardInterrupt):
        sys.exit(0)
