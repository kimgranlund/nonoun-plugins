# Reference: A2UI pipeline overview

**Source:** Absorbed from the former `a2ui-pipeline` skill (Phase 3 rollup). **Used by:** mode 2 of `adia-ui-a2ui` (modify pipeline internals). **Companion:** `chunk-authoring.md`, `strategy-engines.md`, `mcp-tool-reference.md`.

---

## Project Location

Project root (where `package.json` and `vite.config.js` live). Detect via `git rev-parse --show-toplevel` or look for `packages/a2ui/compose/`, `packages/a2ui/mcp/`, and `packages/web-components/`.

## First: Read the specs

The canonical A2UI specs live under `docs/specs/`:

- `a2ui-v0.9-catalog-guide.md` — catalog format + the A2UI v0.9 protocol.
- `a2ui-editor.md` — live authoring tool spec (editor UX, doc model).
- `genui-multiturn-architecture.md` — multi-turn refinement (state cache, refiner two-pass synthesis, issue-reporter, op format).
- `genui-chunk-marker.md` + `genui-chunk-inventory-001.md` — chunk corpus (data-chunk authoring attributes, harvester, retrieval).
- `package-architecture.md` — how `gen-ui`, `gen-ui-mcp`, `gen-ui-training`, `a2ui/utils`, and `web-components` relate.

The chunk pipeline section lives in `docs/conventions/gen-ui-pipeline.md` — read that for the authoring-time attribute conventions, harvester wiring, and embedding-index lifecycle.

For primitive/shell authoring (the artifacts chunks ultimately harvest from), see the sibling skill **adia-ui-authoring** (shells, layout, forms, data, agent, traits, wiring + the four-axis contract guard rails).

## Key Files

### Engine — orchestrators

| File | Role |
| --- | --- |
| `packages/a2ui/compose/core/generator.js` | Top-level orchestrator — instant / thinking / stream modes; routes to fragment-graph or chunk-synthesis path depending on engine config |
| `packages/a2ui/compose/strategies/registry.js` | In-process engine registry — `registerEngine(name, factory)`. Reserved names: `monolithic`, `zettel`, `mcp`, `monolithic-*` |
| `packages/a2ui/compose/strategies/zettel/generate.js` | Zettel engine entry — composes via fragment graph + (optionally) chunk synthesis |
| `packages/a2ui/compose/strategies/zettel/generator-adapter.js` | Glue between the engine API and the LLM adapter |

### Engine — fragment-graph path (the original Zettel pipeline)

| File | Role |
| --- | --- |
| `packages/a2ui/compose/strategies/zettel/fragment-library.js` | Fragment catalog (≥29.9% reuse ratio invariant) — atomic units harvested by extract.js |
| `packages/a2ui/compose/strategies/zettel/synthesizer.js` | Mix-and-match LLM composer — picks a pattern + binds fragments to its slots; pre-search filter ~30 candidates |
| `packages/a2ui/compose/strategies/zettel/composer.js` | Materializer — substitutes fragment bindings into pattern HTML |

### Engine — chunk-corpus path (newer mix-and-match)

