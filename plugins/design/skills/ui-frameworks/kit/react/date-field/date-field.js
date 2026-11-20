// @ts-check
/**
 * date-field.js: a text field for a date, with a calendar to choose it from, for React (docs/specs/targets.md). A
 * plain module that calls createElement; no build step.
 *
 * The root is a <span> with data-ui="date-field" and no role, the box the popup is placed against. It holds the
 * author's children: the native text input marked data-part="input", which has no name, and the element marked
 * data-part="popup", which holds a calendar. Both are found in the DOM and never cloned or wrapped; the input must
 * be uncontrolled, since the field writes its text. The field renders, after them, a hidden input that carries name
 * and value (the author's input already holds the part name "input", so it carries none), and the toggle part, a
 * <span role="button" tabindex="-1"> at the end.
 *
 * As the Web Component does, the field gives the input the combobox role unless the author wrote one, with
 * aria-haspopup, aria-expanded, aria-controls, aria-required and aria-invalid, disables it while the field is
 * disabled and enables only an input it disabled; it gives the popup popover="manual", the dialog role and an id
 * where the author wrote none. It reads typed text when focus leaves the input and on Enter, with the Web
 * Component's own routines (date-field.text.js, D113), and writes the text of the value held. Its validity is the
 * author's input's: setCustomValidity with the Web Component's messages, so a submit is blocked and focuses the
 * input.
 *
 * The calendar belongs to another family. It is found as the Web Component finds it, from the grid inside the popup
 * (the nearest element around the grid with the group role or a custom element's tag), and the field writes `value`,
 * `min` and `max` on it after each render and whenever the subtree changes, and `value` again on opening, so the
 * calendar shows the month of the date held. A React calendar watches those attributes; a Web Component calendar
 * takes them as its own. The day the user chooses comes back from the calendar's change event, read from the day
 * it marks aria-selected. So the author passes value, min and max to the field only (J112).
 *
 * States (X2): open is the author attribute `open` on the root, written once the popup is showing, so the server
 * markup paints closed; invalid and disabled are author attributes; hover and focus-within are the root's own; read-
 * only is the input's own readonly, which the recipe reads through :has().
 *
 * The value is controlled (value with onChange) or uncontrolled (defaultValue); onInput(value, event) then
 * onChange(value, event) are called when the date changes, after a read or a choice. `open` opens and closes the
 * popup as the Web Component's attribute does when a script writes it; `defaultOpen` opens it once mounted. The
 * keys go through onKeyDown, and Enter or Space on the day already held through onKeyDownCapture, before the
 * calendar's own capture handler. `today` (yyyy-mm-dd) is injectable, for the century of a two-digit year.
 *
 * Rules: docs/specs/patterns.md, J109 to J113.
 */
import { createElement, useCallback, useEffect, useId, useLayoutEffect, useRef, useState } from 'react';
import { flushSync } from 'react-dom';
import { dismiss } from '../../behaviours/dismiss.js';
import { parseDate, serial, iso } from '../../components/calendar/calendar.dates.js';
import { format, read } from '../../components/date-field/date-field.text.js';

/**
 * @typedef {Omit<import('react').HTMLAttributes<HTMLSpanElement>, 'onChange' | 'onInput' | 'defaultValue'> & {
 *   value?: string, defaultValue?: string, name?: string, min?: string, max?: string,
 *   open?: boolean, defaultOpen?: boolean, required?: boolean, disabled?: boolean, today?: string,
 *   onInput?: (value: string, event: Event | import('react').SyntheticEvent) => void,
 *   onChange?: (value: string, event: Event | import('react').SyntheticEvent) => void,
 *   ref?: import('react').Ref<HTMLSpanElement>,
 * }} DateFieldProps
 */

/** The toggle's name. */
const TOGGLE = 'Choose a date';
/** What the browser shows for an invalid field: the Web Component's messages. */
const VALUE_MISSING = 'Please enter a date.';
const BAD_INPUT = 'Please enter a whole date.';
/** @param {string} min */
const BELOW = (min) => `Please enter a date on or after ${min}.`;
/** @param {string} max */
const ABOVE = (max) => `Please enter a date on or before ${max}.`;

