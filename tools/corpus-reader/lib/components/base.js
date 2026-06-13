/**
 * Minimal reactive light-DOM custom-element base for the corpus-reader.
 *
 * Self-contained, dependency-free, ~one file: a small signals system, string
 * `html` + constructable-stylesheet `css` helpers, and the `UIElement` base
 * (reactive properties with attribute reflect/parse, an effect-driven render
 * loop, and a clean lifecycle with automatic disposal).
 *
 * Usage:
 *   import { UIElement, html, css, signal, effect } from "./base.js";
 *
 *   class MyThing extends UIElement {
 *     static properties = { label: { type: String, default: "", reflect: true } };
 *     // Imperative: build/update DOM in render() (re-runs when any property changes).
 *     connected() { this.box = document.createElement("div"); this.append(this.box); }
 *     render()    { this.box.textContent = this.label; }
 *     // …or declarative: return a string from static template (set as innerHTML).
 *     // static template = (el) => html`<div>${el.label}</div>`;
 *   }
 *   customElements.define("my-thing", MyThing);
 */

// ════════════════════════════════════════════════════════════
// Signals — reactive primitives (zero DOM, microtask-batched)
// ════════════════════════════════════════════════════════════
const SIGNAL = Symbol("signal");

let tracking = null; // the subscriber currently running (for dependency capture)
let pending = null; // dirty subscribers queued for the next flush
let batching = false;

function notify(subs) {
  for (const s of subs) {
    if (s.disposed) {
      subs.delete(s);
      continue;
    }
    s.dirty = true;
    if (!pending) {
      pending = new Set();
      if (!batching) queueMicrotask(flush);
    }
    pending.add(s);
  }
}

function flush() {
  let queue;
  let loops = 0;
  while ((queue = pending)) {
    if (++loops > 100) {
      pending = null;
      console.error("signals: drain loop exceeded 100 iterations");
      break;
    }
    pending = null;
    for (const s of queue) {
      if (s.disposed || !s.dirty) continue;
      s.dirty = false;
      try {
        s.run();
      } catch (e) {
        if (s.onError) s.onError(e);
        else {
          s.disposed = true;
          queueMicrotask(() => {
            throw e;
          });
        }
      }
    }
  }
}

/** Run `fn` coalescing all signal writes into a single flush. */
export function batch(fn) {
  if (batching) return fn();
  batching = true;
  try {
    return fn();
  } finally {
    batching = false;
    if (pending) flush();
  }
}

/** Run `fn` without subscribing the current effect to anything it reads. */
export function untracked(fn) {
  const prev = tracking;
  tracking = null;
  try {
    return fn();
  } finally {
    tracking = prev;
  }
}

/** A writable reactive value. Read `.value` to subscribe, set `.value` to notify. */
export function signal(v) {
  const subs = new Set();
  return {
    [SIGNAL]: true,
    get value() {
      if (tracking) subs.add(tracking);
      return v;
    },
    set value(next) {
      if (Object.is(v, next)) return;
      v = next;
      notify(subs);
    },
    peek() {
      return v;
    },
  };
}

/** A derived value, recomputed lazily when its dependencies change. */
export function computed(fn) {
  const subs = new Set();
  let cached;
  let dirty = true;
  const self = {
    dirty: false,
    disposed: false,
    run() {
      dirty = true;
      notify(subs);
    },
  };
  return {
    [SIGNAL]: true,
    get value() {
      if (tracking) subs.add(tracking);
      if (dirty) {
        const prev = tracking;
        tracking = self;
        try {
          cached = fn();
          dirty = false;
        } finally {
          tracking = prev;
        }
      }
      return cached;
    },
    peek() {
      return cached;
    },
  };
}

/** Run `fn`, re-running it whenever a signal it read changes. Returns a disposer. */
export function effect(fn, opts) {
  const self = {
    dirty: false,
    disposed: false,
    host: opts?.host ?? null,
    onError: opts?.onError ?? null,
    run() {
      const prev = tracking;
      tracking = self;
      try {
        fn();
      } finally {
        tracking = prev;
      }
    },
  };
  self.run();
  return () => {
    self.disposed = true;
  };
}

export function isSignal(v) {
  return v != null && typeof v === "object" && v[SIGNAL] === true;
}

// ════════════════════════════════════════════════════════════
// Templates — string `html` (auto-escaped) + `css` stylesheet
// ════════════════════════════════════════════════════════════
const RAW = Symbol("raw");

const escapeHtml = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);

/** Mark a string as trusted HTML so `html` interpolates it verbatim (e.g. rendered markdown). */
export function raw(value) {
  return { [RAW]: String(value) };
}

function interpolate(v) {
  if (v == null || v === false || v === true) return "";
  if (Array.isArray(v)) return v.map(interpolate).join("");
  if (v && v[RAW] !== undefined) return v[RAW];
  return escapeHtml(v);
}

