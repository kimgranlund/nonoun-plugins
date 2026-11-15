// @ts-check
/**
 * form.js: UIFormElement, the base of every root that can be disabled, button included (D20).
 * It imports signals.js and element.js.
 *
 * Rules: docs/specs/foundation.md, F1 to F7.
 *
 * A component adds its own props to `UIFormElement.props`, names in `static resets` the props a form
 * reset restores, and overrides formValue(), formValidity() and restore() as it needs.
 */
import { signal } from './signals.js';
import { UIElement, setAttr } from './element.js';

/** @typedef {{ flags: ValidityStateFlags, message: string }} Problem  Why the value is not valid. */

export class UIFormElement extends UIElement {
  static formAssociated = true;
  /** @type {Record<string, import('./element.js').Prop>} */
  static props = { name: { type: 'string' }, disabled: { type: 'boolean' } };
  /** @type {string[]} The props a form reset puts back to what they held at the first connect. */
  static resets = [];

  /** The only ElementInternals in the kit (D46). ARIA still goes in attributes (D9). */
  internals = this.attachInternals();

  #disabledByPlatform = signal(false);
  #invalid = signal(false);
  /** True once the user is due to be told that the value is invalid (D33). */
  #told = signal(false);
  /** @type {Problem | null} */
  #custom = null;
  /** @type {Record<string, unknown> | null} */
  #first = null;

  /** True when the element's own `disabled` is set, or the platform disabled it through a fieldset. */
  get effectiveDisabled() { return /** @type {any} */ (this).disabled || this.#disabledByPlatform.value; }

  get form() { return this.internals.form; }

  /** The value the form submits for this element's name: a string, a File, FormData, or null for nothing. @returns {string | File | FormData | null} */
  formValue() { return null; }

  /** Why the value is not valid, or null. @returns {Problem | null} */
  formValidity() { return null; }

  /** Restores the value the platform kept, after a navigation or a restart. @param {string | File | FormData | null} _state */
  restore(_state) {}

  /** Like the native method: a message makes the element invalid, an empty string clears it. @param {string} message */
  setCustomValidity(message) {
    this.#custom = message ? { flags: { customError: true }, message } : null;
    this.changed();
  }

  /** Publishes the form value and the validity, synchronously, whenever a prop changes (D44). */
  changed() {
    const problem = this.#custom ?? this.formValidity();
    this.internals.setFormValue(this.formValue());
    if (problem) this.internals.setValidity(problem.flags, problem.message, this);
    else this.internals.setValidity({});
    this.#invalid.value = !!problem;
  }

  setup() {
    const self = /** @type {any} */ (this);
    const resets = /** @type {typeof UIFormElement} */ (this.constructor).resets;
    this.#first ??= Object.fromEntries(resets.map((name) => [name, self[name]]));
    const tell = () => { this.#told.value = true; };
    this.listen(this, 'change', tell);
    this.listen(this, 'invalid', tell);
    this.effect(() => setAttr(this, 'aria-disabled', this.effectiveDisabled ? 'true' : null));
    this.effect(() => setAttr(this, 'aria-invalid', this.#told.value && this.#invalid.value ? 'true' : null));
    this.changed();
  }

  /** The platform reports the element disabled, by its own attribute or by a fieldset. It never writes the attribute. @param {boolean} disabled */
  formDisabledCallback(disabled) { this.#disabledByPlatform.value = disabled; }

  formResetCallback() {
    const self = /** @type {any} */ (this);
    for (const [name, value] of Object.entries(this.#first ?? {})) self[name] = value;
    this.#told.value = false;
  }

  /** @param {string | File | FormData | null} state */
  formStateRestoreCallback(state) { this.restore(state); }
}
