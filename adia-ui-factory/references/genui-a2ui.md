---
name: genui-a2ui
load-when: authoring a generative-UI experience — mounting the a2ui runtime, feeding generated A2UI, wiring resolvers, or using the corpus
load-size: ~2.5k tokens
required-for: [adia-ui-genui — all modes]
---

# a2ui runtime & corpus — consumer surface

The consumer-facing a2ui runtime (mount + feed + resolve) and corpus (core vs custom). Pipeline internals (compose strategies, zettel scoring, catalog) are maintainer territory — not here. Exact names below; treat as a snapshot (re-bake with the pinned MCP).

## Render roots

**`<a2ui-root>`** — renders an A2UI surface.
- **Author mode:** set `.doc = A2UIMessage[]` (a JS property; setting it re-renders). Use for editors/previews/tests.
- **Stream mode:** set `src` + `transport` (`sse` | `ws` | `jsonl` | `mcp`); the root opens the stream and reconciles messages as they arrive. (`doc` wins if both are set.)
- **Events:** `a2ui-message` (per message) · `a2ui-connected` / `a2ui-error` / `a2ui-closed` (stream) · `a2ui-action` (a child `[data-action]` fired). History: `back()` / `forward()`.

**`<gen-root mode="chat|split|canvas">`** — a layout shell unifying chat + canvas (+ `inspector` to debug the generated tree). Switch layout via `mode`.

```html
<a2ui-root id="canvas"></a2ui-root>
<script type="module">
  import { registerResolver } from '@adia-ai/a2ui-runtime';
  registerResolver('resource', async (uri) => fetchResource(uri));  // register BEFORE feeding
  document.getElementById('canvas').doc = validatedMessages;        // A2UIMessage[]
</script>
```

## A2UI message format

A discriminated union the runtime reconciles (set `.doc` to an array of these):
- `createSurface` — `{ type, surfaceId, root? }` — start a surface.
- `updateComponents` — `{ type, surfaceId, components: [{ id, component, children?, ...props }] }` — upsert the tree; `component` is an A2UI type name (`Card`, `Text`, `Stat`, …); other keys are props. A prop can be a **data binding** `{ path: 'kpi/value' }`.
- `updateDataModel` — `{ type, surfaceId, path, value }` — set data (JSON-Pointer path) that bindings read.
- `wireComponents` — `{ type, surfaceId, controllers?, dataSources?, … }` — declare controllers/handlers/data sources/actions.
- `meta` — `{ type, feedback? }` — pipeline metadata/reasoning (traces, feedback).

## registerResolver

```js
import { registerResolver } from '@adia-ai/a2ui-runtime';
registerResolver('resource', async (uri, params) => { … });   // resolves resource:// → your data
```
Built-in schemes: `resource:` (→ a `/api/...` REST convention), `api:` (direct URL), `mock:` (returns a stub). Register **once per session, before** any generated UI references the scheme — an unresolved scheme renders empty.

## The loop, end to end

`classify_intent` → `assemble_context` (or `search_chunks` to ground) → `generate_ui` → **`validate_schema` + `check_anti_patterns`** → set `root.doc` → `refine_ui` (carry a `sessionId` for multi-turn; the server keeps the session's fragment state) or `root.back()/forward()`. **Validate before every render** — the runtime renders what you give it; garbage in, garbage rendered.

## Corpus — core vs roll-your-own

- **Shape:** chunks are JSON (`{ name, kind: block|panel|page, component tree, metadata }`), with an `_index`, a `catalog`, and pre-computed `chunk-embeddings`. Harvested from real pages' `data-chunk` markers.
- **Core:** the MCP ships and retrieves over it — `search_chunks` (keyword always; semantic when `VOYAGE_API_KEY`/OpenAI is set) / `lookup_chunk`. Offline-capable (embeddings are committed).
- **Roll your own** *(pattern, lightly documented):* author demo pages → mark regions with `data-chunk` + `data-chunk-kind`/`-domain`/`-description`/`-keywords` → harvest to chunks → point retrieval at your set → (optional) build embeddings (needs a key). **Grounding rule:** every chunk must trace to a real page — no synthetic chunks.

## Consumer vs maintainer

Consumer (here): mount roots, register resolvers, call the MCP to generate/validate/refine, use or author a corpus. Maintainer (elsewhere): compose strategies, zettel scoring, the component catalog, embedding-model choice, evals. If you're editing `packages/a2ui/compose/**` or tuning retrieval scoring, you've crossed into maintainer territory.
