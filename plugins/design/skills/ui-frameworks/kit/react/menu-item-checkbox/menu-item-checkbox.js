// @ts-check
/**
 * menu-item-checkbox.js: a menu item that is on or off, for React (docs/specs/targets.md).
 *
 * The root is a <div role="menuitemcheckbox">, which has no native checked or disabled state, so they are
 * written as aria-checked and aria-disabled (X2). It mounts press, as the Web Component does, so Enter and Space
 * click it. A click turns it on or off: checked is controlled (checked with onChange) or uncontrolled
 * (defaultChecked). onChange(checked, event) is called once per change, after the item is written and while
 * the menu is still open: the click listener is the item's own, which runs before the menu's (J22). The menu
 * writes its tabindex, moves focus to it, and closes after Enter but not after Space or the pointer.
 */
import { createElement, useCallback, useEffect, useLayoutEffect, useRef, useState } from 'react';
import { flushSync } from 'react-dom';
import { press } from '../../behaviours/press.js';
import { role } from '../../components/menu-item-checkbox/menu-item-checkbox.props.js';

/**
 * @typedef {Omit<import('react').HTMLAttributes<HTMLDivElement>, 'onChange' | 'defaultChecked'> & {
 *   checked?: boolean, defaultChecked?: boolean, disabled?: boolean,
 *   onChange?: (checked: boolean, event: MouseEvent) => void,
 *   ref?: import('react').Ref<HTMLDivElement>,
 * }} MenuItemCheckboxProps
 */

/** @param {MenuItemCheckboxProps} props */
function MenuItemCheckboxRoot({ checked, defaultChecked = false, disabled = false, onChange, children, ref, ...rest }) {
  const [own, setOwn] = useState(defaultChecked);
  const on = checked !== undefined ? checked : own;
  /** @type {import('react').RefObject<HTMLDivElement | null>} */
  const root = useRef(null);
  const setRef = useCallback((/** @type {HTMLDivElement | null} */ node) => {
    root.current = node;
    if (typeof ref === 'function') ref(node);
    else if (ref) ref.current = node;
  }, [ref]);
  const latest = useRef({ on, disabled, controlled: checked !== undefined, onChange });
  latest.current = { on, disabled, controlled: checked !== undefined, onChange };

  useLayoutEffect(() => {
    const el = /** @type {HTMLDivElement} */ (root.current);
    const off = new AbortController();
    el.addEventListener('click', (event) => {
      const now = latest.current;
      if (now.disabled) return;
      const next = !now.on;
      // Written before onChange is called, so a listener reads the item up to date.
      if (!now.controlled) flushSync(() => setOwn(next));
      now.onChange?.(next, event);
    }, { signal: off.signal });
    const stop = press(el, { disabled: () => latest.current.disabled });
    return () => { off.abort(); stop(); };
  }, []);
  useEffect(() => {
    const at = requestAnimationFrame(() => root.current?.setAttribute('data-ready', ''));
    return () => cancelAnimationFrame(at);
  }, []);

  return createElement('div', /** @type {any} */ ({
    ...rest, ref: setRef, role, 'data-ui': 'menu-item-checkbox',
    'aria-checked': String(on), 'aria-disabled': disabled ? 'true' : undefined,
  }), children);
}
// Marked pure, so a bundle that does not use the component drops the module (X6).
export const MenuItemCheckbox = /* @__PURE__ */ Object.assign(MenuItemCheckboxRoot, { kitRole: role, displayName: 'MenuItemCheckbox' });
