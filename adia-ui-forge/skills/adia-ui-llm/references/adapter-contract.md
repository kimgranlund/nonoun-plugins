# Adapter contract — modes 1-3

The single shape every provider adapter implements. Source: `packages/llm/src/adapters/anthropic.ts` (the canonical adapter — `openai.ts` and `gemini.ts` import their shared types from it), the facade `packages/llm/src/adapters/index.ts`, and the shared parser `packages/llm/src/adapters/sse.ts`.

This reference is about the adapter object — its three methods, the request it builds, and the response/usage/`stopReason` it parses. The SSE-byte mechanics live in `streaming-sse.md`; the facade that dispatches to an adapter lives in `bridge-facade.md`.

---

## The adapter object — three methods

Each provider exports a single `const` (lowercase provider name) with a `name` literal plus three methods. The facade calls them; consumers never touch an adapter directly.

| Member | Signature (see `anthropic.ts`) | Job |
| --- | --- | --- |
| `name` | `'anthropic' as const` (or `'openai'` / `'gemini'`) | Registry key + error messages |
| `buildRequest(opts)` | `(BuildRequestOpts) => AdapterRequest` | Build the upstream `{ url, headers, body }` — the single source of truth for upstream shape |
| `parseResponse(json)` | `(ProviderResponseBody) => AdapterResponse` | Map a non-streaming JSON body to `{ text, usage, stopReason }` |
| `parseStream(response)` | `(Response) => AsyncGenerator<StreamChunk>` | Map an SSE `Response` to the `StreamChunk` union |

The shared types (`AdapterRequest`, `AdapterUsage`, `AdapterResponse`, `StreamChunk`, `BuildRequestOpts`) are declared in `anthropic.ts` and re-exported from `index.ts`. `openai.ts` and `gemini.ts` `import type` them from `./anthropic.js`. **When you change a shared type, change it in `anthropic.ts`** — the other two adapters and the facade inherit it.

## `AdapterResponse` — the normalized result

`parseResponse` (and the terminal `done` chunk of `parseStream`) always returns:

```text
AdapterResponse = { text: string; usage: AdapterUsage; stopReason: string }
AdapterUsage    = { input: number; output: number; cacheCreation?: number; cacheRead?: number }
```

The facade wraps this as `ChatResult` (same fields) for `chat()`. Each adapter is responsible for mapping its provider's idiosyncratic field names into this shape:

| Field | Anthropic source | OpenAI source | Gemini source |
| --- | --- | --- | --- |
| `text` | first `content[]` block of `type === 'text'` | `choices[0].message.content` | join of `candidates[0].content.parts[].text` |
| `usage.input` | `usage.input_tokens` | `usage.prompt_tokens` | `usageMetadata.promptTokenCount` |
| `usage.output` | `usage.output_tokens` | `usage.completion_tokens` | `usageMetadata.candidatesTokenCount` |
| `usage.cacheCreation` | `usage.cache_creation_input_tokens` | — (absent) | — (absent) |
| `usage.cacheRead` | `usage.cache_read_input_tokens` | — (absent) | — (absent) |
| `stopReason` | `stop_reason` (raw) | `finish_reason` (`stop` → `end`, else raw) | hardcoded `'end'` |

Every numeric field defaults to `0` via `?? 0`; missing cache fields stay absent for non-Anthropic providers. **A new adapter must fill `input` + `output`; cache fields are optional.**

## `stopReason` — propagate raw, never normalize

The `stopReason` string is part of the public contract because the downstream truncation detector reads it. Known values across providers:

- `end` / `stop` / `STOP` — clean completion.
- `max_tokens` (Anthropic) / `length` (OpenAI) / `MAX_TOKENS` (Gemini) — **truncation**; the consumer refuses silent fallback rendering.
- `tool_use` (Anthropic) / `tool_calls` (OpenAI) — tool-call paused output.

OpenAI's adapter maps only its own `finish_reason === 'stop'` to `end` and passes everything else through raw (see `openai.ts` `parseResponse`). Anthropic passes `stop_reason` through untouched. **Do not collapse the truncation values to `end`** — that hides truncation from the consumer and is a defect, not a cleanup (see §Posture in SKILL.md).

## `buildRequest()` — one source of truth for upstream shape

