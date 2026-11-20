// @ts-check
/**
 * popover.js: a non-modal dialog beside the control that opens it, for React (docs/specs/targets.md).
 *
 * The root is a <span>, the inline box the content is placed against, as the Web Component's root is. It holds
 * two things the author wrote, found in the DOM and never cloned: the content, its child marked
 * data-part="content", and the control, its first other child element. After each render and on each change in
 * its subtree it writes on the content the dialog role, an id, popover="manual" and tabindex="-1" where the
 * author wrote none, and on the control aria-haspopup="dialog", aria-controls and aria-expanded; a former
 * control loses the three (J88).
 *
 * Its open state is the author attribute `open` on the root, which the recipe displays the content from; the
 * content is in the top layer exactly while it is open, in the same task as the render (X2). `open` is
 * controlled (with onToggle) or uncontrolled (defaultOpen). As on the Web Component, the root dispatches
 * `toggle`, a ToggleEvent that does not bubble, after each change of what is shown, whoever made it.
 * onToggle(open, event) is called once each time the popover opens or closes itself, with the state already in
 * the page, or asks to when it is controlled, with the event that caused it; it is not called when the `open`
 * prop changes.
 *
 * Each opening after the first render moves focus to the content's first focusable element, or to the content
 * (J89); a popover rendered open shows and takes no focus. A click on the control opens it, or closes it and
 * returns focus to the control: Enter and Space do so through the control's own click. Escape, through the
 * dismiss behaviour, closes it, returns focus to the control and goes no further; a press outside and focus
 * that leaves close it and leave focus where it went.
 */
import { createElement, useCallback, useEffect, useId, useLayoutEffect, useRef, useState } from 'react';
import { flushSync } from 'react-dom';
import { dismiss } from '../../behaviours/dismiss.js';

/**
 * @typedef {Omit<import('react').HTMLAttributes<HTMLSpanElement>, 'onToggle'> & {
 *   open?: boolean, defaultOpen?: boolean,
 *   onToggle?: (open: boolean, event?: Event) => void,
 *   ref?: import('react').Ref<HTMLSpanElement>,
 * }} PopoverProps
 */

/** What can take focus inside the content, in document order. */
const FOCUSABLE = 'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])';
/** The ARIA this element writes on its control. */
const ARIA = ['aria-haspopup', 'aria-expanded', 'aria-controls'];
/** Whether a child of the root is marked as the content. @param {Element} el */
const isContent = (el) => el.getAttribute('data-part') === 'content';
/** @param {Element} el */
const disabled = (el) => el.hasAttribute('disabled') || el.getAttribute('aria-disabled') === 'true';
/** Sets or removes an attribute, only when it differs. @param {Element} el @param {string} name @param {string | null} value */
const put = (el, name, value) => {
  if (el.getAttribute(name) === value) return;
  if (value === null) el.removeAttribute(name);
  else el.setAttribute(name, value);
};
/** @param {boolean} open */
const state = (open) => (open ? 'open' : 'closed');

