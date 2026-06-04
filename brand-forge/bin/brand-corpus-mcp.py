#!/usr/bin/env python3
"""brand-corpus-mcp.py — a minimal MCP (Model Context Protocol) stdio server for brand-corpus retrieval.

The live-data complement to the `brand-corpus` skill (which teaches corpus structure). It demonstrates
the MCP-as-curated-perimeter pattern: a small set of TASK-LEVEL, read-only tools scoped to one
directory (canonical env BRAND_CORPUS_DIR, alias BRAND_CORPUS_ROOT) — not a 1:1 filesystem wrapper. Point it at a brand's corpus via the
plugin's `corpus_dir` userConfig; unset, the tools return a clear "configure corpus_dir" message
rather than failing.

Protocol: JSON-RPC 2.0 over newline-delimited stdin/stdout (initialize / tools/list / tools/call / ping).
Stdlib only (Python 3.8+). Read-only: no tool writes, deletes, or executes anything. Tool-level
failures are returned with isError:true so the model can tell a failure from real corpus content.
"""
import json
import os
import re
import sys

NAME, VERSION = "brand-corpus", "0.1.0"
# Canonical corpus-root env var is BRAND_CORPUS_DIR; BRAND_CORPUS_ROOT is accepted as a back-compat
# alias (some hand-wired servers — e.g. an earlier Node build — used the ROOT name). See
# skills/brand-corpus/references/mcp-wiring.md.
CORPUS = (os.environ.get("BRAND_CORPUS_DIR") or os.environ.get("BRAND_CORPUS_ROOT") or "").strip()

