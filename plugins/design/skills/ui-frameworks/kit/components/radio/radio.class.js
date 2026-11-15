// @ts-check
/**
 * radio.class.js: the class of one radio. Importing it defines no element; radio.js does that.
 *
 * The root has the radio role. It keeps aria-checked and aria-disabled in step with its own attributes and
 * turns Space and Enter into a click. It does not know its group: the radio group writes its checked
 * attribute and its tabindex, and listens for its click.
 *
 * A radio can be disabled but holds no form value; the group is the form control. So it extends UIElement,
 * not UIFormElement (D69).
 */
import { UIElement, setAttr } from '../../foundation/element.js';
import { press } from '../../behaviours/press.js';
import { props, role } from './radio.props.js';

export class UIRadio extends UIElement {
  static props = props;
  static role = role;

  connected() {
    const self = /** @type {any} */ (this);
    this.use(press, { disabled: () => self.disabled });
    this.effect(() => setAttr(this, 'aria-checked', String(self.checked)));
    this.effect(() => setAttr(this, 'aria-disabled', self.disabled ? 'true' : null));
  }
}
