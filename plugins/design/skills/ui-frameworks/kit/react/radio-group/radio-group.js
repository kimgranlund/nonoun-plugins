// @ts-check
/**
 * radio-group.js: the radio group for React (docs/specs/targets.md). It is the form control of the family and
 * coordinates its radios through React context, which this module exports for them.
 *
 * The root is a <div role="radiogroup">. Its radios are labels around native radio inputs, and the group gives
 * them all one `name`, so the browser's own grouping, its radio keys and its form value do the work. With no
 * `name` it makes one up for the grouping and writes form="" on the inputs, so that nothing is submitted under it.
 * The group still mounts roving focus, as the Web Component does: it makes the group one stop in the Tab order
 * (the first radio when none is checked, in both directions), moves focus with the arrows of both orientations,
 * wraps, skips what is disabled, and adds Home and End. Roving focus prevents the arrows' default action, which
 * is the browser's own move-and-check, so the group checks the radio that then has focus by clicking it: that is
 * the one reading it takes of the two (docs/reports/react.radio-group.md).
 *
 * States on the root, in the ARIA the radiogroup role allows (X2): aria-required, aria-invalid once the user is
 * due to be told (F5), aria-disabled, aria-orientation="horizontal"; the variant is data-variant.
 *
 * value is controlled (value with onChange) or uncontrolled (defaultValue). With neither, it is the value of the
 * first radio marked `checked` among the radios it is given when it first renders (J4). A radio without a value has
 * its position among the radios as its value, counted among the children of the group and of fragments in it.
 * onChange(value, event) and onInput(value, event) are called when the user chooses another radio, after the radios
 * are up to date when the value is uncontrolled (J6); neither is called when the value prop changes.
 */
import { Children, Fragment, cloneElement, createContext, createElement, isValidElement, useCallback, useEffect, useId, useLayoutEffect, useRef, useState } from 'react';
import { flushSync } from 'react-dom';
import { rovingFocus } from '../../behaviours/roving-focus.js';
import { props as spec, role } from '../../components/radio-group/radio-group.props.js';

/**
 * @typedef {{
 *   name: string, anonymous: boolean, value: string, disabled: boolean, required: boolean,
 *   choose: (value: string, event: import('react').ChangeEvent<HTMLInputElement>) => void,
 *   input: (value: string, event: import('react').FormEvent<HTMLInputElement>) => void,
 *   invalid: (event: import('react').FormEvent<HTMLInputElement>) => void,
 * }} RadioGroupState
 * @typedef {Omit<import('react').HTMLAttributes<HTMLDivElement>, 'onChange' | 'onInput' | 'defaultValue'> & {
 *   value?: string, defaultValue?: string, name?: string, required?: boolean, disabled?: boolean,
 *   orientation?: 'vertical' | 'horizontal', variant?: 'plain' | 'segmented',
 *   onChange?: (value: string, event: import('react').ChangeEvent<HTMLInputElement>) => void,
 *   onInput?: (value: string, event: import('react').FormEvent<HTMLInputElement>) => void,
 *   ref?: import('react').Ref<HTMLDivElement>,
 * }} RadioGroupProps
 */

/** What the radios of the nearest radio group read. @type {import('react').Context<RadioGroupState | null>} */
export const RadioGroupContext = /* @__PURE__ */ createContext(/** @type {RadioGroupState | null} */ (null));
/** A radio's position among the radios. @type {import('react').Context<{ kind: string, index: number } | null>} */
export const PositionContext = /* @__PURE__ */ createContext(/** @type {{ kind: string, index: number } | null} */ (null));

/** Shown by the browser when a required group has no choice. From the manifest's `messages`. */
const VALUE_MISSING = 'Please choose one';
const ARROWS = ['ArrowDown', 'ArrowRight', 'ArrowUp', 'ArrowLeft'];
const INPUT = 'input[data-part="input"][type="radio"]';

/** The role a component of this family renders, so that the walk below knows it without importing it. @param {unknown} node */
const roleOf = (node) => (isValidElement(node) && typeof node.type === 'function' ? /** @type {any} */ (node.type).kitRole : undefined);

/**
 * Gives every radio among the children its position, through fragments, leaving the rest alone.
 * @param {import('react').ReactNode} children @param {{ n: number }} [count]
 * @returns {import('react').ReactNode}
 */
function positions(children, count = { n: 0 }) {
  return Children.map(children, (child) => {
    if (!isValidElement(child)) return child;
    if (child.type === Fragment) return cloneElement(child, undefined, positions(/** @type {any} */ (child.props).children, count));
    if (roleOf(child) !== 'radio') return child;
    return createElement(PositionContext.Provider, { value: { kind: 'radio', index: count.n++ } }, child);
  });
}

/** The props of the radios among the children, in order, each with the value it will have. @param {import('react').ReactNode} children @param {any[]} [out] */
function collect(children, out = []) {
  Children.forEach(children, (child) => {
    if (!isValidElement(child)) return;
    const props = /** @type {any} */ (child.props);
    if (roleOf(child) === 'radio') out.push({ ...props, value: props.value ?? String(out.length) });
    else if (child.type === Fragment) collect(props.children, out);
  });
  return out;
}

