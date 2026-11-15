// @ts-check
/**
 * icon.class.js: the icon's class. Importing it defines no element; icon.js does that.
 *
 * The icon is drawn by its recipe alone (docs/specs/icons.md, I1): this class draws nothing, creates no part and
 * has no behaviour. It names the icon for assistive technology once, when it connects (I8): an icon the author
 * gave no name is decorative and hidden; one with aria-label or aria-labelledby is an image. It never writes over
 * an aria-hidden or a role the author wrote, and never writes a label.
 */
import { UIElement } from '../../foundation/element.js';
import { props, parts, role, tabindex } from './icon.props.js';

export class UIIcon extends UIElement {
  static props = props;
  static parts = parts;
  static role = role;
  static tabindex = tabindex;

  connected() {
    const named = this.hasAttribute('aria-label') || this.hasAttribute('aria-labelledby');
    if (!named) {
      if (!this.hasAttribute('aria-hidden')) this.setAttribute('aria-hidden', 'true');
    } else if (!this.hasAttribute('role')) {
      this.setAttribute('role', 'img');
    }
  }
}
