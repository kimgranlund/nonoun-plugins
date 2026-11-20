// @ts-check
/**
 * select.class.js: the class of a select, the APG's select-only combobox. Importing it defines no element;
 * select.js does that.
 *
 * The root is the form control: it has the combobox role, is the one stop in the Tab order and keeps focus.
 * It holds the author's popup (the child marked data-part="popup"), which holds the kit's listbox, and it creates
 * the value part, a span at its start that shows the chosen option's text, or the placeholder when none is
 * chosen. The option the keys point at carries data-highlighted and is named by aria-activedescendant on the root.
 *
 * The listbox stays passive here, as in the combobox. The select writes tabindex="-1" on it, so it is no Tab
 * stop whichever element is defined first, gives it no name, so it submits nothing, and cancels a press inside
 * the popup, so it never takes focus. A click on an option still runs the listbox's own logic: it selects the
 * option there and dispatches the listbox's input and change, which the select stops at its root, since its
 * own follow. The listbox's keys never fire, because they are pressed on the root. The option's recipe paints
 * the highlight only on an option marked data-focus, which the listbox writes while it has focus; here the root
 * has it, so the select writes that mark on the highlighted option while the list is open.
 *
 * The select's `value` decides which option is selected: it writes `selected` on that option and on no other,
 * whoever else writes it. With no value written, the first time it finds options it takes the last one the
 * author marked selected.
 *
 * It finds the listbox and the options by their ARIA role and names no tag. An observer held in an effect keeps
 * it right when they are defined later, come, go or change.
 *
 * Rules: docs/specs/patterns.md, J82 to J87; docs/specs/foundation.md, F1 to F7. The overlay is placed as D77
 * places a menu.
 */
import { setAttr } from '../../foundation/element.js';
import { UIFormElement } from '../../foundation/form.js';
import { activeDescendant } from '../../behaviours/active-descendant.js';
import { typeahead } from '../../behaviours/typeahead.js';
import { dismiss } from '../../behaviours/dismiss.js';
import { props, parts, role, tabindex, resets } from './select.props.js';

const LISTBOX = '[role="listbox"]';
const OPTION = '[role="option"]';
const MARK = 'data-highlighted';
/** Shown by the browser when a required select has nothing chosen. The listbox's message. */
const VALUE_MISSING = 'Please choose an option';
/** For the ids this class gives to a listbox that has none. */
let serial = 0;

/** @param {Element} el */
const disabled = (el) => el.hasAttribute('disabled') || el.getAttribute('aria-disabled') === 'true';

/** An option's text, as the value part shows it. @param {Element} el */
const textOf = (el) => (el.textContent ?? '').trim();

/** An option's value: its `value` attribute, or else its text. @param {Element} el */
const valueOf = (el) => el.getAttribute('value') ?? textOf(el);

/**
 * Sets or removes an attribute, only when it differs. The observer then sees nothing when nothing changes.
 * @param {Element} el @param {string} name @param {string | null} value
 */
const put = (el, name, value) => {
  if (el.getAttribute(name) === value) return;
  if (value === null) el.removeAttribute(name);
  else el.setAttribute(name, value);
};

export class UISelect extends UIFormElement {
  static props = props;
  static parts = parts;
  static role = role;
  static tabindex = tabindex;
  static resets = resets;

  /** @type {string | null} The value once the select first settled with its options: what a reset restores. */
  #initial = null;
  /** @type {HTMLElement | null} The option the list opens on, when Home, End or a typed letter opened it. */
  #target = null;
  /** Whether the key going down opened the list, so that activeDescendant does not move on with it. */
  #opened = false;

  /** @returns {HTMLElement | null} */
  #popup() { return this.querySelector(':scope > [data-part="popup"]'); }

  /** The listbox in the popup, once it has its role. @returns {HTMLElement | null} */
  #listbox() { return this.#popup()?.querySelector(LISTBOX) ?? null; }

