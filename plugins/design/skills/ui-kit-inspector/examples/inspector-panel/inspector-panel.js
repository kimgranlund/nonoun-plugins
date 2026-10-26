// inspector-panel.js: a schema-driven parameter panel (jig) with validation, persistence and an element inspector.
// No third-party runtime dependencies. createInspectorPanel({ mount, schema, defaults, render, ... }) builds the controls from the schema,
// owns the config, and calls render(config) whenever it changes and passes validation.

import { panelGeometry } from './panel-geometry.js';

const clone = (o) => JSON.parse(JSON.stringify(o));
const getp = (o, p) => p.reduce((a, k) => (a == null ? a : a[k]), o);
const setp = (o, p, v) => { p.slice(0, -1).reduce((a, k) => a[k], o)[p[p.length - 1]] = v; };
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);
const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);

// Recursively preserve the default shape, including objects and arrays inside arrays.
function merge(base, over) {
  if (Array.isArray(base)) {
    if (!Array.isArray(over) || over.length !== base.length) return base;
    return base.map((value, i) => merge(value, over[i]));
  }
  if (base && typeof base === "object") {
    if (!over || typeof over !== "object" || Array.isArray(over)) return base;
    for (const k of Object.keys(base)) {
      if (Object.hasOwn(over, k)) base[k] = merge(base[k], over[k]);
    }
    return base;
  }
  if (base === null) return base;
  return typeof over === typeof base && (typeof over !== "number" || Number.isFinite(over)) ? over : base;
}
const store = {
  get(k) { try { return JSON.parse(localStorage.getItem(k)); } catch { return null; } },
  set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch { /* storage unavailable: keep working in memory */ } },
};

/**
 * @param {object} o
 * @param {HTMLElement} o.mount       element the panel is built into
 * @param {Array} o.schema            [{ group, hint?, params: ParamSpec[] }]
 * @param {object} o.defaults         the default config; its shape is the only shape accepted
 * @param {(cfg, ctx) => void} o.render   synchronously draws into ctx.root; committed only on success
 * @param {(cfg) => Check[]} [o.validate] [{ id, level: "contract" | "property", pass, title, detail }]
 * @param {number} [o.version]        bump when a path's meaning changes; stored configs from other versions are ignored
 * @param {string} [o.storageKey]     persist the config under this key (omit to keep it in memory only)
 * @param {HTMLElement} o.outputRoot live output container; render must only mutate ctx.root
 * @param {Element} [o.inspectRoot]   where the inspector looks for [data-spec] elements (default: outputRoot)
 */
