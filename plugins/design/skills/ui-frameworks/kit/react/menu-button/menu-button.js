// @ts-check
/**
 * menu-button.js: the element that holds a trigger and its menu, for React (docs/specs/targets.md).
 *
 * The root is a <span>, the box the menu is placed against. It holds whether the menu is open and gives it
 * to its menu through React context, which this module exports. Its trigger is the author's own element of
 * another family, such as the kit's Button, so it finds it as the Web Component does: the first element with
 * the button role, or native button, that is not inside the menu (G10). It writes the pattern's ARIA on the
 * trigger and the menu's name into the DOM, only where it differs, after each render and whenever its
 * subtree changes; a click on the trigger, and so Enter and Space, opens or closes the menu, and ArrowDown and
 * ArrowUp open it (G11).
 */
import { createContext, createElement, useCallback, useEffect, useLayoutEffect, useMemo, useRef, useState } from 'react';
import { flushSync } from 'react-dom';

/**
 * @typedef {{ open: boolean, setOpen: (open: boolean) => void, trigger: () => HTMLElement | null }} MenuButtonState
 * @typedef {import('react').HTMLAttributes<HTMLSpanElement> & { ref?: import('react').Ref<HTMLSpanElement> }} MenuButtonProps
 */

/** What the menu of the nearest menu button reads. @type {import('react').Context<MenuButtonState | null>} */
export const MenuButtonContext = /* @__PURE__ */ createContext(/** @type {MenuButtonState | null} */ (null));

const MENU = '[role="menu"]';
const BUTTON = 'button, [role="button"]';
const ITEM = '[role="menuitem"], [role="menuitemcheckbox"], [role="menuitemradio"]';
const ROOT = '[data-ui="menu-button"]';
/** For the ids given to a trigger that has none. */
let serial = 0;

/** @param {Element} el */
const disabled = (el) => el.hasAttribute('disabled') || el.getAttribute('aria-disabled') === 'true';
/** Sets or removes an attribute, only when it differs. @param {Element} el @param {string} name @param {string | null} value */
const put = (el, name, value) => {
  if (el.getAttribute(name) === value) return;
  if (value === null) el.removeAttribute(name);
  else el.setAttribute(name, value);
};

/** @param {MenuButtonProps} props */
export function MenuButton({ children, ref, ...rest }) {
  const [open, setOpen] = useState(false);
  /** @type {import('react').RefObject<HTMLSpanElement | null>} */
  const root = useRef(null);
  const setRef = useCallback((/** @type {HTMLSpanElement | null} */ node) => {
    root.current = node;
    if (typeof ref === 'function') ref(node);
    else if (ref) ref.current = node;
  }, [ref]);
  const isOpen = useRef(open);
  isOpen.current = open;
  /** @type {import('react').RefObject<WeakMap<Element, string>>} The menu names this element wrote, so that it never replaces an author's. */
  const named = useRef(new WeakMap());

  /** The elements that match and belong to this menu button, not to one nested inside it. @param {string} selector */
  const own = useCallback((/** @type {string} */ selector) => {
    const el = root.current;
    return el ? /** @type {HTMLElement[]} */ ([...el.querySelectorAll(selector)].filter((x) => x.parentElement?.closest(ROOT) === el)) : [];
  }, []);
  const pair = useCallback(() => {
    const menu = own(MENU)[0];
    const trigger = menu && own(BUTTON).find((el) => !menu.contains(el));
    return trigger ? { menu, trigger } : null;
  }, [own]);

  const sync = useCallback(() => {
    const p = pair();
    if (!p) return;
    const { menu, trigger } = p;
    if (!trigger.id) trigger.id = `ui-menu-button-${++serial}`;
    put(trigger, 'aria-haspopup', 'menu');
    if (menu.id) put(trigger, 'aria-controls', menu.id);
    put(trigger, 'aria-expanded', String(isOpen.current));
    const name = menu.getAttribute('aria-labelledby');
    if (menu.hasAttribute('aria-label') || (name !== null && name !== named.current.get(menu))) return;
    put(menu, 'aria-labelledby', trigger.id);
    named.current.set(menu, trigger.id);
  }, [pair]);

  useLayoutEffect(sync);
  useLayoutEffect(() => {
    const el = /** @type {HTMLSpanElement} */ (root.current);
    const off = new AbortController();
    /** The pair when the event happened on a trigger that is not disabled. @param {Event} event */
    const fromTrigger = (event) => {
      const p = pair();
      return p && event.target instanceof Node && p.trigger.contains(event.target) && !disabled(p.trigger) ? p : null;
    };
    el.addEventListener('click', (event) => {
      if (!fromTrigger(event)) return;
      // Seen in the same task by a listener further up, even for a click that Enter dispatched (G11).
      flushSync(() => setOpen(!isOpen.current));
    }, { signal: off.signal });
    el.addEventListener('keydown', (event) => {
      if (event.key !== 'ArrowDown' && event.key !== 'ArrowUp') return;
      const p = fromTrigger(event);
      if (!p) return;
      event.preventDefault();
      flushSync(() => setOpen(true));
      if (event.key === 'ArrowUp') [.../** @type {NodeListOf<HTMLElement>} */ (p.menu.querySelectorAll(ITEM))].filter((item) => item.closest(MENU) === p.menu && !disabled(item)).pop()?.focus();
    }, { signal: off.signal });
    const observer = new MutationObserver(sync);
    observer.observe(el, { childList: true, subtree: true, attributes: true, attributeFilter: ['role', 'id'] });
    return () => { off.abort(); observer.disconnect(); };
  }, [pair, sync]);
  useEffect(() => {
    const at = requestAnimationFrame(() => root.current?.setAttribute('data-ready', ''));
    return () => cancelAnimationFrame(at);
  }, []);

  const state = useMemo(() => ({ open, setOpen, trigger: () => pair()?.trigger ?? null }), [open, pair]);
  return createElement('span', /** @type {any} */ ({ ...rest, ref: setRef, 'data-ui': 'menu-button' }),
    createElement(MenuButtonContext.Provider, { value: state }, children));
}
