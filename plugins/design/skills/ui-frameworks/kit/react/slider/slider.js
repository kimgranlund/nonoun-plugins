// @ts-check
/**
 * slider.js: the slider for React (docs/specs/targets.md). A plain module that calls createElement; no build step.
 *
 * The root is a <div> with the slider role, the control itself (no native element is a slider whose track, fill
 * and thumb the recipe can draw as pseudo-elements). It takes focus, so :hover, :focus-visible and :active are its
 * own, and its states are ARIA attributes the role allows: aria-valuemin, aria-valuemax, aria-valuenow,
 * aria-orientation while vertical and aria-disabled while disabled (X2). The value's share of the range, a number
 * from 0 to 1, goes to the recipe as the private custom property --_share on the root's style, as the class writes
 * it, so the server markup is painted at the value before hydration.
 *
 * A div is no form control, so a hidden input marked data-part="input" carries name and value: the form submits it,
 * a disabled slider submits nothing, and a form reset puts an uncontrolled value back to its first one (F6). A
 * fieldset that is disabled disables the slider too: the component watches the fieldsets around it.
 *
 * value is controlled (value with onInput and onChange) or uncontrolled (defaultValue). As on the Web Component,
 * onInput(value, event) is called while the user changes the value and onChange(value, event) when they have
 * finished: after each key, and at the end of a pointer gesture if the value moved. A change by a prop calls
 * neither. Keys go through onKeyDown on the root; the pointer is captured on the root, as the class captures it.
 *
 * Rules: J53 to J56 in docs/specs/patterns.md, F1 to F7 in docs/specs/foundation.md.
 */
import { createElement, useCallback, useEffect, useLayoutEffect, useRef, useState } from 'react';
import { flushSync } from 'react-dom';
import { props as spec, role, tabindex } from '../../components/slider/slider.props.js';

/**
 * @typedef {Omit<import('react').HTMLAttributes<HTMLDivElement>, 'onChange' | 'onInput' | 'defaultValue'> & {
 *   value?: number, defaultValue?: number, min?: number, max?: number, step?: number,
 *   orientation?: 'horizontal' | 'vertical', name?: string, disabled?: boolean,
 *   onInput?: (value: number, event: import('react').SyntheticEvent) => void,
 *   onChange?: (value: number, event: import('react').SyntheticEvent) => void,
 *   ref?: import('react').Ref<HTMLDivElement>,
 * }} SliderProps
 */

/** A number prop's default from the manifest. @param {string} name */
const fallback = (name) => /** @type {{ default?: number }} */ (spec[name]).default ?? 0;
/** An enum prop's value, or its default when the value is not one of the manifest's. @param {string} name @param {unknown} value */
const pick = (name, value) => {
  const p = /** @type {{ values: readonly string[], default: string }} */ (spec[name]);
  return typeof value === 'string' && p.values.includes(value) ? value : p.default;
};
/** A prop that should be a number, or the default when it is none. @param {unknown} v @param {number} d */
const numberOr = (v, d) => (typeof v === 'number' && Number.isFinite(v) ? v : d);

/** The decimals of a number as written, so that a step of 0.1 gives 0.3 and not 0.30000000000000004. @param {number} n */
const decimals = (n) => {
  const text = String(n), exp = text.indexOf('e-');
  if (exp !== -1) return Number(text.slice(exp + 2));
  const dot = text.indexOf('.');
  return dot === -1 ? 0 : text.length - dot - 1;
};
/** @typedef {{ min: number, max: number, step: number }} Range */
/** A number held between min and max and on a step counted from min. @param {number} v @param {Range} r */
const hold = (v, { min, max, step }) => {
  const places = Math.min(Math.max(decimals(min), decimals(step)), 12);
  const last = min + Math.floor((max - min) / step + 1e-9) * step;
  const steps = Math.round((Math.max(v, min) - min) / step);
  return Number(Math.min(min + steps * step, last).toFixed(places));
};
/** How many steps a key moves the value; Home and End are handled apart. @param {string} key @param {boolean} rtl */
const stepsOf = (key, rtl) => /** @type {Record<string, number>} */ ({ ArrowRight: rtl ? -1 : 1, ArrowLeft: rtl ? 1 : -1, ArrowUp: 1, ArrowDown: -1, PageUp: 10, PageDown: -10 })[key];

