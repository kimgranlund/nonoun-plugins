// @ts-check
/**
 * menu-item.js: one action in a menu, for React (docs/specs/targets.md).
 *
 * The root is a <div role="menuitem">, which has no native disabled state, so disabled is written as
 * aria-disabled (X2). It mounts press, as the Web Component does, so Enter and Space click it; the menu's
 * roving focus writes its tabindex, and the menu closes when it is clicked.
 */
import { createElement, useCallback, useEffect, useLayoutEffect, useRef } from 'react';
import { press } from '../../behaviours/press.js';
import { role } from '../../components/menu-item/menu-item.props.js';

/**
 * @typedef {import('react').HTMLAttributes<HTMLDivElement> & {
 *   disabled?: boolean,
 *   ref?: import('react').Ref<HTMLDivElement>,
 * }} MenuItemProps
 */

/** @param {MenuItemProps} props */
function MenuItemRoot({ disabled = false, children, ref, ...rest }) {
  /** @type {import('react').RefObject<HTMLDivElement | null>} */
  const root = useRef(null);
  const setRef = useCallback((/** @type {HTMLDivElement | null} */ node) => {
    root.current = node;
    if (typeof ref === 'function') ref(node);
    else if (ref) ref.current = node;
  }, [ref]);
  const latest = useRef(disabled);
  latest.current = disabled;

  useLayoutEffect(() => press(/** @type {HTMLDivElement} */ (root.current), { disabled: () => latest.current }), []);
  useEffect(() => {
    const at = requestAnimationFrame(() => root.current?.setAttribute('data-ready', ''));
    return () => cancelAnimationFrame(at);
  }, []);

  return createElement('div', /** @type {any} */ ({ ...rest, ref: setRef, role, 'data-ui': 'menu-item', 'aria-disabled': disabled ? 'true' : undefined }), children);
}
// Marked pure, so a bundle that does not use the component drops the module (X6).
export const MenuItem = /* @__PURE__ */ Object.assign(MenuItemRoot, { kitRole: role, displayName: 'MenuItem' });
