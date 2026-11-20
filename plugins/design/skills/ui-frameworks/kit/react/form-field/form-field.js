// @ts-check
/**
 * form-field.js: the form field for React (docs/specs/targets.md). A plain module that calls createElement; no build step.
 *
 * The root is a <div> that wires a control to the label, the help and the error the author wrote around it, the
 * children marked data-part="label", "help" and "error". It names no component. As the Web Component does, it
 * finds the control by what it is (J50): the first native input, select or textarea inside, or the first element
 * with one of the roles a form control has, and not one of a form field nested in it. So it works with the kit's
 * text field (whose control is its native input), the checkbox (the same), a radio group or a plain input, and with
 * a control that arrives or is replaced later. It points the label at the control with `for`, describes the control
 * by the help and, while it shows, the error, with aria-describedby, gives an id only where there is none (taken
 * from useId), and never replaces an attribute the author wrote (A2). It mirrors the control's invalid, required and
 * disabled onto its root for the recipe, which shows the error from `invalid` alone (J51). A click on the label
 * focuses the control, or its Tab stop (J51).
 *
 * All of it is written in the DOM after the markup is in the page, none of it rendered: the control and the parts
 * are the author's, so the server markup carries none of the wiring until hydration.
 */
import { createElement, useCallback, useEffect, useId, useLayoutEffect, useRef } from 'react';

/**
 * @typedef {import('react').HTMLAttributes<HTMLDivElement> & {
 *   ref?: import('react').Ref<HTMLDivElement>,
 * }} FormFieldProps
 */

// The control, written out as the Web Component does (R1).
const CONTROL = 'input:not([type="hidden"]), select, textarea, [role="checkbox"], [role="switch"], [role="radiogroup"], [role="listbox"], [role="combobox"], [role="slider"], [role="spinbutton"]';
// The conditions of references/states.json, copied unchanged.
const INVALID = ':is([aria-invalid]:not([aria-invalid="false"]), :is(input, select, textarea):user-invalid, [invalid])';
const REQUIRED = ':is([required], [aria-required="true"])';
const DISABLED = ':is(:disabled, [disabled], [aria-disabled="true"])';

/**
 * Sets or removes an attribute, only when it differs. An observer then sees nothing when nothing changes.
 * @param {Element} el @param {string} name @param {string | null} value
 */
const put = (el, name, value) => {
  if (el.getAttribute(name) === value) return;
  if (value === null) el.removeAttribute(name);
  else el.setAttribute(name, value);
};

/** @param {FormFieldProps} props */
export function FormField({ children, ref, ...rest }) {
  const uid = useId();
  /** @type {import('react').RefObject<HTMLDivElement | null>} */
  const root = useRef(null);
  const setRef = useCallback((/** @type {HTMLDivElement | null} */ node) => {
    root.current = node;
    if (typeof ref === 'function') ref(node);
    else if (ref) ref.current = node;
  }, [ref]);
  /** @type {import('react').RefObject<(() => void) | null>} */
  const sync = useRef(null);

  useLayoutEffect(() => {
    const el = /** @type {HTMLDivElement} */ (root.current);
    /** The for values written on a label, the aria-describedby and aria-labelledby values written on a control: never replace an author's (A2). */
    const pointed = new WeakMap(), described = new WeakMap(), named = new WeakMap();
    /** A direct child of the field marked as the part. @param {string} name @returns {HTMLElement | null} */
    const part = (name) => /** @type {HTMLElement | null} */ ([...el.children].find((child) => child.getAttribute('data-part') === name) ?? null);
    /** The control: the first that belongs to this field, and not to a form field nested in it. @returns {HTMLElement | null} */
    const control = () => /** @type {HTMLElement | undefined} */ ([...el.querySelectorAll(CONTROL)].find((c) => c.closest('[data-ui="form-field"]') === el)) ?? null;
    /** An id the element has, or the one it is given. @param {Element} target @param {string} kind */
    const id = (target, kind) => {
      if (!target.id) target.id = `${uid}-${kind}`;
      return target.id;
    };
    /**
     * Writes an attribute this component owns on another element, unless the author wrote one there.
     * @param {Element} target @param {string} name @param {string | null} value @param {WeakMap<Element, string>} mine
     */
    const own = (target, name, value, mine) => {
      const now = target.getAttribute(name);
      if (now !== null && now !== mine.get(target)) return;
      put(target, name, value);
      if (value === null) mine.delete(target);
      else mine.set(target, value);
    };

    const update = () => {
      const c = control();
      const label = part('label'), help = part('help'), error = part('error');
      const invalid = !!c && c.matches(INVALID);
      put(el, 'invalid', invalid ? '' : null);
      put(el, 'required', c?.matches(REQUIRED) ? '' : null);
      put(el, 'disabled', c?.matches(DISABLED) ? '' : null);
      if (!c) return;
      const cid = id(c, 'control');
      if (label) {
        own(label, 'for', cid, pointed);
        // A label names only a labelable element. A control it cannot name, such as a plain element with a role,
        // is named by the label's id instead, unless the author named it.
        const labelled = /** @type {HTMLLabelElement} */ (label).control === c;
        if (!c.hasAttribute('aria-label')) own(c, 'aria-labelledby', labelled ? null : id(label, 'label'), named);
      }
      const ids = [help ? id(help, 'help') : null, error && invalid ? id(error, 'error') : null].filter(Boolean).join(' ');
      own(c, 'aria-describedby', ids || null, described);
    };
    sync.current = update;

    const off = new AbortController();
    const listen = { signal: off.signal };
    // The states the control's own events change. The control's component writes its own marks in the same event
    // (a text field's listener is nearer the input than this one) or, for a rendered one, when React commits, which
    // the observer below sees.
    for (const type of ['input', 'change', 'focusout']) el.addEventListener(type, update, listen);
    el.addEventListener('invalid', update, { capture: true, signal: off.signal });
    // A form reset clears the browser's own mark of a native control after the reset event: look a task later.
    el.ownerDocument.addEventListener('reset', (event) => {
      if (event.target instanceof Node && event.target.contains(el)) setTimeout(() => { if (el.isConnected && !off.signal.aborted) update(); });
    }, { capture: true, signal: off.signal });
    // A click on the label focuses or activates the control (J51). The browser does it for a labelable control
    // that takes focus; for any other control the field moves focus to the control's Tab stop.
    el.addEventListener('click', (event) => {
      const label = part('label'), c = control();
      if (!label || !c || !(event.target instanceof Node) || !label.contains(event.target)) return;
      if (c.matches(DISABLED)) return;
      const stop = c.tabIndex >= 0 ? c : /** @type {HTMLElement | null} */ (c.querySelector('[tabindex="0"]'));
      stop?.focus();
    }, listen);

    const observer = new MutationObserver(update);
    observer.observe(el, {
      childList: true, subtree: true, attributes: true,
      attributeFilter: ['role', 'id', 'type', 'data-part', 'for', 'tabindex', 'aria-invalid', 'invalid', 'required', 'aria-required', 'disabled', 'aria-disabled', 'aria-describedby', 'aria-labelledby', 'aria-label'],
    });
    update();
    return () => { off.abort(); observer.disconnect(); sync.current = null; };
  }, [uid]);
  // The author's markup can change at any render: look again once it has.
  useLayoutEffect(() => { sync.current?.(); });
  useEffect(() => {
    const id = requestAnimationFrame(() => root.current?.setAttribute('data-ready', ''));
    return () => cancelAnimationFrame(id);
  }, []);

  return createElement('div', /** @type {any} */ ({ ...rest, ref: setRef, 'data-ui': 'form-field' }), children);
}
