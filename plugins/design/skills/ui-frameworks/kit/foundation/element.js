// @ts-check
/**
 * element.js: UIElement, the base of every component in the Web Components target. It imports signals.js only.
 *
 * Rules: docs/specs/foundation.md, E1 to E8, L1 to L7, A1 to A4, P1 to P6.
 *
 * A component declares `static props` (generated from its manifest) and may declare `static parts`,
 * `static role` and `static tabindex`. It starts its bindings in `connected()` with `this.effect()`.
 * There is no render pass: a binding is an effect that writes one thing.
 */
import { signal, effect, scope, untracked } from './signals.js';

/**
 * @typedef {{ type: 'boolean' }
 *   | { type: 'string', default?: string }
 *   | { type: 'number', default?: number }
 *   | { type: 'enum', values: readonly string[], default: string }} Prop
 * @typedef {{ tag?: string, at?: 'start' | 'end', attrs?: Record<string, string>, lazy?: boolean }} Part
 *   A part the element creates when the author wrote none. A lazy part is created on the first ensurePart(), not on connect.
 * @typedef {(root: HTMLElement, options?: any) => () => void} Behaviour
 */

/** @param {string} name */
const attributeOf = (name) => name.replace(/[A-Z]/g, (c) => '-' + c.toLowerCase());

/** The value a prop has when nothing sets it. @param {Prop} p */
const defaultOf = (p) => (p.type === 'boolean' ? false : p.default ?? (p.type === 'number' ? 0 : ''));

/** From an attribute to a value. @param {Prop} p @param {string | null} text */
const parse = (p, text) => {
  if (p.type === 'boolean') return text !== null;
  if (text === null) return defaultOf(p);
  if (p.type === 'number') return text.trim() === '' || Number.isNaN(+text) ? defaultOf(p) : +text;
  if (p.type === 'enum') return p.values.includes(text) ? text : defaultOf(p);
  return text;
};

/** From a property write to a value of the prop's type. @param {Prop} p @param {unknown} value */
const coerce = (p, value) => {
  if (p.type === 'boolean') return !!value;
  return parse(p, value == null ? null : String(value));
};

/**
 * Sets, or with null or false removes, an attribute. For bindings that keep a managed attribute in step.
 * @param {Element} el @param {string} name @param {string | boolean | null | undefined} value
 */
export const setAttr = (el, name, value) => {
  if (value == null || value === false) el.removeAttribute(name);
  else el.setAttribute(name, value === true ? '' : value);
};

/**
 * Defines an element, unless the tag is already taken.
 * @param {string} tag @param {CustomElementConstructor} ctor @returns {boolean} False if the tag was taken.
 */
export const define = (tag, ctor) => {
  if (customElements.get(tag)) return false;
  customElements.define(tag, ctor);
  return true;
};

/** @type {WeakSet<Function>} Classes whose prop accessors are installed. */
const installed = new WeakSet();

export class UIElement extends HTMLElement {
  /** @type {Record<string, Prop>} */
  static props = {};
  /** @type {Record<string, Part>} */
  static parts = {};
  /** @type {string | null} The ARIA role written when the author wrote none. */
  static role = null;
  /** @type {number | null} The tabindex written when the author wrote none. */
  static tabindex = null;

  static get observedAttributes() { return Object.keys(this.props).map(attributeOf); }

  /** @type {Record<string, import('./signals.js').Signal<any>>} */
  #signals = {};
  /** @type {Record<string, unknown>} Properties set before the element was defined. */
  #early = {};
  /** @type {import('./signals.js').Scope | null} */
  #scope = null;
  /** @type {AbortController | null} */
  #abort = null;
  #connecting = false;
  #leftWhileConnecting = false;

