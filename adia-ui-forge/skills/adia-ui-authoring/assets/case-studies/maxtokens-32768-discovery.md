# Case study — Mode 6: `maxTokens: 32768` discovery

**Scenario:** [llm-bridge.md](../../references/llm-bridge.md) § Rule 1 — defaults that bit us **Source:** silent-fallback diagnosis in the LLM bridge; commit history at `packages/llm/llm-bridge.js` **Outcome:** A2UI generation for moderately complex UIs was silently truncated at 8k tokens; the validator rubber-stamped incomplete trees at ~89/100. Raised the bridge default to 32768; surfaced `stopReason` as Rule 3.

---

## §The shape

The `@adia-ai/llm` bridge (`packages/llm/llm-bridge.js`) shipped with a default `maxTokens: 8192` — the conservative default common to provider docs. `complete()` and `stream()` both used it.

The A2UI synthesis pipeline (`packages/a2ui/compose/`) generated UI JSON from intent. For simple intents — "a sign-up form," "a settings panel" — output fit comfortably under 4k. For moderately complex intents — "a kanban board with 4 columns," "a SaaS dashboard with 6 KPI cards + a chart," "a pricing tier table with 3 plans" — the JSON regularly approached or exceeded 8k.

The validator scored every output. Reported scores were `~89/100`. Generation looked healthy. Eval coverage looked stable.

Then a consumer complained: "the kanban came back missing the last column."

---

## §The diagnosis

Inspecting the truncated JSON: it ended mid-object, mid-string, with no closing brace. The validator's score-89 was a **lenient fallback**: when JSON parsing failed, the synthesizer wrapped the partial output in a generic shell template and the validator scored _that template_, not the broken JSON.

The bridge wasn't propagating the truncation signal. Each provider's response carried a `stopReason` (`'max_tokens'` for Anthropic + Gemini's `'MAX_TOKENS'`, `'length'` for OpenAI) — but the bridge was normalizing all values to `'end'` and the downstream synthesizer never saw the truncation indicator.

So the failure mode was:

1. Bridge default `maxTokens: 8192` cuts the model off mid-output.
2. Bridge normalizes upstream `stopReason: 'max_tokens'` to `'end'`.
3. Synthesizer attempts JSON.parse → throws.
4. Synthesizer falls back to "render a generic shell + warn."
5. Validator scores the generic shell at ~89/100.
6. Eval pipeline reports healthy coverage.

Three independent bugs compounded into a silent regression. The generator looked fine until a consumer counted columns.

---

## §The fix

### Rule 1 graduate — `maxTokens: 32768` is intentional

`llm-bridge.js` was bumped from `8192` to `32768`:

```js
// llm-bridge.js — complete() and stream() both pass this default
const opts = {
  maxTokens: 32768,           // not configurable from caller for synthesis
  temperature,
  cache: this.#provider === 'anthropic',
  // ...
};
```

32k is the model output ceiling for current Anthropic models (Sonnet + Haiku 4.5). Don't lower this. A2UI JSON for kanban / dashboard / pricing-tier outputs ranges 4-16k typically; 32k gives ~2x headroom.

If adding a new provider with a lower output ceiling (e.g. an older model with 4k output limit), surface it as a **model-level constraint in `MODELS`**, don't bypass the bridge default.

### Rule 3 graduate — `stopReason` must propagate raw

The bridge stopped normalizing. Both `complete()` and `stream()`'s terminal `done` chunk now surface the raw upstream value:

```js
yield { type: 'done', text, usage, stopReason: rawStopReason };
```

Downstream synthesizer (`packages/a2ui/compose/...`) checks for truncation-indicating values:

```js
const TRUNCATED = new Set(['max_tokens', 'length', 'MAX_TOKENS']);
if (TRUNCATED.has(chunk.stopReason)) {
  throw new TruncationError(`output truncated by upstream (${chunk.stopReason})`);
}
```

**Don't normalize all values to `'end'`** — the generator's truncation detector reads them raw. This is now Rule 3 in [llm-bridge.md](../../references/llm-bridge.md).

### Validator hardened

The validator was patched to refuse silent fallback rendering when `stopReason` indicates truncation. The 89/100 silent-pass became an `INCOMPLETE: truncated by upstream` hard fail. Eval coverage dropped ~12pp the day the patch landed — surfacing the previously-hidden generation gap.

---

## §The verification

After the 3 patches:

- `npm run smoke:engines` — green (complex intents now succeed end-to-end)
- `npm run test:a2ui` — passing (truncation-test cases added — artificially low `maxTokens` should produce `TruncationError`, not a 89/100 false-positive)
- Real-LLM eval at `eval:diff` — coverage dropped from reported ~95% to the honest ~83%, then recovered to ~88% as corpus + prompts matured. Honest numbers across all subsequent rebaselines.
- Kanban-intent + dashboard-intent + pricing-tier-intent — all now emit complete JSON without truncation.

---

## §The lesson

Three things graduated from this arc:

1. **Silent fallbacks compound.** Truncation + stopReason normalization + generic-shell fallback + validator scoring stacked into a silent 12pp coverage lie. Every layer in a pipeline must surface failure honestly — generic fallbacks should fail-loud, not fail-friendly.
2. **`maxTokens` ≠ "token budget."** Consumers think of `maxTokens` as "how big can the output be." The truth is it's "where the model will be cut off if it tries to keep going." Set it as generously as the model allows; surface model-level constraints separately if a specific model has a lower ceiling.
3. **Provider-specific terminal values matter.** Anthropic / Gemini / OpenAI all use different stopReason strings (`max_tokens` vs `MAX_TOKENS` vs `length`). Normalizing them throws away information. The bridge surfaces them raw; the consumer maps them to behavior.

Rule 1 (`maxTokens: 32768`) + Rule 3 (`stopReason` propagates raw) + the lazy-load adapter Rule 4 (caught later — `node:fs` imports break SSR consumers) are now the 5 hard rules in [llm-bridge.md](../../references/llm-bridge.md) § Hard rules — defaults that bit us.

## §Cross-references

- [llm-bridge.md](../../references/llm-bridge.md) § Rule 1 (`maxTokens: 32768` is intentional) + Rule 3 (stopReason must propagate)
- `packages/llm/llm-bridge.js` — the bridge with the now-correct default
- `packages/llm/adapters/anthropic.js` / `openai.js` / `gemini.js` — each adapter's `parseStream` surfaces the raw provider-specific `stopReason`
- Spec: `docs/specs/package-architecture.md` § 11 (Phase 5 — engine registry; `@adia-ai/llm` is the 9th lockstep package, leaf-shaped, no internal deps)
