// @ts-check
/**
 * option.js: one option of a listbox, for React (docs/specs/targets.md).
 *
 * The root is a <div role="option">, which has no native selected or disabled state, so both are ARIA
 * (aria-selected, aria-disabled; X2). It never takes focus: its listbox keeps focus and names the highlighted
 * option. It renders `value` as an attribute, since its listbox, and a combobox or a select holding the
 * listbox, read the value from the DOM, as on the Web Component.
 *
 * It renders none of the attributes that its listbox, or a combobox or a select of another family, writes on
 * it: selected, hidden, id (unless the author gives one), data-highlighted and data-focus. So it need not know
 * whether it is held. aria-selected is its own, as on the Web Component: it is rendered once, with the value
 * the option has when it first renders (its listbox's choice, or its own `selected` prop outside a listbox
 * whose options can be read from its children), so that the server markup paints the selection, and it is
 * then kept in step with the `selected` attribute in the DOM, whoever writes it. React never writes it again,
 * since the value it renders never changes. A `selected` prop that changes later is written into the DOM, as a
 * script would set it, and the listbox takes it as its value.
 */
import { createElement, useCallback, useContext, useEffect, useLayoutEffect, useRef, useState } from 'react';
import { ListboxContext, textOf } from '../listbox/listbox.js';
import { role } from '../../components/option/option.props.js';

/**
 * @typedef {Omit<import('react').HTMLAttributes<HTMLDivElement>, 'defaultValue'> & {
 *   value?: string, selected?: boolean, disabled?: boolean,
 *   ref?: import('react').Ref<HTMLDivElement>,
 * }} OptionProps
 */

/** @param {OptionProps} props */
function OptionRoot({ value, selected = false, disabled = false, children, ref, ...rest }) {
  const box = useContext(ListboxContext);
  const own = value ?? textOf(children).trim();
  // The first value only: afterwards the DOM decides, so React never writes aria-selected again.
  const [first] = useState(() => (box?.found ? box.chosen.includes(own) : selected));
  /** @type {import('react').RefObject<HTMLDivElement | null>} */
  const root = useRef(null);
  const setRef = useCallback((/** @type {HTMLDivElement | null} */ node) => {
    root.current = node;
    if (typeof ref === 'function') ref(node);
    else if (ref) ref.current = node;
  }, [ref]);

  // aria-selected follows the selected attribute, whoever writes it.
  useLayoutEffect(() => {
    const el = /** @type {HTMLDivElement} */ (root.current);
    const observer = new MutationObserver(() => {
      const on = String(el.hasAttribute('selected'));
      if (el.getAttribute('aria-selected') !== on) el.setAttribute('aria-selected', on);
    });
    observer.observe(el, { attributes: true, attributeFilter: ['selected'] });
    return () => observer.disconnect();
  }, []);
  // A selected prop that changes after the first render acts as a script that sets the attribute.
  const was = useRef(selected);
  useLayoutEffect(() => {
    if (was.current === selected) return;
    was.current = selected;
    const el = /** @type {HTMLDivElement} */ (root.current);
    if (selected) el.setAttribute('selected', '');
    else el.removeAttribute('selected');
  }, [selected]);
  useEffect(() => {
    const at = requestAnimationFrame(() => root.current?.setAttribute('data-ready', ''));
    return () => cancelAnimationFrame(at);
  }, []);

  return createElement('div', /** @type {any} */ ({
    ...rest, ref: setRef, role, 'data-ui': 'option', value,
    'aria-selected': String(first),
    'aria-disabled': disabled ? 'true' : undefined,
  }), children);
}
// Marked pure, so a bundle that does not use the component drops the module (X6).
export const Option = /* @__PURE__ */ Object.assign(OptionRoot, { kitRole: role, displayName: 'Option' });
