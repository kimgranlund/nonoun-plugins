/* ════════════════════════════════════════════════════════════════════════════
   dev-factory UI — a buildless, dependency-free single-page app over the
   dev-server's REST + SSE surface (TDD §9.3/§9.4). Vanilla web components on a
   tiny reactive base; OKLCH tokens live in styles.css.

   Architecture (mirrors the corpus-reader house style):
     • base.js-style reactivity inlined here: signal / effect / UIElement.
     • A single `store` of signals holds tickets / lattice / ledger / roadmap /
       activities + connection state. Views READ the store; the SSE client and
       fetches WRITE it. The board is the repo, projected — every render is a
       projection of git-tracked substrate the server materialized.
     • One <df-app> shell owns the store, the SSE subscription, and view switch.

   The UI never writes substrate directly: a Kanban drag POSTs a transition
   *request*; the gate runs server-side; a 409 is surfaced as a refusal reason.
   ════════════════════════════════════════════════════════════════════════════ */

// ═══════════════════ reactivity (compact signals + light-DOM base) ═══════════════════
const SIGNAL = Symbol("signal");
let tracking = null, pending = null, batching = false;

function notify(subs) {
  for (const s of subs) {
    if (s.disposed) { subs.delete(s); continue; }
    s.dirty = true;
    if (!pending) { pending = new Set(); if (!batching) queueMicrotask(flush); }
    pending.add(s);
  }
}
function flush() {
  let queue, loops = 0;
  while ((queue = pending)) {
    if (++loops > 100) { pending = null; console.error("signals: drain loop > 100"); break; }
    pending = null;
    for (const s of queue) {
      if (s.disposed || !s.dirty) continue;
      s.dirty = false;
      try { s.run(); } catch (e) { s.disposed = true; queueMicrotask(() => { throw e; }); }
    }
  }
}
export function batch(fn) {
  if (batching) return fn();
  batching = true;
  try { return fn(); } finally { batching = false; if (pending) flush(); }
}
function untracked(fn) { const p = tracking; tracking = null; try { return fn(); } finally { tracking = p; } }
export function signal(v) {
  const subs = new Set();
  return {
    [SIGNAL]: true,
    get value() { if (tracking) subs.add(tracking); return v; },
    set value(n) { if (Object.is(v, n)) return; v = n; notify(subs); },
    peek() { return v; },
  };
}
export function effect(fn) {
  const self = { dirty: false, disposed: false, run() { const p = tracking; tracking = self; try { fn(); } finally { tracking = p; } } };
  self.run();
  return () => { self.disposed = true; };
}

const escapeHtml = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const RAW = Symbol("raw");
export function raw(value) { return { [RAW]: String(value) }; }
function interp(v) {
  if (v == null || v === false || v === true) return "";
  if (Array.isArray(v)) return v.map(interp).join("");
  if (v && v[RAW] !== undefined) return v[RAW];
  return escapeHtml(v);
}
export function html(strings, ...values) {
  let out = strings[0];
  for (let i = 0; i < values.length; i++) out += interp(values[i]) + strings[i + 1];
  // Mark the result as trusted HTML so a nested html`…` is not re-escaped by an outer
  // template's interp(). Boxed String: interp() reads its RAW; everywhere else (innerHTML=,
  // Array.join, `${}`) it coerces back to a plain string.
  const safe = new String(out);
  safe[RAW] = out;
  return safe;
}

