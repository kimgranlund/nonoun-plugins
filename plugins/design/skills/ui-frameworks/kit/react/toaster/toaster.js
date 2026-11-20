// @ts-check
/**
 * toaster.js: the stack that holds toasts, for React (docs/specs/targets.md).
 *
 * The root is a <div> with the region role and popover="manual", named "Notifications" (Toaster.label) in
 * aria-label unless the author passed aria-label or aria-labelledby; a role or a popover the author passes wins
 * (J94). All of it is rendered, so the server markup has it too. It shows in the top layer exactly while one of
 * its children has the status or the alert role and `open`, and leaves it when none has. It finds toasts by
 * role in the DOM, as the Web Component does, so a toast of either target counts; it looks after each render
 * and whenever a child, its `open` or its role changes. It writes nothing on a toast.
 *
 * `placement` is the variant data-placement: the recipe places the stack in that corner of the window, with the
 * newest toast, the last child, nearest it, and lets presses through wherever no toast is.
 */
import { createElement, useCallback, useLayoutEffect, useEffect, useRef } from 'react';
import { props as spec, role } from '../../components/toaster/toaster.props.js';

/**
 * @typedef {import('react').HTMLAttributes<HTMLDivElement> & {
 *   placement?: 'block-end inline-end' | 'block-end inline-start' | 'block-start inline-end' | 'block-start inline-start',
 *   popover?: string,
 *   ref?: import('react').Ref<HTMLDivElement>,
 * }} ToasterProps
 */

/** The roles of a toast. */
const ROLES = ['status', 'alert'];

/** An enum prop's value, or its default when the value is not one of the manifest's. @param {string} name @param {unknown} value */
const pick = (name, value) => {
  const p = /** @type {{ values: readonly string[], default: string }} */ (spec[name]);
  return typeof value === 'string' && p.values.includes(value) ? value : p.default;
};

/** @param {ToasterProps} props */
function ToasterRoot({ placement, children, ref, ...rest }) {
  /** @type {import('react').RefObject<HTMLDivElement | null>} */
  const root = useRef(null);
  const setRef = useCallback((/** @type {HTMLDivElement | null} */ node) => {
    root.current = node;
    if (typeof ref === 'function') ref(node);
    else if (ref) ref.current = node;
  }, [ref]);

  /** Shows the popover while a toast is open and hides it when none is. */
  const sync = useCallback(() => {
    const el = root.current;
    // A popover the author took away leaves nothing to show.
    if (!el?.isConnected || !el.hasAttribute('popover')) return;
    const holds = [...el.children].some((x) => ROLES.includes(x.getAttribute('role') ?? '') && x.hasAttribute('open'));
    if (holds === el.matches(':popover-open')) return;
    if (holds) el.showPopover();
    else el.hidePopover();
  }, []);

  useLayoutEffect(sync);
  useLayoutEffect(() => {
    const el = /** @type {HTMLDivElement} */ (root.current);
    const observer = new MutationObserver(sync);
    observer.observe(el, { childList: true, subtree: true, attributes: true, attributeFilter: ['open', 'role'] });
    return () => observer.disconnect();
  }, [sync]);
  useEffect(() => {
    const at = requestAnimationFrame(() => root.current?.setAttribute('data-ready', ''));
    return () => cancelAnimationFrame(at);
  }, []);

  const named = rest['aria-label'] !== undefined || rest['aria-labelledby'] !== undefined;
  return createElement('div', /** @type {any} */ ({
    role, popover: 'manual', ...(named ? {} : { 'aria-label': Toaster.label }),
    ...rest, ref: setRef, 'data-ui': 'toaster', 'data-placement': pick('placement', placement),
  }), children);
}
// Marked pure, so a bundle that does not use the component drops the module (X6). `label` is the name it has
// when the author gave it none, as the Web Component's static field is.
export const Toaster = /* @__PURE__ */ Object.assign(ToasterRoot, { kitRole: role, displayName: 'Toaster', label: 'Notifications' });
