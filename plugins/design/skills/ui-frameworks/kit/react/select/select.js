// @ts-check
/**
 * select.js: the APG's select-only combobox, a control that shows one chosen option and opens a list to choose
 * another, for React (docs/specs/targets.md).
 *
 * The root is a <div role="combobox">: the one stop in the Tab order, which keeps focus. It renders the value
 * part, a <span> at its start with the chosen option's text, or the placeholder when none is chosen, and holds
 * the author's popup (the child marked data-part="popup"), which holds the kit's listbox. The option the keys
 * point at carries data-highlighted and is named by aria-activedescendant on the root (J82 to J86).
 *
 * The popup is the author's element, and the listbox and the options are of another family, so the select finds
 * them in the DOM, by data-part and by role, as the Web Component does, and writes what its manifest says it
 * writes, only where it differs, after each render and whenever its subtree changes: popover="manual" on a popup
 * that has none, an id and tabindex="-1" on the listbox, aria-controls on itself, and selected and data-focus on
 * the options; activeDescendant writes data-highlighted, the options' ids and aria-activedescendant. The select's
 * value decides which option is selected: it writes `selected` on that option and on no other, whoever else
 * writes it. The listbox's own logic still runs, as on the Web Component: a click on an option selects it there
 * first, and the listbox then takes the select's choice as its own.
 *
 * The value is controlled (value with onChange) or uncontrolled (defaultValue); with neither, it is the last
 * option the author marked `selected`. onInput(value, event) and then onChange(value, event) are called when the
 * user chooses another option, after the value part, the options and the list are written. The text of the
 * value part is read from the children for the first render, so that the server markup shows it, and from the
 * DOM afterwards. `open` is the author attribute on the root (X2), with aria-expanded; it is controlled (open) or
 * uncontrolled (defaultOpen), and a controlled select shows or hides its popup itself when the user asks, and
 * the platform's toggle event on the popup tells the owner, as on the menu.
 *
 * It is a form control with no native control of its own, so it renders a native <input type="hidden"> part
 * with `name` and the value. A reset of the form restores the first value. Required-ness is only aria-required:
 * without ElementInternals nothing blocks a submit (see the report).
 */
import { Children, Fragment, createElement, isValidElement, useCallback, useEffect, useId, useLayoutEffect, useMemo, useRef, useState } from 'react';
import { flushSync } from 'react-dom';
import { activeDescendant } from '../../behaviours/active-descendant.js';
import { typeahead } from '../../behaviours/typeahead.js';
import { dismiss } from '../../behaviours/dismiss.js';
import { role, tabindex } from '../../components/select/select.props.js';

/**
 * @typedef {{ value: string, text: string, selected?: boolean }} Known
 * @typedef {Omit<import('react').HTMLAttributes<HTMLDivElement>, 'onChange' | 'onInput' | 'defaultValue' | 'placeholder'> & {
 *   value?: string, defaultValue?: string, name?: string, placeholder?: string,
 *   open?: boolean, defaultOpen?: boolean, required?: boolean, disabled?: boolean,
 *   onInput?: (value: string, event: import('react').SyntheticEvent | Event) => void,
 *   onChange?: (value: string, event: import('react').SyntheticEvent | Event) => void,
 *   ref?: import('react').Ref<HTMLDivElement>,
 * }} SelectProps
 */

const LISTBOX = '[role="listbox"]';
const OPTION = '[role="option"]';
const MARK = 'data-highlighted';
const OPENERS = ['ArrowDown', 'ArrowUp', 'Home', 'End', 'Enter', ' '];

/** @param {Element} el */
const disabled = (el) => el.hasAttribute('disabled') || el.getAttribute('aria-disabled') === 'true';
/** An option's text, as the value part shows it. @param {Element} el */
const textOf = (el) => (el.textContent ?? '').trim();
/** An option's value: its `value` attribute, or else its text. @param {Element} el */
const valueOf = (el) => el.getAttribute('value') ?? textOf(el);
/** Sets or removes an attribute, only when it differs. @param {Element} el @param {string} name @param {string | null} value */
const put = (el, name, value) => {
  if (el.getAttribute(name) === value) return;
  if (value === null) el.removeAttribute(name);
  else el.setAttribute(name, value);
};
/** The text React children render, as far as it can be read from them. @param {import('react').ReactNode} node @returns {string} */
const text = (node) => {
  if (node === null || node === undefined || typeof node === 'boolean') return '';
  if (typeof node === 'string' || typeof node === 'number') return String(node);
  if (Array.isArray(node)) return node.map(text).join('');
  if (isValidElement(node)) return text(/** @type {any} */ (node.props).children);
  return '';
};
/** The role a component of the kit renders, read from the function, without importing it. @param {unknown} node */
const roleOf = (node) => (isValidElement(node) && typeof node.type === 'function' ? /** @type {any} */ (node.type).kitRole : undefined);
/**
 * The options among the children, through fragments, plain elements and the first listbox, as the first render
 * knows them; not those of a listbox nested in an option.
 * @param {import('react').ReactNode} children @param {Known[]} [out] @returns {Known[]}
 */
