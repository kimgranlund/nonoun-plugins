// @ts-check
/**
 * range-slider.js: the range slider for React (docs/specs/targets.md). A plain module that calls createElement; no
 * build step.
 *
 * The root is a <div> with the group role and data-ui="range-slider". After the author's children it renders the two
 * thumbs the Web Component creates, <span data-part="low"> and <span data-part="high">, each with the slider role, a
 * Tab stop, the name Minimum or Maximum from the manifest's messages, and the limits the other thumb leaves it; then
 * two hidden inputs marked data-part="input" that carry the name twice, the low value first, as the class submits it.
 * Each value's share of the range goes to the recipe as --_low and --_high on the root's style, as the class writes
 * them. Disabled is aria-disabled on the root, which its role allows, and on each thumb, which then has no Tab stop
 * (X2). A disabled fieldset around it disables it too: the component watches the fieldsets around it.
 *
 * low and high are each controlled (low, high) or uncontrolled (defaultLow, defaultHigh). onInput({ low, high }, event)
 * is called while the user changes a value and onChange({ low, high }, event) when they have finished, as on the
 * slider. Keys go through onKeyDown on the thumb that has focus; a press on the track is captured on the root and moves
 * the nearer thumb, which takes focus.
 *
 * Rules: J57 and J58 in docs/specs/patterns.md (with J53 to J55 for each thumb), F1 to F7 in docs/specs/foundation.md.
 */
import { createElement, useCallback, useEffect, useLayoutEffect, useRef, useState } from 'react';
import { flushSync } from 'react-dom';
import { props as spec, role } from '../../components/range-slider/range-slider.props.js';

/**
 * @typedef {{ low: number, high: number }} Pair
 * @typedef {Omit<import('react').HTMLAttributes<HTMLDivElement>, 'onChange' | 'onInput'> & {
 *   low?: number, high?: number, defaultLow?: number, defaultHigh?: number,
 *   min?: number, max?: number, step?: number, name?: string, disabled?: boolean,
 *   onInput?: (value: Pair, event: import('react').SyntheticEvent) => void,
 *   onChange?: (value: Pair, event: import('react').SyntheticEvent) => void,
 *   ref?: import('react').Ref<HTMLDivElement>,
 * }} RangeSliderProps
 */

/** The thumbs' names: messages.low and messages.high in range-slider.manifest.json. */
const MESSAGES = { low: 'Minimum', high: 'Maximum' };
/** @typedef {'low' | 'high'} Thumb */
/** @type {Thumb[]} */
const THUMBS = ['low', 'high'];

/** A number prop's default from the manifest. @param {string} name */
const fallback = (name) => /** @type {{ default?: number }} */ (spec[name]).default ?? 0;
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
/** How many steps a key moves a value; Home and End are handled apart. @param {string} key @param {boolean} rtl */
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