/** Tagged template → an HTML string. Interpolations are escaped; wrap with `raw()` to opt out. */
export function html(strings, ...values) {
  let out = strings[0];
  for (let i = 0; i < values.length; i++) out += interpolate(values[i]) + strings[i + 1];
  return out;
}

/** Tagged template → a constructable CSSStyleSheet (adopt via `static styles`). */
export function css(strings, ...values) {
  let text = strings[0];
  for (let i = 0; i < values.length; i++) text += values[i] + strings[i + 1];
  const sheet = new CSSStyleSheet();
  sheet.replaceSync(text);
  return sheet;
}

// ════════════════════════════════════════════════════════════
// UIElement — reactive light-DOM custom-element base
// ════════════════════════════════════════════════════════════
const SIG = Symbol("sig"); // per-instance Map<propName, signal>
const CH = Symbol("changed"); // per-instance Map<propName, oldValue>

function installProps(el, props) {
  el[CH] = new Map();
  el[SIG] = new Map();
  for (const [key, cfg] of Object.entries(props)) {
    const attr = cfg.attribute ?? key.toLowerCase();
    const type = cfg.type ?? String;
    const sig = signal(cfg.default ?? undefined);
    el[SIG].set(key, sig);
    Object.defineProperty(el, key, {
      get() {
        return sig.value;
      },
      set(v) {
        const old = sig.peek();
        if (Object.is(old, v)) return;
        el[CH].set(key, old);
        sig.value = v;
        if (cfg.reflect) reflectAttr(el, attr, v, type);
      },
      configurable: true,
    });
  }
}

function reflectAttr(el, name, v, type) {
  if (type === Boolean) v ? el.setAttribute(name, "") : el.removeAttribute(name);
  else if (v == null) el.removeAttribute(name);
  else el.setAttribute(name, String(v));
}

function parseAttr(v, type) {
  if (type === Boolean) return v !== null;
  if (type === Number) return v === null ? null : Number(v);
  return v;
}

function adoptStyles(ctor) {
  if (Object.hasOwn(ctor, "_styled")) return;
  ctor._styled = true;
  const styles = ctor.styles;
  if (!styles) return;
  const list = Array.isArray(styles) ? styles : [styles];
  document.adoptedStyleSheets = [...document.adoptedStyleSheets, ...list.filter((s) => !document.adoptedStyleSheets.includes(s))];
}

export class UIElement extends HTMLElement {
  static get properties() {
    return {};
  }
  static template = () => null;

  static get observedAttributes() {
    return Object.entries(this.properties).map(([k, c]) => c.attribute ?? k.toLowerCase());
  }

  #fx = []; // disposers for this element's effects
  #auto = []; // auto-disposed local signals (this.signal())
  #notify = signal(0); // manual re-render channel (requestUpdate)

  constructor() {
    super();
    installProps(this, this.constructor.properties);
  }

  connectedCallback() {
    const ctor = this.constructor;
    if (!ctor._tag) ctor._tag = this.localName;
    adoptStyles(ctor);
    // Setup runs untracked so an enclosing effect (e.g. a parent's render
    // appending this node) never subscribes to this element's signals.
    untracked(() => this.connected());
    this.#fx.push(
      effect(
        () => {
          for (const sig of this[SIG].values()) sig.value; // subscribe to every property
          this.#notify.value; // …and the manual channel
          const result = ctor.template ? ctor.template(this) : null;
          if (typeof result === "string") this.innerHTML = result;
          this.render();
          if (this[CH].size) {
            const changed = new Map(this[CH]);
            this[CH].clear();
            this.updated(changed);
          }
        },
        {
          host: this.localName,
          onError: this.onError ? (e) => this.onError(e) : null,
        },
      ),
    );
  }

  disconnectedCallback() {
    for (const dispose of this.#fx) dispose();
    this.#fx.length = 0;
    for (const s of this.#auto) s.value = undefined;
    this.#auto.length = 0;
    this.disconnected();
  }

  attributeChangedCallback(name, _old, val) {
    for (const [key, cfg] of Object.entries(this.constructor.properties)) {
      if ((cfg.attribute ?? key.toLowerCase()) === name) {
        this[key] = parseAttr(val, cfg.type ?? String);
        break;
      }
    }
  }

  /** Create an instance of this element with properties applied. */
  static create(props = {}) {
    const tag = (customElements.getName && customElements.getName(this)) || this._tag;
    if (!tag) throw new Error("component is not registered");
    const el = document.createElement(tag);
    for (const [k, v] of Object.entries(props)) el[k] = v;
    return el;
  }

  /** A local signal, automatically disposed when the element disconnects. */
  signal(v) {
    const s = signal(v);
    this.#auto.push(s);
    return s;
  }

  /** Force a re-render — for state the reactive properties don't capture. */
  requestUpdate() {
    this.#notify.value++;
  }

  // Lifecycle hooks (override as needed).
  connected() {}
  render() {}
  updated(_changed) {}
  disconnected() {}
}
