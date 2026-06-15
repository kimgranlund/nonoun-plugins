# dev-factory — Server UI fixes (downstream dogfooding log)

Fixes and issues found while **operating** dev-factory's `dev-server` (the kanban board + the
bounded loop) on a real instance (`dark-factory-test`, the HCT-palette-generator spec build-out).
Kept here so the solutions can be passed back to the plugin author. Distinct from the
author's own [ISSUES.md](../ISSUES.md): this is **external-operator feedback** — what broke when
a user *ran* the server, with the patch where we already made it.

`UI-n` = Server UI (`dev-server/ui/`). `DF-n` = dev-server / dev-kernel runtime surfaced in the
same session (non-UI, included because the same author owns them). Severity `P1`(worst)…`P3`.
Append new entries at the top of each section. Snapshot: **2026-06-15**.

---

## Server UI (`dev-server/ui/`)

### UI-3 · P2 — the UI can't tell you whether the factory is WORKING (or what it's doing) · FIXED in source (2026-06-15)

**Symptom.** Operating the board, it was impossible to tell at a glance if anything was active. The header's
green **"live"** dot means only that the SSE socket is connected — *not* that work is happening; the
heartbeat/activity state was buried in the Agents tab; and the Kanban "Active" column conflated *queued* with
*being built*. With 4 "Active" tickets + a green "live" dot, the obvious (wrong) read was "it's running."

**Root cause.** `/api/status` exposed `running_agents` but no single derived "is it working, and what is it
doing" headline, and the UI surfaced only the socket state. Compounded by a **stale projection** (DF-2): the
running server's `index.db` showed 4 active tickets while the canonical `lattice.json` had already validated
the cells — the board was showing work that was actually *done*.

**Fix in source.** `api.factory_state(d, heartbeat_enabled, paused)` — a derived headline from real state
(running workers · heartbeat posture · a dep-readiness check `ready_tickets`): **idle / running / armed
(ready work, heartbeat on) / blocked (active but deps unmet) / drained (queue empty) / paused**. `/api/status`
now carries `factory`; the UI renders a colour-coded work-state chip in the header beside the socket dot
("IDLE · no work queued", "RUNNING · 2 workers", …). `throughput` report alias restored (404'd). `app.js?v`
bumped. selftest locks idle/drained/paused. *(Restart the running server to pick it up — it also runs the
DF-2 boot rebuild, reconciling the stale projection.)*

### UI-2 · P2 — static UI assets have no cache-busting, so a fix to `app.js` never reaches a running browser · FIXED (working tree, 2026-06-15)

**Symptom.** After UI-1's `app.js` fix was in place (the *server* confirmed serving the patched file —
`curl /app.js | grep safe\[RAW\]` → 1), the **browser kept rendering the pre-fix `app.js`** — the
escaped-HTML bug persisted across reloads, looking like UI-1 was never fixed. The tell: the ledger
still showed `<span class="rat">· draft -&gt; active</span>` (the old full-escape behavior).

**Root cause** (`dev-server/ui/index.html:28`). The shell is loaded as
`<script type="module" src="app.js">` with **no version string**, and the FastAPI `StaticFiles` mount
serves it with only `etag`/`last-modified` (no explicit `Cache-Control`). Browsers cache ES-module
scripts aggressively and will serve `app.js` from cache **without revalidating**, so an edit to
`app.js` does not reach a running session — a normal reload (and often even a hard reload, for module
scripts) keeps the stale file. `app.js` has no sub-imports, so busting it alone is sufficient.

**Fix.** Version the script URL so the browser must fetch a new resource:

```html
<script type="module" src="app.js?v=2"></script>
```

The query string makes it a cache-miss URL; `StaticFiles` ignores the query and serves the current
file. On reload the browser revalidates the top-level `index.html` (content changed → new etag), gets
the `?v=2` reference, and fetches the never-cached URL. **Bump the version on each UI change.**

