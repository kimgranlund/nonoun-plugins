// @ts-check
/**
 * text-field.class.js: the text field's class. Importing it defines no element; text-field.js does that.
 *
 * The root is a plain element, not a form control (D14): the author's native input, the child marked
 * data-part="input", carries the name, the value, the type and every constraint, and takes part in the form
 * by itself. The field never creates, moves or wraps it. It disables the input while it is disabled itself,
 * focuses the input on a press anywhere else in the field, and tells the user that the value is invalid
 * the way UIFormElement does (F5): from the input's first `change` or `invalid` event, until a form reset.
 * Validity is read from the input itself.
 *
 * Rules: docs/specs/patterns.md, J47 to J49.
 */
import { UIElement } from '../../foundation/element.js';
import { props } from './text-field.props.js';

/** What a press on one of them is for: the field leaves it alone. */
const INTERACTIVE = 'a[href], button, input, select, textarea, [tabindex], [contenteditable]';

/**
 * Sets or removes an attribute, only when it differs. The observer then sees nothing when nothing changes.
 * @param {Element} el @param {string} name @param {string | null} value
 */
const put = (el, name, value) => {
  if (el.getAttribute(name) === value) return;
  if (value === null) el.removeAttribute(name);
  else el.setAttribute(name, value);
};

export class UITextField extends UIElement {
  static props = props;

  /** @type {WeakSet<HTMLInputElement>} The inputs whose user is due to be told (F5). One per input, so a replaced input starts untold. */
  #told = new WeakSet();
  /** @type {WeakSet<HTMLInputElement>} The inputs this field disabled, so that it never enables one the author disabled. */
  #disabledHere = new WeakSet();

  /** The author's input, looked up each time (P6). @returns {HTMLInputElement | null} */
  #input() { return this.querySelector(':scope > input[data-part="input"]'); }

  /** Brings the input's disabled state and aria-invalid, and the root's invalid and readonly, in step. */
  #sync() {
    const self = /** @type {any} */ (this);
    const input = this.#input();
    if (input) {
      if (self.disabled && !input.disabled) { input.disabled = true; this.#disabledHere.add(input); }
      else if (!self.disabled && this.#disabledHere.has(input)) { input.disabled = false; this.#disabledHere.delete(input); }
    }
    const invalid = !!input && this.#told.has(input) && !input.validity.valid;
    if (input) put(input, 'aria-invalid', invalid ? 'true' : null);
    put(this, 'invalid', invalid ? '' : null);
    put(this, 'readonly', input?.readOnly ? '' : null);
  }

  /** @param {string} name */
  changed(name) {
    if (name === 'disabled' && this.isConnected) this.#sync();
  }

  connected() {
    /** @param {Event} event */
    const fromInput = (event) => event.target === this.#input();
    /** @param {Event} event */
    const tell = (event) => {
      if (!fromInput(event)) return;
      this.#told.add(/** @type {HTMLInputElement} */ (event.target));
      this.#sync();
    };
    // The user is due to be told once they have changed the value and left it, or tried to submit (F5).
    this.listen(this, 'change', tell);
    // invalid does not bubble.
    this.listen(this, 'invalid', tell, { capture: true });
    // Once told, the state follows every keystroke, so a correction clears it at once.
    this.listen(this, 'input', (event) => { if (fromInput(event)) this.#sync(); });
    // A form reset clears the mark (F6). The reset event comes before the values go back; the mark alone decides.
    this.listen(this.ownerDocument, 'reset', (event) => {
      const input = this.#input();
      if (!input || event.target !== input.form) return;
      this.#told.delete(input);
      this.#sync();
    }, { capture: true });
    // A press anywhere in the field focuses the input, except on the input itself or on something that is
    // interactive of its own, such as a button written after the input. On a disabled field it moves no focus.
    this.listen(this, 'mousedown', (event) => {
      const input = this.#input();
      const target = /** @type {Element | null} */ (event.target instanceof Element ? event.target : null);
      if (!input || !target || target === input) return;
      const own = target.closest(INTERACTIVE);
      if (own && own !== this && this.contains(own)) return;
      event.preventDefault();
      if (!input.disabled) input.focus();
    });

    // The observer lives as long as the connection: the effect reads no signal, so it runs once, and its
    // cleanup disconnects. It sees an input that arrives, is replaced, or changes its constraints.
    this.effect(() => {
      const observer = new MutationObserver(() => this.#sync());
      observer.observe(this, {
        childList: true, subtree: true, attributes: true,
        attributeFilter: ['data-part', 'readonly', 'disabled', 'required', 'pattern', 'min', 'max', 'step', 'minlength', 'maxlength', 'type', 'value'],
      });
      return () => observer.disconnect();
    });
    this.#sync();
  }
}
