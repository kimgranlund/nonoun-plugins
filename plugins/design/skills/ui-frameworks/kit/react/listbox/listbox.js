// @ts-check
/**
 * listbox.js: a list from which one option, or several, can be chosen, for React (docs/specs/targets.md).
 *
 * The root is a <div role="listbox">, one stop in the Tab order, that keeps focus: the options never take it.
 * It mounts activeDescendant and typeahead as the Web Component does, so the keys, a typed letter and a press
 * move the highlight, which the behaviour writes as data-highlighted and names in aria-activedescendant. In a
 * single listbox the selection follows the highlight; with `multiple` the keys only move it, and Space or a
 * click toggles an option (J27 to J29).
 *
 * The value is controlled (value with onChange) or uncontrolled (defaultValue); with neither, it is the
 * options the author marked `selected`, the last one in a single listbox. It is a string, the selected values
 * joined by commas with `multiple`, as on the Web Component. onInput(value, event) and then onChange(value,
 * event) are called when the user changes the selection, once the options are written (J29).
 *
 * The DOM is where the selection lives, as on the Web Component, because a combobox or a select of another
 * family holds a listbox and writes its options too: after each render, and whenever its subtree changes, the
 * listbox writes `selected` on the options its value names and on no other, only where it differs. A `selected`
 * that something else writes (a script, a select) is read back as the value while the value is uncontrolled;
 * a controlled value is written over it. The listbox renders none of the attributes another component writes
 * on it or on its options: tabindex, id, selected, data-highlighted and data-focus are written into the DOM.
 * tabindex="0" is written only where the element has none, as the Web Component's base does, so a holder's
 * tabindex="-1" stays.
 *
 * It is a form control with no native control of its own, so it renders a native <input type="hidden"> part
 * per submitted value, under `name` (J30). A reset of the form restores the first value. Required-ness is only
 * aria-required: without ElementInternals nothing blocks a submit (see the report).
 */
import { Children, Fragment, createContext, createElement, isValidElement, useCallback, useEffect, useLayoutEffect, useMemo, useRef, useState } from 'react';
import { flushSync } from 'react-dom';
import { activeDescendant } from '../../behaviours/active-descendant.js';
import { typeahead } from '../../behaviours/typeahead.js';
import { role } from '../../components/listbox/listbox.props.js';

/**
 * @typedef {{ chosen: string[], found: boolean }} ListboxState
 * @typedef {Omit<import('react').HTMLAttributes<HTMLDivElement>, 'onChange' | 'onInput' | 'defaultValue'> & {
 *   value?: string, defaultValue?: string, multiple?: boolean, name?: string, required?: boolean, disabled?: boolean,
 *   onInput?: (value: string, event: import('react').SyntheticEvent) => void,
 *   onChange?: (value: string, event: import('react').SyntheticEvent) => void,
 *   ref?: import('react').Ref<HTMLDivElement>,
 * }} ListboxProps
 */

/**
 * What an option reads when it first renders: the values its listbox has chosen then, and whether the listbox
 * found its options among its children, so that it knows the option's `selected` prop. @type {import('react').Context<ListboxState | null>}
 */
export const ListboxContext = /* @__PURE__ */ createContext(/** @type {ListboxState | null} */ (null));

const OPTION = '[role="option"]';
const LISTBOX = '[role="listbox"]';
const MARK = 'data-highlighted';

/** @param {Element} el */
const disabled = (el) => el.hasAttribute('disabled') || el.getAttribute('aria-disabled') === 'true';
/** Sets or removes an attribute, only when it differs. @param {Element} el @param {string} name @param {string | null} value */
const put = (el, name, value) => {
  if (el.getAttribute(name) === value) return;
  if (value === null) el.removeAttribute(name);
  else el.setAttribute(name, value);
};
/** An option's value in the DOM: its `value` attribute, or else its text. @param {Element} el */
const valueOf = (el) => el.getAttribute('value') ?? (el.textContent ?? '').trim();

/** The text React children render, as far as it can be read from them. @param {import('react').ReactNode} node @returns {string} */
export const textOf = (node) => {
  if (node === null || node === undefined || typeof node === 'boolean') return '';
  if (typeof node === 'string' || typeof node === 'number') return String(node);
  if (Array.isArray(node)) return node.map(textOf).join('');
  if (isValidElement(node)) return textOf(/** @type {any} */ (node.props).children);
  return '';
};
/** The role a component of the kit renders, read from the function, so that a walk knows it without importing it. @param {unknown} node */
const roleOf = (node) => (isValidElement(node) && typeof node.type === 'function' ? /** @type {any} */ (node.type).kitRole : undefined);

