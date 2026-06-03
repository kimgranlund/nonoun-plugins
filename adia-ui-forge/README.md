# adia-ui-forge

**Author and maintain the adia-ui (`@adia-ai`) framework itself.** This is the producer/maintainer counterpart to [`adia-ui-factory`](../adia-ui-factory) — where the factory builds _apps on_ the framework, the forge builds and ships _the framework_: its primitives, composite shells, the A2UI / gen-ui generation engine and training corpus, the LLM client, quality sweeps, and releases — across every `@adia-ai` package.

> **Status: 0.1.0 — built and red-teamed.** All 7 skills, 7 commands, the advisory authoring-lint hook, and shared infra are in place and pass the harness gates (`validate_plugin.py --strict`, `reference-lint.py`, `forge-lint selftest`, markdownlint). The build record is in [ROADMAP.md](ROADMAP.md); the `plugins-factory` council critique is recorded under `reviews/`.

## Who it's for

Anyone working **on** the adia-ui framework — in the `@adia-ai` monorepo or a fork. It assumes the monorepo's package conventions (`packages/web-components`, `packages/web-modules`, `packages/a2ui`, `packages/llm`); it is not a generic "build any component library" toolkit. App authors who _consume_ the framework want `adia-ui-factory` instead.

## Requirements & what it ships

- **Two runtimes.** The hook + `forge-lint` are Python (3.8+); every skill script and `bin/lib/*` are Node ESM. Both must be on PATH — the skills' `§SelfAudit` and eval scripts need Node; the hook needs Python.
- **The release skill bundles real capability.** `adia-ui-release` ships scripts that shell `git`, `npm publish`, `gh`, and `curl` (the deploy verify). They are operator-run (never hook-wired), go through a dry-run gate, and **fail loudly unless run inside an `@adia-ai`-style monorepo checkout** (a `packages/web-components` guard). The deploy host and npm scope are overridable (`--host`/`$ADIA_DEPLOY_HOST`, `--scope`/`$ADIA_NPM_SCOPE`).
- **Skill versions are lineage, not the plugin version.** Per-skill `version` fields (e.g. `adia-ui-authoring` 1.9.2) are carried from the monorepo source skills; the plugin's own version is canonical for the bundle.
- **Gates run via the sibling harness.** `validate_plugin.py` / `reference-lint.py` live in `plugins-factory` and run in CI against this plugin; `forge-lint selftest` is self-contained in the bundle.

## The package surface it covers

| Package / system | What the forge does with it |
| --- | --- |
| `@adia-ai/web-components` | author & evolve light-DOM primitives (props, `@scope` tokens, lifecycle, traits) |
| `@adia-ai/web-modules` | author composite shells & clusters (admin / chat / editor / embed) |
| `@adia-ai/a2ui` (6-pkg cluster: compose · corpus · retrieval · runtime · validator · mcp) | evolve the A2UI / gen-ui generation engine, chunk corpus, and MCP server |
| gen-ui training data (`gen-ui-kit/data`) | author and curate the generation corpus / seed data |
| `@adia-ai/llm` | maintain the provider-agnostic client (anthropic / openai / gemini adapters, SSE, models) |
| all packages | gen-ui output quality review, cross-surface dogfood QA, and lockstep release engineering |

## Skills (7)

| Skill | Job |
| --- | --- |
| `adia-ui-forge` | cold-start orchestrator — classify the package/concern and route to the owning skill |
| `adia-ui-authoring` | author primitives (`web-components`) + composite shells (`web-modules`), tokens, traits |
| `adia-ui-a2ui` | the A2UI / gen-ui generation engine — compose strategies, chunk corpus, retrieval, validator, runtime, MCP server |
| `adia-ui-llm` | the `@adia-ai/llm` client — provider adapters, SSE streaming, model registry, the bridge |
| `adia-ui-gen-review` | closed-loop quality scoring of generated gen-ui output, driving corpus fixes |
| `adia-ui-dogfood` | static + visual QA sweep across components, apps, playgrounds, and catalog |
| `adia-ui-release` | release-engineering discipline (gates, changelog/notes authoring) + migration-guide authoring |

## Relationship to adia-ui-factory

Producer ↔ consumer, fully independent (zero cross-plugin dependencies):

|  | `adia-ui-forge` (maintainer) | `adia-ui-factory` (consumer) |
| --- | --- | --- |
| **authoring** | builds the primitives & shells | composes screens from them |
| **a2ui / gen-ui** | builds the engine + corpus | renders generated UI via the published MCP |
| **llm** | builds the `@adia-ai/llm` package | wires it into an app |
| **migration** | authors the MIGRATION GUIDE | applies it to consumer code |

## Provenance

Carved from the `@adia-ai` monorepo's `.agents/` maintainer system, then authored and red-teamed with [`plugins-factory`](../plugins-factory) against its 9-dimension architecture standard.
