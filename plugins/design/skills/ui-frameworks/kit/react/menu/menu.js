// @ts-check
/**
 * menu.js: a list of actions that opens over the page, for React (docs/specs/targets.md).
 *
 * The root is a <div role="menu" popover="manual">. It is showing exactly while it is open, and its open state
 * is the platform's own, :popover-open: it writes no open attribute (X2). Inside a menu button, the menu
 * button holds whether it is open; on its own it is controlled (open, with the platform's onToggle) or
 * uncontrolled (defaultOpen). When it opens it remembers the element that had focus and moves focus to its
 * first item that is not disabled. It mounts roving focus, typeahead and dismiss as the Web Component does;
 * the pointer moves focus to the item under it; Escape and the activation of an item close it and return
 * focus, a press outside and focus that leaves close it and leave focus alone (G12 to G15).
 */
import { createElement, useCallback, useContext, useEffect, useId, useLayoutEffect, useRef, useState } from 'react';
import { flushSync } from 'react-dom';
import { rovingFocus } from '../../behaviours/roving-focus.js';
import { typeahead } from '../../behaviours/typeahead.js';
import { dismiss } from '../../behaviours/dismiss.js';
import { MenuButtonContext } from '../menu-button/menu-button.js';
import { role } from '../../components/menu/menu.props.js';

/**
 * @typedef {import('react').HTMLAttributes<HTMLDivElement> & {
 *   open?: boolean, defaultOpen?: boolean,
 *   ref?: import('react').Ref<HTMLDivElement>,
 * }} MenuProps
 */

const MENU = '[role="menu"]';
const ITEM = '[role="menuitem"], [role="menuitemcheckbox"], [role="menuitemradio"]';
const CHECKABLE = '[role="menuitemcheckbox"], [role="menuitemradio"]';
/** @param {Element} el */
const disabled = (el) => el.hasAttribute('disabled') || el.getAttribute('aria-disabled') === 'true';
/** @param {Event} event */
const itemOf = (event) => /** @type {HTMLElement | null} */ (event.target instanceof Element ? event.target.closest(ITEM) : null);
/** Whether activating the item leaves its menu open, as on the Web Component. @param {Element} item */
const staysOpen = (item) => ['true', 'menu'].includes(item.getAttribute('aria-haspopup') ?? '')
  || (item.matches(CHECKABLE) && !item.hasAttribute('data-active'));

/** @param {MenuProps} props */
function MenuRoot({ open, defaultOpen = false, children, ref, ...rest }) {
  const owner = useContext(MenuButtonContext);
  const id = useId();
  const [own, setOwn] = useState(defaultOpen);
  const isOpen = owner ? owner.open : open !== undefined ? open : own;
  /** @type {import('react').RefObject<HTMLDivElement | null>} */
  const root = useRef(null);
  const setRef = useCallback((/** @type {HTMLDivElement | null} */ node) => {
    root.current = node;
    if (typeof ref === 'function') ref(node);
    else if (ref) ref.current = node;
  }, [ref]);
  /** @type {import('react').RefObject<HTMLElement | null>} The element that had focus when the menu last opened. */
  const opener = useRef(null);
  const latest = useRef({ isOpen, owner, controlled: open !== undefined });
  latest.current = { isOpen, owner, controlled: open !== undefined };

  /** Closes the menu, and with `restore` returns focus to where it was when it opened. @param {boolean} restore */
  const close = useCallback((/** @type {boolean} */ restore) => {
    const el = /** @type {HTMLDivElement} */ (root.current);
    const back = opener.current;
    const { owner: o, controlled } = latest.current;
    flushSync(() => { if (o) o.setOpen(false); else if (!controlled) setOwn(false); });
    // A controlled menu hides itself too; the platform's toggle event tells its owner.
    if (el.matches(':popover-open')) el.hidePopover();
    if (restore) back?.focus();
  }, []);

  // The behaviours first: the items have their tabindex before the menu moves focus to one of them.
  useLayoutEffect(() => {
    const el = /** @type {HTMLDivElement} */ (root.current);
    const items = () => /** @type {HTMLElement[]} */ ([...el.querySelectorAll(ITEM)].filter((x) => x.closest(MENU) === el));
    const off = new AbortController();
    const listen = { signal: off.signal };
    let stays = false;
    // Something else hid the popover: the state follows (G15).
    el.addEventListener('toggle', () => {
      if (!latest.current.isOpen || el.matches(':popover-open')) return;
      const { owner: o, controlled } = latest.current;
      flushSync(() => { if (o) o.setOpen(false); else if (!controlled) setOwn(false); });
    }, listen);
    el.addEventListener('click', (event) => { const item = itemOf(event); stays = !!item && staysOpen(item); }, { ...listen, capture: true });
    el.addEventListener('click', (event) => {
      const item = itemOf(event);
      if (stays) return;
      if (item && !disabled(item)) close(true);
    }, listen);
    el.addEventListener('mousedown', (event) => event.preventDefault(), listen);
    el.addEventListener('pointermove', (event) => itemOf(event)?.focus({ preventScroll: true }), listen);
    const stops = [
      rovingFocus(el, { items, orientation: () => 'vertical', skip: disabled }),
      typeahead(el, { items, skip: disabled, onMatch: (item) => { if (el.ownerDocument.activeElement?.closest(MENU) === el) item.focus(); } }),
      dismiss(el, {
        ignore: () => [opener.current, latest.current.owner?.trigger()],
        onDismiss: (reason) => close(reason === 'escape'),
      }),
    ];
    return () => { off.abort(); for (const stop of stops) stop(); };
  }, [close]);

  // Shows or hides the popover in the same task as the render that opened or closed it.
  useLayoutEffect(() => {
    const el = /** @type {HTMLDivElement} */ (root.current);
    if (isOpen === el.matches(':popover-open')) return;
    if (!isOpen) { el.hidePopover(); return; }
    opener.current = /** @type {HTMLElement | null} */ (el.ownerDocument.activeElement);
    el.showPopover();
    [.../** @type {NodeListOf<HTMLElement>} */ (el.querySelectorAll(ITEM))].find((x) => x.closest(MENU) === el && !disabled(x))?.focus();
  }, [isOpen]);

  useEffect(() => {
    const at = requestAnimationFrame(() => root.current?.setAttribute('data-ready', ''));
    return () => cancelAnimationFrame(at);
  }, []);

  return createElement('div', /** @type {any} */ ({ popover: 'manual', id, ...rest, ref: setRef, role, 'data-ui': 'menu' }), children);
}
// Marked pure, so a bundle that does not use the component drops the module (X6).
export const Menu = /* @__PURE__ */ Object.assign(MenuRoot, { kitRole: role, displayName: 'Menu' });
