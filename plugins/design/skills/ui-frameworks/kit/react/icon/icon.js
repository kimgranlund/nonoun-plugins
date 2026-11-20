// @ts-check
/**
 * icon.js: one icon from the kit's set, drawn by CSS in the ink of whatever it sits in, for React
 * (docs/specs/targets.md; docs/specs/icons.md, I1 to I8).
 *
 * The root is a <span> with data-ui="icon" and the name attribute: kit/styles/icons.css gives each glyph on this
 * root as well as on the Web Component's `ui-icon` tag. Nothing needs a script: the recipe paints it as it paints the
 * Web Component before it is defined (I1), selecting the root by data-ui and the size by data-size. The icon names itself as the
 * Web Component does (I8): with no aria-label or aria-labelledby it is hidden from assistive technology, and with one it is an
 * image, and an aria-hidden or a role the author wrote is never replaced. It writes no label.
 */
import { createElement, useCallback, useEffect, useRef } from 'react';
import { props as spec } from '../../components/icon/icon.props.js';

/**
 * @typedef {Omit<import('react').HTMLAttributes<HTMLElement>, 'role'> & {
 *   name?: string, size?: 'sm' | 'md' | 'lg' | 'full', role?: string,
 *   ref?: import('react').Ref<HTMLElement>,
 * }} IconProps
 */

/** An enum prop's value, or its default when the value is not one of the manifest's. @param {string} name @param {unknown} value */
const pick = (name, value) => {
  const p = /** @type {{ values: readonly string[], default: string }} */ (spec[name]);
  return typeof value === 'string' && p.values.includes(value) ? value : p.default;
};

/** @param {IconProps} props */
export function Icon({ name, size, children, ref, ...rest }) {
  /** @type {import('react').RefObject<HTMLElement | null>} */
  const root = useRef(null);
  const setRef = useCallback((/** @type {HTMLElement | null} */ node) => {
    root.current = node;
    if (typeof ref === 'function') ref(node);
    else if (ref) ref.current = node;
  }, [ref]);
  useEffect(() => {
    const at = requestAnimationFrame(() => root.current?.setAttribute('data-ready', ''));
    return () => cancelAnimationFrame(at);
  }, []);

  const named = rest['aria-label'] !== undefined || rest['aria-labelledby'] !== undefined;
  return createElement('span', /** @type {any} */ ({
    ...rest, ref: setRef, name, 'data-ui': 'icon', 'data-size': pick('size', size),
    'aria-hidden': named ? rest['aria-hidden'] : (rest['aria-hidden'] ?? 'true'),
    role: named ? (rest.role ?? 'img') : rest.role,
  }), children);
}
