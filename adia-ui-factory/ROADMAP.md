# Roadmap

Phased build (via plugins-factory's `author` method):

- **[a] Skeleton** ✅ — structure + `plugin.json` + marketplace entry + a2ui MCP wiring + stubs (validates clean).
- **[b] Core skills** ✅ — `adia-ui-factory` (decision tree), `adia-ui-compose` (catalog literacy + component authoring + theming), `adia-ui-spa`, `adia-ui-ssr`, plus five vendored `references/` (component-model, authoring-components, spa-architecture, ssr-integration, a2ui-mcp-tools) and the five commands wired as thin routers.
- **[c] Tooling** ✅ — `adia-ui-llm` + `adia-ui-verify` skills (over `references/llm.md` + `references/verification.md`); `bin/adia-scaffold` (deterministic per-mode app scaffolder, with `selftest`); `bin/adia-lint` + `hooks/hooks.json` — the advisory authoring-lint hook (raw colors, `attachShadow`, `::slotted`, width-on-`:scope`, dead `--a-font`, top-level import in SSR, double route-owner, hardcoded overlay `open`); never blocks.
- **[d] Validate + red-team** ✅ — `validate_plugin.py --strict` + `reference-lint` + the scaffolder/lint selftests all green in CI; ran the full plugins-factory 9-critic council (no Criticals; Majors folded — see CHANGELOG). Result: APPROVED with follow-ups below.

## Open (deferred from the red-team)
- **Re-bake discipline** — the vendored methodology + the pinned MCP (`@0.7.8`) are a coupled snapshot; bump and re-verify both together when the framework version moves. No automated drift check yet (e.g. linting `mcp__a2ui__*` references against the live `get_component_map`).
- **a2ui MCP context cost (P6)** — pinned + documented + disable-path given, but Claude Code starts a plugin's MCP on enable and the tool set can't be scoped from `.mcp.json`; a methodology-only user still pays ~24 tool defs. Native per-server gating is an upstream/host limitation; revisit if it lands.
- **`adia-ui-llm` cohesion (Steve/Elon/Karpathy)** — the one skill that's a runtime-feature rather than structure. Considered: demote to a `compose` sub-reference, or split to a sibling `adia-ai-llm` plugin. Kept for now (LLM/chat is core to the kit's purpose); reconsider if the roster grows.
- **Command namespace (Steve, RD4)** — commands are `/adia-*` while skills are `adia-ui-*`; `/adia-verify` is the most collision-prone at marketplace scale. Consider aligning to `/adia-ui-*` before external adoption (breaking rename — cheap now, costly later).
- **SSR top-level-import lint blind spot (Karpathy)** — `adia-lint` flags the kit's top-level import only in files with a framework signal, to avoid false-positives on the legit SPA registration script; a bare `register.ts` module won't trip it. Documented as a known limitation; a smarter per-project signal could close it.
