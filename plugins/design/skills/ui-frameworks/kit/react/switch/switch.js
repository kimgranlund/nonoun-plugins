// @ts-check
/**
 * switch.js: the switch for React (docs/specs/targets.md). A plain module that calls createElement; no build step.
 *
 * The root is a <label> that holds a native <input type="checkbox" role="switch"> marked data-part="input", then
 * the author's text. The input takes focus, holds the value and takes part in the form; its role and its checked
 * state are the browser's own, so no aria-checked is written (a native checkbox with the switch role has it
 * already). The label mirrors the state in the attributes the recipe's conditions select on an element that has
 * no native form of them: checked, disabled, required and invalid as author attributes, and data-focus-visible and
 * data-active while focus or a key press is on the input (X2). The track and the thumb are the recipe's ::before
 * and ::after.
 *
 * checked is controlled (checked with onChange) or uncontrolled (defaultChecked), as React's own input is.
 * onChange, onInput and onClick are the input's.
 */
import { flushSync } from 'react-dom';
import { createElement, useCallback, useEffect, useLayoutEffect, useRef, useState } from 'react';
import { press } from '../../behaviours/press.js';
import { props as spec } from '../../components/switch/switch.props.js';

/**
 * @typedef {Omit<import('react').LabelHTMLAttributes<HTMLLabelElement>, 'onChange' | 'onInput' | 'onClick' | 'onInvalid'> & {
 *   checked?: boolean, defaultChecked?: boolean,
 *   required?: boolean, disabled?: boolean, value?: string, name?: string,
 *   onChange?: import('react').ChangeEventHandler<HTMLInputElement>,
 *   onInput?: import('react').FormEventHandler<HTMLInputElement>,
 *   onClick?: import('react').MouseEventHandler<HTMLInputElement>,
 *   onInvalid?: import('react').FormEventHandler<HTMLInputElement>,
 *   ref?: import('react').Ref<HTMLLabelElement>,
 * }} SwitchProps
 */

/** Shown by the browser when a required switch is off. From the manifest's `messages`. */
const VALUE_MISSING = 'Please turn this on';

/** The value submitted while on, when the author gives none: the manifest's default. */
const defaultValue = () => /** @type {{ default?: string }} */ (spec.value).default ?? 'on';

/** An author attribute that holds while `on`: present and empty, or absent. @param {boolean} on */
const flag = (on) => (on ? '' : undefined);

/** @param {SwitchProps} props */
export function Switch({ checked, defaultChecked = false, required = false, disabled = false, value, name, onChange, onInput, onClick, onInvalid, children, ref, ...rest }) {
  /** @type {import('react').RefObject<HTMLLabelElement | null>} */
  const root = useRef(null);
  /** @type {import('react').RefObject<HTMLInputElement | null>} */
  const input = useRef(null);
  const setRef = useCallback((/** @type {HTMLLabelElement | null} */ node) => {
    root.current = node;
    if (typeof ref === 'function') ref(node);
    else if (ref) ref.current = node;
  }, [ref]);

  const [ownChecked, setOwnChecked] = useState(defaultChecked);
  /** The user is due to be told that the value is invalid (F5): after a change or a submit attempt, until a reset. */
  const [told, setTold] = useState(false);
  const on = checked !== undefined ? checked : ownChecked;
  const invalid = told && required && !on;

  // The message of a required switch that is off is the manifest's, not the browser's.
  useLayoutEffect(() => {
    const el = /** @type {HTMLInputElement} */ (input.current);
    el.setCustomValidity(required && !on ? VALUE_MISSING : '');
  });

  useLayoutEffect(() => {
    const el = /** @type {HTMLInputElement} */ (input.current), label = /** @type {HTMLLabelElement} */ (root.current);
    const stop = press(el, { disabled: () => el.matches(':disabled') });
    // Focus and a key press happen on the input, a part: the root carries their state (X2).
    const mirror = (/** @type {string} */ attr, /** @type {boolean} */ yes) => { if (label.hasAttribute(attr) !== yes) label.toggleAttribute(attr, yes); };
    const pressed = new MutationObserver(() => mirror('data-active', el.hasAttribute('data-active')));
    pressed.observe(el, { attributes: true, attributeFilter: ['data-active'] });
    const off = new AbortController();
    el.addEventListener('focus', () => mirror('data-focus-visible', el.matches(':focus-visible')), { signal: off.signal });
    el.addEventListener('blur', () => mirror('data-focus-visible', false), { signal: off.signal });
    // A form reset puts the input back to its default by itself; the state that mirrors it follows (F6).
    el.form?.addEventListener('reset', () => setTimeout(() => { setOwnChecked(el.checked); setTold(false); }), { signal: off.signal });
    return () => { stop(); pressed.disconnect(); off.abort(); mirror('data-active', false); mirror('data-focus-visible', false); };
  }, []);

  useEffect(() => {
    const id = requestAnimationFrame(() => root.current?.setAttribute('data-ready', ''));
    return () => cancelAnimationFrame(id);
  }, []);

  /** @param {import('react').ChangeEvent<HTMLInputElement>} event */
  const change = (event) => {
    const next = event.target.checked;
    // The label shows the new state before onChange is called, so a listener reads it up to date.
    if (checked === undefined) flushSync(() => { setOwnChecked(next); setTold(true); });
    else setTold(true);
    onChange?.(event);
  };
  /** @param {import('react').FormEvent<HTMLInputElement>} event */
  const invalidEvent = (event) => { setTold(true); onInvalid?.(event); };

  const field = createElement('input', /** @type {any} */ ({
    type: 'checkbox', role: 'switch', 'data-part': 'input', ref: input, name, value: value ?? defaultValue(), disabled, required,
    'aria-invalid': invalid ? 'true' : undefined,
    ...(checked !== undefined ? { checked } : { defaultChecked }),
    onChange: change, onInput, onClick, onInvalid: invalidEvent,
  }));
  return createElement('label', /** @type {any} */ ({
    ...rest, ref: setRef, 'data-ui': 'switch',
    checked: flag(on), invalid: flag(invalid), required, disabled,
  }), field, children);
}
