# The a2ui MCP — the live substrate

This plugin wires `@adia-ai/a2ui-mcp` (declared in `.mcp.json`, run via `npx`). It is the **live** catalog, corpus, generator, and validator — so the methodology references teach how to *think*, and the MCP answers *what exactly* (current tags, props, patterns) and *does* the generation/validation. Tools surface as `mcp__a2ui__<tool>`.

## What runs where

- **Offline (no key):** discovery, retrieval, validation, planning, feedback — the bulk of authoring. These work the moment the server starts.
- **Host LLM via sampling (no key):** in **stdio** mode (how this plugin wires it), `generate_ui` and other generative tools use *your* Claude session's model through MCP sampling — no API key needed.
- **Optional key:** `VOYAGE_API_KEY` (or OpenAI) upgrades `search_chunks` to semantic search; without it, keyword search is the offline fallback. HTTP-transport deployments need their own LLM key.

## Tools by job

**Discover the catalog** — start here instead of guessing tag names:
- `get_component_map` — the full current catalog (the live count + names).
- `lookup_component` — one component's props, slots, events, examples.
- `get_traits` — the behavior catalog (`pressable`, `draggable`, …).
- `get_wiring_catalog` — how components wire together.
- `lookup_chunk` — a specific corpus chunk by id.

**Retrieve patterns & knowledge:**
- `search_chunks` — semantic/keyword search over the 280+ corpus chunks.
- `search_patterns` / `get_fragment` / `get_composition` — reusable composition patterns and fragments.
- `get_chunk` / `get_graph` / `resolve_composition` / `zettel_stats` — chunk graph navigation.

**Classify & assemble (the generation pre-step):**
- `classify_intent` — what kind of UI does this request want?
- `assemble_context` — build the retrieval context for a generation.

**Generate** (host LLM in stdio):
- `generate_ui` — produce A2UI/markup for a described surface.
- `plan_app_state` — plan an app's state shape.

**Validate** (offline):
- `validate_schema` — check generated A2UI against the schema.
- `check_anti_patterns` — the structural smells (overlaps [authoring-components.md](authoring-components.md)'s table).
- `convert_html` — convert/normalize HTML.

**Feedback & authoring loop:**
- `submit_feedback` · `get_quality_metrics` · `get_training_gaps` · `import_pattern`.

## When to reach for it vs. hand-author

- **Always** use `get_component_map` / `lookup_component` before composing — names and props are version-specific; the MCP is authoritative, the references are not.
- Use `search_patterns` / `assemble_context` → `generate_ui` to draft a non-trivial surface, then **always** run `validate_schema` + `check_anti_patterns`, then apply the hand-authoring discipline.
- Hand-author directly for small, well-understood edits — round-tripping through generation isn't worth it.

## A real cost to weigh

Wiring the MCP means **~24 tool definitions load into context whenever the plugin is enabled**, and the server runs on enable. That's the right trade for an authoring plugin — but it's this plugin's biggest context (P6) and trust (P9) surface, and a consumer who only wants the methodology pays it. Tracked for the red-team (`ROADMAP.md`): options include gating the server behind a flag or documenting an easy disable. Note it; don't pretend it's free.
