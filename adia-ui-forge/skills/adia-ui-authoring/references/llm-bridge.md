# LLM Bridge extension — Mode 6

Use when adding a 4th provider, modifying `createAdapter()`, changing the streaming chunk shape, or extending `packages/llm/server.js`.

This reference is about **modifying** the package. For day-to-day consumption (import + call), the README at `packages/llm/README.md` is sufficient.

Absorbed from the legacy `llm-bridge-extension` skill (folded earlier into the code-bestpractices content, now into `adia-ui-authoring` mode 6).

---

## When to use

- Adding a new provider adapter (e.g., DeepSeek, Cohere, Mistral)
- Changing `maxTokens`, `temperature`, or another bridge default
- Extending the streaming chunk type set (currently: `text` / `thinking` / `done` / `error`)
- Adding a new endpoint to `packages/llm/server.js`
- Modifying the bridge's `complete()` / `stream()` shape
- Debugging "why does my LLM call return truncated JSON?"

## When NOT to use

- Just calling the LLM → `import { chat, streamChat } from '@adia-ai/llm'`
- A2UI pipeline integration → use `@adia-ai/llm/bridge` as-is
- Testing pipeline code without API keys → use `StubLLMAdapter` from `@adia-ai/llm/stub`

## Architecture (memorize before extending)

```text
@adia-ai/llm (9th lockstep package, leaf-shaped, no internal deps)

├── adapters/index.js     ← Layer 1: chat() + streamChat() facade
│   ├── anthropic.js      ← Each adapter: { name, buildRequest, parseStream }
│   ├── openai.js
│   ├── gemini.js
│   └── sse.js            ← shared SSE parser
│
├── llm-bridge.js         ← Layer 2: createAdapter() → AdiaUILLMBridge
│                            (lazy-loads adapters/index.js to dodge Vite aliases)
│
├── llm-stub.js           ← StubLLMAdapter (no API calls, deterministic)
├── models.js             ← MODELS catalog + DEFAULT_MODEL (chat-input-ui shape)
└── server.js             ← Local proxy + static server (NOT shipped to npm)
```

## Hard rules — defaults that bit us

### Rule 1: `maxTokens: 32768` is intentional

The bridge hardcodes `maxTokens: 32768` in `complete()` and `stream()`. **Don't lower this.**

A2UI JSON for moderately complex UIs (kanban, dashboard, pricing tier table) routinely exceeds 8k. An 8k truncation was discovered producing silent fallbacks the validator rubber-stamped at ~89/100 — the generator looked healthy but was emitting incomplete component trees.

If you're adding a new provider that has a lower maxTokens ceiling (e.g., a model with 4k output limit), surface it as a model-level constraint in `MODELS`, **don't bypass the 32k bridge default**.

### Rule 2: Anthropic prompt caching is auto-enabled

The bridge passes `cache: this.#provider === 'anthropic'`. This marks the ~23KB AdiaUI system prompt as a cache breakpoint (ephemeral, ~5min TTL).

- First call in window: cache write (+25% cost)
- Subsequent calls: cache read (−90% cost)
- Below provider's minimum cacheable size (1024 tok Sonnet/Opus, 2048 Haiku): no-op
- Other providers silently ignore the unknown opt

When adding a new provider, leave `cache` falsy unless that provider has its own caching mechanism — then add a parallel `case` in the adapter's `buildRequest`.

### Rule 3: stopReason must propagate

The bridge surfaces `stopReason` from the upstream response in both `complete()` and `stream()`'s terminal `done` chunk. Values:

- `'end'` / `'stop'` / `'STOP'` — clean completion
- `'max_tokens'` / `'length'` / `'MAX_TOKENS'` (Gemini) — **truncation**
- `'tool_use'` / `'tool_calls'` — tool-call paused output
- `'error'` — provider-side error

**Downstream parser refuses silent fallback rendering when stopReason indicates truncation.** Don't normalize all values to `'end'` — the generator's truncation detector reads the raw value.

### Rule 4: lazy-load adapters in browser-facing modules

`llm-bridge.js` lazy-loads `./adapters/index.js`:

```js
let _createClient = null;
async function getCreateClient() {
  if (!_createClient) {
    try {
      const mod = await import('./adapters/index.js');
      _createClient = mod.createClient;
    } catch {
      _createClient = null;  // fall back to stub
    }
  }
  return _createClient;
}
```

