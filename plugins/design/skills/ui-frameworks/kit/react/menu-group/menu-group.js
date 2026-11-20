// @ts-check
/**
 * menu-group.js: a set of menu items that belong together, for React (docs/specs/targets.md).
 *
 * The root is a <div role="group">. Of the radio items inside it, it keeps at most one checked: it gives them,
 * through React context which this module exports, the radio that the user turned on last, and each
 * uncontrolled radio is checked exactly when it is that one (J22). A menu inside it, a submenu's, starts afresh.
 *
 * Its label is the author's child marked data-part="label", which it never clones or wraps, so it names itself
 * as the Web Component does, in the DOM after each render and whenever its subtree changes: aria-labelledby to
 * the label's id, giving the label an id only when it has none, unless the author named the group (J23).
 */
import { createContext, createElement, useCallback, useEffect, useLayoutEffect, useMemo, useRef, useState } from 'react';
import { role } from '../../components/menu-group/menu-group.props.js';

/**
 * @typedef {{ chosen: string | null, choose: (id: string) => void }} MenuGroupState
 * @typedef {import('react').HTMLAttributes<HTMLDivElement> & {
 *   ref?: import('react').Ref<HTMLDivElement>,
 * }} MenuGroupProps
 */

/** What the radio items of the nearest group read. @type {import('react').Context<MenuGroupState | null>} */
export const MenuGroupContext = /* @__PURE__ */ createContext(/** @type {MenuGroupState | null} */ (null));

/** For the ids given to a label that has none. */
let serial = 0;

/** @param {MenuGroupProps} props */
function MenuGroupRoot({ children, ref, ...rest }) {
  const [chosen, choose] = useState(/** @type {string | null} */ (null));
  /** @type {import('react').RefObject<HTMLDivElement | null>} */
  const root = useRef(null);
  const setRef = useCallback((/** @type {HTMLDivElement | null} */ node) => {
    root.current = node;
    if (typeof ref === 'function') ref(node);
    else if (ref) ref.current = node;
  }, [ref]);
  /** @type {import('react').RefObject<string | null>} The aria-labelledby value this element wrote, so that it never replaces an author's. */
  const named = useRef(null);

  /** Names the group after its label, unless the author named it. Writes nothing when it already is. */
  const name = useCallback(() => {
    const el = root.current;
    if (!el) return;
    const current = el.getAttribute('aria-labelledby');
    if (current !== null && current !== named.current) return;
    const label = /** @type {HTMLElement | undefined} */ ([...el.children].find((c) => c.getAttribute('data-part') === 'label'));
    // A name the author gave with aria-label wins: the reference this element wrote would hide it.
    if (!label || el.hasAttribute('aria-label')) {
      if (current !== null) el.removeAttribute('aria-labelledby');
      named.current = null;
      return;
    }
    if (!label.id) label.id = `ui-menu-group-${++serial}`;
    if (current !== label.id) el.setAttribute('aria-labelledby', label.id);
    named.current = label.id;
  }, []);

  useLayoutEffect(name);
  useLayoutEffect(() => {
    const observer = new MutationObserver(name);
    observer.observe(/** @type {HTMLDivElement} */ (root.current), { childList: true, subtree: true, attributes: true, attributeFilter: ['data-part', 'id', 'aria-label'] });
    return () => observer.disconnect();
  }, [name]);
  useEffect(() => {
    const at = requestAnimationFrame(() => root.current?.setAttribute('data-ready', ''));
    return () => cancelAnimationFrame(at);
  }, []);

  const state = useMemo(() => ({ chosen, choose }), [chosen]);
  return createElement('div', /** @type {any} */ ({ ...rest, ref: setRef, role, 'data-ui': 'menu-group' }),
    createElement(MenuGroupContext.Provider, { value: state }, children));
}
// Marked pure, so a bundle that does not use the component drops the module (X6).
export const MenuGroup = /* @__PURE__ */ Object.assign(MenuGroupRoot, { kitRole: role, displayName: 'MenuGroup' });