export function createInspectorPanel({ mount, title = "Inspector", schema, defaults, render, validate = () => [], version = 1, storageKey, outputRoot, inspectRoot = outputRoot, onChange, geometry = {} }) {
  if (!outputRoot || mount.contains(outputRoot) || outputRoot.contains(mount)) throw new Error("inspector-panel: supply separate mount and outputRoot elements");
  const panelStyle = panelGeometry(geometry);
  const events = new AbortController();
  const listen = (type, fn) => mount.addEventListener(type, fn, { signal: events.signal });
  const saved = storageKey ? store.get(storageKey) : null;
  let cfg = merge(clone(defaults), saved && saved.v === version ? saved.cfg : null);
  let checks = [], frameId = null, destroyed = false, hovered = null;
  const uid = Math.random().toString(36).slice(2, 7);
  const cid = (p) => `ip-${uid}-${p.join("-").replace(/[^\w-]/g, "_")}`;

  // ── Controls ────────────────────────────────────────────────────────────
  const attrs = (p) => `id="${cid(p.path)}" data-path='${esc(JSON.stringify(p.path))}' data-type="${p.type}"`;
  const field = (html, multiline = false) => `<div class="ip-field${multiline ? " ip-multiline" : ""}">${html}</div>`;
  const num = (p, label) => field(`<input type="number" ${attrs(p)}${p.min != null ? ` min="${p.min}"` : ""}${p.max != null ? ` max="${p.max}"` : ""} step="${p.step ?? "any"}" aria-label="${esc(label)}">`);
  function control(p) {
    const label = p.label + (p.unit ? ` (${p.unit})` : "");
    if (p.type === "number") return row(p, num(p, label));
    if (p.type === "select") return row(p, `<select ${attrs(p)}>${p.options.map(([l], i) => `<option value="${i}">${esc(l)}</option>`).join("")}</select>`);
    if (p.type === "toggle") return `<label class="ip-row ip-check"><input type="checkbox" ${attrs(p)}><span>${esc(label)}</span></label>`;
    if (p.type === "color") return row(p, `<input type="color" ${attrs(p)}>`);
    if (p.type === "text") return row(p, field(`<input type="text" ${attrs(p)} spellcheck="false">`));
    if (p.type === "range") return row(p, `<input type="range" ${attrs(p)} min="${p.min}" max="${p.max}" step="${p.step ?? 1}"><output for="${cid(p.path)}"></output>`);
    if (p.type === "matrix") {
      // rows: [[label, pathPrefix]], cols: [[label, key]]: one number cell per row × column, at [...pathPrefix, key].
      const head = `<span></span>${p.cols.map(([l]) => `<span class="ip-ch">${esc(l)}</span>`).join("")}`;
      const body = p.rows.map(([rl, pre]) => `<span class="ip-rh">${esc(rl)}</span>${p.cols.map(([cl, key]) =>
        num({ ...p, type: "number", path: [...pre, key] }, `${rl} ${cl}`)).join("")}`).join("");
      return `<div class="ip-matrix" role="group" aria-label="${esc(p.label)}" style="grid-template-columns:minmax(0,1.4fr) repeat(${p.cols.length},minmax(0,1fr))">${head}${body}</div>`;
    }
    throw new Error(`inspector-panel: unknown param type "${p.type}" at ${JSON.stringify(p.path)}`);
  }
  const row = (p, input) => `<div class="ip-row"><label for="${cid(p.path)}">${esc(p.label)}${p.unit ? ` <span class="ip-unit">${esc(p.unit)}</span>` : ""}</label>${input}</div>`;

  // Every param must point at a value the defaults have, with a matching type: fail loudly at build time.
  const specs = new Map();
  const TYPES = ["number", "range", "select", "toggle", "color", "text", "matrix"];
  for (const g of schema) for (const p of g.params) {
    if (!TYPES.includes(p.type)) throw new Error(`inspector-panel: unknown param type "${p.type}" at ${JSON.stringify(p.path)}`);
    const leaves = p.type === "matrix" ? p.rows.flatMap(([, pre]) => p.cols.map(([, k]) => ({ ...p, type: "number", path: [...pre, k] }))) : [p];
    for (const q of leaves) {
      const d = getp(defaults, q.path);
      const want = q.type === "toggle" ? "boolean" : q.type === "number" || q.type === "range" ? "number" : q.type === "select" ? typeof q.options[0][1] : "string";
      if (typeof d !== want) throw new Error(`inspector-panel: ${JSON.stringify(q.path)} is ${d === undefined ? "missing from defaults" : typeof d}, schema says ${want}`);
      if (q.type === "select" && !q.options.some(([, v]) => same(v, d))) throw new Error(`inspector-panel: default for ${JSON.stringify(q.path)} isn't one of its options`);
      specs.set(JSON.stringify(q.path), q);
    }
  }

  mount.innerHTML = `<details class="ip" open>
    <summary><span class="ip-title">${esc(title)}</span><span class="ip-count">defaults</span></summary>
    <div class="ip-status" role="status"></div>
    <div class="ip-banner" role="alert" hidden></div>
    <div class="ip-actions"><button type="button" data-act="reset"><span class="ip-label">Reset</span></button><button type="button" data-act="copy"><span class="ip-label">Copy JSON</span></button>
      <label class="ip-check"><input type="checkbox" data-act="inspect"><span>Inspect</span></label><span class="ip-msg" role="status"></span></div>
    <div class="ip-readout" aria-live="polite" hidden></div>
    ${schema.map((g) => `<section class="ip-group"><h2>${esc(g.group)}</h2>${g.hint ? `<p class="ip-hint">${esc(g.hint)}</p>` : ""}${g.params.map(control).join("")}</section>`).join("")}
    <details class="ip-adv"><summary>Config JSON</summary>${field(`<textarea spellcheck="false" aria-label="Config JSON"></textarea>`, true)}
      <div class="ip-actions"><button type="button" data-act="apply"><span class="ip-label">Apply</span></button></div></details>
  </details>`;
  for (const [key, value] of Object.entries(panelStyle)) mount.querySelector(".ip").style.setProperty(key, value);
  const panelElement = mount.querySelector(".ip");
  panelElement.dataset.keyboard = "true";
  // Track modality across entry into the panel; lifecycle belongs to this instance.
  mount.ownerDocument.addEventListener("keydown", (event) => {
    if (!event.metaKey && !event.ctrlKey && !event.altKey) panelElement.dataset.keyboard = "true";
  }, { capture: true, signal: events.signal });
  mount.ownerDocument.addEventListener("pointerdown", () => { panelElement.dataset.keyboard = "false"; }, { capture: true, signal: events.signal });
  const $ = (s) => mount.querySelector(s);
  const inputs = [...mount.querySelectorAll("[data-path]")];

  // ── Read a control, write the config ───────────────────────────────────
  function read(el) {
    const p = specs.get(el.dataset.path);
    if (p.type === "toggle") return el.checked;
    if (p.type === "select") return clone(p.options[+el.value][1]);
    if (p.type === "number" || p.type === "range") { const v = el.valueAsNumber; return Number.isFinite(v) ? v : undefined; }
    return el.value;
  }
  function write(el) {
    const p = specs.get(el.dataset.path), v = getp(cfg, p.path);
    el.removeAttribute("aria-invalid");
    if (p.type === "range") el.nextElementSibling.textContent = v;
    if (el === document.activeElement && p.type !== "select" && p.type !== "toggle" && read(el) === v) return; // don't fight the caret
    if (p.type === "toggle") el.checked = v;
    else if (p.type === "select") el.value = String(p.options.findIndex(([, o]) => same(o, v)));
    else el.value = v;
  }
  listen("input", (e) => {
    const el = e.target.closest("[data-path]");
    if (!el) return;
    const v = read(el);
    if (v === undefined) el.setAttribute("aria-invalid", "true");
    else el.removeAttribute("aria-invalid");
    if (v === undefined) return; // half-typed number: wait for a real one
    setp(cfg, specs.get(el.dataset.path).path, v);
    schedule();
  });

  // ── Update loop: validate → render (only if valid) → sync → persist ────
  const schedule = () => {
    if (!destroyed && frameId === null) frameId = requestAnimationFrame(() => { frameId = null; update(); });
  };
  function update() {
    if (destroyed) return;
    if (frameId !== null) { cancelAnimationFrame(frameId); frameId = null; }
    const failure = (id, title, err) => ({ id, level: "contract", pass: false, title, detail: String(err?.message || err) });
    try { checks = [...(validate(clone(cfg)) || [])]; }
    catch (err) { checks = [failure("V", "validate threw", err)]; }
    let failing = checks.filter((c) => c.level !== "property" && !c.pass);
    if (!failing.length) {
      try {
        const root = outputRoot.cloneNode(false);
        root.removeAttribute("id");
        const result = render(clone(cfg), { checks, root });
        if (result && typeof result.then === "function") {
          Promise.resolve(result).catch(() => {});
          throw new Error("render must be synchronous");
        }
        outputRoot.replaceChildren(...root.childNodes);
      } catch (err) { failing = [failure("R", "render threw", err)]; checks.push(failing[0]); }
    }
    const props = checks.filter((c) => c.level === "property"), contract = checks.filter((c) => c.level !== "property");
    $(".ip-status").textContent = checks.length ? `contract ${contract.length - failing.length}/${contract.length}${props.length ? ` · properties ${props.filter((c) => c.pass).length}/${props.length}` : ""}` : "";
    $(".ip-status").classList.toggle("bad", failing.length > 0);
    const banner = $(".ip-banner");
    banner.hidden = !failing.length;
    banner.innerHTML = failing.length ? `<strong>Output shows the last valid config.</strong><ul>${failing.map((c) => `<li><code>${esc(c.id)}</code> ${esc(c.title)}${c.detail ? `: ${esc(c.detail)}` : ""}</li>`).join("")}</ul>` : "";
    sync();
    if (storageKey) store.set(storageKey, { v: version, cfg });
    onChange && onChange(clone(cfg), checks);
  }
  function sync() {
    let changed = 0;
    for (const el of inputs) {
      write(el);
      const diff = !same(getp(cfg, specs.get(el.dataset.path).path), getp(defaults, specs.get(el.dataset.path).path));
      el.classList.toggle("ip-changed", diff);
      if (diff) changed++;
    }
    $(".ip-count").textContent = changed ? `${changed} changed` : "defaults";
    if (!$(".ip-adv textarea").matches(":focus")) $(".ip-adv textarea").value = JSON.stringify(cfg, null, 2);
  }

  // ── Actions ─────────────────────────────────────────────────────────────
  const msg = (t) => { if (!destroyed) $(".ip-msg").textContent = t; };
  listen("click", (e) => {
    const act = e.target.closest("[data-act]")?.dataset.act;
    if (act === "reset") { cfg = clone(defaults); update(); msg("Back to defaults."); }
    if (act === "copy") {
      const text = JSON.stringify(cfg, null, 2), ta = $(".ip-adv textarea");
      const fallback = () => { if (destroyed) return; ta.value = text; $(".ip-adv").open = true; ta.focus(); ta.select(); msg("Selected. Press Ctrl+C or ⌘C."); };
      try { navigator.clipboard.writeText(text).then(() => msg("Copied."), fallback); } catch { fallback(); }
    }
    if (act === "apply") {
      try { cfg = merge(clone(defaults), JSON.parse($(".ip-adv textarea").value)); $(".ip-adv textarea").blur(); update(); msg("Applied. Unknown keys and mistyped values were ignored."); }
      catch (err) { msg(`Not valid JSON: ${err.message}`); }
    }
  });
  listen("change", (e) => { if (e.target.dataset.act === "inspect") inspect(e.target.checked); });

  // ── Inspector: hover or focus any [data-spec] element outside the panel to read what it uses ──
  const readout = $(".ip-readout");
  const over = (e) => {
    const el = e.target.closest?.("[data-spec]");
    if (!el || mount.contains(el) || el === hovered) return;
    hovered?.classList.remove("ip-hovered");
    hovered = el; el.classList.add("ip-hovered");
    readout.textContent = el.dataset.spec;
  };
  const out = (e) => { if (hovered && !hovered.contains(e.relatedTarget)) { hovered.classList.remove("ip-hovered"); hovered = null; } };
  function inspect(on) {
    if (destroyed) return;
    $('[data-act="inspect"]').checked = on;
    readout.hidden = !on;
    readout.textContent = on ? "Hover or focus an element to see the values it uses." : "";
    inspectRoot.classList.toggle("ip-inspecting", on);
    for (const [t, f] of [["mouseover", over], ["focusin", over], ["mouseout", out], ["focusout", out]]) inspectRoot[on ? "addEventListener" : "removeEventListener"](t, f);
    if (!on) { hovered?.classList.remove("ip-hovered"); hovered = null; }
  }

  update();
  return {
    get: () => clone(cfg),
    set(path, value) { if (destroyed) return; setp(cfg, path, value); update(); },
    reset() { if (destroyed) return; cfg = clone(defaults); update(); },
    inspect,
    checks: () => checks.slice(),
    destroy() {
      if (destroyed) return;
      inspect(false);
      destroyed = true;
      events.abort();
      if (frameId !== null) cancelAnimationFrame(frameId);
      frameId = null;
      mount.replaceChildren();
    },
  };
}
