# Bridge + facade + stub — modes 5 and 7

The three public entry layers above the adapters. Source: the facade `packages/llm/src/adapters/index.ts` (`chat` / `streamChat` / `createClient` + types), the bridge `packages/llm/src/llm-bridge.ts` (`createAdapter` → `AdiaUILLMBridge`), the stub `packages/llm/src/llm-stub.ts` (`StubLLMAdapter`), and the barrel `packages/llm/src/index.ts`.

This reference covers mode 5 (the facade/bridge contract) and mode 7 (the stub). The proxy-flavor mechanics are in `browser-proxy-boundary.md`.

---

## The public barrel — what `@adia-ai/llm` exports

`index.ts` re-exports exactly four things; this is the package's public API surface:

```text
export { chat, streamChat, createClient } from './adapters/index.js';
export { MODELS, DEFAULT_MODEL }          from './models.js';
export { StubLLMAdapter }                 from './llm-stub.js';
export { createAdapter }                  from './llm-bridge.js';
```

Subpath exports (`package.json` `exports`): `.` (the barrel), `./adapters/*` (each adapter, glob), `./bridge`, `./models`, `./stub`. The `./adapters/*` glob means **a new adapter file is exported automatically** — no `package.json` edit needed unless you want a named subpath.

## Layer 1 — the standalone facade (`chat` / `streamChat`)

`chat(opts: ChatOpts): Promise<ChatResult>` and `streamChat(opts): AsyncGenerator<StreamChunk>` are the provider-agnostic functions. Both follow the same arc in `index.ts`:

1. `resolveAdapter(opts)` — uses `opts.provider` or `detectProvider(opts.model)`; throws if neither resolves (see `model-registry.md`).
2. Build the request: if `opts.proxyUrl` is set, branch on `isPassthroughProxy(proxyUrl)` (passthrough vs smart proxy — see `browser-proxy-boundary.md`); otherwise call `adapter.buildRequest({ ...opts, stream })` directly.
3. `fetch(url, { method: 'POST', headers, body: JSON.stringify(body), signal })`.
4. On `!res.ok`: `chat` throws `Error(err.error.message || '<adapter> API error <status>')`; `streamChat` yields an `error` chunk instead of throwing.
5. `chat` returns `adapter.parseResponse(json)`; `streamChat` delegates to `adapter.parseStream(res)`.

`ChatOpts` (the input) and `ChatResult` (the output) are declared in `index.ts`:

```text
ChatOpts   = { model; messages; apiKey; provider?; system?; maxTokens?; temperature?;
               stream?; thinking?; thinkingBudget?; signal?; proxyUrl?; cache? }
ChatResult = { text: string; usage: AdapterUsage; stopReason: string }
```

`ChatResult` is structurally identical to `AdapterResponse` — the facade returns the adapter's parsed response unchanged. **Changing `ChatOpts` / `ChatResult` is a breaking change for every consumer**; adding an optional `ChatOpts` field is additive.

## Layer 1b — `createClient` (reusable instance with defaults)

`createClient(defaults: Partial<ChatOpts> = {}): LLMClient` returns `{ chat, stream }` that merge `defaults` under each call's opts (`{ ...defaults, ...opts }`). The merge is shallow and call-opts-win. Use it to bake in `provider` + `apiKey` + `proxyUrl` once. `LLMClient` is the interface the bridge wraps.

## Layer 2 — the bridge (`createAdapter` → `AdiaUILLMBridge`)

`llm-bridge.ts` adapts the facade to the adia-ui pipeline's simpler interface. The pipeline calls `adapter.complete({ messages, systemPrompt })` and `adapter.stream({ messages, systemPrompt })`; the bridge translates to the facade's `chat({ model, messages, system, … })`.

`createAdapter(opts): Promise<StubLLMAdapter | AdiaUILLMBridge>` (async):

- Resolves `provider` from `opts.provider` / `LLM_PROVIDER` env / `detectProvider()`; resolves the model from `opts.model` / `LLM_MODEL` env / per-provider `DEFAULT_MODELS`.
- Reads the API key from `opts.apiKey` or the provider's `*_API_KEY` env var (with Anthropic/OpenAI/Google fallbacks).
- **No key → returns `StubLLMAdapter`** (with a console warning). Key present → builds a real bridge.
- Lazy-loads the adapters via `getCreateClient()` — see "Lazy-load gate" below.

The `AdiaUILLMBridge` class re-shapes both directions:

