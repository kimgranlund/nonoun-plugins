// @ts-check
/**
 * menubar.js: a row of menus, for React (docs/specs/targets.md).
 *
 * The root is a <div role="menubar">. Its buttons are the triggers of the menu buttons the author writes
 * inside it, which belong to another family, so it finds them in the DOM as the Web Component does: the
 * elements with the button role, or native buttons, that are not inside a menu and that their menu button has
 * marked with aria-haspopup, not of a menubar nested in this one. It mounts roving focus, which writes their
 * tabindex and moves focus among them along the row, wrapping (J26).
 *
 * While one of its menus is open, ArrowRight and ArrowLeft pressed inside it, through React's onKeyDown, move
 * focus to the next or the previous button, which closes the open menu (focus leaves it), and open that
 * button's menu. A React menu has no open attribute (its open state is :popover-open), so the menubar opens it
 * as Enter does: with a click on its button. A key whose default action is already prevented, such as an arrow
 * a submenu took, is left alone. A button's menu is the element its aria-controls names.
 */
import { createElement, useCallback, useEffect, useLayoutEffect, useRef } from 'react';
import { rovingFocus } from '../../behaviours/roving-focus.js';
import { role } from '../../components/menubar/menubar.props.js';

/**
 * @typedef {import('react').HTMLAttributes<HTMLDivElement> & {
 *   ref?: import('react').Ref<HTMLDivElement>,
 * }} MenubarProps
 */

const BUTTON = 'button, [role="button"]';
const MENU = '[role="menu"]';
const ROOT = '[role="menubar"]';
/** @param {Element} el */
const disabled = (el) => el.hasAttribute('disabled') || el.getAttribute('aria-disabled') === 'true';

/** The buttons of a menubar, in document order. @param {HTMLElement} el */
const buttonsOf = (el) => /** @type {HTMLElement[]} */ ([...el.querySelectorAll(BUTTON)].filter((b) => b.closest(ROOT) === el
  && b.hasAttribute('aria-haspopup') && !b.closest(MENU)));

/** @param {MenubarProps} props */
function MenubarRoot({ onKeyDown, children, ref, ...rest }) {
  /** @type {import('react').RefObject<HTMLDivElement | null>} */
  const root = useRef(null);
  const setRef = useCallback((/** @type {HTMLDivElement | null} */ node) => {
    root.current = node;
    if (typeof ref === 'function') ref(node);
    else if (ref) ref.current = node;
  }, [ref]);

  useLayoutEffect(() => {
    const el = /** @type {HTMLDivElement} */ (root.current);
    return rovingFocus(el, {
      items: () => buttonsOf(el),
      orientation: () => 'horizontal',
      skip: disabled,
      // A trigger becomes a button of the bar when its menu button marks it.
      watch: ['aria-haspopup'],
    });
  }, []);
  useEffect(() => {
    const at = requestAnimationFrame(() => root.current?.setAttribute('data-ready', ''));
    return () => cancelAnimationFrame(at);
  }, []);

  /** An arrow along the row, pressed inside an open menu, moves to the next or the previous menu (J26). @param {import('react').KeyboardEvent<HTMLDivElement>} event */
  const keyDown = (event) => {
    onKeyDown?.(event);
    const el = /** @type {HTMLDivElement} */ (root.current);
    if (event.nativeEvent.defaultPrevented || event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) return;
    if (event.key !== 'ArrowRight' && event.key !== 'ArrowLeft') return;
    const target = event.target;
    if (!(target instanceof Element)) return;
    const buttons = buttonsOf(el).filter((b) => !disabled(b));
    const at = buttons.findIndex((b) => {
      const id = b.getAttribute('aria-controls');
      const menu = id ? el.querySelector(`#${CSS.escape(id)}`) : null;
      return !!menu && menu.contains(target);
    });
    if (at < 0) return;
    const forward = (event.key === 'ArrowRight') === (getComputedStyle(el).direction !== 'rtl');
    const next = buttons[(at + (forward ? 1 : -1) + buttons.length) % buttons.length];
    event.preventDefault();
    // Focus leaving the open menu closes it, and every menu inside it (G14).
    next.focus();
    next.click();
  };

  return createElement('div', /** @type {any} */ ({ ...rest, ref: setRef, role, 'data-ui': 'menubar', onKeyDown: keyDown }), children);
}
// Marked pure, so a bundle that does not use the component drops the module (X6).
export const Menubar = /* @__PURE__ */ Object.assign(MenubarRoot, { kitRole: role, displayName: 'Menubar' });
