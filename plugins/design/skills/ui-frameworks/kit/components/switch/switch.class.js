// @ts-check
/**
 * switch.class.js: the switch's class. Importing it defines no element; switch.js does that.
 *
 * The root is the control (D9): a form-associated custom element with the switch role. Its label is
 * whatever the author put inside it, and its track and thumb are drawn by the recipe as pseudo-elements
 * (D57), so this class creates no part. It is a checkbox with another role and mark, and no indeterminate state.
 */
import { setAttr } from '../../foundation/element.js';
import { UIFormElement } from '../../foundation/form.js';
import { press } from '../../behaviours/press.js';
import { props, role, tabindex, resets } from './switch.props.js';

/** Shown by the browser when a required switch is off. From the manifest's `messages`. */
const VALUE_MISSING = 'Please turn this on';

export class UISwitch extends UIFormElement {
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
    this.use(press);
    this.listen(this, 'click', () => {
      if (this.effectiveDisabled) return;
      self.checked = !self.checked;
      this.dispatchEvent(new Event('input', { bubbles: true }));
      this.dispatchEvent(new Event('change', { bubbles: true }));
    });
    this.effect(() => setAttr(this, 'aria-checked', String(self.checked)));
    this.effect(() => setAttr(this, 'aria-required', self.required ? 'true' : null));
  }
}
