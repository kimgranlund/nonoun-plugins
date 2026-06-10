#!/usr/bin/env python3
"""check-mcp-liveness.py — assert every bundled MCP server actually SERVES (the AP-P7 gate).

The critic council's liveness finding, mechanized. A plugin can wire an MCP server in `.mcp.json`
whose script defines a `TOOLS` list and exits — with no JSON-RPC loop. `validate_plugin.py` passes it
(paths legal, JSON well-typed), yet it is 100% non-functional and charges failed-startup cost every
session. Static validation proves WIRING; it never proves EXECUTION. This gate proves execution: it
spawns each declared server, completes an `initialize` + `tools/list` handshake over newline-delimited
stdio, and requires a well-formed JSON-RPC response carrying a tools array.

TRUST BOUNDARY — read before pointing this anywhere. This gate EXECUTES the server, so it is for
TRUSTED catalog plugins only (our own, in CI). The critic council reviewing an UNTRUSTED bundle must
NEVER execute it — there, liveness stays a cold-read finding (`references/critics/eval-prompts.md`
CF5; `references/rubrics/plugins-holistic.md` AP-P7). Do not run this against an unvetted plugin.

A plugin with no `.mcp.json` is a clean SKIP (nothing wired = nothing to prove).

Usage:
  check-mcp-liveness.py plugin <dir>          # check one plugin's bundled MCP server(s)
  check-mcp-liveness.py marketplace <dir>     # check every plugin listed in <dir>/.claude-plugin/marketplace.json
  check-mcp-liveness.py selftest              # prove the gate: PASS a live server, FAIL a dead-but-wired one

Exit 0 = every declared server served (or none declared); 1 = a wired server failed to serve.
Stdlib only; Python 3.8+.
"""
import json
import os
import subprocess
import sys
import tempfile

TIMEOUT = 15  # seconds per server handshake — generous; a real server answers in milliseconds

