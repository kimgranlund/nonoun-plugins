// @ts-check
/**
 * calendar.js: one month of days in a grid, for React (docs/specs/targets.md). A plain module that calls
 * createElement; no build step.
 *
 * The root is a <div> with the group role, unless the author gives another, so the author's name is announced. It
 * renders everything the Web Component creates: a header part with a native button for the previous month, the
 * month's name as a polite live region and a native button for the next month; a grid part, a <table> with the grid
 * role named by the title, whose head row names the weekdays and whose body rows are the weeks; one <td> per day with
 * the gridcell role and data-part="day". The days of the neighbouring months that fill the first and the last week
 * are marked data-outside. A div is no form control, so a hidden input marked data-part="input" carries name and
 * value, and the form submits it only while a date between min and max is chosen.
 *
 * The date arithmetic is the Web Component's own, from calendar.dates.js (D113): plain year, month and day numbers,
 * so no time zone can shift a day. The language is the nearest lang once the calendar is in the page; before that,
 * on the server and in the first render that hydrates it, it is the root's own lang prop, or English. Today is the
 * `today` prop (yyyy-mm-dd) when given, otherwise the user's clock: a test or a server injects it.
 *
 * States (X2): the days carry the ARIA the conditions select (aria-selected, aria-current="date", aria-disabled),
 * the root aria-disabled while disabled, by the prop or a fieldset; hover, focus-visible and active are the parts'
 * own pseudo-classes. rovingFocus keeps the days of the month one Tab stop, and the stop is written after every
 * render as well, so it holds in the same task as a draw (J105).
 *
 * The calendar's keys go through React's onKeyDownCapture on the root. React's capture listener sits on the React
 * root's container, so it runs before rovingFocus's listener on this root, which passes over a key whose default is
 * already prevented (B8): a key the calendar acts on is the calendar's alone, and still reaches the page.
 *
 * The value is controlled (value with onChange) or uncontrolled (defaultValue). onInput(value, event) and then
 * onChange(value, event) are called when the user chooses another day; input and change are then dispatched,
 * bubbling, from the root, so a component of another family, such as a date field, hears the choice in the DOM as it
 * hears the Web Component's. Such a component hands the calendar value, min and max as attributes written on its
 * root, as it does the Web Component's: the calendar watches them. A value written there is taken as a script's
 * value is (the uncontrolled value, and its month shown again); a min or max written there wins over the prop while
 * it is present. The calendar renders none of the three on its root.
 *
 * Rules: docs/specs/patterns.md, J103 to J107.
 */
import { createElement, useCallback, useEffect, useId, useLayoutEffect, useMemo, useRef, useState } from 'react';
import { flushSync } from 'react-dom';
import { rovingFocus } from '../../behaviours/roving-focus.js';
import { daysIn, serial, fromSerial, weekday, iso, parseDate, parseMonth, addMonths, weekStart, format, FIRST, LAST } from '../../components/calendar/calendar.dates.js';
import { role } from '../../components/calendar/calendar.props.js';

/**
 * @typedef {import('../../components/calendar/calendar.dates.js').Day} Day
 * @typedef {{ y: number, m: number }} Month
 * @typedef {Omit<import('react').HTMLAttributes<HTMLDivElement>, 'onChange' | 'onInput' | 'defaultValue'> & {
 *   value?: string, defaultValue?: string, name?: string, min?: string, max?: string, month?: string,
 *   required?: boolean, disabled?: boolean, today?: string,
 *   onInput?: (value: string, event: import('react').SyntheticEvent) => void,
 *   onChange?: (value: string, event: import('react').SyntheticEvent) => void,
 *   ref?: import('react').Ref<HTMLDivElement>,
 * }} CalendarProps
 */

/** The names of the two buttons. */
const NAMES = { previous: 'Previous month', next: 'Next month' };
const DAY = '[data-part="day"]';

