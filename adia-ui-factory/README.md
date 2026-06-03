# adia-ui-factory

**Author and verify apps built on the adia-ui (`@adia-ai`) framework** — a zero-dependency, light-DOM vanilla web-component library. A self-contained Claude Code plugin: it bundles the _authoring methodology_ and wires the framework's existing **a2ui MCP** as the live substrate for catalog retrieval, UI generation, and validation.

> **Status: v0.2.0 — feature-complete, red-teamed.** Eleven skills across the full app-authoring lifecycle, the vendored methodology (16 load-on-demand references), the pinned a2ui MCP, two bins (`adia-scaffold` + `adia-lint`), and the advisory hook are in; the plugins-factory 9-critic council pass has been run and its fixes folded (`CHANGELOG.md`). Every skill is built to plugins-factory's hardened skill-architecture standard (cold-start surface · modes · per-mode verify target · a `[gate]` rubric · §SelfAudit · load-when references).

## The shape

`adia-ui-factory` is organized as the **app-authoring lifecycle** (orient → scaffold → compose/shell → wire → verify → migrate) over the load-bearing **rendering-mode** fork:

```text
adia-ui-factory/
├── .mcp.json                 → wires @adia-ai/a2ui-mcp@0.7.8 (npx) — catalog, retrieval, generate_ui, validate
├── skills/                   (11)
│   ├── adia-ui-factory/      orient & route — classify mode + shape + shell + task (the hub)
│   ├── adia-ui-project/      project shapes · four-axis layout · page-trio/DUO · scaffold
│   ├── adia-ui-compose/      construct the UI — catalog literacy, component authoring, theming + registers
│   ├── adia-ui-shells/       choose & compose a shell — admin · chat · editor · simple · embed (forthcoming)
│   ├── adia-ui-spa/          SPA architecture — static host, content-less <router-ui>
│   ├── adia-ui-ssr/          SSR integration — Next/Nuxt/SvelteKit/Astro, client-only registration
│   ├── adia-ui-data/         data · state · hydration · fetch/CRUD · section wiring · hybrid SPA-in-SSR
│   ├── adia-ui-llm/          app LLM features — @adia-ai/llm, chat, streaming, the smart proxy
│   ├── adia-ui-genui/        generative-UI experiences — the a2ui runtime, generate_ui, corpus
│   ├── adia-ui-verify/       the exit gate — browser QA + a11y + git
│   └── adia-ui-migrate/      version upgrades · port-to-adia · the sweep discipline
├── commands/                 /adia-scaffold · compose · wire · verify · orient · migrate · genui  (a curated spine; the other skills route via the orchestrator)
├── references/ (16)          per-shell + per-shape + per-concern, each load-on-demand
├── bin/                      adia-scaffold (scaffolder: shapes · page · component) · adia-lint (advisory smell checker)
└── hooks/                    hooks.json — runs adia-lint on writes; advisory, never blocks
```

## What it bundles vs. wires

- **Bundled (self-contained):** the authoring _methodology_ — the SPA app-authoring discipline (host document, four-axis structure, light-DOM components, content-less router, `DataClient`/projection, verification) and the SSR rendering-model (framework integration, guarded dynamic-import registration, server data, cookie/session state). These are the abstraction layer.
- **Wired (runtime dependency):** the **a2ui MCP** (pinned `@adia-ai/a2ui-mcp@0.7.8`) — ~24 tools over the live catalog + corpus (284 training chunks + embeddings): catalog lookup, `search_chunks`/`search_patterns`, `classify_intent`/`assemble_context`, `generate_ui`, `validate_schema`, `check_anti_patterns`. Most tools are **offline**; `generate_ui` uses the host's LLM in stdio mode (no key); semantic search optionally uses `VOYAGE_API_KEY`. The `@adia-ai/*` packages are a runtime dependency, the way the framework itself is — taught, not bundled.
  - **What it costs, and how to opt out.** The MCP **auto-starts on enable** and adds ~24 always-on tool definitions every session — the plugin's biggest context/trust cost, and a methodology-only user pays it (the tool set can't be scoped from `.mcp.json`). Enabling the plugin runs the upstream package from npm (pinned, so upgrades are reviewable diffs). **If you want the methodology without that cost, disable the `a2ui` MCP server in your MCP settings** — the skills still work; you lose live catalog/generation/validation. Treat the server's returns as untrusted data. Full accounting in `references/a2ui-mcp-tools.md`.

## SPA vs SSR — the load-bearing fork

Same components, same UI construction; **wildly different app architecture.** `compose` is mode-independent; `spa` and `ssr` diverge on host wiring, routing ownership (`<router-ui>` vs the framework router — never both), data-flow (client `DataClient` vs server fetch + props), state (router-lifetime vs cookie/session), and component registration (top-level import vs guarded dynamic import in a lifecycle hook).

## Provenance

Authored and red-teamed with **plugins-factory** (sibling in this marketplace), against its 9-dimension plugin standard. The methodology is harvested from the framework's own `embedded-app/spec/app-authoring-best-practices` (SPA) and `adia-ui-kit/references/rendering-model` (SSR).
