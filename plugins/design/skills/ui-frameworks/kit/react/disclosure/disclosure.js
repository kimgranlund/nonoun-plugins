// @ts-check
/**
 * disclosure.js: the element that holds a trigger and the panel it shows and hides, for React
 * (docs/specs/targets.md; rules J9 and J10 of docs/specs/patterns.md).
 *
 * The root is a <div>. It has no role and paints nothing; its recipe alone shows the panel, from the root's
 * `open` attribute, so the state is right in the server markup (J10). The panel is the author's child marked
 * `data-part="panel"`; the trigger is the author's own element of another family, such as the kit's Button, so it
 * is found as the Web Component finds it: the first element with the button role, or a native button, that
 * belongs to this disclosure and is not inside the panel, a heading included (J9). Its aria-expanded and
 * aria-controls, and an id on the panel that has none, are written into the DOM only where they differ, after
 * each render and whenever the subtree changes.
 *
 * `open` is controlled (open with onToggle) or uncontrolled (defaultOpen). onToggle(open, event) is called once
 * when the user shows or hides the panel, with the state already in the page when it is uncontrolled, and a
 * `toggle` event that bubbles is dispatched after it, as on the Web Component. When another party writes `open` on
 * the root, such as an accordion that keeps one disclosure open, an uncontrolled disclosure follows it, and a
 * controlled one calls onToggle(open) with no event, so that its owner can follow too.
 */
import { createElement, useCallback, useEffect, useId, useLayoutEffect, useRef, useState } from 'react';
import { flushSync } from 'react-dom';

/**
 * @typedef {Omit<import('react').HTMLAttributes<HTMLDivElement>, 'defaultValue'> & {
 *   open?: boolean, defaultOpen?: boolean,
 *   onToggle?: (open: boolean, event?: Event) => void,
 *   ref?: import('react').Ref<HTMLDivElement>,
 * }} DisclosureProps
 */

const ROOT = '[data-ui="disclosure"]';
const BUTTON = 'button, [role="button"]';

/** @param {Element} el */
const disabled = (el) => el.hasAttribute('disabled') || el.getAttribute('aria-disabled') === 'true';
/** Sets or removes an attribute, only when it differs. @param {Element} el @param {string} name @param {string | null} value */
const put = (el, name, value) => {
  if (el.getAttribute(name) === value) return;
  if (value === null) el.removeAttribute(name);
  else el.setAttribute(name, value);
};

/** @param {DisclosureProps} props */
export function Disclosure({ open, defaultOpen = false, onToggle, children, ref, ...rest }) {
  const base = useId();
  const [own, setOwn] = useState(defaultOpen);
  const controlled = open !== undefined;
  const isOpen = controlled ? !!open : own;
  /** @type {import('react').RefObject<HTMLDivElement | null>} */
  const root = useRef(null);
  const setRef = useCallback((/** @type {HTMLDivElement | null} */ node) => {
    root.current = node;
    if (typeof ref === 'function') ref(node);
    else if (ref) ref.current = node;
  }, [ref]);
  const latest = useRef({ isOpen, controlled, onToggle });
  latest.current = { isOpen, controlled, onToggle };

  /** The panel and its trigger, or null while either is missing. */
  const pair = useCallback(() => {
    const el = root.current;
    if (!el) return null;
    const panel = /** @type {HTMLElement | undefined} */ ([...el.children].find((child) => child.matches('[data-part="panel"]')));
    if (!panel) return null;
    const trigger = /** @type {HTMLElement | undefined} */ ([...el.querySelectorAll(BUTTON)].find((x) => x.closest(ROOT) === el && !panel.contains(x)));
    return trigger ? { panel, trigger } : null;
  }, []);
  /** Brings the trigger's ARIA and the panel's id in step, as the root's `open` stands in the page. */
  const sync = useCallback(() => {
    const p = pair();
    if (!p) return;
    if (!p.panel.id) p.panel.id = `${base}panel`;
    put(p.trigger, 'aria-controls', p.panel.id);
    put(p.trigger, 'aria-expanded', String(/** @type {HTMLElement} */ (root.current).hasAttribute('open')));
  }, [pair, base]);

  useLayoutEffect(sync);
  useLayoutEffect(() => {
    const el = /** @type {HTMLDivElement} */ (root.current);
    const off = new AbortController();
    // A click, and so Enter and Space on the kit's button, shows the panel or hides it (J10). It is seen in the
    // same task by a listener further up, which is why the state is flushed here.
    el.addEventListener('click', (event) => {
      const p = pair();
      if (!p || !(event.target instanceof Node) || !p.trigger.contains(event.target) || disabled(p.trigger)) return;
      const next = !latest.current.isOpen;
      if (latest.current.controlled) flushSync(() => latest.current.onToggle?.(next, event));
      else {
        flushSync(() => setOwn(next));
        latest.current.onToggle?.(next, event);
      }
      // A controlled disclosure whose owner did not follow has not toggled.
      if (el.hasAttribute('open') === next) el.dispatchEvent(new Event('toggle', { bubbles: true }));
    }, { signal: off.signal });
    const observer = new MutationObserver((records) => {
      sync();
      // `open` written by someone else: an accordion, or a script.
      if (!records.some((r) => r.type === 'attributes' && r.attributeName === 'open' && r.target === el)) return;
      const now = el.hasAttribute('open');
      if (now === latest.current.isOpen) return;
      if (latest.current.controlled) latest.current.onToggle?.(now);
      else flushSync(() => setOwn(now));
    });
    observer.observe(el, { childList: true, subtree: true, attributes: true, attributeFilter: ['role', 'data-part', 'open'] });
    return () => { off.abort(); observer.disconnect(); };
  }, [pair, sync]);
  useEffect(() => {
    const at = requestAnimationFrame(() => root.current?.setAttribute('data-ready', ''));
    return () => cancelAnimationFrame(at);
  }, []);

  return createElement('div', /** @type {any} */ ({ ...rest, ref: setRef, 'data-ui': 'disclosure', open: isOpen }), children);
}
