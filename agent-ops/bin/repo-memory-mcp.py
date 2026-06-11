#!/usr/bin/env python3
"""repo-memory-mcp.py — a minimal MCP (Model Context Protocol) stdio server for repo-memory retrieval.

The live-data complement to agent-ops's `repo-ops` skill (which turns a repo into a memory layer for
coding agents). It is the agent-ops mirror of brand-forge's `brand-corpus` and product-forge's
`product-corpus` MCPs — same MCP-as-curated-perimeter pattern — but the "corpus" is a *repository's
agent-facing memory*: AGENTS.md · CLAUDE.md · README · CHANGELOG · ROADMAP · ADRs, plus the
`.brain/audit-history/` ledger that `audit-history.py` maintains. Point it at a repo (or a docs dir)
via the plugin's `corpus_dir` userConfig; unset, the tools return a clear "configure corpus_dir"
message rather than failing.

Five task-level, read-only tools:
  list_repo_memory · search_repo_memory · fetch_doc · outline_doc · read_audit_ledger

Protocol: JSON-RPC 2.0 over newline-delimited stdin/stdout (initialize / tools/list / tools/call / ping).
Stdlib only (Python 3.8+). Read-only: no tool writes, deletes, or executes anything. Tool-level
failures are returned with isError:true so the model can tell a failure from real content.
"""
import json
import os
import re
import sys

NAME, VERSION = "repo-memory", "0.1.0"
CORPUS = (os.environ.get("REPO_MEMORY_DIR") or "").strip()

# Dirs that are never agent memory — skip them when enumerating a repo (keeps the surface task-level,
# not a filesystem dump, and avoids walking giant build/vendor trees). `.brain` is KEPT (it is memory).
_SKIP_DIRS = {".git", "node_modules", "site", "dist", "build", "__pycache__", ".venv", "venv",
              ".next", "target", ".pytest_cache", ".mypy_cache", "coverage", ".tox"}
_MAX_FILES = 300

