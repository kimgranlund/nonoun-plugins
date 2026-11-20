// @ts-check
/**
 * radio.js: one radio for React (docs/specs/targets.md).
 *
 * The root is a <label> that holds a native <input type="radio"> marked data-part="input", then the author's text,
 * as the checkbox is. The input takes focus and carries the group's name and its own value; the radio group
 * decides which one is checked. The label mirrors the state in the attributes the recipe's conditions select:
 * checked and its own disabled as author attributes (a disabled group disables the inputs and paints its radios as
 * the Web Component's group does, which is as enabled ones), and data-focus-visible and data-active while focus or a key press is
 * on the input (X2). In a segmented group the recipe draws the label alone, as the segment.
 *
 * A radio with no value has its position among the group's radios as its value. `checked` marks the radio the
 * group starts with, when the group has no value of its own (J4). Outside a radio group a radio holds its own
 * state: checked or defaultChecked, with onChange of the label's subtree. onClick is the input's.
 */
import { createElement, useCallback, useContext, useEffect, useLayoutEffect, useRef, useState } from 'react';
import { press } from '../../behaviours/press.js';
import { RadioGroupContext, PositionContext } from '../radio-group/radio-group.js';
import { role } from '../../components/radio/radio.props.js';

/**
 * @typedef {Omit<import('react').LabelHTMLAttributes<HTMLLabelElement>, 'onClick' | 'defaultChecked'> & {
 *   value?: string, checked?: boolean, defaultChecked?: boolean, disabled?: boolean,
 *   onClick?: import('react').MouseEventHandler<HTMLInputElement>,
 *   ref?: import('react').Ref<HTMLLabelElement>,
 * }} RadioProps
 */

/** An author attribute that holds while `on`: present and empty, or absent. @param {boolean} on */
const flag = (on) => (on ? '' : undefined);

/** @param {RadioProps} props */
function RadioRoot({ value, checked, defaultChecked = false, disabled = false, onClick, children, ref, ...rest }) {
  const group = useContext(RadioGroupContext);
  const position = useContext(PositionContext);
  const own = value ?? (position?.kind === 'radio' ? String(position.index) : '');
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
  const on = group ? group.value !== '' && group.value === own : checked !== undefined ? checked : ownChecked;
  const off = disabled || (group?.disabled ?? false);

  useLayoutEffect(() => {
    const el = /** @type {HTMLInputElement} */ (input.current), label = /** @type {HTMLLabelElement} */ (root.current);
    const stop = press(el, { disabled: () => el.matches(':disabled') });
    // Focus and a key press happen on the input, a part: the root carries their state (X2).
    const mirror = (/** @type {string} */ attr, /** @type {boolean} */ yes) => { if (label.hasAttribute(attr) !== yes) label.toggleAttribute(attr, yes); };
    const pressed = new MutationObserver(() => mirror('data-active', el.hasAttribute('data-active')));
    pressed.observe(el, { attributes: true, attributeFilter: ['data-active'] });
    const abort = new AbortController();
    el.addEventListener('focus', () => mirror('data-focus-visible', el.matches(':focus-visible')), { signal: abort.signal });
    el.addEventListener('blur', () => mirror('data-focus-visible', false), { signal: abort.signal });
    return () => { stop(); pressed.disconnect(); abort.abort(); mirror('data-active', false); mirror('data-focus-visible', false); };
  }, []);
  useEffect(() => {
    const id = requestAnimationFrame(() => root.current?.setAttribute('data-ready', ''));
    return () => cancelAnimationFrame(id);
  }, []);

  const field = createElement('input', /** @type {any} */ ({
    type: 'radio', 'data-part': 'input', ref: input, value: own, disabled: off, checked: on,
    name: group?.name, form: group?.anonymous ? '' : undefined, required: group?.required,
    onChange: (/** @type {import('react').ChangeEvent<HTMLInputElement>} */ event) => {
      if (group) group.choose(own, event);
      else setOwnChecked(event.target.checked);
    },
    onInput: (/** @type {import('react').FormEvent<HTMLInputElement>} */ event) => group?.input(own, event),
    onInvalid: (/** @type {import('react').FormEvent<HTMLInputElement>} */ event) => group?.invalid(event),
    onClick,
  }));
  return createElement('label', /** @type {any} */ ({ ...rest, ref: setRef, 'data-ui': 'radio', checked: flag(on), disabled }), field, children);
}
// Marked pure, so a bundle that does not use the component drops the module (X6).
export const Radio = /* @__PURE__ */ Object.assign(RadioRoot, { kitRole: role, displayName: 'Radio' });
