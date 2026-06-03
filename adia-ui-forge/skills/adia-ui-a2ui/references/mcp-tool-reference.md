# Reference: MCP tool reference — schemas + I/O contracts

**Source:** Absorbed from the former `adia-ui-training` skill (§MCP tool map + its tool-reference doc) — Phase 3 rollup. **Used by:** mode 1 + mode 7 of `adia-ui-a2ui` (MCP pipeline run / MCP tool add or change). **Companion:** `mcp-pipeline-ops.md`.

---

## MCP tool map

Defined in `packages/a2ui/mcp/server.js` and surfaced through the MCP client (Claude Code exposes them as `mcp__adia-ui__*`). Full input/output schemas are inlined below.

### Composition (intent → A2UI / HTML)

| Tool | Purpose |
| --- | --- |
| `generate_ui` | Intent → A2UI messages. Mode = `instant` \| `thinking` \| `stream`. The default fragment-graph + LLM path. |
| `compose_from_chunks` | Two-tier composer over the gen-UI chunk corpus. Tier 1 = retrieval-first (return matched chunk's HTML when score ≥ 8); Tier 2 = LLM mix-and-match: pick `{page, slot_bindings}` from a pre-filtered ~30 catalog. Validator enforces slot + chunk-kind contracts. Use when the intent is a known page-shape (auth flow, dashboard layout, error shell). |
| `resolve_composition` | Materializes a chunk plan into HTML — same composer the synthesizer uses internally. Useful when authoring or testing a hand-written plan. |
| `get_composition` | Inspect the composition tree (intent → fragment chain → component IDs) for a given executionId. |

### Multi-turn refinement

| Tool | Purpose |
| --- | --- |
| `refine_composition` | Mutate a prior composition by intent — e.g. "add an OAuth row", "swap the password field for a passkey". Two-pass synthesis (locator → modifier); ops = `rebindSlot` / `appendToSlot` / `removeFromSlot` / `replacePage`; emitted as A2UI `updateComponents` messages. Requires the prior `state_id`. |
| `get_state` | Read the current `{intent, html, plan, ops_history, parent_state_id, created_at}` for a `state_id`. Touches LRU recency. |
| `report_issue` | First-class telemetry surface — write an immutable issue record under `.brain/audit-history/issues/`. Reporter values: `llm` (self-fire), `user` (consumer-fire), `auto` (engine failure path). Suppressed when evalMode is true. Distinct from `.tickets/` (curated work items — those are weekly-triage promotions of recurring issue patterns, see spec §11.5). |

### Chunk-corpus retrieval

| Tool | Purpose |
| --- | --- |
| `search_chunks` | Keyword + cosine-blended search over the chunk corpus (`block / panel / page` kinds). Returns ranked chunk-name candidates. Filter by `kind` to constrain. |
| `get_chunk` | Full record for one chunk (HTML, slot regions, nested chunks, metadata). |
| `lookup_chunk` | Find chunks where `<component>` is the primary element (e.g. all chunks centered on `<table-ui>`). |

### Catalog inspection

| Tool | Purpose |
| --- | --- |
| `lookup_component` | Catalog entry for a single component. |
| `get_component_map` | Full catalog map (all components + props). |
| `search_patterns` | Keyword search over the pattern library (legacy fragment-graph corpus, distinct from chunks). |
| `classify_intent` | Free-text intent → UI-category taxonomy. |
| `assemble_context` | Compose retrieval context for a given intent (the bundle the LLM sees pre-prompt). |
| `get_traits` | Trait catalog (pressable, hoverable, focusable, etc.). |
| `get_wiring_catalog` | A2UI wiring contract — createSurface / updateComponents / wireComponents. |
| `get_fragment` | Inspect a single fragment from the fragment library (the atomic units used by the legacy synthesizer). |
| `get_graph` | Pattern-and-fragment graph view (fragment leverage metrics). |
| `get_quality_metrics` | Per-pattern quality scores from the feedback analyzer. |
| `get_training_gaps` | Gap registry — intents with no good pattern match. |
| `zettel_stats` | Zettel-engine corpus stats (coverage, avgScore, MRR). |

### Pipeline (validation, render, ingest)

| Tool | Purpose |
| --- | --- |
| `validate_schema` | Structural + wiring checks on A2UI messages; returns weighted score. |
| `check_anti_patterns` | HTML → anti-pattern report (see list below). |
| `convert_html` | HTML → A2UI transpile (used by the editor's ingest modal). |
| `import_pattern` | Register a new pattern at runtime. |
| `run_eval` | Run the eval suite over the held-out intent set. |
| `submit_feedback` | Post a quality score against an `executionId`. |

## Local scripts (thin wrappers over MCP)

- `scripts/mcp-pipeline.cjs "<intent>"` — full pipeline in one shot. Generates → validates → renders → anti-pattern check → prints a combined report.
- `scripts/mcp-call.cjs <tool> '<json-args>'` — single-tool call. Use when stepping through manually or inspecting an intermediate output.
- `scripts/a2ui-to-html.cjs [file|stdin]` — renders A2UI message arrays to HTML using the gen-ui runtime. Useful between `validate_schema` and `check_anti_patterns` when you want to inspect the rendered markup.

---

## Full tool-reference

Complete input/output schemas for the core gen-ui MCP tools.

---

## generate_ui

Generate A2UI components from natural language.

**Input:**

```json
{
  "intent": "string (required) — description of UI to generate",
  "mode": "instant | thinking (optional, default: instant)"
}
```

**Output:**

```json
{
  "executionId": "string — unique ID for feedback/multi-turn",
  "messages": [
    {
      "type": "updateComponents",
      "surfaceId": "default",
      "components": [
        { "id": "root", "component": "Card", "children": ["hdr", "sec"] },
        { "id": "hdr", "component": "Header", "children": ["title"] },
        { "id": "title", "component": "Text", "variant": "h3", "text": "Title" }
      ]
    }
  ],
  "validation": { "passed": true, "score": 95, "checks": [] },
  "suggestions": ["Add a footer with save button", "Consider tabs for multiple sections"]
}
```

---

## validate_schema

Validate A2UI messages against structural rules.

**Input:**

```json
{
  "messages": "string — JSON-encoded array of A2UI messages"
}
```

**Output:**

```json
{
  "passed": true,
  "score": 95,
  "checks": [
    { "name": "hasRootComponent", "passed": true, "score": 1, "weight": 10, "detail": "Root component found" },
    { "name": "cardContentModel", "passed": false, "score": 0, "weight": 15, "detail": "Section at body-sec missing Column wrapper" }
  ]
}
```

**Checks (15 structural + 5 wiring):** | Check | Weight | What it validates | |-------|--------|-------------------| | `hasRootComponent` | 10 | Root component with id "root" exists | | `uniqueIds` | 10 | No duplicate component IDs | | `validChildren` | 10 | All child IDs reference existing components | | `cardContentModel` | 15 | Card > Header + Section > Column + Footer | | `correctSlotUsage` | 10 | Slots on correct elements | | `flatAdjacency` | 5 | No deep nesting (components use ID references) | | `noRawHTML` | 5 | No native HTML tags as component types | | `buttonProps` | 5 | Button has text prop | | `formFieldProps` | 5 | Form fields have name and label | | `textVariants` | 5 | Text components have valid variants | | `tabStructure` | 5 | Tabs only contain Tab children | | `noEmptyContainers` | 3 | Containers have children | | `actionSlots` | 3 | Footer buttons have slot="action" | | `headingHierarchy` | 3 | No skipped heading levels | | `noOrphans` | 3 | No unreferenced components |

---

## lookup_component

Look up component API by type name.

**Input:**

```json
{
  "type": "string — Component type (Card, Button, TextField, etc.)",
  "level": "index | summary | reference (optional, default: reference)"
}
```

**Output (reference level):**

```json
{
  "component": "card-ui",
  "description": "Container surface with...",
  "properties": {
    "elevation": { "type": "number", "enum": [0,1,2,3], "default": 1 },
    "size": { "type": "string", "enum": ["xs","sm","md","lg","xl"] }
  },
  "children": { "header": {}, "section": {}, "footer": {} },
  "tokens": { "--card-background": "..." },
  "events": {}
}
```

**Detail levels:**

- `index` — type, tag, description only (~50 tokens)
- `summary` — + properties, slots, events (~200 tokens)
- `reference` — + children, tokens, patterns (~500 tokens)

---

## get_component_map

Full catalog — all component types with tags.

**Input:** `{}` (no args)

**Output:** One line per component:

```text
Row -> <row-ui>: Horizontal flex container
Column -> <col-ui>: Vertical flex container
Card -> <card-ui>: Container surface with elevation and variants
...
```

---

## search_patterns

Search the pattern library.

**Input:**

```json
{
  "query": "string — search keywords",
  "semantic": "boolean (optional) — use LLM for conceptual matching",
  "remix": "boolean (optional) — compose new pattern from existing"
}
```

**Output (keyword):**

```json
[
  {
    "name": "stat-cards",
    "description": "KPI grid with 4 stat cards",
    "domain": "dashboard",
    "template": []
  }
]
```

---

## classify_intent

Classify natural language into a UI domain.

**Input:**

```json
{
  "text": "string — intent description"
}
```

**Output:**

```json
{
  "domain": "forms",
  "confidence": 0.85,
  "keywords": ["login", "form", "email", "password"],
  "suggestedComponents": ["Card", "Header", "TextField", "Button", "FormContainer"]
}
```

**Domains:** `forms`, `dashboard`, `data`, `chat`, `settings`, `navigation`, `content`, `commerce`

---

## assemble_context

Progressive-disclosure context assembly for LLM prompts.

**Input:**

```json
{
  "intent": "string — what the LLM needs to generate",
  "tier": "number 0-4 (optional, default: 1)"
}
```

**Budget tiers:** | Tier | Budget | Contents | |------|--------|----------| | 0 | ~200 tokens | Type names only | | 1 | ~1000 tokens | + properties, slots | | 2 | ~3000 tokens | + children, tokens, events | | 3 | ~8000 tokens | + patterns, examples | | 4 | unlimited | Full catalog dump |

---

## check_anti_patterns

Check HTML against the anti-pattern registry.

**Input:**

```json
{
  "html": "string — HTML markup to check"
}
```

**Output:** Array of violations (empty if clean):

```json
[
  {
    "name": "slotOnContainer",
    "description": "Slot attributes must go on children, not Header/Footer",
    "fix": "Move slot=\"heading\" from <header> to the Text child inside it"
  }
]
```

---

## get_traits

Get the trait catalog.

**Input:**

```json
{
  "category": "string (optional) — filter by category"
}
```

**Categories:** `input-interaction`, `focus-keyboard`, `form-state`, `motion-animation`, `layout-positioning`, `observer`, `visual-effect`, `state-management`

---

## get_wiring_catalog

Full wiring knowledge base.

**Input:** `{}` (no args)

**Output:**

```json
{
  "controllers": [
    { "type": "FormController", "manages": "Validation, dirty/pristine", "commands": ["validate","reset","setFieldError"] }
  ],
  "handlers": [
    { "type": "submit-resource", "purpose": "POST/PUT/DELETE to resource URI", "required": ["uri","method"] }
  ],
  "refreshStrategies": ["once", "on-focus", "interval:{ms}", "stream", "on-action:{name}"],
  "valueSources": ["event-detail", "event-target", "model", "literal", "param"],
  "associationTypes": ["routes-to", "feeds", "shares-context", "depends-on", "triggers", "contains", "slots-into"]
}
```

---

## convert_html

Transpile HTML -> A2UI flat adjacency messages.

**Input:**

```json
{
  "html": "string — HTML markup",
  "mode": "instant | reasoning (optional, default: instant)"
}
```

`instant` uses rule-based mapping. `reasoning` uses LLM for complex layouts (requires API key).

---

## import_pattern

Register a pattern in the runtime library.

**Input:**

```json
{
  "pattern": "string — JSON-encoded pattern object"
}
```

Pattern shape:

```json
{
  "name": "login-basic",
  "description": "Simple login form",
  "domain": "forms",
  "template": [{"id":"root","component":"Card","children":["hdr","sec"]}],
  "components": ["Card","Header","TextField","Button"]
}
```

---

## submit_feedback

Submit quality feedback for the evolution engine.

**Input:**

```json
{
  "executionId": "string (required) — from generate_ui result",
  "rating": "number 1-5 (required)",
  "intentAlignment": "number 1-5 (optional)",
  "visualQuality": "number 1-5 (optional)",
  "componentChoice": "number 1-5 (optional)",
  "userEdited": "boolean (optional)",
  "editSummary": "string (optional)",
  "notes": "string (optional)",
  "shouldBePattern": "boolean (optional)",
  "suggestedName": "string (optional)"
}
```
