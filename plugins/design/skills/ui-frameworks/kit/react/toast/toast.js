// @ts-check
/**
 * toast.js: an alert with a time limit, for React (docs/specs/targets.md).
 *
 * The root is a <div> with the status role, or alert when the variant is critical, unless the author passed a
 * role (J92). Its open state is the author attribute `open`, which the recipe gives a box from (X2); the variant
 * is data-variant. `open` is controlled (with onClose) or uncontrolled (defaultOpen).
 *
 * The time is the component's own, written for React with the Web Component's rules (J93): a toast that is open
 * closes itself `duration` milliseconds after it opened, or after it mounted open; with 0 it stays. The time
 * does not run while the pointer is over the toast or focus is inside it, and starts again from the full
 * duration once both have left. A press on a descendant marked data-part="close", and Escape while focus is
 * inside (through the dismiss behaviour), close it. Closing it this way closes an uncontrolled toast, or asks
 * the owner of a controlled one, and calls onClose(event) once, with the state already in the page when it is
 * uncontrolled and the click or the key that closed it (none when the time ran out); onClose is not called when
 * the `open` prop closes it. As on the Web Component, the root dispatches `close`, an event that bubbles, once after each
 * change from open to closed, whoever made it. The toast never removes itself.
 *
 * The entry (J95): when it opens, or mounts open, the root's own inline style gets the private custom property
 * --_entering, 1, for two frames; the recipe reads it, only when motion is allowed, as the starting opacity of
 * a transition. That is the one style it writes.
 */
import { createElement, useCallback, useEffect, useLayoutEffect, useRef, useState } from 'react';
import { flushSync } from 'react-dom';
import { dismiss } from '../../behaviours/dismiss.js';
import { props as spec } from '../../components/toast/toast.props.js';

/**
 * @typedef {Omit<import('react').HTMLAttributes<HTMLDivElement>, 'onClose'> & {
 *   open?: boolean, defaultOpen?: boolean,
 *   variant?: 'neutral' | 'info' | 'success' | 'warning' | 'critical',
 *   duration?: number,
 *   onClose?: (event?: Event) => void,
 *   ref?: import('react').Ref<HTMLDivElement>,
 * }} ToastProps
 */

const CLOSE = '[data-part="close"]';
const ROOT = '[data-ui="toast"]';

/** An enum prop's value, or its default when the value is not one of the manifest's. @param {string} name @param {unknown} value */
const pick = (name, value) => {
  const p = /** @type {{ values: readonly string[], default: string }} */ (spec[name]);
  return typeof value === 'string' && p.values.includes(value) ? value : p.default;
};
/** The duration in milliseconds, or the manifest's default when it is not a number. @param {unknown} value */
const time = (value) => {
  const n = Number(value ?? NaN);
  return Number.isFinite(n) ? n : /** @type {number} */ (/** @type {{ default: number }} */ (spec.duration).default);
};

