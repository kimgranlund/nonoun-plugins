// @ts-check
/**
 * radio-group.class.js: the class of a radio group. Importing it defines no element; radio-group.js does that.
 *
 * The root has the radiogroup role and is the form control: it submits its name with its value while that
 * value names one of its radios. It finds its radios by their ARIA role and names no other component, so it
 * works whichever element is defined first, and with radios that arrive later. It sets a radio's state
 * through the radio's own `checked` attribute, and roving focus writes the radios' tabindex.
 *
 * Rules: docs/specs/patterns.md, J4 to J7; docs/specs/foundation.md, G1 to G3 and F1 to F7.
 */
import { setAttr } from '../../foundation/element.js';
import { UIFormElement } from '../../foundation/form.js';
import { rovingFocus } from '../../behaviours/roving-focus.js';
import { props, role, tabindex, resets } from './radio-group.props.js';

const RADIO = '[role="radio"]';
/** Shown by the browser when a required group has no choice. From the manifest's `messages`. */
const VALUE_MISSING = 'Please choose one';
/** The keys that move focus and choose. Home and End move focus only. */
const ARROWS = ['ArrowDown', 'ArrowRight', 'ArrowUp', 'ArrowLeft'];
/** The flags of ValidityState, to hand a problem on to another anchor. */
const FLAGS = /** @type {const} */ (['valueMissing', 'typeMismatch', 'patternMismatch', 'tooLong', 'tooShort', 'rangeUnderflow', 'rangeOverflow', 'stepMismatch', 'badInput', 'customError']);

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

export class UIRadioGroup extends UIFormElement {
  static props = props;
  static role = role;
  static tabindex = tabindex;
  static resets = resets;

  /** @type {string | null} The value once the group first settled with its radios: what a reset restores. */
  #initial = null;

