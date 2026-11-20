// @ts-check
/**
 * alert.js: a short message that assistive technology announces as soon as it appears, for React
 * (docs/specs/targets.md; rules J15 and J16 of docs/specs/patterns.md).
 *
 * The root is a <div> with the alert role unless the author wrote a role (role="status" for a polite message).
 * The variant is data-variant. It takes no focus and renders its children as given.
 */
import { createElement, useCallback, useEffect, useRef } from 'react';
import { props as spec, role as kitRole } from '../../components/alert/alert.props.js';

/**
 * @typedef {import('react').HTMLAttributes<HTMLDivElement> & {
 *   variant?: 'neutral' | 'info' | 'success' | 'warning' | 'critical',
 *   ref?: import('react').Ref<HTMLDivElement>,
 * }} AlertProps
 */

/** An enum prop's value, or its default when the value is not one of the manifest's. @param {string} name @param {unknown} value */
const pick = (name, value) => {
  const p = /** @type {{ values: readonly string[], default: string }} */ (spec[name]);
  return typeof value === 'string' && p.values.includes(value) ? value : p.default;
};

/** @param {AlertProps} props */
export function Alert({ variant, role = kitRole, children, ref, ...rest }) {
  /** @type {import('react').RefObject<HTMLDivElement | null>} */
  const root = useRef(null);
  const setRef = useCallback((/** @type {HTMLDivElement | null} */ node) => {
    root.current = node;
    if (typeof ref === 'function') ref(node);
    else if (ref) ref.current = node;
  }, [ref]);
  useEffect(() => {
    const at = requestAnimationFrame(() => root.current?.setAttribute('data-ready', ''));
    return () => cancelAnimationFrame(at);
  }, []);

  return createElement('div', /** @type {any} */ ({ ...rest, ref: setRef, role, 'data-ui': 'alert', 'data-variant': pick('variant', variant) }), children);
}