export class UIElement extends HTMLElement {
  #fx = [];
  #notify = signal(0);
  connectedCallback() {
    untracked(() => this.connected());
    this.#fx.push(effect(() => {
      this.#notify.value;
      const t = this.constructor.template ? this.constructor.template(this) : null;
      if (typeof t === "string" || t instanceof String) this.innerHTML = String(t);
      this.render();
    }));
  }
  disconnectedCallback() { for (const d of this.#fx) d(); this.#fx.length = 0; this.disconnected(); }
  requestUpdate() { this.#notify.value++; }
  connected() {}
  render() {}
  disconnected() {}
}

// ═══════════════════ vocab / color maps (status → hue class) ═══════════════════
const TICKET_STATES = ["draft", "active", "claimed", "in-progress", "in-review", "done", "blocked", "paused", "cancelled"];
const ACTIVITY_STATES = ["queued", "running", "handed-off", "completed", "blocked", "failed"];
const LAYERS = ["ontology", "spec", "rubric", "policy", "capability", "methodology", "protocol", "ledger", "pattern"];
const SCOPES = ["call", "task", "workflow", "system", "fleet"];
const MATURITIES = ["absent", "defined", "instantiated", "validated", "operating", "regenerating", "stale", "deprecated"];

// state → semantic hue class (drives the .st .h-* triad in styles.css)
const STATE_HUE = {
  draft: "h-caution", active: "h-positive", claimed: "h-info", "in-progress": "h-caution",
  "in-review": "h-accent", done: "h-positive", blocked: "h-alert", paused: "h-neutral", cancelled: "h-danger",
  queued: "h-neutral", running: "h-info", "handed-off": "h-accent", completed: "h-positive", failed: "h-danger",
};
const EVENT_HUE = {
  dispatch: "h-info", claim: "h-info", transition: "h-accent", signal: "h-positive",
  block: "h-alert", demote: "h-danger", regenerate: "h-accent",
  "activity-start": "h-info", handoff: "h-accent", "activity-complete": "h-positive", "activity-fail": "h-danger",
};
const hueFor = (state) => STATE_HUE[state] || "h-neutral";

// ═══════════════════ store + api client ═══════════════════
const API = ""; // same-origin; the dev-server serves both /api and this UI

const store = {
  view: signal(location.hash.slice(1) || "lattice"),   // the CANVAS mode — lattice|board|roadmap|agents|ledger
  lens: signal("ticket"),       // kanban lens: "ticket" | "agent"
  conn: signal("connecting"),   // "connecting" | "live" | "down"
  tickets: signal([]),
  lattice: signal([]),
  ledger: signal([]),
  roadmap: signal([]),
  activities: signal([]),       // future /api/activities; degrades to [] / ledger-derived
  agents: signal([]),           // future /api/agents/running; degrades to []
  heartbeat: signal(null),      // last tick summary from SSE
  factory: signal(null),        // UI-3: the factory-state headline from /api/status.factory (idle/running/armed/paused)
  milestones: signal(null),     // build-progress rollup from /api/status.milestones (SPEC · CAPABILITY · SHIP + spec revisions)
  adapter: signal("mock"),      // the dispatch adapter — "mock" (free) or "headless" (LIVE, spends tokens)
  guidance: signal({ items: [] }),  // the 5s operator-input buffer (run/guidance.json), streamed on the "guidance" event
  tokens: signal([]),           // the token-burn timeseries (15s snapshots), streamed on the "tokens" event
  clock: signal(Date.now()),    // a 1s tick driving live elapsed timers (no server round-trip)
  panel: signal(null),          // the INSPECTOR selection — { kind:"cell"|"ticket", id } (right-pane, persistent)
  inspectorTab: signal("cell"), // right-pane segmented tab — "cell" | "asset" | "signals" | "steer"
  runBudget: signal(null),      // the bounded-loop gauge from /api/status.run_budget (dispatches/cap + deadline)
  theme: signal(localStorage.getItem("df-theme") || "dark"),  // ◐ light/dark, persisted
  zoom: signal(1),              // canvas zoom (the canvas-header −/Fit/+ scales .canvas-scene)
  modal: signal(null),          // { kind:"create-ticket", state, mode:"structured"|"prompt"|"instruction" }
  toast: signal(null),
};

let _toastTimer = null;
function toast(title, msg, kind = "ok") {
  store.toast.value = { title, msg, kind, t: Date.now() };
  clearTimeout(_toastTimer);
  _toastTimer = setTimeout(() => (store.toast.value = null), kind === "err" ? 7000 : 3500);
}

async function jget(path) {
  const r = await fetch(API + path, { headers: { accept: "application/json" } });
  if (!r.ok) throw new Error(`${path} → ${r.status}`);
  return r.json();
}
async function jsend(method, path, body) {
  const r = await fetch(API + path, {
    method,
    headers: { "content-type": "application/json" },
    body: body == null ? undefined : JSON.stringify(body),
  });
  let data = null;
  try { data = await r.json(); } catch { /* empty body ok */ }
  return { ok: r.ok, status: r.status, data };
}

// Initial full load — each endpoint degrades independently so one empty/500 view
// never blanks the others (the "degrade gracefully when an endpoint is empty" rule).
async function loadAll() {
  const tries = [
    ["tickets", "/api/tickets"],
    ["lattice", "/api/lattice"],
    ["ledger", "/api/ledger"],
    ["roadmap", "/api/roadmap"],
    ["activities", "/api/activities"],   // future — 404 is fine
    ["agents", "/api/agents/running"],   // future — 404 is fine
    ["guidance", "/api/guidance"],       // the 5s operator-input buffer
    ["tokens", "/api/tokens"],           // the token-burn timeseries
  ];
  await Promise.all(tries.map(async ([key, path]) => {
    try { store[key].value = await jget(path); }
    catch { /* leave prior/empty value; views render an empty state */ }
  }));
  refreshStatus();
}

// UI-3: the factory-state headline (is it working, what is it doing) — distinct from the SSE socket dot.
// Also the milestone/build-progress rollup (where is the build, and has it shipped?).
async function refreshStatus() {
  try {
    const st = await jget("/api/status");
    store.factory.value = st.factory || null;
    store.milestones.value = st.milestones || null;
    store.adapter.value = st.adapter || "mock";
    store.runBudget.value = st.run_budget || null;
  } catch { /* leave prior value */ }
}

// the 5s operator-input buffer (also streamed on the "guidance" SSE event; this is the fetch fallback)
async function refreshGuidance() {
  try { store.guidance.value = await jget("/api/guidance"); }
  catch { /* leave prior value */ }
}

// ═══════════════════ SSE live wiring (no polling) ═══════════════════
// app.py: GET /api/stream emits `data: {"kind":"ticket"|"lattice"|"tick","payload":...}`.
// We patch the affected view in place; on drop we reconnect with backoff (degrade
// to a reconnecting state, never a full reload).
let _es = null, _backoff = 1000;
function connectStream() {
  store.conn.value = "connecting";
  try { _es = new EventSource(API + "/api/stream"); }
  catch { store.conn.value = "down"; return; }

  _es.onopen = () => { store.conn.value = "live"; _backoff = 1000; };
  _es.onmessage = (e) => {
    let evt;
    try { evt = JSON.parse(e.data); } catch { return; }
    applyStreamEvent(evt);
  };
  _es.onerror = () => {
    store.conn.value = "down";
    try { _es.close(); } catch {}
    _es = null;
    setTimeout(() => { connectStream(); refreshActive(); }, _backoff);
    _backoff = Math.min(_backoff * 2, 15000);
  };
}

function applyStreamEvent(evt) {
  const { kind, payload } = evt || {};
  if (kind === "ticket" && payload && payload.id) {
    // upsert the materialized ticket; also touch ledger/lattice opportunistically
    upsertTicket(payload);
  } else if (kind === "lattice" && Array.isArray(payload)) {
    store.lattice.value = payload;
  } else if (kind === "tick") {
    // heartbeat tick: { summary, lattice }
    if (payload && Array.isArray(payload.lattice)) store.lattice.value = payload.lattice;
    if (payload && payload.summary) store.heartbeat.value = payload.summary;
  } else if (kind === "guidance") {
    // the 5s operator-input poll streamed an updated guidance buffer
    if (payload && Array.isArray(payload.items)) store.guidance.value = payload;
  } else if (kind === "tokens") {
    // the 15s token-spend poll streamed a new snapshot — append (capped) for the realtime burn graph
    if (payload && payload.ts) store.tokens.value = [...store.tokens.value, payload].slice(-240);
  }
  // any committed write means the ledger advanced — pull the tail cheaply. The 15s `tokens` poll fires even
  // while a long headless tick is mid-flight in its worker thread, so refresh on it too — that's what keeps the
  // milestone strip, the worker cards, and the lattice grid live DURING a multi-minute dispatch (not just at tick-end).
  if (kind === "ticket" || kind === "tick" || kind === "tokens") { refreshLedger(); refreshStatus(); }
}

// The /api/stream ticket payload is the *file-of-record* shape (nested), while
// /api/tickets returns the *materialized flat* shape. Normalize to the flat
// shape the board renders so a streamed upsert and a fetched row look identical.
function flattenTicket(t) {
  if (!t || t.from_maturity !== undefined || t.target_cell === undefined && t.state === undefined) return t;
  const tt = t.target_transition || {};
  const cl = t.claim || {};
  return {
    id: t.id, type: t.type, title: t.title, state: t.state, target_cell: t.target_cell,
    from_maturity: tt.from, to_maturity: tt.to, rubric_cell: (t.acceptance || {}).rubric_cell,
    risk: (t.priority || {}).risk, unlock: (t.priority || {}).unlock, probe_cost: (t.priority || {}).probe_cost,
    claim_worker: cl.worker_id, lease_expiry: cl.lease_expiry, claimed_at: cl.claimed_at, signal_count: (t.signal_refs || []).length,
    created: (t.timestamps || {}).created, updated: (t.timestamps || {}).updated,
    budget: t.budget,
  };
}
function upsertTicket(raw) {
  const flat = flattenTicket(raw);
  const list = store.tickets.peek().slice();
  const i = list.findIndex((x) => x.id === flat.id);
  if (i >= 0) list[i] = { ...list[i], ...flat };
  else list.unshift(flat);
  store.tickets.value = list;
}

async function refreshLedger() {
  try { store.ledger.value = await jget("/api/ledger"); } catch {}
}
async function refreshActive() {
  // re-pull whatever the active view needs after a stream gap
  try { store.tickets.value = await jget("/api/tickets"); } catch {}
  try { store.lattice.value = await jget("/api/lattice"); } catch {}
  refreshLedger();
}

// ═══════════════════ small render helpers ═══════════════════
const chip = (text, hueClass, mono = false) =>
  html`<span class="chip st ${hueClass}${mono ? " mono" : ""}">${text}</span>`;
const fmtTime = (iso) => {
  if (!iso) return "—";
  try { const d = new Date(iso); return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" }); }
  catch { return iso; }
};
const shortId = (id) => (id ? String(id).replace(/^(tkt|epic|iss|act)-/, "$1-").slice(0, 12) : "");
const budgetFrac = (t) => {
  // no live consumption in Crawl; show a faint placeholder fraction if any progress data exists
  const b = t.budget || {};
  const used = (t.iterations_used || 0);
  const cap = b.iterations || 0;
  return cap ? Math.min(1, used / cap) : 0;
};

// continued in part 2 (views + components) …

// ═══════════════════ <df-app> — the app-shell cockpit ═══════════════════
// A three-pane creative-tool shell (ported from the ui-app HCT pattern): a switchable CANVAS framed by a
// persistent ANALYSIS rail (left) + INSPECTOR (right), with app-header/footer + canvas-header/footer chrome.
// The 5 old full-screen views become CANVAS MODES; the panes persist and adapt to the selected cell/ticket.
const CANVAS_MODES = [
  { id: "lattice", label: "Lattice", icon: "▦", tag: "df-lattice", graph: true },
  { id: "board",   label: "Board",   icon: "▤", tag: "df-kanban",  graph: false },
  { id: "roadmap", label: "Roadmap", icon: "⌖", tag: "df-roadmap", graph: true },
  { id: "agents",  label: "Agents",  icon: "◉", tag: "df-monitor", graph: false },
  { id: "ledger",  label: "Ledger",  icon: "≣", tag: "df-ledger",  graph: false },
];
const MODE_BY_ID = Object.fromEntries(CANVAS_MODES.map((m) => [m.id, m]));

const SHELL_HTML = (() => {
  const swtab = (m) => `<button data-view="${m.id}" title="${m.label} canvas">` +
    `<span aria-hidden="true">${m.icon}</span><span class="label">${m.label}</span></button>`;
  return `
    <div class="shell">
      <header class="app-header">
        <div class="brand"><span class="dia" aria-hidden="true">◆</span> dev-factory</div>
        <span class="docname" title="the build this factory is driving to SHIPPED">—</span>
        <div class="milestones" title="build milestones — where the build is, and whether it shipped"></div>
        <span class="spacer"></span>
        <span class="factory-state" title="the factory's work state"></span>
        <span class="adapter" title="dispatch adapter — mock is free, headless spends real tokens"></span>
        <button class="icon-btn theme-toggle" data-theme-toggle title="toggle light / dark" aria-label="Toggle theme">◐</button>
      </header>
      <aside class="left-pane"><df-analysis></df-analysis></aside>
      <section class="center">
        <div class="canvas-header">
          <nav class="canvas-switch" aria-label="Canvas view">${CANVAS_MODES.map(swtab).join("")}</nav>
          <span class="spacer"></span>
          <div class="canvas-tools" hidden>
            <button class="icon-btn" data-zoom="out" aria-label="Zoom out">−</button>
            <button class="zoom-readout" data-zoom="fit" title="Reset to 100%">100%</button>
            <button class="icon-btn" data-zoom="in" aria-label="Zoom in">+</button>
          </div>
          <button class="add-ticket" data-add-ticket title="Create a ticket / brief / instruction">+ Ticket</button>
        </div>
        <div class="canvas-area"><div class="canvas-scene" id="canvas-root"></div></div>
        <div class="canvas-footer"><span class="pulse-line"></span><span class="spacer"></span><span class="hints"></span></div>
      </section>
      <aside class="right-pane"><df-inspector></df-inspector></aside>
      <footer class="app-footer">
        <span class="counts"></span><span class="spacer"></span>
        <span class="conn" role="status" aria-live="polite"><span class="pulse" aria-hidden="true"></span><span class="conn-label"></span></span>
        <span class="warnings"></span>
      </footer>
    </div>
    <div id="overlay-root"></div>`;
})();

// DfApp owns NO static template — it builds the shell ONCE in connected() and patches each region via a SEPARATE
// effect. (The UIElement default effect would re-set innerHTML on every tracked read, recreating the persistent
// panes + the embedded steer input every data tick — so the live regions are patched in place instead, the same
// discipline DfSteer uses. The panes — df-analysis / df-inspector — are mounted once and own their own reactivity.)
class DfApp extends UIElement {
  connected() {
    this.innerHTML = SHELL_HTML;
    addEventListener("hashchange", () => (store.view.value = location.hash.slice(1) || "lattice"));
    this.#wireStatic();
    loadAll();
    connectStream();
    setInterval(() => (store.clock.value = Date.now()), 1000);   // drive live elapsed timers
    // one effect per live region — each reads only its own signals, patches its own DOM, never resets the shell
    this._fx = [
      effect(() => this.#applyTheme()),
      effect(() => this.#renderHeader()),
      effect(() => this.#renderCanvasSwap()),
      effect(() => this.#renderCanvasChrome()),
      effect(() => this.#renderFooters()),
      effect(() => this.#renderOverlays()),
    ];
  }
  disconnected() { (this._fx || []).forEach((d) => d()); }
  #wireStatic() {
    // these controls don't change with data — wire their handlers once
    this.querySelectorAll(".canvas-switch button").forEach((b) => (b.onclick = () => { location.hash = b.dataset.view; }));
    const tt = this.querySelector("[data-theme-toggle]");
    if (tt) tt.onclick = () => { const next = store.theme.peek() === "dark" ? "light" : "dark"; store.theme.value = next; localStorage.setItem("df-theme", next); };
    const add = this.querySelector("[data-add-ticket]");
    if (add) add.onclick = () => (store.modal.value = { kind: "create-ticket", state: "draft", mode: "structured" });
    this.querySelectorAll("[data-zoom]").forEach((b) => (b.onclick = () => {
      const z = store.zoom.peek();
      store.zoom.value = b.dataset.zoom === "in" ? Math.min(2, z + 0.1) : b.dataset.zoom === "out" ? Math.max(0.4, z - 0.1) : 1;
    }));
  }
  #applyTheme() {
    const t = store.theme.value;
    this.dataset.theme = t;
    document.documentElement.style.colorScheme = t;
  }
  #renderCanvasChrome() {
    const view = store.view.value, zoom = store.zoom.value;
    this.querySelectorAll(".canvas-switch button").forEach((b) =>
      b.setAttribute("aria-current", b.dataset.view === view ? "page" : "false"));
    const isGraph = !!(MODE_BY_ID[view] && MODE_BY_ID[view].graph);
    const tools = this.querySelector(".canvas-tools");
    if (tools) tools.hidden = !isGraph;
    const ro = this.querySelector(".zoom-readout");
    if (ro) ro.textContent = `${Math.round(zoom * 100)}%`;
    const scene = this.querySelector("#canvas-root");
    if (scene) scene.style.transform = isGraph && zoom !== 1 ? `scale(${zoom})` : "";
  }
  #renderHeader() {
    // docname — the app being built (derive from the spec/ship cell), so the header names the artifact
    const dn = this.querySelector(".docname");
    if (dn) {
      const cells = store.lattice.value;
      const spec = cells.find((c) => c.layer === "spec" && !String(c.slug).endsWith("-prd")) || cells.find((c) => c.layer === "spec");
      dn.textContent = spec ? spec.slug : (cells.length ? "build" : "—");
    }
    // factory-state headline (UI-3) — the WORK state the socket dot does not tell you
    const fs = store.factory.value;
    const fel = this.querySelector(".factory-state");
    if (fel) {
      if (fs && fs.state) {
        const a = fs.active_tickets ?? 0;
        const detail = fs.state === "running" ? `${fs.running_agents} worker${fs.running_agents === 1 ? "" : "s"}`
          : fs.state === "paused" ? "heartbeat paused"
          : fs.state === "armed" ? `${fs.ready_to_dispatch} ready`
          : fs.state === "blocked" ? `${a} queued · deps unmet`
          : fs.state === "drained" ? "queue empty"
          : (a ? `${a} queued · heartbeat off` : "no work queued");
        fel.dataset.state = fs.state;
        fel.textContent = `${fs.state.toUpperCase()} · ${detail}`;
      } else { fel.textContent = ""; fel.removeAttribute("data-state"); }
    }
    // milestone strip — PRD › SPEC › CAPABILITY › SHIP (+ the bi-directional spec-revision count)
    const ms = store.milestones.value;
    const mel = this.querySelector(".milestones");
    if (mel) {
      if (ms && ms.stages && ms.stages.length) {
        const stage = (s) => {
          const cls = s.done >= s.total ? "done" : s.done > 0 ? "wip" : "todo";
          const label = s.key === "ship" ? (s.done ? "SHIPPED" : "SHIP") : `${s.label} ${s.done}/${s.total}`;
          return `<span class="ms ${cls}">${escapeHtml(label)}</span>`;
        };
        const rev = ms.spec_revisions
          ? `<span class="ms-rev" title="spec revisions from build learnings (bi-directional)">⟲ ${ms.spec_revisions}</span>` : "";
        mel.innerHTML = ms.stages.map(stage).join('<span class="ms-sep">›</span>') + rev;
        mel.dataset.shipped = ms.shipped ? "1" : "0";
      } else { mel.innerHTML = ""; mel.removeAttribute("data-shipped"); }
    }
    // adapter badge — mock (free) vs ● LIVE (headless, spends real tokens)
    const adapter = store.adapter.value || "mock";
    const ael = this.querySelector(".adapter");
    if (ael) {
      ael.textContent = adapter === "headless" ? "● LIVE" : "mock";
      ael.dataset.adapter = adapter;
      ael.title = adapter === "headless"
        ? "headless adapter — the heartbeat dispatches real claude workers (spends tokens)"
        : "mock adapter — the free deterministic loop (no tokens)";
    }
  }
  #renderCanvasSwap() {
    const root = this.querySelector("#canvas-root");
    if (!root) return;
    const view = store.view.value;
    const tag = (MODE_BY_ID[view] || MODE_BY_ID.lattice).tag;
    if (root.firstElementChild?.localName !== tag) { root.innerHTML = ""; root.appendChild(document.createElement(tag)); }
  }
  #renderFooters() {
    // canvas-footer — the factory pulse + canvas hints
    const fs = store.factory.value, rb = store.runBudget.value, view = store.view.value;
    const pl = this.querySelector(".pulse-line");
    if (pl) {
      const bits = [];
      if (fs && fs.state) bits.push(fs.state);
      if (fs && fs.running_agents) bits.push(`${fs.running_agents} agent${fs.running_agents === 1 ? "" : "s"}`);
      if (rb && rb.max_dispatches) bits.push(`${rb.dispatches}/${rb.max_dispatches} dispatches`);
      else if (rb && rb.dispatches) bits.push(`${rb.dispatches} dispatches`);
      if (rb && rb.ticks) bits.push(`tick ${rb.ticks}`);
      pl.textContent = bits.length ? bits.join(" · ") : "Crawl — dispatch is human-driven (heartbeat off)";
      pl.dataset.state = (fs && fs.state) || "idle";
    }
    const hints = this.querySelector(".hints");
    if (hints) hints.textContent = MODE_BY_ID[view] && MODE_BY_ID[view].graph
      ? "click a cell to inspect · −/+ to zoom" : "click a card to inspect";
    // app-footer — counts + warnings
    const cells = store.lattice.value;
    const validated = cells.filter((c) => ["validated", "operating"].includes(c.maturity)).length;
    const blocked = cells.filter((c) => c.blocked).length;
    const stale = cells.filter((c) => c.stale).length;
    const counts = this.querySelector(".app-footer .counts");
    if (counts) counts.textContent = `${cells.length} cells · ${validated} validated · ${store.adapter.value || "mock"}`;
    const warn = this.querySelector(".app-footer .warnings");
    if (warn) {
      const w = [];
      if (blocked) w.push(`⚠ ${blocked} blocked`);
      if (stale) w.push(`⚠ ${stale} stale`);
      if (rb && rb.max_dispatches && rb.dispatches >= rb.max_dispatches) w.push("⚠ budget exhausted");
      warn.innerHTML = w.length ? w.join(" · ") : `<span class="ok">✓ no alarms</span>`;
      warn.classList.toggle("has-warn", w.length > 0);
    }
    // socket dot (the SSE transport, not the work state)
    const conn = store.conn.value;
    const cn = this.querySelector(".app-footer .conn");
    if (cn) { cn.dataset.state = conn; const l = cn.querySelector(".conn-label"); if (l) l.textContent = conn === "live" ? "live" : conn === "connecting" ? "connecting…" : "reconnecting…"; }
  }
  #renderOverlays() {
    const o = this.querySelector("#overlay-root");
    if (!o) return;
    // panel (inspector selection) is now the persistent right-pane; steer is an inspector tab. Only the modal +
    // toast remain true overlays — mount/unmount on presence change so an open modal's input survives data ticks.
    const want = { "df-modal": !!store.modal.value, "df-toast": !!store.toast.value };
    for (const [tag, on] of Object.entries(want)) {
      const existing = o.querySelector(tag);
      if (on && !existing) o.appendChild(document.createElement(tag));
      else if (!on && existing) existing.remove();
    }
  }
}
customElements.define("df-app", DfApp);

// derive a "live workers" list from claimed/in-progress tickets when /api/agents/running is absent
function liveWorkersFromTickets() {
  return store.tickets.value.filter((t) => ["claimed", "in-progress", "in-review"].includes(t.state) && t.claim_worker);
}

// live elapsed since an ISO timestamp (e.g. claimed_at) — drives the per-worker timer (reads store.clock)
function fmtElapsed(iso, now) {
  if (!iso) return null;
  const ms = (now || Date.now()) - new Date(iso).getTime();
  if (!(ms >= 0)) return null;
  const s = Math.floor(ms / 1000), h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60), sec = s % 60;
  return h ? `${h}h${String(m).padStart(2, "0")}m` : m ? `${m}m${String(sec).padStart(2, "0")}s` : `${sec}s`;
}

// ═══════════════════ LEFT PANE · analysis rail ═══════════════════
// Stacked telemetry cards (the HCT analysis-rail idea, for a factory): global build telemetry — run budget,
// token burn, maturity — then analysis of the SELECTED cell (its dependency cone + recent signals). All derived;
// no inputs/async children, so the framework's render-on-tick is safe here (unlike the inspector).
const _fmtTok = (n) => (n >= 1000 ? (n / 1000).toFixed(n >= 10000 ? 0 : 1).replace(/\.0$/, "") + "k" : String(Math.round(n || 0)));
const _tokSpark = (series, W, H) => {
  const n = series.length;
  if (n < 2) return "";
  const maxT = Math.max(1, ...series.map((s) => s.total_tokens || 0));
  const pts = series.map((s, i) => `${((i / (n - 1)) * W).toFixed(1)},${(H - ((s.total_tokens || 0) / maxT) * H).toFixed(1)}`);
  return `<svg class="an-spark" viewBox="0 0 ${W} ${H}" preserveAspectRatio="none" role="img" aria-label="token burn">` +
    `<path class="tk-area" d="M0,${H} L ${pts.join(" L ")} L ${W},${H} Z"/><path class="tk-line" fill="none" d="M ${pts.join(" L ")}"/></svg>`;
};

class DfAnalysis extends UIElement {
  static template = () => html`<div class="pane-label">ANALYSIS <span class="an-sel" id="an-sel"></span></div><div id="an-body"></div>`;
  render() {
    const body = this.querySelector("#an-body"), selEl = this.querySelector("#an-sel");
    if (!body) return;
    const cells = store.lattice.value, rb = store.runBudget.value, tokens = store.tokens.value || [];
    const latest = tokens[tokens.length - 1] || { total_tokens: 0, total_cost_usd: 0 };
    const p = store.panel.value;
    if (selEl) selEl.textContent = p ? p.id : "build overview";

    // run budget — the bounded-loop gauge (dispatches / cap + deadline countdown)
    let budgetCard;
    if (rb) {
      const frac = rb.max_dispatches ? Math.min(1, rb.dispatches / rb.max_dispatches) : 0;
      const remain = rb.deadline_ts ? Math.max(0, new Date(rb.deadline_ts).getTime() - store.clock.value) : null;
      const mins = remain != null ? Math.floor(remain / 60000) : null;
      const cls = frac > 0.85 ? "hot" : frac > 0.6 ? "warn" : "";
      budgetCard = html`<div class="an-card"><div class="an-label">Run budget</div>
        <div class="an-gauge"><div class="budget ${cls}"><span style="width:${Math.round(frac * 100)}%"></span></div>
          <span class="an-gv">${rb.dispatches}${rb.max_dispatches ? "/" + rb.max_dispatches : ""}</span></div>
        <div class="an-sub">${[rb.ticks ? `tick ${rb.ticks}` : "", mins != null ? `${mins}m left` : ""].filter(Boolean).join(" · ")}</div></div>`;
    } else {
      budgetCard = html`<div class="an-card"><div class="an-label">Run budget</div><div class="an-empty">Crawl — human-driven (no armed window)</div></div>`;
    }

    // token burn — cumulative spend + a sparkline
    const tokCard = html`<div class="an-card"><div class="an-label">Token burn</div>
      <div class="an-tok"><span class="an-gv">${_fmtTok(latest.total_tokens)}</span><small>tok · $${(latest.total_cost_usd || 0).toFixed(2)}</small></div>
      ${tokens.length > 1 ? raw(_tokSpark(tokens, 240, 46)) : html`<div class="an-empty">no snapshots yet (15s)</div>`}</div>`;

    // maturity distribution — the lattice at a glance
    const counts = {};
    for (const c of cells) counts[c.maturity || "absent"] = (counts[c.maturity || "absent"] || 0) + 1;
    const present = MATURITIES.filter((m) => counts[m]);
    const segs = present.map((m) => `<span class="mat-seg mat-${m}" style="flex:${counts[m]}" title="${m}: ${counts[m]}"></span>`).join("");
    const matCard = html`<div class="an-card"><div class="an-label">Maturity · ${cells.length} cells</div>
      ${cells.length ? raw(`<div class="mat-bar">${segs}</div>`) : html`<div class="an-empty">empty lattice</div>`}
      <div class="an-legend">${raw(present.map((m) => `<span class="an-leg"><span class="an-leg-mark mat-${m}"></span>${m} ${counts[m]}</span>`).join(""))}</div></div>`;

    // selected-cell analysis — the dependency cone + recent signals
    let selCard = "";
    if (p && p.kind === "cell") {
      const c = cells.find((x) => (x.id || `${x.layer}.${x.scope}.${x.slug}`) === p.id);
      if (c) {
        const deps = c.depends_on || [];
        const dependents = cells.filter((x) => (x.depends_on || []).includes(p.id)).map((x) => x.id || `${x.layer}.${x.scope}.${x.slug}`);
        const sigs = store.ledger.value.filter((e) => (e.subject || {}).cell === p.id && e.event === "signal").slice(-5).reverse();
        const cone = (lbl, arr) => `<div class="cone-row"><b>${lbl}</b> ${arr.length ? arr.map((d) => `<code>${escapeHtml(d)}</code>`).join(" ") : '<span class="an-empty">—</span>'}</div>`;
        selCard = html`<div class="an-card sel"><div class="an-label">Dependency cone</div>
          <div class="cone">${raw(cone("needs", deps))}${raw(cone("unlocks", dependents))}</div>
          <div class="an-label" style="margin-top:.55rem">Recent signals</div>
          ${sigs.length ? raw(`<ul class="an-sigs">${sigs.map((e) => `<li>${escapeHtml(e.rationale || "signal")}</li>`).join("")}</ul>`) : html`<div class="an-empty">none yet</div>`}</div>`;
      }
    }
    body.innerHTML = html`${budgetCard}${tokCard}${matCard}${selCard}`;
  }
}
customElements.define("df-analysis", DfAnalysis);

// ═══════════════════ RIGHT PANE · inspector (Cell · Asset · Signals · Steer) ═══════════════════
// The persistent inspector replaces the old floating panel. It is effect-based (skeleton once, regions patched)
// so the embedded Steer input + the async Asset content survive data ticks. Selection is store.panel; tab is
// store.inspectorTab. The Steer tab is ALWAYS available; Cell/Asset/Signals require a selection.
const INSPECTOR_TABS = [["cell", "Cell"], ["asset", "Asset"], ["signals", "Signals"], ["steer", "Steer"]];
class DfInspector extends UIElement {
  connected() {
    this.innerHTML = `
      <div class="pane-label">INSPECTOR <span class="an-sel" id="insp-sel"></span></div>
      <div class="seg insp-tabs" role="group" aria-label="Inspector tab">
        ${INSPECTOR_TABS.map(([id, lbl]) => `<button data-tab="${id}">${lbl}</button>`).join("")}
      </div>
      <div class="insp-body" id="insp-body"></div>`;
    this.querySelectorAll(".insp-tabs [data-tab]").forEach((b) => (b.onclick = () => (store.inspectorTab.value = b.dataset.tab)));
    this._fx = [
      effect(() => this.#tabs()),       // tab pressed/disabled + label — reads inspectorTab + panel
      effect(() => this.#bodyEffect()),  // the active tab's content — reads inspectorTab + panel + ledger
    ];
  }
  disconnected() { (this._fx || []).forEach((d) => d()); }
  #tabs() {
    const tab = store.inspectorTab.value, p = store.panel.value;
    const sel = this.querySelector("#insp-sel"); if (sel) sel.textContent = p ? p.id : "";
    this.querySelectorAll(".insp-tabs [data-tab]").forEach((b) => {
      b.setAttribute("aria-pressed", b.dataset.tab === tab ? "true" : "false");
      b.disabled = b.dataset.tab !== "steer" && !p;     // Steer is always open; the rest need a selection
    });
  }
  #bodyEffect() {
    const tab = store.inspectorTab.value, p = store.panel.value;
    const body = this.querySelector("#insp-body"); if (!body) return;
    const key = `${tab}:${p ? p.kind + ":" + p.id : ""}`;
    // STEER — mount the embedded dock once; keep it across ticks so the input survives
    if (tab === "steer") { this.#mountSteer(body); this._key = key; return; }
    this.#unmountSteer(body);
    // ASSET is async — only refetch when the (tab, selection) changes, not on every ledger tick
    if (tab === "asset") {
      if (this._key !== key) { this._key = key; this.#asset(p, body); }
      return;
    }
    this._key = key;
    if (!p) { body.innerHTML = `<div class="an-empty insp-empty">Select a cell on the canvas or a card on the board to inspect it. The <b>Steer</b> tab is always open.</div>`; return; }
    if (tab === "cell") body.innerHTML = String(p.kind === "cell" ? DfPanel.cellBody(p.id) : DfPanel.ticketBody(p.id));
    else if (tab === "signals") body.innerHTML = String(this.#signals(p));
    body.querySelectorAll("[data-ticket]").forEach((el) => (el.onclick = () => selectInspector("ticket", el.dataset.ticket)));
    body.querySelectorAll("[data-cell]").forEach((el) => (el.onclick = () => selectInspector("cell", el.dataset.cell)));
    this.#wireCellActions(body, p);
  }
  #signals(p) {
    const key = p.kind === "cell" ? "cell" : "ticket";
    const evs = store.ledger.value.filter((e) => (e.subject || {})[key] === p.id).slice(-40).reverse();
    if (!evs.length) return html`<div class="an-empty insp-empty">No ledger events for <code>${p.id}</code> yet.</div>`;
    // two-row event card: [time ··· tag] on top, then the description in code font below
    return html`<ul class="insp-led">${raw(evs.map((e) => {
      const change = e.from || e.to ? (e.from || "∅") + "→" + (e.to || "∅") + (e.rationale ? " · " : "") : "";
      return `<li>` +
        `<div class="il-top"><span class="il-ts">${fmtTime(e.ts)}</span>` +
        `<span class="il-ev st ${EVENT_HUE[e.event] || "h-neutral"}">${escapeHtml(e.event)}</span></div>` +
        `<div class="il-d">${escapeHtml(change)}${escapeHtml(e.rationale || "")}</div>` +
        `</li>`;
    }).join(""))}</ul>`;
  }
  async #asset(p, body) {
    if (!p) { body.innerHTML = `<div class="an-empty insp-empty">Select a cell to view its authored asset.</div>`; return; }
    if (p.kind !== "cell") {
      const tc = (store.tickets.value.find((t) => t.id === p.id) || {}).target_cell;
      body.innerHTML = `<div class="an-empty insp-empty">This ticket targets ${tc ? `<a data-cell="${escapeHtml(tc)}" href="javascript:void 0">${escapeHtml(tc)}</a>` : "no cell"} — open that cell to view its asset.</div>`;
      body.querySelectorAll("[data-cell]").forEach((el) => (el.onclick = () => selectInspector("cell", el.dataset.cell)));
      return;
    }
    body.innerHTML = `<div class="an-empty insp-empty">Loading <code>${escapeHtml(p.id)}</code>…</div>`;
    try {
      const a = await jget(`/api/cells/${encodeURIComponent(p.id)}/asset`);
      if (store.panel.peek()?.id !== p.id || store.inspectorTab.peek() !== "asset") return;  // selection moved while fetching
      if (a.kind === "file") body.innerHTML = `<div class="asset-head"><code>${escapeHtml(a.asset_ref)}</code></div><pre class="asset-pre">${escapeHtml(a.content || "")}</pre>`;
      else if (a.kind === "dir") body.innerHTML = `<div class="asset-head"><code>${escapeHtml(a.asset_ref)}/</code> · ${a.files.length} files</div><ul class="asset-files">${(a.files || []).map((f) => `<li><code>${escapeHtml(f)}</code></li>`).join("")}</ul>`;
      else body.innerHTML = `<div class="an-empty insp-empty">No asset authored yet (${escapeHtml(a.kind)}).</div>`;
    } catch { body.innerHTML = `<div class="an-empty insp-empty">Could not load the asset.</div>`; }
  }
  #wireCellActions(body, p) {
    body.querySelectorAll("[data-act]").forEach((b) => (b.onclick = () => {
      const act = b.dataset.act, tid = b.dataset.ticket;
      if (act === "transition" && tid) requestTransition(tid, b.dataset.to);
    }));
  }
  #mountSteer(body) {
    if (body.querySelector("df-steer")) return;
    body.innerHTML = "";
    const s = document.createElement("df-steer");
    s.setAttribute("embedded", "");
    body.appendChild(s);
  }
  #unmountSteer(body) { const s = body.querySelector("df-steer"); if (s) s.remove(); }
}
customElements.define("df-inspector", DfInspector);

