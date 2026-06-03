---
name: adia-ui-compose
description: >
  Construct adia-ui UI (mode-independent) — audit the component catalog via the a2ui MCP, compose
  screens from light-DOM primitives + shells, author project-specific light-DOM components
  (render/style split, token-only CSS, size-agnostic), and apply theming/tokens. Shared across SPA and SSR.
---

# adia-ui-compose — construct the UI

How you build screens and components in adia-ui. **Mode-independent** — the markup, components, and tokens are identical whether the app is SPA or SSR; only the host wiring (which `adia-ui-spa` / `adia-ui-ssr` own) differs.

## The loop

1. **Discover before guessing.** Query the catalog — `mcp__a2ui__get_component_map`, then `lookup_component`/`get_traits` for the exact props, slots, events. Names and counts are version-specific; the MCP is authoritative.
2. **Compose from primitives.** Build the screen from catalog elements and layout primitives (`<col-ui>`/`<row-ui>`/`<grid-ui>`/`<stack-ui>`). Catalog-first: never a raw `<div>` for layout, never a raw `<button>`/`<input>` where a `*-ui` exists.
3. **Author only what's missing.** When no primitive composes to the need, author a light-DOM component — the discipline is in `${CLAUDE_PLUGIN_ROOT}/references/authoring-components.md` (two-block `@scope`, side-effect registration, size-agnostic, lifecycle symmetry).
4. **Theme with tokens.** Style only through `--a-*` tokens; scheme via `<toggle-scheme-ui>` + `light-dark()`; density via `--a-density`. No raw colors, no raw px ≥ 3.
5. **Validate.** On anything generated, `mcp__a2ui__validate_schema` + `check_anti_patterns`; then apply the authoring invariants.

## Two ways to compose

- **Hand-compose** — for small, well-understood surfaces and edits. Faster than round-tripping a generator.
- **MCP-assisted** — for non-trivial surfaces: `classify_intent` → `search_patterns`/`assemble_context` → `generate_ui` (host LLM in stdio, no key) → **always** validate → refine by hand. See `${CLAUDE_PLUGIN_ROOT}/references/a2ui-mcp-tools.md`.

## Non-negotiables

- **Catalog-first** — primitive before custom; custom before raw HTML.
- **Token-only styling** — `var(--a-*)`; never a literal color or magic px.
- **Light DOM** — never `attachShadow`; never `::slotted()`; read children via `logicalChildren`.
- **Size-agnostic** — the consumer owns width/height, not the component tag.
- **Two-block `@scope`** — zero-specificity token block + base block, scoped to the tag.

## References

- `${CLAUDE_PLUGIN_ROOT}/references/component-model.md` — catalog vocabulary, tokens, signals, traits.
- `${CLAUDE_PLUGIN_ROOT}/references/authoring-components.md` — authoring a component + the anti-pattern table.
- `${CLAUDE_PLUGIN_ROOT}/references/a2ui-mcp-tools.md` — discovery / generation / validation tools.
