// @ts-check
/**
 * menu-item-checkbox.class.js: the class of a menu item that is on or off. Importing it defines no element;
 * menu-item-checkbox.js does that.
 *
 * The root has the menuitemcheckbox role. It turns Enter and Space into a click, and a click turns it on or
 * off and dispatches `change`, which bubbles. It keeps aria-checked and aria-disabled in step with its own
 * attributes. It does not know its menu: the menu writes its tabindex, moves focus to it, and closes after
 * Enter but not after Space or the pointer (J22).
 *
 * It holds no form value, so it extends UIElement, not UIFormElement, as the menu item does (D69).
 * Rules: docs/specs/patterns.md, J21 and J22.
 */
import { UIElement, setAttr } from '../../foundation/element.js';
import { press } from '../../behaviours/press.js';
import { props, role } from './menu-item-checkbox.props.js';

export class UIMenuItemCheckbox extends UIElement {
  static props = props;
  static role = role;

  connected() {
    const self = /** @type {any} */ (this);
    this.use(press, { disabled: () => self.disabled });
    this.listen(this, 'click', () => {
      if (self.disabled) return;
      self.checked = !self.checked;
      this.dispatchEvent(new Event('change', { bubbles: true }));
    });
    this.effect(() => setAttr(this, 'aria-checked', String(self.checked)));
    this.effect(() => setAttr(this, 'aria-disabled', self.disabled ? 'true' : null));
  }
}