function collect(children, out = []) {
  Children.forEach(children, (child) => {
    if (!isValidElement(child)) return;
    const props = /** @type {any} */ (child.props);
    const kind = roleOf(child);
    if (kind === 'option') { const t = text(props.children).trim(); out.push({ value: props.value ?? t, text: t, selected: !!props.selected }); }
    else if (kind === 'listbox' || (kind === undefined && (child.type === Fragment || typeof child.type === 'string'))) collect(props.children, out);
  });
  return out;
}
const same = (/** @type {Known[]} */ a, /** @type {Known[]} */ b) => a.length === b.length && a.every((k, i) => k.value === b[i].value && k.text === b[i].text);

/** @param {SelectProps} props */
export function Select({ value, defaultValue, name, placeholder, open, defaultOpen = false, required = false, disabled: off = false, onInput, onChange, onKeyDownCapture, onMouseDown, onClick, children, ref, ...rest }) {
  const walked = collect(children);
  const [own, setOwn] = useState(() => defaultValue ?? walked.filter((o) => o.selected).pop()?.value ?? '');
  const current = value !== undefined ? value : own;
  const [ownOpen, setOwnOpen] = useState(defaultOpen);
  const isOpen = (open !== undefined ? open : ownOpen) && !off;
  /** The options in the DOM, with their values and texts, once mounted; the walk's until then. */
  const [known, setKnown] = useState(() => walked.map(({ value: v, text: t }) => ({ value: v, text: t })));
  const knownNow = useRef(known);
  const chosen = current === '' ? undefined : known.find((k) => k.value === current);
  const base = useId();

  /** @type {import('react').RefObject<HTMLDivElement | null>} */
  const root = useRef(null);
  const setRef = useCallback((/** @type {HTMLDivElement | null} */ node) => {
    // Kept after unmount, so that a listener or an observer that outlived it would still act, and be seen (X4).
    if (node) root.current = node;
    if (typeof ref === 'function') ref(node);
    else if (ref) ref.current = node;
  }, [ref]);
  const latest = useRef({ current, isOpen, off, controlled: value !== undefined, openControlled: open !== undefined, found: walked.length > 0, onInput, onChange });
  latest.current = { current, isOpen, off, controlled: value !== undefined, openControlled: open !== undefined, found: walked.length > 0, onInput, onChange };
  /** @type {import('react').RefObject<string | null>} The value once the select first settled with its options: what a reset restores. */
  const initial = useRef(/** @type {string | null} */ (null));
  /** @type {import('react').RefObject<HTMLElement | null>} The option the list opens on, when Home, End or a typed letter opened it. */
  const target = useRef(/** @type {HTMLElement | null} */ (null));
  /** Whether the key going down opened the list, so that activeDescendant does not move on with it. */
  const opened = useRef(false);

  const popup = useCallback(() => /** @type {HTMLElement | null} */ (root.current?.querySelector(':scope > [data-part="popup"]') ?? null), []);
  const listbox = useCallback(() => /** @type {HTMLElement | null} */ (popup()?.querySelector(LISTBOX) ?? null), [popup]);
  /** The options of the listbox, and not of a listbox nested in one. */
  const options = useCallback(() => {
    const list = listbox();
    return list ? /** @type {HTMLElement[]} */ ([...list.querySelectorAll(OPTION)].filter((el) => el.closest(LISTBOX) === list)) : [];
  }, [listbox]);
  const chosenOption = useCallback(() => {
    const v = latest.current.current;
    return v === '' ? null : options().find((el) => valueOf(el) === v) ?? null;
  }, [options]);
  const highlighted = useCallback(() => options().find((el) => el.hasAttribute(MARK)) ?? null, [options]);
  /** Points at `to`, or else at the chosen option, or else at the first; never at a disabled one. @param {HTMLElement | null} [to] */
  const point = useCallback((/** @type {HTMLElement | null} */ to = null) => {
    const usable = options().filter((el) => !disabled(el));
    const at = chosenOption();
    const next = to ?? (at && usable.includes(at) ? at : usable[0]);
    if (next) put(next, MARK, '');
  }, [options, chosenOption]);

  /**
   * Asks for the list to open or close. Uncontrolled, the state changes in the same task; controlled, the popup
   * is shown or hidden and its toggle event tells the owner. @param {boolean} next
   */
  const request = useCallback((/** @type {boolean} */ next) => {
    const { isOpen: now, openControlled, off: no } = latest.current;
    if (next && no) return;
    if (!openControlled) { if (next !== now) { latest.current.isOpen = next; flushSync(() => setOwnOpen(next)); } return; }
    const box = popup();
    if (!box) return;
    if (!box.hasAttribute('popover')) box.setAttribute('popover', 'manual');
    if (next && !box.matches(':popover-open')) { box.showPopover(); point(target.current); target.current = null; }
    else if (!next && box.matches(':popover-open')) { box.hidePopover(); for (const option of options()) put(option, MARK, null); }
  }, [popup, point, options]);
  /** Opens the list on `to`, or on the chosen option. @param {HTMLElement | null | undefined} [to] */
  const openAt = useCallback((/** @type {HTMLElement | null | undefined} */ to) => { target.current = to ?? null; request(true); }, [request]);

  /**
   * Takes a value the DOM says, when the value is uncontrolled. From a native listener or an observer it is
   * rendered in the same task; from an effect React renders it before paint. @param {string} next @param {boolean} [inEffect]
   */
  const adopt = useCallback((/** @type {string} */ next, inEffect = false) => {
    if (latest.current.controlled || next === latest.current.current) return;
    latest.current.current = next;
    if (inEffect) setOwn(next);
    else flushSync(() => setOwn(next));
  }, []);

  /** Brings the listbox's passivity, the options' selection, the known texts and the painted highlight in step. */
  const sync = useCallback((inEffect = false) => {
    const el = root.current, box = popup(), list = listbox();
    if (!el) return;
    if (box && !box.hasAttribute('popover')) box.setAttribute('popover', 'manual');
    if (list) {
      if (!list.id) list.id = `${base}listbox`;
      put(list, 'tabindex', '-1');
    }
    put(el, 'aria-controls', list ? list.id : null);
    const all = options();
    const now = all.map((o) => ({ value: valueOf(o), text: textOf(o) }));
    if (!same(knownNow.current, now)) {
      knownNow.current = now;
      if (inEffect) setKnown(now);
      else flushSync(() => setKnown(now));
    }
    if (all.length && initial.current === null) {
      // No value given and none found among the children (they are wrapped): take the last option marked.
      if (latest.current.current === '' && !latest.current.found) {
        const marked = all.filter((o) => o.hasAttribute('selected') || o.getAttribute('aria-selected') === 'true').pop();
        if (marked) adopt(valueOf(marked), inEffect);
      }
      initial.current = latest.current.current;
    }
    const at = chosenOption();
    for (const option of all) put(option, 'selected', option === at ? '' : null);
    for (const option of all) put(option, 'data-focus', latest.current.isOpen && option.hasAttribute(MARK) ? '' : null);
  }, [base, popup, listbox, options, chosenOption, adopt]);

  /**
   * Chooses an option because the user asked, closes the list, and then calls onInput and onChange when the value
   * changed. None only closes it. @param {HTMLElement | null} option @param {import('react').SyntheticEvent} event
   */
  const choose = (option, event) => {
    const before = latest.current.current;
    const next = option ? valueOf(option) : before;
    flushSync(() => {
      if (!latest.current.controlled && next !== before) { latest.current.current = next; setOwn(next); }
      if (!latest.current.openControlled) { latest.current.isOpen = false; setOwnOpen(false); }
    });
    if (latest.current.openControlled) request(false);
    if (next === before) return;
    onInput?.(next, event);
    onChange?.(next, event);
  };

  // Shows or hides the popup in the same task as the render that opened or closed it; points at an option when
  // the list opens, and at none once it closes.
  useLayoutEffect(() => {
    const box = popup();
    sync(true); // writes popover="manual" on a popup that has none, before it is shown
    const showing = !!box?.matches(':popover-open');
    if (box && isOpen !== showing) {
      if (isOpen) box.showPopover();
      else box.hidePopover();
    }
    if (isOpen && !showing) point(target.current);
    target.current = null;
    if (!isOpen) for (const option of options()) put(option, MARK, null);
    // A list a disabled select closed stays closed once it is enabled again (J86).
    if (off && ownOpen && !latest.current.openControlled) setOwnOpen(false);
    sync(true);
  }, [isOpen, off, ownOpen, popup, point, options, sync]);
  // After every render: the options follow the value.
  useLayoutEffect(() => { sync(true); });

  useLayoutEffect(() => {
    const el = /** @type {HTMLDivElement} */ (root.current);
    const stop = new AbortController();
    // Something else hid the popup, such as a script calling hidePopover(): the state follows.
    el.addEventListener('toggle', (event) => {
      const box = popup();
      if (!box || event.target !== box || box.matches(':popover-open')) return;
      if (latest.current.isOpen && !latest.current.openControlled) { latest.current.isOpen = false; flushSync(() => setOwnOpen(false)); }
    }, { capture: true, signal: stop.signal });
    // A reset of the form puts the first value back, once the platform has reset its own controls.
    el.closest('form')?.addEventListener('reset', () => setTimeout(() => { if (initial.current !== null) adopt(initial.current); }), { signal: stop.signal });
    const stops = [
      activeDescendant(el, {
        items: options,
        skip: disabled,
        // A key on a closed select opens it first and sets `opened`, so this alone keeps a closed list still.
        active: () => !opened.current,
      }), typeahead(el, {
        // The search starts from the option the keys point at, or from the chosen one while the list is closed.
        items: options,
        current: () => highlighted() ?? chosenOption(),
        skip: disabled,
        onMatch: (option) => {
          if (latest.current.isOpen) put(option, MARK, '');
          else openAt(option);
        },
      }), dismiss(el, {
        // Escape, a press outside and focus that leaves close the list and keep the value. Escape goes no further.
        active: () => latest.current.isOpen,
        onDismiss: () => request(false),
      }),
    ];
    const observer = new MutationObserver(() => {
      // Options that arrive in an open list: point at one.
      if (latest.current.isOpen && !highlighted()) point();
      sync();
    });
    observer.observe(el, { childList: true, subtree: true, characterData: true, attributes: true, attributeFilter: ['role', 'id', 'value', 'tabindex', 'popover', 'selected', 'disabled', 'aria-disabled', MARK, 'data-focus'] });
    return () => { stop.abort(); observer.disconnect(); for (const s of stops) s(); };
  }, [popup, options, highlighted, chosenOption, point, openAt, request, adopt, sync]);

  useEffect(() => {
    const at = requestAnimationFrame(() => root.current?.setAttribute('data-ready', ''));
    return () => cancelAnimationFrame(at);
  }, []);

  const self = (/** @type {import('react').SyntheticEvent} */ event) => event.target === root.current;
  // The same element while the name and the value stay, so that React does not write the input again (G3).
  const submitted = name && !off && chosen ? chosen.value : null;
  const field = useMemo(() => (submitted !== null ? createElement('input', { type: 'hidden', 'data-part': 'input', name, value: submitted }) : null), [name, submitted]);
  return createElement('div', /** @type {any} */ ({
    ...rest, ref: setRef, role, 'data-ui': 'select',
    tabIndex: off ? undefined : tabindex,
    'aria-haspopup': 'listbox',
    'aria-expanded': String(isOpen),
    'aria-required': required ? 'true' : undefined,
    'aria-disabled': off ? 'true' : undefined,
    open: isOpen ? true : undefined,
    // Before the behaviours, which listen on this root: the keys that open the list, and those that choose.
    onKeyDownCapture: (/** @type {import('react').KeyboardEvent<HTMLDivElement>} */ event) => {
      onKeyDownCapture?.(event);
      opened.current = false;
      if (!self(event) || off || event.altKey || event.ctrlKey || event.metaKey) return;
      if (!latest.current.isOpen) {
        if (!OPENERS.includes(event.key)) return;
        const usable = options().filter((el) => !disabled(el));
        event.preventDefault();
        opened.current = true;
        openAt(event.key === 'Home' ? usable[0] : event.key === 'End' ? usable[usable.length - 1] : null);
      } else if (event.key === 'Enter' || event.key === ' ' || event.key === 'Tab') {
        // Tab keeps its default: the choice is made, and focus moves on.
        if (event.key !== 'Tab') event.preventDefault();
        choose(highlighted(), event);
      }
    },
    // A press on the select opens the list, or closes it; the press itself gives the root focus. A press in the
    // popup moves no focus: it would focus the listbox.
    onMouseDown: (/** @type {import('react').MouseEvent<HTMLDivElement>} */ event) => {
      onMouseDown?.(event);
      if (!(event.target instanceof Node)) return;
      if (popup()?.contains(event.target)) { event.preventDefault(); return; }
      if (event.button !== 0) return; // request() opens no disabled select
      request(!latest.current.isOpen);
    },
    // A click on an option chooses it. The listbox has selected it already, and the select's value decides.
    onClick: (/** @type {import('react').MouseEvent<HTMLDivElement>} */ event) => {
      onClick?.(event);
      const option = /** @type {HTMLElement | null} */ (event.target instanceof Element ? event.target.closest(OPTION) : null);
      if (option && !disabled(option) && options().includes(option)) choose(option, event);
    },
  }),
  createElement('span', { 'data-part': 'value', 'data-placeholder': chosen ? undefined : '' }, chosen ? chosen.text : placeholder ?? ''),
  children,
  field);
}