  /** The radios of this group, and not of another group nested in it. @returns {HTMLElement[]} */
  #own() {
    return /** @type {HTMLElement[]} */ ([...this.querySelectorAll(RADIO)].filter((el) => el.closest(this.localName) === this));
  }

  /** A radio's value: its `value` attribute, or else its position among the radios. @param {Element} el @param {Element[]} radios */
  #valueOf(el, radios) { return el.getAttribute('value') ?? String(radios.indexOf(el)); }

  /** True when the value names one of the radios. */
  #named() {
    const value = /** @type {any} */ (this).value;
    const radios = this.#own();
    return value !== '' && radios.some((radio) => this.#valueOf(radio, radios) === value);
  }

  /** Brings the radios' `checked` in step with `value`. Writes nothing when they already are. */
  #sync() {
    const self = /** @type {any} */ (this);
    const radios = this.#own();
    if (!radios.length) return;
    if (self.value === '') {
      // No value written: take the radio the author marked, if any.
      const marked = radios.find((radio) => radio.hasAttribute('checked'));
      if (marked) { self.value = this.#valueOf(marked, radios); return; } // changed() has run this again with the value in place.
    }
    if (this.#initial === null) this.#initial = self.value;
    for (const radio of radios) put(radio, 'checked', this.#valueOf(radio, radios) === self.value ? '' : null);
  }

  /** Clears every radio, so that an empty value then takes no mark the user left behind. */
  #clear() { for (const radio of this.#own()) put(radio, 'checked', null); }

  /**
   * Checks a radio because the user asked for it, then tells listeners, who find the radios already written.
   * @param {EventTarget | null} target  Where the click or the focus landed.
   */
  #choose(target) {
    const self = /** @type {any} */ (this);
    if (this.effectiveDisabled) return;
    const radios = this.#own();
    const radio = /** @type {HTMLElement | null} */ (target instanceof Element ? target.closest(RADIO) : null);
    if (!radio || !radios.includes(radio) || disabled(radio)) return;
    const value = this.#valueOf(radio, radios);
    if (value === self.value) return;
    self.value = value; // changed() writes the radios before this returns.
    this.dispatchEvent(new Event('input', { bubbles: true }));
    this.dispatchEvent(new Event('change', { bubbles: true }));
  }

  formValue() { return this.#named() ? /** @type {string} */ (/** @type {any} */ (this).value) : null; }

  formValidity() {
    return /** @type {any} */ (this).required && !this.#named() ? { flags: { valueMissing: true }, message: VALUE_MISSING } : null;
  }

  /** @param {string | File | FormData | null} state */
  restore(state) {
    this.#clear();
    /** @type {any} */ (this).value = typeof state === 'string' ? state : '';
  }

  formResetCallback() {
    this.#clear();
    super.formResetCallback();
    if (this.#initial !== null) /** @type {any} */ (this).value = this.#initial;
  }

  /** @param {string} [name] */
  changed(name) {
    if (name === 'value' && this.isConnected) this.#sync();
    super.changed();
    // The group itself takes no focus, so a problem is anchored on the radio Tab would enter at: on submit
    // the browser moves focus there.
    const validity = this.internals.validity;
    if (validity.valid) return;
    const radios = this.#own();
    const anchor = radios.find((radio) => radio.hasAttribute('checked') && !disabled(radio)) ?? radios.find((radio) => !disabled(radio));
    if (!anchor) return;
    const flags = Object.fromEntries(FLAGS.filter((flag) => validity[flag]).map((flag) => [flag, true]));
    this.internals.setValidity(flags, this.internals.validationMessage, anchor);
  }

  connected() {
    const self = /** @type {any} */ (this);
    const checked = () => this.#own().find((radio) => radio.getAttribute('aria-checked') === 'true');

    // ARIA's default orientation for a radiogroup is not horizontal, so only horizontal is written.
    this.effect(() => setAttr(this, 'aria-orientation', self.orientation === 'horizontal' ? 'horizontal' : null));
    this.effect(() => setAttr(this, 'aria-required', self.required ? 'true' : null));

    this.use(rovingFocus, {
      items: () => this.#own(),
      orientation: () => 'both',
      current: checked,
      skip: (/** @type {HTMLElement} */ radio) => this.effectiveDisabled || disabled(radio),
      watch: ['aria-checked'],
    });
    // Space and a click reach the group as a click on a radio.
    this.listen(this, 'click', (event) => this.#choose(event.target));
    // An arrow key: roving focus, mounted before this listener, has already moved focus, and prevented the
    // key's default when it did. The radio that now has focus is checked. Tab moves focus and checks nothing.
    this.listen(this, 'keydown', (event) => {
      if (!ARROWS.includes(event.key) || !event.defaultPrevented) return;
      const active = this.ownerDocument.activeElement;
      if (active !== event.target) this.#choose(active);
    });

    // The observer lives as long as the connection: the effect reads no signal, so it runs once, and its
    // cleanup disconnects.
    this.effect(() => {
      const observer = new MutationObserver((records) => {
        const radios = this.#own();
        /** @type {HTMLElement | null} */
        let marked = null;
        let cleared = false;
        // Read every record before writing anything: a write would change what the later records find.
        for (const record of records) {
          const radio = /** @type {HTMLElement} */ (record.target);
          if (record.attributeName !== 'checked' || !radios.includes(radio)) continue;
          if (radio.hasAttribute('checked')) marked = radio;
          else if (this.#valueOf(radio, radios) === self.value) cleared = true;
        }
        // A script, or the author, checked a radio: the last one checked is now the value. One that cleared
        // the chosen radio leaves the group with no value.
        if (marked) { const value = this.#valueOf(marked, radios); if (value !== self.value) self.value = value; }
        else if (cleared) self.value = '';
        this.#sync();
        this.changed(); // the form value and the anchor follow the radios that came, went or changed.
      });
      observer.observe(this, { childList: true, subtree: true, attributes: true, attributeFilter: ['role', 'value', 'checked', 'disabled', 'aria-disabled'] });
      return () => observer.disconnect();
    });
    this.#sync();
    this.changed();
  }
}
