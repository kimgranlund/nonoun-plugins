// @ts-check
/**
 * form-field.class.js: the form field's class. Importing it defines no element; form-field.js does that.
 *
 * The root is a plain element that wires a control to the label, the help and the error the author wrote around
 * it, the children marked data-part="label", "help" and "error". It names no component. The control is found by
 * what it is (J50): the first native input, select or textarea inside, or the first element with one of the
 * roles a form control has. So it works with a text field, whose control is its native input, with the kit's
 * checkbox and radio group, whichever is defined first, and with a control that arrives or is replaced later.
 *
 * It reads the control's state through the state matrix's own conditions: invalid (which already means "invalid
 * and the user is due to be told", F5 and D33), required and disabled, and mirrors them onto its root for the
 * recipe. The recipe shows the error from that mirror alone, and hides it from the tag alone before definition.
 *
 * Rules: docs/specs/patterns.md, J50 to J52.
 */
import { UIElement } from '../../foundation/element.js';
import { props } from './form-field.props.js';

// Written out, not computed: a call at the top of a module keeps the module in every bundle that imports it (R1).
const CONTROL = 'input:not([type="hidden"]), select, textarea, [role="checkbox"], [role="switch"], [role="radiogroup"], [role="listbox"], [role="combobox"], [role="slider"], [role="spinbutton"]';
// The conditions of references/states.json, copied unchanged.
const INVALID = ':is([aria-invalid]:not([aria-invalid="false"]), :is(input, select, textarea):user-invalid, [invalid])';
const REQUIRED = ':is([required], [aria-required="true"])';
const DISABLED = ':is(:disabled, [disabled], [aria-disabled="true"])';
/** For the ids this class gives to a control, a label, a help or an error that has none. */
let serial = 0;

/**
 * Sets or removes an attribute, only when it differs. The observer then sees nothing when nothing changes.
 * @param {Element} el @param {string} name @param {string | null} value
 */
const put = (el, name, value) => {
  if (el.getAttribute(name) === value) return;
  if (value === null) el.removeAttribute(name);
  else el.setAttribute(name, value);
};

export class UIFormField extends UIElement {
  static props = props;

  /** @type {WeakMap<Element, string>} The for values this element wrote on a label, so that it never replaces an author's. */
  #pointed = new WeakMap();
  /** @type {WeakMap<Element, string>} The aria-describedby values it wrote on a control, likewise (A2). */
  #described = new WeakMap();
  /** @type {WeakMap<Element, string>} The aria-labelledby values it wrote on a control that a label cannot name. */
  #named = new WeakMap();

  /** The control: the first that belongs to this field, and not to a form field nested in it. @returns {HTMLElement | null} */
  #control() {
    return /** @type {HTMLElement | undefined} */ ([...this.querySelectorAll(CONTROL)].find((el) => el.closest(this.localName) === this)) ?? null;
  }

  /** @param {Element} el */
  #id(el) {
    if (!el.id) el.id = `${this.localName}-${++serial}`;
    return el.id;
  }

  /**
   * Writes an attribute this element owns on another element, unless the author wrote one there.
   * @param {Element} el @param {string} name @param {string | null} value @param {WeakMap<Element, string>} mine
   */
  #own(el, name, value, mine) {
    const now = el.getAttribute(name);
    if (now !== null && now !== mine.get(el)) return; // the author's
    put(el, name, value);
    if (value === null) mine.delete(el);
    else mine.set(el, value);
  }

  /** Brings the label, the descriptions and the root's mirrored states in step with the control. */
  #sync() {
    const control = this.#control();
    const label = this.ensurePart('label');
    const help = this.ensurePart('help');
    const error = this.ensurePart('error');
    const invalid = !!control && control.matches(INVALID);
    put(this, 'invalid', invalid ? '' : null);
    put(this, 'required', control?.matches(REQUIRED) ? '' : null);
    put(this, 'disabled', control?.matches(DISABLED) ? '' : null);
    if (!control) return;
    const id = this.#id(control);
    if (label) {
      this.#own(label, 'for', id, this.#pointed);
      // A label names only a labelable element. A control it cannot name, such as a plain element with a role,
      // is named by the label's id instead, unless the author named it.
      const labelled = /** @type {HTMLLabelElement} */ (label).control === control;
      if (!control.hasAttribute('aria-label')) this.#own(control, 'aria-labelledby', labelled ? null : this.#id(label), this.#named);
    }
    const ids = [help ? this.#id(help) : null, error && invalid ? this.#id(error) : null].filter(Boolean).join(' ');
    this.#own(control, 'aria-describedby', ids || null, this.#described);
  }

  /** The control's own Tab stop: itself when it takes focus, or else the item inside it that does. @param {HTMLElement} control */
  #stop(control) {
    if (control.tabIndex >= 0) return control;
    return /** @type {HTMLElement | null} */ (control.querySelector('[tabindex="0"]'));
  }

  connected() {
    // The states the control's own events change. The control's component may write aria-invalid in the same
    // event, after this listener, so look again once it has; the observer sees what comes later still.
    const soon = () => { this.#sync(); queueMicrotask(() => { if (this.isConnected) this.#sync(); }); };
    for (const type of ['input', 'change', 'focusout']) this.listen(this, type, soon);
    this.listen(this, 'invalid', soon, { capture: true });
    // A form reset clears the browser's own mark of a native control after the reset event: look a task later.
    this.listen(this.ownerDocument, 'reset', (event) => {
      if (event.target instanceof Node && event.target.contains(this)) setTimeout(() => { if (this.isConnected) this.#sync(); });
    }, { capture: true });
    // A click on the label focuses or activates the control (J51). The browser does it for a labelable control
    // that takes focus, and activates it; for any other control, the field moves focus to the control's Tab stop.
    // For a labelable one that focus is the browser's own, given once more.
    this.listen(this, 'click', (event) => {
      const label = this.ensurePart('label');
      const control = this.#control();
      if (!label || !control || !(event.target instanceof Node) || !label.contains(event.target)) return;
      if (control.matches(DISABLED)) return;
      this.#stop(control)?.focus();
    });

    // The observer lives as long as the connection: the effect reads no signal, so it runs once, and its
    // cleanup disconnects.
    this.effect(() => {
      const observer = new MutationObserver(() => this.#sync());
      observer.observe(this, {
        childList: true, subtree: true, attributes: true,
        attributeFilter: ['role', 'id', 'type', 'data-part', 'for', 'tabindex', 'aria-invalid', 'invalid', 'required', 'aria-required', 'disabled', 'aria-disabled', 'aria-describedby', 'aria-labelledby', 'aria-label'],
      });
      return () => observer.disconnect();
    });
    this.#sync();
  }
}
