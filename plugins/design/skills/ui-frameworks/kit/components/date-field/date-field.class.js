// @ts-check
/**
 * date-field.class.js: the class of a date field, the APG's date picker combobox. Importing it defines no element;
 * date-field.js does that.
 *
 * The root is the form control (D18): it submits its `value`, a yyyy-mm-dd string, under its `name`
 * (date.value-format). It holds the author's input, the child marked data-part="input", which has no name and
 * shows the value formatted for the language of the nearest `lang`, in the Gregorian calendar, day and month in two
 * digits and the year in four (date.gregorian, date.year-literal), and the author's popup, the child marked
 * data-part="popup", which holds a calendar. It creates the toggle, a span at its end that opens and closes the
 * popup.
 *
 * Typed text is read only when focus leaves the input and on Enter (date.commit-on-leave), in the field order and
 * with the digits the language's own formatter writes, learnt from formatToParts of known dates (date.locale-digits),
 * ASCII digits too, with any separators or none (date.digits-only). A date that is read replaces the text with its
 * formatted form. Text that is no date stays as typed, the input is marked aria-invalid and the value empties
 * (date.invalid-kept). Escape puts back the text of the value held while the user has typed and not committed, and
 * otherwise is left alone (date.escape-revert).
 *
 * The calendar is found without its tag: the grid inside the popup, then the nearest custom element around it in
 * the popup. The field writes its `value`, `min` and `max` and nothing else on it, and takes the day the user
 * chooses there. Dates are plain year, month and day numbers, compared as day counts with the calendar's own
 * routines (testing.time-zones); the clock is read in `static today()` only, for the century of a two-digit year
 * (testing.inject-now).
 *
 * The input's own input and change events stop at the root: the root's say when the date changed.
 *
 * Rules: docs/specs/patterns.md, J109 to J114; docs/specs/foundation.md, F1 to F7. The popup is placed as D77
 * places a menu.
 */
import { UIFormElement } from '../../foundation/form.js';
import { dismiss } from '../../behaviours/dismiss.js';
import { UICalendar } from '../calendar/calendar.class.js';
import { props, parts, role, tabindex, resets } from './date-field.props.js';
import { layout, format, read } from './date-field.text.js';


/** The toggle's name, when the author gave it none. */
const TOGGLE = 'Choose a date';
/** What the browser shows for an invalid field. */
const VALUE_MISSING = 'Please enter a date.';
const BAD_INPUT = 'Please enter a whole date.';
/** @param {string} min */
const BELOW = (min) => `Please enter a date on or after ${min}.`;
/** @param {string} max */
const ABOVE = (max) => `Please enter a date on or before ${max}.`;
/** The flags of a ValidityState that setValidity takes. */
const FLAGS = /** @type {const} */ (['valueMissing', 'typeMismatch', 'patternMismatch', 'tooLong', 'tooShort', 'rangeUnderflow', 'rangeOverflow', 'stepMismatch', 'badInput', 'customError']);

/** @typedef {import('./date-field.text.js').Day} Day */

/** Sets or removes an attribute, only when it differs. @param {Element} el @param {string} name @param {string | null} value */
const put = (el, name, value) => {
  if (el.getAttribute(name) === value) return;
  if (value === null) el.removeAttribute(name);
  else el.setAttribute(name, value);
};

let count = 0;

export class UIDateField extends UIFormElement {
  static props = props;
  static parts = parts;
  static role = role;
  static tabindex = tabindex;
  static resets = resets;

  /** The pure routines that turn a day into text and back, for a test that runs them under several time zones. */
  static text = { layout, format, read };

  /**
   * Today, as yyyy-mm-dd: the one place the field reads the clock, for the century of a two-digit year. A page or a
   * test replaces it on a subclass (testing.inject-now).
   * @returns {string}
   */
  static today() {
    const now = new Date();
    return UICalendar.dates.iso({ y: now.getFullYear(), m: now.getMonth() + 1, d: now.getDate() });
  }

