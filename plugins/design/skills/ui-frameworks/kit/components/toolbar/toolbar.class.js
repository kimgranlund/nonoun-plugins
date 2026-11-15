// @ts-check
/**
 * toolbar.class.js: the toolbar's class. Importing it defines no element; toolbar.js does that.
 *
 * The root has the toolbar role and is one stop in the Tab order: roving focus keeps one of its controls
 * reachable, the one that last had focus while focus is elsewhere, and moves focus with the arrow keys.
 * It writes only the tabindex of its controls, through the behaviour.
 */
import { UIElement, setAttr } from '../../foundation/element.js';
import { rovingFocus } from '../../behaviours/roving-focus.js';
import { props, role } from './toolbar.props.js';

/** What counts as a control: an element with one of these roles, a native button, a native link. */
const CONTROL = '[role="button"], [role="checkbox"], [role="switch"], [role="link"], button, a[href]';

export class UIToolbar extends UIElement {
  static props = props;
  static role = role;

  connected() {
    const self = /** @type {any} */ (this);
    /**
     * The controls of this toolbar, in document order. A control inside another control (the hidden submit
     * button inside a button) is a part of that one, and a control inside a toolbar nested in this one is its own.
     */
    const controls = () => /** @type {HTMLElement[]} */ ([...this.querySelectorAll(CONTROL)]).filter((el) =>
      el.closest(this.localName) === this && !this.#inside(el));

    // ARIA's default for a toolbar is horizontal, so only vertical is written.
    this.effect(() => setAttr(this, 'aria-orientation', self.orientation === 'vertical' ? 'vertical' : null));

    this.use(rovingFocus, {
      items: controls,
      orientation: () => self.orientation,
      skip: (/** @type {HTMLElement} */ el) => el.hasAttribute('disabled') || el.getAttribute('aria-disabled') === 'true',
      // A button or a checkbox that connects after this has written its own tabindex="0": watching tabindex
      // brings the stop back to one.
      watch: ['tabindex'],
    });
  }

  /** Whether `el` lies inside another element, below this toolbar, that matches CONTROL. @param {Element} el */
  #inside(el) {
    const up = el.parentElement?.closest(CONTROL);
    return !!up && this !== up && this.contains(up);
  }
}
