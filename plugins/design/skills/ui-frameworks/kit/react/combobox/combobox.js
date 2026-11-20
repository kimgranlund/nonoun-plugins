// @ts-check
/**
 * combobox.js: a text field with a list of suggestions that narrows as the user types, for React
 * (docs/specs/targets.md).
 *
 * The root is a <div>, with no role: it is the field, around the author's input (the child marked
 * data-part="input") and the author's popup (the child marked data-part="popup"), which holds the kit's listbox.
 * Focus stays in the input, which carries the combobox role and the form value under its own name (J43). The
 * list follows the APG's list autocomplete with manual selection: typing filters the options and opens the list,
 * the arrows move a highlight, and only Enter or a click takes an option (J44). While the input carries readonly
 * the list stays closed and the value is left alone (J80).
 *
 * The input and the popup are the author's elements, and the listbox and the options are of another family, so
 * the combobox finds them in the DOM, by data-part and by role, as the Web Component does, and writes what its
 * manifest says it writes, only where it differs, after each render and whenever its subtree changes: on the
 * input its role and ARIA, on the popup popover="manual" when it has none, on the listbox an id and
 * tabindex="-1", and on the options hidden, selected and data-focus; activeDescendant writes data-highlighted,
 * the options' ids and the input's aria-activedescendant. The listbox's own logic still runs, as on the Web
 * Component: a click on an option highlights and selects it there first.
 *
 * `open` is the author attribute on the root (X2), which the recipe shows the popup on; the popup is shown in
 * the top layer in the same task. It is controlled (open) or uncontrolled (defaultOpen). A controlled combobox
 * shows or hides its popup itself when the user asks, and the platform's toggle event on the popup tells the
 * owner, as on the menu. onChange(value, event) is called once the user takes an option, after the input, the
 * options and the list are written. The input's own events are the author's.
 */
import { Children, Fragment, createElement, isValidElement, useCallback, useEffect, useId, useLayoutEffect, useRef, useState } from 'react';
import { flushSync } from 'react-dom';
import { activeDescendant } from '../../behaviours/active-descendant.js';
import { dismiss } from '../../behaviours/dismiss.js';

/**
 * @typedef {Omit<import('react').HTMLAttributes<HTMLDivElement>, 'onChange'> & {
 *   open?: boolean, defaultOpen?: boolean,
 *   onChange?: (value: string, event: import('react').SyntheticEvent | Event) => void,
 *   ref?: import('react').Ref<HTMLDivElement>,
 * }} ComboboxProps
 */

const LISTBOX = '[role="listbox"]';
const OPTION = '[role="option"]';
const MARK = 'data-highlighted';

/** @param {Element} el */
const disabled = (el) => el.hasAttribute('disabled') || el.getAttribute('aria-disabled') === 'true';
/** An option's text, as the input shows it once taken. @param {Element} el */
const textOf = (el) => (el.textContent ?? '').trim();
/** Sets or removes an attribute, only when it differs. @param {Element} el @param {string} name @param {string | null} value */
const put = (el, name, value) => {
  if (el.getAttribute(name) === value) return;
  if (value === null) el.removeAttribute(name);
  else el.setAttribute(name, value);
};
/**
 * The props of the author's input among the children, through fragments, when it is written there; null when
 * a component of the author's renders it, and only the DOM can tell.
 * @param {import('react').ReactNode} children @returns {any}
 */
function inputProps(children) {
  let found = /** @type {any} */ (null);
  Children.forEach(children, (child) => {
    if (found || !isValidElement(child)) return;
    const props = /** @type {any} */ (child.props);
    if (child.type === 'input' && props['data-part'] === 'input') found = props;
    else if (child.type === Fragment) found = inputProps(props.children);
  });
  return found;
}

