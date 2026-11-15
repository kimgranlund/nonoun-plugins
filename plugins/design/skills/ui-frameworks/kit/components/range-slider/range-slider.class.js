// @ts-check
/**
 * range-slider.class.js: the range slider's class. Importing it defines no element; range-slider.js does that.
 *
 * The root is a form-associated custom element with the group role. Its two thumbs are the parts `low` and `high`,
 * which it creates at its end unless the author wrote them; each has the slider role, its own aria-valuemin,
 * aria-valuemax and aria-valuenow, and a name, Minimum or Maximum, unless the author named it. Each thumb's limits
 * are what the other leaves it: the low thumb's maximum is the high value, the high thumb's minimum the low value.
 * As the slider does, it hands each value's share of the range to the recipe as a private custom property on the
 * root's inline style, --_low and --_high; those are the one style it writes.
 *
 * Rules: J57 and J58 in docs/specs/patterns.md (with J53 to J55 for each thumb), F1 to F7 in docs/specs/foundation.md.
 *
 * Both values are held between min and max and on a step counted from min, and the high value is never below the
 * low one; the props keep what was written. The form submits the name twice, the low value first. input and change
 * are dispatched from the root as the slider dispatches them; a change by a script dispatches neither.
 */
import { setAttr } from '../../foundation/element.js';
import { UIFormElement } from '../../foundation/form.js';
import { props, parts, role, tabindex, resets } from './range-slider.props.js';

/** The thumbs' names, from the manifest's `messages`. */
const MESSAGES = { low: 'Minimum', high: 'Maximum' };
/** @typedef {'low' | 'high'} Thumb */
/** @type {Thumb[]} */
const THUMBS = ['low', 'high'];

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

/** How many steps a key moves a value; Home and End are handled apart. @param {string} key @param {boolean} rtl */
const stepsOf = (key, rtl) => ({ ArrowRight: rtl ? -1 : 1, ArrowLeft: rtl ? 1 : -1, ArrowUp: 1, ArrowDown: -1, PageUp: 10, PageDown: -10 })[key];

export class UIRangeSlider extends UIFormElement {
  static props = props;
  static parts = parts;
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