/** @param {PopoverProps} props */
export function Popover({ open, defaultOpen = false, onToggle, children, ref, ...rest }) {
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
  /** @type {import('react').RefObject<HTMLElement | null>} The element that last got this element's ARIA. */
  const owned = useRef(null);
  /** Whether the last toggle dispatched said open. */
  const reported = useRef(false);
  /** Whether the first layout effect has run: before it, an opening moves no focus. */
  const live = useRef(false);

  const content = useCallback(() => /** @type {HTMLElement | null} */ (root.current?.querySelector(':scope > [data-part="content"]') ?? null), []);
  const control = useCallback(() => /** @type {HTMLElement | null} */ ([...(root.current?.children ?? [])].find((el) => !isContent(el)) ?? null), []);

  /** Opens or closes the popover, or asks its owner to when it is controlled. @param {boolean} next @param {Event} [event] */
  const set = useCallback((/** @type {boolean} */ next, /** @type {Event | undefined} */ event = undefined) => {
    const { isOpen: was, controlled: c, onToggle: tell } = latest.current;
    if (next === was) return;
    // In the same task: a listener further up sees the content shown or hidden.
    if (!c) flushSync(() => setOwn(next));
    tell?.(next, event);
  }, []);
  /** Closes the popover, and with `restore` returns focus to the control. @param {boolean} restore @param {Event} event */
  const close = useCallback((/** @type {boolean} */ restore, /** @type {Event} */ event) => {
    set(false, event);
    if (restore) control()?.focus();
  }, [control, set]);

  /**
   * Shows or hides the content so that it is showing exactly while the popover is open, moves focus in when it
   * opens after the first render, and dispatches `toggle` when the state differs from the last one dispatched.
   */
  const apply = useCallback(() => {
    const el = content();
    const want = latest.current.isOpen;
    if (!root.current?.isConnected || !el || !el.hasAttribute('popover')) return;
    if (want !== el.matches(':popover-open')) {
      if (want) {
        el.showPopover();
        // The root's open attribute is already rendered, so the content is displayed and can take focus.
        if (live.current) /** @type {HTMLElement} */ (el.querySelector(FOCUSABLE) ?? el).focus();
      } else el.hidePopover();
    }
    if (want === reported.current) return;
    reported.current = want;
    root.current.dispatchEvent(new ToggleEvent('toggle', { oldState: state(!want), newState: state(want) }));
  }, [content]);

  /** Writes the role, the id, the popover and the tabindex on the content, and the ARIA on the control. */
  const sync = useCallback(() => {
    const el = content(), now = control();
    if (el) {
      if (!el.hasAttribute('role')) el.setAttribute('role', 'dialog');
      if (!el.id) el.id = `popover-${id.replace(/[^\w-]/g, '')}`;
      if (!el.hasAttribute('popover')) el.setAttribute('popover', 'manual');
      if (!el.hasAttribute('tabindex')) el.setAttribute('tabindex', '-1');
    }
    const before = owned.current;
    if (before && (before !== now || !el)) {
      for (const name of ARIA) before.removeAttribute(name);
      owned.current = null;
    }
    if (now && el) {
      put(now, 'aria-haspopup', 'dialog');
      put(now, 'aria-controls', el.id);
      owned.current = now;
    }
    if (owned.current) put(owned.current, 'aria-expanded', String(latest.current.isOpen));
    apply();
  }, [apply, content, control, id]);

  useLayoutEffect(() => { sync(); live.current = true; });
  useLayoutEffect(() => {
    const el = /** @type {HTMLSpanElement} */ (root.current);
    const off = new AbortController();
    const listen = { signal: off.signal };
    // A click on the control, from the pointer or from a key that clicks it, opens or closes (J89).
    el.addEventListener('click', (event) => {
      const c = control();
      if (!c || !(event.target instanceof Node) || !c.contains(event.target) || disabled(c)) return;
      if (latest.current.isOpen) close(true, event);
      else set(true, event);
    }, listen);
    // Something else hid the popover: the state follows. The toggle event does not bubble, so it is caught on its way down.
    el.addEventListener('toggle', (event) => {
      const c = content();
      if (event.target === c && latest.current.isOpen && !c?.matches(':popover-open')) set(false, event);
    }, { ...listen, capture: true });
    const stops = [dismiss(el, {
      active: () => latest.current.isOpen,
      onDismiss: (reason, event) => close(reason === 'escape', event),
    })];
    const observer = new MutationObserver(sync);
    observer.observe(el, { childList: true, subtree: true, attributes: true, attributeFilter: ['data-part', 'id'] });
    return () => { off.abort(); for (const end of stops) end(); observer.disconnect(); live.current = false; };
  }, [close, content, control, set, sync]);
  useEffect(() => {
    const at = requestAnimationFrame(() => root.current?.setAttribute('data-ready', ''));
    return () => cancelAnimationFrame(at);
  }, []);

  return createElement('span', /** @type {any} */ ({ ...rest, ref: setRef, 'data-ui': 'popover', open: isOpen || undefined }), children);
}