// select a cell/ticket into the inspector + jump to its detail tab (the canvas + panes use this everywhere)
function selectInspector(kind, id) {
  store.panel.value = { kind, id };
  if (store.inspectorTab.peek() === "steer") store.inspectorTab.value = "cell";
}

// ═══════════════════ VIEW 1 · Kanban (two lenses) ═══════════════════
class DfKanban extends UIElement {
  static template = () => {
    const lens = store.lens.value;
    return html`
      <div class="view-head">
        <h2>Kanban</h2>
        <span class="sub">a drag is a gate-checked transition request — refused with a reason if illegal</span>
        <span class="spacer"></span>
        <div class="seg" role="group" aria-label="Board lens">
          <button data-lens="ticket" aria-pressed="${lens === "ticket"}">Tickets</button>
          <button data-lens="agent" aria-pressed="${lens === "agent"}">Agents / Activity</button>
        </div>
      </div>
      <div id="kanban-body"></div>`;
  };
  render() {
    this.querySelectorAll(".seg button").forEach((b) => (b.onclick = () => (store.lens.value = b.dataset.lens)));
    const body = this.querySelector("#kanban-body");
    if (!body) return;
    if (store.lens.value === "ticket") this.#renderTicketLens(body);
    else this.#renderAgentLens(body);
  }

