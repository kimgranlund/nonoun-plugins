// @ts-check
/**
 * listbox.class.js: the class of a listbox. Importing it defines no element; listbox.js does that.
 *
 * The root has the listbox role, is one stop in the Tab order and keeps focus: the options never take it.
 * activeDescendant marks one option as highlighted and names it in aria-activedescendant; the keys, a typed
 * letter and a press on an option move that mark. In a single listbox the selection follows the highlight; with
 * `multiple` the keys only move it, and Space or a click toggles an option.
 *
 * It finds its options by their ARIA role and names no other component, so it works whichever element is
 * defined first, and with options that arrive later. It sets an option's state through the option's own
 * `selected` attribute, and moves the highlight by writing `data-highlighted` on an option. While it has focus
 * it also writes `data-focus` on the highlighted option, so that the option's recipe, which cannot see its
 * listbox, paints the highlight only then.
 *
 * It is a form control: it submits its name with the selected value, or with `multiple` once per selected value.
 *
 * Rules: docs/specs/patterns.md, J27 to J30; docs/specs/foundation.md, G1 to G6 and F1 to F7.
 */
import { setAttr } from '../../foundation/element.js';
import { UIFormElement } from '../../foundation/form.js';
import { activeDescendant } from '../../behaviours/active-descendant.js';
import { typeahead } from '../../behaviours/typeahead.js';
import { props, role, tabindex, resets } from './listbox.props.js';

const OPTION = '[role="option"]';
const MARK = 'data-highlighted';
/** Shown by the browser when a required listbox has nothing selected. From the manifest's `messages`. */
const VALUE_MISSING = 'Please choose an option';

/** @param {Element} el */
const disabled = (el) => el.hasAttribute('disabled') || el.getAttribute('aria-disabled') === 'true';

/**
 * Sets or removes an attribute, only when it differs. The observer then sees nothing when nothing changes.
 * @param {Element} el @param {string} name @param {string | null} value
 */
const put = (el, name, value) => {
  if (el.getAttribute(name) === value) return;
  if (value === null) el.removeAttribute(name);
  else el.setAttribute(name, value);
};

export class UIListbox extends UIFormElement {
  static props = props;
  static role = role;
  static tabindex = tabindex;
  static resets = resets;

  /** @type {string | null} The value once the listbox first settled with its options: what a reset restores. */
  #initial = null;
  /** @type {HTMLElement | null} The option that was highlighted when the current key went down. */
  #before = null;