/** @param {RadioGroupProps} props */
export function RadioGroup({ value, defaultValue, name, required = false, disabled = false, orientation, variant, onChange, onInput, onKeyDown, children, ref, ...rest }) {
  const radios = collect(children);
  const pick = (/** @type {'orientation' | 'variant'} */ key, /** @type {unknown} */ given) => {
    const p = /** @type {{ values: readonly string[], default: string }} */ (spec[key]);
    return typeof given === 'string' && p.values.includes(given) ? given : p.default;
  };
  const horizontal = pick('orientation', orientation) === 'horizontal';
  const generated = useId();
  const [own, setOwn] = useState(() => defaultValue ?? radios.find((r) => r.checked)?.value ?? '');
  const initial = useRef(own);
  const [told, setTold] = useState(false);
  const [, bump] = useState(0);
  const current = value !== undefined ? value : own;
  const named = radios.length ? radios.some((r) => r.value === current) : current !== '';
  const invalid = told && required && !named;

  /** @type {import('react').RefObject<HTMLDivElement | null>} */
  const root = useRef(null);
  const setRef = useCallback((/** @type {HTMLDivElement | null} */ node) => {
    root.current = node;
    if (typeof ref === 'function') ref(node);
    else if (ref) ref.current = node;
  }, [ref]);
  const latest = useRef({ current, controlled: value !== undefined, onChange, onInput });
  latest.current = { current, controlled: value !== undefined, onChange, onInput };

  /** The inputs of this group's own radios, and not of a group nested in one. @returns {HTMLInputElement[]} */
  const inputs = () => /** @type {HTMLInputElement[]} */ ([...(root.current?.querySelectorAll(INPUT) ?? [])].filter((el) => el.closest('[data-ui="radio-group"]') === root.current));

  const choose = useCallback((/** @type {string} */ next, /** @type {import('react').ChangeEvent<HTMLInputElement>} */ event) => {
    const now = latest.current;
    if (next === now.current) return;
    setTold(true);
    // The radios are written before onChange is called, so a listener reads them up to date (J6).
    if (!now.controlled) flushSync(() => setOwn(next));
    now.onChange?.(next, event);
  }, []);
  const inputEvent = useCallback((/** @type {string} */ next, /** @type {import('react').FormEvent<HTMLInputElement>} */ event) => latest.current.onInput?.(next, event), []);
  const invalidEvent = useCallback(() => setTold(true), []);

  // The browser's own message is replaced by the manifest's while a required group has no choice.
  useLayoutEffect(() => { for (const el of inputs()) el.setCustomValidity(required && !named ? VALUE_MISSING : ''); });

  useLayoutEffect(() => {
    const el = /** @type {HTMLDivElement} */ (root.current);
    const stop = rovingFocus(el, {
      items: inputs,
      orientation: () => 'both',
      current: () => inputs().find((input) => input.checked),
      skip: (item) => item.matches(':disabled'),
      watch: ['checked'],
    });
    // A form reset puts the inputs back to their defaults; the value follows, and one more render writes them (F6).
    const off = new AbortController();
    el.closest('form')?.addEventListener('reset', () => setTimeout(() => {
      if (!latest.current.controlled) setOwn(initial.current);
      setTold(false);
      bump((n) => n + 1);
    }), { signal: off.signal });
    return () => { stop(); off.abort(); };
  }, []);
  useEffect(() => {
    const id = requestAnimationFrame(() => root.current?.setAttribute('data-ready', ''));
    return () => cancelAnimationFrame(id);
  }, []);

  /** @type {RadioGroupState} */
  const state = {
    name: name ?? generated, anonymous: name === undefined, value: current, disabled, required,
    choose, input: inputEvent, invalid: invalidEvent,
  };

  return createElement('div', /** @type {any} */ ({
    ...rest, ref: setRef, role, 'data-ui': 'radio-group', 'data-variant': pick('variant', variant),
    'aria-orientation': horizontal ? 'horizontal' : undefined,
    'aria-required': required ? 'true' : undefined,
    'aria-disabled': disabled ? 'true' : undefined,
    'aria-invalid': invalid ? 'true' : undefined,
    onKeyDown: (/** @type {import('react').KeyboardEvent<HTMLDivElement>} */ event) => {
      onKeyDown?.(event);
      // Roving focus has moved focus to the next radio and prevented the browser's own move, which would have
      // checked it: the radio that has focus now is chosen (J5).
      if (!ARROWS.includes(event.key) || !event.nativeEvent.defaultPrevented) return;
      const active = document.activeElement;
      if (active !== event.target && active instanceof HTMLInputElement && inputs().includes(active)) active.click();
    },
  }), createElement(RadioGroupContext.Provider, { value: state }, positions(children)));
}
