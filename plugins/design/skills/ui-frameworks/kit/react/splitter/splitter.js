// @ts-check
/**
 * splitter.js: the splitter for React (docs/specs/targets.md). A plain module that calls createElement; no build step.
 *
 * The root is a <div> with data-ui="splitter" and no role, around the two panes the author writes, marked
 * data-part="start" and data-part="end", which are found in the DOM and never cloned or wrapped. After them it renders
 * the bar the Web Component creates, <div data-part="bar"> with the separator role, a Tab stop, aria-valuemin, -max and
 * -now, the name Resize from the manifest's messages, aria-orientation across the split,
 * and aria-controls naming the first pane, which gets an id from useId when it has none (J63). The share of the first
 * pane goes to the recipe as --_share on the root's style, as the class writes it, so the server markup is laid out
 * at any share before hydration. Vertical is the author attribute orientation="vertical", which the condition
 * selects: a div with no role cannot carry aria-orientation (X2).
 *
 * value is controlled (value with onInput and onChange) or uncontrolled (defaultValue, 50 by default).
 * onInput(value, event) is called while the bar moves and onChange(value, event) when the user has finished, as on
 * the Web Component. Keys go through onKeyDown on the bar; a drag captures the pointer on the bar, as the class does,
 * and follows React's pointer props there.
 *
 * Rules: docs/specs/patterns.md, J62 and J63.
 */
import { createElement, useCallback, useEffect, useId, useLayoutEffect, useRef, useState } from 'react';
import { flushSync } from 'react-dom';
import { props as spec } from '../../components/splitter/splitter.props.js';

/**
 * @typedef {Omit<import('react').HTMLAttributes<HTMLDivElement>, 'onChange' | 'onInput' | 'defaultValue'> & {
 *   value?: number, defaultValue?: number, min?: number, max?: number,
 *   orientation?: 'horizontal' | 'vertical',
 *   onInput?: (value: number, event: import('react').SyntheticEvent) => void,
 *   onChange?: (value: number, event: import('react').SyntheticEvent) => void,
 *   ref?: import('react').Ref<HTMLDivElement>,
 * }} SplitterProps
 */

/** The bar's name when the author gave none: messages.bar in splitter.manifest.json. */
const NAME = 'Resize';
/** A number prop's default from the manifest. @param {string} name */
const fallback = (name) => /** @type {{ default?: number }} */ (spec[name]).default ?? 0;
/** A prop that should be a number, or the default when it is none. @param {unknown} v @param {number} d */
const numberOr = (v, d) => (typeof v === 'number' && Number.isFinite(v) ? v : d);
/** An enum prop's value, or its default when the value is not one of the manifest's. @param {string} name @param {unknown} value */
const pick = (name, value) => {
  const p = /** @type {{ values: readonly string[], default: string }} */ (spec[name]);
  return typeof value === 'string' && p.values.includes(value) ? value : p.default;
};
/** @param {number} n @param {number} lo @param {number} hi */
const clamp = (n, lo, hi) => Math.min(Math.max(n, lo), hi);

