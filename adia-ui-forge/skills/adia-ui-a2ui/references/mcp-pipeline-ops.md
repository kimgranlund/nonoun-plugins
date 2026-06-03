# Reference: MCP pipeline operations — generate → validate → render → feedback

**Source:** Absorbed from the former `adia-ui-training` skill (§Workflows + §Validation checks + §Feedback loop) — Phase 3 rollup. **Used by:** mode 1 of `adia-ui-a2ui` (operator-side MCP runs). **Companion:** `mcp-tool-reference.md`, `anti-patterns.md`, `eval-diagnostics.md`.

---

## Workflows

### Full pipeline — one command

```bash
node scripts/mcp-pipeline.cjs "dashboard with 4 stat cards and a revenue chart"
```

Pipes `intent → generate_ui → validate_schema → a2ui-to-html → check_anti_patterns` and prints the scores. Fastest way to confirm the whole stack is working after a change.

### Step-by-step (when you need to inspect intermediates)

```bash
# 1. Generate
node scripts/mcp-call.cjs generate_ui \
  '{"intent":"dashboard with 4 stat cards","mode":"instant"}'

# 2. Validate — paste the messages array from step 1
node scripts/mcp-call.cjs validate_schema \
  '{"messages":"<paste-messages-json>"}'

# 3. Render — inspect the HTML before anti-pattern scanning
echo '<paste-messages-json>' | node scripts/a2ui-to-html.cjs

# 4. Anti-pattern check
node scripts/mcp-call.cjs check_anti_patterns \
  '{"html":"<paste-rendered-html>"}'
```

### Validation-only (existing A2UI doc)

Useful for auditing training corpus entries. `validate_schema` is fast and deterministic — batch it over `packages/a2ui/corpus/patterns/**/*.json` to surface drift without re-running the generator.

### Multi-turn generation (legacy executionId chain)

Every `generate_ui` response includes an `executionId`. Pass it back on subsequent calls to keep the pattern-library context and the feedback record coherent — so a score submitted against that id attributes correctly to the original run.

### Compose from the chunk corpus

When the intent matches a known page-shape (auth flow, dashboard layout, error shell), prefer `compose_from_chunks` over `generate_ui`:

```bash
node scripts/mcp-call.cjs compose_from_chunks \
  '{"intent":"sign-in card with email + password + OAuth"}'
```

The synthesizer first checks for a strong retrieval match (score ≥ 8); if no chunk dominates, it picks a `{page, slot_bindings}` plan from a pre-filtered ~30 catalog and materializes via the chunk composer. Validator enforces slot-name + chunk-kind contracts before HTML emission. Returns `{state_id, html, plan, candidates}` — pass `state_id` to `refine_composition` to mutate this surface in subsequent turns.

### Multi-turn refinement (state_id chain)

```bash
# Turn 1: create the surface
node scripts/mcp-call.cjs compose_from_chunks \
  '{"intent":"sign-in card with email + password"}'
# → returns state_id "abc123"

# Turn 2: mutate by intent
node scripts/mcp-call.cjs refine_composition \
  '{"state_id":"abc123","intent":"add OAuth row with Google + GitHub"}'
# → returns updateComponents A2UI messages + new state_id "def456"
```

The refiner runs two-pass synthesis:

1. **Locator** — identifies which slots are affected by the intent
2. **Modifier** — picks the op (`rebindSlot`/`appendToSlot`/`removeFromSlot`/`replacePage`) and target chunk

Validator-driven retry loop (default `maxAttempts=2`). Each refinement chains through `parent_state_id` so you can `get_state` and walk back through the conversation history.

### Reporting issues from the LLM side

If you (the agent) determine that the engine produced something that breaks expectations, fire `report_issue`:

```bash
node scripts/mcp-call.cjs report_issue \
  '{"state_id":"abc123","reporter":"llm","reason":"slot-binding produced empty section","trace":{...}}'
```

Lands as immutable JSON under `.brain/audit-history/issues/`. These become weekly-triage candidates for promotion to curated tickets when patterns emerge.

## Validation checks

`validate_schema` runs a weighted checklist (target aggregate ≥ 80). Common failures when training data drifts:

- `hasRootComponent` — missing `id: "root"` on the surface root.
- `cardContentModel` — section without `col-ui` wrapper, or heading inside section instead of header.
- `headingHierarchy` — skipped levels (h1 → h3).
- `flatAdjacency` — nested components instead of sibling id references.

Full list + weights: `mcp-tool-reference.md`.

## Feedback loop

After a run, score the output with `submit_feedback` keyed on the `executionId`. The feedback analyzer (`packages/a2ui/retrieval/feedback/feedback-analyzer.js`) aggregates these into:

- Per-intent quality trends.
- Promotion candidates (runs scoring ≥ 95 with ≥ 4 rating across 3+ runs become named patterns via `npm run feedback:promote --apply`).
- Gap registry — intents with no pattern match AND low scores land in `packages/a2ui/corpus/gaps/registry.json`.

Running `npm run feedback:report` surfaces the current state.
