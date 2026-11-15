// @ts-check
/**
 * tab.js: one tab, for React (docs/specs/targets.md).
 *
 * The root is a native <button role="tab" type="button">: the native disabled state takes it out of focus and
 * out of the pointer's reach (G8). It mounts press, as the Web Component does, so Enter and Space click it; a
 * click selects it, and with automatic activation so does focus (G7). The tab list's roving focus writes its
 * tabindex. `selected` is read by the tabs element for the first value only; afterwards the tabs element's
 * value decides.
 */
import { createElement, useCallback, useContext, useEffect, useLayoutEffect, useRef } from 'react';
import { press } from '../../behaviours/press.js';
import { TabsContext, PositionContext } from '../tabs/tabs.js';
import { role } from '../../components/tab/tab.props.js';

/**
 * @typedef {Omit<import('react').ButtonHTMLAttributes<HTMLButtonElement>, 'value' | 'type'> & {
 *   value?: string, selected?: boolean, disabled?: boolean,
 *   ref?: import('react').Ref<HTMLButtonElement>,
 * }} TabProps
 */

/** @param {TabProps} props */
function TabRoot({ value, selected = false, disabled = false, onClick, onFocus, id, children, ref, ...rest }) {
  const tabs = useContext(TabsContext);
  const position = useContext(PositionContext);
  const own = value ?? (position?.kind === 'tab' ? String(position.index) : '');
  const isSelected = tabs ? tabs.hasTab(own) && tabs.value === own : selected;
  /** @type {import('react').RefObject<HTMLButtonElement | null>} */
  const root = useRef(null);
  const setRef = useCallback((/** @type {HTMLButtonElement | null} */ node) => {
    root.current = node;
    if (typeof ref === 'function') ref(node);
    else if (ref) ref.current = node;
  }, [ref]);

  useLayoutEffect(() => {
    const el = /** @type {HTMLButtonElement} */ (root.current);
    return press(el, { disabled: () => el.disabled });
  }, []);
  useEffect(() => {
    const at = requestAnimationFrame(() => root.current?.setAttribute('data-ready', ''));
    return () => cancelAnimationFrame(at);
  }, []);

  return createElement('button', /** @type {any} */ ({
    ...rest, ref: setRef, type: 'button', role, 'data-ui': 'tab',
    id: id ?? tabs?.tabId(own),
    'aria-selected': String(isSelected),
    'aria-controls': tabs?.hasPanel(own) ? tabs.panelId(own) : undefined,
    disabled,
    onClick: (/** @type {import('react').MouseEvent<HTMLButtonElement>} */ event) => {
      onClick?.(event);
      if (!event.defaultPrevented && !disabled) tabs?.choose(own, event);
    },
    onFocus: (/** @type {import('react').FocusEvent<HTMLButtonElement>} */ event) => {
      onFocus?.(event);
      if (!event.defaultPrevented && !disabled && tabs?.activation === 'automatic') tabs.choose(own, event);
    },
  }), children);
}
// Marked pure, so a bundle that does not use the component drops the module (X6).
export const Tab = /* @__PURE__ */ Object.assign(TabRoot, { kitRole: role, displayName: 'Tab' });