  /** The user has typed since the text was last written or read. */
  #draft = false;
  /** The text in the input is not a date: it stays, and the value is empty. */
  #bad = false;
  /** The user is due to be told whether the field is invalid: after a commit or a submit attempt. */
  #told = false;
  /** The input this class marked aria-invalid, so that it removes only its own mark. @type {HTMLInputElement | null} */
  #marked = null;
  /** The input this class disabled, so that it enables only what it disabled. @type {HTMLInputElement | null} */
  #disabledInput = null;
  /** The input the text of the value was last written in. @type {HTMLInputElement | null} */
  #shown = null;
  /** A write of the value that must leave the text as typed. */
  #keep = false;
  #id = `date-field-popup-${++count}`;

  /** The author's input. @returns {HTMLInputElement | null} */
  #input() {
    const el = this.querySelector(':scope > [data-part="input"]');
    return el instanceof HTMLInputElement ? el : null;
  }

  /** @returns {HTMLElement | null} */
  #popup() { return this.querySelector(':scope > [data-part="popup"]'); }

  /** The toggle part. */
  #toggle() { return this.ensurePart('toggle'); }

  /** The calendar in the popup: the nearest custom element around its grid, inside the popup. @returns {HTMLElement | null} */
  #calendar() {
    const popup = this.#popup();
    const grid = popup?.querySelector('[role="grid"]');
    for (let el = grid?.parentElement ?? null; el && el !== popup; el = el.parentElement) if (el.localName.includes('-')) return el;
    return null;
  }

  /** The language of the text: the nearest lang, or the browser's. */
  #lang() {
    const lang = this.closest('[lang]')?.getAttribute('lang') || navigator.language || 'en';
    try { return Intl.getCanonicalLocales(lang)[0] ?? 'en'; } catch { return navigator.language || 'en'; }
  }

  /** The day the field holds, or null. */
  #held() { return UICalendar.dates.parseDate(/** @type {any} */ (this).value); }

  /** The field cannot be changed: its input is read-only or disabled. A disabled field has disabled its input. */
  #locked() {
    const input = this.#input();
    return !input || input.readOnly || input.disabled;
  }

  /** Writes the text of the value held into the input, and drops a draft and an unreadable text. */
  #show() {
    const input = this.#input();
    this.#shown = input;
    this.#draft = false;
    this.#bad = false;
    if (!input) return;
    const day = this.#held();
    const text = day ? format(this.#lang(), day) : '';
    if (input.value !== text) input.value = text;
    if (this.ownerDocument.activeElement === input) {
      // The caret goes to the end of the rewritten text, and the field scrolls to show it (form.caret-after-rewrite).
      input.setSelectionRange(text.length, text.length);
      input.scrollLeft = input.scrollWidth;
    }
  }

  /**
   * Sets the value because the user asked for it, and tells listeners when it changed. The write rewrites the text,
   * unless `keep` says to leave it as typed. @param {string} value @param {boolean} [keep]
   */
  #set(value, keep = false) {
    const self = /** @type {any} */ (this);
    const before = self.value;
    this.#told = true;
    this.#keep = keep;
    self.value = value;
    this.#keep = false;
    this.changed();
    if (self.value === before) return;
    this.dispatchEvent(new Event('input', { bubbles: true }));
    this.dispatchEvent(new Event('change', { bubbles: true }));
  }

  /** Reads what the user typed, when they typed (J110, J111). */
  #commit() {
    const input = this.#input();
    if (!input || !this.#draft || this.#locked()) return;
    const year = UICalendar.dates.parseDate(/** @type {typeof UIDateField} */ (this.constructor).today())?.y ?? 2000;
    const value = read(this.#lang(), input.value, year);
    this.#draft = false;
    if (value === null) {
      this.#bad = true;
      this.#set('', true);
    } else this.#set(value);
  }

  /** Takes the day chosen in the calendar, closes the popup and gives focus back to the input. @param {string | null} value */
  #take(value) {
    if (!UICalendar.dates.parseDate(value)) return;
    /** @type {any} */ (this).open = false;
    this.#input()?.focus();
    this.#set(/** @type {string} */ (value));
  }

  /** Writes value, min and max on the calendar. On opening, the value is written again so the calendar shows its month. @param {boolean} [opening] */
  #hand(opening = false) {
    const calendar = this.#calendar();
    if (!calendar) return;
    const self = /** @type {any} */ (this);
    const day = this.#held();
    const value = day ? UICalendar.dates.iso(day) : null;
    if (opening && value !== null) calendar.setAttribute('value', value);
    else put(calendar, 'value', value);
    put(calendar, 'min', self.min || null);
    put(calendar, 'max', self.max || null);
  }

  /** Moves focus to the calendar's Tab stop, which is the chosen day when there is one in the month shown. */
  #enter() {
    const cell = /** @type {HTMLElement | null} */ (this.#popup()?.querySelector('[role="grid"] [tabindex="0"]') ?? null);
    cell?.focus();
  }

  /** Opens the popup because the user asked for it: commits a draft first, then hands the calendar the date and moves focus into it. */
  #open() {
    this.#commit();
    /** @type {any} */ (this).open = true;
    if (/** @type {any} */ (this).open) this.#enter();
  }

  /** Closes the popup, and gives focus back to the input when it was in the popup. */
  #close() {
    const popup = this.#popup();
    const inside = !!popup && popup.contains(this.ownerDocument.activeElement);
    /** @type {any} */ (this).open = false;
    if (inside) this.#input()?.focus();
  }

  /** Shows or hides the popup so that it is showing exactly while `open` is set. Runs synchronously. */
  #apply() {
    if (!this.isConnected) return;
    const self = /** @type {any} */ (this);
    // A field that cannot be changed does not open: #sync() undoes the write, which runs this again (J113).
    this.#sync();
    const popup = this.#popup();
    const showing = !!popup?.matches(':popover-open');
    if (popup && self.open !== showing) {
      if (self.open) { this.#hand(true); popup.showPopover(); }
      else popup.hidePopover();
    }
  }

  /** Brings the input's, the popup's and the toggle's attributes in step. Writes nothing when they already are. */
  #sync() {
    const self = /** @type {any} */ (this);
    const input = this.#input();
    const popup = this.#popup();
    if (popup) {
      if (!popup.hasAttribute('popover')) popup.setAttribute('popover', 'manual');
      if (!popup.hasAttribute('role')) popup.setAttribute('role', 'dialog');
      if (!popup.id) popup.id = this.#id;
    }
    if (input) {
      if (!input.hasAttribute('role')) input.setAttribute('role', 'combobox');
      put(input, 'aria-haspopup', 'dialog');
      put(input, 'aria-expanded', String(!!self.open));
      put(input, 'aria-controls', popup ? popup.id : null);
      put(input, 'aria-required', self.required ? 'true' : null);
    }
    const toggle = this.#toggle();
    if (toggle) {
      if (!toggle.hasAttribute('aria-label') && !toggle.hasAttribute('aria-labelledby')) toggle.setAttribute('aria-label', TOGGLE);
      put(toggle, 'aria-disabled', this.effectiveDisabled ? 'true' : null);
    }
    this.#hand();
    if (self.open && this.#locked()) self.open = false;
  }

  /** Marks the input aria-invalid and the root invalid while the user is due to be told (J111). */
  #mark() {
    const input = this.#input();
    const shown = !!input && (this.#bad || (this.#told && !this.internals.validity.valid));
    if (this.#marked && this.#marked !== input) put(this.#marked, 'aria-invalid', null);
    if (input && (shown || this.#marked === input)) put(input, 'aria-invalid', shown ? 'true' : null);
    // Only a mark this class wrote is taken off the root: an author's invalid stays as written.
    if (shown || this.#marked) put(this, 'invalid', shown ? '' : null);
    this.#marked = shown ? input : null;
  }

  /** Makes the input the element a submit focuses when the field is invalid; the root takes no focus (form.visible-control). */
  #anchor() {
    const validity = this.internals.validity;
    const input = this.#input();
    if (validity.valid || !input || !this.isConnected) return;
    /** @type {ValidityStateFlags} */
    const flags = {};
    for (const flag of FLAGS) if (validity[flag]) flags[flag] = true;
    this.internals.setValidity(flags, this.internals.validationMessage, input);
  }

  formValue() {
    const day = this.#held();
    return day ? UICalendar.dates.iso(day) : null;
  }

  formValidity() {
    const self = /** @type {any} */ (this);
    if (this.#bad) return { flags: { badInput: true }, message: BAD_INPUT };
    const day = this.#held();
    if (!day) return self.required ? { flags: { valueMissing: true }, message: VALUE_MISSING } : null;
    const min = UICalendar.dates.parseDate(self.min), max = UICalendar.dates.parseDate(self.max);
    const lang = this.isConnected ? this.#lang() : 'en';
    if (min && UICalendar.dates.serial(day) < UICalendar.dates.serial(min)) return { flags: { rangeUnderflow: true }, message: BELOW(format(lang, min)) };
    if (max && UICalendar.dates.serial(day) > UICalendar.dates.serial(max)) return { flags: { rangeOverflow: true }, message: ABOVE(format(lang, max)) };
    return null;
  }

  /** @param {string | File | FormData | null} state */
  restore(state) { /** @type {any} */ (this).value = typeof state === 'string' ? state : ''; }

  /** The value goes back, which writes its text and drops a draft and an unreadable text; the user is no longer due to be told. */
  formResetCallback() {
    this.#told = false;
    super.formResetCallback();
  }

  /** The platform calls this for the field's own disabled attribute, in the same task, and for a fieldset. @param {boolean} off */
  formDisabledCallback(off) {
    super.formDisabledCallback(off);
    this.#disable();
  }

  /** Disabled, by the attribute or a fieldset: the input is disabled with it, and the popup closes (J113). */
  #disable() {
    if (!this.isConnected) return;
    const off = this.effectiveDisabled;
    const input = this.#input();
    if (input) {
      if (off && !input.disabled) { input.disabled = true; this.#disabledInput = input; }
      else if (!off && this.#disabledInput) { this.#disabledInput.disabled = false; this.#disabledInput = null; }
    }
    this.#sync();
  }

  /** @param {string} [name] */
  changed(name) {
    if (this.isConnected) {
      if (name === 'open') this.#apply();
      else if (name === 'value' || name === 'min' || name === 'max' || name === 'required') {
        if (name === 'value' && !this.#keep) this.#show();
        this.#sync();
      }
    }
    super.changed();
    this.#anchor();
    if (this.isConnected) this.#mark();
  }

  connected() {
    const self = /** @type {any} */ (this);
    /** @param {KeyboardEvent} event */
    const plain = (event) => !event.altKey && !event.ctrlKey && !event.metaKey && !event.shiftKey;

    // Before dismiss, which listens on this root too and takes Escape while the popup is open.
    this.listen(this, 'keydown', (/** @type {KeyboardEvent} */ event) => {
      const input = this.#input();
      if (event.altKey && !event.ctrlKey && !event.metaKey && (event.key === 'ArrowDown' || event.key === 'ArrowUp')) {
        if (event.key === 'ArrowDown' && event.target === input && !self.open) {
          event.preventDefault();
          this.#open();
        } else if (event.key === 'ArrowUp' && self.open) {
          event.preventDefault();
          this.#close();
        }
        return;
      }
      if (event.target !== input || !plain(event)) return;
      // Enter keeps its default, so the form is submitted with the date just read.
      if (event.key === 'Enter') this.#commit();
      else if (event.key === 'Escape' && !self.open && this.#draft) {
        event.preventDefault();
        event.stopPropagation();
        this.#show();
        this.changed();
      }
    });
    // Enter or Space on the day already chosen: the calendar would do nothing the field could hear, so the field
    // takes that day itself, before the calendar sees the key.
    this.listen(this, 'keydown', (/** @type {KeyboardEvent} */ event) => {
      if ((event.key !== 'Enter' && event.key !== ' ') || !plain(event) || !self.open) return;
      const cell = event.target instanceof Element ? event.target.closest('[role="gridcell"]') : null;
      const calendar = this.#calendar();
      if (!cell || !calendar?.contains(cell) || cell.getAttribute('aria-selected') !== 'true') return;
      event.preventDefault();
      event.stopPropagation();
      this.#take(calendar.getAttribute('value'));
    }, { capture: true });
    // The input's own events stop here, and the calendar's too: the root's say when the date changed. A day
    // chosen in the calendar is taken from its change.
    for (const type of ['input', 'change']) {
      this.listen(this, type, (event) => {
        if (event.target === this) return;
        event.stopPropagation();
        if (type === 'input' && event.target === this.#input()) this.#draft = true;
        const calendar = this.#calendar();
        if (type === 'change' && calendar && event.target === calendar && self.open) this.#take(calendar.getAttribute('value'));
      });
    }
    // A press on the day already chosen closes the popup with it; a press on another reached the calendar's change.
    this.listen(this, 'click', (/** @type {MouseEvent} */ event) => {
      if (!(event.target instanceof Element)) return;
      const toggle = this.#toggle();
      if (toggle && toggle.contains(event.target)) {
        if (self.open) this.#close();
        else this.#open();
        return;
      }
      const cell = event.target.closest('[role="gridcell"]');
      const calendar = this.#calendar();
      if (self.open && cell && calendar?.contains(cell) && cell.getAttribute('aria-selected') === 'true') this.#take(calendar.getAttribute('value'));
    });
    // A press on the field outside the input and the popup moves no focus to the press, and puts it in the input.
    this.listen(this, 'mousedown', (/** @type {MouseEvent} */ event) => {
      const input = this.#input();
      const target = event.target instanceof Node ? event.target : null;
      if (!input || !target || target === input || this.#popup()?.contains(target)) return;
      event.preventDefault();
      const toggle = this.#toggle();
      if (!input.disabled && !toggle?.contains(target) && this.ownerDocument.activeElement !== input) input.focus();
    });
    // Focus that leaves the input reads what was typed.
    this.listen(this, 'focusout', (event) => { if (event.target === this.#input()) this.#commit(); });
    // A submit attempt tells the user. invalid does not bubble, and is fired on the root.
    this.listen(this, 'invalid', () => { this.#told = true; this.#mark(); });
    // Something else hid the popup, such as a script calling hidePopover(): the attribute follows.
    this.listen(this, 'toggle', (event) => {
      const popup = this.#popup();
      if (popup && event.target === popup && self.open && !popup.matches(':popover-open')) self.open = false;
    }, { capture: true });
    // Escape, a press outside and focus that leaves close the popup. Escape goes no further (overlay.escape-innermost).
    this.use(dismiss, {
      active: () => self.open,
      onDismiss: (/** @type {string} */ reason) => {
        if (reason === 'escape') this.#close();
        else self.open = false;
      },
    });
    // The observer lives as long as the connection. It sees an input or a popup that arrives or is replaced, a
    // calendar that is defined later, and readonly or disabled written on the input.
    this.effect(() => {
      const observer = new MutationObserver(() => {
        // An input that replaces another shows the date held.
        if (this.#input() !== this.#shown) this.#show();
        this.#disable();
        this.#mark();
      });
      observer.observe(this, { childList: true, subtree: true, attributes: true, attributeFilter: ['data-part', 'role', 'readonly', 'disabled', 'id', 'popover'] });
      return () => observer.disconnect();
    });
    this.#show();
    this.#disable();
    this.#apply();
    this.changed();
  }
}
