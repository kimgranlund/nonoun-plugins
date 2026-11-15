// @ts-check
/**
 * alert.class.js: the alert's class. Importing it defines no element; alert.js does that.
 *
 * The root has the alert role, which UIElement writes when the author wrote no role (J15). The author's icon and
 * message are left as written, and the alert takes no focus. There is no other logic.
 */
import { UIElement } from '../../foundation/element.js';
import { props, parts, role, tabindex } from './alert.props.js';

export class UIAlert extends UIElement {
  static props = props;
  static parts = parts;
  static role = role;
  static tabindex = tabindex;
}
