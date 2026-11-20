// @ts-check
/**
 * calendar.class.js: the class of a calendar. Importing it defines no element; calendar.js does that.
 *
 * The calendar creates everything inside itself: a header part with a native button for the previous month, the
 * month's name as a polite live region and a native button for the next month, and a grid part, a table with the
 * grid role whose head row names the weekdays and whose body rows are the weeks. Each day is a cell with the
 * gridcell role and `data-part="day"` that holds the day number and takes focus itself. The days of the
 * neighbouring months that fill the first and the last week are shown, marked `data-outside`; they take no focus,
 * and a press on one chooses it and shows its month.
 *
 * Dates are plain year, month and day numbers of the proleptic Gregorian calendar (date.gregorian), counted as days
 * since 1970-01-01 with integer arithmetic only, so no time zone or clock change can shift one (testing.time-zones).
 * Names are formatted with Intl in the Gregorian calendar and in UTC, from a Date set in UTC. The language is the
 * nearest `lang`, or else the browser's; the first day of the week is the engine's week information for it, or a
 * table of regions where the engine has none (date.week-start). Today is read through `static today()` only, so a
 * page or a test can inject it (testing.inject-now).
 *
 * rovingFocus keeps the days of the month shown one Tab stop: the day focus is on while it is inside the grid, and
 * otherwise the chosen day, or today, or the first day of the month (J105). The behaviour's own arrow keys walk the
 * days as a list; the calendar's keys are a calendar's (date.grid-keys) and are handled before it, which is why
 * the calendar stops the propagation of a key it acts on. Focus that moves out of the month shown shows the month
 * it lands in. Navigation stops at 0001-01-01 and 9999-12-31 (date.bounds).
 *
 * It is a form control: it submits its name with the value when the value is a date between `min` and `max`, and
 * nothing otherwise. Everything is written by #update(), synchronously, from changed() and from the user's input,
 * so a script sees the result in the same task.
 *
 * Rules: docs/specs/patterns.md, J103 to J107; docs/specs/foundation.md, F1 to F7.
 */
import { setAttr } from '../../foundation/element.js';
import { UIFormElement } from '../../foundation/form.js';
import { rovingFocus } from '../../behaviours/roving-focus.js';
import { props, parts, role, tabindex, resets } from './calendar.props.js';
import { leap, daysIn, serial, fromSerial, weekday, iso, parseDate, parseMonth, addMonths, weekStart, format, FIRST, LAST } from './calendar.dates.js';

/** The names of the two buttons. */
const NAMES = { previous: 'Previous month', next: 'Next month' };
/** Shown by the browser when a required calendar has no date chosen. */
const VALUE_MISSING = 'Please choose a date';
/** The flags of a ValidityState that setValidity takes. */
const FLAGS = /** @type {const} */ (['valueMissing', 'typeMismatch', 'patternMismatch', 'tooLong', 'tooShort', 'rangeUnderflow', 'rangeOverflow', 'stepMismatch', 'badInput', 'customError']);

/** @typedef {import('./calendar.dates.js').Day} Day */


/**
 * Sets or removes an attribute, only when it differs. The observers then see nothing when nothing changes.
 * @param {Element} el @param {string} name @param {string | null} value
 */
const put = (el, name, value) => {
  if (el.getAttribute(name) === value) return;
  if (value === null) el.removeAttribute(name);
  else el.setAttribute(name, value);
};

let count = 0;

export class UICalendar extends UIFormElement {
  static props = props;
  static parts = parts;
  static role = role;
  static tabindex = tabindex;
  static resets = resets;
  /**
   * The pure date routines, for the date field and for a test that runs them under several time zones
   * (testing.time-zones). A static member, not a second export: a class module exports its class alone (R1).
   */
  static dates = { leap, daysIn, serial, fromSerial, weekday, iso, parseDate, parseMonth, addMonths, weekStart, format, FIRST, LAST };

  /**
   * Today, as yyyy-mm-dd, in the user's own time zone: the one place the calendar reads the clock. A page or a test
   * replaces it on a subclass to inject today (testing.inject-now).
   * @returns {string}
   */
  static today() {
    const now = new Date();
    return iso({ y: now.getFullYear(), m: now.getMonth() + 1, d: now.getDate() });
  }

  /** @type {{ y: number, m: number } | null} The month the user moved to; null shows `month`, the value's or today's. */
  #moved = null;
  /** What the grid was last drawn for: the language, the first weekday and the month. */
  #drawn = '';
  /** The id of the title, which names the grid. */
  #id = `calendar-${++count}-title`;

