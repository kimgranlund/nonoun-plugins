// @ts-check
/**
 * tabs.js: the element that holds a tab list and its panels, for React (docs/specs/targets.md).
 *
 * It coordinates the tab list, the tabs and the panels through React context, which this module exports for
 * them; it writes nothing into the DOM itself. The selected value is controlled (value with onChange) or
 * uncontrolled (defaultValue). With neither, it is the value of the first tab marked selected, or else of the
 * first tab that is not disabled (G9), read from the elements it is given when it first renders.
 *
 * A tab or a panel with no value has its position among its kind as its value, as on the Web Component. In
 * React the position is counted among the children of the tab list, or of the tabs element, and of fragments
 * inside them: a tab or a panel that a component of the author's wraps needs a value.
 *
 * onChange(value, event) is called when the user selects another tab, after the tabs and the panels are up to
 * date when the value is uncontrolled (G5). It is not called when the value prop changes.
 */
import { Children, Fragment, cloneElement, createContext, createElement, isValidElement, useCallback, useEffect, useId, useRef, useState } from 'react';
import { flushSync } from 'react-dom';
import { props as spec } from '../../components/tabs/tabs.props.js';

/**
 * @typedef {{
 *   value: string, activation: 'automatic' | 'manual',
 *   choose: (value: string, event: import('react').SyntheticEvent) => void,
 *   tabId: (value: string) => string, panelId: (value: string) => string,
 *   hasTab: (value: string) => boolean, hasPanel: (value: string) => boolean,
 * }} TabsState
 * @typedef {Omit<import('react').HTMLAttributes<HTMLDivElement>, 'onChange' | 'defaultValue'> & {
 *   value?: string, defaultValue?: string, activation?: 'automatic' | 'manual',
 *   onChange?: (value: string, event: import('react').SyntheticEvent) => void,
 *   ref?: import('react').Ref<HTMLDivElement>,
 * }} TabsProps
 */

/** What the tab list, the tabs and the panels of the nearest tabs element read. @type {import('react').Context<TabsState | null>} */
export const TabsContext = /* @__PURE__ */ createContext(/** @type {TabsState | null} */ (null));
/** A tab's or a panel's position among its kind. @type {import('react').Context<{ kind: string, index: number } | null>} */
export const PositionContext = /* @__PURE__ */ createContext(/** @type {{ kind: string, index: number } | null} */ (null));

/** The role a component of this family renders, so that the walk below knows it without importing it. @param {unknown} node */
export const roleOf = (node) => (isValidElement(node) && typeof node.type === 'function' ? /** @type {any} */ (node.type).kitRole : undefined);

/**
 * Gives every child element of one role its position, through fragments, leaving the rest alone.
 * @param {import('react').ReactNode} children @param {string} kind @param {{ n: number }} [count]
 * @returns {import('react').ReactNode}
 */
export function positions(children, kind, count = { n: 0 }) {
  return Children.map(children, (child) => {
    if (!isValidElement(child)) return child;
    if (child.type === Fragment) return cloneElement(child, undefined, positions(/** @type {any} */ (child.props).children, kind, count));
    if (roleOf(child) !== kind) return child;
    return createElement(PositionContext.Provider, { value: { kind, index: count.n++ } }, child);
  });
}

/**
 * The props of the tabs and the panels among the children, in order, each with the value it will have.
 * @param {import('react').ReactNode} children
 * @param {{ tabs: any[], panels: any[] }} [out]
 */
function collect(children, out = { tabs: [], panels: [] }) {
  Children.forEach(children, (child) => {
    if (!isValidElement(child)) return;
    const props = /** @type {any} */ (child.props);
    const role = roleOf(child);
    if (role === 'tab') out.tabs.push({ ...props, value: props.value ?? String(out.tabs.length) });
    else if (role === 'tabpanel') out.panels.push({ ...props, value: props.value ?? String(out.panels.length) });
    else if (role === 'tablist' || child.type === Fragment) collect(props.children, out);
  });
  return out;
}

/** An id made of a value. @param {string} value */
const safe = (value) => value.replace(/[^\w-]/g, '_');

/** @param {TabsProps} props */
export function Tabs({ value, defaultValue, activation, onChange, children, ref, ...rest }) {
  const { tabs, panels } = collect(children);
  const [own, setOwn] = useState(() => defaultValue
    ?? (tabs.find((t) => t.selected) ?? tabs.find((t) => !t.disabled) ?? tabs[0])?.value
    ?? '0');
  const current = value !== undefined ? value : own;
  const mode = /** @type {'automatic' | 'manual'} */ ((/** @type {{ values: readonly string[] }} */ (spec.activation)).values.includes(activation ?? '') ? activation : 'automatic');
  const base = useId();
  const latest = useRef({ current, controlled: value !== undefined, onChange });
  latest.current = { current, controlled: value !== undefined, onChange };
  /** @type {import('react').RefObject<{ value: string | null, from: string | null }>} The last value the user asked for, and the value it was asked from. */
  const asked = useRef({ value: /** @type {string | null} */ (null), from: /** @type {string | null} */ (null) });

  const choose = useCallback((/** @type {string} */ next, /** @type {import('react').SyntheticEvent} */ event) => {
    const now = latest.current;
    // A click on a tab also focuses it: with automatic activation both ask for the same value, and a controlled
    // value has not changed yet when the second one asks. One selection calls onChange once.
    if (next === now.current || (asked.current.value === next && asked.current.from === now.current)) return;
    asked.current = { value: next, from: now.current };
    // The panels are shown before onChange is called, so a listener reads them up to date (G5).
    if (!now.controlled) flushSync(() => setOwn(next));
    now.onChange?.(next, event);
  }, []);

  const tabIds = new Map(tabs.map((t) => [t.value, t.id ?? `${base}tab-${safe(t.value)}`]));
  const panelIds = new Map(panels.map((p) => [p.value, p.id ?? `${base}panel-${safe(p.value)}`]));
  /** @type {TabsState} */
  const state = {
    value: current, activation: mode, choose,
    tabId: (v) => tabIds.get(v) ?? `${base}tab-${safe(v)}`,
    panelId: (v) => panelIds.get(v) ?? `${base}panel-${safe(v)}`,
    // When the walk found none of a kind, an author's component wraps them: every value may name one.
    hasTab: (v) => !tabs.length || tabIds.has(v),
    hasPanel: (v) => !panels.length || panelIds.has(v),
  };

  /** @type {import('react').RefObject<HTMLDivElement | null>} */
  const root = useRef(null);
  const setRef = useCallback((/** @type {HTMLDivElement | null} */ node) => {
    root.current = node;
    if (typeof ref === 'function') ref(node);
    else if (ref) ref.current = node;
  }, [ref]);
  useEffect(() => {
    const id = requestAnimationFrame(() => root.current?.setAttribute('data-ready', ''));
    return () => cancelAnimationFrame(id);
  }, []);

  return createElement('div', /** @type {any} */ ({ ...rest, ref: setRef, 'data-ui': 'tabs' }),
    createElement(TabsContext.Provider, { value: state }, positions(children, 'tabpanel')));
}
