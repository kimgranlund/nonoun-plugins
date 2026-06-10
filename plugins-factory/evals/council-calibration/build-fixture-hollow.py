#!/usr/bin/env python3
"""build-fixture-hollow.py <dir> — write the SECOND council-calibration fixture: `docs-studio`.

Where `mega-helper` (build-fixture.py) fails by EXCESS — a kitchen sink (P3) + a 1:1 API-wrapper MCP
(P2) — this fixture fails by the opposite, the panel's own former blind spots, isolated so the OLD
panel would likely pass it and the NEW probes (PF5/CF5, AP-P6/AP-P7) must catch it:

  - It is a COHERENT single job (documentation quality) — no kitchen sink, no undeclared sibling — so
    P1/P3 pass on the surface and do not mask the planted defects.
  - Its bundled MCP is TASK-SHAPED (3 curated intent-level tools, not 1:1 endpoints) — so P2/AP-P4
    (the wrapper anti-pattern) does NOT fire, isolating the liveness defect.

Planted JUDGMENT defects (both pass every DETERMINISTIC gate — valid kebab manifest, no `../`, no
slug collision, parsable .mcp.json, every reference resolves, version↔CHANGELOG in sync):

  - **H — hollow components (AP-P6 / PF5).** Every skill and the command has a body THINNER than its
    own description: rich routing blurbs promising "a comprehensive catalog … with rationale and a
    worked before/after fix" / "auto-fix every violation", delivering one sentence and no references/.
    Pure routing surface, zero capability the base model lacked. "Lean by hollowness" is not "lean by
    design."
  - **L — dead-but-wired MCP (AP-P7 / CF5).** `.mcp.json` wires `bin/docs-mcp.py`, which defines a
    well-shaped TOOLS list and exits — no JSON-RPC loop, no stdin read. Green to every static
    validator, 100% non-functional, charging failed-startup cost every session. Detectable cold
    (the missing protocol loop is readable); PROVING it dead is a CI smoke test, not a cold review.

ST5 injection is NOT planted here (this fixture isolates PF5/CF5); the mega-helper fixture carries the
ST5 surface. Built on demand (never committed as a plugin) so it never trips the catalog's own gates.
Stdlib only.
"""
import json
import os
import sys


def _w(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def build(d):
    # Coherent single job — deliberately NOT a kitchen sink (isolates the hollowness finding from P3).
    _w(os.path.join(d, ".claude-plugin", "plugin.json"), json.dumps({
        "name": "docs-studio",
        "version": "1.0.0",
        "description": "Keep a project's documentation correct, consistent, and well-styled.",
    }, indent=2))

    # H — hollow skills: the description promises depth; the body is one sentence; no references/ exist.
    _w(os.path.join(d, "skills", "doc-rules", "SKILL.md"),
       "---\nname: doc-rules\n"
       "description: A comprehensive catalog of documentation lint rules — heading hierarchy, link "
       "integrity, code-fence language tags, and terminology consistency — each rule with its "
       "rationale and a worked before/after fix.\n---\n"
       "Check the docs for common problems.\n")
    _w(os.path.join(d, "skills", "style-canon", "SKILL.md"),
       "---\nname: style-canon\n"
       "description: The complete house style guide — voice, tense, capitalization, and list and "
       "table conventions — with a before/after rewrite for every rule.\n---\n"
       "Apply the house style to the writing.\n")
    # H — hollow command: names a deterministic auto-fix action, ships no script/pipeline to do it.
    _w(os.path.join(d, "commands", "doc-fix.md"),
       "---\ndescription: Auto-fix every documentation lint violation in the repository in one pass.\n---\n"
       "Fix the documentation issues.\n")

    # L — a TASK-SHAPED MCP (3 curated intent-level tools, not a wrapper) whose server is dead-but-wired.
    _w(os.path.join(d, ".mcp.json"), json.dumps({
        "mcpServers": {"docs": {"command": "python3", "args": ["${CLAUDE_PLUGIN_ROOT}/bin/docs-mcp.py"]}}
    }, indent=2))
    tools = [
        {"name": "check_links", "description": "Verify every link in a document resolves.",
         "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}},
        {"name": "lint_doc", "description": "Run the doc-rules catalog against a file and return the violations.",
         "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}},
        {"name": "apply_style", "description": "Rewrite a document to conform to the house style canon.",
         "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}},
    ]
    # The server is DEAD-BUT-WIRED: it defines a well-shaped TOOLS list and exits. No stdin read, no
    # JSON-RPC dispatch, no __main__ — it can never answer `initialize` or `tools/list`.
    _w(os.path.join(d, "bin", "docs-mcp.py"),
       '#!/usr/bin/env python3\n"""Documentation MCP — three task-level tools for the docs-studio workflow."""\n'
       "import json, sys\n\n"
       "TOOLS = " + json.dumps(tools, indent=2) + "\n\n"
       "# Tool shapes are correct and task-level; there is no server loop to serve them.\n")

    _w(os.path.join(d, "CHANGELOG.md"), "# Changelog\n\n## 1.0.0 — 2026-01-01\n\n- initial\n")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: build-fixture-hollow.py <target-dir>", file=sys.stderr)
        sys.exit(2)
    build(sys.argv[1])
    print(f"built council-calibration fixture `docs-studio` at {sys.argv[1]} "
          f"(coherent single job; hollow components; a task-shaped but dead-but-wired MCP)")
