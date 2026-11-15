// @ts-check
/**
 * checkbox.class.js: the checkbox's class. Importing it defines no element; checkbox.js does that.
 *
 * The root is the control (D9): a form-associated custom element with the checkbox role. Its label is
 * whatever the author put inside it, and its mark is drawn by the recipe as a pseudo-element (D57),
 * so this class creates no part.
 */
import { setAttr } from '../../foundation/element.js';
import { UIFormElement } from '../../foundation/form.js';
import { press } from '../../behaviours/press.js';
import { props, role, tabindex, resets } from './checkbox.props.js';

/** Shown by the browser when a required checkbox is off. From the manifest's `messages`. */
const VALUE_MISSING = 'Please tick this box';

export class UICheckbox extends UIFormElement {
  static props = props;
  static role = role;
  static tabindex = tabindex;
  static resets = resets;

  formValue() {
    const self = /** @type {any} */ (this);
    return self.checked ? /** @type {string} */ (self.value) : null;
  }

  formValidity() {
    const self = /** @type {any} */ (this);
    return self.required && !self.checked ? { flags: { valueMissing: true }, message: VALUE_MISSING } : null;
  }

  /** @param {string | File | FormData | null} state */
  restore(state) { /** @type {any} */ (this).checked = state !== null; }

  connected() {
    const self = /** @type {any} */ (this);
    this.use(press, { disabled: () => this.effectiveDisabled });
    this.listen(this, 'click', () => {
      if (this.effectiveDisabled) return;
      self.indeterminate = false;
      self.checked = !self.checked;
      this.dispatchEvent(new Event('input', { bubbles: true }));
      this.dispatchEvent(new Event('change', { bubbles: true }));
    });
    this.effect(() => setAttr(this, 'aria-checked', self.indeterminate ? 'mixed' : String(self.checked)));
    this.effect(() => setAttr(this, 'aria-required', self.required ? 'true' : null));
  }
}
