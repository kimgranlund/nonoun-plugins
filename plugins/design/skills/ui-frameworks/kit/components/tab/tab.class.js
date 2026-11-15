// @ts-check
/**
 * tab.class.js: the class of one tab. Importing it defines no element; tab.js does that.
 *
 * The root has the tab role. It keeps aria-selected and aria-disabled in step with its own attributes and
 * turns Enter and Space into a click. It does not know its list or its panel: the tab list writes its
 * tabindex, and the tabs element writes its selected attribute and listens for its click.
 *
 * A tab can be disabled but holds no form value, so it extends UIElement, not UIFormElement.
 */
import { UIElement, setAttr } from '../../foundation/element.js';
import { press } from '../../behaviours/press.js';
import { props, role } from './tab.props.js';

export class UITab extends UIElement {
  static props = props;
  static role = role;

  connected() {
    const self = /** @type {any} */ (this);
    this.use(press, { disabled: () => self.disabled });
    this.effect(() => setAttr(this, 'aria-selected', String(self.selected)));
    this.effect(() => setAttr(this, 'aria-disabled', self.disabled ? 'true' : null));
  }
}