`buildRequest(opts: BuildRequestOpts)` returns `{ url, headers, body }`. It is called from two places — direct mode and passthrough-proxy mode — and **must produce the same upstream body + auth headers in both**. Don't fork it for proxy mode; the dispatcher swaps only the URL (see `browser-proxy-boundary.md`).

Per-provider request facts grounded in the source:

| Concern | Anthropic (`anthropic.ts`) | OpenAI (`openai.ts`) | Gemini (`gemini.ts`) |
| --- | --- | --- | --- |
| URL | `https://api.anthropic.com/v1/messages` | `https://api.openai.com/v1/chat/completions` | `.../v1beta/models/<model>:<action>` |
| Auth header | `x-api-key` + `anthropic-version: 2023-06-01` | `authorization: Bearer <key>` | `x-goog-api-key` |
| System prompt | top-level `system` (string or cache-control block) | prepended as a `role: 'system'` message | `systemInstruction.parts[].text` |
| Max-tokens key | `max_tokens` (default `32768`) | `max_tokens` (only if set) | `generationConfig.maxOutputTokens` (default `32768`) |
| Stream flag | `stream` in body | `stream` + `stream_options.include_usage` | encoded in the URL action |
| Roles | `messages[]` verbatim | `messages[]` verbatim | `assistant` → `model`, else `user` |

Gemini's URL is action-dependent: `generateContent` for non-streaming, `streamGenerateContent?alt=sse` for streaming (see `gemini.ts` — the `action` ternary). The other two use one URL and a `stream` body flag.

## Anthropic prompt caching — the `cache` opt

`BuildRequestOpts.cache` is Anthropic-specific. When `cache` is truthy, `anthropic.ts` wraps the system prompt as a cache-control block:

```text
body.system = [{ type: 'text', text: opts.system, cache_control: { type: 'ephemeral' } }]
```

`openai.ts` and `gemini.ts` ignore `cache` (they read only the fields they understand). The bridge sets `cache: this.#provider === 'anthropic'` so the adia-ui system prompt becomes a cache breakpoint. **A new adapter should ignore `cache` unless its provider has its own caching mechanism** — then add a parallel branch in that adapter's `buildRequest` and surface the cache fields in `parseResponse`.

## `thinking` — Anthropic-only request, two adapters surface a chunk

`BuildRequestOpts.thinking` / `thinkingBudget` are read only by `anthropic.ts` (`body.thinking = { type: 'enabled', budget_tokens: opts.thinkingBudget ?? 10000 }`). On the streaming side, both Anthropic (`thinking_delta`) and OpenAI (`delta.reasoning_content`) emit a `{ type: 'thinking', text }` chunk; Gemini does not. Consumers may ignore `thinking` chunks, but they must not crash on them.

## Worked example — auditing an adapter's `usage` mapping

Symptom: cache hit-rate telemetry reads `0` for Anthropic even though the API returned cache reads.

1. Plan: verify target is a real `chat()` against Anthropic with a system prompt large enough to cache (≥1024 tok Sonnet/Opus, ≥2048 Haiku) and `cache: true`, run twice in the cache window.
2. Execute: inspect `anthropic.ts` `parseResponse` — confirm `cacheRead` reads `usage.cache_read_input_tokens` (not a camelCase guess). For streaming, confirm `message_start` sets `usage.cacheCreation` / `usage.cacheRead` and `message_delta` sets `usage.output` (see `parseStream` in `anthropic.ts`).
3. Verify: the second `chat()` returns `usage.cacheRead > 0`; the bridge's `cacheReadTokens` is non-zero. If it's still `0`, the bug is the field name, not the bridge.

## Cross-references

- [streaming-sse.md](streaming-sse.md) — the `StreamChunk` union, the shared SSE parser, and the per-provider event mapping
- [bridge-facade.md](bridge-facade.md) — how `chat()` / `streamChat()` resolve and call an adapter; the `ChatResult` wrapper
- [browser-proxy-boundary.md](browser-proxy-boundary.md) — why `buildRequest()` must stay proxy-agnostic
- [add-a-provider.md](add-a-provider.md) — the end-to-end recipe that uses this contract
- Source: `packages/llm/src/adapters/anthropic.ts` (canonical types + adapter), `openai.ts`, `gemini.ts`
