---
name: browser-bundle-node-imports
applies-to: monorepos with shared packages reachable from both Node and browser bundles
severity: hard-runtime-regression (silent in tests)
detected: 2026-05-12 (chat-ui v0.4.7 §72 follow-up)
related-postmortem: chat-ui/.brain/postmortems/2026-05-12-browser-bundle-node-imports.md
---

# Audit pattern — Browser bundle crashes from top-level `import 'node:*'`

## The bug class

A module that needs to work in both Node (server-side smoke, tests, MCP, evals) and the browser (live app surface) statically imports `node:fs`, `node:path`, `node:url`, `node:crypto`, etc. at module top level. The module is reachable from the browser bundle via static import chain.

In the browser, Vite (or any bundler) externalizes the `node:*` modules — it can't bundle them. Vite emits a shim that throws on **property access**, not on import resolution. So:

1. Bundler logs a warning: `Module "node:path" has been externalized for browser compatibility.`
2. Module's top-level code accesses a property (`path.dirname(...)`, `fs.existsSync(...)`).
3. Module init throws.
4. First consumer up the import chain fails to mount.
5. User sees either a hard error or a graceful-degradation message ("demo mode", "fallback enabled", etc.) depending on the import site's catch handling.

## Why it's hard to catch

- **Vitest is Node-only.** Tests pass.
- **The bundler doesn't fail-fast.** It externalizes and warns; the bug surfaces only when production code accesses the externalized stub.
- **`@vite-ignore` on inner dynamic imports is a known defensive pattern** but doesn't help here — the failure is at top-level static import, before any runtime branch.
- **Sibling modules may already be correctly dual-mode'd.** The pattern is well-known; one module gets fixed; the next sibling slips through.
- **No CI gate detects this.** A `vite build` smoke would catch it, but most repos run `vitest` + `npm test` and call it done.

## The discriminating signal

Top-level static `import .* 'node:*'` in a module reachable from the browser bundle. Distinct from:

```js
// SAFE — dynamic, Node-only branch
if (IS_NODE) {
  const fs = await import(/* @vite-ignore */ 'node:fs');
}
```

vs.

```js
// UNSAFE — runs at module init regardless of environment
import fs from 'node:fs';
const __dirname = fs.existsSync(...);  // throws in browser
```

## How to audit

```bash
# Find every browser-reachable module with top-level static node:* imports
grep -rln "^import .* 'node:" packages/ apps/ playgrounds/ catalog/ 2>/dev/null \
  | grep -v 'node_modules\|dist/\|/test/\|\.test\.\|/evals/\|/scripts/\|server\.js'
```

Each hit is a candidate. Triage:

1. **Node-only file (`.mjs` extension + imports `playwright`/`fs`/etc. liberally)** → safe, ignore.
2. **Used only by Node-only consumers (MCP scripts, evals, tests)** → safe.
3. **Imported by anything in `core/`, `strategies/monolithic/`, `strategies/zettel/` (if lazy-loaded) — trace upward.** If the chain reaches `apps/*/app/*.contents.js` or a similar browser entry, it's a bug.
4. **Lazy-loaded via `await import('./this-module.js')`** → safe (the static-import trap doesn't fire).

Look for protective comments in registries / barrels: e.g.,

```js
// Zettel is lazy-loaded — it transitively imports node:fs / node:path / node:url.
// Static-importing it here would break browser loads of core/generator.js.
```

That comment is the canonical protective documentation — when you see it, the lazy-load wall is intentional. Check that the wall hasn't been breached by a sibling `import` statement at the top of another file in the same package.

## The fix pattern

Replace top-level static `import 'node:*'` with the dual-mode loader:

```js
const IS_NODE =
  typeof process !== 'undefined' &&
  typeof process.versions?.node === 'string';

// Vite resolves this at build time; at runtime in Node the variable is unused.
let _globModules = null;
if (!IS_NODE) {
  try {
    _globModules = import.meta.glob('../path/to/files/**/*.json', {
      query: '?raw',
      import: 'default',
      eager: false,
    });
  } catch {
    // Not in a Vite context — no data in this realm.
  }
}

async function _loadNode() {
  const fs = await import(/* @vite-ignore */ 'node:fs');
  const path = await import(/* @vite-ignore */ 'node:path');
  // ... Node-only logic
}

async function _loadBrowser() {
  if (!_globModules) return;
  for (const [, loader] of Object.entries(_globModules)) {
    const raw = await loader();
    // ... browser-only logic
  }
}

export async function load() {
  if (IS_NODE) await _loadNode();
  else await _loadBrowser();
}

// Eager top-level load: Node side awaits; browser side fires-and-forgets
// (because module-init top-level await is permitted but blocks all importers).
if (IS_NODE) {
  await load();
} else {
  load().catch(() => {});
}
```

The `import.meta.glob(...)` pattern is Vite-specific. For non-Vite bundlers, swap in the bundler's equivalent or expose a `setLoader(fn)` hook.

## Trip-wires (what to add)

1. **Pre-cut audit**: run the grep above as part of the release F-N1 dry-run. Hit count == 0 for browser-reachable surface, OR every hit traces to a Node-only-consumer chain.

2. **Vite build smoke**: a new `scripts/release/check-browser-safe.mjs` (proposed) that:
   - Runs `vite build` over the app surface.
   - Asserts zero `[vite] Module "node:*" has been externalized` warnings in the build output.
   - Exits non-zero if any are present.

3. **Playwright end-to-end probe**: extend any existing smoke spec (e.g. `smoke:genui-error-ux`) to assert specific behavior that requires the browser-side composition library / catalog to be loaded (e.g. retrieval strategy is reported, not just "demo mode"). Catches the symptom even if the trip-wire grep misses an instance.

## Common patterns this catches

- Loaders that walk a corpus directory at module init (`fs.readdirSync` → `Map` of records)
- Cache files that hash + write fingerprints (`crypto.createHash` + `fs.writeFile`)
- Issue reporters that write `.brain/findings/` JSONL files (`fs.appendFile`)
- Path resolvers that compute `__dirname` from `import.meta.url`

In each case, the Node use case is real, but it must be guarded.

## What this audit does NOT catch

- Runtime calls to `process.env.SOMETHING` (those are separate; Vite injects polyfills) — those need `typeof process !== 'undefined'` guards but the failure mode is different.
- `Buffer` references (browser polyfill is fragmented; see Vite docs).
- Worker / service-worker boundaries (`new Worker(new URL(...))`) — those need their own audit.

## Reference incident

chat-ui v0.4.7 §72 follow-up — `packages/a2ui/compose/strategies/zettel/composition-library.js` had top-level `import 'node:fs/path/url'` from the v0.4.4 §38 fragment-library → composition-library rename. Reached the browser via `gen-ui.contents.js → @adia-ai/a2ui-compose → core/reference.js → strategies/zettel/composition-library.js`. Fixed in commit `76dbcff2`. Postmortem: `/Users/kimba/Projects/chat-ui/.brain/postmortems/2026-05-12-browser-bundle-node-imports.md`. Latent for ~8 days. Detected by user runtime, not CI.

Sibling module `retrieval/component-catalog.js` had the same risk but was correctly dual-mode'd in an earlier arc. The pattern was known; the fix was not propagated. **The audit gap was: no one ran the discriminating grep across the package after fixing the first module.**