  /** The options of the listbox, and not of a listbox nested in one. @returns {HTMLElement[]} */
  #options() {
    const listbox = this.#listbox();
    if (!listbox) return [];
    return /** @type {HTMLElement[]} */ ([...listbox.querySelectorAll(OPTION)].filter((el) => el.closest(LISTBOX) === listbox));
  }

  /** The option whose value is the select's, or null. */
  #chosen() {
    const value = /** @type {any} */ (this).value;
    return value === '' ? null : this.#options().find((el) => valueOf(el) === value) ?? null;
  }

  /** The option the keys point at. */
  #highlighted() { return this.#options().find((el) => el.hasAttribute(MARK)) ?? null; }

  /**
   * Points at `target`, or else at the chosen option, or else at the first; never at a disabled one, which
   * activeDescendant would refuse. @param {HTMLElement | null} [target]
   */
  #point(target = null) {
    const usable = this.#options().filter((el) => !disabled(el));
    const chosen = this.#chosen();
    const to = target ?? (chosen && usable.includes(chosen) ? chosen : usable[0]);
    if (to) put(to, MARK, '');
  }

  /** Opens the list on `target`, or on the chosen option. @param {HTMLElement | null | undefined} [target] */
  #open(target) {
    this.#target = target ?? null;
    /** @type {any} */ (this).open = true;
  }

  /**
   * Chooses an option because the user asked for it, closes the list, and then tells listeners, who find
   * everything written. None only closes it. A disabled option never arrives here: activeDescendant does not
   * point at one, and the click handler passes it over. @param {HTMLElement | null} option
   */
  #choose(option) {
    const self = /** @type {any} */ (this);
    const before = self.value;
    if (option) self.value = valueOf(option);
    self.open = false;
    if (self.value === before) return;
    this.dispatchEvent(new Event('input', { bubbles: true }));
    this.dispatchEvent(new Event('change', { bubbles: true }));
  }

  /**
   * Shows or hides the popup so that it is showing exactly while `open` is set, points at an option when the
   * list opens and at none once it closes. Runs synchronously, so a script that sets `open` finds it all in the
   * same task.
   */
  #apply() {
    if (!this.isConnected) return;
    const self = /** @type {any} */ (this);
    const open = self.open;
    // A disabled select does not open: the write that asked for it is undone, which runs this again (J86).
    if (open && this.effectiveDisabled) { self.open = false; return; }
    const popup = this.#popup();
    if (popup && !popup.hasAttribute('popover')) popup.setAttribute('popover', 'manual');
    const showing = !!popup?.matches(':popover-open');
    if (popup && open !== showing) {
      if (open) popup.showPopover();
      else popup.hidePopover();
    }
    setAttr(this, 'aria-expanded', String(open));
    const options = this.#options();
    // Only opening points at an option, so a second write of open leaves where the keys moved to.
    if (open && !showing) this.#point(this.#target);
    this.#target = null;
    if (!open) for (const option of options) put(option, MARK, null);
    this.#sync();
  }

  /** Brings the listbox's passivity, the options' selection, the value part and the painted highlight in step. Writes nothing when they already are. */
  #sync() {
    const self = /** @type {any} */ (this);
    const popup = this.#popup();
    const listbox = this.#listbox();
    if (popup && !popup.hasAttribute('popover')) popup.setAttribute('popover', 'manual');
    if (listbox) {
      // -listbox- keeps it apart from the ids activeDescendant gives the options, from its own count, under the same tag.
      if (!listbox.id) listbox.id = `${this.localName}-listbox-${++serial}`;
      put(listbox, 'tabindex', '-1');
    }
    put(this, 'aria-controls', listbox ? listbox.id : null);
    const options = this.#options();
    if (options.length && this.#initial === null) {
      // No value written: take the option the author marked, the last one when several are.
      const marked = options.filter((el) => el.hasAttribute('selected'));
      if (self.value === '' && marked.length) {
        self.value = valueOf(marked[marked.length - 1]);
        return; // changed() has run this again with the value in place.
      }
      this.#initial = self.value;
    }
    const chosen = this.#chosen();
    for (const option of options) put(option, 'selected', option === chosen ? '' : null);
    const part = /** @type {HTMLElement} */ (this.ensurePart('value'));
    const text = chosen ? textOf(chosen) : self.placeholder;
    if (part.textContent !== text) part.textContent = text;
    put(part, 'data-placeholder', chosen ? null : '');
    for (const option of options) put(option, 'data-focus', self.open && option.hasAttribute(MARK) ? '' : null);
  }

  formValue() {
    const chosen = this.#chosen();
    return chosen ? valueOf(chosen) : null;
  }

  formValidity() {
    return /** @type {any} */ (this).required && !this.#chosen() ? { flags: { valueMissing: true }, message: VALUE_MISSING } : null;
  }

  /** @param {string | File | FormData | null} state */
  restore(state) {
    /** @type {any} */ (this).value = typeof state === 'string' ? state : '';
  }

  formResetCallback() {
    super.formResetCallback();
    if (this.#initial !== null) /** @type {any} */ (this).value = this.#initial;
  }

  /** @param {boolean} off */
  formDisabledCallback(off) {
    super.formDisabledCallback(off);
    // A select that becomes disabled, by its attribute or a fieldset, closes its list (J86).
    if (off && /** @type {any} */ (this).open) /** @type {any} */ (this).open = false;
  }

  /** @param {string} [name] */
  changed(name) {
    if (name === 'open') this.#apply();
    else if ((name === 'value' || name === 'placeholder') && this.isConnected) this.#sync();
    super.changed();
  }

  connected() {
    const self = /** @type {any} */ (this);
    setAttr(this, 'aria-haspopup', 'listbox');
    this.effect(() => setAttr(this, 'aria-required', self.required ? 'true' : null));

    // Before the behaviours, which listen on this root too: the keys that open the list, and those that choose.
    this.listen(this, 'keydown', (event) => {
      this.#opened = false;
      if (event.target !== this || event.altKey || event.ctrlKey || event.metaKey) return;
      if (!self.open) {
        const usable = this.#options().filter((el) => !disabled(el));
        if (!['ArrowDown', 'ArrowUp', 'Home', 'End', 'Enter', ' '].includes(event.key)) return;
        event.preventDefault();
        this.#opened = true;
        this.#open(event.key === 'Home' ? usable[0] : event.key === 'End' ? usable[usable.length - 1] : null);
      } else if (event.key === 'Enter' || event.key === ' ' || event.key === 'Tab') {
        // Tab keeps its default: the choice is made, and focus moves on.
        if (event.key !== 'Tab') event.preventDefault();
        this.#choose(this.#highlighted());
      }
    });
    // A press on the select opens the list, or closes it; the press itself gives the root focus. A disabled
    // select receives no press: the platform withholds it from a disabled form-associated element. A press in
    // the popup moves no focus: it would focus the listbox.
    this.listen(this, 'mousedown', (event) => {
      if (!(event.target instanceof Node)) return;
      if (this.#popup()?.contains(event.target)) { event.preventDefault(); return; }
      if (event.button !== 0) return;
      self.open = !self.open;
    });
    // A click on an option chooses it. The listbox has selected it already, and the select's value decides.
    this.listen(this, 'click', (event) => {
      const option = /** @type {HTMLElement | null} */ (event.target instanceof Element ? event.target.closest(OPTION) : null);
      if (option && !disabled(option) && this.#options().includes(option)) this.#choose(option);
    });
    // The listbox's own input and change stop here: the select's say what the user chose.
    for (const type of ['input', 'change']) {
      this.listen(this, type, (event) => {
        if (event.target !== this && event.target instanceof Node && this.#popup()?.contains(event.target)) event.stopPropagation();
      });
    }
    // Something else hid the popup, such as a script calling hidePopover(): the attribute follows.
    this.listen(this, 'toggle', (event) => {
      const popup = this.#popup();
      if (popup && event.target === popup && self.open && !popup.matches(':popover-open')) self.open = false;
    }, { capture: true });

    this.use(activeDescendant, {
      items: () => this.#options(),
      skip: disabled,
      active: () => self.open && !this.#opened,
    });
    this.use(typeahead, {
      // The search starts from the option the keys point at, or from the chosen one while the list is closed.
      items: () => this.#options(),
      current: () => this.#highlighted() ?? this.#chosen(),
      skip: disabled,
      onMatch: (/** @type {HTMLElement} */ option) => {
        if (self.open) put(option, MARK, '');
        else this.#open(option);
      },
    });
    // Escape, a press outside and focus that leaves close the list and keep the value. Escape goes no further.
    this.use(dismiss, {
      active: () => self.open,
      onDismiss: () => { self.open = false; },
    });

    // The observer lives as long as the connection: the effect reads no signal, so it runs once, and its
    // cleanup disconnects.
    this.effect(() => {
      const observer = new MutationObserver(() => {
        // Options that arrive in an open list, such as one written open before they were defined: point at one.
        if (self.open && !this.#highlighted()) this.#point();
        this.#sync();
        this.changed(); // the form value follows the options that came, went or changed.
      });
      observer.observe(this, { childList: true, subtree: true, characterData: true, attributes: true, attributeFilter: ['role', 'id', 'value', 'tabindex', 'popover', 'selected', 'disabled', 'aria-disabled', MARK, 'data-focus'] });
      return () => observer.disconnect();
    });
    this.#apply();
    this.changed();
  }
}
