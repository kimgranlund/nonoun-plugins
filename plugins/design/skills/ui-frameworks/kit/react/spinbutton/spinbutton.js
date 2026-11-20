// @ts-check
/**
 * spinbutton.js: the spinbutton for React (docs/specs/targets.md). A plain module that calls createElement; no build
 * step.
 *
 * The root is a <span> with data-ui="spinbutton" and no role: a field around the author's native text input, the
 * child marked data-part="input" (D14), which is found in the DOM and never cloned or wrapped. The input carries the
 * name and the value and takes part in the form by itself; this component gives it the spinbutton role, inputmode
 * and aria-valuemin, -max and -now (J59), steps it from the keys and from the two buttons it renders after the
 * author's children, <span data-part="decrease"> and <span data-part="increase"> (J60), and makes it invalid with
 * setCustomValidity when its text is not a number or lies outside the limits. Once the user is due to be told (J48)
 * it writes aria-invalid on the input and renders invalid on the root.
 *
 * States (X2): the root has no role, so disabled and invalid are the author attributes the conditions select;
 * focus-within and hover are the root's own pseudo-classes; read-only is the input's own readonly, which the recipe
 * reads through :has(). A disabled field disables the input, and enables only an input it disabled.
 *
 * The input's own input and change are its events: a step writes the value through the native setter, so React's
 * onChange on the author's input hears it as a user's change, and dispatches input then change, bubbling, from the
 * input. A controlled input must then take its value from its own onChange. Keys reach the root's onKeyDown from the
 * input; a click on a button reaches the button's onClick.
 *
 * Rules: docs/specs/patterns.md, J59 to J61 and J81, and J48 that J60 cites.
 */
import { createElement, useCallback, useEffect, useLayoutEffect, useRef, useState } from 'react';
import { flushSync } from 'react-dom';
import { props as spec } from '../../components/spinbutton/spinbutton.props.js';

/**
 * @typedef {Omit<import('react').HTMLAttributes<HTMLSpanElement>, 'onInvalid'> & {
 *   min?: number, max?: number, step?: number, disabled?: boolean,
 *   ref?: import('react').Ref<HTMLSpanElement>,
 * }} SpinbuttonProps
 */

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

