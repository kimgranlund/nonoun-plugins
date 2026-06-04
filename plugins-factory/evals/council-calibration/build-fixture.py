#!/usr/bin/env python3
"""build-fixture.py <dir> — write a deliberately-flawed fixture plugin for council calibration.

The fixture passes every DETERMINISTIC gate (valid kebab manifest, no `../`, no command↔skill slug
collision, parsable .mcp.json) — so `validate_plugin.py`, `reference-lint.py`, and
`check-manifest-sync.py` all PASS it. Its defects are pure architecture JUDGMENT, the kind only the
critic council can catch:

  - **P3 kitchen-sink** — four unrelated domains bundled in one plugin (PDF tooling, brand strategy,
    recipe search, deployment).
  - **P2 API-wrapper MCP** — a bundled MCP that is a 1:1 wrapper over REST endpoints (one tool per
    verb×resource), the field's most-cited MCP anti-pattern.

Used by the council-calibration eval — see README.md. Builds on demand (not committed as a plugin)
so it never trips the catalog's own gates. Stdlib only.
"""
import json
import os
import sys


def _w(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def build(d):
    _w(os.path.join(d, ".claude-plugin", "plugin.json"), json.dumps({
        "name": "mega-helper",
        "version": "1.0.0",
        "description": "A handy toolbox: PDF tools, brand strategy, deployment, and recipe search — all in one place.",
    }, indent=2))

    # P3 — four unrelated domains in one plugin
    _w(os.path.join(d, "skills", "pdf-tools", "SKILL.md"),
       "---\nname: pdf-tools\ndescription: Extract text and tables from PDF files.\n---\nSplit, merge, and extract from PDFs.\n")
    _w(os.path.join(d, "skills", "brand-strategy", "SKILL.md"),
       "---\nname: brand-strategy\ndescription: Develop brand positioning, voice, and identity.\n---\nBuild a brand foundation and a voice.\n")
    _w(os.path.join(d, "skills", "recipe-finder", "SKILL.md"),
       "---\nname: recipe-finder\ndescription: Find recipes by the ingredients you have.\n---\nSearch recipes by what is in your fridge.\n")
    _w(os.path.join(d, "commands", "deploy.md"),
       "---\ndescription: Deploy the application to production.\n---\nRun the deploy pipeline.\n")

    # P2 — a 1:1 REST-endpoint wrapper MCP (one tool per verb × resource)
    _w(os.path.join(d, ".mcp.json"), json.dumps({
        "mcpServers": {"api": {"command": "python3", "args": ["${CLAUDE_PLUGIN_ROOT}/bin/api-mcp.py"]}}
    }, indent=2))
    tools = []
    for res in ("user", "order", "product", "invoice", "payment"):
        for verb in ("get", "list", "create", "update", "delete"):
            tools.append({"name": f"{verb}_{res}",
                          "description": f"{verb.upper()} /{res}s — direct passthrough to the REST endpoint.",
                          "inputSchema": {"type": "object", "properties": {"id": {"type": "string"}, "body": {"type": "object"}}}})
    _w(os.path.join(d, "bin", "api-mcp.py"),
       '#!/usr/bin/env python3\n"""A thin MCP that exposes one tool per REST endpoint — a direct 1:1 passthrough."""\n'
       "import json, sys\n\n"
       "TOOLS = " + json.dumps(tools, indent=2) + "\n\n"
       "# Each tool maps verbatim to GET/POST/PUT/DELETE /<resource>; no task-level shaping.\n")

    _w(os.path.join(d, "CHANGELOG.md"), "# Changelog\n\n## 1.0.0 — 2026-01-01\n\n- initial\n")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: build-fixture.py <target-dir>", file=sys.stderr)
        sys.exit(2)
    build(sys.argv[1])
    print(f"built council-calibration fixture `mega-helper` at {sys.argv[1]} "
          f"(4 unrelated domains; a 25-tool 1:1 API-wrapper MCP)")
