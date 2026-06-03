# Add a provider — mode 1

The end-to-end recipe for a 4th provider adapter (DeepSeek, Mistral, Cohere, an OpenAI-compatible gateway, …). Grounded in the existing three adapters under `packages/llm/src/adapters/` and the facade `packages/llm/src/adapters/index.ts`. Read `adapter-contract.md` first — this recipe wires the contract it defines.

Adding a provider is **additive** to the public surface (a new adapter, a new `MODELS` group, a new `detectProvider` branch). It does not break existing consumers if you follow the contract.

---

## Decide first: is this OpenAI-compatible?

Many providers (Groq, Together, Mistral, any OpenAI-compatible gateway) speak the OpenAI Chat Completions wire format. `openai.ts` already notes this. If the new provider is OpenAI-compatible, you may not need a new adapter at all — you may only need a `detectProvider` branch and a base-URL override. A genuinely new wire format (different request body, different SSE event shape) needs a new adapter. Confirm against the provider's API docs before writing code.

## Step 1 — write the adapter

Create `packages/llm/src/adapters/<name>.ts` exporting one `const` matching the contract (model on `anthropic.ts`):

- `name: '<name>' as const`.
- `buildRequest(opts: BuildRequestOpts): AdapterRequest` — return `{ url, headers, body }`. Set the auth header the provider expects. Map `opts.system`, `opts.messages`, `opts.maxTokens` (default to the package's `32768` unless the provider's ceiling is lower), `opts.temperature`, and the `stream` flag into the provider's body shape.
- `parseResponse(json): AdapterResponse` — map to `{ text, usage: { input, output }, stopReason }`. Pass `stopReason` through RAW (don't normalize).
- `parseStream(response): AsyncGenerator<StreamChunk>` — guard `response.body`, consume `readSSE` from `./sse.js`, accumulate `snapshot` + `usage`, yield `text` deltas with the running `snapshot`, and yield exactly one terminal `done`.

`import type { AdapterRequest, AdapterResponse, AdapterUsage, StreamChunk, BuildRequestOpts } from './anthropic.js';` — reuse the canonical types; don't redeclare them.

## Step 2 — register in the facade

Edit `packages/llm/src/adapters/index.ts`:

```text
import { myprovider } from './myprovider.js';
const providers = { anthropic, openai, gemini, myprovider } as const;
```

Then add a `detectProvider` branch so model ids route without an explicit `provider`:

```text
if (m.includes('<id-substring>') || m.startsWith('<name>/')) return 'myprovider';
```

Support both conventions — a substring (`m.includes(...)`) and a `provider/model` prefix (`m.startsWith('<name>/')`) — to match how the existing branches behave (see `model-registry.md`).

## Step 3 — subpath export (usually automatic)

`package.json` already has `"./adapters/*"` as a glob export, so `@adia-ai/llm/adapters/<name>` resolves without an edit. Only add a named subpath (like `./bridge` / `./models`) if you want a stable short import.

## Step 4 — add to the model registry

Edit `packages/llm/src/models.ts` — add a `ModelGroup`:

```text
{ label: 'MyProvider', options: [ { value: '<model-id>', label: '<display name>' } ] }
```

Keep the `[{ label, options: [{ value, label }] }]` shape exactly (the `<chat-input-ui>` setter depends on it). The `value` must be a model id your Step 2 `detectProvider` branch classifies. Don't change `DEFAULT_MODEL` to the new provider unless you intend a default switch (keep it cheap/fast).

## Step 5 — wire the bridge default + browser route (if browser-routable)

Edit `packages/llm/src/llm-bridge.ts`:

- Add `myprovider: '<default-model-id>'` to `DEFAULT_MODELS` (the per-provider fallback `createAdapter()` uses when no model is supplied — distinct from `models.ts`'s `DEFAULT_MODEL`; see `model-registry.md`).
- If the provider should work in the browser, add a `resolveBaseUrl` entry whose path is `/api/llm/<name>/...` so it matches the passthrough regex (see `browser-proxy-boundary.md`). The deployed app's same-origin proxy must have a matching route that injects the server-side key.

## Step 6 — caching + thinking (only if the provider supports them)

`BuildRequestOpts.cache` and `thinking` are currently Anthropic-shaped. Leave `cache` ignored unless the provider has its own prompt-cache mechanism — then add a parallel branch in your `buildRequest` and surface the cache fields in `parseResponse`/`parseStream`. Same for `thinking`: only emit a `{ type: 'thinking', text }` chunk if the provider streams reasoning deltas (OpenAI does, via `delta.reasoning_content`; Gemini does not).

## Step 7 — verify against the real provider

This is the mode-1 verify target. Do not declare done on a clean compile alone:

1. `npm run build` (`tsc --build`) — the new adapter compiles with no type error against the shared types.
2. A real `chat({ provider: 'myprovider', apiKey: '<key>', model: '<model-id>', messages: [...] })` returns non-empty `text` and a sane `usage` (`input`/`output` > 0) and a raw `stopReason`.
3. A real `streamChat(...)` shows ordered `text` deltas with a growing `snapshot`, a terminal `done` carrying final `usage`, and an `error` chunk on a forced failure (bad key).
4. `detectProvider('<model-id>')` returns `'myprovider'` (auto-detection works with no explicit provider).
5. Run `node scripts/audit-llm-roster.mjs --strict` — the provider-roster axis recognizes the new adapter once it's wired into the menu/posture.

## Worked example — adding an OpenAI-compatible gateway

A gateway that speaks the OpenAI wire format with a different base URL and a `gw-` model prefix.

1. Plan: verify target is a real `chat()` against the gateway returning text, plus `detectProvider('gw-fast')` resolving it.
2. Execute: since it's OpenAI-compatible, the cheapest path is to add a `detectProvider` branch (`m.startsWith('gw-')` → a provider key) and reuse the OpenAI body shape with a base-URL override; if the base URL must differ per call, route via `proxyUrl`/smart proxy rather than hardcoding. Add a `MODELS` group + a `DEFAULT_MODELS` entry.
3. Verify: `npm run build`; `chat()` returns text; streaming yields a terminal `done`; `audit-llm-roster --strict` is clean.

## Cross-references

- [adapter-contract.md](adapter-contract.md) — the three-method object + the `usage` / `stopReason` mapping this recipe implements
- [streaming-sse.md](streaming-sse.md) — the `StreamChunk` protocol the new `parseStream` must satisfy
- [model-registry.md](model-registry.md) — the `MODELS` group + `detectProvider` branch
- [browser-proxy-boundary.md](browser-proxy-boundary.md) — the `resolveBaseUrl` entry + passthrough regex
- [bridge-facade.md](bridge-facade.md) — `DEFAULT_MODELS` and the lazy-load gate
