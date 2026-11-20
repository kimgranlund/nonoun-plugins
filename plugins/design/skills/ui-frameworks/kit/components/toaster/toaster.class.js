// @ts-check
/**
 * toaster.class.js: the toaster's class, the stack that holds toasts. Importing it defines no element; toaster.js does that.
 *
 * The root has the region role, which UIElement writes when the author wrote none, and the name "Notifications" in
 * aria-label unless the author wrote aria-label or aria-labelledby (J94). It is a manual popover: it shows in the top
 * layer exactly while one of its children has the status or the alert role and `open`, and leaves it when none has
 * (D77). It finds toasts by role, never by tag, so it counts a toast once that toast is defined and has written its
 * role, and it works whichever element is defined first. A MutationObserver held in an effect watches the children,
 * their `open` and their role.
 *
 * The recipe places it in the corner `placement` names, stacks the toasts with the newest, the last child, nearest
 * that corner, and lets presses through wherever no toast is. The toaster writes nothing on a toast.
 *
 * It names no tag. Rules: docs/specs/patterns.md, J94.
 */
import { UIElement } from '../../foundation/element.js';
import { props, parts, role, tabindex } from './toaster.props.js';

/** The roles of a toast. */
const ROLES = ['status', 'alert'];

export class UIToaster extends UIElement {
  static props = props;
  static parts = parts;
  static role = role;
  static tabindex = tabindex;

  /** The name the toaster has when the author named it nothing else. */
  static label = 'Notifications';

  /** Whether a child is a toast that is open. */
  #holdsOpen() {
    return [...this.children].some((el) => ROLES.includes(el.getAttribute('role') ?? '') && el.hasAttribute('open'));
  }

  /** Shows the popover while a toast is open and hides it when none is. */
  #sync() {
    // A popover attribute the author removed leaves nothing to show. Showing a shown popover, or hiding a hidden
    // one, does nothing.
    if (!this.hasAttribute('popover')) return;
    if (this.#holdsOpen()) this.showPopover();
    else this.hidePopover();
  }

  connected() {
    if (!this.hasAttribute('aria-label') && !this.hasAttribute('aria-labelledby')) {
      this.setAttribute('aria-label', /** @type {typeof UIToaster} */ (this.constructor).label);
    }
    if (!this.hasAttribute('popover')) this.setAttribute('popover', 'manual');
    // The observer lives as long as the connection: the effect reads no signal, so it runs once.
    this.effect(() => {
      const observer = new MutationObserver(() => this.#sync());
      observer.observe(this, { childList: true, subtree: true, attributes: true, attributeFilter: ['open', 'role'] });
      return () => observer.disconnect();
    });
    this.#sync();
  }
}
