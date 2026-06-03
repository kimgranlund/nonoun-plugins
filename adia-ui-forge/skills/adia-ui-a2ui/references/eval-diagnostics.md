# Reference: Eval diagnostics — gap diagnosis + regression triage

**Source:** Absorbed from the former `a2ui-pipeline` skill (§Eval Gap Diagnosis + §Eval Suite + §Verification) — Phase 3 rollup. **Used by:** mode 6 of `adia-ui-a2ui` (diagnose eval gap or regression). **Companion:** `strategy-engines.md`, `zettel-calibration.md`.

---

## Eval Gap Diagnosis

**Mandatory first step — run diagnostics before touching code.**

The #1 anti-pattern: "tweak and hope" — changing a prompt or adding a chunk without knowing why the current score is low. This wastes eval runs (real LLM cost per run).

## Phase 0: Author a diagnostic script

For each failing intent, capture:

1. **Search ranking** — what `searchChunks()` returns for the intent query
2. **Composition output** — what the pipeline actually emitted (HTML or plan)
3. **Tag inventory** — every custom-element-like tag in emitted HTML
4. **Coverage delta** — expected_components vs. found_components

Diagnostic must be runnable in **stub mode** (no LLM cost).

Template:

```js
async function diagnose(intent) {
  const search = searchChunks(intent.intent, { limit: 10 });
  const comp = await composeFromIntent({ intent: intent.intent, llmAdapter: null });
  const tags = [...comp.html.matchAll(/<([a-z]+-[a-z-]+)[\s>]/gi)]
    .map(m => m[1]).filter((v,i,a) => a.indexOf(v)===i);
  const found = intent.expected_components.filter(tag =>
    new RegExp(`<${kebab(tag)}-ui[\\s>]`).test(comp.html));
  return { search, tags, found, missing: intent.expected_components.filter(t => !found.includes(t)) };
}
```

## Phase 1: Classify failures

| Bucket | Symptom | Root cause | Speed |
| --- | --- | --- | --- |
| A. Holdout misalignment | Top-1 retrieved ≠ expected_chunk | Holdout expected_chunk drifted from corpus | Minutes |
| B. Coverage gap | Retrieved chunk exists but HTML lacks expected tags | Chunk HTML doesn't contain those components | Hours (new chunks) |
| C. Wrong shell | Retrieval OK but LLM picks wrong page shell | Prompt ambiguity or missing domain→shell mapping | Hours (prompt tuning) |
| D. Broken render | HTML emitted but console errors / blank | Missing component registrations or bad markup | Hours (harvester bug) |
| E. Measurement bug | Composition looks correct but score low | Scoring code has regex/casing/substring bug | Minutes (fix scorer) |
| F. Embedding drift | Async search returns different top-1 than sync | Embeddings non-deterministically boost wrong chunks | Minutes (use sync for fast path) |

**Fix order:** A → E → F → C → B → D

- Fix measurement before fixing content (otherwise you can't trust scores)
- Fix determinism before adding content (otherwise evals fluctuate)

## Phase 2: Specific fixes

### A. Holdout alignment

```bash
npm run eval:diagnose
# Or directly: node packages/a2ui/mcp/scripts/eval-fix.mjs --verbose
```

Map each intent's `expected_chunk` to the actual top-1 retrieved chunk. Update `holdout-compose-from-chunks.jsonl`.

### E. Measurement bugs (common traps)

1. **PascalCase → kebab-case** — `AgentTrace` must become `agent-trace` (not `agenttrace`)
2. **Substring match** — `pane` matching `panel` gives false positives
3. **Regex escaping** — `textarea-ui` contains `text-ui` as substring; need word boundaries
4. **Case sensitivity** — HTML may be uppercase; regex needs `/i` flag

### F. Embedding drift

Symptom: `searchChunksAsync` returns different top-1 than `searchChunks`. Root cause: small cosine boosts (0.1–0.3) flip rankings unpredictably. Fix: prefer sync keyword search for deterministic paths (fast-retrieval tier). Keep async for synthesis-tier only (where creativity is desired).

### B. Coverage gap (adding block chunks)

When the LLM needs components not in corpus:

1. Create `catalog/ui-patterns/app/<name>/<name>.contents.html`
2. Use `data-chunk="<name>"` + `data-chunk-kind="block"` markers
3. Include actual component tags (`<input-ui>`, `<button-ui>`, etc.) so coverage scoring matches
4. Re-harvest: `npm run harvest:chunks`

### C. Wrong shell (prompt tuning)

When the LLM consistently picks the wrong page shell:

1. Check `SYSTEM_PROMPT` domain→shell mapping table
2. Add explicit examples for the failing domain
3. Add negative constraint: "NEVER default to dashboard-admin-page for non-dashboard intents"

### D. Broken render

When HTML is structurally valid but render score is low:

1. Check `render-fidelity.mjs` output: console errors, blank viewport, undefined custom elements
2. Verify component registrations in `packages/web-components/index.js`
3. Check harvester didn't strip `data-chunk-slot` from page shells

## Verification

After all fixes, run:

```bash
# Stub first (fast, free)
npm run eval:compose-from-chunks

# Then real-LLM if stub improved
npm run eval:compose-from-chunks -- --real-llm --report-file
```

Stop only when all intents pass and avg is stable across 3 runs.

## Eval Suite

`packages/a2ui/mcp/scripts/test-evals.mjs` scores generated output on 5 weighted dimensions:

- structural_validity (30%): schema validation score
- intent_alignment (25%): F1 of required vs present components
- component_coverage (20%): absence of forbidden patterns
- card_model_compliance (15%): header/section/footer structure
- anti_pattern_count (10%): text without variant, header children without slot

Baseline regression: `--save-baseline` stores scores, subsequent runs flag any dimension dropping

> 5 points or aggregate dropping >3 points. Exit code 2 = regression.
