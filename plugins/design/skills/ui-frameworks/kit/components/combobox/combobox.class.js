// @ts-check
/**
 * combobox.class.js: the class of a combobox, a text field with a list of suggestions that narrows as the user
 * types. Importing it defines no element; combobox.js does that.
 *
 * The root has no role and is the field: it holds the author's input (the child marked data-part="input") and
 * the popup (the child marked data-part="popup"), and the popup holds the kit's listbox. Focus stays in the
 * input; the input carries the combobox role and the form value under its own name (J43). The list follows the
 * APG's list autocomplete with manual selection: typing filters the options and opens the list, the arrows move
 * a highlight, and only Enter or a click takes an option (J44).
 *
 * The listbox stays passive here. The combobox writes tabindex="-1" on it, so it is no Tab stop whichever element
 * is defined first, gives it no name, so it submits nothing, and cancels a press inside the popup, so it never
 * takes focus. The listbox's own logic still runs: a click on an option highlights and selects it there and
 * dispatches the listbox's input and change, which the combobox stops at its root, since its own change follows.
 * Its keys never fire, because they are pressed on the input, so its "selection follows the highlight" never runs.
 * The listbox paints a highlight only on an option marked data-focus, which it writes while it has focus; here
 * the input has it, so the combobox writes that mark on the highlighted option while the input has focus.
 *
 * It finds the listbox and the options by their ARIA role and names no tag. An observer held in an effect keeps
 * it right when they are defined later, come, go or change.
 *
 * While the input carries readonly the list stays closed, whoever asks for it, and the component does not change
 * the input's value (J80). The observer closes a list that is open when the input becomes read-only.
 *
 * Rules: docs/specs/patterns.md, J43 to J46 and J80. The overlay is placed as D77 places a menu.
 */
import { UIElement } from '../../foundation/element.js';
import { activeDescendant } from '../../behaviours/active-descendant.js';
import { dismiss } from '../../behaviours/dismiss.js';
import { props } from './combobox.props.js';

const LISTBOX = '[role="listbox"]';
const OPTION = '[role="option"]';
const MARK = 'data-highlighted';
/** For the ids this class gives to a listbox that has none. */
let serial = 0;

/** @param {Element} el */
const disabled = (el) => el.hasAttribute('disabled') || el.getAttribute('aria-disabled') === 'true';

/** An option's text, as the input shows it once taken. @param {Element} el */
const textOf = (el) => (el.textContent ?? '').trim();

/**
 * Sets or removes an attribute, only when it differs. The observer then sees nothing when nothing changes.
 * @param {Element} el @param {string} name @param {string | null} value
 */
const put = (el, name, value) => {
  if (el.getAttribute(name) === value) return;
  if (value === null) el.removeAttribute(name);
  else el.setAttribute(name, value);
};

export class UICombobox extends UIElement {
  static props = props;

  /** Whether the key going down is Home or End, which stay with the input's text even while the list is open. */
  #textKey = false;

  /** @returns {HTMLInputElement | null} */
  #input() { return this.querySelector(':scope > input[data-part="input"]'); }

  /** Whether the input is read-only, so that the list does not open and the value does not change (J80). */
  #readOnly() { return !!this.#input()?.hasAttribute('readonly'); }

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

  /** The options the filter shows. */
  #shown() { return this.#options().filter((el) => !el.hasAttribute('hidden')); }

