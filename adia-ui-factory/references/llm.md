# LLM features with `@adia-ai/llm`

Wiring chat / streaming / AI features into an app. This is **app-level LLM use** — distinct from _generating UI markup_, which is the a2ui MCP's `generate_ui` (see the boundary at the end). All of the below is from the framework's own `@adia-ai/llm` package.

> **Snapshot, not a spec.** The exact signatures, `StreamChunk` field names, and `<chat-shell-ui>` API below are verified against `@adia-ai/llm` **v0.7.8** (the pinned MCP's sibling). LLM client APIs drift fast — treat precise names as a starting point, confirm against the installed version, and lean on the **smart-proxy contract** (stable) rather than memorizing fields.

## Import & the core API

```js
import { chat, streamChat, createClient } from '@adia-ai/llm';
import { MODELS, DEFAULT_MODEL } from '@adia-ai/llm/models';
```

- `chat(opts) → Promise<{ text, usage, stopReason }>` — non-streaming.
- `streamChat(opts) → AsyncGenerator<StreamChunk>` — streaming; `for await` the chunks.
- `createClient(defaults) → { chat, stream }` — a client with baked-in defaults.

`ChatOpts` (the fields you'll actually use): `model`, `messages: [{role, content}]`, `provider?` (auto-detected from the model name), `system?`, `maxTokens?`, `temperature?`, `stream?`, `signal?` (AbortSignal), `proxyUrl?`, plus Anthropic extras `thinking?` / `cache?`.

`StreamChunk` is a tagged union — branch on `chunk.type`:

```js
for await (const chunk of streamChat(opts)) {
  if (chunk.type === 'text')     append(chunk.text);            // also has .snapshot (full text so far)
  else if (chunk.type === 'thinking') showThinking(chunk.text); // Anthropic extended thinking
  else if (chunk.type === 'done')     finalize(chunk.usage, chunk.stopReason);
  else if (chunk.type === 'error')    fail(chunk.error);
}
```

## Providers

Anthropic, OpenAI, and Gemini, **auto-detected from the model name** (`claude*` → anthropic, `gpt*`/`o1*` → openai, `gemini*` → google). Override with `provider`. Keys are read server-side from `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` / `GOOGLE_API_KEY`.

## The proxy / security model — read this first

**Never ship a provider API key to the browser in production.** `@adia-ai/llm` supports two proxy shapes, auto-selected by the `proxyUrl`:

- **Smart proxy (production):** point `proxyUrl` at your own same-origin endpoint (e.g. `/api/chat`). The browser sends a provider-neutral body (`{provider, model, messages, …}`); **your server** holds the real key, reformats per provider, and pipes the SSE bytes back. The browser never sees a key.

  ```js
  for await (const c of streamChat({ proxyUrl: '/api/chat', model, messages })) { … }
  ```

  A reference server lives at `@adia-ai/llm`'s `server.js` (`POST /api/chat`).

- **Passthrough proxy (LOCAL DEV ONLY):** a `proxyUrl` matching `/api/llm/<provider>/…` (e.g. a Vite dev proxy). The browser sends the real upstream body **and the real key in headers** — anyone with DevTools can read it. The package logs a loud one-time warning. **Never deploy this shape.**

When authoring: default to the smart-proxy pattern; only use passthrough behind a Vite dev proxy, and say so explicitly.

## The chat shell

`<chat-shell-ui>` is a behavior-only web-module that renders a chat surface and wires it to `streamChat` for you:

```html
<chat-shell-ui proxy-url="/api/chat" model="claude-sonnet-4-6">
  <chat-header><span slot="name">Assistant</span><chat-status slot="status"></chat-status></chat-header>
  <chat-thread><chat-empty><empty-state-ui heading="Hello!"></empty-state-ui></chat-empty></chat-thread>
  <chat-composer><chat-input-ui placeholder="Message…"></chat-input-ui></chat-composer>
</chat-shell-ui>
```

- **Properties:** `model`, `provider`, `proxyUrl`, `system`, `thinking`, `streaming`.
- **Events:** `submit`, `chunk`, `thinking`, `done`, `error`, `abort`, `message`, `clear`.
- **Methods:** `send(text, {model})`, `appendMessage(...)`, `clear()`, `abort()`; accessors `messages` / `conversation` / `export` / `import(...)`.

Set `proxy-url` (or, dev-only, an `apiKey`) and it auto-sends on submit; otherwise it just emits `submit` for you to handle. For SSR, register it client-side like any other component (see `ssr-integration.md`).

## Boundary: app LLM vs. UI generation

Two separate paths — don't conflate them:

- **`@adia-ai/llm`** — a generic chat/streaming client for _your app's_ AI features (a chat box, a summarize button). Knows nothing about A2UI.
- **a2ui MCP `generate_ui`** — turns an intent into A2UI component markup (retrieval-first, LLM fallback). Use it to _build UI_, then `validate_schema` / `check_anti_patterns` (see `a2ui-mcp-tools.md`).
- The bridge (`createAdapter` from `@adia-ai/llm/bridge`) is what the A2UI generation pipeline uses internally to call an LLM for that fallback — you rarely call it directly.

## Not in the package (don't assume)

Tool/function-calling chunks, structured-output/JSON-schema modes, built-in retry/backoff, and client-side token estimation are **not** surfaced by `@adia-ai/llm` as of this snapshot. If you need them, handle them in your own server layer — and check `mcp__a2ui__search_chunks` for anything added since.