/** Whether a disabled fieldset disables an element: it is inside one, and not inside that fieldset's first legend. @param {Element} el */
const fenced = (el) => {
  for (let f = el.parentElement?.closest('fieldset'); f; f = f.parentElement?.closest('fieldset')) {
    if (!f.disabled) continue;
    const legend = [...f.children].find((c) => c.localName === 'legend');
    if (!legend || !legend.contains(el)) return true;
  }
  return false;
};

/** @param {SliderProps} props */
function SliderRoot({ value, defaultValue, min, max, step, orientation, name, disabled = false, onInput, onChange, onKeyDown, onPointerDown, onPointerMove, onLostPointerCapture, style, ref, ...rest }) {
  /** @type {import('react').RefObject<HTMLDivElement | null>} */
  const root = useRef(null);
  /** @type {import('react').RefObject<HTMLInputElement | null>} */
  const field = useRef(null);
  const setRef = useCallback((/** @type {HTMLDivElement | null} */ node) => {
    root.current = node;
    if (typeof ref === 'function') ref(node);
    else if (ref) ref.current = node;
  }, [ref]);

  // The range as it is used: max is never below min, and the step is above 0.
  const lo = numberOr(min, fallback('min'));
  const rawStep = numberOr(step, fallback('step'));
  /** @type {Range} */
  const range = { min: lo, max: Math.max(numberOr(max, fallback('max')), lo), step: rawStep > 0 ? rawStep : 1 };
  const first = useRef(numberOr(defaultValue, 0));
  const [own, setOwn] = useState(first.current);
  const controlled = value !== undefined;
  const now = hold(numberOr(controlled ? value : own, 0), range);
  const vertical = pick('orientation', orientation) === 'vertical';
  const [fieldsetOff, setFieldsetOff] = useState(false);
  const off = disabled || fieldsetOff;

  /** What the event handlers read: the value as it is now, and the last one the user chose. */
  const latest = useRef({ now, range, off, vertical, controlled, onInput, onChange });
  latest.current = { now, range, off, vertical, controlled, onInput, onChange };
  /** The value when the pointer went down, while a gesture runs. @type {import('react').RefObject<number | null>} */
  const start = useRef(null);

  // A disabled fieldset around the slider disables it (F4); its disabled attribute is watched, since no event tells.
  useLayoutEffect(() => {
    const el = /** @type {HTMLDivElement} */ (root.current);
    setFieldsetOff(fenced(el));
    const observer = new MutationObserver(() => { const f = fenced(el); flushSync(() => setFieldsetOff(f)); });
    for (let f = el.parentElement?.closest('fieldset'); f; f = f.parentElement?.closest('fieldset')) observer.observe(f, { attributes: true, attributeFilter: ['disabled'] });
    return () => observer.disconnect();
  }, []);

  // A form reset puts the hidden input back by itself; an uncontrolled value goes back to its first one (F6). A
  // controlled one shows its prop whatever the held value is.
  useLayoutEffect(() => {
    const form = /** @type {HTMLInputElement} */ (field.current).form;
    if (!form) return;
    const off = new AbortController();
    form.addEventListener('reset', () => setTimeout(() => flushSync(() => setOwn(first.current))), { signal: off.signal });
    return () => off.abort();
  }, []);

  // data-ready one frame after the root is in the page, as on every Web Component (L6): transitions start then.
  useEffect(() => {
    const id = requestAnimationFrame(() => root.current?.setAttribute('data-ready', ''));
    return () => cancelAnimationFrame(id);
  }, []);

  /** Sets the value the user chose, held, and calls onInput if it changed. @param {number} next @param {import('react').SyntheticEvent} event */
  const choose = (next, event) => {
    const { now: was, range: r, controlled: held } = latest.current;
    const v = hold(next, r);
    if (v === was) return false;
    latest.current.now = v;
    if (!held) flushSync(() => setOwn(v));
    latest.current.onInput?.(v, event);
    return true;
  };

  /** The value under the pointer: the thumb's centre runs from half a thumb after the start to half a thumb before the end. @param {PointerEvent | import('react').PointerEvent} event */
  const at = (event) => {
    const el = /** @type {HTMLDivElement} */ (root.current);
    const r = el.getBoundingClientRect();
    const thumb = parseFloat(getComputedStyle(el, '::after').width) || 0;
    const { vertical: up, range: { min: a, max: b } } = latest.current;
    const rtl = !up && getComputedStyle(el).direction === 'rtl';
    const along = up ? r.bottom - event.clientY : rtl ? r.right - event.clientX : event.clientX - r.left;
    const length = (up ? r.height : r.width) - thumb;
    const share = length > 0 ? Math.min(Math.max((along - thumb / 2) / length, 0), 1) : 0;
    return a + share * (b - a);
  };

  /** @param {import('react').KeyboardEvent<HTMLDivElement>} event */
  const keyDown = (event) => {
    onKeyDown?.(event);
    if (event.defaultPrevented || latest.current.off || event.altKey || event.ctrlKey || event.metaKey) return;
    const el = /** @type {HTMLDivElement} */ (root.current);
    const { min: a, max: b, step: s } = latest.current.range;
    // Right to left swaps the left and right arrows of a horizontal slider; the direction is read now.
    const rtl = !latest.current.vertical && getComputedStyle(el).direction === 'rtl';
    const steps = stepsOf(event.key, rtl);
    const next = event.key === 'Home' ? a : event.key === 'End' ? b : steps === undefined ? null : latest.current.now + steps * s;
    if (next === null) return;
    event.preventDefault();
    if (choose(next, event)) latest.current.onChange?.(latest.current.now, event);
  };

  /** @param {import('react').PointerEvent<HTMLDivElement>} event */
  const pointerDown = (event) => {
    onPointerDown?.(event);
    if (latest.current.off || event.button !== 0) return;
    start.current = latest.current.now;
    /** @type {HTMLDivElement} */ (root.current).setPointerCapture(event.pointerId);
    choose(at(event), event);
  };
  /** @param {import('react').PointerEvent<HTMLDivElement>} event */
  const pointerMove = (event) => {
    onPointerMove?.(event);
    if (start.current !== null && !latest.current.off) choose(at(event), event);
  };
  /** @param {import('react').PointerEvent<HTMLDivElement>} event */
  const end = (event) => {
    if (start.current === null) return;
    const before = start.current;
    start.current = null;
    if (latest.current.now !== before) latest.current.onChange?.(latest.current.now, event);
  };

  const share = range.max > range.min ? (now - range.min) / (range.max - range.min) : 0;
  const hidden = createElement('input', { type: 'hidden', 'data-part': 'input', ref: field, name, value: String(now), disabled: off });
  return createElement('div', /** @type {any} */ ({
    ...rest, ref: setRef, role, 'data-ui': 'slider',
    tabIndex: off ? undefined : tabindex,
    'aria-valuemin': String(range.min), 'aria-valuemax': String(range.max), 'aria-valuenow': String(now),
    'aria-orientation': vertical ? 'vertical' : undefined,
    'aria-disabled': off ? 'true' : undefined,
    style: { ...style, '--_share': String(share) },
    onKeyDown: keyDown,
    onPointerDown: pointerDown,
    onPointerMove: pointerMove,
    // The capture ends when the pointer is released or cancelled, and when the root leaves the document.
    onLostPointerCapture: (/** @type {import('react').PointerEvent<HTMLDivElement>} */ event) => { onLostPointerCapture?.(event); end(event); },
  }), hidden);
}

export const Slider = /* @__PURE__ */ Object.assign(SliderRoot, { kitRole: role, displayName: 'Slider' });
