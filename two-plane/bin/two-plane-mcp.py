#!/usr/bin/env python3
"""two-plane-mcp.py — a read-only MCP query surface over a two-plane project. Self-contained (stdlib).

The MCP-as-curated-perimeter pattern (mirrors product-corpus-mcp.py): a small set of task-level,
read-only tools scoped to ONE two-plane project dir, so *other* agents can read the current Charter,
Blueprint, lattice maturities, cross-check verdict, and ledger without re-deriving them — the two docs
become shared, citable context. The project dir (TWO_PLANE_DIR) holds charter.json / blueprint.json /
lattice.json / ledger.jsonl. Unset, the tools return a clear "configure TWO_PLANE_DIR".

Protocol: JSON-RPC 2.0 over newline-delimited stdin/stdout (initialize / tools/list / tools/call / ping).
Read-only by construction: there is no path argument and no write tool, so there is no traversal surface.
Python 3.8+.
"""
import importlib.util
import json
import os
import sys

NAME, VERSION = "two-plane", "0.1.0"
DIR = os.environ.get("TWO_PLANE_DIR", "")

# load the deterministic core (sibling, hyphenated → importlib) for extract / crosscheck / lattice_state
_core_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "two-plane.py")
_spec = importlib.util.spec_from_file_location("two_plane_core", _core_path)
_core = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_core)

TOOLS = [
    {"name": "get_charter", "description": "The OUTSIDE-IN Charter (goals doc). Pass extract=true for the "
     "distilled constraints extract (ranked characteristics + principles + non-goals only) — the prose-"
     "stripped view the Blueprint agent is given.",
     "inputSchema": {"type": "object", "properties": {"extract": {"type": "boolean"}}}},
    {"name": "get_blueprint", "description": "The INSIDE-OUT Blueprint (structure doc): mechanisms with "
     "the characteristic ids they serve, honored principles, and the charter_ref it was derived against.",
     "inputSchema": {"type": "object", "properties": {}}},
    {"name": "lattice_status", "description": "Each cell's maturity and whether it is STALE relative to "
     "the current docs (a charter drift stales the blueprint + cross-check). The maintainer's view.",
     "inputSchema": {"type": "object", "properties": {}}},
    {"name": "crosscheck", "description": "Run the deterministic seam gate over the current docs: every "
     "ranked characteristic served, principles acknowledged, not stale. Returns the findings.",
     "inputSchema": {"type": "object", "properties": {}}},
    {"name": "read_ledger", "description": "The most recent append-only ledger events (produce / grade / "
     "cross-check / regeneration). limit defaults to 20.",
     "inputSchema": {"type": "object", "properties": {"limit": {"type": "integer"}}}},
]


def _no_dir():
    return ("two-plane is not configured. Set TWO_PLANE_DIR to a two-plane project directory holding "
            "charter.json / blueprint.json / lattice.json / ledger.jsonl.")


def _load(fname):
    path = os.path.join(DIR, fname)
    if not os.path.isfile(path):
        return None
    try:
        return json.load(open(path, encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def call(name, args):
    """Return (text, is_error)."""
    if not DIR or not os.path.isdir(DIR):
        return (_no_dir(), True)
    if name == "get_charter":
        ch = _load("charter.json")
        if ch is None:
            return ("no charter.json in the project dir.", True)
        out = _core.extract(ch) if args.get("extract") else ch
        return (json.dumps(out, indent=2, ensure_ascii=False), False)
    if name == "get_blueprint":
        bp = _load("blueprint.json")
        return (json.dumps(bp, indent=2, ensure_ascii=False), False) if bp else ("no blueprint.json.", True)
    if name == "lattice_status":
        latt, ch, bp = _load("lattice.json"), _load("charter.json"), _load("blueprint.json")
        if not (latt and ch and bp):
            return ("need lattice.json + charter.json + blueprint.json.", True)
        return (json.dumps(_core.lattice_state(latt, ch, bp), indent=2), False)
    if name == "crosscheck":
        ch, bp = _load("charter.json"), _load("blueprint.json")
        if not (ch and bp):
            return ("need charter.json + blueprint.json.", True)
        fails, warns = _core.crosscheck(ch, bp)
        lines = ["FAIL: %s — %s" % (k, m) for k, m in fails] + ["warn: %s — %s" % (k, m) for k, m in warns]
        return ("ok — seam clear" if not lines else "\n".join(lines), False)
    if name == "read_ledger":
        path = os.path.join(DIR, "ledger.jsonl")
        if not os.path.isfile(path):
            return ("no ledger.jsonl yet.", False)
        limit = args.get("limit") if isinstance(args.get("limit"), int) else 20
        lines = open(path, encoding="utf-8").read().splitlines()
        return ("\n".join(lines[-limit:]) or "(empty ledger)", False)
    return ("unknown tool: %s" % name, True)


def _send(obj):
    sys.stdout.write(json.dumps(obj) + "\n")
    sys.stdout.flush()


def _result(mid, result):
    _send({"jsonrpc": "2.0", "id": mid, "result": result})


def _error(mid, code, msg):
    _send({"jsonrpc": "2.0", "id": mid, "error": {"code": code, "message": msg}})


def serve():
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
            _result(mid, {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}},
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
            _error(mid, -32601, "method not found: %s" % method)
    return 0


def selftest():
    """Smoke the tools over a synthetic two-plane project dir; no external state needed."""
    import tempfile
    global DIR
    fails = []
    tmp = tempfile.mkdtemp(prefix="two-plane-mcp-selftest-")
    DIR = tmp
    json.dump(_core._CHARTER, open(os.path.join(tmp, "charter.json"), "w"))
    json.dump(_core._BP_GREEN, open(os.path.join(tmp, "blueprint.json"), "w"))
    json.dump(_core._LATTICE, open(os.path.join(tmp, "lattice.json"), "w"))
    open(os.path.join(tmp, "ledger.jsonl"), "w").write('{"event":"a"}\n{"event":"b"}\n')
    # get_charter extract must strip prose
    t, e = call("get_charter", {"extract": True})
    if e or "diagnosis" in t or "characteristics" not in t:
        fails.append("get_charter extract leaked prose or failed: %s" % t[:80])
    # crosscheck over the green pair is clean
    t, e = call("crosscheck", {})
    if e or not t.startswith("ok"):
        fails.append("crosscheck not clean on green pair: %s" % t[:80])
    # lattice_status returns the cells
    t, e = call("lattice_status", {})
    if e or "blueprint" not in t:
        fails.append("lattice_status failed")
    # read_ledger honors limit
    t, e = call("read_ledger", {"limit": 1})
    if e or t.count("\n") != 0:
        fails.append("read_ledger limit not honored: %r" % t)
    # unconfigured → clear error
    DIR = ""
    t, e = call("get_charter", {})
    if not e or "TWO_PLANE_DIR" not in t:
        fails.append("unconfigured dir not reported as an error")
    if fails:
        for f in fails:
            sys.stderr.write("  - %s\n" % f)
        sys.stderr.write("two-plane-mcp: FAIL (%d)\n" % len(fails))
        return 1
    print("two-plane-mcp: OK — tools smoke + extract isolation + unconfigured-guard verified")
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        raise SystemExit(selftest())
    raise SystemExit(serve())