/** @param {ComboboxProps} props */
export function Combobox({ open, defaultOpen = false, onChange, onInput, onClick, onMouseDown, onKeyDownCapture, onFocus, onBlur, children, ref, ...rest }) {
  const [own, setOwn] = useState(defaultOpen);
  const written = inputProps(children);
  // A read-only or disabled input among the children opens no list, whoever asks (J80).
  const isOpen = (open !== undefined ? open : own) && !written?.readOnly && !written?.disabled;
  const base = useId();
  /** @type {import('react').RefObject<HTMLDivElement | null>} */
  const root = useRef(null);
  const setRef = useCallback((/** @type {HTMLDivElement | null} */ node) => {
    // Kept after unmount, so that a listener or an observer that outlived it would still act, and be seen (X4).
    if (node) root.current = node;
    if (typeof ref === 'function') ref(node);
    else if (ref) ref.current = node;
  }, [ref]);
  const latest = useRef({ isOpen, controlled: open !== undefined, written: !!written, onChange });
  latest.current = { isOpen, controlled: open !== undefined, written: !!written, onChange };
  /** Whether the key going down is Home or End, which stay with the input's text even while the list is open. */
  const textKey = useRef(false);

  const input = useCallback(() => /** @type {HTMLInputElement | null} */ (root.current?.querySelector(':scope > input[data-part="input"]') ?? null), []);
  const readOnly = useCallback(() => !!input()?.hasAttribute('readonly'), [input]);
  const popup = useCallback(() => /** @type {HTMLElement | null} */ (root.current?.querySelector(':scope > [data-part="popup"]') ?? null), []);
  const listbox = useCallback(() => /** @type {HTMLElement | null} */ (popup()?.querySelector(LISTBOX) ?? null), [popup]);
  /** The options of the listbox, and not of a listbox nested in one. */
  const options = useCallback(() => {
    const list = listbox();
    return list ? /** @type {HTMLElement[]} */ ([...list.querySelectorAll(OPTION)].filter((el) => el.closest(LISTBOX) === list)) : [];
  }, [listbox]);
  const shown = useCallback(() => options().filter((el) => !el.hasAttribute('hidden')), [options]);

  /**
   * Asks for the list to open or close. Uncontrolled, the state changes in the same task; controlled, the popup
   * is shown or hidden and its toggle event tells the owner. @param {boolean} next
   */
  const request = useCallback((/** @type {boolean} */ next) => {
    const { isOpen: now, controlled } = latest.current;
    if (next && readOnly()) return;
    if (!controlled) { if (next !== now) { latest.current.isOpen = next; flushSync(() => setOwn(next)); } return; }
    const el = popup();
    if (!el) return;
    if (!el.hasAttribute('popover')) el.setAttribute('popover', 'manual');
    if (next && !el.matches(':popover-open')) el.showPopover();
    else if (!next && el.matches(':popover-open')) el.hidePopover();
  }, [popup, readOnly]);

  /** Shows the options whose text contains `text`, whatever its case, and hides the others, with the highlight cleared. @param {string} text */
  const filter = useCallback((/** @type {string} */ text) => {
    const query = text.toLowerCase();
    const all = options();
    for (const option of all) put(option, MARK, null);
    for (const option of all) put(option, 'hidden', textOf(option).toLowerCase().includes(query) ? null : '');
    return shown().length;
  }, [options, shown]);

  /** Brings the input's ARIA, the listbox's passivity and the painted highlight in step. Writes nothing when they already are. */
  const sync = useCallback(() => {
    const field = input(), box = popup(), list = listbox(), el = root.current;
    const now = latest.current.isOpen;
    if (box && !box.hasAttribute('popover')) box.setAttribute('popover', 'manual');
    if (list) {
      if (!list.id) list.id = `${base}listbox`;
      put(list, 'tabindex', '-1');
    }
    if (field) {
      put(field, 'role', 'combobox');
      put(field, 'aria-autocomplete', 'list');
      if (list) put(field, 'aria-controls', list.id);
      put(field, 'aria-expanded', String(now));
      // Rendered when the input is among the children; else only the DOM can say.
      if (el && !latest.current.written) put(el, 'aria-disabled', field.hasAttribute('disabled') ? 'true' : null);
    }
    // The option's recipe paints the highlight only on data-focus. The input has focus here, so the combobox writes it.
    const focused = !!field && field.ownerDocument.activeElement === field;
    for (const option of options()) put(option, 'data-focus', now && focused && option.hasAttribute(MARK) ? '' : null);
  }, [base, input, popup, listbox, options]);

  /**
   * Takes an option: its text goes into the input, it alone is selected, the list closes, and onChange is called
   * once all of that is written. @param {HTMLElement | null | undefined} option @param {import('react').SyntheticEvent} event
   */
  const take = (option, event) => {
    const field = input();
    if (!field || !option || disabled(option) || option.hasAttribute('hidden') || readOnly()) return;
    field.value = textOf(option);
    for (const other of options()) put(other, 'selected', other === option ? '' : null);
    filter(field.value);
    request(false);
    latest.current.onChange?.(field.value, event);
  };

  // Shows or hides the popup in the same task as the render that opened or closed it, and clears the highlight of a closed list.
  useLayoutEffect(() => {
    const box = popup();
    // A read-only or disabled input does not open its list (J80).
    if (isOpen && (readOnly() || input()?.hasAttribute('disabled'))) {
      latest.current.isOpen = false;
      if (!latest.current.controlled) setOwn(false);
      sync();
      return;
    }
    // A list closed because its input became read-only or disabled stays closed once the input is not.
    if (!isOpen && own && !latest.current.controlled) setOwn(false);
    sync(); // writes popover="manual" on a popup that has none, before it is shown
    if (box && isOpen !== box.matches(':popover-open')) {
      if (isOpen) box.showPopover();
      else box.hidePopover();
    }
    if (!isOpen) for (const option of options()) put(option, MARK, null);
    sync();
  }, [isOpen, own, popup, input, readOnly, options, sync]);
  // After every render: the DOM may have changed under the author's own elements.
  useLayoutEffect(() => { sync(); });

  useLayoutEffect(() => {
    const el = /** @type {HTMLDivElement} */ (root.current);
    const off = new AbortController();
    // Something else hid the popup, such as a script calling hidePopover(): the state follows.
    el.addEventListener('toggle', (event) => {
      const box = popup();
      if (!box || event.target !== box || box.matches(':popover-open')) return;
      if (latest.current.isOpen && !latest.current.controlled) { latest.current.isOpen = false; flushSync(() => setOwn(false)); }
    }, { capture: true, signal: off.signal });
    const stops = [
      activeDescendant(el, {
        items: shown,
        skip: disabled,
        wrap: true,
        focus: () => input() ?? el,
        active: () => !textKey.current && !readOnly(),
      }), dismiss(el, {
        // Escape, a press outside and focus that leaves close the list. A press on the input is inside the root.
        active: () => latest.current.isOpen,
        onDismiss: () => request(false),
      }),
    ];
    const observer = new MutationObserver(() => {
      const field = input();
      // A disabled input takes no keys, and a read-only one opens no list, so its list does not stay open.
      if (latest.current.isOpen && (field?.hasAttribute('disabled') || field?.hasAttribute('readonly'))) request(false);
      sync();
    });
    observer.observe(el, { childList: true, subtree: true, attributes: true, attributeFilter: ['role', 'id', 'tabindex', 'popover', 'disabled', 'readonly', MARK, 'data-focus'] });
    return () => { off.abort(); observer.disconnect(); for (const stop of stops) stop(); };
  }, [input, popup, shown, readOnly, request, sync]);

  useEffect(() => {
    const at = requestAnimationFrame(() => root.current?.setAttribute('data-ready', ''));
    return () => cancelAnimationFrame(at);
  }, []);

  return createElement('div', /** @type {any} */ ({
    ...rest, ref: setRef, 'data-ui': 'combobox',
    open: isOpen ? true : undefined,
    'aria-disabled': written ? (written.disabled ? 'true' : undefined) : rest['aria-disabled'],
    // Typing filters the options, and opens the list while one shows (J44).
    onInput: (/** @type {import('react').InputEvent<HTMLDivElement>} */ event) => {
      onInput?.(event);
      const field = input();
      // A read-only input fires no input event, and request() opens no read-only list.
      if (event.target !== field || !field) return;
      request(filter(field.value) > 0);
    },
    // Before the behaviours, which listen on this root: the keys the combobox handles itself.
    onKeyDownCapture: (/** @type {import('react').KeyboardEvent<HTMLDivElement>} */ event) => {
      onKeyDownCapture?.(event);
      const field = input();
      if (!field || event.target !== field) return;
      textKey.current = event.key === 'Home' || event.key === 'End';
      if (event.altKey || event.ctrlKey || event.metaKey || event.shiftKey || readOnly()) return;
      const now = latest.current.isOpen;
      if ((event.key === 'ArrowDown' || event.key === 'ArrowUp') && !now) {
        // Opening first lets activeDescendant, which runs next, take the key: with nothing highlighted,
        // ArrowDown goes to the first option that shows and ArrowUp to the last.
        if (shown().length) request(true);
      } else if (event.key === 'Enter' && now) {
        const option = shown().find((el) => el.hasAttribute(MARK));
        if (!option) return; // Nothing highlighted: Enter submits the form, as in a plain input.
        event.preventDefault();
        take(option, event);
      } else if (event.key === 'Escape' && !now && field.value !== '') {
        // With the list open, dismiss closes it; with the list closed, Escape clears the field.
        event.preventDefault();
        field.value = '';
        filter('');
      }
    },
    // A click on an option takes it. The listbox has highlighted and selected it already.
    onClick: (/** @type {import('react').MouseEvent<HTMLDivElement>} */ event) => {
      onClick?.(event);
      const option = /** @type {HTMLElement | null} */ (event.target instanceof Element ? event.target.closest(OPTION) : null);
      if (option && options().includes(option)) take(option, event);
    },
    // A press moves no focus: inside the popup it would focus the listbox, and on the field around the input
    // it would take focus from the input, which it gives to the input instead.
    onMouseDown: (/** @type {import('react').MouseEvent<HTMLDivElement>} */ event) => {
      onMouseDown?.(event);
      const field = input();
      if (!(event.target instanceof Node) || event.target === field) return;
      event.preventDefault();
      if (event.target === root.current) field?.focus();
    },
    onFocus: (/** @type {import('react').FocusEvent<HTMLDivElement>} */ event) => { onFocus?.(event); sync(); },
    onBlur: (/** @type {import('react').FocusEvent<HTMLDivElement>} */ event) => { onBlur?.(event); sync(); },
  }), children);
}