  /**
   * Shows the options whose text contains `text`, whatever its case, and hides the others. The highlight is
   * cleared first, so that Enter takes nothing the user did not point at. @param {string} text @returns {number}
   */
  #filter(text) {
    const query = text.toLowerCase();
    const options = this.#options();
    for (const option of options) put(option, MARK, null);
    for (const option of options) put(option, 'hidden', textOf(option).toLowerCase().includes(query) ? null : '');
    return this.#shown().length;
  }

  /**
   * Takes an option: its text goes into the input, it alone is selected, the list closes, and change is
   * dispatched once all of that is written. @param {HTMLElement | null | undefined} option
   */
  #take(option) {
    const input = this.#input();
    if (!input || !option || disabled(option) || option.hasAttribute('hidden') || this.#readOnly()) return;
    input.value = textOf(option);
    for (const other of this.#options()) put(other, 'selected', other === option ? '' : null);
    this.#filter(input.value);
    /** @type {any} */ (this).open = false;
    this.dispatchEvent(new Event('change', { bubbles: true }));
  }

  /**
   * Shows or hides the popup so that it is showing exactly while `open` is set, and clears the highlight of a
   * closed list. Runs synchronously, so a script that sets `open` finds the popup shown in the same task.
   */
  #apply() {
    if (!this.isConnected) return;
    const open = /** @type {any} */ (this).open;
    // A read-only list does not open: the write that asked for it is undone, which runs this again (J80).
    if (open && this.#readOnly()) { /** @type {any} */ (this).open = false; return; }
    const popup = this.#popup();
    if (popup && !popup.hasAttribute('popover')) popup.setAttribute('popover', 'manual');
    if (popup && open !== popup.matches(':popover-open')) {
      if (open) popup.showPopover();
      else popup.hidePopover();
    }
    if (!open) for (const option of this.#options()) put(option, MARK, null);
    this.#sync();
  }

  /** Brings the ARIA of the input, the listbox's passivity and the painted highlight in step. Writes nothing when they already are. */
  #sync() {
    const open = /** @type {any} */ (this).open;
    const input = this.#input();
    const popup = this.#popup();
    const listbox = this.#listbox();
    if (popup && !popup.hasAttribute('popover')) popup.setAttribute('popover', 'manual');
    if (listbox) {
      // -listbox- keeps it apart from the ids activeDescendant gives the options, from its own count, under the same tag.
      if (!listbox.id) listbox.id = `${this.localName}-listbox-${++serial}`;
      put(listbox, 'tabindex', '-1');
    }
    if (input) {
      put(input, 'role', 'combobox');
      put(input, 'aria-autocomplete', 'list');
      if (listbox) put(input, 'aria-controls', listbox.id);
      put(input, 'aria-expanded', String(open));
      put(this, 'aria-disabled', input.hasAttribute('disabled') ? 'true' : null);
    }
    // The option's recipe paints the highlight only on data-focus, which its listbox writes while it has focus.
    // Here the input has focus, so the combobox writes it; the listbox clears it again when its observer runs,
    // and this element's observer, which watches the mark, puts it back.
    const focused = !!input && this.ownerDocument.activeElement === input;
    for (const option of this.#options()) put(option, 'data-focus', open && focused && option.hasAttribute(MARK) ? '' : null);
  }

  /** @param {string} name */
  changed(name) {
    if (name === 'open') this.#apply();
  }

  connected() {
    const self = /** @type {any} */ (this);
    const input = () => this.#input();

    // Typing filters the options, and opens the list while one shows (J44).
    this.listen(this, 'input', (event) => {
      if (event.target !== input()) return;
      self.open = this.#filter(/** @type {HTMLInputElement} */ (event.target).value) > 0;
    });
    // Before the behaviours, which listen on this root too: the keys the combobox handles itself.
    this.listen(this, 'keydown', (event) => {
      const field = input();
      if (!field || event.target !== field) return;
      this.#textKey = event.key === 'Home' || event.key === 'End';
      // A read-only input keeps its value and opens nothing: Escape does not clear it (J80).
      if (event.altKey || event.ctrlKey || event.metaKey || event.shiftKey || this.#readOnly()) return;
      if ((event.key === 'ArrowDown' || event.key === 'ArrowUp') && !self.open) {
        // Opening first lets activeDescendant, which runs next, take the key: with nothing highlighted,
        // ArrowDown goes to the first option that shows and ArrowUp to the last.
        if (this.#shown().length) self.open = true;
      } else if (event.key === 'Enter' && self.open) {
        const option = this.#shown().find((el) => el.hasAttribute(MARK));
        if (!option) return; // Nothing highlighted: Enter submits the form, as in a plain input.
        event.preventDefault();
        this.#take(option);
      } else if (event.key === 'Escape' && !self.open && field.value !== '') {
        // With the list open, dismiss closes it; with the list closed, Escape clears the field.
        event.preventDefault();
        field.value = '';
        this.#filter('');
      }
    });
    // A click on an option takes it. The listbox has highlighted and selected it already.
    this.listen(this, 'click', (event) => {
      const option = /** @type {HTMLElement | null} */ (event.target instanceof Element ? event.target.closest(OPTION) : null);
      if (option && this.#options().includes(option)) this.#take(option);
    });
    // The listbox's own input and change stop here: the combobox's change says what the user took.
    for (const type of ['input', 'change']) {
      this.listen(this, type, (event) => {
        if (event.target instanceof Node && event.target !== input() && this.#popup()?.contains(event.target)) event.stopPropagation();
      });
    }
    // A press moves no focus: inside the popup it would focus the listbox, and on the field around the input
    // it would take focus from the input, which it gives to the input instead.
    this.listen(this, 'mousedown', (event) => {
      const field = input();
      if (!(event.target instanceof Node) || event.target === field) return;
      event.preventDefault();
      if (event.target === this) field?.focus();
    });
    // Something else hid the popup, such as a script calling hidePopover(): the attribute follows.
    this.listen(this, 'toggle', (event) => {
      const popup = this.#popup();
      if (popup && event.target === popup && self.open && !popup.matches(':popover-open')) self.open = false;
    }, { capture: true });
    this.listen(this, 'focusin', () => this.#sync());
    this.listen(this, 'focusout', () => this.#sync());

    this.use(activeDescendant, {
      items: () => this.#shown(),
      skip: disabled,
      wrap: true,
      focus: () => this.#input() ?? this,
      // No need to ask whether the list is open: an arrow on a closed list opens it first, above, or finds no
      // option that shows, and then the behaviour has nothing to move.
      active: () => !this.#textKey && !this.#readOnly(),
    });
    // Escape, a press outside and focus that leaves close the list. A press on the input is inside the root.
    this.use(dismiss, {
      active: () => self.open,
      onDismiss: () => { self.open = false; },
    });

    // The observer lives as long as the connection: the effect reads no signal, so it runs once, and its
    // cleanup disconnects.
    this.effect(() => {
      const observer = new MutationObserver(() => {
        const field = input();
        // A disabled input takes no keys, and a read-only one opens no list, so its list does not stay open.
        if (self.open && field?.hasAttribute('disabled')) self.open = false;
        if (self.open && field?.hasAttribute('readonly')) self.open = false;
        this.#sync();
      });
      observer.observe(this, { childList: true, subtree: true, attributes: true, attributeFilter: ['role', 'id', 'tabindex', 'popover', 'disabled', 'readonly', MARK, 'data-focus'] });
      return () => observer.disconnect();
    });
    this.#apply();
  }
}
