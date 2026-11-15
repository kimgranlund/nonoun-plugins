// @ts-check
/**
 * menu-item-radio.class.js: the class of a menu item that is one choice of a group. Importing it defines no
 * element; menu-item-radio.js does that.
 *
 * The root has the menuitemradio role. It turns Enter and Space into a click, and a click turns it on, never
 * off, and dispatches `change`, which bubbles, only when it was off. It keeps aria-checked and aria-disabled in
 * step with its own attributes. Its group, not this class, turns the other choices off (J22). It does not know
 * its menu: the menu closes after Enter but not after Space or the pointer.
 *
 * It holds no form value, so it extends UIElement, not UIFormElement, as the menu item does (D69).
 * Rules: docs/specs/patterns.md, J21 and J22.
 */
import { UIElement, setAttr } from '../../foundation/element.js';
import { press } from '../../behaviours/press.js';
import { props, role } from './menu-item-radio.props.js';

export class UIMenuItemRadio extends UIElement {
  static props = props;
  static role = role;

  connected() {
    const self = /** @type {any} */ (this);
    this.use(press, { disabled: () => self.disabled });
    this.listen(this, 'click', () => {
      if (self.disabled || self.checked) return;
      self.checked = true;
      this.dispatchEvent(new Event('change', { bubbles: true }));
    });
    this.effect(() => setAttr(this, 'aria-checked', String(self.checked)));
    this.effect(() => setAttr(this, 'aria-disabled', self.disabled ? 'true' : null));
  }
}
