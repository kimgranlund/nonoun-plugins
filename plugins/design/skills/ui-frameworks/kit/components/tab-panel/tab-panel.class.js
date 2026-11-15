// @ts-check
/**
 * tab-panel.class.js: the class of one panel. Importing it defines no element; tab-panel.js does that.
 *
 * The root has the tabpanel role and is in the Tab order, so that a keyboard user reaches a panel whose
 * content holds nothing focusable. It has no logic of its own: the tabs element hides it, shows it and
 * names it after its tab.
 */
import { UIElement } from '../../foundation/element.js';
import { props, role, tabindex } from './tab-panel.props.js';

export class UITabPanel extends UIElement {
  static props = props;
  static role = role;
  static tabindex = tabindex;
}
