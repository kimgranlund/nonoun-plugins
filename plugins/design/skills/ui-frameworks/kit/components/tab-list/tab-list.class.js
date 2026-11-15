// @ts-check
/**
 * tab-list.class.js: the class of the list of tabs. Importing it defines no element; tab-list.js does that.
 *
 * The root has the tablist role and is one stop in the Tab order: roving focus keeps one of its tabs
 * reachable, the selected one while focus is elsewhere, and moves focus with the arrow keys. It does not
 * select anything; the tabs element does that.
 */
import { UIElement, setAttr } from '../../foundation/element.js';
import { rovingFocus } from '../../behaviours/roving-focus.js';
import { props, role } from './tab-list.props.js';

export class UITabList extends UIElement {
  static props = props;
  static role = role;

  connected() {
    const self = /** @type {any} */ (this);
    /** The tabs of this list. A panel, and any tabs nested in it, lies outside the list. */
    const tabs = () => /** @type {HTMLElement[]} */ ([...this.querySelectorAll('[role="tab"]')]);

    // ARIA's default for a tablist is horizontal, so only vertical is written.
    this.effect(() => setAttr(this, 'aria-orientation', self.orientation === 'vertical' ? 'vertical' : null));

    this.use(rovingFocus, {
      items: tabs,
      orientation: () => self.orientation,
      current: () => tabs().find((tab) => tab.getAttribute('aria-selected') === 'true'),
      skip: (/** @type {HTMLElement} */ tab) => tab.hasAttribute('disabled') || tab.getAttribute('aria-disabled') === 'true',
      watch: ['aria-selected'],
    });
  }
}