  /** The options of this listbox, and not of another listbox nested in it. @returns {HTMLElement[]} */
  #own() {
    return /** @type {HTMLElement[]} */ ([...this.querySelectorAll(OPTION)].filter((el) => el.closest(this.localName) === this));
  }

  /** An option's value: its `value` attribute, or else its text. @param {Element} el */
  #valueOf(el) { return el.getAttribute('value') ?? (el.textContent ?? '').trim(); }

  /** The values `value` names: one, or with multiple those between the commas. @returns {string[]} */
  #chosen() {
    const self = /** @type {any} */ (this);
    if (self.value === '') return [];
    return self.multiple ? self.value.split(',') : [self.value];
  }

  /** The values among `values` that name an option, once each, in the order of the options. @param {string[]} values */
  #ordered(values) {
    return [...new Set(this.#own().map((el) => this.#valueOf(el)).filter((value) => values.includes(value)))];
  }

  /**
   * The highlighted option. While a mark written in this task waits for activeDescendant to clear the one before,
   * two options carry it, and the one that is not `before` is the new one.
   * @param {HTMLElement | null} [before]
   */
  #highlighted(before = null) {
    const marked = this.#own().filter((el) => el.hasAttribute(MARK));
    return marked.find((el) => el !== before) ?? (before && marked.includes(before) ? before : null);
  }

  /** Brings the options' `selected` in step with `value`. Writes nothing when they already are. */
  #sync() {
    const self = /** @type {any} */ (this);
    const options = this.#own();
    if (!options.length) return;
    if (this.#initial === null) {
      // No value written: take the options the author marked, the last one in a single listbox.
      const marked = options.filter((el) => el.hasAttribute('selected'));
      if (self.value === '' && marked.length) {
        self.value = (self.multiple ? marked : marked.slice(-1)).map((el) => this.#valueOf(el)).join(',');
        return; // changed() has run this again with the value in place.
      }
      this.#initial = self.value;
    }
    const chosen = this.#chosen();
    for (const option of options) put(option, 'selected', chosen.includes(this.#valueOf(option)) ? '' : null);
  }

  /** Paints the highlight while the listbox has focus: `data-focus` on the highlighted option, and on no other. */
  #mirror(on = this.ownerDocument.activeElement === this) {
    for (const option of this.#own()) put(option, 'data-focus', on && option.hasAttribute(MARK) ? '' : null);
  }

  /**
   * Selects an option, or with multiple toggles it, because the user asked for it; then tells listeners, who find
   * the options already written.
   * @param {HTMLElement | null} option
   */
  #choose(option) {
    const self = /** @type {any} */ (this);
    if (!option || disabled(option)) return;
    const value = this.#valueOf(option);
    let next = value;
    if (self.multiple) {
      const chosen = this.#chosen();
      next = this.#ordered(chosen.includes(value) ? chosen.filter((v) => v !== value) : [...chosen, value]).join(',');
    }
    if (next === self.value) return;
    self.value = next; // changed() writes the options before this returns.
    this.dispatchEvent(new Event('input', { bubbles: true }));
    this.dispatchEvent(new Event('change', { bubbles: true }));
  }

  formValue() {
    const self = /** @type {any} */ (this);
    const values = this.#ordered(this.#chosen());
    if (!values.length) return null;
    if (!self.multiple) return values[0];
    if (!self.name) return null;
    const data = new FormData();
    for (const value of values) data.append(self.name, value);
    return data;
  }

  formValidity() {
    return /** @type {any} */ (this).required && !this.#ordered(this.#chosen()).length ? { flags: { valueMissing: true }, message: VALUE_MISSING } : null;
  }

  /** @param {string | File | FormData | null} state */
  restore(state) {
    const values = state instanceof FormData ? [...state.values()].filter((v) => typeof v === 'string') : typeof state === 'string' ? [state] : [];
    /** @type {any} */ (this).value = values.join(',');
  }

  formResetCallback() {
    super.formResetCallback();
    if (this.#initial !== null) /** @type {any} */ (this).value = this.#initial;
  }

  /** @param {string} [name] */
  changed(name) {
    if ((name === 'value' || name === 'multiple') && this.isConnected) this.#sync();
    super.changed();
  }

  connected() {
    const self = /** @type {any} */ (this);
    this.effect(() => setAttr(this, 'aria-multiselectable', self.multiple ? 'true' : null));
    this.effect(() => setAttr(this, 'aria-required', self.required ? 'true' : null));

    // Before the behaviours: which option was highlighted when the key went down.
    this.listen(this, 'keydown', () => { this.#before = this.#highlighted(); });
    this.use(activeDescendant, {
      items: () => this.#own(),
      skip: (/** @type {HTMLElement} */ option) => disabled(option),
      fallback: () => this.#own().find((el) => el.hasAttribute('selected')),
    });
    this.use(typeahead, {
      // The search starts from the highlighted option: focus stays on the listbox, so typeahead cannot see it.
      items: () => this.#own(),
      current: () => /** @type {HTMLElement | null} */ (this.#highlighted()),
      skip: (/** @type {HTMLElement} */ option) => disabled(option),
      onMatch: (/** @type {HTMLElement} */ option) => put(option, MARK, ''),
    });
    // After the behaviours: a single listbox selects the option a key moved the highlight to. With multiple,
    // Space toggles the highlighted option.
    this.listen(this, 'keydown', (event) => {
      if (event.target !== this) return;
      if (self.multiple) {
        if (event.key !== ' ' || event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) return;
        event.preventDefault();
        this.#choose(this.#highlighted());
        return;
      }
      const after = this.#highlighted(this.#before);
      if (after !== this.#before) this.#choose(after);
    });
    // A press on an option highlights it, and selects it, or with multiple toggles it. The options take no focus,
    // so the press leaves focus on the listbox, or gives it to the listbox. A disabled option refuses both: the
    // behaviour does not highlight it and #choose() does not select it. A disabled listbox receives no click: the
    // platform withholds it from a disabled form-associated element and from what is inside it.
    this.listen(this, 'click', (event) => {
      const option = /** @type {HTMLElement | null} */ (event.target instanceof Element ? event.target.closest(OPTION) : null);
      if (!option || !this.#own().includes(option)) return;
      put(option, MARK, '');
      this.#choose(option);
    });
    // Taking focus highlights the first selected option, or the first that is not disabled, when none is.
    this.listen(this, 'focusin', (event) => {
      if (event.target !== this) return;
      if (!this.#highlighted()) {
        const options = this.#own().filter((el) => !disabled(el));
        const first = options.find((el) => el.hasAttribute('selected')) ?? options[0];
        if (first) put(first, MARK, '');
      }
      this.#mirror(true);
    });
    this.listen(this, 'focusout', (event) => { if (event.target === this) this.#mirror(false); });

    // The observer lives as long as the connection: the effect reads no signal, so it runs once, and its
    // cleanup disconnects.
    this.effect(() => {
      const observer = new MutationObserver((records) => {
        const options = this.#own();
        let chosen = this.#chosen();
        let marked = false;
        // Read every record before writing anything: a write would change what the later records find.
        for (const record of records) {
          const option = /** @type {HTMLElement} */ (record.target);
          if (record.attributeName !== 'selected' || !options.includes(option)) continue;
          const value = this.#valueOf(option);
          // A script, or the author, selected an option or cleared a selected one: the value follows.
          if (option.hasAttribute('selected') && !chosen.includes(value)) chosen = self.multiple ? [...chosen, value] : [value];
          else if (!option.hasAttribute('selected') && chosen.includes(value)) chosen = chosen.filter((v) => v !== value);
          else continue;
          marked = true;
        }
        if (marked) {
          const value = self.multiple ? this.#ordered(chosen).join(',') : chosen[0] ?? '';
          if (value !== self.value) self.value = value;
        }
        this.#sync();
        this.#mirror();
        this.changed(); // the form value follows the options that came, went or changed.
      });
      observer.observe(this, { childList: true, subtree: true, attributes: true, attributeFilter: ['role', 'value', 'selected', 'disabled', 'aria-disabled', MARK] });
      return () => observer.disconnect();
    });
    this.#sync();
    this.changed();
  }
}
