// @ts-check
/**
 * button.js: the button for React (docs/specs/targets.md). A plain module that calls createElement; no build step.
 *
 * The root is a native <button>, so the platform submits and resets the form, gives the submitter, and makes
 * this the form's default button: the Web Component needs a hidden submit part for that (D19), this does not.
 * The press behaviour is mounted as on the Web Component, so Enter activates at key down and Space at key up,
 * once, with data-active while the key is held (F8 to F10).
 */
import { createElement, useCallback, useEffect, useLayoutEffect, useRef } from 'react';
import { press } from '../../behaviours/press.js';
import { props as spec } from '../../components/button/button.props.js';

/**
 * @typedef {Omit<import('react').ButtonHTMLAttributes<HTMLButtonElement>, 'type'> & {
 *   variant?: 'neutral' | 'primary' | 'ghost',
 *   type?: 'button' | 'submit' | 'reset',
 *   ref?: import('react').Ref<HTMLButtonElement>,
 * }} ButtonProps
 */

/** An enum prop's value, or its default when the value is not one of the manifest's. @param {string} name @param {unknown} value */
const pick = (name, value) => {
  const p = /** @type {{ values: readonly string[], default: string }} */ (spec[name]);
  return typeof value === 'string' && p.values.includes(value) ? value : p.default;
};

/** @param {ButtonProps} props */
export function Button({ variant, type, value, name, disabled = false, ref, ...rest }) {
  /** @type {import('react').RefObject<HTMLButtonElement | null>} */
  const own = useRef(null);
  const setRef = useCallback((/** @type {HTMLButtonElement | null} */ node) => {
    own.current = node;
    if (typeof ref === 'function') ref(node);
    else if (ref) ref.current = node;
  }, [ref]);

  // The platform's own disabled state, which a fieldset sets too (F4).
  useLayoutEffect(() => {
    const el = /** @type {HTMLButtonElement} */ (own.current);
    return press(el, { disabled: () => el.matches(':disabled') });
  }, []);
  // data-ready one frame after the root is in the page, as on every Web Component (L6): transitions start then.
  useEffect(() => {
    const id = requestAnimationFrame(() => own.current?.setAttribute('data-ready', ''));
    return () => cancelAnimationFrame(id);
  }, []);

  return createElement('button', /** @type {any} */ ({ ...rest, ref: setRef, 'data-ui': 'button', 'data-variant': pick('variant', variant), type: pick('type', type), value, name, disabled }));
}
