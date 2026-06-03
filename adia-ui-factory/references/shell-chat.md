---
name: shell-chat
load-when: authoring a chat-shell LLM conversation surface
load-size: ~1.5k tokens
required-for: [adia-ui-shells — chat path]
---

# chat-shell — the conversation surface

LLM chat chrome from `@adia-ai/web-modules`. Register: `import '@adia-ai/web-modules/chat'`. The **LLM client/proxy/security** lives in `adia-ui-llm` — this is the _surface_; that is the _wiring_.

## Cluster roster

`<chat-shell>` (orchestrator) · `<chat-header>` (+ `<chat-status slot="status">`) · `<chat-thread>` (scrolling messages, reflects `[streaming]`) · `<chat-empty>` (empty-state slot) · `<chat-composer>` (input wrapper, disables while streaming) · `<chat-input-ui>` · `<chat-sidebar slot="sidebar">` (optional).

## Canonical skeleton

```html
<chat-shell proxy-url="/api/chat" model="claude-sonnet-4-6">
  <chat-header><span slot="name">Assistant</span><chat-status slot="status"></chat-status></chat-header>
  <chat-thread>
    <chat-empty><empty-state-ui icon="chat-circle" heading="Hello!" description="Ask me anything."></empty-state-ui></chat-empty>
  </chat-thread>
  <chat-composer><chat-input-ui placeholder="Message…"></chat-input-ui></chat-composer>
</chat-shell>
```

## Props · events · methods

- **Props:** `model` · `provider` (anthropic|openai|google|stub) · `proxy-url` · `system` · `thinking` · reflects `[streaming]`.
- **Events:** `submit {text, model}` · `chunk {text, snapshot}` · `thinking {text}` · `done {text, usage, stopReason}` · `error {error}` · `abort` · `clear` · `message {id, role, content}`.
- **Methods:** `send(text, {model})` · `appendMessage({role, content})` · `appendChunk(text)` · `clear()` · `abort()` · `export()` / `import(data)`; accessors `conversation` / `messages`.

## Wiring to the LLM

Set `proxy-url` (or, dev-only, `apiKey`) and the shell **auto-sends on submit** via `streamChat` and renders the stream for you. Otherwise it just emits `submit` — you call your endpoint and drive the UI with `appendChunk`/`done`/`error`. **Security:** the production pattern is a same-origin smart proxy that holds the key server-side — never ship a provider key to the browser. Full client/proxy contract: `adia-ui-llm`.

## Gotchas

- Import the **chat barrel**; piecemeal imports leave children unregistered.
- Legacy shapes (`[data-chat-messages]`, `[data-chat-input]`, `[data-chat-empty]`, `[data-chat-name]`) were retired v0.4.0 — use the bespoke tags (`adia-lint` `LEGACY-SHELL`).
- SSR: register `<chat-shell>` client-side like any component; keep the key server-side.

Real usage: `apps/genui/app/factory-chat/`.
