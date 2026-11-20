// @ts-check
/**
 * menu-item-radio.js: a menu item that is one choice of a group, for React (docs/specs/targets.md).
 *
 * The root is a <div role="menuitemradio">, which has no native checked or disabled state, so they are written
 * as aria-checked and aria-disabled (X2). It mounts press, as the Web Component does, so Enter and Space click
 * it. A click turns it on, never off: checked is controlled (checked with onChange) or uncontrolled
 * (defaultChecked). An uncontrolled item in a menu group tells the group, which then turns the group's other
 * uncontrolled items off, in the same render, before onChange(true, event) is called (J22, G5). value is
 * written on the root, for the author to read.
 */
import { createElement, useCallback, useContext, useEffect, useId, useLayoutEffect, useRef, useState } from 'react';
import { flushSync } from 'react-dom';
import { press } from '../../behaviours/press.js';
import { MenuGroupContext } from '../menu-group/menu-group.js';
import { role } from '../../components/menu-item-radio/menu-item-radio.props.js';

/**
 * @typedef {Omit<import('react').HTMLAttributes<HTMLDivElement>, 'onChange' | 'defaultChecked'> & {
 *   checked?: boolean, defaultChecked?: boolean, disabled?: boolean, value?: string,
 *   onChange?: (checked: boolean, event: MouseEvent) => void,
 *   ref?: import('react').Ref<HTMLDivElement>,
 * }} MenuItemRadioProps
 */

/** @param {MenuItemRadioProps} props */
function MenuItemRadioRoot({ checked, defaultChecked = false, value, disabled = false, onChange, children, ref, ...rest }) {
  const id = useId();
  const group = useContext(MenuGroupContext);
  const [own, setOwn] = useState(defaultChecked);
  // Once the user has chosen in the group, the group's choice decides; until then, what the author wrote.
  const on = checked !== undefined ? checked : group && group.chosen !== null ? group.chosen === id : own;
  /** @type {import('react').RefObject<HTMLDivElement | null>} */
  const root = useRef(null);
  const setRef = useCallback((/** @type {HTMLDivElement | null} */ node) => {
    root.current = node;
    if (typeof ref === 'function') ref(node);
    else if (ref) ref.current = node;
  }, [ref]);
  const latest = useRef({ on, disabled, controlled: checked !== undefined, group, onChange });
  latest.current = { on, disabled, controlled: checked !== undefined, group, onChange };

  useLayoutEffect(() => {
    const el = /** @type {HTMLDivElement} */ (root.current);
    const off = new AbortController();
    el.addEventListener('click', (event) => {
      const now = latest.current;
      if (now.disabled || now.on) return;
      // The group's other items are written before onChange is called, so a listener reads them up to date.
      if (!now.controlled) flushSync(() => { setOwn(true); now.group?.choose(id); });
      now.onChange?.(true, event);
    }, { signal: off.signal });
    const stop = press(el, { disabled: () => latest.current.disabled });
    return () => { off.abort(); stop(); };
  }, [id]);
  useEffect(() => {
    const at = requestAnimationFrame(() => root.current?.setAttribute('data-ready', ''));
    return () => cancelAnimationFrame(at);
  }, []);

  return createElement('div', /** @type {any} */ ({
    ...rest, ref: setRef, role, 'data-ui': 'menu-item-radio', value,
    'aria-checked': String(on), 'aria-disabled': disabled ? 'true' : undefined,
  }), children);
}
// Marked pure, so a bundle that does not use the component drops the module (X6).
export const MenuItemRadio = /* @__PURE__ */ Object.assign(MenuItemRadioRoot, { kitRole: role, displayName: 'MenuItemRadio' });