/** Sets or removes an attribute, only when it differs. @param {Element} el @param {string} name @param {string | null} value */
const put = (el, name, value) => {
  if (el.getAttribute(name) === value) return;
  if (value === null) el.removeAttribute(name);
  else el.setAttribute(name, value);
};
/** A language as Intl reads it, or English. @param {string | null | undefined} lang @param {string} fallback */
const canonical = (lang, fallback) => {
  try { return Intl.getCanonicalLocales(lang || fallback)[0] ?? 'en'; } catch { return fallback || 'en'; }
};
/** The language of the names: the nearest lang, or the browser's where that is empty, which HTML reads as unknown. @param {Element} el */
const langOf = (el) => canonical(el.closest('[lang]')?.getAttribute('lang') || navigator.language, navigator.language || 'en');
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
/** The grid of a calendar root. @param {Element | null} el @returns {HTMLTableElement | null} */
const gridOf = (el) => /** @type {HTMLTableElement | null} */ (el?.querySelector(':scope > [data-part="grid"]') ?? null);
/** Every cell of the grid's body. @param {Element | null} el @returns {HTMLElement[]} */
const cellsOf = (el) => [.../** @type {NodeListOf<HTMLElement>} */ (gridOf(el)?.querySelectorAll(`:scope > tbody > tr > ${DAY}`) ?? [])];
/** The days of the month shown, which take focus, in order. @param {Element | null} el */
const daysOf = (el) => cellsOf(el).filter((cell) => !cell.hasAttribute('data-outside'));

