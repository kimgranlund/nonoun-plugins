# Reference: Zettel calibration — constants + history + locator/modifier two-pass

**Source:** Absorbed from the former `zettel-internals` skill (§Calibration constants + §The locator → modifier two-pass pattern) — Phase 3 rollup. **Used by:** mode 5 of `adia-ui-a2ui` (tune calibration; lift fails). **Companion:** `strategy-engines.md`, `semantic-fail-lifting.md`.

> **Calibration history is the substrate.** Each tweak leaves a row. Read history before retuning — the same value may have been tried and rejected before.

---

## Calibration constants — values + history

**Don't change these without running the eval-diff suite first.** Each is calibrated against the held-out 100-intent set or production telemetry.

### `STRONG_MATCH_THRESHOLD = 40`

- **File**: `generator-adapter.js`
- **Raised**: 22 → 40 post-incident
- **Reason**: At 22, login-form / signup-form played verbatim too often → repetitive output. At 40, only near-perfect retrievals (chart-dashboard=48, pricing-tiers=54) match; merely-good fall through to LLM for compositional variety.
- **Scale**: **Absolute**, not relative. Score is a weighted sum of `semantic_role` (12) + `tags` (5 each) + `keywords` (3 each) matches between query tokens and fragment metadata. Adding/removing fragments from the corpus does not shift any specific (query, fragment) score — it's deterministic per pair. **Don't recalibrate as a function of corpus size** — that would be a misdiagnosis.
- **Tradeoff**: More LLM calls (slower, costlier) ↔ compositional variety
- **Re-eval before changing**: `npm run eval:diff -- --engine zettel`

### `STRONG_RETRIEVAL_SCORE = 8`

- **File**: `chunk-synthesizer.js`
- **Scale**: corpus-size-**independent** absolute keyword score from `chunk-library.js#keywordScore()`. Adding 1k chunks doesn't shift any individual (chunk, query) score. Don't propose recalibration as a function of corpus size — that's a misdiagnosis.
- **What 8 means**: at least one whole-word overlap between query and chunk name (10), OR full-query substring (5) + ≥1 whole-word token (3). Anything less is a "retrieval too weak — synthesize" signal.
- **Async path**: `searchChunksAsync` blends `kw + cos*5`. Cosine ranges 0..1 so embeddings contribute 0..5 — pure-cosine matches max out at 5 and won't pass the 8 threshold. **Embeddings are a tie-breaker**, not the primary signal. This is intentional.
- **Different scale** than fragment-graph `STRONG_MATCH_THRESHOLD=40` (which scores semantic_role + tags + keywords). Don't normalize the two scales — they measure different things.
- **WONTFIX rationale** documented in the corpus audit reports under `docs/reports/`.

### `PRE_SEARCH_LIMIT = 30`

- **Files**: `chunk-synthesizer.js`, `chunk-refiner.js`
- **Reason**: Token-budget mitigation — pre-filter catalog before LLM sees it. Sending the full catalog every prompt would burn tens of thousands of input tokens.
- **Synthesizer** (`chunk-synthesizer.js`): kind-aware allocation — `limit: PRE_SEARCH_LIMIT - pageChunks.length - panelChunks.length`. All pages and panels included unconditionally; blocks fill the remaining budget. **Self-tuning by structure.**
- **Refiner** (`chunk-refiner.js`): block-only allocation — `limit: PRE_SEARCH_LIMIT` for blocks alone, plus all pages/panels on top. Intentionally more generous because refinement is doing targeted edits and the LLM needs more options.
- **Don't naively divide PRE_SEARCH_LIMIT by corpus size** to assess over-permissiveness. The kind-aware allocation makes the math non-linear. See the pre-search-limit audit under `docs/reports/` for the full analysis.

### `SCOPE_DRIFT_RATIO = 1.5`

- **File**: `chunk-synthesizer.js`
- **Trigger**: Composed envelope's component count > 1.5× sum of bound chunks' component counts → auto-fires `scope-drift` issue
- **Catches**: LLM creative expansion that hallucinates extra components beyond what's in the bound chunks

### `SCOPE_DRIFT_MIN_ACTUAL = 20`

- **File**: `chunk-synthesizer.js`
- **Floor against false positives** on small UIs where slot-wrapper noise dominates. UIs with < 20 components don't trip the gate even if the ratio exceeds 1.5×.

### `DEFAULT_MAX_ATTEMPTS = 2`

- **Files**: `chunk-refiner.js`, `chunk-synthesizer.js`
- **Validator-driven retry budget**. After 2 failed validations, emit `synthesis-failed` strategy.

### `DEFAULT_MAX_SIZE = 64` (state-cache)

- **File**: `state-cache.js`
- **Override**: `A2UI_STATE_CACHE_SIZE` env var
- **Per-process, in-memory.** Survives only as long as the MCP server. Multi-turn refinement breaks across server restarts.
- **Eviction**: LRU on `set` when at capacity; `get` and overwriting `set` touch recency; `peek` reads without touching.

### `TRACE_INLINE_THRESHOLD_BYTES = 200 * 1024` (issue-reporter)

- **File**: `issue-reporter.js`
- Above this, traces spill to sidecar `.trace.json` next to the issue JSON to keep the issue file readable.

## The locator → modifier two-pass pattern (chunk-refiner.js)

Multi-turn refinements use **two LLM passes**:

### Pass 1 — Locator

LLM is given:

- The intent ("change the title", "remove the funnel", "add a country list")
- A component map listing slots in the prior UI + their bound chunks

LLM classifies the intent as:

- **`targeted`** — specific slot/element named, OR verb implies localized change
- **`untargeted`** — broad changes touching many slots ("more compact", "use teal")

### Pass 2 — Modifier

LLM emits ops from a fixed vocabulary:

```text
VALID_OP_TYPES = { rebindSlot, appendToSlot, removeFromSlot, replacePage }
```

Ops translate to A2UI `updateComponents` messages via `opsToA2UI()`.

**Phase A simplification**: refinements operate on the chunk binding plan only. A later phase may introduce component-tree refinements; current code honors the wire format while keeping engine code chunk-focused.
