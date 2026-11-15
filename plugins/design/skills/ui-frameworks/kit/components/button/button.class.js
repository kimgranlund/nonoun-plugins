// @ts-check
/**
 * button.class.js: the button's class. Importing it defines no element; button.js does that.
 *
 * The root is the control (D9): a form-associated custom element with the button role. When its type is
 * submit it keeps a hidden native submit button as a part and submits through it (D19), so the form has
 * a default button for Enter and a real submitter.
 */
import { UIFormElement } from '../../foundation/form.js';
import { press } from '../../behaviours/press.js';
import { props, parts, role, tabindex } from './button.props.js';

export class UIButton extends UIFormElement {
  static props = props;
  static parts = parts;
  static role = role;
  static tabindex = tabindex;

  /** The native submit button inside the root, if there is one. It is never created here. */
  get #submit() { return /** @type {HTMLButtonElement | null} */ (this.querySelector(':scope > [data-part="submit"]')); }

  connected() {
    const self = /** @type {any} */ (this);
    this.use(press, { disabled: () => this.effectiveDisabled });

    // The part exists while the type is submit. It is the author's if they wrote one, so it is never removed;
    // when the type changes it stops being a submit button.
    this.effect(() => {
      const submits = self.type === 'submit';
      const part = submits ? /** @type {HTMLButtonElement} */ (this.ensurePart('submit')) : this.#submit;
      if (!part) return;
      part.type = submits ? 'submit' : 'button';
      part.name = self.name;
      part.value = self.value;
      part.disabled = this.effectiveDisabled;
    });

    this.listen(this, 'click', (event) => {
      // A click on the part is the platform submitting already: Enter in a text field clicks the default button.
      if (event.target === this.#submit || this.effectiveDisabled) return;
      const form = this.form;
      if (!form) return;
      // Called from the prototype: a control in the form with the id or name "reset" or "requestSubmit"
      // replaces form.reset and form.requestSubmit with itself.
      if (self.type === 'submit') HTMLFormElement.prototype.requestSubmit.call(form, this.#submit);
      else if (self.type === 'reset') HTMLFormElement.prototype.reset.call(form);
    });
  }
}