- **`complete()`** calls `chat()` with `maxTokens: 32768` and `cache: provider === 'anthropic'`, then returns `{ content, stopReason, usage: { inputTokens, outputTokens, cacheCreationTokens, cacheReadTokens } }` — note the field rename from the facade's `usage.input` to the pipeline's `usage.inputTokens`.
- **`stream()`** iterates `client.stream()`, re-emits `text` chunks as `{ type: 'text', content }`, and re-emits `done` as `{ type: 'done', stopReason, usage: {…Tokens} }`. Chunk types it doesn't consume (`thinking`, `error`) fall through silently — when you add a chunk type, decide whether the bridge should surface it.

### The `maxTokens: 32768` default is intentional — don't lower it

Both `complete()` and `stream()` hardcode `maxTokens: 32768`. A2UI JSON for moderately complex UIs (kanban, dashboard, pricing table) routinely exceeds 8k; an 8k cap produced silent truncation that the validator rubber-stamped at ~89/100. The adapters' own `DEFAULT_MAX_TOKENS` (Anthropic + Gemini) is also `32768`. If a new provider has a lower output ceiling, surface it as a model-level constraint in `MODELS` — **do not lower the 32k bridge default**.

### Lazy-load gate — don't break Node/SSR consumers

`createAdapter` reaches the adapters through `getCreateClient()`, which `await import('./adapters/index.js')` inside a `try`/`catch` (falling back to the stub on failure) and memoizes the result. This is load-bearing: `llm-bridge.ts` is browser/SSR-facing, and a top-level static import of the adapters can throw at module-load time in pure-Node contexts (Vite-alias / `node:` resolution). **If you add a module under `adapters/` that imports `node:` builtins, keep the lazy gate intact** — top-level imports break SSR.

## The stub — `StubLLMAdapter` (mode 7)

`llm-stub.ts` is the deterministic, no-API-key adapter pipeline code develops against. It mirrors the bridge's interface — `complete({ messages, systemPrompt })` and `async *stream(request)` — so consumers swap it in transparently.

Contract the stub must keep:

- **`complete()` returns parseable A2UI.** It builds a canned component tree and returns `{ content: JSON.stringify([{ type: 'updateComponents', surfaceId: 'default', components }]), usage: { inputTokens, outputTokens } }`. The `content` must stay valid A2UI JSON or pipeline parsing breaks.
- **`stream()` yields the same content as one `text` chunk.** It calls `complete()` and yields `{ type: 'text', content: result.content }` — a single chunk that simulates streaming.
- **`usage` is a rough estimate.** `estimateTokens` is `~chars/4`; it's deterministic, not exact, and that's fine — the stub exists for offline development, not telemetry fidelity.

The stub's `complete()` result shape (`{ content, usage: { inputTokens, outputTokens } }`) matches the bridge's `complete()` minus the cache fields — keep them aligned when the bridge's shape changes so the stub stays a drop-in.

## Worked example — `createAdapter()` returns the stub when a key IS set

1. Plan: verify target is a `createAdapter({ provider: 'anthropic', apiKey: '<real>' })` returning an `AdiaUILLMBridge` whose `.provider === 'anthropic'`, and `complete()` returning real `content`.
2. Execute: trace `createAdapter` — `provider !== 'stub'` so it resolves the key; if the key is falsy it warns and returns the stub. Check the env-var path (`<PROVIDER>_API_KEY` then the Anthropic/OpenAI/Google fallbacks) and confirm `getCreateClient()` didn't fall back to `null` (lazy import failed → stub).
3. Verify: with a real key, `createAdapter` returns a bridge (not a stub), `complete()` returns provider text, and `usage.cacheCreationTokens` / `cacheReadTokens` are populated for Anthropic.

## Cross-references

- [adapter-contract.md](adapter-contract.md) — what `resolveAdapter` / `buildRequest` / `parseResponse` do
- [browser-proxy-boundary.md](browser-proxy-boundary.md) — the `proxyUrl` dispatch and the production-host stub path
- [model-registry.md](model-registry.md) — `DEFAULT_MODEL` vs the bridge's `DEFAULT_MODELS`
- [streaming-sse.md](streaming-sse.md) — the `StreamChunk` union the bridge re-shapes
- Source: `packages/llm/src/adapters/index.ts`, `packages/llm/src/llm-bridge.ts`, `packages/llm/src/llm-stub.ts`, `packages/llm/src/index.ts`