  #renderTicketLens(body) {
    const tickets = store.tickets.value;
    const byState = Object.fromEntries(TICKET_STATES.map((s) => [s, []]));
    for (const t of tickets) (byState[t.state] || (byState[t.state] = [])).push(t);
    body.className = "board";
    body.setAttribute("role", "list");
    body.innerHTML = TICKET_STATES.map((s) => this.#column(s, byState[s] || [])).join("");
    this.#wireDnD(body);
    body.querySelectorAll("[data-add]").forEach((b) =>
      (b.onclick = () => (store.modal.value = { kind: "create-ticket", state: b.dataset.add })));
    body.querySelectorAll(".card").forEach((c) =>
      (c.onclick = (e) => { if (!c.dataset.grabbing) selectInspector("ticket", c.dataset.id); }));
  }

  #column(state, items) {
    const h = hueFor(state);
    return html`
      <section class="col st ${h}" data-state="${state}" role="listitem" aria-label="${state} (${items.length})" style="background:var(--surface-sunken)">
        <header class="st ${h}">
          <span class="dot" aria-hidden="true"></span>
          <span class="name">${state}</span>
          <span class="count">${items.length}</span>
          <button class="add" data-add="${state}" title="Create ticket in ${state}" aria-label="Create ticket in ${state}">+</button>
        </header>
        <div class="stack">${raw(items.map((t) => this.#card(t)).join(""))}</div>
      </section>`;
  }

  #card(t) {
    const h = hueFor(t.state);
    const frac = budgetFrac(t);
    return html`
      <article class="card" tabindex="0" role="button" aria-roledescription="draggable ticket"
        draggable="true" data-id="${t.id}" data-state="${t.state}" aria-grabbed="false"
        aria-label="${t.title || t.id}, state ${t.state}. Press space to pick up, then arrow keys to move.">
        <div class="title">${t.title || raw("<em>untitled</em>")}</div>
        <div class="meta">
          ${raw(chip(t.type || "task", "h-neutral"))}
          ${t.target_cell ? html`<span class="cell">${t.target_cell}</span>` : ""}
        </div>
        ${t.from_maturity && t.to_maturity ? html`<div class="cell" style="margin-top:.25rem">${t.from_maturity} → ${t.to_maturity}</div>` : ""}
        ${frac > 0 ? html`<div class="budget ${frac > 0.85 ? "hot" : frac > 0.6 ? "warn" : ""}"><span style="width:${Math.round(frac * 100)}%"></span></div>` : ""}
        <div class="id">${shortId(t.id)}${t.claim_worker ? " · " + t.claim_worker : ""}</div>
        <div class="move-hint">Use ← → to move · Enter to drop · Esc to cancel</div>
      </article>`;
  }

  // Drag-and-drop + full keyboard accessibility. A drop = POST transition request.
  #wireDnD(board) {
    let dragId = null;
    board.querySelectorAll(".card").forEach((card) => {
      card.addEventListener("dragstart", (e) => {
        dragId = card.dataset.id; card.dataset.grabbing = "1";
        e.dataTransfer.setData("text/plain", dragId); e.dataTransfer.effectAllowed = "move";
      });
      card.addEventListener("dragend", () => { delete card.dataset.grabbing; dragId = null; board.querySelectorAll(".col").forEach((c) => c.classList.remove("drop-target")); });
      // keyboard pick-up / move
      card.addEventListener("keydown", (e) => this.#cardKey(e, card, board));
    });
    board.querySelectorAll(".col").forEach((col) => {
      col.addEventListener("dragover", (e) => { e.preventDefault(); col.classList.add("drop-target"); });
      col.addEventListener("dragleave", () => col.classList.remove("drop-target"));
      col.addEventListener("drop", (e) => {
        e.preventDefault(); col.classList.remove("drop-target");
        const id = e.dataTransfer.getData("text/plain") || dragId;
        if (id) requestTransition(id, col.dataset.state);
      });
    });
  }

  #cardKey(e, card, board) {
    const grabbed = card.getAttribute("aria-grabbed") === "true";
    if (e.key === " " || (e.key === "Enter" && !grabbed)) {
      e.preventDefault();
      if (!grabbed) { board.querySelectorAll(".card").forEach((c) => c.setAttribute("aria-grabbed", "false")); card.setAttribute("aria-grabbed", "true"); card.dataset.grabbing = "1"; }
      else this.#dropKey(card);
    } else if (grabbed && (e.key === "ArrowRight" || e.key === "ArrowLeft")) {
      e.preventDefault();
      const dir = e.key === "ArrowRight" ? 1 : -1;
      const i = TICKET_STATES.indexOf(card.dataset.target || card.dataset.state);
      const next = TICKET_STATES[Math.max(0, Math.min(TICKET_STATES.length - 1, i + dir))];
      card.dataset.target = next;
      card.setAttribute("aria-label", `${card.querySelector(".title")?.textContent} — will move to ${next}. Enter to confirm.`);
    } else if (e.key === "Enter" && grabbed) {
      e.preventDefault(); this.#dropKey(card);
    } else if (e.key === "Escape" && grabbed) {
      card.setAttribute("aria-grabbed", "false"); delete card.dataset.grabbing; delete card.dataset.target;
    }
  }
  #dropKey(card) {
    const to = card.dataset.target;
    card.setAttribute("aria-grabbed", "false"); delete card.dataset.grabbing;
    if (to && to !== card.dataset.state) requestTransition(card.dataset.id, to);
    delete card.dataset.target;
  }

  // ── Agent / activity lens — swimlanes per agent, activities in status columns ──
  #renderAgentLens(body) {
    body.className = "";
    const acts = store.activities.value.length ? store.activities.value : activitiesFromLedger();
    if (!acts.length) {
      body.innerHTML = html`<div class="empty"><strong>No activities yet.</strong>
        Activities materialize from the ledger's <code>activity-*</code> events once workers dispatch (Walk). The ticket lens is the coordination view meanwhile.</div>`;
      return;
    }
    // group by agent; build delegation tree by parent_activity
    const lanes = {};
    for (const a of acts) (lanes[a.agent || "—"] ||= []).push(a);
    body.className = "lanes";
    body.innerHTML = Object.entries(lanes).map(([agent, list]) => this.#lane(agent, list)).join("");
    body.querySelectorAll(".act-card .toggle").forEach((tg) =>
      (tg.onclick = () => { const k = tg.closest(".act-card").dataset.kids; body.querySelectorAll(`[data-parent="${k}"]`).forEach((el) => (el.hidden = !el.hidden)); }));
  }
  #lane(agent, list) {
    const byStatus = Object.fromEntries(ACTIVITY_STATES.map((s) => [s, []]));
    for (const a of list) (byStatus[a.status] || (byStatus[a.status] = [])).push(a);
    const cols = ACTIVITY_STATES.filter((s) => byStatus[s]?.length).map((s) => html`
      <div class="act-col">
        <h4>${raw(chip(s, hueFor(s)))} <span style="color:var(--faint)">${byStatus[s].length}</span></h4>
        ${raw(byStatus[s].map((a) => this.#actCard(a)).join(""))}
      </div>`).join("");
    return html`
      <section class="lane" aria-label="agent ${agent}">
        <header><span class="agent">${agent}</span>
          <span style="color:var(--faint);font-size:12px">${list.length} activities · max depth ${Math.max(0, ...list.map((a) => a.depth || 0))}</span>
        </header>
        <div class="activity-cols">${raw(cols)}</div>
      </section>`;
  }
  #actCard(a) {
    const frac = (a.progress || {}).budget_fraction || 0;
    const isChild = a.parent_activity != null;
    return html`
      <article class="act-card ${isChild ? "child" : ""}" data-kids="${a.id}" data-parent="${a.parent_activity || ""}" ${isChild ? "hidden" : ""}>
        <div class="k">${a.kind || "?"} ${a.team?.role ? raw(chip(a.team.role, "h-accent")) : ""}</div>
        ${a.cell ? html`<div class="cell">${a.cell}</div>` : ""}
        <div class="badges">
          ${a.orchestration_shape ? raw(chip(a.orchestration_shape, "h-info", true)) : ""}
          ${a.loop_strategy ? raw(chip(a.loop_strategy, "h-neutral", true)) : ""}
        </div>
        ${frac > 0 ? html`<div class="budget ${frac > 0.85 ? "hot" : frac > 0.6 ? "warn" : ""}"><span style="width:${Math.round(frac * 100)}%"></span></div>` : ""}
        ${(a.progress || {}).summary ? html`<div style="font-size:11px;color:var(--muted);margin-top:.3rem">${a.progress.summary}</div>` : ""}
      </article>`;
  }
}
customElements.define("df-kanban", DfKanban);