/** @param {CalendarProps} props */
function CalendarRoot({ value, defaultValue, name, min, max, month, required = false, disabled = false, today, onInput, onChange, onKeyDownCapture, onClick, children, ref, ...rest }) {
  /** @type {import('react').RefObject<HTMLDivElement | null>} */
  const root = useRef(null);
  /** @type {import('react').RefObject<HTMLInputElement | null>} */
  const field = useRef(null);
  const setRef = useCallback((/** @type {HTMLDivElement | null} */ node) => {
    root.current = node;
    if (typeof ref === 'function') ref(node);
    else if (ref) ref.current = node;
  }, [ref]);
  const titleId = `${useId()}title`;

  const first = useRef(defaultValue ?? '');
  const [own, setOwn] = useState(first.current);
  /** @type {[Month | null, (m: Month | null | ((was: Month | null) => Month | null)) => void]} The month the user moved to; null shows `month`, the value's or today's. */
  const [moved, setMoved] = useState(/** @type {Month | null} */ (null));
  /** min and max written on the root by a component of another family, such as a date field. */
  const [written, setWritten] = useState(/** @type {{ min: string | null, max: string | null }} */ ({ min: null, max: null }));
  const [mounted, setMounted] = useState(false);
  const [fieldsetOff, setFieldsetOff] = useState(false);
  // A value or a month from the author shows its month again, as a script's does on the Web Component.
  // A value the user has just chosen, when the page writes it back, is no new value: the month shown stays.
  const [given, setGiven] = useState({ value, month });
  const chose = useRef(/** @type {string | null} */ (null));
  const fresh = (given.value !== value && value !== chose.current) || given.month !== month;
  if (given.value !== value && !fresh) setGiven({ value, month });
  if (fresh) { setGiven({ value, month }); setMoved(null); }

  const controlled = value !== undefined;
  const held = (controlled ? value : own) ?? '';
  const off = disabled || fieldsetOff;
  const lo = parseDate(written.min ?? min), hi = parseDate(written.max ?? max);
  const from = Math.max(FIRST, lo ? serial(lo) : FIRST), to = Math.min(LAST, hi ? serial(hi) : LAST);
  const day = parseDate(held);
  const chosen = day && serial(day) >= from && serial(day) <= to ? iso(day) : null;
  const now = today ?? clock();
  // The page's language once mounted; before that the same on the server and in the render that hydrates.
  const lang = mounted && root.current ? langOf(root.current) : canonical(/** @type {any} */ (rest).lang, 'en');
  const start = weekStart(lang);
  const shown = (fresh ? null : moved) ?? parseMonth(month) ?? day ?? parseDate(now) ?? { y: 1970, m: 1 };

  /** What the handlers read: the state as it was last rendered. */
  const latest = useRef({ held, controlled, off, from, to, chosen, now, shown, start, onInput, onChange });
  latest.current = { held, controlled, off, from, to, chosen, now, shown, start, onInput, onChange };

  // The day focus is on when this render starts: a grid drawn again gives focus back to the same day.
  const refocus = useRef(/** @type {string | null} */ (null));
  if (root.current) {
    const active = root.current.ownerDocument.activeElement;
    refocus.current = active && gridOf(root.current)?.contains(active) ? active.getAttribute('data-date') : null;
  }

  // What does not change while the month and the language stay: the weeks, the numbers and the names.
  const sheet = useMemo(() => {
    const number = new Intl.NumberFormat(lang, { useGrouping: false });
    // 2023-01-01 was a Sunday.
    const heads = Array.from({ length: 7 }, (_, n) => ({
      abbr: format(lang, { weekday: 'long' }, 2023, 1, 1 + ((start + n) % 7)),
      text: format(lang, { weekday: 'short' }, 2023, 1, 1 + ((start + n) % 7)),
    }));
    const one = serial({ y: shown.y, m: shown.m, d: 1 });
    const begin = one - ((weekday(one) - start + 7) % 7);
    const weeks = Math.ceil((one - begin + daysIn(shown.y, shown.m)) / 7);
    const rows = Array.from({ length: weeks }, (_, w) => Array.from({ length: 7 }, (__, n) => {
      const at = begin + w * 7 + n;
      const d = fromSerial(at);
      const inside = at >= FIRST && at <= LAST;
      return {
        at, text: number.format(d.d), outside: d.m !== shown.m || d.y !== shown.y,
        date: inside ? iso(d) : null, label: inside ? format(lang, { dateStyle: 'full' }, d.y, d.m, d.d) : null,
      };
    }));
    return { heads, rows, title: format(lang, { month: 'long', year: 'numeric' }, shown.y, shown.m, 1) };
  }, [lang, start, shown.y, shown.m]);

  /** The cell of a day among the days of the month shown. @param {string | null} date */
  const cellOf = (date) => (date === null ? null : daysOf(root.current).find((cell) => cell.getAttribute('data-date') === date) ?? null);
  /** The day that is the Tab stop while focus is outside the grid: the chosen day, or today, or the first day shown. */
  const preferred = () => cellOf(latest.current.chosen) || cellOf(latest.current.now) || daysOf(root.current)[0] || null;

  // The page's language and a fieldset around it are known once the calendar is in the page.
  useLayoutEffect(() => {
    const el = /** @type {HTMLDivElement} */ (root.current);
    setMounted(true);
    setFieldsetOff(fenced(el));
    const observer = new MutationObserver(() => { const f = fenced(el); flushSync(() => setFieldsetOff(f)); });
    for (let f = el.parentElement?.closest('fieldset'); f; f = f.parentElement?.closest('fieldset')) observer.observe(f, { attributes: true, attributeFilter: ['disabled'] });
    return () => observer.disconnect();
  }, []);

  // value, min and max written on the root by a component of another family (see the header).
  useLayoutEffect(() => {
    const el = /** @type {HTMLDivElement} */ (root.current);
    const read = () => ({ min: el.getAttribute('min'), max: el.getAttribute('max') });
    const observer = new MutationObserver((records) => {
      const valued = records.some((r) => r.attributeName === 'value');
      flushSync(() => {
        setWritten((was) => { const now = read(); return now.min === was.min && now.max === was.max ? was : now; });
        if (!valued) return;
        if (!latest.current.controlled) setOwn(el.getAttribute('value') ?? '');
        setMoved(null);
      });
    });
    observer.observe(el, { attributes: true, attributeFilter: ['value', 'min', 'max'] });
    if (el.hasAttribute('min') || el.hasAttribute('max')) setWritten(read());
    if (el.hasAttribute('value') && !latest.current.controlled) setOwn(el.getAttribute('value') ?? '');
    return () => observer.disconnect();
  }, []);

  useLayoutEffect(() => {
    const el = /** @type {HTMLDivElement} */ (root.current);
    return rovingFocus(el, {
      items: () => daysOf(el),
      current: () => preferred(),
      skip: () => latest.current.off,
    });
  }, []);

  // After every render, in the same task: one day of the month is the Tab stop, as rovingFocus will write it, and a
  // grid drawn again gives focus back to the day that had it (J105). A day of a neighbouring month takes no focus.
  useLayoutEffect(() => {
    const el = /** @type {HTMLDivElement} */ (root.current);
    const days = daysOf(el);
    const active = el.ownerDocument.activeElement;
    const back = refocus.current && !(active && gridOf(el)?.contains(active)) ? cellOf(refocus.current) : null;
    const stop = latest.current.off ? null : back || days.find((cell) => cell === active) || preferred();
    for (const cell of cellsOf(el)) put(cell, 'tabindex', stop === null || !days.includes(cell) ? null : cell === stop ? '0' : '-1');
    back?.focus();
    refocus.current = null;
  });

  // A form reset puts an uncontrolled value back to its first one, and shows its month (F6).
  useLayoutEffect(() => {
    const form = /** @type {HTMLInputElement} */ (field.current).form;
    if (!form) return;
    const stop = new AbortController();
    form.addEventListener('reset', () => setTimeout(() => flushSync(() => { setOwn(first.current); setMoved(null); })), { signal: stop.signal });
    return () => stop.abort();
  }, []);

  useEffect(() => {
    const id = requestAnimationFrame(() => root.current?.setAttribute('data-ready', ''));
    return () => cancelAnimationFrame(id);
  }, []);

  /** Shows a day's month and moves focus to the day. @param {Day} d */
  const focusDay = (d) => {
    flushSync(() => setMoved((was) => (was && was.y === d.y && was.m === d.m ? was : { y: d.y, m: d.m })));
    cellOf(iso(d))?.focus();
  };

  /** Chooses a day because the user asked for it, then tells listeners, who find the grid already written. @param {Day} d @param {import('react').SyntheticEvent} event */
  const choose = (d, event) => {
    const n = serial(d), now = latest.current;
    if (n < now.from || n > now.to) { focusDay(d); return; }
    const next = iso(d);
    const changed = next !== now.held;
    if (!now.controlled) flushSync(() => setOwn(next));
    focusDay(d);
    if (!changed) return;
    chose.current = next;
    // In flushSync, so a page that holds the value has rendered it when the events below are dispatched.
    flushSync(() => {
      now.onInput?.(next, event);
      now.onChange?.(next, event);
    });
    chose.current = null;
    const el = /** @type {HTMLDivElement} */ (root.current);
    el.dispatchEvent(new Event('input', { bubbles: true }));
    el.dispatchEvent(new Event('change', { bubbles: true }));
  };

  /** The calendar's keys on a day (date.grid-keys). @param {import('react').KeyboardEvent<HTMLDivElement>} event */
  const keyDown = (event) => {
    onKeyDownCapture?.(event);
    const cell = /** @type {HTMLElement} */ (event.target);
    // WebKit keeps focus on a day that loses its tabindex when the calendar is disabled: its keys stop here.
    if (event.altKey || event.ctrlKey || event.metaKey || latest.current.off || !daysOf(root.current).includes(cell)) return;
    const d = parseDate(cell.getAttribute('data-date'));
    if (!d) return;
    const paging = event.key === 'PageUp' || event.key === 'PageDown';
    if (event.shiftKey && !paging) return;
    const n = serial(d);
    const forward = getComputedStyle(/** @type {HTMLDivElement} */ (root.current)).direction === 'rtl' ? -1 : 1;
    const back = (weekday(n) - latest.current.start + 7) % 7;
    /** @type {number | null} */
    let target = null;
    if (event.key === 'ArrowRight') target = n + forward;
    else if (event.key === 'ArrowLeft') target = n - forward;
    else if (event.key === 'ArrowDown') target = n + 7;
    else if (event.key === 'ArrowUp') target = n - 7;
    else if (event.key === 'Home') target = n - back;
    else if (event.key === 'End') target = n - back + 6;
    else if (paging) {
      const next = addMonths(d, (event.shiftKey ? 12 : 1) * (event.key === 'PageUp' ? -1 : 1));
      target = next ? serial(next) : n;
    } else if (event.key !== 'Enter' && event.key !== ' ') return;
    // rovingFocus would walk the days as a list; it passes over a key whose default is prevented (B8).
    event.preventDefault();
    if (target === null) { choose(d, event); return; }
    focusDay(fromSerial(target < FIRST || target > LAST ? n : target));
  };

  /** A press on a day chooses it; on a button, shows the month before or after. @param {import('react').MouseEvent<HTMLDivElement>} event */
  const click = (event) => {
    onClick?.(event);
    const el = root.current;
    if (latest.current.off || !el || !(event.target instanceof Element)) return;
    const button = event.target.closest('[data-part="previous"], [data-part="next"]');
    if (button && button.parentElement?.parentElement === el) {
      // At 0001 or 9999 the button is aria-disabled, and addMonths stops there.
      const next = addMonths({ ...latest.current.shown, d: 1 }, button.getAttribute('data-part') === 'next' ? 1 : -1);
      if (next) flushSync(() => setMoved({ y: next.y, m: next.m }));
    }
    // A button holds no day, so a press on one chooses nothing.
    const cell = event.target.closest(DAY);
    const d = cell && gridOf(el)?.contains(cell) ? parseDate(cell.getAttribute('data-date')) : null;
    if (d) choose(d, event);
  };

  const header = createElement('div', { 'data-part': 'header' },
    createElement('button', { type: 'button', 'data-part': 'previous', 'aria-label': NAMES.previous, 'aria-disabled': shown.y === 1 && shown.m === 1 ? 'true' : undefined, disabled: off }),
    createElement('span', { 'data-part': 'title', id: titleId, 'aria-live': 'polite' }, sheet.title),
    createElement('button', { type: 'button', 'data-part': 'next', 'aria-label': NAMES.next, 'aria-disabled': shown.y === 9999 && shown.m === 12 ? 'true' : undefined, disabled: off }));
  const grid = createElement('table', {
    'data-part': 'grid', role: 'grid', 'aria-labelledby': titleId,
    'aria-required': required ? 'true' : undefined, 'aria-disabled': off ? 'true' : undefined,
  },
  createElement('thead', null, createElement('tr', null, sheet.heads.map((h, n) => createElement('th', { key: n, scope: 'col', abbr: h.abbr }, h.text)))),
  createElement('tbody', null, sheet.rows.map((row, w) => createElement('tr', { key: w }, row.map((c) => {
    const d = parseDate(c.date);
    return createElement('td', {
      key: c.date ?? `at${c.at}`, role: 'gridcell', 'data-part': 'day',
      'data-outside': c.outside ? '' : undefined, 'data-date': c.date ?? undefined, 'aria-label': c.label ?? undefined,
      'aria-selected': c.date !== null && c.date === chosen ? 'true' : undefined,
      'aria-current': c.date !== null && c.date === now ? 'date' : undefined,
      'aria-disabled': d && serial(d) >= from && serial(d) <= to ? undefined : 'true',
    }, c.text);
  })))));
  const hidden = createElement('input', { type: 'hidden', 'data-part': 'input', ref: field, name, value: chosen ?? '', disabled: off || chosen === null });

  return createElement('div', /** @type {any} */ ({
    role, ...rest, ref: setRef, 'data-ui': 'calendar',
    'aria-disabled': off ? 'true' : undefined,
    onKeyDownCapture: keyDown,
    onClick: click,
  }), header, grid, hidden);
}
// Marked pure, so a bundle that does not use the component drops the module (X6).
export const Calendar = /* @__PURE__ */ Object.assign(CalendarRoot, { kitRole: role, displayName: 'Calendar' });
