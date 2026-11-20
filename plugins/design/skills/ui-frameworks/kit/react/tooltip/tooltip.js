// @ts-check
/**
 * tooltip.js: a short description shown beside the element it describes, for React (docs/specs/targets.md).
 *
 * The root is a <span>, the inline box the content is placed against, as the Web Component's root is. It holds
 * two things the author wrote, found in the DOM and never cloned: the content, its child marked
 * data-part="content", and the subject, its first other child element. After each render and on each change in
 * its subtree it writes the tooltip role, an id and popover="manual" on the content where the author wrote none,
 * and aria-describedby on the subject unless the author wrote one; it remembers the values it wrote, so that it
 * updates its own and never the author's (J36).
 *
 * Its open state is the author attribute `open` on the root, which the recipe displays the content from; the
 * content is in the top layer exactly while it is open, in the same task as the render (J37, X2). `open` is
 * controlled (with onToggle) or uncontrolled (defaultOpen). onToggle(open, event) is called once each time the
 * tooltip opens or closes itself, with the state already in the page, or asks to when it is controlled, with
 * the event that caused it where there is one; it is not called when the `open` prop changes.
 *
 * When it opens and closes, as on the Web Component (J37):
 * - The pointer resting on the root for Tooltip.delay milliseconds opens it; leaving the root closes it after
 *   Tooltip.closeDelay milliseconds, which a return to the root or the content cancels. A touch pointer opens
 *   nothing.
 * - Focus on the subject that matches :focus-visible opens it at once; focus that leaves the subject closes it.
 * - Escape, through the dismiss behaviour, closes it and goes no further. A press on the subject closes it.
 */
import { createElement, useCallback, useEffect, useId, useLayoutEffect, useRef, useState } from 'react';
import { flushSync } from 'react-dom';
import { dismiss } from '../../behaviours/dismiss.js';

/**
 * @typedef {Omit<import('react').HTMLAttributes<HTMLSpanElement>, 'onToggle'> & {
 *   open?: boolean, defaultOpen?: boolean,
 *   onToggle?: (open: boolean, event?: Event) => void,
 *   ref?: import('react').Ref<HTMLSpanElement>,
 * }} TooltipProps
 */

/** Whether a child of the root is marked as the content. @param {Element} el */
const isContent = (el) => el.getAttribute('data-part') === 'content';
/** Sets or removes an attribute, only when it differs. @param {Element} el @param {string} name @param {string | null} value */
const put = (el, name, value) => {
  if (el.getAttribute(name) === value) return;
  if (value === null) el.removeAttribute(name);
  else el.setAttribute(name, value);
};