/** @param {RangeSliderProps} props */
function RangeSliderRoot({ low, high, defaultLow, defaultHigh, min, max, step, name, disabled = false, onInput, onChange, onPointerDown, onPointerMove, onLostPointerCapture, style, children, ref, ...rest }) {
  /** @type {import('react').RefObject<HTMLDivElement | null>} */
  const root = useRef(null);
  /** @type {import('react').RefObject<HTMLInputElement | null>} */
  const field = useRef(null);
  /** @type {import('react').RefObject<Record<Thumb, HTMLSpanElement | null>>} */
  const parts = useRef({ low: null, high: null });
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
  const first = useRef({ low: numberOr(defaultLow, 0), high: numberOr(defaultHigh, 0) });
  const [own, setOwn] = useState(first.current);
  const held = { low: low !== undefined, high: high !== undefined };
  // Both values are held in the range and on a step, and the high value is never below the low one.
  const a = hold(numberOr(held.low ? low : own.low, 0), range);
  const now = { low: a, high: Math.max(hold(numberOr(held.high ? high : own.high, 0), range), a) };
  /** @type {Record<Thumb, [number, number]>} */
  const limits = { low: [range.min, now.high], high: [now.low, range.max] };
  const [fieldsetOff, setFieldsetOff] = useState(false);
  const off = disabled || fieldsetOff;

  /** What the event handlers read. */
  const latest = useRef({ now, range, limits, off, held, onInput, onChange });
  latest.current = { now, range, limits, off, held, onInput, onChange };
  /** The thumb that follows the pointer, and its value when the gesture began. @type {import('react').RefObject<{ thumb: Thumb, before: number } | null>} */
  const drag = useRef(null);

  // A disabled fieldset around the range slider disables it (F4); its disabled attribute is watched.
  useLayoutEffect(() => {
    const el = /** @type {HTMLDivElement} */ (root.current);
    setFieldsetOff(fenced(el));
    const observer = new MutationObserver(() => { const f = fenced(el); flushSync(() => setFieldsetOff(f)); });
    for (let f = el.parentElement?.closest('fieldset'); f; f = f.parentElement?.closest('fieldset')) observer.observe(f, { attributes: true, attributeFilter: ['disabled'] });
    return () => observer.disconnect();
  }, []);

  // A form reset puts the hidden inputs back by themselves; uncontrolled values go back to their first ones (F6), and
  // a controlled one shows its prop whatever the held value is.
  useLayoutEffect(() => {
    const form = /** @type {HTMLInputElement} */ (field.current).form;
    if (!form) return;
    const stop = new AbortController();
    form.addEventListener('reset', () => setTimeout(() => flushSync(() => setOwn(first.current))), { signal: stop.signal });
    return () => stop.abort();
  }, []);

  useEffect(() => {
    const id = requestAnimationFrame(() => root.current?.setAttribute('data-ready', ''));
    return () => cancelAnimationFrame(id);
  }, []);

  /** Sets one value as the user chose it, held inside that thumb's limits, and calls onInput if it changed. @param {Thumb} thumb @param {number} next @param {import('react').SyntheticEvent} event */
  const choose = (thumb, next, event) => {
    const { now: was, range: r, limits: l } = latest.current;
    const [from, to] = l[thumb];
    const v = Math.min(Math.max(hold(next, r), from), to);
    if (v === was[thumb]) return false;
    const pair = { ...was, [thumb]: v };
    latest.current.now = pair;
    if (!latest.current.held[thumb]) flushSync(() => setOwn((o) => ({ ...o, [thumb]: v })));
    latest.current.onInput?.(pair, event);
    return true;
  };

  /** The value under the pointer: a thumb's centre runs from half a thumb after the start to half a thumb before the end. @param {import('react').PointerEvent} event */
  const at = (event) => {
    const el = /** @type {HTMLDivElement} */ (root.current);
    const r = el.getBoundingClientRect();
    const thumb = parts.current.low?.getBoundingClientRect().width ?? 0;
    const rtl = getComputedStyle(el).direction === 'rtl';
    const along = rtl ? r.right - event.clientX : event.clientX - r.left;
    const length = r.width - thumb;
    const share = length > 0 ? Math.min(Math.max((along - thumb / 2) / length, 0), 1) : 0;
    const { min: x, max: y } = latest.current.range;
    return x + share * (y - x);
  };

  /** The thumb nearer to a value; on a tie, the one that can move towards it. @param {number} v @returns {Thumb} */
  const nearer = (v) => {
    const { now: { low: l, high: hi }, range: r } = latest.current;
    const v2 = hold(v, r);
    const toLow = Math.abs(v2 - l), toHigh = Math.abs(v2 - hi);
    if (toLow !== toHigh) return toLow < toHigh ? 'low' : 'high';
    return v2 < l || (v2 === l && hi === r.max) ? 'low' : 'high';
  };

  /** @param {Thumb} thumb @param {import('react').KeyboardEvent<HTMLSpanElement>} event */
  const keyDown = (thumb, event) => {
    if (latest.current.off || event.altKey || event.ctrlKey || event.metaKey) return;
    const { now: n, range: r } = latest.current;
    // Right to left swaps the left and right arrows; the direction is read now. Home and End go to the ends of the
    // range, which choose() holds inside what the other thumb leaves.
    const steps = stepsOf(event.key, getComputedStyle(/** @type {HTMLDivElement} */ (root.current)).direction === 'rtl');
    const next = event.key === 'Home' ? r.min : event.key === 'End' ? r.max : steps === undefined ? null : n[thumb] + steps * r.step;
    if (next === null) return;
    event.preventDefault();
    if (choose(thumb, next, event)) latest.current.onChange?.(latest.current.now, event);
  };

  /** @param {import('react').PointerEvent<HTMLDivElement>} event */
  const pointerDown = (event) => {
    onPointerDown?.(event);
    if (latest.current.off || event.button !== 0) return;
    // Focus goes to the thumb that moves, not where the pointer went down, so the platform's own focusing is stopped.
    event.preventDefault();
    const v = at(event), thumb = nearer(v);
    drag.current = { thumb, before: latest.current.now[thumb] };
    /** @type {HTMLDivElement} */ (root.current).setPointerCapture(event.pointerId);
    parts.current[thumb]?.focus();
    choose(thumb, v, event);
  };
  /** @param {import('react').PointerEvent<HTMLDivElement>} event */
  const pointerMove = (event) => {
    onPointerMove?.(event);
    if (drag.current && !latest.current.off) choose(drag.current.thumb, at(event), event);
  };
  /** @param {import('react').PointerEvent<HTMLDivElement>} event */
  const end = (event) => {
    if (!drag.current) return;
    const { thumb, before } = drag.current;
    drag.current = null;
    if (latest.current.now[thumb] !== before) latest.current.onChange?.(latest.current.now, event);
  };

  const share = (/** @type {number} */ v) => String(range.max > range.min ? (v - range.min) / (range.max - range.min) : 0);
  const thumbs = THUMBS.map((thumb) => createElement('span', {
    key: thumb, 'data-part': thumb, role: 'slider',
    ref: (/** @type {HTMLSpanElement | null} */ node) => { parts.current[thumb] = node; },
    tabIndex: off ? undefined : 0,
    'aria-label': MESSAGES[thumb],
    'aria-valuemin': String(limits[thumb][0]), 'aria-valuemax': String(limits[thumb][1]), 'aria-valuenow': String(now[thumb]),
    'aria-disabled': off ? 'true' : undefined,
    onKeyDown: (/** @type {import('react').KeyboardEvent<HTMLSpanElement>} */ event) => keyDown(thumb, event),
  }));
  const fields = THUMBS.map((thumb) => createElement('input', {
    key: `${thumb}-input`, type: 'hidden', 'data-part': 'input', ref: thumb === 'low' ? field : undefined,
    name, value: String(now[thumb]), disabled: off,
  }));
  return createElement('div', /** @type {any} */ ({
    ...rest, ref: setRef, role, 'data-ui': 'range-slider',
    'aria-disabled': off ? 'true' : undefined,
    style: { ...style, '--_low': share(now.low), '--_high': share(now.high) },
    onPointerDown: pointerDown,
    onPointerMove: pointerMove,
    // The capture ends when the pointer is released or cancelled, and when the root leaves the document.
    onLostPointerCapture: (/** @type {import('react').PointerEvent<HTMLDivElement>} */ event) => { onLostPointerCapture?.(event); end(event); },
  }), children, ...thumbs, ...fields);
}

export const RangeSlider = /* @__PURE__ */ Object.assign(RangeSliderRoot, { kitRole: role, displayName: 'RangeSlider' });
