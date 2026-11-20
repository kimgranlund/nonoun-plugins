// @ts-check
/**
 * meter.js: a value within a known range, shown as a filled track, for React (docs/specs/targets.md; rules J17
 * and J18 of docs/specs/patterns.md).
 *
 * The root is a <div> with the meter role. Its aria-valuemin, aria-valuemax and aria-valuenow follow min, max
 * and value, with the value held between min and max and a max that is not above min treated as min (J17). The
 * value's share of the range, a number from 0 to 1, goes to the recipe as the private custom property --_share on
 * the root's inline style, as on the Web Component; it is the one style this component writes, and the author's
 * own style is kept (J18). A value that is missing or is not a number reads as 0, as a number prop does on the
 * Web Component; the value attribute is rendered as the author gave it.
 */
import { createElement, useCallback, useEffect, useRef } from 'react';
import { props as spec, role as kitRole } from '../../components/meter/meter.props.js';

/**
 * @typedef {Omit<import('react').HTMLAttributes<HTMLDivElement>, 'defaultValue'> & {
 *   value?: number, min?: number, max?: number,
 *   ref?: import('react').Ref<HTMLDivElement>,
 * }} MeterProps
 */

/** A number prop's value, or its default when the value is not a finite number. @param {string} name @param {unknown} value */
const num = (name, value) => {
  const n = typeof value === 'string' && value.trim() === '' ? NaN : Number(value);
  return value !== undefined && value !== null && Number.isFinite(n) ? n : /** @type {{ default?: number }} */ (spec[name]).default ?? 0;
};

/** @param {MeterProps} props */
export function Meter({ value, min, max, role = kitRole, style, children, ref, ...rest }) {
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
  const now = Math.min(Math.max(num('value', value), low), high);
  return createElement('div', /** @type {any} */ ({
    ...rest, ref: setRef, role, 'data-ui': 'meter',
    value, min, max,
    'aria-valuemin': String(low), 'aria-valuemax': String(high), 'aria-valuenow': String(now),
    style: { ...style, '--_share': String(high > low ? (now - low) / (high - low) : 0) },
  }), children);
}