/** @param {SplitterProps} props */
export function Splitter({ value, defaultValue, min, max, orientation, onInput, onChange, style, children, ref, ...rest }) {
  /** @type {import('react').RefObject<HTMLDivElement | null>} */
  const root = useRef(null);
  /** @type {import('react').RefObject<HTMLDivElement | null>} */
  const bar = useRef(null);
  const setRef = useCallback((/** @type {HTMLDivElement | null} */ node) => {
    root.current = node;
    if (typeof ref === 'function') ref(node);
    else if (ref) ref.current = node;
  }, [ref]);
  const startId = useId();

  // The limits and the share as they are used: 0 ≤ min ≤ value ≤ max ≤ 100.
  const lo = clamp(numberOr(min, fallback('min')), 0, 100);
  const hi = clamp(numberOr(max, fallback('max')), lo, 100);
  const [own, setOwn] = useState(() => numberOr(defaultValue, fallback('value')));
  const controlled = value !== undefined;
  const now = clamp(numberOr(controlled ? value : own, fallback('value')), lo, hi);
  const vertical = pick('orientation', orientation) === 'vertical';
  /** The id of the first pane, which the bar names in aria-controls; null while there is no first pane. */
  const [controls, setControls] = useState(/** @type {string | null} */ (null));

  const latest = useRef({ now, lo, hi, vertical, controlled, onInput, onChange });
  latest.current = { now, lo, hi, vertical, controlled, onInput, onChange };
  /** The share the first pane had when Enter last collapsed it. @type {import('react').RefObject<number | null>} */
  const restore = useRef(null);
  /** The drag in progress: the pointer, where it held the bar, and the share it started from. @type {import('react').RefObject<{ id: number, grip: number, from: number } | null>} */
  const drag = useRef(null);

  // aria-controls on the first pane, which the author may add or replace later; a pane with no id gets one.
  useLayoutEffect(() => {
    const el = /** @type {HTMLDivElement} */ (root.current);
    const name = () => {
      const start = el.querySelector(':scope > [data-part="start"]');
      if (start && !start.id) start.id = startId;
      return start ? start.id : null;
    };
    setControls(name());
    const observer = new MutationObserver(() => { const id = name(); flushSync(() => setControls(id)); });
    observer.observe(el, { childList: true, subtree: true, attributes: true, attributeFilter: ['id', 'data-part'] });
    return () => observer.disconnect();
  }, [startId]);

  useEffect(() => {
    const id = requestAnimationFrame(() => root.current?.setAttribute('data-ready', ''));
    return () => cancelAnimationFrame(id);
  }, []);

  /** Moves the bar to a share, rounded to hundredths and held inside the limits, and calls onInput when it moved. @param {number} share @param {import('react').SyntheticEvent} event */
  const move = (share, event) => {
    const { now: was, lo: a, hi: b, controlled: held } = latest.current;
    const next = clamp(Math.round(share * 100) / 100, a, b);
    if (next === was) return false;
    latest.current.now = next;
    if (!held) flushSync(() => setOwn(next));
    latest.current.onInput?.(next, event);
    return true;
  };

  /** The room the two panes share, along the split: the root's content box less the bar. */
  const room = () => {
    const el = /** @type {HTMLDivElement} */ (root.current);
    const rect = el.getBoundingClientRect();
    const s = getComputedStyle(el);
    const up = latest.current.vertical;
    const b = /** @type {HTMLDivElement} */ (bar.current).getBoundingClientRect();
    const px = (/** @type {string} */ name) => parseFloat(s.getPropertyValue(name)) || 0;
    const rtl = s.direction === 'rtl';
    const padStart = up ? px('padding-top') + px('border-top-width') : px(rtl ? 'padding-right' : 'padding-left') + px(rtl ? 'border-right-width' : 'border-left-width');
    const content = up
      ? rect.height - px('padding-top') - px('padding-bottom') - px('border-top-width') - px('border-bottom-width')
      : rect.width - px('padding-left') - px('padding-right') - px('border-left-width') - px('border-right-width');
    return { rect, start: padStart, length: content - (up ? b.height : b.width) };
  };

  /** How far a pointer is along the split from the start edge of a box: from the top, the left, or the right right to left. @param {import('react').PointerEvent} event @param {DOMRect} rect @param {number} [offset] */
  const along = (event, rect, offset = 0) => {
    if (latest.current.vertical) return event.clientY - rect.top - offset;
    return getComputedStyle(/** @type {HTMLDivElement} */ (root.current)).direction === 'rtl' ? rect.right - event.clientX - offset : event.clientX - rect.left - offset;
  };

  /** @param {import('react').KeyboardEvent<HTMLDivElement>} event */
  const keyDown = (event) => {
    if (event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) return;
    const { lo: a, hi: b, now: v, vertical: up } = latest.current;
    const rtl = getComputedStyle(/** @type {HTMLDivElement} */ (root.current)).direction === 'rtl';
    const keys = /** @type {Record<string, number>} */ (up ? { ArrowUp: -1, ArrowDown: 1 } : { ArrowLeft: rtl ? 1 : -1, ArrowRight: rtl ? -1 : 1 });
    let next;
    if (event.key in keys) next = v + keys[event.key];
    else if (event.key === 'Home') next = a;
    else if (event.key === 'End') next = b;
    else if (event.key === 'Enter') {
      if (v > a) { restore.current = v; next = a; }
      else if (restore.current !== null) next = restore.current;
      else return;
    } else return;
    event.preventDefault();
    if (move(next, event)) latest.current.onChange?.(latest.current.now, event);
  };

  /** @param {import('react').PointerEvent<HTMLDivElement>} event */
  const pointerDown = (event) => {
    const b = /** @type {HTMLDivElement} */ (bar.current);
    if (event.button !== 0) return;
    // WebKit selects the text a captured drag passes over unless the press is cancelled; Chromium and Firefox do not.
    event.preventDefault();
    b.focus({ preventScroll: true });
    drag.current = { id: event.pointerId, grip: along(event, b.getBoundingClientRect()), from: latest.current.now };
    b.setPointerCapture(event.pointerId);
  };
  /** @param {import('react').PointerEvent<HTMLDivElement>} event */
  const pointerMove = (event) => {
    const d = drag.current;
    if (!d || event.pointerId !== d.id) return;
    const r = room();
    if (r.length <= 0) return;
    move(((along(event, r.rect, r.start) - d.grip) / r.length) * 100, event);
  };
  // The capture ends when the pointer is released or cancelled, and when the bar leaves the document.
  /** @param {import('react').PointerEvent<HTMLDivElement>} event */
  const end = (event) => {
    const d = drag.current;
    if (!d || event.pointerId !== d.id) return;
    drag.current = null;
    if (latest.current.now !== d.from) latest.current.onChange?.(latest.current.now, event);
  };

  const handle = createElement('div', {
    key: 'bar', ref: bar, 'data-part': 'bar', role: 'separator', tabIndex: 0,
    'aria-label': NAME,
    'aria-valuemin': String(lo), 'aria-valuemax': String(hi), 'aria-valuenow': String(now),
    'aria-orientation': vertical ? 'horizontal' : 'vertical',
    'aria-controls': controls ?? undefined,
    onKeyDown: keyDown,
    onPointerDown: pointerDown,
    onPointerMove: pointerMove,
    onLostPointerCapture: end,
  });
  return createElement('div', /** @type {any} */ ({
    ...rest, ref: setRef, 'data-ui': 'splitter',
    orientation: vertical ? 'vertical' : undefined,
    style: { ...style, '--_share': String(now) },
  }), children, handle);
}