// Derive activity cards from ledger activity-* events when no /api/activities exists.
function activitiesFromLedger() {
  const seen = new Map();
  for (const e of store.ledger.value) {
    if (!String(e.event || "").startsWith("activity") && e.event !== "handoff" && e.event !== "dispatch") continue;
    const sub = e.subject || {};
    const id = (sub.ticket || "") + ":" + (sub.cell || "");
    const status = e.event === "activity-complete" ? "completed" : e.event === "activity-fail" ? "failed" : e.event === "handoff" ? "handed-off" : "running";
    seen.set(id, { id, agent: (e.actor || {}).id || "agent", kind: e.event.replace("activity-", ""), cell: sub.cell, ticket: sub.ticket, status, depth: 0, parent_activity: null, progress: {} });
  }
  return [...seen.values()];
}

// THE transition request: POST /api/tickets/{id}/transition {to}; 409 surfaces the gate's reason.
async function requestTransition(id, to) {
  const t = store.tickets.peek().find((x) => x.id === id);
  if (t && t.state === to) return;
  const res = await jsend("POST", `/api/tickets/${id}/transition`, { to });
  if (res.ok && res.data?.ok) {
    if (res.data.ticket) upsertTicket(res.data.ticket);
    toast("Transition applied", `${id} → ${to}`, "ok");
  } else {
    const reason = res.data?.reason || res.data?.detail || `HTTP ${res.status}`;
    if (res.data?.ticket) upsertTicket(res.data.ticket); // server returns the unchanged ticket
    toast("Transition refused", reason, "err");
  }
  refreshLedger();
}

