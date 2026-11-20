// @ts-check
/**
 * dialog.js: a window over the page that holds focus until it is closed, for React (docs/specs/targets.md).
 *
 * The root is a <div> that takes no room (the recipe gives it display: contents), as the Web Component's root
 * is. The modal layer is the browser's own dialog element, which the author writes inside the root and marks
 * data-part="panel" (D91): it is found in the DOM, never cloned or wrapped. While the dialog is open the part is
 * shown with showModal(), in the same task as the render, and closed when it is not (J39). When the browser
 * closes the part (Escape, a form with method="dialog") the dialog closes, or asks its owner to.
 *
 * After each render and on each change in its subtree it names the part after the element marked
 * data-part="title" and describes it by the one marked data-part="description", giving each an id when it has
 * none, and with `alert` gives the part the alertdialog role; it never replaces what the author wrote (J41).
 * It adds no focus handling, no inertness and no Escape handling of its own (J40).
 *
 * Its open state is the author attribute `open` on the root (X2); the part's own `open` and :modal are the
 * platform's. `open` is controlled (with onClose) or uncontrolled (defaultOpen). onClose(event) gets the part's
 * close event when the browser closed it; it is not called when the `open` prop closes it. onOpen(event) gets the
 * part's toggle event when the browser opened it (a native button's command="show-modal", a script's showModal()):
 * an uncontrolled dialog is then open, and a controlled one is closed again at the next render unless its owner
 * sets `open`. The part's own close
 * event and returnValue stay the author's interface, as on the Web Component. `side` is the variant
 * data-side, which makes a drawer (J122).
 */
import { createElement, useCallback, useEffect, useId, useLayoutEffect, useRef, useState } from 'react';
import { flushSync } from 'react-dom';
import { props as spec } from '../../components/dialog/dialog.props.js';

/**
 * @typedef {Omit<import('react').HTMLAttributes<HTMLDivElement>, 'onClose'> & {
 *   open?: boolean, defaultOpen?: boolean, alert?: boolean,
 *   side?: 'center' | 'inline-start' | 'inline-end' | 'block-end',
 *   onClose?: (event: Event) => void, onOpen?: (event: Event) => void,
 *   ref?: import('react').Ref<HTMLDivElement>,
 * }} DialogProps
 */

/** An enum prop's value, or its default when the value is not one of the manifest's. @param {string} name @param {unknown} value */
const pick = (name, value) => {
  const p = /** @type {{ values: readonly string[], default: string }} */ (spec[name]);
  return typeof value === 'string' && p.values.includes(value) ? value : p.default;
};

