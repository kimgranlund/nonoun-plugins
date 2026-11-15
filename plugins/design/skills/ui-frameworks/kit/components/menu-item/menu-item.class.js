// @ts-check
/**
 * menu-item.class.js: the class of one action in a menu. Importing it defines no element; menu-item.js does that.
 *
 * The root has the menuitem role. It turns Enter and Space into a click and keeps aria-disabled in step with
 * its own attribute. It does not know its menu: the menu writes its tabindex (roving focus), moves focus to it,
 * and closes when it is clicked.
 *
 * An item can be disabled but holds no form value, so it extends UIElement, not UIFormElement (D69).
 */
import { UIElement, setAttr } from '../../foundation/element.js';
import { press } from '../../behaviours/press.js';
import { props, role } from './menu-item.props.js';

export class UIMenuItem extends UIElement {
  static props = props;
  static role = role;

  connected() {
    const self = /** @type {any} */ (this);
    this.use(press, { disabled: () => self.disabled });
    this.effect(() => setAttr(this, 'aria-disabled', self.disabled ? 'true' : null));
  }
}