  /** The grid part, when it is a table. */
  #table() {
    const table = this.ensurePart('grid');
    return table instanceof HTMLTableElement ? table : null;
  }

  /** One of the header's own elements. @param {string} name */
  #own(name) {
    return /** @type {HTMLElement | null} */ (this.ensurePart('header')?.querySelector(`:scope > [data-part="${name}"]`) ?? null);
  }

  /** The days of the month shown, which take focus, in order. @returns {HTMLElement[]} */
  #days() {
    const body = this.#table()?.tBodies[0];
    return body ? [...body.rows].flatMap((row) => [...row.cells]).filter((cell) => !cell.hasAttribute('data-outside')) : [];
  }

  /** The cell of a day among the days of the month shown. @param {string} date */
  #cell(date) { return this.#days().find((cell) => cell.getAttribute('data-date') === date) ?? null; }

  /** The language of the names: the nearest lang, or the browser's where that is empty, which HTML reads as unknown. */
  #lang() {
    const lang = this.closest('[lang]')?.getAttribute('lang') || navigator.language || 'en';
    try { return Intl.getCanonicalLocales(lang)[0] ?? 'en'; } catch { return navigator.language || 'en'; }
  }

  /** The chosen day: the value, when it is a date between min and max. */
  #chosen() {
    const day = parseDate(/** @type {any} */ (this).value);
    return day && this.#allowed(serial(day)) ? day : null;
  }

  /** Whether a day, as a count, may be chosen: between min and max, and inside the years 0001 to 9999. @param {number} n */
  #allowed(n) {
    const self = /** @type {any} */ (this);
    const min = parseDate(self.min), max = parseDate(self.max);
    return n >= Math.max(FIRST, min ? serial(min) : FIRST) && n <= Math.min(LAST, max ? serial(max) : LAST);
  }

  /** The month shown: the one the user moved to, or `month`, or the value's, or today's. */
  #shown() {
    const self = /** @type {any} */ (this);
    const value = parseDate(self.value);
    const today = parseDate(/** @type {typeof UICalendar} */ (this.constructor).today());
    return this.#moved ?? parseMonth(self.month) ?? value ?? today ?? { y: 1970, m: 1 };
  }

  /** The day that is the Tab stop while focus is outside the grid: the chosen day, or today, or the first day shown. */
  #preferred() {
    const chosen = this.#chosen();
    const today = /** @type {typeof UICalendar} */ (this.constructor).today();
    return (chosen && this.#cell(iso(chosen))) || this.#cell(today) || this.#days()[0] || null;
  }

  /** Creates the header's buttons and title when they are missing, in their order. */
  #header() {
    const header = this.ensurePart('header');
    if (!header) return;
    for (const [name, tag] of [['previous', 'button'], ['title', 'span'], ['next', 'button']]) {
      let el = this.#own(name);
      if (!el) {
        el = document.createElement(tag);
        el.setAttribute('data-part', name);
        if (el instanceof HTMLButtonElement) {
          el.type = 'button';
          el.setAttribute('aria-label', NAMES[/** @type {'previous' | 'next'} */ (name)]);
        } else {
          el.id = this.#id;
          el.setAttribute('aria-live', 'polite');
        }
      }
      header.append(el);
    }
  }

  /** Draws the head row and the weeks of a month. @param {HTMLTableElement} table @param {string} lang @param {number} start @param {{ y: number, m: number }} month */
  #draw(table, lang, start, { y, m }) {
    const active = this.ownerDocument.activeElement;
    const focused = active && table.contains(active) ? active.getAttribute('data-date') : null;
    const number = new Intl.NumberFormat(lang, { useGrouping: false });
    const head = document.createElement('thead');
    const names = head.insertRow();
    for (let n = 0; n < 7; n++) {
      // 2023-01-01 was a Sunday.
      const th = document.createElement('th');
      th.scope = 'col';
      th.abbr = format(lang, { weekday: 'long' }, 2023, 1, 1 + ((start + n) % 7));
      th.textContent = format(lang, { weekday: 'short' }, 2023, 1, 1 + ((start + n) % 7));
      names.append(th);
    }
    const body = document.createElement('tbody');
    const first = serial({ y, m, d: 1 });
    const from = first - ((weekday(first) - start + 7) % 7);
    const weeks = Math.ceil((first - from + daysIn(y, m)) / 7);
    for (let w = 0; w < weeks; w++) {
      const row = body.insertRow();
      for (let n = 0; n < 7; n++) {
        const at = from + w * 7 + n;
        const day = fromSerial(at);
        const cell = row.insertCell();
        cell.setAttribute('role', 'gridcell');
        cell.setAttribute('data-part', 'day');
        cell.textContent = number.format(day.d);
        if (day.m !== m || day.y !== y) cell.setAttribute('data-outside', '');
        if (at >= FIRST && at <= LAST) {
          cell.setAttribute('data-date', iso(day));
          cell.setAttribute('aria-label', format(lang, { dateStyle: 'full' }, day.y, day.m, day.d));
        }
      }
    }
    table.replaceChildren(head, body);
    return focused;
  }

  /** Brings the grid, the title and the buttons up to date with the props, the month shown and today. */
  #update() {
    // Before the element connects it has no parts, and must not create them.
    const table = this.isConnected ? this.#table() : null;
    if (!table) return;
    const self = /** @type {any} */ (this);
    const lang = this.#lang();
    const start = weekStart(lang);
    const month = this.#shown();
    const key = `${lang} ${start} ${month.y}-${month.m}`;
    /** @type {string | null} The day that had focus when the grid was drawn again. */
    let refocus = null;
    if (key !== this.#drawn) { refocus = this.#draw(table, lang, start, month); this.#drawn = key; }

    put(table, 'role', 'grid');
    put(table, 'aria-labelledby', this.#id);
    put(table, 'aria-required', self.required ? 'true' : null);
    const title = this.#own('title');
    const name = format(lang, { month: 'long', year: 'numeric' }, month.y, month.m, 1);
    if (title && title.textContent !== name) title.textContent = name;
    const previous = this.#own('previous'), next = this.#own('next');
    if (previous) put(previous, 'aria-disabled', month.y === 1 && month.m === 1 ? 'true' : null);
    if (next) put(next, 'aria-disabled', month.y === 9999 && month.m === 12 ? 'true' : null);

    const chosen = this.#chosen();
    const value = chosen ? iso(chosen) : null;
    const today = /** @type {typeof UICalendar} */ (this.constructor).today();
    for (const cell of table.tBodies[0]?.querySelectorAll('[data-part="day"]') ?? []) {
      const date = cell.getAttribute('data-date');
      const day = parseDate(date);
      put(cell, 'aria-selected', date !== null && date === value ? 'true' : null);
      put(cell, 'aria-current', date !== null && date === today ? 'date' : null);
      put(cell, 'aria-disabled', day && this.#allowed(serial(day)) ? null : 'true');
    }
    this.#stop(refocus);
    this.#anchor();
  }

  /**
   * Writes the Tab stop in the same task as a draw or a new value, as rovingFocus will once its observer runs: the
   * day that has focus, or the day that had it before the draw, or else the chosen day, today or the first of the
   * month (J105). rovingFocus writes the same, so the two never disagree.
   * @param {string | null} refocus
   */
  #stop(refocus) {
    const days = this.#days();
    const active = this.ownerDocument.activeElement;
    const stop = this.effectiveDisabled ? null
      : (refocus && this.#cell(refocus)) || days.find((cell) => cell === active) || this.#preferred();
    for (const cell of days) put(cell, 'tabindex', stop === null ? null : cell === stop ? '0' : '-1');
    if (refocus && stop && stop.getAttribute('data-date') === refocus) stop.focus();
  }

  /**
   * Makes the Tab stop the element the browser focuses when a submit finds the calendar invalid: the root takes no
   * focus. The flags and the message stay as UIFormElement set them.
   */
  #anchor() {
    const validity = this.internals.validity;
    if (validity.valid || !this.isConnected) return;
    const cell = this.#preferred();
    if (!cell) return;
    /** @type {ValidityStateFlags} */
    const flags = {};
    for (const flag of FLAGS) if (validity[flag]) flags[flag] = true;
    this.internals.setValidity(flags, this.internals.validationMessage, cell);
  }

  /** Shows a day's month and moves focus to the day. @param {Day} day */
  #focus(day) {
    this.#moved = { y: day.y, m: day.m };
    this.#update();
    this.#cell(iso(day))?.focus();
  }

  /** Shows the month before or after the one shown, and leaves focus where it is. @param {number} by */
  #step(by) {
    const month = this.#shown();
    const next = addMonths({ ...month, d: 1 }, by);
    if (!next) return;
    this.#moved = { y: next.y, m: next.m };
    this.#update();
  }

  /** Chooses a day because the user asked for it, then tells listeners, who find the grid already written. @param {Day} day */
  #choose(day) {
    const self = /** @type {any} */ (this);
    if (!this.#allowed(serial(day))) { this.#focus(day); return; }
    const value = iso(day);
    const changed = value !== self.value;
    self.value = value; // changed() writes the grid before this returns
    this.#focus(day);
    if (!changed) return;
    this.dispatchEvent(new Event('input', { bubbles: true }));
    this.dispatchEvent(new Event('change', { bubbles: true }));
  }

  /** The calendar's keys on a day (date.grid-keys). @param {KeyboardEvent} event */
  #key(event) {
    const cell = /** @type {HTMLElement} */ (event.target);
    // WebKit keeps focus on a day that loses its tabindex when the calendar is disabled: its keys stop here.
    if (event.altKey || event.ctrlKey || event.metaKey || this.effectiveDisabled || !this.#days().includes(cell)) return;
    const day = parseDate(cell.getAttribute('data-date'));
    if (!day) return;
    const paging = event.key === 'PageUp' || event.key === 'PageDown';
    if (event.shiftKey && !paging) return;
    const n = serial(day);
    const forward = getComputedStyle(this).direction === 'rtl' ? -1 : 1;
    const back = (weekday(n) - weekStart(this.#lang()) + 7) % 7;
    /** @type {number | null} */
    let to = null;
    if (event.key === 'ArrowRight') to = n + forward;
    else if (event.key === 'ArrowLeft') to = n - forward;
    else if (event.key === 'ArrowDown') to = n + 7;
    else if (event.key === 'ArrowUp') to = n - 7;
    else if (event.key === 'Home') to = n - back;
    else if (event.key === 'End') to = n - back + 6;
    else if (paging) {
      const next = addMonths(day, (event.shiftKey ? 12 : 1) * (event.key === 'PageUp' ? -1 : 1));
      to = next ? serial(next) : n;
    } else if (event.key !== 'Enter' && event.key !== ' ') return;
    // rovingFocus would walk the days as a list. It passes over a key whose default is prevented (B8), and this
    // listener is added before it is mounted, so the key is the calendar's alone and still reaches the page.
    event.preventDefault();
    if (to === null) { this.#choose(day); return; }
    this.#focus(fromSerial(to < FIRST || to > LAST ? n : to));
  }

  formValue() {
    const chosen = this.#chosen();
    return chosen ? iso(chosen) : null;
  }

  formValidity() {
    return /** @type {any} */ (this).required && !this.#chosen() ? { flags: { valueMissing: true }, message: VALUE_MISSING } : null;
  }

  /** @param {string | File | FormData | null} state */
  restore(state) { /** @type {any} */ (this).value = typeof state === 'string' ? state : ''; }

  /** @param {string} [name] */
  changed(name) {
    // A value or a month from a script or the author shows its month again.
    if (name === 'value' || name === 'month') this.#moved = null;
    this.#update();
    super.changed();
    this.#anchor();
  }

  connected() {
    this.#header();
    // Before rovingFocus: the calendar's keys stop there.
    this.listen(this, 'keydown', (/** @type {KeyboardEvent} */ event) => this.#key(event));
    this.use(rovingFocus, {
      items: () => this.#days(),
      current: () => this.#preferred(),
      skip: () => this.effectiveDisabled,
    });
    // A press on a day chooses it; on a button, shows the month before or after. A disabled calendar receives no
    // click from the platform; one inside a disabled fieldset is held off here too.
    this.listen(this, 'click', (/** @type {MouseEvent} */ event) => {
      if (this.effectiveDisabled || !(event.target instanceof Element)) return;
      const button = event.target.closest('[data-part="previous"], [data-part="next"]');
      if (button && button.parentElement === this.ensurePart('header')) {
        // At 0001 or 9999 the button is aria-disabled, and #step() stops there.
        this.#step(button.getAttribute('data-part') === 'next' ? 1 : -1);
        return;
      }
      const cell = event.target.closest('[data-part="day"]');
      const day = cell && this.#table()?.contains(cell) ? parseDate(cell.getAttribute('data-date')) : null;
      if (day) this.#choose(day);
    });
    // Disabled, by the attribute or by a fieldset: the buttons take no focus, and the grid says so.
    this.effect(() => {
      const off = this.effectiveDisabled;
      for (const name of ['previous', 'next']) {
        const button = this.#own(name);
        if (button instanceof HTMLButtonElement && button.disabled !== off) button.disabled = off;
      }
      const table = this.#table();
      if (table) setAttr(table, 'aria-disabled', off ? 'true' : null);
    });
    this.changed();
  }
}
