// @ts-check
/**
 * toolbar.js: a row of controls that is one stop in the Tab order, for React (docs/specs/targets.md).
 *
 * The root is a <div role="toolbar">. Its controls are the author's elements of other families, so it finds
 * them in the DOM by their role, as the Web Component does: the button, checkbox, switch and link roles, a
 * native button, a native link, and the native checkbox, whose role is implicit (the React checkbox's input).
 * It mounts roving focus, which writes their tabindex and moves focus among them with the arrow keys (J19);
 * no control renders a tabindex of its own. Vertical is written as aria-orientation, ARIA's form (X2).
 */
import { createElement, useCallback, useEffect, useLayoutEffect, useRef } from 'react';
import { rovingFocus } from '../../behaviours/roving-focus.js';
import { props as spec, role } from '../../components/toolbar/toolbar.props.js';

/**
 * @typedef {import('react').HTMLAttributes<HTMLDivElement> & {
 *   orientation?: 'horizontal' | 'vertical',
 *   ref?: import('react').Ref<HTMLDivElement>,
 * }} ToolbarProps
 */

/** What counts as a control. The Web Component's list, and the native checkbox, whose checkbox role is implicit. */
const CONTROL = '[role="button"], [role="checkbox"], [role="switch"], [role="link"], button, a[href], input[type="checkbox"]';
const ROOT = '[role="toolbar"]';
/** @param {Element} el */
const disabled = (el) => el.hasAttribute('disabled') || el.getAttribute('aria-disabled') === 'true';

/** @param {ToolbarProps} props */
function ToolbarRoot({ orientation, children, ref, ...rest }) {
  const p = /** @type {{ values: readonly string[], default: string }} */ (spec.orientation);
  const o = /** @type {'horizontal' | 'vertical'} */ (p.values.includes(orientation ?? '') ? orientation : p.default);
  /** @type {import('react').RefObject<HTMLDivElement | null>} */
  const root = useRef(null);
  const setRef = useCallback((/** @type {HTMLDivElement | null} */ node) => {
    root.current = node;
    if (typeof ref === 'function') ref(node);
    else if (ref) ref.current = node;
  }, [ref]);
  const latest = useRef(o);
  latest.current = o;

  useLayoutEffect(() => {
    const el = /** @type {HTMLDivElement} */ (root.current);
    /** Whether a control lies inside another control below this toolbar: it is a part of that one. @param {Element} c */
    const inside = (c) => { const up = c.parentElement?.closest(CONTROL); return !!up && el.contains(up); };
    // In document order; a control of a toolbar nested in this one is that toolbar's.
    const controls = () => /** @type {HTMLElement[]} */ ([...el.querySelectorAll(CONTROL)].filter((c) => c.closest(ROOT) === el && !inside(c)));
    return rovingFocus(el, {
      items: controls,
      orientation: () => latest.current,
      skip: disabled,
      // A control that writes its own tabindex="0" later brings the stop back to one.
      watch: ['tabindex'],
    });
  }, []);
  useEffect(() => {
    const at = requestAnimationFrame(() => root.current?.setAttribute('data-ready', ''));
    return () => cancelAnimationFrame(at);
  }, []);

  // ARIA's default for a toolbar is horizontal, so only vertical is written.
  return createElement('div', /** @type {any} */ ({ ...rest, ref: setRef, role, 'data-ui': 'toolbar', 'aria-orientation': o === 'vertical' ? 'vertical' : undefined }), children);
}
// Marked pure, so a bundle that does not use the component drops the module (X6).
export const Toolbar = /* @__PURE__ */ Object.assign(ToolbarRoot, { kitRole: role, displayName: 'Toolbar' });
