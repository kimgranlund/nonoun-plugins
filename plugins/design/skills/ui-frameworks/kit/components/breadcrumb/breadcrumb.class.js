// @ts-check
/**
 * breadcrumb.class.js: the breadcrumb's class. Importing it defines no element; breadcrumb.js does that.
 *
 * The root has the navigation role (J13). The links are the author's native anchors and stay untouched: the
 * class only names the navigation when the author did not.
 */
import { UIElement } from '../../foundation/element.js';
import { props, parts, role, tabindex } from './breadcrumb.props.js';

/** The name written when the author wrote none: messages.label in breadcrumb.manifest.json. */
const LABEL = 'Breadcrumb';

export class UIBreadcrumb extends UIElement {
  static props = props;
  static parts = parts;
  static role = role;
  static tabindex = tabindex;

  connected() {
    if (!this.hasAttribute('aria-label') && !this.hasAttribute('aria-labelledby')) this.setAttribute('aria-label', LABEL);
  }
}
