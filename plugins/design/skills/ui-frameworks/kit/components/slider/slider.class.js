// @ts-check
/**
 * slider.class.js: the slider's class. Importing it defines no element; slider.js does that.
 *
 * The root is the control (D9): a form-associated custom element with the slider role. Its track, fill and thumb
 * are drawn by the recipe as pseudo-elements, so this class creates no part. As the meter does, it hands the value's
 * share of the range, a number from 0 to 1, to the recipe as the private custom property --_share on the root's own
 * inline style; that is the one style it writes.
 *
 * Rules: J53 to J56 in docs/specs/patterns.md, F1 to F7 in docs/specs/foundation.md.
 *
 * The value it uses (aria-valuenow, the form value, the share) is held between min and max and on a step counted
 * from min; the value prop keeps what was written, as the meter's does. A max below min is min, and a step that is
 * not above 0 is 1. The user changes the value with the keys and the pointer; each such change dispatches input, and
 * change follows after each key and at the end of a pointer gesture. A change by a script dispatches neither.
 */
import { setAttr } from '../../foundation/element.js';
import { UIFormElement } from '../../foundation/form.js';
import { props, role, tabindex, resets } from './slider.props.js';

/** The decimals of a number as written, so that a step of 0.1 gives 0.3 and not 0.30000000000000004. @param {number} n */
const decimals = (n) => {
  const text = String(n), exp = text.indexOf('e-');
  if (exp !== -1) return Number(text.slice(exp + 2));
  const dot = text.indexOf('.');
  return dot === -1 ? 0 : text.length - dot - 1;
};

/** @typedef {{ min: number, max: number, step: number }} Range */

/** A number held between min and max and on a step counted from min: never below min, never above the last step at or below max. @param {number} v @param {Range} r */
const hold = (v, { min, max, step }) => {
  const places = Math.min(Math.max(decimals(min), decimals(step)), 12);
  const last = min + Math.floor((max - min) / step + 1e-9) * step;
  const steps = Math.round((Math.max(v, min) - min) / step);
  return Number(Math.min(min + steps * step, last).toFixed(places));
};

/** How many steps a key moves the value; Home and End are handled apart. @param {string} key @param {boolean} rtl */
const stepsOf = (key, rtl) => ({ ArrowRight: rtl ? -1 : 1, ArrowLeft: rtl ? 1 : -1, ArrowUp: 1, ArrowDown: -1, PageUp: 10, PageDown: -10 })[key];

export class UISlider extends UIFormElement {
  static props = props;
  static role = role;
  static tabindex = tabindex;
  static resets = resets;

  /** The range as it is used: max is never below min, and the step is above 0. @returns {Range} */
  #range() {
    const self = /** @type {any} */ (this);
    const min = /** @type {number} */ (self.min);
    const step = /** @type {number} */ (self.step);
    return { min, max: Math.max(/** @type {number} */ (self.max), min), step: step > 0 ? step : 1 };
  }

  /** The value as it is used. */
  #now() { return hold(/** @type {any} */ (this).value, this.#range()); }

  formValue() { return String(this.#now()); }

  /** @param {string | File | FormData | null} state */
  restore(state) {
    if (typeof state === 'string' && state.trim() !== '' && !Number.isNaN(Number(state))) /** @type {any} */ (this).value = Number(state);
  }

  /** Sets the value the user chose, held, and dispatches input if it changed. @param {number} next @returns {boolean} Whether it changed. */
  #choose(next) {
    const held = hold(next, this.#range());
    if (held === this.#now()) return false;
    /** @type {any} */ (this).value = held;
    this.dispatchEvent(new Event('input', { bubbles: true }));
    return true;
  }

  /** The value under the pointer: the thumb's centre runs from half a thumb after the start to half a thumb before the end. @param {PointerEvent} event */
  #at(event) {
    const self = /** @type {any} */ (this);
    const vertical = self.orientation === 'vertical';
    const r = this.getBoundingClientRect();
    const thumb = parseFloat(getComputedStyle(this, '::after').width) || 0;
    const rtl = !vertical && getComputedStyle(this).direction === 'rtl';
    const along = vertical ? r.bottom - event.clientY : rtl ? r.right - event.clientX : event.clientX - r.left;
    const length = (vertical ? r.height : r.width) - thumb;
    const share = length > 0 ? Math.min(Math.max((along - thumb / 2) / length, 0), 1) : 0;
    const { min, max } = this.#range();
    return min + share * (max - min);
  }

  connected() {
    const self = /** @type {any} */ (this);
    this.effect(() => setAttr(this, 'aria-valuemin', String(this.#range().min)));
    this.effect(() => setAttr(this, 'aria-valuemax', String(this.#range().max)));
    this.effect(() => setAttr(this, 'aria-valuenow', String(this.#now())));
    this.effect(() => setAttr(this, 'aria-orientation', self.orientation === 'vertical' ? 'vertical' : null));
    this.effect(() => {
      const { min, max } = this.#range();
      this.style.setProperty('--_share', String(max > min ? (this.#now() - min) / (max - min) : 0));
      return () => this.style.removeProperty('--_share');
    });

    this.listen(this, 'keydown', (/** @type {KeyboardEvent} */ event) => {
      if (this.effectiveDisabled || event.altKey || event.ctrlKey || event.metaKey) return;
      const { min, max, step } = this.#range();
      // Right to left swaps the left and right arrows of a horizontal slider; the direction is read now.
      const rtl = self.orientation !== 'vertical' && getComputedStyle(this).direction === 'rtl';
      const steps = stepsOf(event.key, rtl);
      const next = event.key === 'Home' ? min : event.key === 'End' ? max : steps === undefined ? null : this.#now() + steps * step;
      if (next === null) return;
      event.preventDefault();
      if (this.#choose(next)) this.dispatchEvent(new Event('change', { bubbles: true }));
    });

    /** @type {number | null} The value when the pointer went down, while a gesture runs. */
    let start = null;
    this.listen(this, 'pointerdown', (/** @type {PointerEvent} */ event) => {
      if (this.effectiveDisabled || event.button !== 0) return;
      start = this.#now();
      this.setPointerCapture(event.pointerId);
      this.#choose(this.#at(event));
    });
    this.listen(this, 'pointermove', (/** @type {PointerEvent} */ event) => {
      if (start !== null && !this.effectiveDisabled) this.#choose(this.#at(event));
    });
    const end = () => {
      if (start === null) return;
      const before = start;
      start = null;
      if (this.#now() !== before) this.dispatchEvent(new Event('change', { bubbles: true }));
    };
    this.listen(this, 'pointerup', end);
    this.listen(this, 'pointercancel', end);
    this.listen(this, 'lostpointercapture', end);
  }
}
