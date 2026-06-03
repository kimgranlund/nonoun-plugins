# Wiring the brand-corpus MCP

The `brand-corpus` skill defines the corpus _structure_; this reference defines how to stand up the MCP that reads it, and how to choose its implementation. The bundled reference server is `bin/brand-corpus-mcp.py`.

## The contract is the format — not the language

An MCP server is a **wire contract**, not a source-file format: JSON-RPC 2.0 over newline-delimited stdio (`initialize` / `tools/list` / `tools/call` / `ping`), exposing exactly these read-only, task-level tools over one corpus directory:

| Tool | Returns |
| --- | --- |
| `list_brand_documents` | the corpus's markdown documents, by layer |
| `search_brand` | `file:line` snippets for a query |
| `fetch_brand_section` | the full text of one document (path relative to the corpus root) |
| `outline_brand_document` | a document's markdown heading outline |
| `get_brand_tokens` | the brand's design tokens (`tokens.json` / `design-tokens.json` / `tokens.css`) |

It is **read-only and path-guarded** (no tool writes/deletes/executes; every path resolves under the corpus root, rejecting `..`/symlink escape) and **scoped to one directory** via an env var — a curated perimeter, not a 1:1 filesystem wrapper. Any language that reads stdin, writes stdout, and parses JSON satisfies this identically; the host cannot tell a Python server from a Node one. **Standardize the contract; pick the language by how you ship it.**

## Canonical corpus-root env var

- **`BRAND_CORPUS_DIR`** — canonical. Set to the corpus root (a folder-convention dir, e.g. `…/<brand>/brand`).
- **`BRAND_CORPUS_ROOT`** — accepted as a back-compat alias (hand-wired Node builds have used it). Emit `BRAND_CORPUS_DIR` in anything you generate.

## Choosing the implementation language (default + two gates)

Default to the **bundled Python reference**; branch only when a signal appears.

| Situation | Language | Why |
| --- | --- | --- |
| **Bundled in a stamped plugin** (default) | **Python stdlib** (`bin/brand-corpus-mcp.py`) | zero deps, **no build step**, runs anywhere `python3` is — lowest-friction to drop into a plugin |
| **Published standalone for easy install** | **TS/Node, via npm + `npx`** | `npx -y …-mcp` auto-fetches with no clone/build for the user (Python analog: `uvx`) |
| **Integrates with an existing app codebase** | **match the app** | share its data layer, types, and build (why a brand with a Node app ships a Node MCP) |

The stamp flow assumes Python and asks only two yes/no questions — "does this brand have an app the MCP should plug into?" and "publish it standalone?" — not an open language question each time. Same discipline as component fit: the _primitive_ (it's an MCP) and the _contract_ (these five tools) are fixed; language is the last, cheapest decision.

## The three registration contexts

**1 — Bundled in a plugin** (`.mcp.json` at the plugin root), corpus from `userConfig`:

```json
{ "mcpServers": { "brand-corpus": {
  "command": "python3",
  "args": ["${CLAUDE_PLUGIN_ROOT}/bin/brand-corpus-mcp.py"],
  "env": { "BRAND_CORPUS_DIR": "${user_config.corpus_dir}" }
} } }
```

**2 — Standalone, user-scoped** (available in all projects) via the CLI:

```bash
claude mcp add brand-corpus -s user -e BRAND_CORPUS_DIR="/path/to/<brand>/brand" \
  -- python3 /path/to/brand-corpus-mcp.py
# a Node build instead:  -- node /path/to/brand-corpus-mcp/dist/server.js
```

**3 — Published standalone** (no local clone), once packaged:

```bash
claude mcp add brand-corpus -s user -e BRAND_CORPUS_DIR="/path/to/<brand>/brand" -- npx -y @scope/brand-corpus-mcp
```

## Bundle vs share (a P4 call when stamping)

Because only the corpus root differs between brands, a stamped brand needn't ship MCP _code_: it can **co-locate** the ~160-line reference server (self-contained — the default), or point at a **shared** brand-corpus MCP declared as a `dependency`. Co-locate unless you're managing a fleet of brands.