TOOLS = [
    {"name": "list_repo_memory",
     "description": "List the repo's agent-memory documents (markdown: AGENTS.md, CLAUDE.md, README, CHANGELOG, ROADMAP, ADRs, and any docs). Use to see what memory exists before fetching.",
     "inputSchema": {"type": "object", "properties": {}}},
    {"name": "search_repo_memory",
     "description": "Search the repo's memory docs for a term and return matching file:line snippets. Use to locate where a decision, convention, or change is recorded.",
     "inputSchema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}},
    {"name": "fetch_doc",
     "description": "Return the full text of one memory document. `path` is relative to the configured root.",
     "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}},
    {"name": "outline_doc",
     "description": "Return the markdown heading outline of one memory document. `path` is relative to the configured root.",
     "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}},
    {"name": "read_audit_ledger",
     "description": "Read the repo's `.brain/audit-history/` ledger if present — the newest-first trend-table README plus the list of audit records. The agent-ops self-healing signal.",
     "inputSchema": {"type": "object", "properties": {}}},
]


def _no_corpus():
    return "repo-memory is not configured. Set the plugin's `corpus_dir` userConfig to a repo (or docs dir) whose agent memory you want to read."


def _safe(path):
    """Resolve `path` under CORPUS, rejecting traversal/symlink escape. Returns abs path or None."""
    base = os.path.realpath(CORPUS)
    full = os.path.realpath(os.path.join(base, path))
    if full == base or full.startswith(base + os.sep):
        return full
    return None


def _md_files():
    """List repo-memory prose files (markdown). Skips noise/build/vendor dirs and any entry whose
    realpath escapes the root (symlink/traversal). Capped so a huge repo can't flood the surface."""
    base = os.path.realpath(CORPUS)
    out = []
    for root, dirs, files in os.walk(base, followlinks=False):
        dirs[:] = [d for d in dirs if d not in _SKIP_DIRS]
        for f in sorted(files):
            if not f.lower().endswith((".md", ".mdx", ".txt")):
                continue
            rel = os.path.relpath(os.path.join(root, f), base)
            if _safe(rel) is None:
                continue
            out.append(rel)
            if len(out) >= _MAX_FILES:
                return sorted(out)
    return sorted(out)


def call(name, args):
    """Return (text, is_error). is_error=True marks a tool-level failure (bad input / not found / not
    configured), distinct from valid content the model should read."""
    if not CORPUS or not os.path.isdir(CORPUS):
        return (_no_corpus(), True)
    if name == "list_repo_memory":
        files = _md_files()
        return ("Repo memory documents:\n" + ("\n".join(f"  {p}" for p in files) if files else "  (none found)"), False)
    if name == "search_repo_memory":
        q = (args.get("query") or "").strip()
        if not q:
            return ("search_repo_memory: provide a `query`.", True)
        rx = re.compile(re.escape(q), re.I)
        hits = []
        for rel in _md_files():
            full = _safe(rel)
            if not full:
                continue
            try:
                for i, line in enumerate(open(full, encoding="utf-8", errors="replace"), 1):
                    if rx.search(line):
                        hits.append(f"{rel}:{i}: {line.strip()[:120]}")
                        if len(hits) >= 40:
                            break
            except OSError:
                continue
            if len(hits) >= 40:
                break
        return (f"search '{q}' — {len(hits)} match(es):\n" + ("\n".join(hits) if hits else "  (no matches)"), False)
    if name in ("fetch_doc", "outline_doc"):
        full = _safe(args.get("path", ""))
        if not full or not os.path.isfile(full):
            return (f"{name}: '{args.get('path','')}' not found under the configured root.", True)
        try:
            text = open(full, encoding="utf-8", errors="replace").read()
        except OSError as e:
            return (f"{name}: cannot read — {e}", True)
        if name == "fetch_doc":
            return (text[:20000] + ("\n…[truncated at 20000 chars]" if len(text) > 20000 else ""), False)
        heads = [ln.rstrip() for ln in text.splitlines() if ln.lstrip().startswith("#")]
        return ("Outline:\n" + ("\n".join(heads) if heads else "  (no headings)"), False)
    if name == "read_audit_ledger":
        ldir = _safe(os.path.join(".brain", "audit-history"))
        if not ldir or not os.path.isdir(ldir):
            return ("read_audit_ledger: no `.brain/audit-history/` ledger found in this repo.", False)
        parts = []
        readme = os.path.join(ldir, "README.md")
        if os.path.isfile(readme):
            raw = open(readme, encoding="utf-8", errors="replace").read()
            parts.append(raw[:12000] + ("\n…[truncated]" if len(raw) > 12000 else ""))
        records = sorted(f for f in os.listdir(ldir) if f.endswith(".json"))
        parts.append(f"\nLedger records ({len(records)}):\n" + ("\n".join(f"  .brain/audit-history/{r}" for r in records[:60]) or "  (none)"))
        return ("\n".join(parts), False)
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
            continue  # notifications: no response
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
    """Exercise the path guard (`_safe`/`_md_files`) against traversal, absolute-path, symlink, and
    prefix-sibling escape, the noise-dir exclusion, and a tools smoke over a synthetic repo with a
    `.brain/audit-history/` ledger. No external repo needed. Exit 0 = pass, 1 = fail."""
    import tempfile
    import shutil
    global CORPUS
    fails = []
    def check(cond, label):
        if not cond:
            fails.append(label)
    tmp = tempfile.mkdtemp(prefix="repo-memory-selftest-")
    try:
        repo = os.path.join(tmp, "repo")
        outside = os.path.join(tmp, "outside")
        evil = os.path.join(tmp, "repo-evil")  # prefix-sibling: shares the "repo" prefix, must NOT pass
        os.makedirs(os.path.join(repo, "docs", "adr"))
        os.makedirs(os.path.join(repo, ".brain", "audit-history"))
        os.makedirs(os.path.join(repo, "node_modules", "pkg"))  # noise dir — must be excluded
        os.makedirs(outside)
        os.makedirs(evil)
        open(os.path.join(repo, "AGENTS.md"), "w", encoding="utf-8").write("# AGENTS\nconventions for agents\n")
        open(os.path.join(repo, "ROADMAP.md"), "w", encoding="utf-8").write("# Roadmap\nthe plan\n")
        open(os.path.join(repo, "docs", "adr", "0001-use-x.md"), "w", encoding="utf-8").write("# ADR 1\ndecision\n")
        open(os.path.join(repo, ".brain", "audit-history", "README.md"), "w", encoding="utf-8").write("# Audit history\ntrend table\n")
        open(os.path.join(repo, ".brain", "audit-history", "2026-06-11.json"), "w", encoding="utf-8").write('{"ok":true}\n')
        open(os.path.join(repo, "node_modules", "pkg", "README.md"), "w", encoding="utf-8").write("# vendor noise\n")
        open(os.path.join(outside, "secret.md"), "w", encoding="utf-8").write("# SECRET\n")
        open(os.path.join(evil, "secret.md"), "w", encoding="utf-8").write("# SECRET\n")
        link = os.path.join(repo, "escape")
        try:
            os.symlink(outside, link)
            symlinks_ok = True
        except (OSError, NotImplementedError):
            symlinks_ok = False

        CORPUS = repo
        # _safe: legitimate paths resolve…
        check(_safe("AGENTS.md") is not None, "valid path was rejected")
        check(_safe("") is not None, "repo root was rejected")
        # …and every escape is refused
        check(_safe("../outside/secret.md") is None, "parent traversal accepted")
        check(_safe("/etc/passwd") is None, "absolute path accepted")
        check(_safe("../repo-evil/secret.md") is None, "prefix-sibling accepted (trailing os.sep guard missing)")
        if symlinks_ok:
            check(_safe("escape/secret.md") is None, "symlink escape accepted")
        # _md_files: includes memory docs, excludes node_modules, never advertises an escaped one
        listed = _md_files()
        check("AGENTS.md" in listed and "ROADMAP.md" in listed, "canonical memory docs not enumerated")
        check(os.path.join("docs", "adr", "0001-use-x.md") in listed, "ADR not enumerated")
        check(not any("node_modules" in p for p in listed), "node_modules noise was enumerated")
        check(not any("secret" in p for p in listed), "escaped doc was enumerated")
        # call(): guard holds at the tool layer; read tools + the audit ledger work
        _, err = call("fetch_doc", {"path": "../outside/secret.md"})
        check(err, "fetch_doc served a path outside the root")
        txt, err = call("list_repo_memory", {})
        check(not err and "AGENTS.md" in txt, "list_repo_memory failed")
        txt, err = call("search_repo_memory", {"query": "conventions"})
        check(not err and "AGENTS.md" in txt, "search_repo_memory failed")
        txt, err = call("read_audit_ledger", {})
        check(not err and "trend table" in txt and "2026-06-11.json" in txt, "read_audit_ledger failed")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    if fails:
        sys.stderr.write("repo-memory-mcp selftest: FAIL\n")
        for f in fails:
            sys.stderr.write(f"  - {f}\n")
        return 1
    print("repo-memory-mcp selftest: OK")
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        sys.exit(selftest())
    try:
        sys.exit(main())
    except (BrokenPipeError, KeyboardInterrupt):
        sys.exit(0)
