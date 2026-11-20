// @ts-check
/**
 * progress.js: how far a task has got, shown as a filled track, or that it is running when how far is not known,
 * for React (docs/specs/targets.md; rules J96 and J97 of docs/specs/patterns.md).
 *
 * The root is a <div> with the progressbar role. Its aria-valuemin and aria-valuemax follow min and max, and its
 * aria-valuenow follows value, held between min and max (J96). It is indeterminate when `value` is undefined or
 * null, and 0 is a value: the root then renders no `value` attribute, which is the form its recipe selects for the
 * moving run (`:not([value])`), no aria-valuenow and no --_share. With a value, the share of the range, a number
 * from 0 to 1, goes to the recipe as the private custom property --_share on the root's inline style, as on the Web
 * Component (J97); it is the one style this component writes, and the author's own style is kept.
 */
import { createElement, useCallback, useEffect, useRef } from 'react';
import { props as spec, role as kitRole } from '../../components/progress/progress.props.js';

/**
 * @typedef {Omit<import('react').HTMLAttributes<HTMLDivElement>, 'defaultValue'> & {
 *   value?: number | null, min?: number, max?: number,
 *   ref?: import('react').Ref<HTMLDivElement>,
 * }} ProgressProps
 */

/** A number prop's value, or its default when the value is not a finite number. @param {string} name @param {unknown} value */
const num = (name, value) => {
  const n = typeof value === 'string' && value.trim() === '' ? NaN : Number(value);
  return value !== undefined && value !== null && Number.isFinite(n) ? n : /** @type {{ default?: number }} */ (spec[name]).default ?? 0;
};

/** @param {ProgressProps} props */
export function Progress({ value, min, max, role = kitRole, style, children, ref, ...rest }) {
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

  // The range as it is used: max is never below min, and the value is held inside.
  const low = num('min', min);
  const high = Math.max(num('max', max), low);
  const determinate = value !== undefined && value !== null;
  const now = Math.min(Math.max(num('value', value), low), high);
  return createElement('div', /** @type {any} */ ({
    ...rest, ref: setRef, role, 'data-ui': 'progress',
    value, min, max,
    'aria-valuemin': String(low), 'aria-valuemax': String(high), 'aria-valuenow': determinate ? String(now) : undefined,
    style: determinate ? { ...style, '--_share': String(high > low ? (now - low) / (high - low) : 0) } : style,
  }), children);
}
