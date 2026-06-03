# Browser / proxy boundary — mode 6

The browser+Node duality and the two proxy flavors. Source: the dispatch in `packages/llm/src/adapters/index.ts` (`isPassthroughProxy`, `proxyRequest`, `passthroughRequest`) and the browser logic in `packages/llm/src/llm-bridge.ts` (`resolveBaseUrl`, `isProductionHost`, `createBrowserProxyBridge`, the key-in-browser warning).

This is the single most error-prone area of the package: `proxyUrl` is overloaded, and getting it wrong produces silent 401s in the browser even when the local server works fine.

---

## Three transport modes

`chat()` / `streamChat()` choose a transport from `opts.proxyUrl`:

| Mode | When | Body shape | Auth |
| --- | --- | --- | --- |
| **Direct** | `proxyUrl` unset | `adapter.buildRequest()` upstream body | Adapter's own auth header (the real key) |
| **Smart proxy** | `proxyUrl` set, NOT matching the passthrough regex | Provider-neutral `{ provider, model, messages, system?, maxTokens?, temperature?, thinking?, stream }` | `content-type` only — the proxy holds the key server-side |
| **Passthrough proxy** | `proxyUrl` matches `/api/llm/<provider>(/...)` | Real upstream body (`adapter.buildRequest()`), URL swapped to the proxy | Adapter's own auth header, forwarded verbatim by the dumb proxy |

The dispatcher (in `index.ts`): `opts.proxyUrl ? (isPassthroughProxy(opts.proxyUrl) ? passthroughRequest(...) : proxyRequest(...)) : adapter.buildRequest(...)`.

## `isPassthroughProxy` — the URL-shape classifier

```text
PASSTHROUGH_PROXY_RE = /\/api\/llm\/[a-z]+(\/|$)/
isPassthroughProxy(url) = typeof url === 'string' && PASSTHROUGH_PROXY_RE.test(url)
```

Anything matching `/api/llm/<provider>/` is a **passthrough** proxy (a dumb URL rewriter — e.g. the Vite dev server forwarding to `https://api.<provider>.com/...`). Everything else is treated as a **smart** proxy (a server that speaks the provider-neutral protocol and holds the key). **This regex is the entire contract** between the two flavors — if you change the dev-server proxy path, update the regex, and vice versa.

## `proxyRequest` vs `passthroughRequest` — the two builders

- **`proxyRequest(opts, stream)`** builds the provider-neutral body `{ provider, model, messages, stream }` plus the optional `system` / `maxTokens` / `temperature` / `thinking`, with headers `content-type: application/json` only. **No `apiKey` in the body** — the smart proxy holds the key. URL is `opts.proxyUrl`.
- **`passthroughRequest(opts, stream)`** calls `adapter.buildRequest({ ...opts, stream })` (the real upstream body + the adapter's auth headers) and then swaps in `opts.proxyUrl` as the URL. The proxy forwards the bytes verbatim.

So `buildRequest()` is the single source of upstream shape for BOTH direct mode and passthrough mode (see `adapter-contract.md`). The only thing passthrough changes is the URL. **Don't fork `buildRequest` for proxy mode.**

## The browser bridge — `resolveBaseUrl` + the proxy map

In the browser, `llm-bridge.ts` routes through a same-origin passthrough proxy. `resolveBaseUrl(provider)` returns `undefined` outside the browser (let the adapter use its default upstream URL) and, in the browser, maps:

```text
anthropic → /api/llm/anthropic/v1/messages
openai    → /api/llm/openai/v1/chat/completions
google    → /api/llm/google
```

These paths match `PASSTHROUGH_PROXY_RE`, so the facade routes them through `passthroughRequest`. **A new browser-routable provider needs a `resolveBaseUrl` entry whose path matches the passthrough regex.**

## Production-host path — real calls with no client key

`isProductionHost()` returns `true` when the browser is on a non-local host (not `localhost` / `127.0.0.1` / `0.0.0.0` / `*.local` / private `10.` / `192.168.` / `172.16–31.` ranges). When `createAdapter()` detects `provider === 'stub'` (no env vars in the browser) BUT `IS_BROWSER && isProductionHost()`, it calls `createBrowserProxyBridge('anthropic', …)` instead of returning the stub:

- It builds a real client with a **sentinel** `apiKey: 'browser-uses-server-side-proxy-key'` so the non-empty-key check passes.
- The sentinel **never reaches the upstream provider** — the same-origin proxy strips the incoming auth header and injects its own server-side key.
- This is how a deployed app makes real LLM calls without ever exposing a key to the browser.

**Preserve this path.** Removing it makes production browsers fall back to the stub (canned UI) instead of real generation.

## Key-in-browser safety — the one-shot warning

In direct/passthrough browser mode with a real `apiKey`, the key is sent verbatim in `x-api-key` / `Authorization` headers and is readable in DevTools. `createAdapter()` logs a styled, deduplicated (window-flag `__adia_llm_key_warning_shown`) warning naming the provider and a masked key, stating this is local-dev only. This is intentional friction:

- Dev passthrough with a real browser key: **local-dev only, never deploy.**
- Production: the smart/same-origin proxy holds the key server-side; the browser sends the sentinel.

Keep the warning and the dedup flag when touching `createAdapter()`.

## Worked example — "401 in the browser, but `node` works fine"

1. Plan: verify target is a real browser `streamChat()` through the proxy returning `text` deltas, and the same call in Node (direct) succeeding.
2. Execute — the usual cause is a proxy-flavor mismatch:
   - Is `proxyUrl` matching `PASSTHROUGH_PROXY_RE`? If the dev server is a passthrough but the URL doesn't match the regex, the facade builds a provider-neutral body and sends it to a dumb proxy that expects the raw upstream shape → upstream 401/400.
   - For passthrough, confirm the adapter's auth header is present (`passthroughRequest` forwards `buildRequest` headers). For smart proxy, confirm NO key is in the body and the server injects it.
   - SSE buffering: a proxy that buffers responses breaks streaming — confirm the proxy flushes SSE (this is a transport bug, surfaced as a "never emits `done`" in `streaming-sse.md`).
3. Verify: browser `streamChat()` streams; Node direct works; no real key is visible in the browser Network panel on a production host.

## Pitfalls

- **Putting `apiKey` in the smart-proxy body.** The proxy holds the key; `proxyRequest` must not include it.
- **Forking `buildRequest` for proxy mode.** Passthrough reuses it; direct reuses it. One source of truth.
- **Changing a `resolveBaseUrl` path so it no longer matches the passthrough regex.** Then the browser silently switches to smart-proxy body shape against a passthrough proxy → 4xx.
- **Dropping the production-host sentinel path.** Deployed browsers fall back to the stub instead of real generation.

## Cross-references

- [adapter-contract.md](adapter-contract.md) — `buildRequest()` as the single upstream-shape source
- [bridge-facade.md](bridge-facade.md) — `createAdapter()` and the stub fallback
- [streaming-sse.md](streaming-sse.md) — SSE-through-a-proxy buffering symptoms
- Source: `isPassthroughProxy` / `proxyRequest` / `passthroughRequest` in `packages/llm/src/adapters/index.ts`; `resolveBaseUrl` / `isProductionHost` / `createBrowserProxyBridge` in `packages/llm/src/llm-bridge.ts`