// ═══════════════════ VIEW 2 · Lattice grid ═══════════════════
class DfLattice extends UIElement {
  static template = () => {
    const cells = store.lattice.value;
    return html`
      <div class="view-head">
        <h2>Lattice grid</h2>
        <span class="sub">9 layers × 5 scopes · colored by maturity, badged with signals + staleness · ${cells.length} cells</span>
      </div>
      <div id="lattice-body"></div>`;
  };
  render() {
    const body = this.querySelector("#lattice-body");
    if (!body) return;
    const cells = store.lattice.value;
    if (!cells.length) {
      body.innerHTML = html`<div class="empty"><strong>The lattice is empty.</strong>
        Seed cells via the kernel (<code>lattice.py</code>) or the API; this grid is a projection of <code>lattice.json</code>.</div>`;
      return;
    }
    const index = {};
    for (const c of cells) index[`${c.layer}.${c.scope}`] = (index[`${c.layer}.${c.scope}`] || []).concat(c);
    body.className = "lattice-wrap";
    const head = SCOPES.map((s) => html`<th scope="col">${s}</th>`).join("");
    const rows = LAYERS.map((layer) => {
      const tds = SCOPES.map((scope) => {
        const list = index[`${layer}.${scope}`] || [];
        if (!list.length) return html`<td><div class="cell empty-cell" aria-hidden="true"></div></td>`;
        return html`<td>${raw(list.map((c) => this.#cell(c)).join(""))}</td>`;
      }).join("");
      return html`<tr><th scope="row" class="row-h">${layer}</th>${raw(tds)}</tr>`;
    }).join("");
    body.innerHTML = html`
      <table class="lattice"><thead><tr><th></th>${raw(head)}</tr></thead>
        <tbody>${raw(rows)}</tbody></table>`;
    body.querySelectorAll(".cell[data-id]").forEach((el) =>
      (el.onclick = () => selectInspector("cell", el.dataset.id)));
  }
  #cell(c) {
    const id = c.id || `${c.layer}.${c.scope}.${c.slug}`;
    const mat = c.maturity || "absent";
    return html`
      <button class="cell st mat-${mat}" data-id="${id}"
        aria-label="${id}, ${mat}${c.stale ? ", stale" : ""}${c.blocked ? ", blocked" : ""}, ${c.signal_count || 0} signals">
        <div class="flags" aria-hidden="true">
          ${(["validated", "operating"].includes(mat) && c.signal_count && !c.stale) ? html`<span class="f ok" title="verified — its harness/critic signal passed">✓</span>` : ""}
          ${c.signal_count ? html`<span class="f" title="${c.signal_count} signal(s)">${c.signal_count}</span>` : ""}
          ${c.stale ? html`<span class="f" title="stale — must re-verify against the revised upstream">⚠</span>` : ""}
          ${c.blocked ? html`<span class="f" title="blocked">⛔</span>` : ""}
        </div>
        <div class="slug">${c.slug}</div>
        <div class="mat">${mat}</div>
      </button>`;
  }
}
customElements.define("df-lattice", DfLattice);

// ═══════════════════ VIEW 3 · Ledger feed (live append-only) ═══════════════════
class DfLedger extends UIElement {
  connected() { this._seen = new Set(); }
  static template = () => html`
    <div class="view-head">
      <h2>Ledger feed</h2>
      <span class="sub">append-only event stream — the source of truth every view projects · live via SSE</span>
      <span class="spacer"></span>
      <span class="conn-mini" style="font-size:12px;color:var(--faint)">${store.ledger.value.length} events</span>
    </div>
    <div id="feed"></div>`;
  render() {
    const feed = this.querySelector("#feed");
    if (!feed) return;
    const events = store.ledger.value;
    if (!events.length) {
      feed.innerHTML = html`<div class="empty"><strong>No ledger events yet.</strong> Dispatches, claims, transitions, and signals will stream here as work flows.</div>`;
      return;
    }
    feed.className = "feed";
    feed.setAttribute("role", "log");
    feed.setAttribute("aria-live", "polite");
    // newest last (append-only reads chronological); render newest first for the feed
    const rows = events.slice(-200).reverse();
    feed.innerHTML = rows.map((e, i) => this.#row(e, i)).join("");
  }
  #row(e, i) {
    const h = EVENT_HUE[e.event] || "h-neutral";
    const sub = e.subject || {};
    const subj = sub.ticket || sub.cell || "";
    const actor = e.actor ? `${e.actor.kind}:${e.actor.id}` : "";
    const change = e.from || e.to ? html` <span style="color:var(--faint)">${e.from || "∅"} → ${e.to || "∅"}</span>` : "";
    const key = `${e.ts}|${e.event}|${subj}`;
    const fresh = !this._seen.has(key);
    this._seen.add(key);
    if (this._seen.size > 1000) this._seen = new Set([...this._seen].slice(-500)); // bound the fresh-flash memo
    return html`
      <div class="ev ${fresh && i < 3 ? "fresh" : ""}">
        <span class="ts">${fmtTime(e.ts)}</span>
        <span class="ev-name">${raw(chip(e.event, h, true))}</span>
        <span class="detail">
          <span class="subj">${subj}</span>${raw(change)}
          ${e.rationale ? html` <span class="rat">· ${e.rationale}</span>` : ""}
          <span class="rat"> · ${actor}</span>
        </span>
      </div>`;
  }
}
customElements.define("df-ledger", DfLedger);

// ═══════════════════ VIEW 4 · Agent monitor ═══════════════════
class DfMonitor extends UIElement {
  static template = () => html`
    <div class="view-head">
      <h2>Agent monitor</h2>
      <span class="sub">the running slice — live workers, target cells, worktrees, delegation depth, budgets burning</span>
      <span class="spacer"></span>
      ${store.heartbeat.value ? raw(`<span class="chip st ${store.heartbeat.value.halted ? "h-alert" : "h-positive"}">heartbeat ${store.heartbeat.value.halted ? "halted" : "ticking"}</span>`) : raw('<span class="chip st h-neutral">heartbeat OFF (Crawl)</span>')}
    </div>
    <div id="mon-body"></div>`;
  render() {
    const body = this.querySelector("#mon-body");
    if (!body) return;
    // Prefer a real /api/agents/running payload; degrade to claimed/in-progress tickets.
    const live = store.agents.value.length ? store.agents.value : liveWorkersFromTickets();
    if (!live.length) {
      body.innerHTML = html`<div class="empty"><strong>No workers running.</strong>
        In Crawl the heartbeat is OFF and dispatch is human-driven; claimed/in-progress tickets and a future <code>/api/agents/running</code> feed appear here as workers run.</div>`;
      return;
    }
    body.className = "monitor-grid";
    body.innerHTML = live.map((w) => this.#worker(w)).join("");
    body.querySelectorAll("[data-cancel]").forEach((b) => (b.onclick = () => control(`/api/tickets/${b.dataset.cancel}`, "DELETE", "Cancel requested")));
    body.querySelectorAll("[data-checkpoint]").forEach((b) => (b.onclick = () => toast("Checkpoint", "checkpoint() is a dispatcher control stub (Walk)", "ok")));
  }
  #worker(w) {
    // w is either an /api/agents/running record or a flat ticket row
    const id = w.id || w.ticket || w.claim_worker;
    const agent = w.agent || w.claim_worker || "worker";
    const cell = w.cell || w.target_cell;
    const wt = w.worktree || (w.claim && w.claim.worktree) || "—";
    const depth = w.depth ?? 0;
    const b = w.budget || {};
    const used = w.progress || {};
    const gauge = (lbl, frac, val) => {
      const cls = frac > 0.85 ? "hot" : frac > 0.6 ? "warn" : "";
      return html`<div class="gauge"><span class="lbl">${lbl}</span>
        <div class="budget ${cls}"><span style="width:${Math.round((frac || 0) * 100)}%"></span></div>
        <span class="val">${val}</span></div>`;
    };
    const iFrac = b.iterations ? (used.iterations_used || 0) / b.iterations : 0;
    const tFrac = b.tokens ? (used.tokens_used || 0) / b.tokens : 0;
    const wFrac = (b.wallclock_seconds || b.wallclock) ? (used.wallclock_seconds || 0) / (b.wallclock_seconds || b.wallclock) : 0;
    const elapsed = fmtElapsed(w.claimed_at || (w.claim && w.claim.claimed_at), store.clock.value);
    const eta = w.probe_cost ? `~${_fmtTok(w.probe_cost)} tok est.` : null;
    const team = w.delegation_mode === "team" ? `team×${depth}` : (depth ? `depth ${depth}` : null);
    const orch = [w.orchestration_shape, team, w.model_tier].filter(Boolean).join(" · ");
    return html`
      <div class="worker">
        <header>
          <span class="agent">${agent}</span>
          ${cell ? raw(chip(cell, "h-info", true)) : ""}
          <span style="margin-left:auto;color:var(--faint);font-size:12px">${elapsed ? html`<span class="elapsed">⏱ ${elapsed}</span>` : ""}</span>
        </header>
        ${orch ? html`<div class="orch">${w.delegation_mode === "team" ? raw('<span class="team-dot" title="orchestrator-workers sub-agent team"></span>') : ""}${orch}${w.reasoning_effort ? html` · ${w.reasoning_effort}` : ""}</div>` : ""}
        <div class="kv">
          <span>ticket <code>${shortId(w.ticket || id)}</code></span>
          <span>worktree <code>${String(wt).split("/").slice(-1)[0] || wt}</code></span>
          ${eta ? html`<span>effort <code>${eta}</code></span>` : ""}
          ${w.lease_expiry || (w.claim && w.claim.lease_expiry) ? html`<span>lease <code>${fmtTime(w.lease_expiry || w.claim.lease_expiry)}</code></span>` : ""}
        </div>
        <div class="gauges">
          ${raw(gauge("iterations", iFrac, `${used.iterations_used || 0}/${b.iterations ?? "—"}`))}
          ${raw(gauge("tokens", tFrac, `${(used.tokens_used || 0).toLocaleString()}/${(b.tokens || 0).toLocaleString() || "—"}`))}
          ${raw(gauge("wall-clock", wFrac, `${used.wallclock_seconds || 0}s`))}
        </div>
        <div class="controls">
          <button class="btn sm danger" data-cancel="${w.ticket || id}">Cancel</button>
          <button class="btn sm" data-checkpoint="${w.ticket || id}">Checkpoint</button>
        </div>
      </div>`;
  }
}
customElements.define("df-monitor", DfMonitor);

async function control(path, method, okMsg) {
  const res = await jsend(method, path, null);
  if (res.ok) toast("Control", okMsg, "ok");
  else toast("Control failed", res.data?.detail || `HTTP ${res.status}`, "err");
  refreshActive();
}