/** @param {ToastProps} props */
export function Toast({ open, defaultOpen = false, variant, duration, onClose, role, children, ref, ...rest }) {
  const [own, setOwn] = useState(defaultOpen);
  const controlled = open !== undefined;
  const isOpen = controlled ? open : own;
  const kind = pick('variant', variant);
  /** @type {import('react').RefObject<HTMLDivElement | null>} */
  const root = useRef(null);
  const setRef = useCallback((/** @type {HTMLDivElement | null} */ node) => {
    root.current = node;
    if (typeof ref === 'function') ref(node);
    else if (ref) ref.current = node;
  }, [ref]);
  const latest = useRef({ isOpen, controlled, onClose, duration: time(duration) });
  latest.current = { isOpen, controlled, onClose, duration: time(duration) };
  /** @type {import('react').RefObject<{ hovered: boolean, focused: boolean, wasOpen: boolean, timer?: ReturnType<typeof setTimeout>, frame?: number }>} */
  const run = useRef({ hovered: false, focused: false, wasOpen: false });

  /** Closes the toast, or asks its owner to when it is controlled, and tells onClose once. @param {Event} [event] */
  const close = useCallback((/** @type {Event | undefined} */ event = undefined) => {
    const { isOpen: was, controlled: c, onClose: tell } = latest.current;
    if (!was) return;
    if (!c) flushSync(() => setOwn(false));
    tell?.(event);
  }, []);

  /** Starts the time from the full duration, unless it is closed, paused or has no duration. */
  const start = useCallback(() => {
    const r = run.current;
    clearTimeout(r.timer);
    r.timer = undefined;
    const { isOpen: now, duration: ms } = latest.current;
    if (!now || ms <= 0 || r.hovered || r.focused) return;
    r.timer = setTimeout(() => close(), ms);
  }, [close]);

  /** Removes --_entering, and the style attribute when nothing else is left in it. */
  const entered = useCallback(() => {
    const el = root.current;
    if (!el) return;
    el.style.removeProperty('--_entering');
    if (el.getAttribute('style') === '') el.removeAttribute('style');
  }, []);
  /** Hands --_entering to the recipe for two frames: the first paints the start, the second starts the transition. */
  const enter = useCallback(() => {
    const el = /** @type {HTMLDivElement} */ (root.current);
    const r = run.current;
    if (r.frame !== undefined) cancelAnimationFrame(r.frame);
    el.style.setProperty('--_entering', '1');
    r.frame = requestAnimationFrame(() => {
      r.frame = requestAnimationFrame(() => { r.frame = undefined; entered(); });
    });
  }, [entered]);

  // Each change of the open state, the first render included: an opening enters and starts the time, a closing
  // stops it and dispatches close.
  useLayoutEffect(() => {
    const r = run.current;
    if (isOpen === r.wasOpen) return;
    r.wasOpen = isOpen;
    if (isOpen) { enter(); start(); return; }
    clearTimeout(r.timer);
    r.timer = undefined;
    root.current?.dispatchEvent(new Event('close', { bubbles: true }));
  }, [isOpen, enter, start]);

  useLayoutEffect(() => {
    const el = /** @type {HTMLDivElement} */ (root.current);
    const r = run.current;
    const off = new AbortController();
    const listen = { signal: off.signal };
    const pause = () => { clearTimeout(r.timer); r.timer = undefined; };
    el.addEventListener('pointerenter', () => { r.hovered = true; pause(); }, listen);
    el.addEventListener('pointerleave', () => { r.hovered = false; start(); }, listen);
    el.addEventListener('focusin', () => { r.focused = true; pause(); }, listen);
    // Focus that moves inside the toast leaves one element and enters another: focusin stops the time again.
    el.addEventListener('focusout', () => { r.focused = false; start(); }, listen);
    // A press on the close part of this toast, by the pointer or by a key that clicks it.
    el.addEventListener('click', (event) => {
      const part = event.target instanceof Element ? event.target.closest(CLOSE) : null;
      if (part && part.closest(ROOT) === el) close(event);
    }, listen);
    // Escape while focus is inside. A press outside and focus that leaves close nothing.
    const stops = [dismiss(el, {
      active: () => latest.current.isOpen,
      onDismiss: (reason, event) => { if (reason === 'escape') close(event); },
    })];
    return () => {
      off.abort();
      for (const end of stops) end();
      clearTimeout(r.timer);
      r.timer = undefined;
      if (r.frame !== undefined) { cancelAnimationFrame(r.frame); r.frame = undefined; entered(); }
      r.hovered = r.focused = false;
      r.wasOpen = false;
    };
  }, [close, entered, start]);
  useEffect(() => {
    const at = requestAnimationFrame(() => root.current?.setAttribute('data-ready', ''));
    return () => cancelAnimationFrame(at);
  }, []);

  return createElement('div', /** @type {any} */ ({
    ...rest, ref: setRef, role: role ?? (kind === 'critical' ? 'alert' : 'status'),
    'data-ui': 'toast', 'data-variant': kind, open: isOpen || undefined,
  }), children);
}