/**
 * The props of the options among the children, through fragments and plain elements, each with its value; not
 * those of a listbox nested inside one.
 * @param {import('react').ReactNode} children @param {{ value: string, selected: boolean }[]} [out]
 */
function collect(children, out = []) {
  Children.forEach(children, (child) => {
    if (!isValidElement(child)) return;
    const props = /** @type {any} */ (child.props);
    const kind = roleOf(child);
    if (kind === 'option') out.push({ value: props.value ?? textOf(props.children).trim(), selected: !!props.selected });
    else if (kind === undefined && (child.type === Fragment || typeof child.type === 'string')) collect(props.children, out);
  });
  return out;
}

/** @param {ListboxProps} props */
function ListboxRoot({ value, defaultValue, multiple = false, name, required = false, disabled: off = false, onInput, onChange, onKeyDown, onKeyDownCapture, onClick, onFocus, onBlur, children, ref, ...rest }) {
  const options = collect(children);
  const [own, setOwn] = useState(() => {
    if (defaultValue !== undefined) return defaultValue;
    const marked = options.filter((o) => o.selected).map((o) => o.value);
    return (multiple ? marked : marked.slice(-1)).join(',');
  });
  const current = value !== undefined ? value : own;
  /** The values `current` names: one, or with multiple those between the commas. */
  const chosen = current === '' ? [] : multiple ? current.split(',') : [current];
  /** The values of the options in the DOM, in their order, once mounted; the walk's until then. */
  const [known, setKnown] = useState(() => options.map((o) => o.value));

  /** @type {import('react').RefObject<HTMLDivElement | null>} */
  const root = useRef(null);
  const setRef = useCallback((/** @type {HTMLDivElement | null} */ node) => {
    // Kept after unmount, so that a listener or an observer that outlived it would still act, and be seen (X4).
    if (node) root.current = node;
    if (typeof ref === 'function') ref(node);
    else if (ref) ref.current = node;
  }, [ref]);
  const latest = useRef({ current, multiple, controlled: value !== undefined, off, found: options.length > 0, onInput, onChange });
  latest.current = { current, multiple, controlled: value !== undefined, off, found: options.length > 0, onInput, onChange };
  /** @type {import('react').RefObject<string | null>} The value once the listbox first settled with its options: what a reset restores. */
  const initial = useRef(/** @type {string | null} */ (null));
  /** @type {import('react').RefObject<HTMLElement | null>} The option that was highlighted when the current key went down. */
  const before = useRef(/** @type {HTMLElement | null} */ (null));

  /** The options of this listbox, and not of another listbox nested in it. */
  const mine = useCallback(() => {
    const el = root.current;
    return el ? /** @type {HTMLElement[]} */ ([...el.querySelectorAll(OPTION)].filter((x) => x.closest(LISTBOX) === el)) : [];
  }, []);
  const chosenNow = useCallback(() => {
    const { current: v, multiple: m } = latest.current;
    return v === '' ? [] : m ? v.split(',') : [v];
  }, []);
  /** The values among `values` that name an option, once each, in the order of the options. @param {string[]} values */
  const ordered = useCallback((/** @type {string[]} */ values) => [...new Set(mine().map(valueOf).filter((v) => values.includes(v)))], [mine]);
  /** The highlighted option; while two carry the mark, the one that is not `was`. @param {HTMLElement | null} [was] */
  const highlighted = useCallback((/** @type {HTMLElement | null} */ was = null) => {
    const marked = mine().filter((x) => x.hasAttribute(MARK));
    return marked.find((x) => x !== was) ?? (was && marked.includes(was) ? was : null);
  }, [mine]);
  /** Paints the highlight while the listbox has focus: data-focus on the highlighted option alone. @param {boolean} on */
  const mirror = useCallback((/** @type {boolean} */ on) => {
    for (const option of mine()) put(option, 'data-focus', on && option.hasAttribute(MARK) ? '' : null);
  }, [mine]);
  /**
   * Takes a value that the DOM says, when the value is uncontrolled. From a native listener or an observer it is
   * rendered in the same task; from an effect React renders it before paint, and flushSync may not be called.
   * @param {string} next @param {boolean} [inEffect]
   */
  const adopt = useCallback((/** @type {string} */ next, inEffect = false) => {
    if (latest.current.controlled || next === latest.current.current) return;
    latest.current.current = next;
    if (inEffect) setOwn(next);
    else flushSync(() => setOwn(next));
  }, []);
  const knownNow = useRef(known);
  /** @type {import('react').RefObject<MutationObserver | null>} */
  const watcher = useRef(/** @type {MutationObserver | null} */ (null));

  /**
   * Takes the value from `selected` attributes that something else wrote: a script, a select, or an option whose
   * selected prop changed. Every record is read before anything is written.
   * @param {MutationRecord[]} records @param {boolean} [inEffect]
   */
  const read = useCallback((/** @type {MutationRecord[]} */ records, inEffect = false) => {
    const options = mine();
    let now = chosenNow();
    let marked = false;
    for (const record of records) {
      const option = /** @type {HTMLElement} */ (record.target);
      if (record.attributeName !== 'selected' || !options.includes(option)) continue;
      const v = valueOf(option);
      if (option.hasAttribute('selected') && !now.includes(v)) now = latest.current.multiple ? [...now, v] : [v];
      else if (!option.hasAttribute('selected') && now.includes(v)) now = now.filter((x) => x !== v);
      else continue;
      marked = true;
    }
    if (marked) adopt(latest.current.multiple ? ordered(now).join(',') : now[0] ?? '', inEffect);
  }, [mine, chosenNow, ordered, adopt]);

  /** Brings the options' `selected` in step with the value, and the known options with the DOM. */
  const sync = useCallback(() => {
    const options = mine();
    const values = options.map(valueOf);
    const was = knownNow.current;
    if (was.length !== values.length || was.some((v, i) => v !== values[i])) { knownNow.current = values; setKnown(values); }
    if (!options.length) return;
    if (initial.current === null) {
      // No value given and none found among the children (they are wrapped): take what the options say.
      if (latest.current.current === '' && !latest.current.found) {
        const marked = options.filter((x) => x.getAttribute('aria-selected') === 'true').map(valueOf);
        if (marked.length) adopt((latest.current.multiple ? marked : marked.slice(-1)).join(','), true);
      }
      initial.current = latest.current.current;
    }
    const now = chosenNow();
    for (const option of options) put(option, 'selected', now.includes(valueOf(option)) ? '' : null);
  }, [mine, chosenNow, adopt]);

  /** Selects an option, or with multiple toggles it, because the user asked; then tells the props. @param {HTMLElement | null} option @param {import('react').SyntheticEvent} event */
  const choose = (option, event) => {
    if (!option || disabled(option)) return;
    const v = valueOf(option);
    let next = v;
    if (multiple) {
      const now = chosenNow();
      next = ordered(now.includes(v) ? now.filter((x) => x !== v) : [...now, v]).join(',');
    }
    if (next === latest.current.current) return;
    if (!latest.current.controlled) { latest.current.current = next; flushSync(() => setOwn(next)); }
    onInput?.(next, event);
    onChange?.(next, event);
  };

  // After each render: the options follow the value, once what was written since the last look is read, such as
  // the mark an option whose selected prop changed wrote in this commit.
  useLayoutEffect(() => {
    const records = watcher.current?.takeRecords();
    if (records?.length) read(records, true);
    sync();
  });
  // tabindex is written only where there is none, so a holder's tabindex="-1" stays; a disabled listbox has none.
  useLayoutEffect(() => {
    const el = /** @type {HTMLDivElement} */ (root.current);
    if (off) { if (el.getAttribute('tabindex') === '0') el.removeAttribute('tabindex'); }
    else if (!el.hasAttribute('tabindex')) el.setAttribute('tabindex', '0');
  }, [off]);

  useLayoutEffect(() => {
    const el = /** @type {HTMLDivElement} */ (root.current);
    const stops = [
      activeDescendant(el, {
        items: mine,
        skip: disabled,
        fallback: () => mine().find((x) => x.hasAttribute('selected')),
      }),
      typeahead(el, {
        // The search starts from the highlighted option: focus stays on the listbox, so typeahead cannot see it.
        items: mine,
        current: () => highlighted(),
        skip: disabled,
        onMatch: (option) => put(option, MARK, ''),
      }),
    ];
    const observer = new MutationObserver((records) => {
      read(records);
      sync();
      if (el.ownerDocument.activeElement === el) mirror(true);
    });
    watcher.current = observer;
    observer.observe(el, { childList: true, subtree: true, attributes: true, attributeFilter: ['role', 'value', 'selected', 'disabled', 'aria-disabled', MARK] });
    // A reset of the form puts the first value back, once the platform has reset its own controls.
    const off = new AbortController();
    el.closest('form')?.addEventListener('reset', () => setTimeout(() => { if (initial.current !== null) adopt(initial.current); }), { signal: off.signal });
    return () => { for (const stop of stops) stop(); observer.disconnect(); watcher.current = null; off.abort(); };
  }, [mine, highlighted, read, adopt, sync, mirror]);

  useEffect(() => {
    const at = requestAnimationFrame(() => root.current?.setAttribute('data-ready', ''));
    return () => cancelAnimationFrame(at);
  }, []);

  const self = (/** @type {import('react').SyntheticEvent} */ event) => event.target === root.current;
  const submitted = multiple ? known.filter((v, i) => chosen.includes(v) && known.indexOf(v) === i) : chosen.length && known.includes(chosen[0]) ? [chosen[0]] : [];
  // The same elements while the name and the values stay, so that React does not write the inputs again (G3).
  const key = name && !off ? `${name}\u0000${submitted.join('\u0000')}` : '';
  const fields = useMemo(() => (key ? submitted.map((v) => createElement('input', { key: v, type: 'hidden', 'data-part': 'input', name, value: v })) : null), [key]);
  return createElement('div', /** @type {any} */ ({
    ...rest, ref: setRef, role, 'data-ui': 'listbox',
    'aria-multiselectable': multiple ? 'true' : undefined,
    'aria-required': required ? 'true' : undefined,
    'aria-disabled': off ? 'true' : undefined,
    // Before the behaviours, which listen on the root: which option was highlighted when the key went down.
    onKeyDownCapture: (/** @type {import('react').KeyboardEvent<HTMLDivElement>} */ event) => {
      onKeyDownCapture?.(event);
      if (self(event)) before.current = highlighted();
    },
    // After the behaviours: a single listbox selects the option a key moved the highlight to; with multiple,
    // Space toggles the highlighted option.
    onKeyDown: (/** @type {import('react').KeyboardEvent<HTMLDivElement>} */ event) => {
      onKeyDown?.(event);
      if (!self(event) || off) return;
      if (multiple) {
        if (event.key !== ' ' || event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) return;
        event.preventDefault();
        choose(highlighted(), event);
        return;
      }
      const after = highlighted(before.current);
      if (after !== before.current) choose(after, event);
    },
    // A press on an option highlights it and selects it, or with multiple toggles it. The options take no focus,
    // so the press leaves focus on the listbox, or gives it to the listbox. A disabled listbox answers nothing.
    onClick: (/** @type {import('react').MouseEvent<HTMLDivElement>} */ event) => {
      onClick?.(event);
      if (off) return;
      const option = /** @type {HTMLElement | null} */ (event.target instanceof Element ? event.target.closest(OPTION) : null);
      if (!option || !mine().includes(option)) return;
      put(option, MARK, '');
      choose(option, event);
    },
    // Taking focus highlights the first selected option, or the first that is not disabled, when none is.
    onFocus: (/** @type {import('react').FocusEvent<HTMLDivElement>} */ event) => {
      onFocus?.(event);
      if (!self(event)) return;
      if (!highlighted()) {
        const usable = mine().filter((x) => !disabled(x));
        const first = usable.find((x) => x.hasAttribute('selected')) ?? usable[0];
        if (first) put(first, MARK, '');
      }
      mirror(true);
    },
    onBlur: (/** @type {import('react').FocusEvent<HTMLDivElement>} */ event) => {
      onBlur?.(event);
      if (self(event)) mirror(false);
    },
  }), createElement(ListboxContext.Provider, { value: { chosen, found: options.length > 0 } }, children),
  fields);
}
// Marked pure, so a bundle that does not use the component drops the module (X6).
export const Listbox = /* @__PURE__ */ Object.assign(ListboxRoot, { kitRole: role, displayName: 'Listbox' });
