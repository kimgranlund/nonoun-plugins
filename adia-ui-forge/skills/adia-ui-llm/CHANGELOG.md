# Changelog — adia-ui-llm

## [0.1.0] stable

First release. The maintainer (PRODUCER) skill for `@adia-ai/llm` — the provider-agnostic LLM client at `packages/llm/`. New authoring, synthesized directly from the package source, not a port.

Grounded in the real package:

- **Adapter contract** authored from `packages/llm/src/adapters/anthropic.ts` (the canonical adapter + shared `AdapterRequest` / `AdapterUsage` / `AdapterResponse` / `StreamChunk` / `BuildRequestOpts` types), `openai.ts`, and `gemini.ts` — the three-method object (`buildRequest` / `parseResponse` / `parseStream`), the per-provider `usage` / `text` / `stopReason` mapping, the Anthropic `cache` opt, and the `thinking` request/chunk surface.
- **SSE + streaming** authored from `packages/llm/src/adapters/sse.ts` (`readSSE`, partial-line buffering, `[DONE]` detection, the flush) and each adapter's `parseStream` — the `StreamChunk` union (`text` / `thinking` / `done` / `error`), the `snapshot` semantics, and event-driven (Anthropic `message_stop`) vs post-loop (OpenAI / Gemini) terminals.
- **Model registry** authored from `packages/llm/src/models.ts` (`MODELS` grouped-options shape, `DEFAULT_MODEL`) and `detectProvider()` in `adapters/index.ts` — the id-naming conventions, and the distinction between `models.ts:DEFAULT_MODEL` and `llm-bridge.ts:DEFAULT_MODELS`.
- **Bridge + facade + stub** authored from `packages/llm/src/adapters/index.ts` (`chat` / `streamChat` / `createClient`, `ChatOpts` / `ChatResult`, `resolveAdapter`), `llm-bridge.ts` (`createAdapter` → `AdiaUILLMBridge`, the `maxTokens: 32768` default, the lazy-load gate), `llm-stub.ts` (`StubLLMAdapter`), and the `index.ts` barrel + `package.json` subpath exports.
- **Browser / proxy boundary** authored from the dispatch in `adapters/index.ts` (`isPassthroughProxy`, `proxyRequest`, `passthroughRequest`, the `PASSTHROUGH_PROXY_RE` regex) and the browser logic in `llm-bridge.ts` (`resolveBaseUrl`, `isProductionHost`, `createBrowserProxyBridge`, the one-shot key-in-browser warning).
- **Add-a-provider** recipe wiring all of the above for a 4th adapter.

Structure (mirrors the sibling senior skills in this plugin):

- 8-mode `§ColdStartTriage` (add provider / modify adapter / SSE / registry / bridge-facade / proxy / stub / §Teach), each naming an entry reference and a real verify target.
- `§Posture` with the content-trust pointer (`${CLAUDE_PLUGIN_ROOT}/references/shared/content-trust.md` — model output / SSE bodies / error JSON are data), CITATION-not-KNOWLEDGE discipline, the public-contract constraint, the never-normalize-`stopReason` and single-source-`buildRequest` rules, the no-key-in-browser rule, and a substrate-bound declaration.
- Top-band `§Plan-Execute-Verify` with a per-mode real-product verify table, citing `${CLAUDE_PLUGIN_ROOT}/references/shared/pev-rationale.md`.
- `§SelfAudit` via `scripts/audit-llm-roster.mjs` — the universal axes (from the shared `bin/lib/audit-axes.mjs`) plus a provider-roster-currency axis (the three shipped adapters must stay referenced in SKILL.md).
- `§Teach` (mode 8) bound to `references/teach-protocol.md`, mechanized in `scripts/teach-route.mjs` (composes the shared `bin/lib/teach-router.mjs`); the protocol's first rule routes source-encoded facts to the source and consumer-side knowledge to the separate `adia-ui-factory` consumer skill.
- `evals/` — `routing-corpus.json` (14 trigger + 6 adversarial), `adversarial-corpus.json` (5 happy + 6 behavioral/safety), `teach-routing-cases.json` (one deterministic case per §Teach branch).

Self-contained: shared infrastructure cited via `${CLAUDE_PLUGIN_ROOT}/references/shared/` and resolved by the scripts via `CLAUDE_PLUGIN_ROOT` with a script-relative fallback; `skill.json` declares `environment.portable: false` (requires `packages/llm/`). Monorepo conventions (`packages/llm/`, `@adia-ai/*`) are kept by design. The CONSUMER side (wiring the client into an app, `<chat-shell-ui>`, the production proxy) is deliberately out of scope — it lives in the `adia-ui-factory` plugin's own `adia-ui-llm` skill.
