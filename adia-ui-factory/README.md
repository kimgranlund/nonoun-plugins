# adia-ui-factory

**Author and verify apps built on the adia-ui (`@adia-ai`) framework** — a zero-dependency, light-DOM vanilla web-component library. A self-contained Claude Code plugin: it bundles the *authoring methodology* and wires the framework's existing **a2ui MCP** as the live substrate for catalog retrieval, UI generation, and validation.

> **Status: v0.1.0, feature-complete pending red-team.** Phases (a)–(c) are in — the six skills, the vendored methodology, the wired a2ui MCP, the deterministic scaffolder (`bin/adia-scaffold`), and the advisory authoring-lint hook (`bin/adia-lint`). Phase (d) is the adversarial red-team (see `ROADMAP.md`).

## The shape

`adia-ui-factory` is organized around one architectural axis — the **rendering mode** — over a shared UI-construction core:

```
adia-ui-factory/
├── .mcp.json                 → wires @adia-ai/a2ui-mcp (npx) — catalog, retrieval, generate_ui, validate
├── skills/
│   ├── adia-ui-factory/      orchestrator — classify mode (SPA/SSR) + task, route   [shared]
│   ├── adia-ui-compose/      construct the UI — catalog literacy, component authoring, theming   [shared]
│   ├── adia-ui-spa/          SPA architecture — static host, <router-ui>, DataClient/projection
│   ├── adia-ui-ssr/          SSR architecture — Next/Nuxt/SvelteKit/Astro, guarded registration, server data
│   ├── adia-ui-llm/          app LLM features — @adia-ai/llm, chat, streaming   [shared]
│   └── adia-ui-verify/       browser-QA gate + a11y + git discipline   [shared]
├── commands/                 /adia-scaffold · compose · wire · verify · orient
├── references/               vendored methodology (component-model · authoring · spa · ssr · a2ui-mcp · llm · verification)
├── bin/                      adia-scaffold (deterministic app scaffolder) · adia-lint (advisory smell checker)
└── hooks/                    hooks.json — runs adia-lint on component/page writes (advisory, never blocks)
```

## What it bundles vs. wires

- **Bundled (self-contained):** the authoring *methodology* — the SPA app-authoring discipline (host document, four-axis structure, light-DOM components, content-less router, `DataClient`/projection, verification) and the SSR rendering-model (framework integration, guarded dynamic-import registration, server data, cookie/session state). These are the abstraction layer.
- **Wired (runtime dependency):** the **a2ui MCP** (`@adia-ai/a2ui-mcp`) — 24 tools over the live catalog + corpus (284 training chunks + embeddings): catalog lookup, `search_chunks`/`search_patterns`, `classify_intent`/`assemble_context`, `generate_ui`, `validate_schema`, `check_anti_patterns`. Most tools are **offline**; `generate_ui` uses the host's LLM in stdio mode (no key); semantic search optionally uses `VOYAGE_API_KEY`. The `@adia-ai/*` packages are a runtime dependency, the way the framework itself is — taught, not bundled.

## SPA vs SSR — the load-bearing fork

Same components, same UI construction; **wildly different app architecture.** `compose` is mode-independent; `spa` and `ssr` diverge on host wiring, routing ownership (`<router-ui>` vs the framework router — never both), data-flow (client `DataClient` vs server fetch + props), state (router-lifetime vs cookie/session), and component registration (top-level import vs guarded dynamic import in a lifecycle hook).

## Provenance

Authored and red-teamed with **plugins-factory** (sibling in this marketplace), against its 9-dimension plugin standard. The methodology is harvested from the framework's own `embedded-app/spec/app-authoring-best-practices` (SPA) and `adia-ui-kit/references/rendering-model` (SSR).
