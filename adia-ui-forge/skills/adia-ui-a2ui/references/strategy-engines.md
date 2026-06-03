# Reference: Strategy engines — file map + 5 strategy labels + parallel pipelines

**Source:** Absorbed from the former `zettel-internals` skill (Phase 3 rollup). **Used by:** mode 5 of `adia-ui-a2ui` (debug zettel composition). **Companion:** `zettel-calibration.md`, `semantic-fail-lifting.md`, `fragment-graph.md`.

---

## File map (~2,936 LOC across 12 files)

```text
packages/a2ui/compose/strategies/zettel/
├── generator-adapter.js  202   ← entry point + 5-strategy dispatch
├── generate.js            15   ← thin wrapper for direct invocation
├── _smoke.js              37   ← in-tree smoke test
│
├── fragment-library.js   209   ← loader: corpus/{fragments,compositions}/*.json
├── composer.js           146   ← resolves $fragment refs, prefixes IDs, applies bindings
├── synthesizer.js        343   ← LLM-driven composition (fragment-graph)
├── session-store.js      121   ← multi-turn artifact tracking (in-memory)
│
├── chunk-synthesizer.js  417   ← page-shell + slot-binding (chunk-corpus)
├── chunk-composer.js     182   ← resolves chunk plan into A2UI messages
├── chunk-refiner.js      514   ← multi-turn refinement (locator → modifier)
├── state-cache.js        153   ← bounded LRU keyed by state_id
└── issue-reporter.js     597   ← telemetry → .brain/audit-history/issues/
```

## Two parallel pipelines under one strategy

```text
                 ┌─ retrieval (always tried first)
                 │   from corpus/fragments + corpus/compositions OR corpus/chunks
                 │
generator       │
-adapter.js    ─┼─ session iteration (turn > 1 + LLM)
                │   reads session-store, hydrates priorTurns into prompt
                │
                └─ synthesis fallback (retrieval < threshold + LLM)
                   ├─ synthesizer.js     (fragment-graph)
                   └─ chunk-synthesizer  (chunk-corpus)
```

**These are NOT a hierarchy** — they're two parallel reasoning loops. `zettel` engine = fragment-graph; `chunk-zettel` engine = chunk-corpus. Both register independently in the engine registry.

## The 5 strategy labels (emitted to eval harness)

| Strategy | Trigger | Hot path? |
| --- | --- | --- |
| `composition-match` | Fresh retrieval, score ≥ `STRONG_MATCH_THRESHOLD` | Yes — no LLM call |
| `composition-synthesized` | Fresh LLM composition (no prior turns) | No — LLM call |
| `composition-iterated` | LLM modified prior turn's template | No — LLM call w/ history |
| `fragment-candidates` | Retrieval weak + no LLM available → atoms only | Yes — no LLM call |
| `synthesis-failed` | LLM tried + failed validation | Cold — failure path |

For chunk-zettel, mirror set: `chunk-match`, `chunk-synthesized`, `chunk-iterated`, `chunk-failed`.

## Issue reporter — three call paths

| Path | Trigger | `ctx.reporter` | Suppression |
| --- | --- | --- | --- |
| LLM self-fire | `report_issue` MCP tool | `'llm'` | None |
| Consumer-fire | Human requests bug ticket | `'user'` | None |
| Engine auto-fire | Internal failure (e.g., scope-drift, synthesis-failed) | `'auto'` | When `ctx.evalMode = true` (avoid eval-run noise) |

**Storage**: `.brain/audit-history/issues/<id>.json` (immutable). Traces > 200KB spill to sidecar `.trace.json`.

**Type taxonomy**:

- `bug` (code defect)
- `training-gap` (corpus missing a pattern)
- `protocol-gap` (MCP / engine contract issue)
- `ux-feedback` (output quality complaint)

**Severity ranks**: `nit` (0) < `drift` (1) < `blocker` (2)

**Owner taxonomy**: `synthesis | retrieval | validator | chunk-corpus | mcp-protocol | unknown`

**Distinct from `.tickets/`** — those are human-authored work items. Issues are runtime telemetry, promoted to tickets during weekly triage when patterns emerge (spec §11.5).

## Session iteration — the priority flag

```js
if (hasHistory && llmAdapter) {
  // ALWAYS goes to synthesis with history context.
  // NEVER picks a fresh retrieved composition on follow-up turns.
}
```

This is what makes "add a button" / "hydrate with real images" work — follow-ups modify the existing canvas instead of regenerating.

## Pitfalls

- **`STRONG_MATCH_THRESHOLD` was raised post-incident**. Lowering it back to 22 reverts to repetitive output. If you suspect retrieval is too cold, profile the score distribution first via `searchAll()` debugging, don't just lower the threshold.
- **`PRE_SEARCH_LIMIT = 30` may be over-permissive at small corpus sizes.** It was calibrated for a much larger corpus. Worth re-tuning post-corpus-migration.
- **`state-cache` is per-process** — multi-turn breaks across MCP restarts. Anything that needs durable state should write to `.brain/audit-history/` or `.tickets/`, not state-cache.
- **`issueAccumulator` must be passed via `opts`** to refinement engines — if you wire a new engine, propagate it or auto-fire issues are lost.
- **Strategy labels are public contract.** The eval harness, MCP tools, and dialog-recorder all pattern-match on the 5 strategy strings. Don't rename without a coordinated migration.

## Verification

```bash
# Smoke tests (fast, no LLM)
npm run zettel:smoke
npm run smoke:engines

# Full eval (slow, real LLM)
npm run eval:diff -- --engine zettel
npm run eval:diff -- --engine chunk-zettel

# Issue store sanity (after auto-fire test)
ls .brain/audit-history/issues/ | head
```
