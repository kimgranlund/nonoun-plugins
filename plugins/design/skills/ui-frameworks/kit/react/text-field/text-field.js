// @ts-check
/**
 * text-field.js: the text field for React (docs/specs/targets.md). A plain module that calls createElement; no build step.
 *
 * The root is a <span>, a plain element and not a form control (D14): the author's native input, the child marked
 * data-part="input", carries the name, the value, the type and every constraint, and takes part in the form by itself.
 * The component finds it in the DOM and never renders, clones, moves or wraps it. As the Web Component does, it
 * disables the input while the field is disabled (and never enables one the author disabled), focuses the input on
 * a press anywhere else in the field, writes aria-invalid on the input once the user is due to be told (F5: after
 * the input's first `change` or `invalid` event, until a form reset), and mirrors `invalid` and `readonly` onto the
 * root for the recipe (J47 to J49). Those writes are made in the DOM at the event, so a listener sees them in the
 * same task; none of them is rendered, so the server markup carries `disabled` and the input's own readonly, which
 * the recipe's conditions already select (J77, U2).
 *
 * `disabled` is the one prop of the manifest; every other prop goes to the root.
 */
import { createElement, useCallback, useEffect, useLayoutEffect, useRef } from 'react';

/**
 * @typedef {import('react').HTMLAttributes<HTMLSpanElement> & {
 *   disabled?: boolean,
 *   ref?: import('react').Ref<HTMLSpanElement>,
 * }} TextFieldProps
 */

/** What a press on one of them is for: the field leaves it alone. */
const INTERACTIVE = 'a[href], button, input, select, textarea, [tabindex], [contenteditable]';

/**
 * Sets or removes an attribute, only when it differs. An observer then sees nothing when nothing changes.
 * @param {Element} el @param {string} name @param {string | null} value
 */
const put = (el, name, value) => {
  if (el.getAttribute(name) === value) return;
  if (value === null) el.removeAttribute(name);
  else el.setAttribute(name, value);
};

/** @param {TextFieldProps} props */
export function TextField({ disabled = false, onMouseDown, children, ref, ...rest }) {
  /** @type {import('react').RefObject<HTMLSpanElement | null>} */
  const root = useRef(null);
  const setRef = useCallback((/** @type {HTMLSpanElement | null} */ node) => {
    root.current = node;
    if (typeof ref === 'function') ref(node);
    else if (ref) ref.current = node;
  }, [ref]);
  const latest = useRef(disabled);
  latest.current = disabled;
  /** @type {import('react').RefObject<(() => void) | null>} */
  const sync = useRef(null);

  useLayoutEffect(() => {
    const el = /** @type {HTMLSpanElement} */ (root.current);
    /** The inputs whose user is due to be told (F5). One per input, so a replaced input starts untold. */
    const told = new WeakSet();
    /** The inputs this field disabled, so that it never enables one the author disabled. */
    const disabledHere = new WeakSet();
    /** The author's input, looked up each time (P6). @returns {HTMLInputElement | null} */
    const input = () => el.querySelector(':scope > input[data-part="input"]');

    const update = () => {
      const field = input();
      if (field) {
        if (latest.current && !field.disabled) { field.disabled = true; disabledHere.add(field); }
        else if (!latest.current && disabledHere.has(field)) { field.disabled = false; disabledHere.delete(field); }
      }
      const invalid = !!field && told.has(field) && !field.validity.valid;
      if (field) put(field, 'aria-invalid', invalid ? 'true' : null);
      put(el, 'invalid', invalid ? '' : null);
      put(el, 'readonly', field?.readOnly ? '' : null);
    };
    sync.current = update;

    const off = new AbortController();
    const listen = { signal: off.signal };
    /** @param {Event} event */
    const tell = (event) => {
      const field = input();
      if (!field || event.target !== field) return;
      told.add(field);
      update();
    };
    // The user is due to be told once they have changed the value and left it, or tried to submit (F5).
    el.addEventListener('change', tell, listen);
    // invalid does not bubble.
    el.addEventListener('invalid', tell, { capture: true, signal: off.signal });
    // Once told, the state follows every keystroke, so a correction clears it at once.
    el.addEventListener('input', update, listen);
    // A form reset clears the mark (F6). The reset event comes before the values go back; the mark alone decides.
    el.ownerDocument.addEventListener('reset', (event) => {
      const field = input();
      if (!field || event.target !== field.form) return;
      told.delete(field);
      update();
    }, { capture: true, signal: off.signal });

    // The observer sees an input that arrives, is replaced, or changes its constraints.
    const observer = new MutationObserver(update);
    observer.observe(el, {
      childList: true, subtree: true, attributes: true,
      attributeFilter: ['data-part', 'readonly', 'disabled', 'required', 'pattern', 'min', 'max', 'step', 'minlength', 'maxlength', 'type'],
    });
    update();
    return () => { off.abort(); observer.disconnect(); sync.current = null; };
  }, []);
  // The prop and the author's own markup can change at any render: bring the input and the mirrors in step.
  useLayoutEffect(() => { sync.current?.(); });
  useEffect(() => {
    const id = requestAnimationFrame(() => root.current?.setAttribute('data-ready', ''));
    return () => cancelAnimationFrame(id);
  }, []);

  /** A press anywhere in the field focuses the input, except on something interactive of its own, the input included (focus() on a disabled input does nothing). @param {import('react').MouseEvent<HTMLSpanElement>} event */
  const press = (event) => {
    onMouseDown?.(event);
    if (event.defaultPrevented) return;
    const el = event.currentTarget;
    const input = /** @type {HTMLInputElement | null} */ (el.querySelector(':scope > input[data-part="input"]'));
    const target = event.target instanceof Element ? event.target : null;
    if (!input || !target) return;
    const own = target.closest(INTERACTIVE);
    if (own && own !== el && el.contains(own)) return;
    event.preventDefault();
    input.focus();
  };

  return createElement('span', /** @type {any} */ ({ ...rest, ref: setRef, 'data-ui': 'text-field', disabled: disabled ? true : undefined, onMouseDown: press }), children);
}
