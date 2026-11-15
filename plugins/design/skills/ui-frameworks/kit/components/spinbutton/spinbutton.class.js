// @ts-check
/**
 * spinbutton.class.js: the spinbutton's class. Importing it defines no element; spinbutton.js does that.
 *
 * The root is a plain element around the author's native text input, the child marked data-part="input" (D14).
 * The input carries the name and the value and takes part in the form by itself; this class gives it the
 * spinbutton role and its values (J59), steps it from the keys and from two buttons it creates at the end of the
 * root (J60), and makes it invalid with setCustomValidity when its text is not a number or lies outside the
 * limits. It writes aria-invalid on the input, and invalid on its own root for the recipe, once the user is due to
 * be told, in the sense of J48: after the user changed the input and left it, or after a submit attempt.
 *
 * A limit is set when its attribute is present and is a number: a number prop reads 0 when it is absent, so the
 * class reads the attributes, not the props, for min and max. Everything is written by #sync(), synchronously, from
 * changed() and from the events, so a script sees the result in the same task.
 *
 * Rules: docs/specs/patterns.md, J59 to J61, and J48 that J60 cites.
 */
import { UIElement, setAttr } from '../../foundation/element.js';
import { props, parts, role, tabindex } from './spinbutton.props.js';

/** The names of the two buttons: messages.increase and messages.decrease in spinbutton.manifest.json. */
const NAMES = { increase: 'Increase', decrease: 'Decrease' };
/** What the browser shows for an invalid value: messages.notANumber, rangeUnderflow and rangeOverflow in the manifest. */
const NOT_A_NUMBER = 'Enter a number.';
/** @param {number} min */
const BELOW = (min) => `Enter a number of ${min} or more.`;
/** @param {number} max */
const ABOVE = (max) => `Enter a number of ${max} or less.`;
/** The keys that step, and by how many steps. Home and End go to a limit instead. */
const STEPS = /** @type {Record<string, number>} */ ({ ArrowUp: 1, ArrowDown: -1, PageUp: 10, PageDown: -10 });

/** The number a text says: null for an empty text, NaN for one that is not a number. @param {string} text */
const read = (text) => {
  const t = text.trim();
  if (t === '') return null;
  const n = Number(t);
  return Number.isFinite(n) ? n : NaN;
};
/** How many decimals a number is written with. @param {number} n */
const decimals = (n) => { const text = String(n); const dot = text.indexOf('.'); return dot === -1 ? 0 : text.length - dot - 1; };

/** Sets or removes an attribute, only when it differs. @param {Element} el @param {string} name @param {string | null} value */
const put = (el, name, value) => {
  if (el.getAttribute(name) === value) return;
  if (value === null) el.removeAttribute(name);
  else el.setAttribute(name, value);
};

export class UISpinbutton extends UIElement {
  static props = props;
  static parts = parts;
  static role = role;
  static tabindex = tabindex;

  /** The user has changed the input since it connected or since the form was reset. */
  #changed = false;
  /** The user is due to be told whether the input is invalid (J48). */
  #told = false;
  /** This class wrote the invalid mark on the input and the root. */
  #marked = false;
  /** The custom validity message this class set last. */
  #message = '';
  /** The input this class disabled, so that it enables only what it disabled. @type {HTMLInputElement | null} */
  #disabledInput = null;