| File | Role |
| --- | --- |
| `packages/a2ui/corpus/scripts/chunk-library.js` | Chunk catalog API — `getChunk()`, `searchChunks()` (keyword + cosine when embeddings available), `searchChunksAsync()`, `listChunksByKind()`, `getAllChunks()`. Reads `packages/a2ui/corpus/chunks/` + `_index.json` |
| `packages/a2ui/compose/strategies/zettel/chunk-synthesizer.js` | Two-tier composer — (1) retrieval-first (return matched chunk's HTML when score ≥ 8); (2) LLM synthesis fallback that picks `{page, slot_bindings}` from a pre-filtered ~30 catalog |
| `packages/a2ui/compose/strategies/zettel/chunk-composer.js` | Validator + materializer for chunk plans — enforces slot-name + chunk-kind contracts; substitutes slot regions with bound chunks' HTML |
| `packages/a2ui/compose/strategies/zettel/chunk-refiner.js` | Multi-turn refinement engine — two-pass synthesis (locator → modifier), validator-driven retry loop. Op format: `rebindSlot` / `appendToSlot` / `removeFromSlot` / `replacePage`. Outputs A2UI `updateComponents` messages |

### Engine — multi-turn state + telemetry

| File | Role |
| --- | --- |
| `packages/a2ui/compose/strategies/zettel/state-cache.js` | Bounded LRU keyed by `state_id` (default 64; `A2UI_STATE_CACHE_SIZE` env var). Stores `{intent, html, plan, ops_history, parent_state_id, created_at}` for the refiner chain |
| `packages/a2ui/compose/strategies/zettel/session-store.js` | Per-session conversation context (intent history, prior compositions) |
| `packages/a2ui/compose/strategies/zettel/issue-reporter.js` | First-class telemetry — `report_issue` MCP tool (LLM/user/auto reporters). Writes immutable JSON under `.brain/audit-history/issues/`; traces > 200KB spill to sidecar `.trace.json`. Distinct from `.tickets/` (curated work items) |

### Retrieval (catalog + analytics)

| File | Role |
| --- | --- |
| `packages/a2ui/retrieval/pattern-library.js` | Hardcoded seed patterns + runtime `registerPattern()`, keyword search, synonym merging (ingest tops it up from `packages/a2ui/corpus/patterns/`) |
| `packages/a2ui/retrieval/feedback/feedback-analyzer.js` | Reads JSONL feedback, aggregates by intent, finds weak/promotion candidates |
| `packages/a2ui/retrieval/intent/intent-categorizer.js` | Maps free-text intents to ~25 UI categories (form/_, data/_, layout/_, agent/_, etc. — see `CATEGORY_RULES` table for the live list) |
| `packages/a2ui/retrieval/feedback/gap-registry.js` | Persistent gap tracking (`packages/a2ui/corpus/gaps/registry.json`) |
| `packages/a2ui/compose/core/reference.js` | Thin wrappers over retrieval/ exports |

### LLM bridge + adapters

| File | Role |
| --- | --- |
| `packages/llm/llm-bridge.js` | createAdapter() — real LLM or stub fallback |
| `packages/llm/*.js` | Provider adapters (MUST use relative imports, not Vite `@llm/` aliases) |
| `scripts/load-env.mjs` | Shared .env loader for Node scripts |

### Corpus pipelines

| File | Role |
| --- | --- |
| `packages/a2ui/corpus/scripts/extract.js` | HTML → A2UI JSON (describeTree + generateTags) |
| `packages/a2ui/corpus/scripts/ingest.js` | JSON → pattern library (registerPattern with replace) |
| `scripts/build/harvest-chunks.mjs` | `[data-chunk]` boundary walker — writes `packages/a2ui/corpus/chunks/<name>.json` + `_index.json`. Run via `npm run harvest:chunks` |
| `packages/a2ui/corpus/scripts/run-pipeline.mjs` | Combined harvester → embeddings → ingest pipeline (Step 1 = chunks) |
| `packages/a2ui/corpus/scripts/build-pattern-index.mjs` | Pattern embedding-index builder (`text-embedding-3-small`) |

### MCP server

| File | Role |
| --- | --- |
| `packages/a2ui/mcp/server.js` | MCP stdio server, auto-ingests on startup. Hosts the `generate_ui` / `compose_from_chunks` / `refine_composition` / `report_issue` / `get_state` / `search_chunks` / `get_chunk` / `lookup_chunk` / `validate_schema` / `check_anti_patterns` / `submit_feedback` tool surface (full list: `mcp-tool-reference.md`) |

## Critical Rules

1. **Relative imports in `packages/llm/*.js`** — NEVER use `@llm/` aliases. They only work in the Vite browser context, not Node. Use `./anthropic.js` etc. Note that the repo-wide refactor rewrote all `@core`/`@components`/`@traits`/`@styles`/`@llm` aliases to relative paths so published consumers don't hit `ERR_MODULE_NOT_FOUND`; the Vite alias block in `vite.config.js` still exists but nothing in the codebase relies on it.

2. **load-env.mjs before any a2ui import** — Node doesn't read .env. Without it, createAdapter() silently returns StubLLMAdapter (canned 6-component Card).

3. **Metadata IS the search index** — Pattern descriptions and tags are what keyword search matches against. Bad metadata = invisible patterns. If you add patterns, make descriptions and tags rich.

4. **Two search paths**:
   - Instant mode: `searchBlocks()` → keyword only
   - Thinking mode: `searchBlocksSemantic()` → keyword + LLM reranking

5. **Instant mode gate**: tiered STRONG/WEAK/REJECTED matching lives in `generator.js`. Words ≥3 chars can match; `GATE_STOPS` filters boilerplate. Search the file for `searchBlocks(` / gate logic before tightening — line numbers drift.

6. **ingest.js: pages skip, chunks replace** — pages never overwrite hardcoded patterns (skips existing names). Chunks use `replace: true` so re-extraction updates stale chunk metadata.

7. **Chunk vs fragment paths are not interchangeable.** The fragment-graph synthesizer (`synthesizer.js` + `fragment-library.js`) operates on extracted fragment subtrees — atomic A2UI subtrees with strict reuse-ratio targets (≥29.9%). The chunk-synthesizer operates on `data-chunk`-marked HTML in `packages/a2ui/corpus/chunks/` — page/panel/block-kinded compositions with named slots. They share the same engine entry but consume different catalogs. Don't pipe one's catalog into the other's composer.

8. **Multi-turn refinements emit A2UI `updateComponents` messages, not new compositions.** The refiner mutates the plan via four ops (`rebindSlot` / `appendToSlot` / `removeFromSlot` / `replacePage`) and wraps each in a `updateComponents` message so the wire-format contract holds. The state-cache keys by `state_id` and chains through `parent_state_id` so refinement history reconstructs by walking the parent chain. Spec: `docs/specs/genui-multiturn-architecture.md`.

9. **issue-reporter is auto-fire-aware.** Engine failure paths call `autoReport(reason)` through `ctx.issueAccumulator`; this is suppressed when `ctx.evalMode` is true so eval runs don't pollute `.brain/audit-history/issues/`. When adding new failure paths in the engine, plumb the accumulator through; don't write directly to disk.

## Testing & Running

### Core

```bash
npm run test:a2ui              # smoke checks, no LLM calls
npm run test:a2ui:full         # + thinking mode (calls API)
npm run test:evals             # 5-dimension quality evals (instant mode)
npm run test:evals:thinking    # quality evals with LLM
npm run test:evals:baseline    # save baseline for regression detection
npm run test:all               # smoke + evals together
npm run pipeline               # extract + ingest
npm run pipeline:stats         # pattern counts by domain
npm run generate "login form"  # instant mode CLI
npm run generate --thinking "dashboard with charts"  # LLM mode
npm run generate --html "login form"  # output as AdiaUI HTML
npm run feedback:report        # quality trends, top gaps, promotion candidates
npm run feedback:promote       # run promotion check
npm run smoke:engines          # all registered engines
npm run smoke:register-engine  # in-process registration check
npm run eval:diff -- --engine zettel  # zettel coverage + avgScore floor
```

### Chunk-corpus pipeline

```bash
npm run harvest:chunks         # walk site/pages/** + corpus/exemplars → chunks/
npm run harvest:chunks:dry     # dry run
npm run smoke:chunks           # stub-LLM smoke (offline)
npm run eval:chunk-synthesis   # hold-out intents against real LLM
npm run build:embeddings       # patterns
npm run build:embeddings:chunks # chunks
npm run build:embeddings:all   # both
```

### Multi-turn (refiner + state-cache + issue-reporter)

```bash
npm run smoke:refine           # chunk-refiner two-pass synthesis smoke
npm run smoke:state-cache      # bounded LRU + chain-back invariants
npm run smoke:issues           # issue-reporter LLM/user/auto paths
npm run eval:refine-synthesis  # multi-turn refinement quality
```

## Key Insight: Metadata IS the Search Index

Pattern descriptions and tags are what keyword search matches against. The single biggest quality improvement came from enriching extract.js to derive descriptions from component structure (headings, labels, icons, button text) instead of using filenames. Went from 40% to 95% meaningful descriptions. When search quality degrades, check `describeTree()` and `generateTags()` in extract.js first.

## Subagent QA Checklist

When subagents create training HTML, they consistently produce these bugs:

1. `slot="heading"` without `variant` (headings render unstyled)
2. `timeline-item-ui` with nested slots instead of `label`/`description`/`time` attributes
3. `table-ui` wrapping native `<table>` HTML (shows "No data" overlay — use plain `<div>` for static tables)
4. Footer buttons missing `block` or `style="flex:1"` (narrow CTAs in wide cards)
5. Star icons without `weight="fill"` (renders as outlines)

The sibling skill **adia-ui-authoring** owns these audits (the four-axis contract guard rails plus token-contract audits).