**Better long-term** (author's call): content-hashed asset filenames (`app.<hash>.js`), or serve the
HTML document with `Cache-Control: no-cache` while hashed JS/CSS stay `immutable`. The manual `?v=N`
bump is the zero-dependency interim.

**Why this matters for the catalog.** Any future `dev-server/ui/` fix is **invisible to a running
operator** until the version is bumped — UI-1 was correct in the served file yet looked broken on
screen for exactly this reason. Pair every UI fix with a `?v` bump.

### UI-1 · P1 — nested ``html`…` `` renders as escaped literal text across the whole board · FIXED (working tree, 2026-06-15)

**Symptom.** Every ticket card, cell card, and ledger row showed raw HTML as text instead of
rendering it:
- ticket card body: `<span class="cell">capability.system.semantic-mapping</span><div class="cell" style="margin-top:.25rem">defined → instantiated</div>`
- cell card signal badge: `<span class="f" title="1 signals">1</span>` (overlapping the slug)
- ledger row: `<span class="rat">· cell spec.system.color-mode advanced to validated …</span>`

So the board was effectively unusable — the dominant content of every card was escaped markup.

**Root cause** (`dev-server/ui/app.js`). The ``html`…` `` tagged template returned a **plain
string**, and `interp()` only skips escaping for `raw()`-wrapped values
(`if (v && v[RAW] !== undefined) return v[RAW]; return escapeHtml(v);`). The codebase nests
``html`…` `` inside other ``html`…` `` templates in many places (the card/cell/ledger builders —
e.g. `${t.target_cell ? html\`<span class="cell">${t.target_cell}</span>\` : ""}`). When the inner
result (a plain string) reaches the **outer** template's `interp()`, it has no `RAW` marker, so the
outer template **escapes it** → the static `<span>`/`<div>` tags print as literal text. Author
intent was clearly that ``html`` produces nestable trusted HTML; the implementation just never
marked its output as trusted. Affected sites: app.js ~`421`, `423`, `518`, `604`, `646`, `657`,
`783`, `888` (every nested ``html``).

**Fix** (2 lines, systemic — in the tag itself, so all nested sites are repaired at once):

```js
// html(): mark output trusted so a nested html`…` is not re-escaped by an outer interp().
// Boxed String — interp() reads its RAW; innerHTML=, Array.join, `${}` all coerce it back to a
// plain string, so no call site changes.
export function html(strings, ...values) {
  let out = strings[0];
  for (let i = 0; i < values.length; i++) out += interp(values[i]) + strings[i + 1];
  const safe = new String(out);
  safe[RAW] = out;
  return safe;
}

// UIElement render path (was: if (typeof t === "string") …) — accept the boxed String too:
if (typeof t === "string" || t instanceof String) this.innerHTML = String(t);
```

(As served: `dev-server/ui/app.js:79` `safe[RAW] = out;` and `:91` the `instanceof String` guard.)

**Why a boxed `String` and not `raw()` everywhere.** Wrapping each nested call in `raw()` would
work but is N sites and misses future ones. A boxed `String` is the systemic fix: `interp()` reads
`RAW` (→ not re-escaped when nested), while every other consumer — `el.innerHTML = html\`…\``,
`rows.map(...).join("")`, ``${html\`…\`}`` — coerces it back to a primitive. Only the one
`typeof === "string"` check (the `template()`→`innerHTML` path) needed widening.

**Verification.** `node --check app.js` clean; an 8-case logic test (mirroring the patched
`html`/`interp`/`raw`) passes: the three reported render sites now emit real markup, **user input
is still escaped** (`<script>` → `&lt;script&gt;` — no XSS regression), and `String()` / `Array.join`
/ `raw()` coercion all intact. The running server (static-serves from disk) already returns the
patched file; operator just hard-reloads the browser.

**Note for the author.** No build step in `dev-server/ui/` (index.html loads app.js as a module
directly), so the edit is live on reload. The fix is self-contained in the template machinery —
no styles.css or call-site changes.

---

## dev-server / dev-kernel runtime (non-UI, same session)

### DF-7 · P2 — an author ticket (`defined→instantiated`) can't close `done` once `validate.py` takes its cell to `validated` · worked around

**Symptom.** Building `capability.system.color-engine`: the advancer authored the asset, then `validate.py`
ran the harness and advanced the cell **`defined → validated`** in one pass (validate.py auto-steps
`defined→instantiated→validated`). The author ticket targets only `{from:defined, to:instantiated}`, so closing
it `done` was **denied**: *"authoring done denied: illegal maturity advance validated → instantiated"* — the
done-morphism tries to advance the cell to the ticket's target (`instantiated`), but it's already past it.

**Root cause.** Two models collide: (a) the **ticket** model is single-step (gate-ticket-ready rejects
`defined→validated`, so a build is meant to be *two* tickets — author `defined→instantiated`, then validate
`instantiated→validated`); (b) **`validate.py`** collapses straight to `validated`. Validate-first overshoots
the author ticket's target, which the done-gate then can't satisfy (it only advances *toward* the target,
never accepts "cell already at/beyond target").

**Suggested fix.** Either (1) the done-gate treats "cell maturity ≥ ticket target" as satisfied; or (2)
`validate.py` stops at the next legal step when an open author ticket exists; or (3) allow a single
`defined→validated` build ticket whose acceptance binds a validated rubric (one ticket spans author+validate).
As-is, the clean order is **close the author ticket `done` FIRST** (advances `defined→instantiated`), **then**
run `validate.py` (`instantiated→validated`) — validate-last, not validate-first.

**Workaround we used.** color-engine (validated-first): cancelled the subsumed author ticket as superseded.
Later cells: reorder to author → close-done (→instantiated) → validate (→validated).

### DF-6 · P2 — `validate.py` prints "→ validated" even when the cell did NOT advance · FIXED upstream + re-vendored (2026-06-15)

**Fixed in source.** harness-forge `validate.py` `run_validation` now reports the ACTUAL resulting maturity (`before → after`) and names the `regenerating` route when a passing verifier can't advance the cell to `validated` directly (e.g. a `stale` cell) — no more misleading `→ validated`. Re-vendored into dev-kernel; harness-forge 0.5.12.

**Symptom.** Re-validating a `stale` rubric cell, `validate.py … rubric.system.tonal-generation` printed
`PASS — rubric.system.tonal-generation → validated` and exited 0 — but the cell stayed **`stale`**. The
hardcoded success message hid the no-op; only inspecting `lattice.json` revealed maturity was unchanged.

**Root cause** (`dev-kernel/bin/validate.py`, `run_validation`). On a passing verifier it writes the signal,
then advances conditionally: `if cell["maturity"]=="defined": …="instantiated"; if transition_ok(maturity,"validated"): …="validated"`. But the return string is the literal `f"PASS — {cell_id} → validated …"`
**regardless of whether the transition fired.** From `stale`, `transition_ok(stale,"validated")` is False
(the FSM allows `stale → {regenerating, defined, deprecated}` only, `lattice.py:78`), so maturity is left
`stale` while the message claims `validated`. A fresh signal is appended to a still-stale cell.

**Suggested fix.** (1) Report the **actual** resulting maturity: `f"PASS — {cell_id} signal minted; {old}→{cell['maturity']}"`, and when the requested advance didn't fire, say so + name the legal route
("`stale`→`validated` is illegal; route via `regenerating`"). (2) Better: a passing re-validation of a
`stale`/`regenerating` cell should auto-route `stale → regenerating → validated`, or `validate.py` should
refuse with guidance — not emit a misleading `PASS`. Today a caller trusting stdout believes a stale cell
was cleared when it wasn't.

**Workaround we used.** `seed_cell(maturity="regenerating")` (the legal `stale → regenerating` step), then
`validate.py` does `regenerating → validated`.

### DF-1 · P1 — a malformed ticket file poisons **every** `store.rebuild` (incl. server boot) · FIXED in source (2026-06-15)

**Fixed in source.** store.py `upsert_ticket` coerces every non-dict field to `{}` (one bad ticket can no longer brick `store.rebuild`/boot); `api.create_ticket` validates `target_transition` is a `{from,to}` dict at the source.

**Symptom.** `api.create_ticket(...)` with `target_transition="validated"` (a string) wrote the
ticket file, then threw `AttributeError: 'str' object has no attribute 'get'` from inside
`store.rebuild` → `upsert_ticket`. Worse: because `save_ticket` runs *before* the failed rebuild,
the malformed file stays on disk and **every later rebuild — including server boot — crashes** on
it until the file is hand-repaired.

**Root cause** (`dev-server/store.py:73,88`). `upsert_ticket` does `tt = t.get("target_transition", {})`
then `tt.get("from")`, `tt.get("to")` — assuming `target_transition` is a dict. A string value
(or any non-dict) makes `.get` throw, and the throw is unguarded so it aborts the whole replay.
`api.create_ticket` accepts `target_transition` without validating its shape.

**Suggested fix.** (1) `create_ticket` should validate/normalize `target_transition` to
`{"from","to"}` (reject or coerce a bare string) at write time — fail at the source, not at every
future rebuild. (2) `upsert_ticket` should be defensive: `tt = t.get("target_transition") or {}; if not isinstance(tt, dict): tt = {}` so one bad file can't brick the index. The "a corrupted index
is a rebuild, not a loss" property is undermined if a single bad *ticket* makes rebuild itself
non-terminating.

**Workaround we used.** Repaired the file to `{"from":"defined","to":"instantiated"}` (single legal
step) and rebuilt.

### DF-2 · P2 — `validate.py` advances `lattice.json` but does not re-project `index.db`; reboot didn't re-materialize · FIXED in source (2026-06-15)

**Fixed in source.** `app.py` boot now calls `store.rebuild(DIR)` after `init_instance` — it re-projects `lattice.json` + the ledger into the grid, so the RUNBOOK's "reboot re-materializes the index" is now literal.

**Symptom.** After `validate.py` drove a spec cell to `validated` (correct in `lattice.json` with
the signal), the board still showed it `defined` / `signal_count 0`. A full server **reboot did
not fix it** — it trusted the existing (stale) `index.db`. Only an explicit
`python3 store.py rebuild --dir …` re-projected it.

**Root cause / discrepancy.** `validate.py` writes the substrate (`lattice.json` + signal) but never
calls `store.rebuild`, and boot's materialization didn't re-derive cell maturity from the updated
`lattice.json`. This contradicts the RUNBOOK's claim that re-booting "re-materializes the index from
the ledger + files." Net: a validated cell is invisible on the board until a manual rebuild.

**Suggested fix.** Either have `validate.py` call `store.rebuild` after a successful advance (it's a
kernel script, but the cell *did* change), or make boot unconditionally re-project `lattice.json`
into the grid, or document "run `store.py rebuild` after `validate.py`" in the RUNBOOK. The
single-writer story is otherwise clean — this is the one place a substrate write doesn't reach the
projection.

### DF-3 · P2 — agent model tier `deep` is unresolvable → spec-council / rubric-architect / critics fail to launch · FIXED in source (2026-06-15)

**Fixed in source.** the 11 agents' `model: deep/fast` remapped to resolvable `opus/sonnet` (the dev-server adapter's `small/mid/large`→model map was already concrete; this was the Task-tool/orchestrator path).

**Symptom.** Dispatching `dev-kernel:spec-council` failed: *"issue with the selected model (deep) —
it may not exist or you may not have access."* The deep-tier critic/architect agents
(`rubric-architect`, `critic-*`, `spec-architect`) carry the same tier and would hit it too.

**Workaround.** Dispatched the lens-critics and `rubric-architect` directly with an explicit model
override, which works. But the **orchestrator** agents (`spec-council`, `plugin-council`) that fan
out internally can't be overridden from the caller, so they're unusable as-is in this environment.

**Suggested fix.** Make the `deep` tier alias resolve to a concrete model in the agent frontmatter
(or document the required model mapping), and let orchestrators pass a resolvable model to their
fan-out. Otherwise the council path — the adversarial half of REVIEW — is dead on arrival wherever
`deep` isn't provisioned.

### DF-4 · P3 — kit verifiers (`rubric-check.py`, `spec-quality-check.py`, `doc-check.py`) aren't discoverable from inside an instance · FIXED in source (2026-06-15)

**Fixed in source.** `dispatch.py` now `--add-dir`s the bound kit (`DEV_FACTORY_KIT`, read-only) so a worker can locate + RUN the kit's `bin/` meta-verifiers instead of self-attesting.

**Symptom.** A `rubric-architect` agent reported it *could not find* `rubric-check.py` "inside the
`.agents/dev-factory/` instance — the Python harness tree is unmaterialized," and validated its
output by hand instead of running the real gate. The checkers live in the **plugin source**
(`dev-kit-corpus/bin/`), not in the instance.

**Suggested fix.** Give agents a stable way to locate the kit `bin/` (e.g. a `DEV_KERNEL_BIN` /
`DEV_KIT_BIN` env the dispatcher already sets for the server, surfaced to agents; or a documented
absolute path in the agent mandate). As-is, an agent that can't find its meta-verifier will
self-attest — exactly the generator/critic split the kernel is built to prevent.

### DF-5 · P3 — minor API ergonomics (`create_ticket` / `transition_ticket`) · FIXED in source (2026-06-15)

**Fixed in source.** `create_ticket`'s docstring documents the `{from,to}` single-step + `{kind,id}` actor shapes; the `target_transition` shape is validated at the source (DF-1).

- `target_transition` must be `{"from","to"}` — unvalidated at `create_ticket` (root of DF-1).
- `actor` must be `{"kind","id"}` — `ledger.append` raises a bare `ValueError` on a string; correct
  but undocumented in the `transition_ticket` signature.
- Maturity transitions are single-step (`defined→validated` is rejected as "illegal maturity
  transition"); a ticket must target one legal step (`defined→instantiated`, then
  `instantiated→validated`). Sensible, but worth a one-line note in the API/ticket docs.