/** Sets or removes an attribute, only when it differs. @param {Element} el @param {string} name @param {string | null} value */
const put = (el, name, value) => {
  if (el.getAttribute(name) === value) return;
  if (value === null) el.removeAttribute(name);
  else el.setAttribute(name, value);
};
/** The language of the text: the nearest lang, or the browser's. @param {Element} el */
const langOf = (el) => {
  const lang = el.closest('[lang]')?.getAttribute('lang') || navigator.language || 'en';
  try { return Intl.getCanonicalLocales(lang)[0] ?? 'en'; } catch { return navigator.language || 'en'; }
};
/** Today in the user's own time zone, as yyyy-mm-dd: read only when no `today` is given. */
const clock = () => { const now = new Date(); return iso({ y: now.getFullYear(), m: now.getMonth() + 1, d: now.getDate() }); };
/** Whether a disabled fieldset around the element disables it (F4): one whose first legend does not hold it. @param {Element} el */
const fenced = (el) => {
  for (let f = el.parentElement?.closest('fieldset'); f; f = f.parentElement?.closest('fieldset')) {
    if (!f.disabled) continue;
    const legend = [...f.children].find((c) => c.localName === 'legend');
    if (!legend || !legend.contains(el)) return true;
  }
  return false;
};

/** @param {DateFieldProps} props */
export function DateField({ value, defaultValue, name, min, max, open, defaultOpen = false, required = false, disabled = false, today, onInput, onChange, onKeyDown, onKeyDownCapture, onClick, onMouseDown, children, ref, ...rest }) {
  /** @type {import('react').RefObject<HTMLSpanElement | null>} */
  const root = useRef(null);
  /** @type {import('react').RefObject<HTMLInputElement | null>} */
  const field = useRef(null);
  const setRef = useCallback((/** @type {HTMLSpanElement | null} */ node) => {
    root.current = node;
    if (typeof ref === 'function') ref(node);
    else if (ref) ref.current = node;
  }, [ref]);
  const popupId = `${useId()}popup`;

  const first = useRef(defaultValue ?? '');
  const [own, setOwn] = useState(first.current);
  /** The popup is showing: the root's open attribute. */
  const [showing, setShowing] = useState(false);
  /** The invalid mark is shown on the root. */
  const [marked, setMarked] = useState(false);
  const [fieldsetOff, setFieldsetOff] = useState(false);
  const controlled = value !== undefined;
  const held = (controlled ? value : own) ?? '';
  const day = parseDate(held);
  const off = disabled || fieldsetOff;

  /** What the handlers read: the props and the state as they were last rendered, and the popup as it is now. */
  const latest = useRef({ held, controlled, off, min, max, required, today, onInput, onChange, showing });
  latest.current = { ...latest.current, held, controlled, off, min, max, required, today, onInput, onChange };
  /**
   * What the field holds between renders: the user has typed since the text was last written or read; the text is
   * not a date; the user is due to be told; the input marked aria-invalid; the input disabled; the input the text was
   * last written in; the message set; a write of the value must leave the text as typed.
   */
  const state = useRef({
    draft: false, bad: false, told: false, keep: false, message: '',
    marked: /** @type {HTMLInputElement | null} */ (null), disabledInput: /** @type {HTMLInputElement | null} */ (null), shown: /** @type {HTMLInputElement | null} */ (null),
  });

  /** The author's input. */
  const inputOf = () => {
    const el = root.current?.querySelector(':scope > [data-part="input"]');
    return el instanceof HTMLInputElement ? el : null;
  };
  /** @returns {HTMLElement | null} */
  const popupOf = () => root.current?.querySelector(':scope > [data-part="popup"]') ?? null;
  /** @returns {HTMLElement | null} */
  const toggleOf = () => root.current?.querySelector(':scope > [data-part="toggle"]') ?? null;
  /** The calendar in the popup: the nearest element around its grid, inside the popup, that is a group or a custom element. @returns {HTMLElement | null} */
  const calendarOf = () => {
    const popup = popupOf();
    const grid = popup?.querySelector('[role="grid"]');
    for (let el = grid?.parentElement ?? null; el && el !== popup; el = el.parentElement) if (el.getAttribute('role') === 'group' || el.localName.includes('-')) return el;
    return null;
  };
  /** The field cannot be changed: its input is read-only or disabled. A disabled field has disabled its input. */
  const locked = () => { const input = inputOf(); return !input || input.readOnly || input.disabled; };
  const lang = () => (root.current ? langOf(root.current) : 'en');

  /** Writes the text of a value into the input, and drops a draft and an unreadable text. @param {string} v */
  const show = (v) => {
    const input = inputOf();
    const s = state.current;
    s.shown = input;
    s.draft = false;
    s.bad = false;
    if (!input) return;
    const d = parseDate(v);
    const text = d ? format(lang(), d) : '';
    if (input.value !== text) input.value = text;
    if (input.ownerDocument.activeElement === input) {
      // The caret goes to the end of the rewritten text, and the field scrolls to show it (form.caret-after-rewrite).
      input.setSelectionRange(text.length, text.length);
      input.scrollLeft = input.scrollWidth;
    }
  };

  /** The message of the field's validity, or '' when it is valid. */
  const message = () => {
    const s = state.current, now = latest.current;
    if (s.bad) return BAD_INPUT;
    const d = parseDate(now.held);
    if (!d) return now.required ? VALUE_MISSING : '';
    const lo = parseDate(now.min), hi = parseDate(now.max);
    if (lo && serial(d) < serial(lo)) return BELOW(format(lang(), lo));
    if (hi && serial(d) > serial(hi)) return ABOVE(format(lang(), hi));
    return '';
  };

  /** Writes value, min and max on the calendar. On opening, the value is written again so the calendar shows its month. @param {boolean} [opening] */
  const hand = (opening = false) => {
    const calendar = calendarOf();
    if (!calendar) return;
    const d = parseDate(latest.current.held);
    const v = d ? iso(d) : null;
    if (opening && v !== null) calendar.setAttribute('value', v);
    else put(calendar, 'value', v);
    put(calendar, 'min', latest.current.min || null);
    put(calendar, 'max', latest.current.max || null);
  };

  /** Shows or hides the popup. A field that cannot be changed does not open (J113). @param {boolean} want @param {boolean} [flush] */
  const apply = (want, flush = true) => {
    const popup = popupOf();
    const yes = want && !!popup && !locked() && !latest.current.off;
    if (popup) {
      const now = popup.matches(':popover-open');
      // Read by dismiss and the toggle listener while the popover changes, so neither closes it a second time.
      latest.current.showing = yes;
      if (yes && !now) { hand(true); popup.showPopover(); }
      else if (!yes && now) popup.hidePopover();
    }
    latest.current.showing = yes;
    if (flush) flushSync(() => setShowing(yes));
    else setShowing(yes);
    return yes;
  };

  /** Brings the input's, the popup's, the toggle's and the calendar's attributes in step, and the validity and the mark. */
  const sync = () => {
    const input = inputOf(), popup = popupOf(), s = state.current, now = latest.current;
    if (popup) {
      if (!popup.hasAttribute('popover')) popup.setAttribute('popover', 'manual');
      if (!popup.hasAttribute('role')) popup.setAttribute('role', 'dialog');
      if (!popup.id) popup.id = popupId;
    }
    if (input) {
      // Disabled, by the prop or a fieldset: the input is disabled with it; only an input the field disabled is enabled.
      if (now.off && !input.disabled) { input.disabled = true; s.disabledInput = input; }
      else if (!now.off && s.disabledInput) { s.disabledInput.disabled = false; s.disabledInput = null; }
      if (!input.hasAttribute('role')) input.setAttribute('role', 'combobox');
      put(input, 'aria-haspopup', 'dialog');
      put(input, 'aria-expanded', String(now.showing));
      put(input, 'aria-controls', popup ? popup.id : null);
      put(input, 'aria-required', now.required ? 'true' : null);
      const text = message();
      if (s.message !== text || input.validationMessage !== text) { input.setCustomValidity(text); s.message = text; }
    }
    hand();
    // Marked while the user is due to be told (J111); only a mark the field wrote is taken off.
    const shown = !!input && (s.bad || (s.told && s.message !== ''));
    if (s.marked && s.marked !== input) put(s.marked, 'aria-invalid', null);
    if (input && (shown || s.marked === input)) put(input, 'aria-invalid', shown ? 'true' : null);
    s.marked = shown ? input : null;
    setMarked(shown);
  };

  /** Sets the value because the user asked for it, and tells listeners when it changed. @param {string} next @param {Event | import('react').SyntheticEvent} event @param {boolean} [keep] */
  const set = (next, event, keep = false) => {
    const before = latest.current.held;
    const s = state.current;
    s.told = true;
    if (!latest.current.controlled) { s.keep = keep; flushSync(() => setOwn(next)); s.keep = false; }
    latest.current.held = next;
    if (!keep) show(next);
    flushSync(sync);
    if (next === before) return;
    // In flushSync, so a page that holds the value has rendered it before the caller goes on.
    flushSync(() => {
      latest.current.onInput?.(next, event);
      latest.current.onChange?.(next, event);
    });
  };

  /** Reads what the user typed, when they typed (J110, J111). @param {Event | import('react').SyntheticEvent} event */
  const commit = (event) => {
    const input = inputOf(), s = state.current;
    if (!input || !s.draft || locked()) return;
    const year = parseDate(latest.current.today ?? clock())?.y ?? 2000;
    const v = read(lang(), input.value, year);
    s.draft = false;
    if (v === null) { s.bad = true; set('', event, true); }
    else set(v, event);
  };

  /** Moves focus to the calendar's Tab stop, which is the chosen day when there is one in the month shown. */
  const enter = () => /** @type {HTMLElement | null} */ (popupOf()?.querySelector('[role="grid"] [tabindex="0"]') ?? null)?.focus();

  /**
   * Opens the popup because the user asked for it: reads a draft first, then hands the calendar the date and moves
   * focus into it. A React calendar takes the attributes from its observer, a microtask later: focus follows then.
   * @param {Event | import('react').SyntheticEvent} event
   */
  const openUp = (event) => {
    commit(event);
    if (apply(true)) queueMicrotask(enter);
  };

  /** Closes the popup, and gives focus back to the input when it was in the popup. */
  const close = () => {
    const popup = popupOf();
    const inside = !!popup && popup.contains(popup.ownerDocument.activeElement);
    apply(false);
    if (inside) inputOf()?.focus();
  };

  /** Takes the day chosen in the calendar, closes the popup and gives focus back to the input. @param {string | null | undefined} v @param {Event | import('react').SyntheticEvent} event */
  const take = (v, event) => {
    if (!parseDate(v)) return;
    apply(false);
    inputOf()?.focus();
    set(/** @type {string} */ (v), event);
  };

  /** The day the calendar holds: the one it marks selected, or else the one it focused when it was chosen. @param {HTMLElement} calendar */
  const chosenIn = (calendar) => calendar.querySelector('[role="grid"] [aria-selected="true"]')?.getAttribute('data-date')
    ?? (calendar.contains(calendar.ownerDocument.activeElement) ? calendar.ownerDocument.activeElement?.getAttribute('data-date') : null);

  // After every render: the attributes, the validity and the mark take effect before paint.
  useLayoutEffect(() => { sync(); });

  // The text of the value held, whenever it changes; a write that keeps the text as typed leaves it.
  const heldDate = day ? iso(day) : '';
  useLayoutEffect(() => {
    // Unreadable text stays as typed while the value it emptied is held (J111).
    if (state.current.keep || (state.current.bad && heldDate === '')) return;
    const input = inputOf();
    const d = parseDate(heldDate);
    if (input && input.value === (d ? format(lang(), d) : '') && state.current.shown === input) return;
    show(heldDate);
  }, [heldDate]);

  // open from the author opens and closes the popup, as the Web Component's attribute does, without moving focus.
  useLayoutEffect(() => {
    if (open !== undefined) apply(open, false);
    else if (defaultOpen && !latest.current.showing) apply(true, false);
  }, [open]);

  useLayoutEffect(() => {
    const el = /** @type {HTMLSpanElement} */ (root.current);
    const quit = new AbortController();
    const listen = { signal: quit.signal };
    // A disabled fieldset around the field disables it (F4); its disabled attribute is watched, since no event tells.
    setFieldsetOff(fenced(el));
    const fence = new MutationObserver(() => { const f = fenced(el); flushSync(() => setFieldsetOff(f)); });
    for (let f = el.parentElement?.closest('fieldset'); f; f = f.parentElement?.closest('fieldset')) fence.observe(f, { attributes: true, attributeFilter: ['disabled'] });
    // The calendar's own events stop here: the field's say when the date changed. A day chosen comes from its change.
    for (const type of ['input', 'change']) {
      el.addEventListener(type, (event) => {
        const calendar = calendarOf();
        if (calendar && event.target === calendar) {
          event.stopPropagation();
          if (type === 'change' && latest.current.showing) take(chosenIn(calendar), event);
          return;
        }
        if (type === 'input' && event.target === inputOf()) state.current.draft = true;
      }, listen);
    }
    // Focus that leaves the input reads what was typed.
    el.addEventListener('focusout', (event) => { if (event.target === inputOf()) commit(event); }, listen);
    // A submit attempt tells the user. invalid does not bubble: it reaches the root in the capture phase.
    el.addEventListener('invalid', (event) => { if (event.target === inputOf()) { state.current.told = true; flushSync(sync); } }, { ...listen, capture: true });
    // Something else hid the popup, such as a script calling hidePopover(): the state follows.
    el.addEventListener('toggle', (event) => {
      const popup = popupOf();
      if (popup && event.target === popup && latest.current.showing && !popup.matches(':popover-open')) apply(false);
    }, { ...listen, capture: true });
    // A reset puts the value back after the event: an uncontrolled one to its first, and its text; the user is no longer due to be told.
    el.ownerDocument.addEventListener('reset', (event) => {
      if (!(event.target instanceof HTMLFormElement) || !event.target.contains(el)) return;
      setTimeout(() => {
        if (!root.current?.isConnected) return;
        state.current.told = false;
        if (!latest.current.controlled) flushSync(() => setOwn(first.current));
        latest.current.held = latest.current.controlled ? latest.current.held : first.current;
        show(latest.current.held);
        flushSync(sync);
      });
    }, listen);
    // An input or a popup that arrives or is replaced, a calendar that appears later, readonly or disabled written on the input.
    const observer = new MutationObserver(() => {
      if (inputOf() !== state.current.shown) show(latest.current.held);
      if (latest.current.showing && locked()) apply(false);
      flushSync(sync);
    });
    observer.observe(el, { childList: true, subtree: true, attributes: true, attributeFilter: ['data-part', 'role', 'readonly', 'disabled', 'id', 'popover'] });
    // Escape, a press outside and focus that leaves close the popup. Escape goes no further (overlay.escape-innermost).
    const stop = dismiss(el, {
      active: () => latest.current.showing,
      onDismiss: (reason) => {
        if (reason === 'escape') close();
        else apply(false);
      },
    });
    return () => { quit.abort(); fence.disconnect(); observer.disconnect(); stop(); };
  }, []);

  // Disabled or read-only while open: the popup closes (J113).
  useLayoutEffect(() => { if (latest.current.showing && (off || locked())) apply(false, false); }, [off]);

  useEffect(() => {
    const id = requestAnimationFrame(() => root.current?.setAttribute('data-ready', ''));
    return () => cancelAnimationFrame(id);
  }, []);

  /** @param {import('react').KeyboardEvent<HTMLSpanElement>} event */
  const plain = (event) => !event.altKey && !event.ctrlKey && !event.metaKey && !event.shiftKey;

  /** The input's keys, and Alt+ArrowDown and Alt+ArrowUp (J110 to J112). @param {import('react').KeyboardEvent<HTMLSpanElement>} event */
  const keyDown = (event) => {
    onKeyDown?.(event);
    const input = inputOf();
    if (event.altKey && !event.ctrlKey && !event.metaKey && (event.key === 'ArrowDown' || event.key === 'ArrowUp')) {
      if (event.key === 'ArrowDown' && event.target === input && !latest.current.showing) {
        event.preventDefault();
        openUp(event);
      } else if (event.key === 'ArrowUp' && latest.current.showing) {
        event.preventDefault();
        close();
      }
      return;
    }
    if (event.target !== input || !plain(event)) return;
    // Enter keeps its default, so the form is submitted with the date just read.
    if (event.key === 'Enter') commit(event);
    else if (event.key === 'Escape' && !latest.current.showing && state.current.draft) {
      event.preventDefault();
      event.stopPropagation();
      show(latest.current.held);
      flushSync(sync);
    }
  };

  /**
   * Enter or Space on the day already held: the calendar would do nothing the field could hear, so the field takes
   * that day itself, before the calendar's own capture handler sees the key.
   * @param {import('react').KeyboardEvent<HTMLSpanElement>} event
   */
  const keyDownCapture = (event) => {
    onKeyDownCapture?.(event);
    if ((event.key !== 'Enter' && event.key !== ' ') || !plain(event) || !latest.current.showing) return;
    const cell = event.target instanceof Element ? event.target.closest('[role="gridcell"]') : null;
    const calendar = calendarOf();
    if (!cell || !calendar?.contains(cell) || cell.getAttribute('aria-selected') !== 'true') return;
    // The calendar sees the key after this, on a day of a popup already hidden: it chooses the same day and its
    // focus goes nowhere, so the key is not stopped.
    take(cell.getAttribute('data-date'), event);
  };

  /** The toggle opens and closes; a press on the day already held closes the popup with it. @param {import('react').MouseEvent<HTMLSpanElement>} event */
  const click = (event) => {
    onClick?.(event);
    if (!(event.target instanceof Element)) return;
    const toggle = toggleOf();
    if (toggle && toggle.contains(event.target)) {
      if (latest.current.showing) close();
      else openUp(event);
      return;
    }
    const cell = event.target.closest('[role="gridcell"]');
    const calendar = calendarOf();
    if (latest.current.showing && cell && calendar?.contains(cell) && cell.getAttribute('aria-selected') === 'true') take(cell.getAttribute('data-date'), event);
  };

  /** A press on the field outside the input and the popup moves no focus to the press, and puts it in the input. @param {import('react').MouseEvent<HTMLSpanElement>} event */
  const mouseDown = (event) => {
    onMouseDown?.(event);
    const input = inputOf();
    const target = event.target instanceof Node ? event.target : null;
    if (!input || !target || target === input || popupOf()?.contains(target)) return;
    event.preventDefault();
    if (!input.disabled && !toggleOf()?.contains(target) && input.ownerDocument.activeElement !== input) input.focus();
  };

  const hidden = createElement('input', { type: 'hidden', ref: field, name, value: heldDate, disabled: off || heldDate === '' });
  const toggle = createElement('span', { 'data-part': 'toggle', role: 'button', tabIndex: -1, 'aria-label': TOGGLE, 'aria-disabled': off ? 'true' : undefined });
  return createElement('span', /** @type {any} */ ({
    ...rest, ref: setRef, 'data-ui': 'date-field',
    // open and disabled are boolean attributes to React: true renders them empty, as the conditions select.
    open: showing || undefined,
    disabled: off || undefined,
    // An invalid the author wrote stays as written (J111).
    invalid: marked ? '' : /** @type {any} */ (rest).invalid,
    onKeyDown: keyDown,
    onKeyDownCapture: keyDownCapture,
    onClick: click,
    onMouseDown: mouseDown,
  }), children, hidden, toggle);
}
