# Changelog

## Unreleased — 0.1.0 (in progress)

- **Phase (b) — core skills + methodology.** Authored the four core skills — `adia-ui-factory`
  (orient & route: the SPA/SSR fork + task routing), `adia-ui-compose` (catalog-driven UI construction
  + light-DOM component authoring + theming), `adia-ui-spa`, and `adia-ui-ssr` — and vendored the
  methodology into five `references/` files (`component-model`, `authoring-components`,
  `spa-architecture`, `ssr-integration`, `a2ui-mcp-tools`), synthesized as a verified surface from the
  framework's own authoring skills with SSR claims labeled documented-vs-inferred. Wired the five
  commands from stubs into thin mode-aware routers. `adia-ui-llm` + `adia-ui-verify` remain stubs (phase c).
- **Phase (a) — skeleton.** Scaffolded the plugin structure, `plugin.json`, the marketplace entry, and the
  **a2ui MCP wiring** (`.mcp.json` → `npx @adia-ai/a2ui-mcp`). Six skills and five commands stubbed with real
  frontmatter (routing surface live); content authored in later phases. Authored via plugins-factory.