_INIT = {"jsonrpc": "2.0", "id": 1, "method": "initialize",
         "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "liveness-gate", "version": "1"}}}
_LIST = {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}


def _resolve(args, plugin_root):
    """Substitute ${CLAUDE_PLUGIN_ROOT} the way Claude Code does at launch."""
    return [a.replace("${CLAUDE_PLUGIN_ROOT}", plugin_root) for a in args]


def _probe(command, args, plugin_root):
    """Spawn one server and run the handshake. Return (ok: bool, detail: str)."""
    # Faithful to the manifest, but map the conventional `python3`/`python` to THIS interpreter so the
    # gate is hermetic on a runner where the bare name may be absent or a different version.
    exe = sys.executable if command in ("python3", "python") else command
    argv = [exe] + _resolve(args, plugin_root)
    env = dict(os.environ, CLAUDE_PLUGIN_ROOT=plugin_root)
    payload = json.dumps(_INIT) + "\n" + json.dumps(_LIST) + "\n"
    try:
        proc = subprocess.run(argv, input=payload, capture_output=True, text=True,
                              timeout=TIMEOUT, env=env, cwd=plugin_root)
    except FileNotFoundError:
        return False, f"command not found: {argv[0]}"
    except subprocess.TimeoutExpired:
        return False, f"no response within {TIMEOUT}s — server hung (a serving loop answers in ms)"

    # Scan stdout for the tools/list response: a JSON-RPC envelope with id==2 and result.tools a list.
    saw_any_json = False
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except ValueError:
            continue
        saw_any_json = True
        if msg.get("id") == 2:
            if "error" in msg:
                return False, f"tools/list returned a JSON-RPC error: {msg['error']}"
            tools = msg.get("result", {}).get("tools")
            if isinstance(tools, list):
                names = ", ".join(t.get("name", "?") for t in tools) or "(none)"
                return True, f"served tools/list — {len(tools)} tool(s): {names}"
            return False, "tools/list response had no result.tools array"

    # No tools/list response. Diagnose the dead-but-wired case explicitly.
    if not proc.stdout.strip():
        tail = (proc.stderr or "").strip().splitlines()[-1:] or ["(no stderr)"]
        return False, f"produced no stdout — defined-and-exited (the AP-P7 dead-but-wired shape); stderr tail: {tail[0][:120]}"
    if not saw_any_json:
        return False, f"emitted non-JSON-RPC stdout: {proc.stdout.strip()[:120]}"
    return False, "responded but never answered tools/list (id=2)"


def check_plugin(path):
    """Return a list of (server_name, ok, detail). Empty list = no MCP declared (clean skip)."""
    mcp = os.path.join(path, ".mcp.json")
    if not os.path.isfile(mcp):
        return []
    try:
        servers = json.load(open(mcp, encoding="utf-8")).get("mcpServers", {})
    except ValueError as e:
        return [("<.mcp.json>", False, f"unparseable .mcp.json: {e}")]
    results = []
    for name, spec in servers.items():
        cmd = spec.get("command")
        if not cmd:
            results.append((name, False, "no command in server spec"))
            continue
        ok, detail = _probe(cmd, spec.get("args", []), os.path.abspath(path))
        results.append((name, ok, detail))
    return results


def _report(label, results):
    if not results:
        print(f"  SKIP  {label} — no .mcp.json (nothing wired)")
        return True
    allok = True
    for name, ok, detail in results:
        print(f"  {'PASS' if ok else 'FAIL'}  {label} · {name} — {detail}")
        allok = allok and ok
    return allok


def cmd_plugin(path):
    ok = _report(os.path.basename(os.path.abspath(path)) or path, check_plugin(path))
    print(f"\nRESULT: {'PASS' if ok else 'FAIL'} (mcp-liveness)")
    return 0 if ok else 1


def cmd_marketplace(path):
    mpath = os.path.join(path, ".claude-plugin", "marketplace.json")
    if not os.path.isfile(mpath):
        print(f"RESULT: FAIL — no marketplace.json at {mpath}")
        return 1
    entries = json.load(open(mpath, encoding="utf-8")).get("plugins", [])
    allok, checked = True, 0
    for e in entries:
        src = e.get("source", "")
        rel = src[2:] if src.startswith("./") else src
        pdir = os.path.join(path, rel)
        if not os.path.isdir(pdir):
            continue
        allok = _report(e.get("name", rel), check_plugin(pdir)) and allok
        checked += 1
    print(f"\nRESULT: {'PASS' if allok else 'FAIL'} (mcp-liveness over {checked} plugin(s))")
    return 0 if allok else 1


_LIVE = (
    "import sys, json\n"
    "for line in sys.stdin:\n"
    "    line = line.strip()\n"
    "    if not line: continue\n"
    "    m = json.loads(line); mid = m.get('id'); method = m.get('method')\n"
    "    if method == 'initialize':\n"
    "        print(json.dumps({'jsonrpc':'2.0','id':mid,'result':{'protocolVersion':'2024-11-05','capabilities':{}}}), flush=True)\n"
    "    elif method == 'tools/list':\n"
    "        print(json.dumps({'jsonrpc':'2.0','id':mid,'result':{'tools':[{'name':'ping','description':'x','inputSchema':{'type':'object'}}]}}), flush=True)\n"
)
# The AP-P7 shape: defines a TOOLS list and exits — no loop, never serves.
_DEAD = "import sys, json\nTOOLS = [{'name': 'dead', 'description': 'never served'}]\n"


def _mk_fixture(root, name, body):
    d = os.path.join(root, name)
    os.makedirs(os.path.join(d, "bin"))
    with open(os.path.join(d, "bin", "server.py"), "w") as f:
        f.write(body)
    with open(os.path.join(d, ".mcp.json"), "w") as f:
        json.dump({"mcpServers": {name: {"command": "python3", "args": ["${CLAUDE_PLUGIN_ROOT}/bin/server.py"]}}}, f)
    return d


def cmd_selftest():
    with tempfile.TemporaryDirectory() as tmp:
        live = _mk_fixture(tmp, "live-srv", _LIVE)
        dead = _mk_fixture(tmp, "dead-srv", _DEAD)
        live_ok = check_plugin(live)[0][1]
        dead_ok = check_plugin(dead)[0][1]
        # also prove the empty case is a clean skip
        skip = check_plugin(tmp) == []
        # label shows the PROBE outcome + whether it matched expectation (✓/✗), so PASS/FAIL is never ambiguous
        print(f"  live server  -> probe says {'SERVED' if live_ok else 'DEAD'}   {'✓' if live_ok else '✗ expected SERVED'}")
        print(f"  dead server  -> probe says {'SERVED' if dead_ok else 'DEAD'}   {'✓ (correctly rejected)' if not dead_ok else '✗ expected DEAD'}")
        print(f"  no .mcp.json -> probe says {'SKIP' if skip else 'CHECKED'}   {'✓' if skip else '✗ expected SKIP'}")
        ok = live_ok and (not dead_ok) and skip
        print(f"\nRESULT: {'PASS' if ok else 'FAIL'} (mcp-liveness selftest)")
        return 0 if ok else 1


def main(argv):
    if len(argv) == 1 and argv[0] == "selftest":
        return cmd_selftest()
    if len(argv) == 2 and argv[0] == "plugin":
        return cmd_plugin(argv[1])
    if len(argv) == 2 and argv[0] == "marketplace":
        return cmd_marketplace(argv[1])
    print(__doc__.split("Usage:")[1].split("Stdlib")[0].strip() if "Usage:" in __doc__ else "usage error", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
