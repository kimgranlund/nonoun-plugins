// @ts-check
/**
 * breadcrumb.js: the trail of links from the top of a site to the current page, for React
 * (docs/specs/targets.md; rules J13 and J14 of docs/specs/patterns.md).
 *
 * The root is a native <nav>, which has the navigation role itself, so no role is written. It is named
 * "Breadcrumb" (messages.label of the manifest) unless the author wrote aria-label or aria-labelledby, an empty
 * aria-label included, so the server markup already carries the name. The links are the author's anchors and are
 * rendered as given; the author marks the current page with aria-current="page".
 */
import { createElement, useCallback, useEffect, useRef } from 'react';
import { role as kitRole } from '../../components/breadcrumb/breadcrumb.props.js';

/** The name written when the author wrote none: messages.label in breadcrumb.manifest.json. */
const LABEL = 'Breadcrumb';

/**
 * @typedef {import('react').HTMLAttributes<HTMLElement> & {
 *   ref?: import('react').Ref<HTMLElement>,
 * }} BreadcrumbProps
 */

/** @param {BreadcrumbProps} props */
export function Breadcrumb({ children, ref, ...rest }) {
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
  // A <nav> has the role the manifest names; an author's own role goes through the rest.
  void kitRole;
  return createElement('nav', /** @type {any} */ ({ ...rest, ref: setRef, 'data-ui': 'breadcrumb', 'aria-label': named ? rest['aria-label'] : LABEL }), children);
}