/** @param {TooltipProps} props */
function TooltipRoot({ open, defaultOpen = false, onToggle, children, ref, ...rest }) {
  const id = useId();
  const [own, setOwn] = useState(defaultOpen);
  const controlled = open !== undefined;
  const isOpen = controlled ? open : own;
  /** @type {import('react').RefObject<HTMLSpanElement | null>} */
  const root = useRef(null);
  const setRef = useCallback((/** @type {HTMLSpanElement | null} */ node) => {
    root.current = node;
    if (typeof ref === 'function') ref(node);
    else if (ref) ref.current = node;
  }, [ref]);
  const latest = useRef({ isOpen, controlled, onToggle });
  latest.current = { isOpen, controlled, onToggle };
  /** @type {import('react').RefObject<WeakMap<Element, string>>} The aria-describedby values this element wrote. */
  const described = useRef(new WeakMap());
  /** @type {import('react').RefObject<Element | null>} The subject that last got this element's aria-describedby. */
  const subject = useRef(null);
  /** @type {import('react').RefObject<{ opening?: ReturnType<typeof setTimeout>, closing?: ReturnType<typeof setTimeout> }>} */
  const timers = useRef({});

  const content = useCallback(() => /** @type {HTMLElement | null} */ (root.current?.querySelector(':scope > [data-part="content"]') ?? null), []);
  const describes = useCallback(() => /** @type {HTMLElement | null} */ ([...(root.current?.children ?? [])].find((el) => !isContent(el)) ?? null), []);

  /** Cancels a pending open and a pending close. */
  const stop = useCallback(() => {
    clearTimeout(timers.current.opening);
    clearTimeout(timers.current.closing);
    timers.current = {};
  }, []);

  /** Opens or closes the tooltip, or asks its owner to when it is controlled. @param {boolean} next @param {Event} [event] */
  const set = useCallback((/** @type {boolean} */ next, /** @type {Event | undefined} */ event = undefined) => {
    stop();
    const { isOpen: was, controlled: c, onToggle: tell } = latest.current;
    if (next === was) return;
    // In the same task: a listener further up sees the content shown or hidden.
    if (!c) flushSync(() => setOwn(next));
    tell?.(next, event);
  }, [stop]);

  /** Shows or hides the content so that it is showing exactly while the tooltip is open. */
  const apply = useCallback(() => {
    const el = content();
    const want = latest.current.isOpen;
    if (!root.current?.isConnected || !el || !el.hasAttribute('popover') || want === el.matches(':popover-open')) return;
    if (want) el.showPopover();
    else el.hidePopover();
  }, [content]);

  /** Writes the role, the id and the popover on the content, and aria-describedby on the subject. */
  const sync = useCallback(() => {
    const el = content(), now = describes();
    if (el) {
      if (!el.hasAttribute('role')) el.setAttribute('role', 'tooltip');
      if (!el.id) el.id = `tooltip-${id.replace(/[^\w-]/g, '')}`;
      if (!el.hasAttribute('popover')) el.setAttribute('popover', 'manual');
    }
    // A subject this element described, that is no longer the subject or has nothing to name, loses the value
    // this element wrote; a value the author wrote since stays.
    const before = subject.current;
    if (before && (before !== now || !el)) {
      if (before.getAttribute('aria-describedby') === described.current.get(before)) before.removeAttribute('aria-describedby');
      described.current.delete(before);
      subject.current = null;
    }
    if (now && el) {
      const value = now.getAttribute('aria-describedby');
      if (value === null || value === described.current.get(now)) {
        put(now, 'aria-describedby', el.id);
        described.current.set(now, el.id);
        subject.current = now;
      }
    }
    apply();
  }, [apply, content, describes, id]);

  useLayoutEffect(sync);
  useLayoutEffect(() => {
    const el = /** @type {HTMLSpanElement} */ (root.current);
    const off = new AbortController();
    const listen = { signal: off.signal };
    /** @param {EventTarget | null} node */
    const onSubject = (node) => node instanceof Node && !!describes()?.contains(node);
    // The pointer. Entering the root, the content included, cancels a pending close and starts the delay.
    el.addEventListener('pointerenter', (event) => {
      if (event.pointerType === 'touch') return;
      clearTimeout(timers.current.closing);
      timers.current.closing = undefined;
      if (latest.current.isOpen || timers.current.opening !== undefined) return;
      timers.current.opening = setTimeout(() => set(true), Tooltip.delay);
    }, listen);
    el.addEventListener('pointerleave', (event) => {
      if (event.pointerType === 'touch') return;
      clearTimeout(timers.current.opening);
      timers.current.opening = undefined;
      if (!latest.current.isOpen || timers.current.closing !== undefined) return;
      timers.current.closing = setTimeout(() => set(false), Tooltip.closeDelay);
    }, listen);
    // The keyboard: focus that the browser would show opens at once, and focus that leaves the subject closes.
    el.addEventListener('focusin', (event) => {
      if (onSubject(event.target) && /** @type {Element} */ (event.target).matches(':focus-visible')) set(true, event);
    }, listen);
    el.addEventListener('focusout', (event) => {
      if (onSubject(event.target) && !onSubject(event.relatedTarget)) set(false, event);
    }, listen);
    // A press on the subject, by the pointer or by a key that clicks it, is the user acting: it closes.
    el.addEventListener('pointerdown', (event) => { if (onSubject(event.target)) set(false, event); }, listen);
    el.addEventListener('click', (event) => { if (onSubject(event.target)) set(false, event); }, listen);
    // Something else hid the popover: the state follows. The toggle event does not bubble, so it is caught on its way down.
    el.addEventListener('toggle', (event) => {
      const c = content();
      if (event.target === c && latest.current.isOpen && !c?.matches(':popover-open')) set(false, event);
    }, { ...listen, capture: true });
    const stops = [dismiss(el, {
      active: () => latest.current.isOpen,
      onDismiss: (reason, event) => { if (reason === 'escape') set(false, event); },
    })];
    const observer = new MutationObserver(sync);
    observer.observe(el, { childList: true, subtree: true, attributes: true, attributeFilter: ['data-part', 'id'] });
    return () => {
      off.abort();
      for (const end of stops) end();
      observer.disconnect();
      stop();
    };
  }, [content, describes, set, stop, sync]);
  useEffect(() => {
    const at = requestAnimationFrame(() => root.current?.setAttribute('data-ready', ''));
    return () => cancelAnimationFrame(at);
  }, []);

  return createElement('span', /** @type {any} */ ({ ...rest, ref: setRef, 'data-ui': 'tooltip', open: isOpen || undefined }), children);
}
// Marked pure, so a bundle that does not use the component drops the module (X6). `delay` and `closeDelay` are
// the milliseconds before it opens and before it closes, read at each use, as the Web Component's static fields are.
export const Tooltip = /* @__PURE__ */ Object.assign(TooltipRoot, { displayName: 'Tooltip', delay: 500, closeDelay: 100 });
