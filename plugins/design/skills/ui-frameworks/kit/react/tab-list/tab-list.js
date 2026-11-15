// @ts-check
/**
 * tab-list.js: the list of tabs, for React (docs/specs/targets.md).
 *
 * The root is a <div role="tablist">. It mounts roving focus as the Web Component does, so it is one stop in
 * the Tab order and the arrow keys move among its tabs (B6 to B10); the behaviour writes the tabs' tabindex,
 * which no tab renders. It gives each tab among its children its position, which is the value of a tab that
 * has none.
 */
import { createElement, useCallback, useEffect, useLayoutEffect, useRef } from 'react';
import { rovingFocus } from '../../behaviours/roving-focus.js';
import { positions } from '../tabs/tabs.js';
import { props as spec, role } from '../../components/tab-list/tab-list.props.js';

/**
 * @typedef {import('react').HTMLAttributes<HTMLDivElement> & {
 *   orientation?: 'horizontal' | 'vertical',
 *   ref?: import('react').Ref<HTMLDivElement>,
 * }} TabListProps
 */

const TAB = '[role="tab"]';
/** @param {Element} el */
const disabled = (el) => el.hasAttribute('disabled') || el.getAttribute('aria-disabled') === 'true';

/** @param {TabListProps} props */
function TabListRoot({ orientation, children, ref, ...rest }) {
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
    const tabs = () => /** @type {HTMLElement[]} */ ([...el.querySelectorAll(TAB)]);
    return rovingFocus(el, {
      items: tabs,
      orientation: () => latest.current,
      current: () => tabs().find((tab) => tab.getAttribute('aria-selected') === 'true'),
      skip: disabled,
      watch: ['aria-selected'],
    });
  }, []);
  useEffect(() => {
    const id = requestAnimationFrame(() => root.current?.setAttribute('data-ready', ''));
    return () => cancelAnimationFrame(id);
  }, []);

  // ARIA's default for a tablist is horizontal, so only vertical is written.
  return createElement('div', /** @type {any} */ ({ ...rest, ref: setRef, role, 'data-ui': 'tab-list', 'aria-orientation': o === 'vertical' ? 'vertical' : undefined }), positions(children, 'tab'));
}
// Marked pure, so a bundle that does not use the component drops the module (X6).
export const TabList = /* @__PURE__ */ Object.assign(TabListRoot, { kitRole: role, displayName: 'TabList' });