/** The step's default from the manifest. */
const stepDefault = () => /** @type {{ default?: number }} */ (spec.step).default ?? 1;
/** A limit is set when it is a number; with none there is no limit. @param {unknown} v */
const limitOf = (v) => (typeof v === 'number' && Number.isFinite(v) ? v : null);
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
/** The input's value setter of the platform, which React's own tracking of the value does not see. */
const setValue = (/** @type {HTMLInputElement} */ input, /** @type {string} */ text) => {
  /** @type {PropertyDescriptor} */ (Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value')).set?.call(input, text);
};

/** @param {SpinbuttonProps} props */
export function Spinbutton({ min, max, step, disabled = false, onKeyDown, onInput, onBlur, onPointerDown, children, ref, ...rest }) {
  /** @type {import('react').RefObject<HTMLSpanElement | null>} */
  const root = useRef(null);
  const setRef = useCallback((/** @type {HTMLSpanElement | null} */ node) => {
    root.current = node;
    if (typeof ref === 'function') ref(node);
    else if (ref) ref.current = node;
  }, [ref]);

  /** The invalid mark is shown on the root (J48). */
  const [shown, setShown] = useState(false);
  /** What the component holds between renders: the user changed the input, the user is due to be told, the mark it wrote, the message it set, the input it disabled. */
  const state = useRef({ changed: false, told: false, marked: false, message: '', disabledInput: /** @type {HTMLInputElement | null} */ (null) });
  const lo = limitOf(min), hi = limitOf(max);
  const latest = useRef({ lo, hi, step, disabled });
  latest.current = { lo, hi, step, disabled };

  /** The author's input, a direct child marked data-part="input". */
  const input = () => {
    const el = root.current?.querySelector(':scope > [data-part="input"]');
    return el instanceof HTMLInputElement ? el : null;
  };

  /** Writes everything the input and the root carry. It runs after each render and after each event that may change them. */
  const sync = useCallback(() => {
    const el = input(), s = state.current, { lo: a, hi: b, disabled: off } = latest.current;
    if (!el) return;
    if (off) {
      if (!el.disabled) { el.disabled = true; s.disabledInput = el; }
    } else if (s.disabledInput) {
      s.disabledInput.disabled = false;
      s.disabledInput = null;
    }
    if (!el.hasAttribute('role')) el.setAttribute('role', 'spinbutton');
    if (!el.hasAttribute('inputmode')) el.setAttribute('inputmode', 'decimal');
    put(el, 'aria-valuemin', a === null ? null : String(a));
    put(el, 'aria-valuemax', b === null ? null : String(b));
    const n = read(el.value);
    put(el, 'aria-valuenow', n === null || Number.isNaN(n) ? null : String(n));
    const message = n === null ? '' : Number.isNaN(n) ? NOT_A_NUMBER : a !== null && n < a ? BELOW(a) : b !== null && n > b ? ABOVE(b) : '';
    if (message !== s.message) { el.setCustomValidity(message); s.message = message; }
    // Only a mark this component wrote is taken off: an author's aria-invalid and invalid stay as written.
    const show = s.told && !el.validity.valid;
    if (show || s.marked) {
      put(el, 'aria-invalid', show ? 'true' : null);
      s.marked = show;
      setShown(show);
    }
  }, []);

  // After every render: min, max, step and disabled take effect before paint, and an input the author rendered or
  // replaced is read again.
  useLayoutEffect(() => { sync(); });

  useLayoutEffect(() => {
    const el = /** @type {HTMLSpanElement} */ (root.current);
    const stop = new AbortController();
    // invalid does not bubble: the submit attempt reaches the root in the capture phase.
    el.addEventListener('invalid', (event) => { if (event.target === input()) { state.current.told = true; flushSync(sync); } }, { capture: true, signal: stop.signal });
    // A reset restores the input after the event, so the state is read again in the next task.
    document.addEventListener('reset', (event) => {
      const field = input();
      if (!field || event.target !== field.form) return;
      state.current.changed = state.current.told = false;
      setTimeout(() => { if (root.current?.isConnected) flushSync(sync); });
    }, { signal: stop.signal });
    return () => stop.abort();
  }, [sync]);

  useEffect(() => {
    const id = requestAnimationFrame(() => root.current?.setAttribute('data-ready', ''));
    return () => cancelAnimationFrame(id);
  }, []);

  /** Writes a value, held inside the limits, and dispatches input and change from the input when it changed. @param {number} value */
  const set = (value) => {
    const el = input();
    if (!el || el.disabled || el.readOnly) return;
    const { lo: a, hi: b } = latest.current;
    let next = value;
    if (b !== null) next = Math.min(next, b);
    if (a !== null) next = Math.max(next, a);
    const text = String(next);
    if (el.value === text) return;
    setValue(el, text);
    el.dispatchEvent(new Event('input', { bubbles: true }));
    el.dispatchEvent(new Event('change', { bubbles: true }));
    // React puts a controlled input back after the event when its onChange kept the value: read it again then.
    queueMicrotask(() => { if (root.current?.isConnected) flushSync(sync); });
  };

  /** Steps the value by count steps, held inside the limits. A step from an empty field starts at the minimum, or at 0. @param {number} count */
  const stepBy = (count) => {
    const el = input();
    if (!el) return;
    const given = latest.current.step ?? stepDefault();
    const size = typeof given === 'number' && given > 0 ? given : 1;
    const n = read(el.value);
    if (n === null || Number.isNaN(n)) { set(latest.current.lo ?? 0); return; }
    const places = Math.max(decimals(size), decimals(n));
    set(Number((n + count * size).toFixed(places)));
  };

  /** @param {import('react').KeyboardEvent<HTMLSpanElement>} event */
  const keyDown = (event) => {
    onKeyDown?.(event);
    const el = input();
    if (!el || event.target !== el || event.defaultPrevented || event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) return;
    if (event.key in STEPS) {
      event.preventDefault();
      stepBy(STEPS[event.key]);
    } else if (event.key === 'Home' || event.key === 'End') {
      const limit = event.key === 'Home' ? latest.current.lo : latest.current.hi;
      if (limit === null) return;
      event.preventDefault();
      set(limit);
    }
  };

  /** A press anywhere on the field but the input keeps focus in the input (J60) and puts it there (J47). @param {import('react').PointerEvent<HTMLSpanElement>} event */
  const pointerDown = (event) => {
    onPointerDown?.(event);
    const el = input();
    if (!el || event.target === el || !(event.target instanceof Node) || !root.current?.contains(event.target)) return;
    event.preventDefault();
    if (!el.disabled && document.activeElement !== el) el.focus({ preventScroll: true });
  };

  const button = (/** @type {'decrease' | 'increase'} */ name) => createElement('span', {
    key: name, 'data-part': name, role: 'button', tabIndex: -1, 'aria-label': NAMES[name],
    'aria-disabled': disabled ? 'true' : undefined,
    onClick: () => stepBy(name === 'increase' ? 1 : -1),
  });

  return createElement('span', /** @type {any} */ ({
    ...rest, ref: setRef, 'data-ui': 'spinbutton',
    disabled: disabled || undefined,
    // An invalid the author wrote stays as written (J48).
    invalid: shown ? '' : /** @type {any} */ (rest).invalid,
    onKeyDown: keyDown,
    onPointerDown: pointerDown,
    onInput: (/** @type {any} */ event) => {
      onInput?.(event);
      if (event.target === input()) { state.current.changed = true; sync(); }
    },
    onBlur: (/** @type {import('react').FocusEvent<HTMLSpanElement>} */ event) => {
      onBlur?.(event);
      if (event.target !== input()) return;
      if (state.current.changed) state.current.told = true;
      sync();
    },
  }), children, button('decrease'), button('increase'));
}