// ═══════════════════ VIEW 5 · Roadmap & backlog ═══════════════════
class DfRoadmap extends UIElement {
  static template = () => html`
    <div class="view-head">
      <h2>Roadmap &amp; backlog</h2>
      <span class="sub">epics decomposing into tickets · issues awaiting triage · dependency order</span>
    </div>
    <div id="rm-body"></div>`;
  render() {
    const body = this.querySelector("#rm-body");
    if (!body) return;
    const epics = store.roadmap.value;
    const tickets = store.tickets.value;
    const byId = Object.fromEntries(tickets.map((t) => [t.id, t]));
    const issues = tickets.filter((t) => t.type === "issue" || (t.state === "draft" && !t.target_cell));
    let out = "";
    if (epics.length) {
      body.className = "roadmap";
      out += epics.map((ep) => this.#epic(ep, byId)).join("");
    } else {
      out += html`<div class="empty"><strong>No epics on the roadmap.</strong> The roadmap-planner decomposes a goal into a dependency-ordered ticket set; epics appear here as <code>coordination/roadmap/*.json</code>.</div>`;
    }
    out += this.#specIteration();
    out += html`<div class="backlog"><h3>Backlog · issues awaiting triage (${issues.length})</h3>
      ${issues.length ? raw(`<div class="tickets" style="display:grid;gap:.4rem">${issues.map((t) => this.#backlogRow(t)).join("")}</div>`)
        : raw('<div class="empty">No untriaged issues.</div>')}</div>`;
    body.innerHTML = out;
    body.querySelectorAll("[data-ticket]").forEach((el) => (el.onclick = () => selectInspector("ticket", el.dataset.ticket)));
  }
  // the bi-directional spec-iteration timeline — build learnings flowing UPSTREAM (regenerate) + the staleness
  // cascade DOWNSTREAM (stale-propagated), derived from the ledger. The first-class view of "we work both ways".
  #specIteration() {
    const revs = store.ledger.value.filter((e) => e.event === "regenerate" || e.event === "stale-propagated");
    if (!revs.length) return "";
    const n = revs.filter((e) => e.event === "regenerate").length;
    const rows = revs.slice(-12).reverse().map((e) => {
      const regen = e.event === "regenerate";
      return `<li><span class="si-ev ${regen ? "regen" : "prop"}">${regen ? "⟲ spec revised" : "→ propagated"}</span>` +
        ` <span class="si-rat">${escapeHtml(e.rationale || "")}</span><span class="si-ts">${fmtTime(e.ts)}</span></li>`;
    }).join("");
    return html`<div class="spec-iter"><h3>Spec iteration (bi-directional) · ${n} revision${n === 1 ? "" : "s"}</h3>
      <ul class="si-list">${raw(rows)}</ul></div>`;
  }
  #epic(ep, byId) {
    const members = (ep.tickets || []).map((id) => byId[id]).filter(Boolean);
    const done = members.filter((t) => t.state === "done").length;
    const frac = members.length ? done / members.length : 0;
    return html`
      <section class="epic">
        <header>
          ${raw(chip(ep.status || "draft", hueFor(ep.status === "done" ? "done" : ep.status === "blocked" ? "blocked" : "active")))}
          <span class="ttl">${ep.title}</span>
          <span class="prog" title="${done}/${members.length} done" style="margin-left:auto"><span style="width:${Math.round(frac * 100)}%"></span></span>
          <span style="color:var(--faint);font-size:12px">${done}/${members.length}</span>
        </header>
        <div class="body">
          ${ep.body ? html`<p>${ep.body}</p>` : ""}
          ${ep.target_cell ? html`<div class="cell" style="font-family:var(--mono);color:var(--faint);font-size:12px;margin-bottom:.5rem">target ${ep.target_cell}</div>` : ""}
          <div class="tickets">
            ${raw((ep.tickets || []).map((id, i) => {
              const t = byId[id];
              return html`<div class="tk" data-ticket="${id}" tabindex="0" role="button">
                <span class="dep">${i + 1}.</span>
                ${t ? raw(chip(t.state, hueFor(t.state))) : raw(chip("missing", "h-alert"))}
                <span class="tt">${t ? t.title : id}</span>
                <span class="dep">${shortId(id)}</span></div>`;
            }).join(""))}
          </div>
        </div>
      </section>`;
  }
  #backlogRow(t) {
    return html`<div class="tk" data-ticket="${t.id}" tabindex="0" role="button">
      ${raw(chip(t.type || "issue", "h-neutral"))}
      <span class="tt">${t.title || t.id}</span>
      <span class="dep">${shortId(t.id)}</span></div>`;
  }
}
customElements.define("df-roadmap", DfRoadmap);

// ═══════════════════ Tokens (full burn graph) — retained; the rail carries the live sparkline, this is the
// detailed breakdown view (reachable by hash #tokens; _fmtTok is defined once, up in the analysis rail) ═══════
class DfTokens extends UIElement {
  static template = () => {
    const series = store.tokens.value || [];
    const latest = series[series.length - 1] || { total_tokens: 0, total_cost_usd: 0, by_model: {}, by_effort: {}, workers: 0 };
    const W = 600, H = 200;
    const maxT = Math.max(1, ...series.map((s) => s.total_tokens || 0));
    const xs = (i) => (series.length > 1 ? (i / (series.length - 1)) * W : 0);
    const pathFor = (get) => series.map((s, i) => `${xs(i).toFixed(1)},${(H - ((get(s) || 0) / maxT) * H).toFixed(1)}`);
    const totalPts = pathFor((s) => s.total_tokens);
    const area = totalPts.length ? `M0,${H} L ${totalPts.join(" L ")} L ${(series.length > 1 ? W : 0)},${H} Z` : "";
    const totalLine = totalPts.length ? `M ${totalPts.join(" L ")}` : "";
    const modelKeys = Object.keys(latest.by_model || {});
    const modelLines = modelKeys.map((k) => {
      const pts = pathFor((s) => (s.by_model || {})[k]);
      return `<path class="tk-model" data-m="${escapeHtml(k)}" fill="none" d="${pts.length ? "M " + pts.join(" L ") : ""}"/>`;
    }).join("");
    const rows = (obj) => {
      const ents = Object.entries(obj || {}).sort((a, b) => b[1] - a[1]);
      const mx = Math.max(1, ...ents.map((e) => e[1]));
      return ents.map(([k, v]) =>
        `<div class="tk-bar"><span class="tk-k" data-k="${escapeHtml(k)}">${escapeHtml(k)}</span>` +
        `<div class="tk-track"><div class="tk-fill" data-k="${escapeHtml(k)}" style="width:${(v / mx * 100).toFixed(1)}%"></div></div>` +
        `<span class="tk-v">${_fmtTok(v)}</span></div>`).join("");
    };
    return html`
      <div class="view-head"><h2>Token burn</h2><span class="sub">cumulative spend · snapshot every 15s · attributed per model + effort</span></div>
      <div class="tk-summary">
        <span class="tk-total">${_fmtTok(latest.total_tokens)} <small>tokens</small></span>
        <span class="tk-cost">$${(latest.total_cost_usd || 0).toFixed(2)}</span>
        <span class="tk-workers">${latest.workers || 0} worker${latest.workers === 1 ? "" : "s"}</span>
      </div>
      ${series.length
        ? raw(`<svg class="tk-chart" viewBox="0 0 ${W} ${H}" preserveAspectRatio="none" role="img" aria-label="token burn over time">
            <path class="tk-area" d="${area}"/><path class="tk-line" d="${totalLine}" fill="none"/>${modelLines}</svg>`)
        : html`<p style="color:var(--faint)">No token snapshots yet — they record every 15s once the loop dispatches workers.</p>`}
      <div class="tk-breakdowns">
        <div class="tk-group"><h4>by model tier</h4>${raw(rows(latest.by_model))}</div>
        <div class="tk-group"><h4>by reasoning effort</h4>${raw(rows(latest.by_effort))}</div>
      </div>`;
  };
}
customElements.define("df-tokens", DfTokens);

// ═══════════════════ OVERLAY · side panel (cell + ticket detail) ═══════════════════
class DfPanel extends UIElement {
  connected() {
    this._onKey = (e) => { if (e.key === "Escape") this.#close(); };
    addEventListener("keydown", this._onKey);
  }
  disconnected() { removeEventListener("keydown", this._onKey); }
  #close() { store.panel.value = null; }
  static template = () => {
    const p = store.panel.value;
    if (!p) return "";
    const inner = p.kind === "cell" ? DfPanel.cellBody(p.id) : DfPanel.ticketBody(p.id);
    return html`
      <div class="scrim" data-close></div>
      <aside class="panel" role="dialog" aria-modal="true" aria-label="${p.kind} detail">
        <header>
          <h3>${p.id}</h3>
          <button class="btn ghost x" data-close aria-label="Close panel">✕</button>
        </header>
        <div class="body">${raw(inner)}</div>
      </aside>`;
  };
  render() {
    this.querySelectorAll("[data-close]").forEach((el) => (el.onclick = () => this.#close()));
    this.querySelector(".panel")?.focus?.();
    this.querySelectorAll("[data-ticket]").forEach((el) => (el.onclick = () => (store.panel.value = { kind: "ticket", id: el.dataset.ticket })));
  }

  static cellBody(id) {
    const c = store.lattice.value.find((x) => (x.id || `${x.layer}.${x.scope}.${x.slug}`) === id);
    if (!c) return html`<p class="empty">No such cell in the current lattice.</p>`;
    // tickets + activities targeting this cell
    const tks = store.tickets.value.filter((t) => t.target_cell === id);
    const led = store.ledger.value.filter((e) => (e.subject || {}).cell === id).slice(-12).reverse();
    return html`
      <dl>
        <dt>maturity</dt><dd>${raw(chip(c.maturity || "absent", `mat-${c.maturity || "absent"} st`))}</dd>
        <dt>layer · scope</dt><dd class="mono">${c.layer} · ${c.scope}</dd>
        <dt>signals</dt><dd>${c.signal_count || 0}</dd>
        <dt>flags</dt><dd>${c.stale ? "stale " : ""}${c.blocked ? "blocked " : ""}${!c.stale && !c.blocked ? "—" : ""}</dd>
        <dt>artifact</dt><dd class="mono">${c.asset_ref || "—"}</dd>
      </dl>
      <h4>Tickets targeting this cell (${tks.length})</h4>
      ${tks.length ? raw(`<ul>${tks.map((t) => `<li><a data-ticket="${t.id}" href="javascript:void 0">${escapeHtml(t.title || t.id)}</a> — ${t.state}</li>`).join("")}</ul>`) : raw('<p style="color:var(--faint)">none</p>')}
      <h4>Recent ledger (this cell)</h4>
      ${led.length ? raw(`<ul>${led.map((e) => `<li><code>${e.event}</code> ${e.from || ""}${e.to ? "→" + e.to : ""} — <span style="color:var(--faint)">${escapeHtml(e.rationale || "")}</span></li>`).join("")}</ul>`) : raw('<p style="color:var(--faint)">none</p>')}`;
  }
  static ticketBody(id) {
    const t = store.tickets.value.find((x) => x.id === id);
    if (!t) return html`<p class="empty">No such ticket.</p>`;
    const led = store.ledger.value.filter((e) => (e.subject || {}).ticket === id).slice(-12).reverse();
    return html`
      <dl>
        <dt>title</dt><dd>${t.title || "—"}</dd>
        <dt>type · state</dt><dd>${t.type} · ${raw(chip(t.state, hueFor(t.state)))}</dd>
        <dt>target cell</dt><dd class="mono">${t.target_cell || "—"}</dd>
        <dt>transition</dt><dd class="mono">${t.from_maturity || "∅"} → ${t.to_maturity || "∅"}</dd>
        <dt>rubric (acceptance)</dt><dd class="mono">${t.rubric_cell || "—"}</dd>
        <dt>claim</dt><dd class="mono">${t.claim_worker || "—"}</dd>
        <dt>signals</dt><dd>${t.signal_count || 0}</dd>
        <dt>updated</dt><dd>${fmtTime(t.updated)}</dd>
      </dl>
      <h4>Ledger (this ticket)</h4>
      ${led.length ? raw(`<ul>${led.map((e) => `<li><code>${e.event}</code> ${e.from || ""}${e.to ? "→" + e.to : ""} — <span style="color:var(--faint)">${escapeHtml(e.rationale || "")}</span></li>`).join("")}</ul>`) : raw('<p style="color:var(--faint)">none</p>')}`;
  }
}
customElements.define("df-panel", DfPanel);

// ═══════════════════ OVERLAY · create-ticket modal ═══════════════════
class DfModal extends UIElement {
  connected() {
    this._onKey = (e) => { if (e.key === "Escape") this.#close(); };
    addEventListener("keydown", this._onKey);
  }
  disconnected() { removeEventListener("keydown", this._onKey); }
  #close() { store.modal.value = null; }
  static template = () => {
    const m = store.modal.value;
    if (!m) return "";
    const mode = m.mode || "structured";
    const tab = (id, label) => `<button type="button" data-mode="${id}" aria-pressed="${mode === id}">${label}</button>`;
    const structured = html`
      <div class="field"><div class="row">
        <div class="field"><label for="ct-type">Type</label>
          <select id="ct-type" name="type">${raw(["feature", "task", "bug", "chore", "spike", "epic", "issue"].map((x) => `<option>${x}</option>`).join(""))}</select></div>
        <div class="field"><label for="ct-cell">Target cell</label><input id="ct-cell" name="target_cell" class="mono" placeholder="layer.scope.slug" autocomplete="off" /></div>
      </div></div>
      <div class="field"><div class="row">
        <div class="field"><label for="ct-from">From maturity</label>
          <select id="ct-from" name="from"><option value=""></option>${raw(MATURITIES.map((x) => `<option>${x}</option>`).join(""))}</select></div>
        <div class="field"><label for="ct-to">To maturity</label>
          <select id="ct-to" name="to"><option value=""></option>${raw(MATURITIES.map((x) => `<option>${x}</option>`).join(""))}</select></div>
      </div></div>
      <div class="field"><label for="ct-rubric">Acceptance rubric cell</label><input id="ct-rubric" name="rubric" class="mono" placeholder="rubric.scope.slug" autocomplete="off" /></div>
      <div class="field"><label for="ct-body">Body</label><textarea id="ct-body" name="body" rows="3"></textarea></div>`;
    const prompt = html`
      <p class="modal-hint">A free-form brief. The cold-start planner triages it into a spec, hydrated lattice cells, and structured build tickets.</p>
      <div class="field"><label for="ct-body">Brief</label><textarea id="ct-body" name="body" rows="6" required
        placeholder="e.g. A playable solitaire card game with drag-and-drop, score keeping, and a leaderboard."></textarea></div>`;
    const instruction = html`
      <p class="modal-hint">Literal steps — dispatched closer to verbatim and folded into the loop's guidance for the next worker.</p>
      <div class="field"><label for="ct-body">Instruction</label><textarea id="ct-body" name="body" rows="6" required
        placeholder="e.g. Use a standard 52-card deck; cap the leaderboard at the top 10."></textarea></div>`;
    const titleLabel = mode === "structured" ? "Title" : mode === "prompt" ? "Prompt title" : "Instruction title";
    const heading = mode === "structured" ? "ticket" : mode;
    return html`
      <div class="modal" role="dialog" aria-modal="true" aria-label="Create intake">
        <div class="sheet">
          <header><h3>New ${heading}${m.state && m.state !== "draft" && mode === "structured" ? html` <span style="color:var(--faint);font-weight:400">(will request → ${m.state})</span>` : ""}</h3></header>
          <div class="seg modal-tabs" role="group" aria-label="Intake mode">${raw(tab("structured", "Structured") + tab("prompt", "Prompt") + tab("instruction", "Instruction"))}</div>
          <form id="ct-form">
            <div class="field"><label for="ct-title">${titleLabel}</label><input id="ct-title" name="title" required autocomplete="off" /></div>
            ${mode === "prompt" ? prompt : mode === "instruction" ? instruction : structured}
          </form>
          <div class="actions">
            <button class="btn ghost" data-cancel>Cancel</button>
            <button class="btn primary" data-submit>${mode === "structured" ? "Create ticket" : mode === "prompt" ? "Create prompt" : "Create instruction"}</button>
          </div>
        </div>
      </div>`;
  };
  render() {
    this.querySelector("[data-cancel]")?.addEventListener("click", () => this.#close());
    this.querySelector("[data-submit]")?.addEventListener("click", () => this.#submit());
    // tab switch: change the mode on the modal signal (re-renders the form for that intake mode)
    this.querySelectorAll(".modal-tabs [data-mode]").forEach((b) =>
      b.addEventListener("click", () => { store.modal.value = { ...store.modal.value, mode: b.dataset.mode }; }));
    this.querySelector("#ct-title")?.focus();
    const form = this.querySelector("#ct-form");
    form?.addEventListener("submit", (e) => { e.preventDefault(); this.#submit(); });
  }
  async #submit() {
    const f = this.querySelector("#ct-form");
    if (!f.reportValidity()) return;
    const g = (n) => f.elements[n]?.value?.trim() || "";
    const mode = store.modal.value?.mode || "structured";
    let body;
    if (mode === "prompt" || mode === "instruction") {
      // free-form intake: no cell — a prompt parks for the planner, an instruction folds into guidance (server-side)
      body = { type: mode, title: g("title"), body: g("body"), created_by: "human" };
    } else {
      body = { type: g("type") || "task", title: g("title"), body: g("body"), created_by: "human" };
      if (g("target_cell")) body.target_cell = g("target_cell");
      if (g("from") || g("to")) body.target_transition = { from: g("from"), to: g("to") };
      if (g("rubric")) body.acceptance = { rubric_cell: g("rubric") };
    }
    const res = await jsend("POST", "/api/tickets", body);
    if (!res.ok) { toast("Create failed", res.data?.detail || `HTTP ${res.status}`, "err"); return; }
    const created = res.data;
    if (created) upsertTicket(created);
    const target = store.modal.value?.state;
    this.#close();
    const label = mode === "structured" ? "Ticket" : mode === "prompt" ? "Prompt" : "Instruction";
    toast(`${label} created`, `${created?.id || ""}${mode === "structured" ? " · draft" : " · intake"}`, "ok");
    // a structured "+" on a non-draft column requests the transition toward it (the gate decides)
    if (created && target && target !== "draft" && mode === "structured") requestTransition(created.id, "active");
    if (mode === "instruction") refreshGuidance();   // the server folded it into guidance; reflect it now
    refreshLedger();
  }
}
customElements.define("df-modal", DfModal);

// ═══════════════════ OVERLAY · toast ═══════════════════
class DfToast extends UIElement {
  static template = () => {
    const t = store.toast.value;
    if (!t) return "";
    return html`<div class="toast ${t.kind}" role="status" aria-live="${t.kind === "err" ? "assertive" : "polite"}">
      <div class="ttl">${t.title}</div>${t.msg ? html`<div class="msg">${t.msg}</div>` : ""}</div>`;
  };
}
customElements.define("df-toast", DfToast);

// ═══════════════════ DOCK · steer (the 5s operator-input channel) ═══════════════════
// A persistent corner dock: type guidance → POST /api/input; the server's 5s poll folds it into the
// guidance buffer the next dispatched worker reads, and streams it back here. The template is STATIC and
// the feed is patched by a SEPARATE effect (and the open/closed toggle is direct-DOM) so a guidance update
// every 5s never rebuilds the dock and never wipes what the operator is typing.
class DfSteer extends UIElement {
  connected() {
    this._open = false;
    this._fxFeed = effect(() => { const g = store.guidance.value; this.#patchFeed(g); });
  }
  disconnected() { this._fxFeed?.(); }
  // `embedded` (inside the inspector's Steer tab) drops the dock chrome + toggle — the feed + form, always open.
  static template = (el) => el.hasAttribute("embedded")
    ? html`
      <div class="steer embedded" data-open="true">
        <div class="steer-body">
          <header>Operator guidance <small>read every 5s · folded into the next worker</small></header>
          <ul class="steer-feed"></ul>
          <form class="steer-form" id="steer-form">
            <input id="steer-input" name="text" autocomplete="off" placeholder="Steer the loop… e.g. prioritise the leaderboard" />
            <button type="submit" class="btn primary" data-send>Send</button>
          </form>
        </div>
      </div>`
    : html`
      <div class="steer" data-open="false">
        <button type="button" class="steer-tab" data-toggle aria-expanded="false">
          <span class="dot" aria-hidden="true"></span> Steer <span class="n" hidden></span>
        </button>
        <div class="steer-body" hidden>
          <header>Operator guidance <small>read every 5s · folded into the next worker</small></header>
          <ul class="steer-feed"></ul>
          <form class="steer-form" id="steer-form">
            <input id="steer-input" name="text" autocomplete="off" placeholder="Steer the loop… e.g. prioritise the leaderboard" />
            <button type="submit" class="btn primary" data-send>Send</button>
          </form>
        </div>
      </div>`;
  render() {
    const wrap = this.querySelector(".steer");
    const tab = this.querySelector("[data-toggle]");
    const body = this.querySelector(".steer-body");
    if (tab && !tab._wired) {
      tab._wired = true;
      tab.addEventListener("click", () => {        // direct-DOM toggle — no requestUpdate, so the input survives
        this._open = !this._open;
        wrap.dataset.open = String(this._open);
        body.hidden = !this._open;
        tab.setAttribute("aria-expanded", String(this._open));
        if (this._open) this.querySelector("#steer-input")?.focus();
      });
    }
    const form = this.querySelector("#steer-form");
    if (form && !form._wired) {
      form._wired = true;
      form.addEventListener("submit", (e) => { e.preventDefault(); this.#send(); });
    }
    this.#patchFeed(store.guidance.peek());        // initial paint (untracked — the feed effect owns updates)
  }
  #patchFeed(g) {
    const feed = this.querySelector(".steer-feed");
    if (!feed) return;
    const items = ((g && g.items) || []).slice(-8);
    feed.innerHTML = items.length
      ? items.map((it) => `<li><span class="gt">${it.kind === "instruction" ? "▸" : "•"}</span> ${escapeHtml(it.text || "")}</li>`).join("")
      : '<li class="empty">No guidance yet — type to steer the loop; it folds into the next dispatched worker.</li>';
    const n = this.querySelector(".steer-tab .n");
    if (n) { n.textContent = items.length || ""; n.hidden = !items.length; }
  }
  async #send() {
    const input = this.querySelector("#steer-input");
    const text = (input?.value || "").trim();
    if (!text) return;
    const res = await jsend("POST", "/api/input", { text });
    if (!res.ok) { toast("Steer failed", res.data?.detail || `HTTP ${res.status}`, "err"); return; }
    input.value = "";
    refreshGuidance();                              // the server drains + streams "guidance"; refetch in case SSE is down
  }
}
customElements.define("df-steer", DfSteer);