TOOLS = [
    {"name": "list_brand_documents",
     "description": "List the brand corpus documents (markdown files), by layer. Use to see what exists before fetching.",
     "inputSchema": {"type": "object", "properties": {}}},
    {"name": "search_brand",
     "description": "Search the brand corpus for a term and return matching file:line snippets. Use to locate where a concept is defined.",
     "inputSchema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}},
    {"name": "fetch_brand_section",
     "description": "Return the full text of one corpus document. `path` is relative to the corpus root.",
     "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}},
    {"name": "outline_brand_document",
     "description": "Return the markdown heading outline of one corpus document. `path` is relative to the corpus root.",
     "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}},
    {"name": "get_brand_tokens",
     "description": "Return the brand's design tokens (tokens.json / design-tokens.json / tokens.css) if present in the corpus.",
     "inputSchema": {"type": "object", "properties": {}}},
]


def _no_corpus():
    return "brand-corpus is not configured. Set the plugin's `corpus_dir` userConfig to a brand corpus directory."


def _safe(path):
    """Resolve `path` under CORPUS, rejecting traversal/symlink escape. Returns abs path or None."""
    base = os.path.realpath(CORPUS)
    full = os.path.realpath(os.path.join(base, path))
    if full == base or full.startswith(base + os.sep):
        return full
    return None


def _md_files():
    """List corpus prose files. Skips any entry whose realpath escapes the corpus (symlink/traversal),
    so the enumeration surface never advertises a document the read guard would refuse (Simon's nit)."""
    base = os.path.realpath(CORPUS)
    out = []
    for root, _dirs, files in os.walk(base, followlinks=False):
        for f in sorted(files):
            if not f.lower().endswith((".md", ".mdx", ".txt")):
                continue
            rel = os.path.relpath(os.path.join(root, f), base)
            if _safe(rel) is None:
                continue
            out.append(rel)
    return sorted(out)


def call(name, args):
    """Return (text, is_error). is_error=True marks a tool-level failure (bad input / not found / not
    configured), distinct from valid content the model should read."""
    if not CORPUS or not os.path.isdir(CORPUS):
        return (_no_corpus(), True)
    if name == "list_brand_documents":
        files = _md_files()
        return ("Brand corpus documents:\n" + ("\n".join(f"  {p}" for p in files) if files else "  (none found)"), False)
    if name == "search_brand":
        q = (args.get("query") or "").strip()
        if not q:
            return ("search_brand: provide a `query`.", True)
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
    if name in ("fetch_brand_section", "outline_brand_document"):
        full = _safe(args.get("path", ""))
        if not full or not os.path.isfile(full):
            return (f"{name}: '{args.get('path','')}' not found in the corpus.", True)
        try:
            text = open(full, encoding="utf-8", errors="replace").read()
        except OSError as e:
            return (f"{name}: cannot read — {e}", True)
        if name == "fetch_brand_section":
            return (text[:20000] + ("\n…[truncated at 20000 chars]" if len(text) > 20000 else ""), False)
        heads = [ln.rstrip() for ln in text.splitlines() if ln.lstrip().startswith("#")]
        return ("Outline:\n" + ("\n".join(heads) if heads else "  (no headings)"), False)
    if name == "get_brand_tokens":
        for cand in ("tokens.json", "design-tokens.json", "tokens.css", "01-foundation/tokens.json"):
            full = _safe(cand)
            if full and os.path.isfile(full):
                raw = open(full, encoding="utf-8", errors="replace").read()
                body = raw[:20000] + ("\n…[truncated at 20000 chars]" if len(raw) > 20000 else "")
                return (f"# {cand}\n" + body, False)
        return ("get_brand_tokens: no tokens file found (looked for tokens.json / design-tokens.json / tokens.css).", False)
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
    prefix-sibling escape, plus a tools smoke. This server is copied verbatim into every stamped
    artifact (brand-stamp `_copy_mcp`), so this test travels with the hand-rolled guard and catches
    divergence across copies. No external corpus needed. Exit 0 = pass, 1 = fail."""
    import tempfile
    import shutil
    global CORPUS
    fails = []
    def check(cond, label):
        if not cond:
            fails.append(label)
    tmp = tempfile.mkdtemp(prefix="brand-corpus-selftest-")
    try:
        corpus = os.path.join(tmp, "corpus")
        outside = os.path.join(tmp, "outside")
        evil = os.path.join(tmp, "corpus-evil")  # prefix-sibling: shares the "corpus" prefix, must NOT pass
        os.makedirs(os.path.join(corpus, "01-foundation"))
        os.makedirs(outside)
        os.makedirs(evil)
        open(os.path.join(corpus, "01-foundation", "strategy.md"), "w", encoding="utf-8").write("# Strategy\nhello world\n")
        open(os.path.join(corpus, "tokens.json"), "w", encoding="utf-8").write('{"color":"red"}\n')
        open(os.path.join(outside, "secret.md"), "w", encoding="utf-8").write("# SECRET\n")
        open(os.path.join(evil, "secret.md"), "w", encoding="utf-8").write("# SECRET\n")
        link = os.path.join(corpus, "escape")
        try:
            os.symlink(outside, link)
            symlinks_ok = True
        except (OSError, NotImplementedError):
            symlinks_ok = False  # e.g. Windows without privilege — skip just the symlink assertion

        CORPUS = corpus
        # _safe: legitimate paths resolve…
        check(_safe("01-foundation/strategy.md") is not None, "valid corpus path was rejected")
        check(_safe("") is not None, "corpus root was rejected")
        # …and every escape is refused
        check(_safe("../outside/secret.md") is None, "parent traversal accepted")
        check(_safe("../../etc/passwd") is None, "deep traversal accepted")
        check(_safe("/etc/passwd") is None, "absolute path accepted")
        check(_safe("../corpus-evil/secret.md") is None, "prefix-sibling accepted (trailing os.sep guard missing)")
        if symlinks_ok:
            check(_safe("escape/secret.md") is None, "symlink escape accepted")
        # _md_files: enumeration includes the real doc, never advertises an escaped one
        listed = _md_files()
        check("01-foundation/strategy.md" in listed, "valid doc not enumerated")
        check(not any("secret" in p for p in listed), "escaped doc was enumerated")
        # call(): the guard holds at the tool layer, and the read tools work
        _, err = call("fetch_brand_section", {"path": "../outside/secret.md"})
        check(err, "fetch_brand_section served a path outside the corpus")
        txt, err = call("list_brand_documents", {})
        check(not err and "strategy.md" in txt, "list_brand_documents failed")
        txt, err = call("get_brand_tokens", {})
        check(not err and "color" in txt, "get_brand_tokens failed")
        txt, err = call("search_brand", {"query": "hello"})
        check(not err and "strategy.md" in txt, "search_brand failed")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    if fails:
        sys.stderr.write("brand-corpus-mcp selftest: FAIL\n")
        for f in fails:
            sys.stderr.write(f"  - {f}\n")
        return 1
    print("brand-corpus-mcp selftest: OK")
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        sys.exit(selftest())
    try:
        sys.exit(main())
    except (BrokenPipeError, KeyboardInterrupt):
        sys.exit(0)
