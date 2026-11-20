// @ts-check
/**
 * submenu.js: the element that holds a menu item and the menu it opens, for React (docs/specs/targets.md).
 *
 * The root is a <div> with no role, a row of the menu around it and the box its menu is placed against (J25):
 * a block among the menu's rows, which a <span> could not hold. It is the menu button one level down, with a
 * menu item as its trigger: it holds whether its menu is open and gives it to the menu through the menu
 * button's context, and a radio item of its menu belongs to no group around it. The trigger is the child with
 * the menuitem role and the menu the element with the menu role whose nearest submenu is this one; it writes
 * the pattern's ARIA on the trigger and names the menu after it, in the DOM, after each render and whenever its
 * subtree changes (G10's way, one level down).
 *
 * A click on the trigger, and so Enter and Space, and the arrow pointing at the inline end, through React's
 * onKeyDown, open the menu, which moves focus to its first item and returns it to the trigger. The arrow
 * pointing at the inline start, pressed in the menu, returns focus to the trigger, and the menu closes as focus
 * leaves it; Escape does the same through the menu's dismiss. An arrow it acts on has its default prevented,
 * which tells a menubar around that the key is taken. A menu around it that closes closes this one too (J24).
 */
import { createElement, useCallback, useEffect, useLayoutEffect, useMemo, useRef, useState } from 'react';
import { flushSync } from 'react-dom';
import { MenuButtonContext } from '../menu-button/menu-button.js';
import { MenuGroupContext } from '../menu-group/menu-group.js';

/**
 * @typedef {import('react').HTMLAttributes<HTMLDivElement> & {
 *   ref?: import('react').Ref<HTMLDivElement>,
 * }} SubmenuProps
 */

const MENU = '[role="menu"]';
const ROOT = '[data-ui="submenu"]';
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

/** @param {SubmenuProps} props */
export function Submenu({ onKeyDown, children, ref, ...rest }) {
  const [open, setOpen] = useState(false);
  /** @type {import('react').RefObject<HTMLDivElement | null>} */
  const root = useRef(null);
  const setRef = useCallback((/** @type {HTMLDivElement | null} */ node) => {
    root.current = node;
    if (typeof ref === 'function') ref(node);
    else if (ref) ref.current = node;
  }, [ref]);
  const isOpen = useRef(open);
  isOpen.current = open;
  /** @type {import('react').RefObject<WeakMap<Element, string>>} The menu names this element wrote, so that it never replaces an author's. */
  const named = useRef(new WeakMap());

  /** The trigger and the menu, or null while either is missing. */
  const pair = useCallback(() => {
    const el = root.current;
    if (!el) return null;
    const trigger = /** @type {HTMLElement | undefined} */ ([...el.children].find((c) => c.getAttribute('role') === 'menuitem'));
    const menu = /** @type {HTMLElement | undefined} */ ([...el.querySelectorAll(MENU)].find((m) => m.closest(ROOT) === el));
    return trigger && menu ? { menu, trigger } : null;
  }, []);

  const sync = useCallback(() => {
    const p = pair();
    if (!p) return;
    const { menu, trigger } = p;
    if (!trigger.id) trigger.id = `ui-submenu-${++serial}`;
    put(trigger, 'aria-haspopup', 'menu');
    put(trigger, 'aria-controls', menu.id);
    put(trigger, 'aria-expanded', String(isOpen.current));
    // A menu the author named keeps its name (A2). One this element named follows its trigger.
    const name = menu.getAttribute('aria-labelledby');
    if (menu.hasAttribute('aria-label') || (name !== null && name !== named.current.get(menu))) return;
    put(menu, 'aria-labelledby', trigger.id);
    named.current.set(menu, trigger.id);
  }, [pair]);

  /**
   * Opens the menu, which moves focus to its first item. A menu that is open already closes first, with focus
   * on the trigger, and opens again, so that focus goes back into it.
   */
  const show = useCallback((/** @type {{ menu: HTMLElement, trigger: HTMLElement }} */ p) => {
    if (isOpen.current) {
      flushSync(() => setOpen(false));
      p.trigger.focus();
    }
    flushSync(() => setOpen(true));
  }, []);
  /** The pair, when the event happened on a trigger that is not disabled. @param {Event} event */
  const fromTrigger = useCallback((/** @type {Event} */ event) => {
    const p = pair();
    return p && event.target instanceof Node && p.trigger.contains(event.target) && !disabled(p.trigger) ? p : null;
  }, [pair]);

  useLayoutEffect(sync);
  useLayoutEffect(() => {
    const el = /** @type {HTMLDivElement} */ (root.current);
    const off = new AbortController();
    const listen = { signal: off.signal };
    // A click, and so Enter and Space on the item, opens the menu (J24).
    el.addEventListener('click', (event) => { const p = fromTrigger(event); if (p) show(p); }, listen);
    // While the menu is open, the pointer passing over the trigger leaves focus in the menu: the menu around
    // would otherwise move focus to the trigger, and this menu would close as focus left it.
    el.addEventListener('pointermove', (event) => { if (isOpen.current && fromTrigger(event)) event.stopPropagation(); }, listen);
    // A menu around this one that closes, by a script or otherwise, closes this one too. toggle does not
    // bubble, so it is caught on its way down.
    el.ownerDocument.addEventListener('toggle', (event) => {
      const p = pair();
      const closed = /** @type {ToggleEvent} */ (event).newState === 'closed';
      if (closed && p && isOpen.current && event.target instanceof Node && event.target !== p.menu && event.target.contains(el)) flushSync(() => setOpen(false));
    }, { ...listen, capture: true });
    const observer = new MutationObserver(sync);
    observer.observe(el, { childList: true, subtree: true, attributes: true, attributeFilter: ['role', 'id'] });
    return () => { off.abort(); observer.disconnect(); };
  }, [fromTrigger, pair, show, sync]);
  useEffect(() => {
    const at = requestAnimationFrame(() => root.current?.setAttribute('data-ready', ''));
    return () => cancelAnimationFrame(at);
  }, []);

  /** @param {import('react').KeyboardEvent<HTMLDivElement>} event */
  const keyDown = (event) => {
    onKeyDown?.(event);
    if (event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) return;
    const el = /** @type {HTMLDivElement} */ (root.current);
    const rtl = getComputedStyle(el).direction === 'rtl';
    const end = rtl ? 'ArrowLeft' : 'ArrowRight';
    if (event.key === end) {
      const p = fromTrigger(event.nativeEvent);
      if (!p) return;
      event.preventDefault();
      show(p);
      return;
    }
    if (event.key !== (rtl ? 'ArrowRight' : 'ArrowLeft')) return;
    const p = pair();
    // Only a key pressed on an item of this menu, not of a menu nested deeper, which has its own submenu.
    if (!p || !isOpen.current || !(event.target instanceof Element) || event.target.closest(MENU) !== p.menu) return;
    event.preventDefault();
    // Focus leaving the menu closes it, through its dismiss (G14), as on the Web Component's close.
    p.trigger.focus();
  };

  const state = useMemo(() => ({ open, setOpen, trigger: () => pair()?.trigger ?? null }), [open, pair]);
  return createElement('div', /** @type {any} */ ({ ...rest, ref: setRef, 'data-ui': 'submenu', onKeyDown: keyDown }),
    createElement(MenuButtonContext.Provider, { value: state },
      createElement(MenuGroupContext.Provider, { value: null }, children)));
}