  constructor() {
    super();
    const ctor = /** @type {typeof UIElement} */ (this.constructor);
    const self = /** @type {any} */ (this);
    if (!installed.has(ctor)) {
      installed.add(ctor);
      for (const name of Object.keys(ctor.props)) {
        Object.defineProperty(ctor.prototype, name, {
          configurable: true,
          /** @this {UIElement} */
          get() { return this.#signal(name).value; },
          /** @this {UIElement} @param {unknown} value */
          set(value) { this.#write(name, value); },
        });
      }
    }
    for (const name of Object.keys(ctor.props)) {
      if (Object.hasOwn(this, name)) { this.#early[name] = self[name]; delete self[name]; }
    }
  }

  /** @param {string} name */
  #prop(name) { return /** @type {typeof UIElement} */ (this.constructor).props[name]; }

  /** @param {string} name */
  #signal(name) { return (this.#signals[name] ??= signal(defaultOf(this.#prop(name)))); }

  /**
   * A property write: set the value, then make the attribute say the same. The attribute change comes back
   * through attributeChangedCallback with an equal value, which the signal ignores, so the two cannot echo.
   * @param {string} name @param {unknown} value
   */
  #write(name, value) {
    const p = this.#prop(name);
    const next = coerce(p, value);
    this.#signal(name).value = next;
    this.changed(name);
    const attribute = attributeOf(name);
    const text = next === defaultOf(p) ? null : next === true ? '' : String(next);
    if (this.getAttribute(attribute) !== text) setAttr(this, attribute, text);
  }

  /** @param {string} attribute @param {string | null} _before @param {string | null} text */
  attributeChangedCallback(attribute, _before, text) {
    const props = /** @type {typeof UIElement} */ (this.constructor).props;
    const name = Object.keys(props).find((n) => attributeOf(n) === attribute);
    if (!name) return;
    this.#signal(name).value = parse(props[name], text);
    this.changed(name);
  }

  connectedCallback() {
    if (this.#scope) return;
    const ctor = /** @type {typeof UIElement} */ (this.constructor);
    const self = /** @type {any} */ (this);
    const owner = (this.#scope = scope(this.localName));
    this.#abort = new AbortController();
    this.#connecting = true;
    try {
      for (const name of Object.keys(this.#early)) self[name] = this.#early[name];
      this.#early = {};
      if (ctor.role && !this.hasAttribute('role')) this.setAttribute('role', ctor.role);
      if (ctor.tabindex !== null && !this.hasAttribute('tabindex')) this.setAttribute('tabindex', String(ctor.tabindex));
      for (const name of Object.keys(ctor.parts)) if (!ctor.parts[name].lazy) this.ensurePart(name);
      owner.run(() => untracked(() => { this.setup(); this.connected(); }));
    } finally {
      this.#connecting = false;
      if (this.#leftWhileConnecting) {
        this.#leftWhileConnecting = false;
        if (!this.isConnected) this.#teardown();
      }
    }
    if (!this.hasAttribute('data-ready')) {
      requestAnimationFrame(() => { if (this.isConnected) this.setAttribute('data-ready', ''); });
    }
  }

  disconnectedCallback() {
    if (this.#connecting) this.#leftWhileConnecting = true;
    else this.#teardown();
  }

  /** Present so that Element.moveBefore() moves the element without a disconnect and a connect. */
  connectedMoveCallback() {}

  #teardown() {
    this.#scope?.dispose();
    this.#abort?.abort();
    this.#scope = this.#abort = null;
  }

  /** The component's hook. It runs once per connection, after props, managed defaults and parts are in place. */
  connected() {}

  /** The same hook for a base class such as UIFormElement. It runs just before connected(). */
  setup() {}

  /**
   * Called synchronously after a prop has changed, from its property or from its attribute.
   * @param {string} _name
   */
  changed(_name) {}

  /**
   * Runs fn now and again when a value it read changes, until the element disconnects.
   * @param {() => void | (() => void)} fn
   */
  effect(fn) {
    if (!this.#scope) throw new Error(`${this.localName}: effect() needs a connected element`);
    return this.#scope.run(() => effect(fn));
  }

  /**
   * Listens until the element disconnects.
   * @param {EventTarget} target @param {string} type @param {(event: any) => void} handler @param {AddEventListenerOptions} [options]
   */
  listen(target, type, handler, options) {
    if (!this.#abort) throw new Error(`${this.localName}: listen() needs a connected element`);
    target.addEventListener(type, handler, { ...options, signal: this.#abort.signal });
  }

  /**
   * Mounts a behaviour until the element disconnects.
   * @param {Behaviour} behaviour @param {any} [options]
   */
  use(behaviour, options) {
    if (!this.#abort) throw new Error(`${this.localName}: use() needs a connected element`);
    this.#abort.signal.addEventListener('abort', behaviour(this, options), { once: true });
  }

  /**
   * The part of that name: a child the author marked, or one created from `static parts` when there is none.
   * Look it up each time; do not keep the result. (The name `part` is taken: it is the browser's own property
   * for shadow parts.)
   * @param {string} name @returns {HTMLElement | null}
   */
  ensurePart(name) {
    for (const child of this.children) {
      if (child.getAttribute('data-part') === name) return /** @type {HTMLElement} */ (child);
    }
    const definition = /** @type {typeof UIElement} */ (this.constructor).parts[name];
    if (!definition) return null;
    const tag = definition.tag ?? 'span';
    if (tag.includes('-')) throw new Error(`${this.localName}: the part "${name}" must be a plain element, not <${tag}>`);
    const created = document.createElement(tag);
    created.setAttribute('data-part', name);
    for (const [attribute, value] of Object.entries(definition.attrs ?? {})) created.setAttribute(attribute, value);
    if (definition.at === 'start') this.prepend(created);
    else this.append(created);
    return created;
  }

  /**
   * Dispatches a bubbling, cancelable event. @param {string} type @param {unknown} [detail]
   * @returns {boolean} False if a listener cancelled it.
   */
  emit(type, detail) {
    return this.dispatchEvent(new CustomEvent(type, { detail, bubbles: true, cancelable: true }));
  }
}