/** @param {DialogProps} props */
export function Dialog({ open, defaultOpen = false, alert = false, side, onClose, onOpen, children, ref, ...rest }) {
  const id = useId();
  const [own, setOwn] = useState(defaultOpen);
  const controlled = open !== undefined;
  const isOpen = controlled ? open : own;
  /** @type {import('react').RefObject<HTMLDivElement | null>} */
  const root = useRef(null);
  const setRef = useCallback((/** @type {HTMLDivElement | null} */ node) => {
    root.current = node;
    if (typeof ref === 'function') ref(node);
    else if (ref) ref.current = node;
  }, [ref]);
  const latest = useRef({ isOpen, controlled, onClose, onOpen, alert });
  latest.current = { isOpen, controlled, onClose, onOpen, alert };
  /** @type {import('react').RefObject<{ part: HTMLDialogElement | null, off: () => void }>} The part whose close event is heard. */
  const bound = useRef({ part: null, off: () => {} });
  /** @type {import('react').RefObject<Map<string, string>>} What this element wrote on the part, by attribute. */
  const wrote = useRef(new Map());
  /** The browser is opening the part and has not yet said so with `toggle`: the part is not closed meanwhile. */
  const opening = useRef(false);
  /** This element is the one showing the part. */
  const mine = useRef(false);

  /** The dialog part, or null while it is missing or not a dialog element. */
  const part = useCallback(() => {
    const el = root.current?.querySelector(':scope > [data-part="panel"]');
    return el instanceof HTMLDialogElement && el.isConnected ? el : null;
  }, []);

  /** Sets or removes an attribute this element wrote, only when it differs. @param {HTMLElement} el @param {string} name @param {string | null} value */
  const write = useCallback((/** @type {HTMLElement} */ el, /** @type {string} */ name, /** @type {string | null} */ value) => {
    const mine = wrote.current.get(name);
    if (el.hasAttribute(name) && el.getAttribute(name) !== mine) return; // the author's
    if (value === null) { el.removeAttribute(name); wrote.current.delete(name); return; }
    if (el.getAttribute(name) !== value) el.setAttribute(name, value);
    wrote.current.set(name, value);
  }, []);

  /** Listens for the close event of the part, and again when the part is replaced. */
  const bind = useCallback(() => {
    const el = part();
    if (el === bound.current.part) return;
    bound.current.off();
    wrote.current.clear();
    if (!el) { bound.current = { part: null, off: () => {} }; return; }
    /** @param {Event} event */
    const onPartClose = (event) => {
      const { isOpen: was, controlled: c, onClose: tell } = latest.current;
      if (el.open || !was) return;
      // In the same task: the author's own listener on the part finds the dialog closed.
      if (!c) flushSync(() => setOwn(false));
      tell?.(event);
    };
    // The browser opened the part itself: an invoker command, or a script. The state follows, as it follows a close.
    /** @param {Event} event */
    const onPartToggle = (event) => {
      opening.current = false;
      const { isOpen: was, controlled: c, onOpen: tell } = latest.current;
      if (/** @type {ToggleEvent} */ (event).newState !== 'open' || was) return;
      if (!c) flushSync(() => setOwn(true));
      tell?.(event);
    };
    el.addEventListener('close', onPartClose);
    /** @param {Event} event */
    const onPartBefore = (event) => { opening.current = /** @type {ToggleEvent} */ (event).newState === 'open' && !mine.current; };
    el.addEventListener('beforetoggle', onPartBefore);
    el.addEventListener('toggle', onPartToggle);
    bound.current = { part: el, off: () => { el.removeEventListener('close', onPartClose); el.removeEventListener('beforetoggle', onPartBefore); el.removeEventListener('toggle', onPartToggle); } };
  }, [part]);

  /** Names and describes the part, and gives it the alertdialog role. */
  const name = useCallback(() => {
    const el = part();
    if (!el) return;
    const idOf = (/** @type {Element | null} */ x, /** @type {string} */ what) => {
      if (!x) return null;
      if (!x.id) x.id = `dialog-${what}-${id.replace(/[^\w-]/g, '')}`;
      return x.id;
    };
    write(el, 'aria-labelledby', idOf(el.querySelector('[data-part="title"]'), 'title'));
    write(el, 'aria-describedby', idOf(el.querySelector('[data-part="description"]'), 'description'));
    write(el, 'role', latest.current.alert ? 'alertdialog' : null);
  }, [id, part, write]);

  /** Brings the part in step with the open state. */
  const apply = useCallback(() => {
    const el = part();
    if (!el || !root.current?.isConnected) return;
    if (latest.current.isOpen && !el.matches(':modal')) {
      // A part that is open but not modal is shown again as a modal.
      if (el.open) el.close();
      mine.current = true;
      el.showModal();
      mine.current = false;
    } else if (!latest.current.isOpen && el.open && !opening.current) el.close();
  }, [part]);

  const refresh = useCallback(() => { bind(); name(); apply(); }, [apply, bind, name]);

  useLayoutEffect(refresh);
  useLayoutEffect(() => {
    const el = /** @type {HTMLDivElement} */ (root.current);
    const observer = new MutationObserver(refresh);
    observer.observe(el, { childList: true, subtree: true });
    return () => { observer.disconnect(); bound.current.off(); bound.current = { part: null, off: () => {} }; };
  }, [refresh]);
  useEffect(() => {
    const at = requestAnimationFrame(() => root.current?.setAttribute('data-ready', ''));
    return () => cancelAnimationFrame(at);
  }, []);

  return createElement('div', /** @type {any} */ ({ ...rest, ref: setRef, 'data-ui': 'dialog', 'data-side': pick('side', side), open: isOpen || undefined }), children);
}
