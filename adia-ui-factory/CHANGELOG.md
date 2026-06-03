# Changelog

## Unreleased — 0.1.0 (in progress)

- **Phase (c) — tooling + the last two skills.** Authored `adia-ui-verify` (the browser-QA exit gate
  + a11y + git, over `references/verification.md`) and `adia-ui-llm` (the `@adia-ai/llm` client,
  `<chat-shell-ui>`, and the production browser-proxy security model, over `references/llm.md`).
  Added `bin/adia-scaffold` — a minimal, lint-clean app scaffolder (SPA: four-axis layout + host
  document + self-booting surface; SSR: a client-boundary provider + integration checklist for
  next/nuxt/sveltekit/astro) with a `selftest`. Added `bin/adia-lint` + `hooks/hooks.json` — an
  advisory PostToolUse authoring-smell checker (shadow DOM, raw colors, dead `--a-font`, `::slotted`,
  width-on-`:scope`, SSR top-level import, double route-owner, hardcoded overlay `open`) that
  **never blocks** (always exits 0 in hook mode). CI runs the scaffolder selftest.
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