  /** The author's input, a direct child marked data-part="input". */
  #input() {
    const el = this.ensurePart('input');
    return el instanceof HTMLInputElement ? el : null;
  }

  /** A limit, when its attribute is present and a number. @param {'min' | 'max'} name */
  #limit(name) {
    const text = this.getAttribute(name);
    return text === null || text.trim() === '' || Number.isNaN(+text) ? null : +text;
  }

  connected() {
    this.#sync();
    this.listen(this, 'keydown', (/** @type {KeyboardEvent} */ event) => this.#key(event));
    this.listen(this, 'input', (event) => { if (event.target === this.#input()) { this.#changed = true; this.#sync(); } });
    this.listen(this, 'focusout', (event) => {
      if (event.target !== this.#input()) return;
      if (this.#changed) this.#told = true;
      this.#sync();
    });
    // invalid does not bubble: the submit attempt reaches the root in the capture phase.
    this.listen(this, 'invalid', (event) => { if (event.target === this.#input()) { this.#told = true; this.#sync(); } }, { capture: true });
    // A press anywhere on the field but the input keeps focus in the input (J60) and puts it there (J47).
    const hold = (/** @type {Event} */ event) => {
      const input = this.#input();
      if (!input || event.target === input || !(event.target instanceof Node) || !this.contains(event.target)) return;
      event.preventDefault();
      if (!input.disabled && document.activeElement !== input) input.focus({ preventScroll: true });
    };
    this.listen(this, 'pointerdown', hold);
    this.listen(this, 'click', (event) => {
      const button = event.target instanceof Element ? event.target.closest('[data-part]') : null;
      if (!button || button.parentElement !== this) return;
      const name = button.getAttribute('data-part');
      if (name === 'increase') this.#step(1);
      else if (name === 'decrease') this.#step(-1);
    });
    // A reset restores the input after the event, so the state is read again in the next task.
    this.listen(document, 'reset', (event) => {
      const input = this.#input();
      if (!input || event.target !== input.form) return;
      this.#changed = this.#told = false;
      setTimeout(() => { if (this.isConnected) this.#sync(); });
    });
    // An input written or replaced after connect is found here.
    this.effect(() => {
      const observer = new MutationObserver(() => this.#sync());
      observer.observe(this, { childList: true });
      return () => observer.disconnect();
    });
  }

  /** min, max, step and disabled take effect in the same task. */
  changed() {
    if (this.isConnected) this.#sync();
  }

  /** Writes everything the input, the buttons and the root carry. */
  #sync() {
    const self = /** @type {any} */ (this);
    const input = this.#input();
    for (const name of /** @type {const} */ (['increase', 'decrease'])) {
      const button = this.ensurePart(name);
      if (!button) continue;
      if (!button.hasAttribute('aria-label') && !button.hasAttribute('aria-labelledby')) button.setAttribute('aria-label', NAMES[name]);
      put(button, 'aria-disabled', self.disabled ? 'true' : null);
    }
    if (!input) return;
    if (self.disabled) {
      if (!input.disabled) { input.disabled = true; this.#disabledInput = input; }
    } else if (this.#disabledInput) {
      this.#disabledInput.disabled = false;
      this.#disabledInput = null;
    }
    if (!input.hasAttribute('role')) input.setAttribute('role', 'spinbutton');
    if (!input.hasAttribute('inputmode')) input.setAttribute('inputmode', 'decimal');
    const min = this.#limit('min'), max = this.#limit('max');
    put(input, 'aria-valuemin', min === null ? null : String(min));
    put(input, 'aria-valuemax', max === null ? null : String(max));
    const n = read(input.value);
    put(input, 'aria-valuenow', n === null || Number.isNaN(n) ? null : String(n));
    const message = n === null ? '' : Number.isNaN(n) ? NOT_A_NUMBER : min !== null && n < min ? BELOW(min) : max !== null && n > max ? ABOVE(max) : '';
    if (message !== this.#message) { input.setCustomValidity(message); this.#message = message; }
    // Only a mark this class wrote is taken off: an author's aria-invalid and invalid stay as written.
    const shown = this.#told && !input.validity.valid;
    if (shown || this.#marked) {
      put(input, 'aria-invalid', shown ? 'true' : null);
      setAttr(this, 'invalid', shown);
      this.#marked = shown;
    }
  }

  /** @param {KeyboardEvent} event */
  #key(event) {
    const input = this.#input();
    if (!input || event.target !== input || event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) return;
    if (event.key in STEPS) {
      event.preventDefault();
      this.#step(STEPS[event.key]);
    } else if (event.key === 'Home' || event.key === 'End') {
      const limit = this.#limit(event.key === 'Home' ? 'min' : 'max');
      if (limit === null) return;
      event.preventDefault();
      this.#set(limit);
    }
  }

  /** Steps the value by count steps, held inside the limits. A step from an empty field starts at the minimum, or at 0. @param {number} count */
  #step(count) {
    const input = this.#input();
    if (!input) return;
    const self = /** @type {any} */ (this);
    const step = self.step > 0 ? /** @type {number} */ (self.step) : 1;
    const min = this.#limit('min');
    const n = read(input.value);
    if (n === null || Number.isNaN(n)) { this.#set(min ?? 0); return; }
    const places = Math.max(decimals(step), decimals(n));
    this.#set(Number((n + count * step).toFixed(places)));
  }

  /** Writes a value, held inside the limits, and dispatches input and change from the input when it changed. @param {number} value */
  #set(value) {
    const input = this.#input();
    if (!input || input.disabled || input.readOnly) return;
    const min = this.#limit('min'), max = this.#limit('max');
    let next = value;
    if (max !== null) next = Math.min(next, max);
    if (min !== null) next = Math.max(next, min);
    const text = String(next);
    if (input.value === text) return;
    input.value = text;
    input.dispatchEvent(new Event('input', { bubbles: true }));
    input.dispatchEvent(new Event('change', { bubbles: true }));
  }
}