  /** The two values as they are used, and the limits each thumb has. */
  #now() {
    const self = /** @type {any} */ (this);
    const range = this.#range();
    const low = hold(self.low, range);
    const high = Math.max(hold(self.high, range), low);
    return { ...range, low, high, limits: { low: [range.min, high], high: [low, range.max] } };
  }

  formValue() {
    const self = /** @type {any} */ (this);
    if (!self.name) return null;
    const { low, high } = this.#now();
    const data = new FormData();
    data.append(self.name, String(low));
    data.append(self.name, String(high));
    return data;
  }

  /** @param {string | File | FormData | null} state */
  restore(state) {
    if (!(state instanceof FormData)) return;
    const [low, high] = [...state.values()].map(Number);
    const self = /** @type {any} */ (this);
    if (Number.isFinite(low)) self.low = low;
    if (Number.isFinite(high)) self.high = high;
  }

  /** Sets one value as the user chose it, held inside that thumb's limits, and dispatches input if it changed. @param {Thumb} thumb @param {number} next */
  #choose(thumb, next) {
    const now = this.#now();
    const [from, to] = now.limits[thumb];
    const held = Math.min(Math.max(hold(next, now), from), to);
    if (held === now[thumb]) return false;
    /** @type {any} */ (this)[thumb] = held;
    this.dispatchEvent(new Event('input', { bubbles: true }));
    return true;
  }

  /** The value under the pointer: a thumb's centre runs from half a thumb after the start to half a thumb before the end. @param {PointerEvent} event */
  #at(event) {
    const r = this.getBoundingClientRect();
    const thumb = this.ensurePart('low')?.getBoundingClientRect().width ?? 0;
    const rtl = getComputedStyle(this).direction === 'rtl';
    const along = rtl ? r.right - event.clientX : event.clientX - r.left;
    const length = r.width - thumb;
    const share = length > 0 ? Math.min(Math.max((along - thumb / 2) / length, 0), 1) : 0;
    const { min, max } = this.#range();
    return min + share * (max - min);
  }

  /** The thumb nearer to a value; on a tie, the one that can move towards it. @param {number} v */
  #nearer(v) {
    const { low, high, max } = this.#now();
    const held = hold(v, this.#range());
    const toLow = Math.abs(held - low), toHigh = Math.abs(held - high);
    if (toLow !== toHigh) return toLow < toHigh ? 'low' : 'high';
    return held < low || (held === low && high === max) ? 'low' : 'high';
  }

  /** Which thumb an event came from, if any. @param {Event} event @returns {Thumb | null} */
  #thumbOf(event) {
    const target = /** @type {Element} */ (event.target);
    const name = target.parentElement === this ? target.getAttribute('data-part') : null;
    return name === 'low' || name === 'high' ? name : null;
  }

  connected() {
    for (const name of THUMBS) {
      const thumb = /** @type {HTMLElement} */ (this.ensurePart(name));
      if (!thumb.hasAttribute('role')) thumb.setAttribute('role', 'slider');
      if (!thumb.hasAttribute('aria-label') && !thumb.hasAttribute('aria-labelledby')) thumb.setAttribute('aria-label', MESSAGES[name]);
      this.effect(() => {
        const now = this.#now();
        const part = this.ensurePart(name);
        if (!part) return;
        setAttr(part, 'aria-valuemin', String(now.limits[name][0]));
        setAttr(part, 'aria-valuemax', String(now.limits[name][1]));
        setAttr(part, 'aria-valuenow', String(now[name]));
      });
      // A disabled range slider takes no focus: its thumbs lose their tabindex until it is enabled again.
      this.effect(() => {
        const disabled = this.effectiveDisabled;
        const part = this.ensurePart(name);
        if (!part) return;
        setAttr(part, 'tabindex', disabled ? null : '0');
        setAttr(part, 'aria-disabled', disabled ? 'true' : null);
      });
    }
    this.effect(() => {
      const { min, max, low, high } = this.#now();
      const share = (/** @type {number} */ v) => String(max > min ? (v - min) / (max - min) : 0);
      this.style.setProperty('--_low', share(low));
      this.style.setProperty('--_high', share(high));
      return () => { this.style.removeProperty('--_low'); this.style.removeProperty('--_high'); };
    });

    this.listen(this, 'keydown', (/** @type {KeyboardEvent} */ event) => {
      const thumb = this.#thumbOf(event);
      if (!thumb || this.effectiveDisabled || event.altKey || event.ctrlKey || event.metaKey) return;
      const now = this.#now();
      // Right to left swaps the left and right arrows; the direction is read now. Home and End go to the ends of
      // the range, which #choose holds inside what the other thumb leaves.
      const steps = stepsOf(event.key, getComputedStyle(this).direction === 'rtl');
      const next = event.key === 'Home' ? now.min : event.key === 'End' ? now.max : steps === undefined ? null : now[thumb] + steps * now.step;
      if (next === null) return;
      event.preventDefault();
      if (this.#choose(thumb, next)) this.dispatchEvent(new Event('change', { bubbles: true }));
    });

    /** @type {{ thumb: Thumb, before: number } | null} The thumb that follows the pointer, while a gesture runs. */
    let drag = null;
    this.listen(this, 'pointerdown', (/** @type {PointerEvent} */ event) => {
      if (this.effectiveDisabled || event.button !== 0) return;
      // Focus goes to the thumb that moves, not where the pointer went down, so the platform's own focusing is stopped.
      event.preventDefault();
      const at = this.#at(event), thumb = this.#nearer(at);
      drag = { thumb, before: this.#now()[thumb] };
      this.setPointerCapture(event.pointerId);
      this.ensurePart(thumb)?.focus();
      this.#choose(thumb, at);
    });
    this.listen(this, 'pointermove', (/** @type {PointerEvent} */ event) => {
      if (drag && !this.effectiveDisabled) this.#choose(drag.thumb, this.#at(event));
    });
    const end = () => {
      if (!drag) return;
      const { thumb, before } = drag;
      drag = null;
      if (this.#now()[thumb] !== before) this.dispatchEvent(new Event('change', { bubbles: true }));
    };
    this.listen(this, 'pointerup', end);
    this.listen(this, 'pointercancel', end);
    this.listen(this, 'lostpointercapture', end);
  }
}
