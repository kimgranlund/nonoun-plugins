// @ts-check
/**
 * tab-panel.js: the content one tab shows, for React (docs/specs/targets.md).
 *
 * The root is a <div role="tabpanel">, in the Tab order unless the author gives another tabIndex. The tabs
 * element decides whether it is hidden, gives it an id when the author gave none, and names it after its tab
 * when the author named it neither with aria-label nor with aria-labelledby (G4, A2).
 */
import { createElement, useCallback, useContext, useEffect, useRef } from 'react';
import { TabsContext, PositionContext } from '../tabs/tabs.js';
import { role, tabindex } from '../../components/tab-panel/tab-panel.props.js';

/**
 * @typedef {import('react').HTMLAttributes<HTMLDivElement> & {
 *   value?: string,
 *   ref?: import('react').Ref<HTMLDivElement>,
 * }} TabPanelProps
 */

/** @param {TabPanelProps} props */
function TabPanelRoot({ value, id, children, ref, ...rest }) {
  const tabs = useContext(TabsContext);
  const position = useContext(PositionContext);
  const own = value ?? (position?.kind === 'tabpanel' ? String(position.index) : '');
  const shown = tabs ? tabs.hasTab(tabs.value) && tabs.value === own : true;
  const named = rest['aria-label'] !== undefined || rest['aria-labelledby'] !== undefined;
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

  return createElement('div', /** @type {any} */ ({
    tabIndex: tabindex, ...rest, ref: setRef, role, 'data-ui': 'tab-panel',
    id: id ?? tabs?.panelId(own),
    'aria-labelledby': named || !tabs?.hasTab(own) ? rest['aria-labelledby'] : tabs.tabId(own),
    hidden: !shown,
  }), children);
}
// Marked pure, so a bundle that does not use the component drops the module (X6).
export const TabPanel = /* @__PURE__ */ Object.assign(TabPanelRoot, { kitRole: role, displayName: 'TabPanel' });