**Reason**: `adapters/index.js` transitively reaches `node:fs` / `node:path` constructs (via Vite's externalize behavior) that throw at module load time in pure-Node contexts without aliases. Top-level static imports break SSR / Node-script consumers.

If you add a new module under `adapters/` that imports `node:` builtins, keep the lazy-load gate intact.

### Rule 5: `server.js` is NOT shipped to npm

`package.json:files` excludes `server.js`. It's a local dev / visual-eval convenience. Production consumers deploy their own proxy.

If you add a new endpoint, document it in the npm README under "Browser proxy mode" but **don't promise it as a published API**.

## How to add a 4th provider

### Step 1: Create the adapter

`packages/llm/adapters/<name>.js` exports a single object matching the shape used by anthropic / openai / gemini:

```js
import { readSSE } from './sse.js';

export const myProvider = {
  name: 'myprovider',
  buildRequest(opts) {
    return {
      url: 'https://api.example.com/v1/chat',
      headers: { 'content-type': 'application/json', 'x-api-key': opts.apiKey },
      body: { model: opts.model, messages: opts.messages, stream: opts.stream },
    };
  },
  async *parseStream(response) {
    for await (const event of readSSE(response.body)) {
      // yield { type: 'text', text, snapshot } | { type: 'done', text, usage, stopReason }
    }
  },
  parseResponse(json) {
    // returns { text, usage: { input, output }, stopReason }
  },
};
```

### Step 2: Register in the facade

Edit `packages/llm/adapters/index.js`:

```js
import { myProvider } from './myprovider.js';
const providers = { anthropic, openai, gemini, myprovider: myProvider };

function detectProvider(model) {
  // ...existing branches
  if (m.includes('myprovider-prefix') || m.startsWith('myprovider/')) return 'myprovider';
  return null;
}
```

### Step 3: Subpath export

Edit `packages/llm/package.json`:

```json
"exports": {
  ".": "./index.js",
  "./adapters/*": "./adapters/*.js",
  ...
}
```

The `./adapters/*` glob already covers new files — no edit needed unless you want a named subpath.

### Step 4: Update `models.js` catalog

Add a new group:

```js
export const MODELS = [
  ...,
  {
    label: 'MyProvider',
    options: [
      { value: 'myprovider-flagship', label: 'Flagship' },
    ],
  },
];
```

### Step 5: Wire Vite proxy (browser dev)

Edit `vite.config.*`:

```js
'/api/llm/myprovider': {
  target: 'https://api.example.com',
  changeOrigin: true,
  rewrite: (path) => path.replace(/^\/api\/llm\/myprovider/, ''),
}
```

### Step 6: Wire `server.js` (visual-eval proxy)

Add a `PROVIDERS.myprovider` config block matching anthropic / openai / gemini's shape (`url`, `keyEnv`, `buildHeaders`, `buildBody`).

### Step 7: Bridge default model

Edit `llm-bridge.js`:

```js
const DEFAULT_MODELS = {
  anthropic: 'claude-sonnet-4-20250514',
  openai: 'gpt-4o',
  google: 'gemini-2.0-flash',
  myprovider: 'myprovider-flagship',
};
```

### Step 8: Test surface

Run the smoke tests against the new provider:

```bash
MYPROVIDER_API_KEY=*** node packages/a2ui/mcp/scripts/smoke-engine-registry.mjs
```

Then run real-LLM eval at low intent count:

```bash
LLM_PROVIDER=myprovider node packages/a2ui/mcp/scripts/eval-diff.mjs --semantic
```

## Pitfalls

- **Two proxy shapes — `proxyUrl` is overloaded.** The bridge supports two architecturally different proxies and the dispatcher in `packages/llm/adapters/index.js` chooses between them by URL shape. Get this wrong and you get silent 401s in the browser even though `node packages/llm/server.js` works fine.
  - **Smart proxy** (`packages/llm/server.js`, route `POST /api/chat`): accepts a **provider-neutral body** `{ provider, model, messages, ... }`, holds the API key server-side, and dispatches internally to the right adapter. Headers are just `content-type: application/json`.
  - **Passthrough proxy** (Vite dev `/api/llm/<provider>/<rest>` → real upstream URL `https://api.<provider>.com/<rest>`): expects the **real upstream body shape** (Anthropic-shaped for `/anthropic/`, OpenAI-shaped for `/openai/`, etc.) plus the **adapter's own auth headers** (`x-api-key` + `anthropic-version`, or `Authorization: Bearer …`). The proxy is dumb — it just rewrites the URL and forwards bytes.
  - Dispatcher: `chat()` and `streamChat()` in `adapters/index.js` call `isPassthroughProxy(proxyUrl)` (regex `/\/api\/llm\/[a-z]+(\/|$)/`). If true, they call `passthroughRequest()` which builds the real upstream body via `adapter.buildRequest()` then swaps in `proxyUrl`. If false, they call `proxyRequest()` with the provider-neutral body.
  - **When adding a new provider**, make sure: (1) `buildRequest()` omits the API key header when `proxyUrl` is the smart proxy (already handled), (2) `buildRequest()` _includes_ the API key header when called from `passthroughRequest()` (also already handled — passthroughRequest forwards adapter headers). The adapter's `buildRequest()` is the single source of truth for upstream-shape body + headers. Don't fork it for proxy mode.
- **Don't add `apiKey` to the proxy body**. The proxy holds the key server-side. Adapter's `buildRequest` should set the API-key header only when `proxyUrl` is unset (i.e., direct mode).
- **Don't normalize `stopReason`**. Each provider uses different terminal values (`max_tokens` vs `length` vs `MAX_TOKENS`); the truncation detector reads them raw.
- **Don't import the package from itself.** `index.js` re-exports from `./adapters/index.js`; consumers inside the package reference relative paths to dodge the package-name resolution loop.
- **`MODELS` is consumed by `<chat-input-ui>`** — its shape is `[{ label, options: [{ value, label }] }]` matching `<select-ui>` with `<optgroup>`s. Don't deviate from this shape or 3 apps break.
- **`DEFAULT_MODEL` is the cheapest option** — resist the urge to default to a flagship model — most consumers want fast/cheap by default.

## Verification gates

After any extension:

```bash
npm run check:lockstep         # @adia-ai/llm version must match the others
npm run smoke:engines          # engines still register; pick still works
npm run test:a2ui              # 22 pass / 0 fail / 1 skipped
node packages/llm/server.js    # boots cleanly; .env auto-loads
```

If you added a new SSE chunk type to the streaming protocol, verify all 7 consumers (chat-shell, generator.js, synthesis.js, eval-chunk-synthesis, eval-refine-synthesis, playgrounds/chat, apps/genui) still handle it correctly or fall through gracefully.

## Cross-references

- [code-style.md](code-style.md) — general AdiaUI conventions (this is a specialty path; start there if you need broader context)
- **adia-ui-a2ui** (sibling skill) — generator / MCP / zettel synthesis (consumes the bridge)
- Spec: `docs/specs/package-architecture.md` § 11 (Phase 5 — engine registry)
- README: `packages/llm/README.md` — consumer-facing docs
