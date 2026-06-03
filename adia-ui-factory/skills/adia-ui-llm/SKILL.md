---
name: adia-ui-llm
description: >
  Wire LLM-powered features into an adia-ui app — the @adia-ai/llm client (Anthropic/OpenAI/Gemini),
  streaming chat, the <chat-shell-ui> web-module, and the production browser proxy — plus UI
  generation via the a2ui MCP. Use for chat/AI features and A2UI generation.
---

# adia-ui-llm — LLM features

Two distinct concerns; pick the right one:

- **App LLM features** (a chat box, a summarize action) → `@adia-ai/llm` + `<chat-shell-ui>`.
- **Generating UI markup** from an intent → the a2ui MCP's `generate_ui` (see `adia-ui-compose` / `a2ui-mcp-tools.md`), not `@adia-ai/llm`.

Full depth: `${CLAUDE_PLUGIN_ROOT}/references/llm.md`.

## The one rule to get right first

**Never ship a provider API key to the browser in production.** Use the **smart proxy**: point `streamChat({ proxyUrl: '/api/chat', … })` at your own same-origin endpoint that holds the key server-side and pipes SSE back. The dev-only passthrough proxy (`/api/llm/<provider>/…`) sends the real key in browser headers — Vite-dev only, never deployed.

## The fast path

1. **Chat surface** — drop in `<chat-shell-ui proxy-url="/api/chat" model="…">` with its `chat-header` / `chat-thread` / `chat-composer` slots; it wires `streamChat` for you and emits `submit`/`chunk`/`done`/`error`.
2. **Custom features** — call `streamChat(opts)` directly and branch on `chunk.type` (`text` / `thinking` / `done` / `error`); provider auto-detects from the model name.
3. **SSR** — register `<chat-shell-ui>` client-side like any component (`adia-ui-ssr`); keep the key server-side behind the smart proxy.
4. **Generating UI?** — that's `mcp__a2ui__generate_ui` → `validate_schema` / `check_anti_patterns`, a different path.

## Don't assume

Tool-calling, structured-output modes, and built-in retry are **not** in `@adia-ai/llm` as of this snapshot — handle them in your server layer. Verify against `mcp__a2ui__search_chunks` if you need something newer.

## Reference

- `${CLAUDE_PLUGIN_ROOT}/references/llm.md` — the client API, `StreamChunk`, providers, the proxy model, the chat-shell surface, and the app-LLM-vs-UI-generation boundary.
