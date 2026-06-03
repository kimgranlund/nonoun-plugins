# Streaming + SSE — mode 3

The streaming protocol and the shared SSE parser. Source: `packages/llm/src/adapters/sse.ts` (the parser) and the `parseStream` method of each adapter in `packages/llm/src/adapters/anthropic.ts` / `openai.ts` / `gemini.ts`. The `StreamChunk` union is declared in `anthropic.ts`.

---

## The `StreamChunk` union — the streaming contract

`streamChat()` and `client.stream()` yield this union (declared in `anthropic.ts`, re-exported from `index.ts`):

```text
StreamChunk =
  | { type: 'text';     text: string; snapshot: string }
  | { type: 'thinking'; text: string }
  | { type: 'done';     text: string; usage: AdapterUsage; stopReason: string }
  | { type: 'error';    error: Error }
```

Contract rules consumers depend on:

- **`text` chunks carry both the delta and the running `snapshot`.** `text` is the new fragment; `snapshot` is the full text accumulated so far. A consumer can render incrementally (`text`) or replace wholesale (`snapshot`).
- **Exactly one terminal.** A stream ends with a `done` chunk (carrying final `text`, `usage`, raw `stopReason`) OR an `error` chunk — never both, never neither on success.
- **`thinking` is optional and may interleave.** Anthropic + OpenAI emit it; Gemini doesn't. Consumers ignore it safely but must not crash.
- **`error` is a chunk, not a throw.** `streamChat()` catches a `fetch` failure and a non-`ok` response and yields `{ type: 'error', error }` rather than throwing (see `index.ts` `streamChat`). The consumer must handle the `error` chunk; a dropped `error` is a defect.

Adding a new chunk type (e.g., a tool-call chunk) is additive but touches every consumer — see "Adding a chunk type" below.

## Where the terminal `done` comes from — per provider

The terminal differs by provider, which matters when you debug a missing `done`:

| Provider | Terminal source (`parseStream`) |
| --- | --- |
| Anthropic | An explicit `message_stop` SSE event yields `done`; `message_delta` sets `stopReason` + `usage.output` first |
| OpenAI | No terminal event — `parseStream` yields `done` after the SSE loop completes (the `[DONE]` sentinel ends the loop) |
| Gemini | No terminal event — `done` yielded after the loop; `stopReason` is the constant `'end'` |

So Anthropic's `done` is event-driven; OpenAI and Gemini synthesize it after the byte stream closes. A new adapter picks whichever matches its provider — but it MUST yield exactly one `done` on success.

## The shared SSE parser — `readSSE`

`sse.ts` exports `async function* readSSE(body: ReadableStream<Uint8Array>): AsyncGenerator<SSEEvent>` where:

```text
SSEEvent = { event: string | undefined; data: string; done: boolean }
```

What it handles — and why each matters:

- **Partial-line buffering.** It decodes with `{ stream: true }` and keeps a `buffer`; an event split across two network chunks is reassembled. Don't re-implement line splitting in an adapter — consume `readSSE`.
- **Double-newline framing.** Events are split on `\n\n` or `\r\n\r\n`; the trailing partial is carried as `remainder`.
- **Field parsing.** Lines starting with `event:` set the event type; lines starting with `data:` append (one leading space stripped per the SSE spec); comment lines (`:`) are skipped.
- **Multi-line data.** Multiple `data:` lines in one event are joined with `\n`.
- **`[DONE]` detection.** An event whose joined data equals `[DONE]` gets `done: true`. Each adapter's `parseStream` does `if (event.done) break;` at the top of the loop.
- **Flush.** After the reader closes, a non-empty trailing buffer is parsed once more (with an appended `\n\n`) so a final unterminated event isn't lost.

`readSSE` releases the reader lock in a `finally`. An adapter must guard `if (!response.body) throw new Error('Response body is null')` before calling it (all three do).

## How an adapter consumes events

The shape every `parseStream` follows (grounded in `anthropic.ts`):

1. Guard `response.body`; init `snapshot = ''`, `usage`, `stopReason`.
2. `for await (const event of readSSE(response.body))` → `if (event.done) break;`.
3. `JSON.parse(event.data)` in a `try`/`catch` — a malformed frame is skipped (`catch { continue; }`), never fatal.
4. Branch on the event type. For Anthropic, `event.event ?? data.type` selects the SSE event (`message_start` / `content_block_delta` / `message_delta` / `message_stop` / `error`). OpenAI/Gemini branch on the JSON body shape (`choices[0].delta` / `candidates[0].content.parts`).
5. On a text delta: `snapshot += delta; yield { type: 'text', text: delta, snapshot };`.
6. On terminal: `yield { type: 'done', text: snapshot, usage, stopReason };`.

`usage` accumulates across events — e.g. Anthropic sets `input` + cache fields at `message_start` and `output` at `message_delta`, so the `done` chunk carries the complete tally.

## Worked example — "streamChat never emits `done`"

1. Plan: verify target is a real `streamChat()` against the affected provider, asserting the last chunk is `{ type: 'done' }` with non-zero `usage`.
2. Execute — bisect by layer:
   - Is `readSSE` framing the events? Log raw `SSEEvent`s — if they arrive but the adapter yields no `done`, the bug is in the adapter's terminal branch.
   - Anthropic: confirm a `message_stop` event actually arrives (event-driven terminal). OpenAI/Gemini: confirm the loop exits (a `[DONE]` or a closed body) so the post-loop `done` yields.
   - If frames don't arrive at all, the proxy may be buffering SSE (see `browser-proxy-boundary.md`) — that's a transport bug, not a parser bug.
3. Verify: a forced `streamChat()` shows ordered `text` deltas, a growing `snapshot`, and exactly one terminal `done`.

## Adding a new chunk type

A new `StreamChunk` variant (e.g. `{ type: 'tool_call'; ... }`):

1. Add the variant to the union in `anthropic.ts` (the canonical type).
2. Emit it from the adapters that support it; leave the others unchanged.
3. **Audit every consumer.** The two named consumers are the adia-ui chat-shell and the A2UI generation pipeline (via `createAdapter()` — see `bridge-facade.md`). Confirm each either handles the new type or falls through gracefully (the bridge's `stream()` already ignores chunk types it doesn't consume).
4. This is additive but consumer-visible — note it in CHANGELOG as a MINOR bump.

## Cross-references

- [adapter-contract.md](adapter-contract.md) — the adapter object, `parseResponse`, and the `usage` / `stopReason` mapping
- [bridge-facade.md](bridge-facade.md) — how the bridge re-shapes `StreamChunk` for the adia-ui pipeline
- [browser-proxy-boundary.md](browser-proxy-boundary.md) — SSE through a proxy (buffering pitfalls)
- Source: `packages/llm/src/adapters/sse.ts`, and the `parseStream` of `anthropic.ts` / `openai.ts` / `gemini.ts`
